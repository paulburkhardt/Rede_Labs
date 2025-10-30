from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.metadata import PhaseResponse, PhaseUpdateRequest
from app.services.phase_manager import get_current_phase, set_current_phase

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

