import enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.family import Family


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"
    OBSERVER = "observer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        SQLEnum(RoleEnum),
        default=RoleEnum.MEMBER,
        nullable=False
    )
    family_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("families.id", ondelete="SET NULL"),
        nullable=True
    )
    family: Mapped[Optional["Family"]] = relationship(back_populates="members")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
