import secrets
from sqlalchemy.orm import Session
from app.models.family import Family
from app.models.user import User
from app.schemas.family import FamilyCreate
from app.repositories.family import FamilyRepository


def generate_invite_code() -> str:
    return secrets.token_urlsafe(8)

class FamilyService:
    def __init__(self, db: Session):
        self.repository = FamilyRepository(db)


    def create_family(self, obj_in: FamilyCreate, current_user: User) -> Family:
        return self.repository.create_family(obj_in=obj_in,
                                             current_user=current_user,
                                             invite_code=generate_invite_code())


    def get_family_by_code(self, invite_code: str) -> Family | None:
        return self.repository.get_family_by_code(invite_code=invite_code)


    def join_family(self, family: Family, user: User) -> Family:
        return self.repository.join_family(family=family, user=user)
