from datetime import date
from pydantic import BaseModel, field_validator
from decimal import Decimal
from typing import Optional


class ExpenseBase(BaseModel):
    telegram_user_id: str
    amount_in_uah: Decimal
    description: Optional[str] = None


class ExpenseUpdate(ExpenseBase):
    id: str


class ExpenseCreate(ExpenseBase):
    expense_date: date


class Expense(ExpenseBase):
    id: str
    amount_in_usd: Decimal
    expense_date: date

    class Config:
        from_attributes = True

        json_encoders = {
            date: lambda v: v.strftime("%d.%m.%Y")  # Format date as dd.mm.YYYY
        }
