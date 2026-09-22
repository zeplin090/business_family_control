from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.budget_schema import BudgetProgressResponse
from app.services import budget_service

router = APIRouter(prefix="/budget", tags=["Categories & Budgeting"])


@router.get("/progress", response_model=BudgetProgressResponse)
def get_budget_progress(
        year: int = Query(default_factory=lambda: date.today().year, description="Год"),
        month: int = Query(default_factory=lambda: date.today().month, ge=1, le=12, description="Месяц (1-12)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="Вы не состоите в семье")

    return budget_service.get_budget_progress(db, current_user.family_id, year, month)
