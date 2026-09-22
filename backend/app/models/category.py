import enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.family import Family
    from app.models.transaction import Transaction


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType), nullable=False)
    monthly_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id", ondelete="CASCADE"), nullable=False)
    family: Mapped["Family"] = relationship()
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan"
    )
