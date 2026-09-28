from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self, db: Session):
        self.db = db


    def get_categories(self, family_id: int) -> list[Category]:
        stmt = select(Category).where(Category.family_id == family_id)
        return list(self.db.execute(stmt).scalars().all())


    def get_category_by_id(self, category_id: int, family_id: int) -> Category | None:
        stmt = select(Category).where(Category.id == category_id, Category.family_id == family_id)
        return self.db.execute(stmt).scalar_one_or_none()


    def create_category(self, obj_in: CategoryCreate, family_id: int) -> Category:
        db_obj = Category(
            name=obj_in.name,
            type=obj_in.type,
            monthly_limit=obj_in.monthly_limit,
            family_id=family_id
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def update_category(self, db_obj: Category, obj_in: CategoryUpdate) -> Category:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def delete_category(self, db_obj: Category) -> None:
        try:
            self.db.delete(db_obj)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невозможно удалить категорию: к ней привязаны существующие транзакции. Сначала удалите или перенесите их."
            )