from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/members")
def get_family_members(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    service = AnalyticsService(db=db)
    return service.get_family_members(current_user)


@router.get("/filter")
def get_filtered_transactions(
        start_date: Optional[date] = Query(None, description="Начальная дата"),
        end_date: Optional[date] = Query(None, description="Конечная дата"),
        author_id: Optional[int] = Query(None, description="ID автора транзакции"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    service = AnalyticsService(db=db)
    results = service.get_filtered_transactions(
        start_date=start_date,
        end_date=end_date,
        author_id=author_id,
        current_user=current_user
    )
    return [
        {
            "id": row.id,
            "amount": row.amount,
            "type": row.type,
            "date": row.date,
            "description": row.comment,
            "author_name": row.author_name,
            "category_name": row.category_name
        }
        for row in results
    ]


@router.get("/monthly")
def get_monthly_analytics(
        year: int = Query(..., description="Год для фильтрации"),
        month: int = Query(..., description="Месяц для фильтрации"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    service = AnalyticsService(db)
    family_id = current_user.family_id

    analytics = service.get_monthly_analytics(family_id=family_id, year=year, month=month)

    transactions_rows = service.get_transaction_details(
        family_id=family_id,
        year=year,
        month=month
    )

    return {
        "total_income": analytics.total_income,
        "total_expense": analytics.total_expense,
        "income_by_category": analytics.income_by_category,     
        "expense_by_category": analytics.expense_by_category,   
        "transactions": [
            {
                "id": row.id,
                "amount": row.amount,
                "type": row.type,
                "date": row.date,
                "description": row.description,
                "author_name": row.author_name,
                "category_name": row.category_name
            }
            for row in transactions_rows
        ]
    }
