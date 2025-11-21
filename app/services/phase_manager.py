from enum import Enum
from typing import Iterable

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.metadata import Metadata


# If you change something here, also change it in agents/green_agent/green_agent_tools.py 
class Phase(str, Enum):
    """Lifecycle phases that gate marketplace operations."""

    #: Phase for seller management, where sellers can update listings
    SELLER_MANAGEMENT = "seller_management"
    #: Phase for buyer shopping, where buyers can purchase products
    BUYER_SHOPPING = "buyer_shopping"
    #: Phase for open marketplace, where all interactions are allowed
    OPEN = "open"


PHASE_KEY = "current_phase"
DEFAULT_PHASE = Phase.SELLER_MANAGEMENT


def get_current_phase(db: Session, battle_id: str) -> Phase:
    """Return the currently active marketplace phase for a specific battle."""
    record = db.query(Metadata).filter(
        Metadata.key == PHASE_KEY,
        Metadata.battle_id == battle_id
    ).first()
    if not record:
        return DEFAULT_PHASE

    try:
        return Phase(record.value)
    except ValueError:
        # Fallback to default if stored value is unexpected
        return DEFAULT_PHASE


def set_current_phase(db: Session, battle_id: str, phase: Phase) -> Phase:
    """Persist the given phase as the current marketplace phase for a specific battle."""
    record = db.query(Metadata).filter(
        Metadata.key == PHASE_KEY,
        Metadata.battle_id == battle_id
    ).first()

    if record is None:
        record = Metadata(key=PHASE_KEY, battle_id=battle_id, value=phase.value)
        db.add(record)
    else:
        record.value = phase.value

    db.commit()
    db.refresh(record)
    return phase


def ensure_phase(db: Session, battle_id: str, allowed_phases: Iterable[Phase]) -> Phase:
    """
    Ensure the active phase is one of the allowed phases for a specific battle.

    Raises:
        HTTPException: If the current phase is not permitted.
    """
    current_phase = get_current_phase(db, battle_id)

    allowed_set = set(allowed_phases)
    if current_phase == Phase.OPEN or current_phase in allowed_set:
        return current_phase

    allowed_labels = ", ".join(phase.value for phase in allowed_set) or "none"
    raise HTTPException(
        status_code=403,
        detail=(
            f"Operation not allowed during phase '{current_phase.value}'. "
            f"Allowed phases: {allowed_labels}"
        ),
    )

