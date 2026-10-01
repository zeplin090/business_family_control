from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.repositories.transaction import TransactionRepository


class TransactionService:
    def __init__(self, db: Session):
        self.repository = TransactionRepository(db)

    def create_transaction(self, obj_in: TransactionCreate, user_id: int, family_id: int) -> Transaction:
        return self.repository.create_transaction(obj_in=obj_in, user_id=user_id, 
                                                  family_id=family_id)

    def get_transactions(self, family_id: int, skip: int = 0, limit: int = 100) -> list[Transaction]:
        return self.repository.get_transactions(family_id=family_id, skip=skip, 
                                                limit=limit)

    def get_transaction_by_id(self, transaction_id: int, family_id: int) -> Transaction | None:
        return self.repository.get_transaction_by_id(transaction_id=transaction_id, family_id=family_id)

    def update_transaction(self, db_obj: Transaction, obj_in: TransactionUpdate) -> Transaction:
        return self.repository.update_transaction(db_obj=db_obj, obj_in=obj_in)

    def delete_transaction(self, db_obj: Transaction) -> None:
        self.repository.delete_transaction(db_obj=db_obj)
