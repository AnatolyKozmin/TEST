import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot_config import settings


dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="Открыть мини‑апп", web_app={"url": settings.webapp_url})
    await message.answer(
        "Регистрация на FCL/SCL 26.\n\nНажмите кнопку, чтобы открыть мини‑апп.",
        reply_markup=kb.as_markup(),
    )


@dp.message(F.text)
async def fallback(message: Message):
    await message.answer("Напишите /start, чтобы открыть мини‑апп.")


async def main():
    bot = Bot(settings.bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

