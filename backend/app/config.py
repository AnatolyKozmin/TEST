from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/fcl"
    redis_url: str = "redis://redis:6379/0"

    cors_origins: str = "http://localhost:5173"
    draft_ttl_seconds: int = 60 * 60 * 24 * 7
    max_auth_age_seconds: int = 60 * 60 * 24


settings = Settings()

