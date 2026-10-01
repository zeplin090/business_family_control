from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category, TransactionType
from app.models.transaction import Transaction

class BudgetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_category(self, category_id: int, family_id: int) -> Category | None:
        stmt_cat = select(Category).where(Category.id == category_id, Category.family_id == family_id)
        return self.db.execute(stmt_cat).scalar_one_or_none()
    
    def get_spent_value(self,
            category_id: int,
            family_id: int,
            start_date: date,
            end_date: date
        ):

        stmt_sum = select(func.sum(Transaction.amount)).where(
            Transaction.category_id == category_id,
            Transaction.family_id == family_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        current_spent = self.db.execute(stmt_sum).scalar() or Decimal("0.0")
        return current_spent


    def get_budget_utilization_data(self, family_id: int, start_date: date, end_date: date):
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
        
        return self.db.execute(stmt).all()