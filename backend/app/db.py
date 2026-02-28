from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .config import settings


class Base(DeclarativeBase):
    pass


class Registration(Base):
    __tablename__ = "registrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    tg_username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tg_first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tg_last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    discipline: Mapped[str] = mapped_column(String(16), nullable=False)
    mode: Mapped[str] = mapped_column(String(16), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source_init_data: Mapped[str | None] = mapped_column(Text, nullable=True)


engine: AsyncEngine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

