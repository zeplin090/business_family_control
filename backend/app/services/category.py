from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.repositories.category import CategoryRepository

class CategoryService:
    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)


    def get_categories(self, family_id: int) -> list[Category]:
        return self.repository.get_categories(family_id=family_id)


    def get_category_by_id(self, category_id: int, family_id: int) -> Category | None:
        return self.repository.get_category_by_id(category_id=category_id, 
                                                  family_id=family_id)


    def create_category(self, obj_in: CategoryCreate, family_id: int) -> Category:
        return self.repository.create_category(obj_in=obj_in, family_id=family_id)


    def update_category(self, db_obj: Category, obj_in: CategoryUpdate) -> Category:
        return self.repository.update_category(db_obj=db_obj, obj_in=obj_in)


    def delete_category(self, db_obj: Category) -> None:
        try:
            self.repository.delete(db_obj)
        except ValueError as e:
            if str(e) == "category_in_use":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Невозможно удалить категорию: к ней привязаны существующие транзакции. Сначала удалите или перенесите их."
                )
            raise e