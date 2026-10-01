from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user import UserRepository

class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)


    def get_user_by_email(self, email: str) -> User | None:
        return self.repository.get_user_by_email(email=email)


    def create_user(self, user_in: UserCreate) -> User:
        return self.repository.create_user(user_in=user_in)


    def authenticate_user(self, email: str, password: str) -> User | None:
        return self.repository.authenticate_user(email=email, password=password)
