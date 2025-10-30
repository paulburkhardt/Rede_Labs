from pydantic import BaseModel

from app.services.phase_manager import Phase


class PhaseResponse(BaseModel):
    phase: Phase


class PhaseUpdateRequest(BaseModel):
    phase: Phase

