from decimal import Decimal
from typing import Text
from sqlalchemy import Numeric, String, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date

from uuid import uuid4


class Base(DeclarativeBase):
    pass


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=lambda: str(uuid4())
    )
    telegram_user_id: Mapped[str] = mapped_column(String(255), nullable=False)

    amount_in_uah: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    amount_in_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    description: Mapped[str] = mapped_column(Text(255))
    expense_date: Mapped[date] = mapped_column(Date)

    def __repr__(self) -> str:
        return f"Expense(id={self.id}, uah={self.amount_in_uah}, usd={self.amount_in_usd}, date={self.expense_date.strftime("%d.%m.%Y")})"
