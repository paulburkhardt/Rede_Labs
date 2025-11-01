from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.metadata import (
    PhaseResponse,
    PhaseUpdateRequest,
    DayResponse,
    DayUpdateRequest,
    RoundResponse,
    RoundUpdateRequest,
)
from app.services.phase_manager import get_current_phase, set_current_phase
from app.services.day_manager import get_current_day, set_current_day
from app.services.round_manager import get_current_round, set_current_round

router = APIRouter(prefix="/admin", tags=["admin"])


def ensure_admin_key(
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")
) -> None:
    """Validate the admin API key header."""
    if settings.admin_api_key is None:
        return

    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing admin key")


@router.get("/phase", response_model=PhaseResponse)
def get_phase(
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> PhaseResponse:
    """Return the currently active marketplace phase."""
    current_phase = get_current_phase(db)
    return PhaseResponse(phase=current_phase)


@router.post("/phase", response_model=PhaseResponse)
def update_phase(
    phase_update: PhaseUpdateRequest,
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> PhaseResponse:
    """Update the marketplace phase."""
    new_phase = set_current_phase(db, phase_update.phase)
    return PhaseResponse(phase=new_phase)


@router.get("/day", response_model=DayResponse)
def get_day(
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> DayResponse:
    """Return the currently configured marketplace day."""
    current_day = get_current_day(db)
    return DayResponse(day=current_day)


@router.post("/day", response_model=DayResponse)
def update_day(
    day_update: DayUpdateRequest,
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> DayResponse:
    """Update the marketplace day."""
    new_day = set_current_day(db, day_update.day)
    return DayResponse(day=new_day)


@router.get("/round", response_model=RoundResponse)
def get_round(
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> RoundResponse:
    """Return the currently configured simulation round."""
    current_round = get_current_round(db)
    return RoundResponse(round=current_round)


@router.post("/round", response_model=RoundResponse)
def update_round(
    round_update: RoundUpdateRequest,
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> RoundResponse:
    """Update the simulation round."""
    new_round = set_current_round(db, round_update.round)
    return RoundResponse(round=new_round)
