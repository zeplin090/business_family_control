from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Numeric, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from decimal import Decimal

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.family import Family
    from app.models.category import Category


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, default=func.current_date())
    comment: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    category: Mapped["Category"] = relationship(back_populates="transactions")
    user: Mapped["User"] = relationship()
    family: Mapped["Family"] = relationship()
