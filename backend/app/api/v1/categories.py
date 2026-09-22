from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User, RoleEnum
from app.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["Categories & Budgeting"])


@router.get("/", response_model=list[CategoryResponse])
def read_categories(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.family_id:
        return []
    return category_service.get_categories(db, family_id=current_user.family_id)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
        category_in: CategoryCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="Вы не состоите в семье")

    return category_service.create_category(db, obj_in=category_in, family_id=current_user.family_id)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
        category_id: int,
        category_in: CategoryUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="Вы не состоите в семье")

    category = category_service.get_category_by_id(db, category_id, current_user.family_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    if category_in.monthly_limit is not None and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор семьи может устанавливать лимиты бюджета"
        )

    return category_service.update_category(db, db_obj=category, obj_in=category_in)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
        category_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="Вы не состоите в семье")

    category = category_service.get_category_by_id(db, category_id, current_user.family_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    # Право на удаление также можно ограничить администратором, если это нужно по бизнес-логике
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Только администратор может удалять категории")

    category_service.delete_category(db, db_obj=category)
    return None
