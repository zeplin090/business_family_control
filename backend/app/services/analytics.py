import calendar
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.category import TransactionType
from app.models.user import User
from app.repositories.analytics import AnalyticsRepository
from app.schemas.analytics import CategoryData, MonthlyAnalyticsResponse, TransactionDetailItem


class AnalyticsService:
    def __init__(self, db: Session):
        self.repository = AnalyticsRepository(db)


    def get_monthly_analytics(self, family_id: int, year: int, month: int) -> MonthlyAnalyticsResponse:
        start_date, end_date = self._get_date_range(year, month)
        results = self.repository.get_monthly_category_totals(
            family_id, start_date, end_date
        )

        if not results:
            return MonthlyAnalyticsResponse(
                total_income=Decimal("0.0"),
                total_expense=Decimal("0.0"),
                income_by_category=[],
                expense_by_category=[]
            )

        income_rec  = [r for r in results if r.type == TransactionType.INCOME]
        expense_rec = [r for r in results if r.type == TransactionType.EXPENSE]

        total_income  = sum((r.amount for r in income_rec),  Decimal("0.0"))
        total_expense = sum((r.amount for r in expense_rec), Decimal("0.0"))

        income_list = [
            CategoryData(category_name=r.category_name, amount=r.amount)
            for r in income_rec
        ]
        expense_list = [
            CategoryData(category_name=r.category_name, amount=r.amount)
            for r in expense_rec
        ]

        return MonthlyAnalyticsResponse(
            total_income=total_income,
            total_expense=total_expense,
            income_by_category=income_list,
            expense_by_category=expense_list
        )

    
    def get_transaction_details(self, family_id: int, year: int, month: int) -> list[TransactionDetailItem]:
        start_date, end_date = self._get_date_range(year, month)
        return self.repository.get_transaction_details(
            family_id, start_date, end_date
        )


    def get_filtered_transactions(self, start_date: date = None, end_date: date = None, author_id: int = None, 
            current_user: User = None):
        return self.repository.get_filtered_transactions(
            family_id=current_user.family_id,
            start_date=start_date,
            end_date=end_date,
            author_id=author_id,
        )


    def get_family_members(self, current_user: User) -> list[dict]:
        members = self.repository.get_family_members(current_user.family_id)
        return [{"id": m.id, "full_name": m.full_name} for m in members]

    
    def _get_date_range(self, year: int, month: int) -> tuple[date, date]:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        return start_date, end_date
