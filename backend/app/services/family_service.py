import secrets
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.family import Family
from app.models.user import User, RoleEnum
from app.schemas.family_schema import FamilyCreate


def generate_invite_code() -> str:
    return secrets.token_urlsafe(8)


def create_family(db: Session, obj_in: FamilyCreate, current_user: User) -> Family:
    db_family = Family(
        name=obj_in.name,
        invite_code=generate_invite_code()
    )
    db.add(db_family)
    db.commit()
    db.refresh(db_family)

    current_user.family_id = db_family.id
    current_user.role = RoleEnum.ADMIN
    db.add(current_user)
    db.commit()

    db.refresh(db_family)
    return db_family


def get_family_by_code(db: Session, invite_code: str) -> Family | None:
    stmt = select(Family).where(Family.invite_code == invite_code)
    return db.execute(stmt).scalar_one_or_none()


def join_family(db: Session, family: Family, user: User) -> Family:
    user.family_id = family.id
    user.role = RoleEnum.MEMBER
    db.add(user)
    db.commit()
    db.refresh(family)
    return family
