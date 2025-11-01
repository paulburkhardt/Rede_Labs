from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.metadata import Metadata

ROUND_KEY = "current_round"
DEFAULT_ROUND = 1


def get_current_round(db: Session) -> int:
    """Return the currently configured simulation round."""
    record = db.query(Metadata).filter(Metadata.key == ROUND_KEY).first()
    if record is None:
        return DEFAULT_ROUND

    try:
        return int(record.value)
    except (TypeError, ValueError):
        return DEFAULT_ROUND


def set_current_round(db: Session, round_number: int) -> int:
    """Persist the provided round value in metadata."""
    if round_number < 1:
        raise HTTPException(
            status_code=400,
            detail="Round must be a positive integer",
        )

    record = db.query(Metadata).filter(Metadata.key == ROUND_KEY).first()
    if record is None:
        record = Metadata(key=ROUND_KEY, value=str(round_number))
        db.add(record)
    else:
        record.value = str(round_number)

    db.commit()
    db.refresh(record)
    return round_number
