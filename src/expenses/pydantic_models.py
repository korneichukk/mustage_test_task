from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class ExpenseBase(BaseModel):
    amount_in_uah: Decimal
    amount_in_usd: Decimal
    description: Optional[str] = None


class Expense(ExpenseBase):
    id: str

    class Config:
        from_attributes = True
