from aiogram import F, Router, html
from aiogram.types import CallbackQuery, Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from datetime import datetime
import aiohttp

from src.config import get_settings
from src.telegram.keyboards import actions
from src.telegram.validators import validate_amount, validate_date


router = Router()
settings = get_settings()


class AddExpense(StatesGroup):
    title = State()
    date = State()
    amount = State()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.reply(f"Hello, {html.bold(message.from_user.full_name)}!", reply_markup=actions)  # type: ignore


@router.callback_query(F.data == "add_expense")
async def new_expense(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddExpense.title)

    await callback.answer()
    await callback.message.answer("Enter expense title.")  # type: ignore


@router.message(AddExpense.title)
async def new_expense_date(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddExpense.date)

    await message.answer("Enter expense date (format: [dd.mm.yyyy])")  # type: ignore


@router.message(AddExpense.date)
async def new_expense_sum(message: Message, state: FSMContext):
    message_date = message.text or ""
    if not validate_date(message_date):
        await message.answer(
            "Invalid date format! Please, try again, using format [dd.mm.yyyy] or check the date correctness."
        )
        return

    # Convert the date to yyyy-mm-dd format
    try:
        date_obj = datetime.strptime(message_date, "%d.%m.%Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
    except ValueError:
        await message.answer(
            "Invalid date format! Please, use the format [dd.mm.yyyy]."
        )
        return

    await state.update_data(date=formatted_date)
    await state.set_state(AddExpense.amount)

    await message.answer("Enter the sum (in UAH).")


@router.message(AddExpense.amount)
async def new_expense_amount(message: Message, state: FSMContext):
    message_amount = message.text or ""
    if not validate_amount(message_amount):
        await message.answer("Invalid amount! Please enter a valid decimal number.")
        return

    await state.update_data(amount=message_amount)
    data = await state.get_data()

    payload = {
        "telegram_user_id": str(message.from_user.id),  # type: ignore
        "amount_in_uah": float(message_amount),
        "description": data.get("title", ""),
        "expense_date": data.get("date", ""),
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:8000/expense", json=payload
            ) as response:
                if response.status == 201:
                    await message.answer(f"Expense added successfully!")
                else:
                    await message.answer(
                        f"Failed to add expense. Error: {response.status}"
                    )
        except Exception as e:
            await message.answer(
                f"An error occurred while sending the expense data: {str(e)}"
            )

    await state.clear()

    await message.answer(
        "Operation complete. Choose an action:",
        reply_markup=actions,
    )
