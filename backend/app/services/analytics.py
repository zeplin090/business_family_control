import calendar
from datetime import date
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.category import Category, TransactionType
from app.schemas.analytics import MonthlyAnalyticsResponse, CategoryData, TransactionDetailItem
from app.models.user import User

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db


    def get_monthly_analytics(self, family_id: int, year: int, month: int) -> MonthlyAnalyticsResponse:
        start_date, end_date = self._get_date_range(year, month)
        stmt = (
            select(
                Category.name.label("category_name"),
                Category.type,
                func.sum(Transaction.amount).label("amount")
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.family_id == family_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
            .group_by(Category.type, Category.name)
        )
        results = self.db.execute(stmt).all()

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
        stmt = (
            select(
                Transaction.id,
                Transaction.amount,
                Category.type.label("type"),
                Transaction.date,
                Transaction.comment.label("description"),
                User.full_name.label("author_name"),
                Category.name.label("category_name")
            )
            .join(User, Transaction.user_id == User.id)
            .join(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.family_id == family_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
            .order_by(Transaction.date.desc())
        )
        return self.db.execute(stmt).all()


    def get_filtered_transactions(self, start_date: date = None, end_date: date = None, author_id: int = None, 
            current_user: User = None):
        query = self.db.query(
            Transaction.id,
            Transaction.amount,
            Category.type.label("type"),
            Transaction.date,
            Transaction.comment,
            User.full_name.label("author_name"),
            Category.name.label("category_name")
        ).join(User, Transaction.user_id == User.id) \
            .join(Category, Transaction.category_id == Category.id) \
            .filter(Transaction.family_id == current_user.family_id)

        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if author_id:
            query = query.filter(Transaction.user_id == author_id)

        results = query.order_by(Transaction.date.desc()).all()
        return results


    def get_family_members(self, current_user: User) -> list[dict]:
        members = (
            self.db.query(User.id, User.full_name)
            .filter(User.family_id == current_user.family_id)
            .all()
        )

        return [{"id": m.id, "full_name": m.full_name} for m in members]
    def _get_date_range(self, year: int, month: int) -> tuple[date, date]:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        return start_date, end_date