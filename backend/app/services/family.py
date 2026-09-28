import secrets
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.family import Family
from app.models.user import User, RoleEnum
from app.schemas.family import FamilyCreate


def generate_invite_code() -> str:
    return secrets.token_urlsafe(8)

class FamilyService:
    def __init__(self, db: Session):
        self.db = db


    def create_family(self, obj_in: FamilyCreate, current_user: User) -> Family:
        db_family = Family(
            name=obj_in.name,
            invite_code=generate_invite_code()
        )
        self.db.add(db_family)
        self.db.commit()
        self.db.refresh(db_family)

        current_user.family_id = db_family.id
        current_user.role = RoleEnum.ADMIN
        self.db.add(current_user)
        self.db.commit()

        self.db.refresh(db_family)
        return db_family


    def get_family_by_code(self, invite_code: str) -> Family | None:
        stmt = select(Family).where(Family.invite_code == invite_code)
        return self.db.execute(stmt).scalar_one_or_none()


    def join_family(self, family: Family, user: User) -> Family:
        user.family_id = family.id
        user.role = RoleEnum.MEMBER
        self.db.add(user)
        self.db.commit()
        self.db.refresh(family)
        return family
