from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, obj_in: TransactionCreate, user_id: int, family_id: int) -> Transaction:
        db_obj = Transaction(
            amount=obj_in.amount,
            date=obj_in.date,
            comment=obj_in.comment,
            category_id=obj_in.category_id,
            user_id=user_id,
            family_id=family_id
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_transactions(self, family_id: int, skip: int = 0, limit: int = 100) -> list[Transaction]:
        stmt = select(Transaction).where(Transaction.family_id == family_id).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_transaction_by_id(self, transaction_id: int, family_id: int) -> Transaction | None:
        stmt = select(Transaction).where(Transaction.id == transaction_id, Transaction.family_id == family_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def update_transaction(self, db_obj: Transaction, obj_in: TransactionUpdate) -> Transaction:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete_transaction(self, db_obj: Transaction) -> None:
        self.db.delete(db_obj)
        self.db.commit()
