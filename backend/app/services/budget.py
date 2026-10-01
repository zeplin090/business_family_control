import calendar
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.category import TransactionType
from app.schemas.budget import BudgetProgressResponse, CategoryBudgetProgress
from app.repositories.budget import BudgetRepository

class BudgetService:
    def __init__(self, db: Session):
        self.repository = BudgetRepository(db)

    def check_category_limit(self,
            category_id: int,
            family_id: int,
            new_amount: Decimal,
            transaction_date: date
        ) -> str | None:

        category = self.repository.get_category(category_id=category_id, family_id=family_id)
        if not category or category.type != TransactionType.EXPENSE or not category.monthly_limit:
            return None

        year = transaction_date.year
        month = transaction_date.month
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        current_spent = self.repository.get_spent_value(
            category_id=category_id, 
            family_id=family_id, 
            start_date=start_date, 
            end_date=end_date)
        
        total_projected = current_spent + new_amount

        if total_projected > category.monthly_limit:
            over = total_projected - category.monthly_limit
            return f"Лимит превышен! Бюджет категории «{category.name}»: {category.monthly_limit}. Перерасход: {over}."

        if total_projected >= category.monthly_limit * Decimal("0.9"):
            left = category.monthly_limit - total_projected
            return f"Внимание: Вы приближаетесь к лимиту категории «{category.name}». Остаток бюджета: {left}."

        return None


    def get_budget_progress(self, family_id: int, year: int, month: int) -> BudgetProgressResponse:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        results = self.repository.get_budget_utilization_data(
            family_id=family_id, 
            start_date=start_date, 
            end_date=end_date)
        
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
