from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal


class CategoryData(BaseModel):
    category_name: str = Field(..., description="Название категории")
    amount: Decimal = Field(..., description="Суммарное значение за период")


class MonthlyAnalyticsResponse(BaseModel):
    total_income: Decimal = Field(..., description="Общий доход за месяц")
    total_expense: Decimal = Field(..., description="Общий расход за месяц")
    income_by_category: List[CategoryData] = Field(..., description="Данные для круговой диаграммы доходов")
    expense_by_category: List[CategoryData] = Field(..., description="Данные для круговой диаграммы расходов")
