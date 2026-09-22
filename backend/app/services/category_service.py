from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.category import Category
from app.schemas.category_schema import CategoryCreate, CategoryUpdate


def get_categories(db: Session, family_id: int) -> list[Category]:
    stmt = select(Category).where(Category.family_id == family_id)
    return list(db.execute(stmt).scalars().all())


def get_category_by_id(db: Session, category_id: int, family_id: int) -> Category | None:
    stmt = select(Category).where(Category.id == category_id, Category.family_id == family_id)
    return db.execute(stmt).scalar_one_or_none()


def create_category(db: Session, obj_in: CategoryCreate, family_id: int) -> Category:
    db_obj = Category(
        name=obj_in.name,
        type=obj_in.type,
        monthly_limit=obj_in.monthly_limit,
        family_id=family_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_category(db: Session, db_obj: Category, obj_in: CategoryUpdate) -> Category:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_category(db: Session, db_obj: Category) -> None:
    try:
        db.delete(db_obj)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно удалить категорию: к ней привязаны существующие транзакции. Сначала удалите или перенесите их."
        )
