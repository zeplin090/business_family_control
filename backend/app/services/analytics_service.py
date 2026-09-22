import calendar
import pandas as pd
from datetime import date
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.category import Category, TransactionType
from app.schemas.analytics_schema import MonthlyAnalyticsResponse, CategoryData


def get_monthly_analytics(db: Session, family_id: int, year: int, month: int) -> MonthlyAnalyticsResponse:
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    stmt = (
        select(Transaction.amount, Category.name.label("category_name"), Category.type)
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.family_id == family_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
    )
    results = db.execute(stmt).all()

    if not results:
        return MonthlyAnalyticsResponse(
            total_income=Decimal("0.0"),
            total_expense=Decimal("0.0"),
            income_by_category=[],
            expense_by_category=[]
        )

    df = pd.DataFrame([
        {"amount": float(r.amount), "category": r.category_name, "type": r.type.value}
        for r in results
    ])

    grouped = df.groupby(['type', 'category'], as_index=False)['amount'].sum()

    income_df = grouped[grouped['type'] == TransactionType.INCOME.value]
    expense_df = grouped[grouped['type'] == TransactionType.EXPENSE.value]

    total_income = Decimal(str(round(income_df['amount'].sum(), 2))) if not income_df.empty else Decimal("0.0")
    total_expense = Decimal(str(round(expense_df['amount'].sum(), 2))) if not expense_df.empty else Decimal("0.0")

    income_list = [
        CategoryData(category_name=row['category'], amount=Decimal(str(round(row['amount'], 2))))
        for _, row in income_df.iterrows()
    ]

    expense_list = [
        CategoryData(category_name=row['category'], amount=Decimal(str(round(row['amount'], 2))))
        for _, row in expense_df.iterrows()
    ]

    return MonthlyAnalyticsResponse(
        total_income=total_income,
        total_expense=total_expense,
        income_by_category=income_list,
        expense_by_category=expense_list
    )
