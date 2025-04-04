from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import asyncio

from src.config import get_settings
from src.telegram.router import router

settings = get_settings()


async def main():
    dp = Dispatcher()
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp.include_router(router)
    # dp.message.outer_middleware(UserAllowedMiddleware())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
