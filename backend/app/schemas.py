from enum import Enum
from typing import Any

from pydantic import BaseModel


class Discipline(str, Enum):
    CS2 = "CS2"
    DOTA2 = "DOTA2"
    FC26 = "FC26"


class RegistrationMode(str, Enum):
    team = "team"
    individual = "individual"


class DraftPayload(BaseModel):
    discipline: Discipline | None = None
    mode: RegistrationMode | None = None
    data: dict[str, Any] = {}


class DraftResponse(BaseModel):
    draft: DraftPayload | None

