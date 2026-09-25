from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from app.services.transaction import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
        transaction_in: TransactionCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="Пользователь не состоит в семье")

    return TransactionService(db).create_transaction(
        obj_in=transaction_in,
        user_id=current_user.id,
        family_id=current_user.family_id
    )


@router.get("/", response_model=list[TransactionResponse])
def read_transactions(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.family_id:
        return []
    return TransactionService(db).get_transactions(family_id=current_user.family_id, skip=skip, limit=limit)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def read_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    transaction = TransactionService(db).get_transaction_by_id(transaction_id, current_user.family_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
        transaction_id: int,
        transaction_in: TransactionUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    transaction = transaction.get_transaction_by_id(db, transaction_id, current_user.family_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")

    return TransactionService(db).update_transaction(db_obj=transaction, obj_in=transaction_in)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    service = TransactionService(db)
    transaction = service.get_transaction_by_id(transaction_id, current_user.family_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")

    service.delete_transaction(transaction)
    return None


from app.services import budget_service
from app.schemas.transaction import TransactionCreateResult


@router.post("/", response_model=TransactionCreateResult, status_code=status.HTTP_201_CREATED)
def create_transaction(
        transaction_in: TransactionCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="Пользователь не состоит в семье")

    warning_message = budget_service.check_category_limit(
        db=db,
        category_id=transaction_in.category_id,
        family_id=current_user.family_id,
        new_amount=transaction_in.amount,
        transaction_date=transaction_in.date
    )

    transaction = transaction.create_transaction(
        db=db,
        obj_in=transaction_in,
        user_id=current_user.id,
        family_id=current_user.family_id
    )

    return TransactionCreateResult(
        transaction=transaction,
        limit_warning=warning_message
    )
