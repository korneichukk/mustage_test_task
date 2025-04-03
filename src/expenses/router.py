from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status

from src.database import AsyncSessionLocal
from src.expenses.crud import (
    create_expense,
    delete_expense,
    get_all_expenses,
    update_expense,
)
from src.expenses.pydantic_models import Expense

router = APIRouter(prefix="/expenses")


@router.post("", response_model=Expense, status_code=status.HTTP_201_CREATED)
async def add_expense(amount_in_uah: Decimal, description: str):
    async with AsyncSessionLocal() as session:
        new_expense = await create_expense(
            session, amount_in_uah, amount_in_uah / Decimal(41.3), description
        )
        return new_expense


@router.get("", response_model=List[Expense], status_code=status.HTTP_200_OK)
async def get_expenses():
    async with AsyncSessionLocal() as session:
        result = await get_all_expenses(session)
        return result


@router.put("", response_model=Expense, status_code=status.HTTP_200_OK)
async def change_expense(
    expense_id: str, amount_in_uah: Decimal, description: Optional[str]
):
    async with AsyncSessionLocal() as session:
        result = await update_expense(
            session,
            expense_id=expense_id,
            amount_in_uah=amount_in_uah,
            amount_in_usd=amount_in_uah / Decimal(41.3),
            description=description,
        )
        if not result:
            return HTTPException(
                status_code=404, detail=f"Expense with id [{expense_id}] was not found."
            )

        return result


@router.delete("/{expense_id}")
async def remove_expense(expense_id: str):
    async with AsyncSessionLocal() as session:
        result = await delete_expense(session, expense_id)

        if not result:
            return HTTPException(
                status_code=404, detail=f"Expense with id [{expense_id}] was not found."
            )

    return {"message": f"[{expense_id}] was deleted"}
