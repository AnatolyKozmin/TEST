import json
import logging
from typing import Any

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, func, insert, select

from .config import settings
from .db import Registration, SessionLocal, init_db
from .redis_client import redis
from .schemas import DraftPayload, DraftResponse, Discipline, RegistrationMode
from .telegram_auth import TelegramWebAppUser, verify_telegram_init_data


app = FastAPI(title="FCL Mini App API")
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_tg_user(x_telegram_init_data: str | None = Header(default=None)) -> TelegramWebAppUser:
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Missing X-Telegram-Init-Data")
    try:
        return verify_telegram_init_data(
            init_data=x_telegram_init_data,
            bot_token=settings.bot_token,
            max_age_seconds=settings.max_auth_age_seconds,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


def require_admin(x_admin_token: str | None = Header(default=None)):
    if not settings.admin_token:
        raise HTTPException(status_code=503, detail="Admin stats disabled: ADMIN_TOKEN is not configured")
    if not x_admin_token or x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Invalid admin token")


def _draft_key(tg_user_id: int) -> str:
    return f"draft:{tg_user_id}"


def _safe(v: Any) -> str:
    if v is None:
        return "-"
    s = str(v).strip()
    return s if s else "-"


def _build_submission_message(payload: DraftPayload) -> str:
    lines = [
        "Заявка успешно отправлена!",
        "",
        f"Дисциплина: {_safe(payload.discipline.value if payload.discipline else None)}",
        f"Тип: {_safe(payload.mode.value if payload.mode else None)}",
    ]

    data = payload.data or {}
    if payload.mode == RegistrationMode.team:
        players = data.get("team_players")
        if isinstance(players, list):
            lines.append("")
            lines.append("Состав команды:")
            for i, p in enumerate(players, start=1):
                if not isinstance(p, dict):
                    continue
                role = "осн." if i <= 5 else "зап."
                lines.append(
                    f"{i}. [{role}] {_safe(p.get('full_name'))} | ник: {_safe(p.get('game_nick'))} | tg: {_safe(p.get('telegram'))}"
                )
    else:
        lines.append("")
        lines.append("Данные участника:")
        lines.append(f"ФИО: {_safe(data.get('full_name'))}")
        lines.append(f"Ник: {_safe(data.get('game_nick'))}")
        lines.append(f"Telegram: {_safe(data.get('telegram'))}")

    return "\n".join(lines)


async def _send_telegram_notification(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(url, json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})
            if not res.is_success:
                logger.warning("Telegram sendMessage failed: chat_id=%s status=%s body=%s", chat_id, res.status_code, res.text)
    except Exception:
        logger.exception("Failed to send Telegram notification to chat_id=%s", chat_id)


@app.on_event("startup")
async def _startup():
    await init_db()


@app.get("/api/health")
async def health():
    return {"ok": True}


@app.get("/api/draft", response_model=DraftResponse)
async def get_draft(user: TelegramWebAppUser = Depends(get_tg_user)):
    raw = await redis.get(_draft_key(user.id))
    if not raw:
        return DraftResponse(draft=None)
    try:
        payload = DraftPayload.model_validate(json.loads(raw))
    except Exception:
        return DraftResponse(draft=None)
    return DraftResponse(draft=payload)


@app.put("/api/draft", status_code=204)
async def put_draft(draft: DraftPayload, user: TelegramWebAppUser = Depends(get_tg_user)):
    # Normalize: FC26 only individual; CS2/DOTA2 default team if omitted (frontend also enforces)
    discipline = draft.discipline
    mode = draft.mode

    if discipline == Discipline.FC26:
        mode = RegistrationMode.individual
    if discipline in (Discipline.CS2, Discipline.DOTA2) and mode is None:
        mode = RegistrationMode.team

    normalized = DraftPayload(discipline=discipline, mode=mode, data=draft.data or {})
    await redis.set(_draft_key(user.id), normalized.model_dump_json(), ex=settings.draft_ttl_seconds)
    return Response(status_code=204)


@app.post("/api/submit", status_code=204)
async def submit(
    draft: DraftPayload,
    background_tasks: BackgroundTasks,
    user: TelegramWebAppUser = Depends(get_tg_user),
    x_telegram_init_data: str | None = Header(default=None),
):
    if not draft.discipline or not draft.mode:
        raise HTTPException(status_code=422, detail="discipline and mode are required")

    if draft.discipline == Discipline.FC26 and draft.mode != RegistrationMode.individual:
        raise HTTPException(status_code=422, detail="FC26 требует индивидуальную регистрацию")

    if draft.discipline in (Discipline.CS2, Discipline.DOTA2) and draft.mode not in (
        RegistrationMode.team,
        RegistrationMode.individual,
    ):
        raise HTTPException(status_code=422, detail="Некорректный mode")

    payload = DraftPayload(discipline=draft.discipline, mode=draft.mode, data=draft.data or {}).model_dump()

    async with SessionLocal() as session:
        await session.execute(
            insert(Registration).values(
                tg_user_id=user.id,
                tg_username=user.username,
                tg_first_name=user.first_name,
                tg_last_name=user.last_name,
                discipline=draft.discipline.value,
                mode=draft.mode.value,
                payload=payload,
                source_init_data=x_telegram_init_data,
            )
        )
        await session.commit()

    message = _build_submission_message(draft)
    background_tasks.add_task(_send_telegram_notification, user.id, message)

    await redis.delete(_draft_key(user.id))
    return Response(status_code=204)


@app.get("/api/admin/stats")
async def admin_stats(_: None = Depends(require_admin)):
    async with SessionLocal() as session:
        total = (await session.execute(select(func.count()).select_from(Registration))).scalar_one()
        unique_users = (await session.execute(select(func.count(func.distinct(Registration.tg_user_id))))).scalar_one()

        by_discipline_rows = (
            await session.execute(
                select(Registration.discipline, func.count())
                .group_by(Registration.discipline)
                .order_by(desc(func.count()))
            )
        ).all()
        by_mode_rows = (
            await session.execute(
                select(Registration.mode, func.count()).group_by(Registration.mode).order_by(desc(func.count()))
            )
        ).all()
        recent_rows = (
            await session.execute(
                select(
                    Registration.id,
                    Registration.tg_user_id,
                    Registration.tg_username,
                    Registration.discipline,
                    Registration.mode,
                    Registration.submitted_at,
                ).order_by(desc(Registration.submitted_at)).limit(30)
            )
        ).all()

    return {
        "total_registrations": int(total or 0),
        "unique_users": int(unique_users or 0),
        "by_discipline": [{"discipline": d, "count": c} for d, c in by_discipline_rows],
        "by_mode": [{"mode": m, "count": c} for m, c in by_mode_rows],
        "recent": [
            {
                "id": r.id,
                "tg_user_id": r.tg_user_id,
                "tg_username": r.tg_username,
                "discipline": r.discipline,
                "mode": r.mode,
                "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
            }
            for r in recent_rows
        ],
    }

