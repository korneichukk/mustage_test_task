from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query

from src.database import AsyncSessionLocal
from src.expenses.crud import (
    create_expense,
    delete_expense,
    get_all_user_expenses,
    get_all_user_expenses_on_date_range,
    update_expense,
)
from src.expenses.currency_parser import get_usd_to_uah
from src.expenses.pydantic_models import (
    Expense,
    ExpenseCreate,
    ExpenseUpdate,
)
from src.log import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/expense", response_model=Expense, status_code=status.HTTP_201_CREATED)
async def add_expense(expense: ExpenseCreate):
    usd_to_uah_result = get_usd_to_uah()
    if error := usd_to_uah_result["error"]:
        logger.warning(error)
        usd_to_uah_rate = 42
    else:
        usd_to_uah_rate = usd_to_uah_result["result"]

    async with AsyncSessionLocal() as session:
        new_expense = await create_expense(
            session,
            expense.telegram_user_id,
            expense.amount_in_uah,
            expense.amount_in_uah / Decimal(usd_to_uah_rate),
            expense.description or "",
            expense.expense_date,
        )
        return new_expense


@router.get("/expenses", response_model=List[Expense], status_code=status.HTTP_200_OK)
async def get_expenses(
    expense_telegram_user_id: str,
    start_date: Optional[str] = Query(
        None, alias="start_date", description="Start date in format yyyy-mm-dd"
    ),
    end_date: Optional[str] = Query(
        None, alias="end_date", description="End date in format yyyy-mm-dd"
    ),
):
    async with AsyncSessionLocal() as session:
        result = await get_all_user_expenses_on_date_range(
            session, expense_telegram_user_id, start_date=start_date, end_date=end_date
        )
        return result


@router.put("/expense", response_model=Expense, status_code=status.HTTP_200_OK)
async def change_expense(expense_update: ExpenseUpdate):
    usd_to_uah_result = get_usd_to_uah()
    if error := usd_to_uah_result["error"]:
        logger.warning(error)
        usd_to_uah_rate = 42
    else:
        usd_to_uah_rate = usd_to_uah_result["result"]

    async with AsyncSessionLocal() as session:
        result = await update_expense(
            session,
            expense_id=expense_update.id,
            telegram_user_id=expense_update.telegram_user_id,
            amount_in_uah=expense_update.amount_in_uah,
            amount_in_usd=expense_update.amount_in_uah / Decimal(usd_to_uah_rate),
            description=expense_update.description,
        )
        if not result:
            return HTTPException(
                status_code=404,
                detail=f"Expense with id [{expense_update.id}] was not found.",
            )

        return result


@router.delete("/expense/{expense_id}")
async def remove_expense(expense_id: str):
    async with AsyncSessionLocal() as session:
        result = await delete_expense(session, expense_id)

        if not result:
            return HTTPException(
                status_code=404, detail=f"Expense with id [{expense_id}] was not found."
            )

    return {"message": f"[{expense_id}] was deleted"}
