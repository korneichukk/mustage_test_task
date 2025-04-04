from aiogram import F, Router, html
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from datetime import datetime
import aiohttp
import openpyxl
from io import BytesIO

from src.config import get_settings
from src.telegram.keyboards import actions
from src.telegram.utils import create_excel
from src.telegram.validators import validate_amount, validate_date


router = Router()
settings = get_settings()


class AddExpense(StatesGroup):
    title = State()
    date = State()
    amount = State()


class DateRange(StatesGroup):
    start_date = State()
    end_date = State()


class DeleteExpense(StatesGroup):
    expense_id = State()


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


@router.callback_query(F.data == "report")
async def get_expenses(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DateRange.start_date)

    await callback.answer()
    await callback.message.answer("Enter start date of the period (format: [dd.mm.yyyy]).")  # type: ignore


@router.message(DateRange.start_date)
async def get_expenses_end_date(message: Message, state: FSMContext):
    start_date = message.text or ""
    if not validate_date(start_date):
        await message.answer(
            "Invalid date format! Please, try again, using format [dd.mm.yyyy] or check the date correctness."
        )
        return

    try:
        start_date_obj = datetime.strptime(start_date, "%d.%m.%Y")
        formatted_start_date = start_date_obj.strftime("%Y-%m-%d")
    except ValueError:
        await message.answer(
            "Invalid date format! Please, use the format [dd.mm.yyyy]."
        )
        return

    await state.update_data(start_date=formatted_start_date)
    await state.set_state(DateRange.end_date)

    await message.answer("Enter end date of the period (format: [dd.mm.yyyy]).")  # type: ignore


@router.message(DateRange.end_date)
async def get_expenses_data(message: Message, state: FSMContext):
    end_date = message.text or ""
    if not validate_date(end_date):
        await message.answer(
            "Invalid date format! Please, try again, using format [dd.mm.yyyy] or check the date correctness."
        )
        return

    try:
        end_date_obj = datetime.strptime(end_date, "%d.%m.%Y")
        formatted_end_date = end_date_obj.strftime("%Y-%m-%d")
    except ValueError:
        await message.answer(
            "Invalid date format! Please, use the format [dd.mm.yyyy]."
        )
        return

    data = await state.get_data()
    start_date = data.get("start_date", "")
    telegram_user_id = str(message.from_user.id)  # type: ignore

    params = {
        "expense_telegram_user_id": telegram_user_id,
        "start_date": start_date,
        "end_date": formatted_end_date,
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                "http://localhost:8000/expenses", params=params
            ) as response:
                if response.status == 200:
                    expenses = await response.json()
                    if expenses:
                        save_path = (
                            settings.PROJECT_ROOT / "expenses_data" / telegram_user_id
                        )
                        save_path.mkdir(parents=True, exist_ok=True)

                        file_path = create_excel(
                            expenses, save_path, start_date, end_date
                        )
                        input_file = FSInputFile(file_path)
                        await message.answer_document(
                            document=input_file,
                            caption="Here is generated report.",
                        )
                    else:
                        await message.answer(
                            f"No expenses found for the specified date range."
                        )
                else:
                    await message.answer(
                        f"Failed to retrieve expenses. Error: {response.status}"
                    )
        except Exception as e:
            await message.answer(
                f"An error occurred while processing the request: {str(e)}"
            )

    await state.clear()

    await message.answer(
        "Operation complete. Choose an action:",
        reply_markup=actions,
    )


@router.callback_query(F.data == "delete_expense")
async def delete_expense(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DeleteExpense.expense_id)

    await callback.answer()
    await callback.message.answer("Fetching your expenses...")  # type: ignore

    telegram_user_id = str(callback.from_user.id)  # type: ignore
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"http://localhost:8000/expenses?expense_telegram_user_id={telegram_user_id}"
            ) as response:
                if response.status == 200:
                    expenses = await response.json()
                    if expenses:
                        save_path = (
                            settings.PROJECT_ROOT / "expenses_data" / telegram_user_id
                        )
                        save_path.mkdir(parents=True, exist_ok=True)

                        file_path = create_excel(expenses, save_path, None, None)
                        input_file = FSInputFile(file_path)
                        await callback.message.answer_document(  # type: ignore
                            document=input_file,
                            caption="Here is generated report.",
                        )
                    else:
                        await callback.message.answer("You don't have any expenses.")
                else:
                    await callback.message.answer(
                        f"Failed to fetch your expenses. Error: {response.status}"
                    )
        except Exception as e:
            await callback.message.answer(
                f"An error occurred while fetching your expenses: {str(e)}"
            )

    await state.set_state(DeleteExpense.expense_id)
    await callback.message.answer("Enter exense_id you want to delete.")  # type: ignore


@router.message(DeleteExpense.expense_id)
async def delete_expense_by_id(message: Message, state: FSMContext):
    expense_id = message.text.strip()

    if not expense_id:
        await message.answer("Please provide a valid expense ID.")
        return

    async with aiohttp.ClientSession() as session:
        try:
            async with session.delete(
                f"http://localhost:8000/expense/{expense_id}"
            ) as response:
                if response.status == 200:
                    await message.answer(
                        f"Expense with ID {expense_id} has been successfully deleted."
                    )
                else:
                    await message.answer(
                        f"Failed to delete expense. Error: {response.status}"
                    )
        except Exception as e:
            await message.answer(
                f"An error occurred while deleting the expense: {str(e)}"
            )

    await state.clear()

    # Provide feedback to the user and show them the options to continue
    await message.answer(
        "Operation complete. Choose an action:",
        reply_markup=actions,
    )
