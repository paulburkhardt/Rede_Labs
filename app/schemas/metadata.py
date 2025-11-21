from pydantic import BaseModel

from app.services.phase_manager import Phase


class PhaseResponse(BaseModel):
    phase: Phase


class PhaseUpdateRequest(BaseModel):
    battle_id: str
    phase: Phase


class DayResponse(BaseModel):
    day: int


class DayUpdateRequest(BaseModel):
    battle_id: str
    day: int


class RoundResponse(BaseModel):
    round: int


class RoundUpdateRequest(BaseModel):
    battle_id: str
    round: int

