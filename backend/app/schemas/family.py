from pydantic import BaseModel, ConfigDict, Field
from typing import List
from app.schemas.user import UserResponse


class FamilyBase(BaseModel):
    name: str = Field(..., max_length=100, description="Название семьи (например, 'Семья Ивановых')")


class FamilyCreate(FamilyBase):
    pass


class FamilyJoin(BaseModel):
    invite_code: str = Field(..., description="Уникальный код приглашения")


class FamilyResponse(FamilyBase):
    id: int
    invite_code: str
    members: List[UserResponse] = []

    model_config = ConfigDict(from_attributes=True)
