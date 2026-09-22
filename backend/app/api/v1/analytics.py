from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from sqlalchemy import extract
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/members")
def get_family_members(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    members = db.query(User.id, User.full_name).filter(
        User.family_id == current_user.family_id
    ).all()
    return [{"id": m.id, "full_name": m.full_name} for m in members]


@router.get("/filter")
def get_filtered_transactions(
        start_date: Optional[date] = Query(None, description="Начальная дата"),
        end_date: Optional[date] = Query(None, description="Конечная дата"),
        author_id: Optional[int] = Query(None, description="ID автора транзакции"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = db.query(
        Transaction.id,
        Transaction.amount,
        Category.type.label("type"),
        Transaction.date,
        Transaction.comment,
        User.full_name.label("author_name"),
        Category.name.label("category_name")
    ).join(User, Transaction.user_id == User.id) \
        .join(Category, Transaction.category_id == Category.id) \
        .filter(Transaction.family_id == current_user.family_id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if author_id:
        query = query.filter(Transaction.user_id == author_id)

    results = query.order_by(Transaction.date.desc()).all()

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
    query = db.query(
        Transaction.id,
        Transaction.amount,
        Category.type.label("type"),
        Transaction.date,
        Transaction.comment,
        User.full_name.label("author_name"),
        Category.name.label("category_name")
    ).join(User, Transaction.user_id == User.id) \
        .join(Category, Transaction.category_id == Category.id) \
        .filter(
        Transaction.family_id == current_user.family_id,
        extract('year', Transaction.date) == year,
        extract('month', Transaction.date) == month
    )

    results = query.order_by(Transaction.date.desc()).all()

    total_income = sum(row.amount for row in results if row.type == 'income')
    total_expense = sum(row.amount for row in results if row.type == 'expense')

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "transactions": [
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
    }
