from decimal import Decimal
from typing import Text
from sqlalchemy import Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from uuid import uuid4


class Base(DeclarativeBase):
    pass


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=lambda: str(uuid4())
    )

    amount_in_uah: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    amount_in_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    description: Mapped[str] = mapped_column(Text(255))

    def __repr__(self) -> str:
        return (
            f"Expense(id={self.id}, uah={self.amount_in_uah}, usd={self.amount_in_usd})"
        )
