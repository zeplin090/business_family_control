from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.family import FamilyCreate, FamilyJoin, FamilyResponse
from app.services.family import FamilyService

router = APIRouter(prefix="/family", tags=["Family"])


@router.post("/", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
def create_new_family(
        family_in: FamilyCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    service = FamilyService(db=db)
    if current_user.family_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже состоит в семейной группе"
        )
    return service.create_family(db=db, obj_in=family_in, current_user=current_user)


@router.post("/join", response_model=FamilyResponse, status_code=status.HTTP_200_OK)
def join_existing_family(
        join_in: FamilyJoin,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    service = FamilyService(db=db)
    if current_user.family_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже состоит в семейной группе"
        )

    family = service.get_family_by_code(db, invite_code=join_in.invite_code)
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Неверный код приглашения"
        )

    return service.join_family(db=db, family=family, user=current_user)


@router.get("/me", response_model=FamilyResponse)
def get_my_family(
        current_user: User = Depends(get_current_user)
):
    if not current_user.family_id or not current_user.family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вы не состоите в семейной группе"
        )
    return current_user.family
