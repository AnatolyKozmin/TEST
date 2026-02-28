import json

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import insert

from .config import settings
from .db import Registration, SessionLocal, init_db
from .redis_client import redis
from .schemas import DraftPayload, DraftResponse, Discipline, RegistrationMode
from .telegram_auth import TelegramWebAppUser, verify_telegram_init_data


app = FastAPI(title="FCL Mini App API")

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
async def submit(draft: DraftPayload, user: TelegramWebAppUser = Depends(get_tg_user), x_telegram_init_data: str | None = Header(default=None)):
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

    await redis.delete(_draft_key(user.id))
    return Response(status_code=204)

