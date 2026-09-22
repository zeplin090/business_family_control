from pydantic import BaseModel, Field
from decimal import Decimal


class CategoryBudgetProgress(BaseModel):
    category_id: int = Field(..., description="ID категории")
    category_name: str = Field(..., description="Название категории")
    monthly_limit: Decimal = Field(..., description="Установленный лимит на месяц")
    spent: Decimal = Field(..., description="Потрачено за выбранный месяц")
    remaining: Decimal = Field(..., description="Остаток лимита (может быть отрицательным при перерасходе)")
    percentage: float = Field(..., description="Процент расхода (от 0 до бесконечности)")


class BudgetProgressResponse(BaseModel):
    year: int
    month: int
    progress_bars: list[CategoryBudgetProgress]
