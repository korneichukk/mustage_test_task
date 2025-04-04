from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

actions = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Add Expense", callback_data="add_expense")],
        [InlineKeyboardButton(text="Update Expense", callback_data="edit_expense")],
        [InlineKeyboardButton(text="Delete Expense", callback_data="delete_expense")],
        [InlineKeyboardButton(text="Get Report", callback_data="report")],
    ]
)
