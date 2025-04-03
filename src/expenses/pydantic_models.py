from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class ExpenseBase(BaseModel):
    amount_in_uah: Decimal
    description: Optional[str] = None


class ExpenseUpdate(ExpenseBase):
    id: str


class Expense(ExpenseBase):
    id: str
    amount_in_usd: Decimal

    class Config:
        from_attributes = True
