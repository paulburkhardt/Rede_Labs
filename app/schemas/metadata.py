from pydantic import BaseModel

from app.services.phase_manager import Phase


class PhaseResponse(BaseModel):
    phase: Phase


class PhaseUpdateRequest(BaseModel):
    phase: Phase


class DayResponse(BaseModel):
    day: int


class DayUpdateRequest(BaseModel):
    day: int


class RoundResponse(BaseModel):
    round: int


class RoundUpdateRequest(BaseModel):
    round: int
