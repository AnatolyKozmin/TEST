import hashlib
import hmac
import json
import time
import urllib.parse
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TelegramWebAppUser:
    id: int
    username: str | None
    first_name: str | None
    last_name: str | None


def _parse_init_data(init_data: str) -> dict[str, str]:
    parsed = urllib.parse.parse_qs(init_data, strict_parsing=True)
    flat: dict[str, str] = {}
    for k, v in parsed.items():
        if not v:
            continue
        flat[k] = v[0]
    return flat


def _data_check_string(params: dict[str, str]) -> str:
    items = [(k, v) for k, v in params.items() if k != "hash"]
    items.sort(key=lambda x: x[0])
    return "\n".join([f"{k}={v}" for k, v in items])


def _expected_hash(bot_token: str, data_check_string: str) -> str:
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    return hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_telegram_init_data(init_data: str, bot_token: str, max_age_seconds: int) -> TelegramWebAppUser:
    params = _parse_init_data(init_data)
    their_hash = params.get("hash")
    if not their_hash:
        raise ValueError("initData hash missing")

    dcs = _data_check_string(params)
    our_hash = _expected_hash(bot_token, dcs)
    if not hmac.compare_digest(our_hash, their_hash):
        raise ValueError("initData hash mismatch")

    auth_date_s = params.get("auth_date")
    if not auth_date_s:
        raise ValueError("auth_date missing")
    auth_date = int(auth_date_s)
    now = int(time.time())
    if now - auth_date > max_age_seconds:
        raise ValueError("initData is too old")

    user_raw = params.get("user")
    if not user_raw:
        raise ValueError("user missing")
    user_obj: dict[str, Any] = json.loads(user_raw)
    user_id = int(user_obj["id"])

    return TelegramWebAppUser(
        id=user_id,
        username=user_obj.get("username"),
        first_name=user_obj.get("first_name"),
        last_name=user_obj.get("last_name"),
    )

