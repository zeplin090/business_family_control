from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date as dt_date, datetime
from decimal import Decimal
from typing import Optional


class TransactionBase(BaseModel):
    amount: Decimal = Field(..., description="Сумма операции")
    date: dt_date = Field(..., description="Дата совершения операции")
    comment: Optional[str] = Field(None, max_length=255, description="Необязательный комментарий")
    category_id: int = Field(..., description="ID категории (дохода или расхода)")


class TransactionCreate(TransactionBase):
    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Сумма транзакции должна быть строго больше нуля")
        return v


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[dt_date] = None
    comment: Optional[str] = Field(None, max_length=255)
    category_id: Optional[int] = None


class TransactionResponse(TransactionBase):
    id: int
    user_id: Optional[int]
    family_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionCreateResult(BaseModel):
    transaction: TransactionResponse
    limit_warning: Optional[str] = Field(
        default=None,
        description="Текст предупреждения, если лимит превышен или почти исчерпан"
    )
