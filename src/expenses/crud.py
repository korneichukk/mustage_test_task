from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Expense


async def create_expense(
    session: AsyncSession,
    amount_in_uah: Decimal,
    amount_in_usd: Decimal,
    description: str,
) -> Expense:
    new_expense = Expense(
        amount_in_uah=amount_in_uah,
        amount_in_usd=amount_in_usd,
        description=description,
    )

    session.add(new_expense)
    await session.commit()
    return new_expense


async def get_all_expenses(session: AsyncSession) -> Optional[List[Expense]]:
    result = await session.execute(select(Expense))
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
