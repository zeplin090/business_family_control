from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User, RoleEnum
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories & Budgeting"])


@router.get("/", response_model=list[CategoryResponse])
def read_categories(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    service = CategoryService(db)
    if not current_user.family_id:
        return []
    return service.get_categories(family_id=current_user.family_id)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
        category_in: CategoryCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    service = CategoryService(db)
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="Вы не состоите в семье")

    return service.create_category(obj_in=category_in, family_id=current_user.family_id)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
        category_id: int,
        category_in: CategoryUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    service = CategoryService(db)
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="Вы не состоите в семье")

    category = service.get_category_by_id(category_id, current_user.family_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    if category_in.monthly_limit is not None and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор семьи может устанавливать лимиты бюджета"
        )

    return service.update_category(category, category_in)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
        category_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    Удалить категорию по ID.

    Требования:
    - Пользователь должен состоять в семье.
    - Пользователь должен иметь роль ADMIN.

    Возвращает 204 No Content при успехе.
    """
    service = CategoryService(db)
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="Вы не состоите в семье")

    
    category = service.get_category_by_id(category_id, current_user.family_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    # Право на удаление также можно ограничить администратором, если это нужно по бизнес-логике
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Только администратор может удалять категории")

    service.delete_category(category)
    return None
