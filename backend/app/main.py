import io
import json
import logging
from typing import Any

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy import String, cast, desc, func, insert, or_, select

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


def _draft_key(tg_user_id: int) -> str:
    return f"draft:{tg_user_id}"


def _safe(v: Any) -> str:
    if v is None:
        return "-"
    s = str(v).strip()
    return s if s else "-"


def _build_submission_message(payload: DraftPayload) -> str:
    if payload.discipline == Discipline.GUEST:
        data = payload.data or {}
        fac = _safe(data.get("faculty"))
        if fac == "Другое":
            fac = _safe(data.get("faculty_other")) or fac
        return "\n".join(
            [
                "Регистрация зрителя успешно отправлена!",
                "",
                f"ФИО: {_safe(data.get('full_name'))}",
                f"Telegram: {_safe(data.get('telegram'))}",
                f"Факультет: {fac}",
            ]
        )

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
    discipline = draft.discipline
    mode = draft.mode
    kind = draft.registration_kind

    if kind == "guest" or discipline == Discipline.GUEST:
        normalized = DraftPayload(
            registration_kind="guest",
            discipline=Discipline.GUEST,
            mode=RegistrationMode.individual,
            data=draft.data or {},
        )
    else:
        if discipline == Discipline.FC26:
            mode = RegistrationMode.individual
        if discipline in (Discipline.CS2, Discipline.DOTA2):
            mode = RegistrationMode.team
        normalized = DraftPayload(
            registration_kind="participant",
            discipline=discipline,
            mode=mode,
            data=draft.data or {},
        )

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

    if draft.discipline == Discipline.GUEST:
        if draft.mode != RegistrationMode.individual:
            raise HTTPException(status_code=422, detail="GUEST требует индивидуальный тип")
        data = draft.data or {}
        for field in ("full_name", "telegram", "faculty"):
            v = data.get(field)
            if not v or not str(v).strip():
                raise HTTPException(status_code=422, detail=f"Поле {field} обязательно")
        if str(data.get("faculty", "")).strip() == "Другое":
            other = data.get("faculty_other")
            if not other or not str(other).strip():
                raise HTTPException(status_code=422, detail="Укажите факультет (поле «Другое»)")
    else:
        if draft.discipline == Discipline.FC26 and draft.mode != RegistrationMode.individual:
            raise HTTPException(status_code=422, detail="FC26 требует индивидуальную регистрацию")

        if draft.discipline in (Discipline.CS2, Discipline.DOTA2) and draft.mode != RegistrationMode.team:
            raise HTTPException(status_code=422, detail="Для CS2 и Dota2 доступна только командная регистрация")

    payload = DraftPayload(
        registration_kind=draft.registration_kind,
        discipline=draft.discipline,
        mode=draft.mode,
        data=draft.data or {},
    ).model_dump()

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
async def admin_stats():
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


@app.get("/api/admin/registrations")
async def admin_registrations(
    discipline: str | None = None,
    mode: str | None = None,
    q: str | None = None,
    limit: int = 30,
    offset: int = 0,
):
    safe_limit = max(1, min(limit, 100))
    safe_offset = max(0, offset)

    async with SessionLocal() as session:
        query = select(Registration)
        count_query = select(func.count()).select_from(Registration)

        if discipline:
            query = query.where(Registration.discipline == discipline)
            count_query = count_query.where(Registration.discipline == discipline)
        if mode:
            query = query.where(Registration.mode == mode)
            count_query = count_query.where(Registration.mode == mode)
        if q:
            needle = f"%{q.strip()}%"
            search_condition = or_(
                Registration.tg_username.ilike(needle),
                cast(Registration.tg_user_id, String).ilike(needle),
                cast(Registration.payload, String).ilike(needle),
            )
            query = query.where(search_condition)
            count_query = count_query.where(search_condition)

        total = (await session.execute(count_query)).scalar_one()
        rows = (
            await session.execute(
                query.order_by(desc(Registration.submitted_at), desc(Registration.id))
                .limit(safe_limit)
                .offset(safe_offset)
            )
        ).scalars().all()

    return {
        "total": int(total or 0),
        "limit": safe_limit,
        "offset": safe_offset,
        "items": [
            {
                "id": r.id,
                "tg_user_id": r.tg_user_id,
                "tg_username": r.tg_username,
                "tg_first_name": r.tg_first_name,
                "tg_last_name": r.tg_last_name,
                "discipline": r.discipline,
                "mode": r.mode,
                "payload": r.payload,
                "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
            }
            for r in rows
        ],
    }


def _safe_str(v: Any) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    return s if s else ""


def _build_excel_export(rows: list) -> bytes:
    wb = Workbook()
    wb.remove(wb.active)

    by_sheet: dict[str, list] = {}
    for r in rows:
        key = f"{r.discipline}_{r.mode}"
        if key not in by_sheet:
            by_sheet[key] = []
        by_sheet[key].append(r)

    for sheet_name, regs in sorted(by_sheet.items()):
        ws = wb.create_sheet(title=sheet_name[:31])

        if regs and regs[0].mode == "team":
            headers = [
                "ID", "TG User ID", "TG Username", "Дата заявки",
                "Игрок 1 (ФИО)", "Ник", "Steam", "Faceit", "Факультет", "TG",
                "Игрок 2 (ФИО)", "Ник", "Steam", "Faceit", "Факультет", "TG",
                "Игрок 3 (ФИО)", "Ник", "Steam", "Faceit", "Факультет", "TG",
                "Игрок 4 (ФИО)", "Ник", "Steam", "Faceit", "Факультет", "TG",
                "Игрок 5 (ФИО)", "Ник", "Steam", "Faceit", "Факультет", "TG",
                "Запас 1", "Запас 2", "Запас 3",
            ]
            ws.append(headers)
            for r in regs:
                data = r.payload or {}
                inner = data.get("data", data)
                players = (inner.get("team_players") if isinstance(inner, dict) else []) or []
                if not isinstance(players, list):
                    players = []
                row = [
                    r.id,
                    r.tg_user_id,
                    _safe_str(r.tg_username),
                    (r.submitted_at.isoformat()[:19] if r.submitted_at else ""),
                ]
                for i in range(8):
                    p = players[i] if i < len(players) and isinstance(players[i], dict) else {}
                    if i < 5:
                        row.extend([
                            _safe_str(p.get("full_name")),
                            _safe_str(p.get("game_nick")),
                            _safe_str(p.get("steam_url")),
                            _safe_str(p.get("faceit_url")),
                            _safe_str(p.get("faculty")) or _safe_str(p.get("faculty_other")),
                            _safe_str(p.get("telegram")),
                        ])
                    else:
                        row.append(_safe_str(p.get("full_name")) + " | " + _safe_str(p.get("game_nick")))
                ws.append(row)
        elif regs and getattr(regs[0], "discipline", None) == "GUEST":
            headers = ["ID", "TG User ID", "TG Username", "Дата заявки", "ФИО", "Telegram", "Факультет"]
            ws.append(headers)
            for r in regs:
                data = r.payload or {}
                inner = data.get("data", data)
                if not isinstance(inner, dict):
                    inner = {}
                fac = _safe_str(inner.get("faculty"))
                if fac == "Другое":
                    fac = _safe_str(inner.get("faculty_other")) or fac
                row = [
                    r.id,
                    r.tg_user_id,
                    _safe_str(r.tg_username),
                    (r.submitted_at.isoformat()[:19] if r.submitted_at else ""),
                    _safe_str(inner.get("full_name")),
                    _safe_str(inner.get("telegram")),
                    fac,
                ]
                ws.append(row)
        else:
            headers = ["ID", "TG User ID", "TG Username", "Дата заявки", "ФИО", "Ник", "Telegram"]
            ws.append(headers)
            for r in regs:
                data = r.payload or {}
                inner = data.get("data", data)
                if not isinstance(inner, dict):
                    inner = {}
                row = [
                    r.id,
                    r.tg_user_id,
                    _safe_str(r.tg_username),
                    (r.submitted_at.isoformat()[:19] if r.submitted_at else ""),
                    _safe_str(inner.get("full_name")),
                    _safe_str(inner.get("game_nick")),
                    _safe_str(inner.get("telegram")),
                ]
                ws.append(row)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@app.get("/api/admin/registrations/export")
async def admin_registrations_export():
    async with SessionLocal() as session:
        rows = (
            await session.execute(
                select(Registration)
                .order_by(Registration.discipline, Registration.mode, desc(Registration.submitted_at))
            )
        ).scalars().all()

    if not rows:
        raise HTTPException(status_code=404, detail="Нет заявок для экспорта")

    excel_bytes = _build_excel_export(rows)
    filename = "registrations.xlsx"
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

