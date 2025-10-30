from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.metadata import Metadata

DAY_KEY = "current_day"
DEFAULT_DAY = 0


def get_current_day(db: Session) -> int:
    """Return the currently configured simulated marketplace day."""
    record = db.query(Metadata).filter(Metadata.key == DAY_KEY).first()
    if record is None:
        return DEFAULT_DAY

    try:
        return int(record.value)
    except (TypeError, ValueError):
        return DEFAULT_DAY


def set_current_day(db: Session, day: int) -> int:
    """Persist the provided day value in metadata."""
    if day < 0:
        raise HTTPException(
            status_code=400,
            detail="Day must be a non-negative integer",
        )

    record = db.query(Metadata).filter(Metadata.key == DAY_KEY).first()
    if record is None:
        record = Metadata(key=DAY_KEY, value=str(day))
        db.add(record)
    else:
        record.value = str(day)

    db.commit()
    db.refresh(record)
    return day
