from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Expense


async def create_expense(
    session: AsyncSession,
    telegram_user_id: str,
    amount_in_uah: Decimal,
    amount_in_usd: Decimal,
    description: str,
    date: date,
) -> Expense:
    new_expense = Expense(
        telegram_user_id=telegram_user_id,
        amount_in_uah=amount_in_uah,
        amount_in_usd=amount_in_usd,
        description=description,
        expense_date=date,
    )

    session.add(new_expense)
    await session.commit()
    return new_expense


async def get_all_expenses(session: AsyncSession) -> Optional[List[Expense]]:
    result = await session.execute(select(Expense))
    expenses = result.scalars().all()
    return list(expenses)


async def get_all_user_expenses(
    session: AsyncSession, telegram_user_id: str
) -> Optional[List[Expense]]:
    result = await session.execute(
        select(Expense).filter(Expense.telegram_user_id == telegram_user_id)
    )
    expenses = result.scalars().all()
    return list(expenses)


async def get_all_user_expenses_on_date_range(
    session: AsyncSession,
    telegram_user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Optional[List[Expense]]:
    query = select(Expense).filter(Expense.telegram_user_id == telegram_user_id)

    if start_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(Expense.expense_date >= start_date_obj)

    if end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.filter(Expense.expense_date <= end_date_obj)

    result = await session.execute(query)
    expenses = result.scalars().all()
    return list(expenses)


async def get_expense_by_id(
    session: AsyncSession, expense_id: str
) -> Optional[Expense]:
    result = await session.execute(select(Expense).filter(Expense.id == expense_id))
    expense = result.scalars().first()
    return expense


async def update_expense(
    session: AsyncSession, expense_id: str, **kwargs
) -> Optional[Expense]:
    expense = await get_expense_by_id(session, expense_id)
    if expense:
        for key, value in kwargs.items():
            if hasattr(expense, key):
                setattr(expense, key, value)
            session.add(expense)
            await session.commit()
    return expense


async def delete_expense(session, expense_id: str) -> bool:
    expense = await get_expense_by_id(session, expense_id)
    if expense:
        await session.delete(expense)
        await session.commit()
        return True
    return False
