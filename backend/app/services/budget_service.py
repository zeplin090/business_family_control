import calendar
from datetime import date
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.category import Category, TransactionType
from app.models.transaction import Transaction


def check_category_limit(
        db: Session,
        category_id: int,
        family_id: int,
        new_amount: Decimal,
        transaction_date: date
) -> str | None:
    stmt_cat = select(Category).where(Category.id == category_id, Category.family_id == family_id)
    category = db.execute(stmt_cat).scalar_one_or_none()

    if not category or category.type != TransactionType.EXPENSE or not category.monthly_limit:
        return None

    year = transaction_date.year
    month = transaction_date.month
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    stmt_sum = select(func.sum(Transaction.amount)).where(
        Transaction.category_id == category_id,
        Transaction.family_id == family_id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    )
    current_spent = db.execute(stmt_sum).scalar() or Decimal("0.0")

    total_projected = current_spent + new_amount

    if total_projected > category.monthly_limit:
        over = total_projected - category.monthly_limit
        return f"Лимит превышен! Бюджет категории «{category.name}»: {category.monthly_limit}. Перерасход: {over}."

    if total_projected >= category.monthly_limit * Decimal("0.9"):
        left = category.monthly_limit - total_projected
        return f"Внимание: Вы приближаетесь к лимиту категории «{category.name}». Остаток бюджета: {left}."

    return None


from sqlalchemy.orm import Session
from app.schemas.budget_schema import BudgetProgressResponse, CategoryBudgetProgress


def get_budget_progress(db: Session, family_id: int, year: int, month: int) -> BudgetProgressResponse:
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    stmt = (
        select(
            Category.id,
            Category.name,
            Category.monthly_limit,
            func.sum(Transaction.amount).label("total_spent")
        )
        .outerjoin(
            Transaction,
            (Transaction.category_id == Category.id) &
            (Transaction.date >= start_date) &
            (Transaction.date <= end_date) &
            (Transaction.family_id == family_id)
        )
        .where(
            Category.family_id == family_id,
            Category.type == TransactionType.EXPENSE,
            Category.monthly_limit.is_not(None)
        )
        .group_by(Category.id)
    )

    results = db.execute(stmt).all()
    progress_list = []

    for row in results:
        spent = Decimal(str(row.total_spent)) if row.total_spent else Decimal("0.0")
        limit = row.monthly_limit

        remaining = limit - spent
        percentage = round((float(spent) / float(limit)) * 100, 2)

        progress_list.append(CategoryBudgetProgress(
            category_id=row.id,
            category_name=row.name,
            monthly_limit=limit,
            spent=spent,
            remaining=remaining,
            percentage=percentage
        ))

    progress_list.sort(key=lambda x: x.percentage, reverse=True)

    return BudgetProgressResponse(
        year=year,
        month=month,
        progress_bars=progress_list
    )
