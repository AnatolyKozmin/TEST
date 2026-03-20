from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Discipline(str, Enum):
    CS2 = "CS2"
    DOTA2 = "DOTA2"
    FC26 = "FC26"
    GUEST = "GUEST"


class RegistrationMode(str, Enum):
    team = "team"
    individual = "individual"


class DraftPayload(BaseModel):
    registration_kind: Literal["participant", "guest"] = Field(default="participant")
    discipline: Discipline | None = None
    mode: RegistrationMode | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class DraftResponse(BaseModel):
    draft: DraftPayload | None

