from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from decimal import Decimal

from app.models.category import TransactionType


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100, description="Название категории (например, 'Продукты')")
    type: TransactionType = Field(..., description="Тип: income (доход) или expense (расход)")
    monthly_limit: Optional[Decimal] = Field(None, ge=0, description="Лимит трат в месяц")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    monthly_limit: Optional[Decimal] = Field(None, ge=0)


class CategoryResponse(CategoryBase):
    id: int
    family_id: int

    model_config = ConfigDict(from_attributes=True)
