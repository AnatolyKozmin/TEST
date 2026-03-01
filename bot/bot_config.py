from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str
    webapp_url: str = "http://localhost:5173"
    stats_api_url: str = "http://backend:8000/api/admin/stats"
    admin_token: str = ""
    admin_user_ids: str = ""

    @property
    def parsed_admin_user_ids(self) -> set[int]:
        result: set[int] = set()
        raw = self.admin_user_ids.strip()
        if not raw:
            return result
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                result.add(int(part))
            except ValueError:
                continue
        return result


settings = Settings()

