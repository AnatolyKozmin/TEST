import asyncio

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot_config import settings


dp = Dispatcher()


def _is_admin(message: Message) -> bool:
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        return False
    return user_id in settings.parsed_admin_user_ids


def _render_stats(data: dict) -> str:
    total = data.get("total_registrations", 0)
    unique = data.get("unique_users", 0)
    by_discipline = data.get("by_discipline", []) or []
    by_mode = data.get("by_mode", []) or []
    recent = data.get("recent", []) or []

    lines = [
        "Статистика регистраций",
        "",
        f"Всего заявок: {total}",
        f"Уникальных пользователей: {unique}",
        "",
        "По дисциплинам:",
    ]
    if by_discipline:
        for item in by_discipline:
            lines.append(f"- {item.get('discipline')}: {item.get('count')}")
    else:
        lines.append("- нет данных")

    lines.append("")
    lines.append("По типу:")
    if by_mode:
        for item in by_mode:
            lines.append(f"- {item.get('mode')}: {item.get('count')}")
    else:
        lines.append("- нет данных")

    lines.append("")
    lines.append("Последние заявки:")
    if recent:
        for item in recent[:8]:
            lines.append(
                f"- #{item.get('id')} | {item.get('discipline')}/{item.get('mode')} | "
                f"@{item.get('tg_username') or '-'} | {item.get('submitted_at') or '-'}"
            )
    else:
        lines.append("- нет данных")

    return "\n".join(lines)


@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="Открыть мини‑апп", web_app={"url": settings.webapp_url})
    await message.answer(
        "Регистрация на FCL 26.\n\n"
        "Важно: не закрывайте страницу через крестик до отправки данных — иначе введённая информация "
        "может не сохраниться полностью.\n\n"
        "Если мини‑приложение не открывается или работает нестабильно, попробуйте временно отключить VPN "
        "и открыть его снова через кнопку ниже.\n\n"
        "Нажмите кнопку, чтобы открыть мини‑апп.",
        reply_markup=kb.as_markup(),
    )


@dp.message(Command("stats"))
async def stats(message: Message):
    if not _is_admin(message):
        await message.answer("Недостаточно прав для просмотра статистики.")
        return
    if not settings.admin_token:
        await message.answer("ADMIN_TOKEN не настроен в bot/.env.")
        return
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get(
                settings.stats_api_url,
                headers={"X-Admin-Token": settings.admin_token},
            )
        if resp.status_code != 200:
            await message.answer(f"Не удалось получить статистику: HTTP {resp.status_code}\n{resp.text[:300]}")
            return
        payload = resp.json()
        await message.answer(_render_stats(payload))
    except Exception as e:
        await message.answer(f"Ошибка запроса статистики: {e}")


@dp.message(F.text)
async def fallback(message: Message):
    await message.answer("Напишите /start, чтобы открыть мини‑апп.")


async def main():
    bot = Bot(settings.bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

