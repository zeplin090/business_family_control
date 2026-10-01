from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_monthly_category_totals(self, family_id: int, start_date: date, end_date: date):
        """Вывод всех транзакций по категориям, для круговой диаграммы.

        Args:
            family_id (int): Id семьи
            start_date (date): Дата начала отчёта
            end_date (date): Дата конца отчёта
        Returns:
            _type_: Список транзакций по категориям
        """
        stmt = (
            select(
                Category.name.label("category_name"),
                Category.type,
                func.sum(Transaction.amount).label("amount"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.family_id == family_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .group_by(Category.type, Category.name)
        )
        return self.db.execute(stmt).all()

    def get_transaction_details(self, family_id: int, start_date: date, end_date: date):
        """Получение информации о транзакцииях

        Args:
            family_id (int): Id семьи
            start_date (date): Дата начала отчёта
            end_date (date): Дата конца отчёта

        Returns:
            _type_: Список транзакций
        """
        stmt = (
            select(
                Transaction.id,
                Transaction.amount,
                Category.type.label("type"),
                Transaction.date,
                Transaction.comment.label("description"),
                User.full_name.label("author_name"),
                Category.name.label("category_name"),
            )
            .join(User, Transaction.user_id == User.id)
            .join(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.family_id == family_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .order_by(Transaction.date.desc())
        )
        return self.db.execute(stmt).all()

    def get_filtered_transactions(self, family_id: int, start_date: date | None = None, 
                                  end_date: date | None = None, author_id: int | None = None):
        """Получение списка транзакций семьи с фильтрацией.. (хз чем от предыдущего отличается)
    
        Args:
            family_id (int): Id семьи
            start_date (date): Дата начала отчёта
            end_date (date): Дата конца отчёта
            author_id (int | None, optional): Id автора. Defaults to None.

        Returns:
            _type_: Список транзакций
        """
        stmt = (
            select(
                Transaction.id,
                Transaction.amount,
                Category.type.label("type"),
                Transaction.date,
                Transaction.comment,
                User.full_name.label("author_name"),
                Category.name.label("category_name"),
            )
            .join(User, Transaction.user_id == User.id)
            .join(Category, Transaction.category_id == Category.id)
            .where(Transaction.family_id == family_id)
        )

        if start_date:
            stmt = stmt.where(Transaction.date >= start_date)
        if end_date:
            stmt = stmt.where(Transaction.date <= end_date)
        if author_id:
            stmt = stmt.where(Transaction.user_id == author_id)

        return self.db.execute(stmt.order_by(Transaction.date.desc())).all()

    def get_family_members(self, family_id: int):
        """Получение списков членов семьи

        Args:
            family_id (int): ID семьи

        Returns:
            _type_: табличка из айдишников и имён семьянинов
        """
        stmt = (
            select(User.id, User.full_name)
            .where(User.family_id == family_id)
            .order_by(User.full_name)
        )
        return self.db.execute(stmt).all()
