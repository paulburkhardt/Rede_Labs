from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.metadata import Metadata
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
    battle_id: str,
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> PhaseResponse:
    """Return the currently active marketplace phase for a specific battle."""
    current_phase = get_current_phase(db, battle_id)
    return PhaseResponse(phase=current_phase)


@router.post("/phase", response_model=PhaseResponse)
def update_phase(
    phase_update: PhaseUpdateRequest,
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> PhaseResponse:
    """Update the marketplace phase for a specific battle."""
    new_phase = set_current_phase(db, phase_update.battle_id, phase_update.phase)
    return PhaseResponse(phase=new_phase)


@router.get("/day", response_model=DayResponse)
def get_day(
    battle_id: str,
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> DayResponse:
    """Return the currently configured marketplace day for a specific battle."""
    current_day = get_current_day(db, battle_id)
    return DayResponse(day=current_day)


@router.post("/day", response_model=DayResponse)
def update_day(
    day_update: DayUpdateRequest,
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> DayResponse:
    """Update the marketplace day for a specific battle."""
    new_day = set_current_day(db, day_update.battle_id, day_update.day)
    return DayResponse(day=new_day)


@router.get("/round", response_model=RoundResponse)
def get_round(
    battle_id: str,
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> RoundResponse:
    """Return the currently configured simulation round for a specific battle."""
    current_round = get_current_round(db, battle_id)
    return RoundResponse(round=current_round)


@router.post("/round", response_model=RoundResponse)
def update_round(
    round_update: RoundUpdateRequest,
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> RoundResponse:
    """Update the simulation round for a specific battle."""
    new_round = set_current_round(db, round_update.battle_id, round_update.round)
    return RoundResponse(round=new_round)

@router.post("/metadata")
def store_battle_metadata(
    metadata: dict,
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> dict:
    """Store battle context metadata (battle_id and backend_url) for agents to retrieve."""
    battle_id = metadata.get("battle_id")
    backend_url = metadata.get("backend_url")
    
    if not battle_id or not backend_url:
        raise HTTPException(status_code=400, detail="battle_id and backend_url are required")
    
    # Store or update battle_id
    battle_id_meta = db.query(Metadata).filter(Metadata.key == "battle_id").first()
    if battle_id_meta:
        battle_id_meta.value = battle_id
    else:
        battle_id_meta = Metadata(key="battle_id", value=battle_id)
        db.add(battle_id_meta)
    
    # Store or update backend_url
    backend_url_meta = db.query(Metadata).filter(Metadata.key == "backend_url").first()
    if backend_url_meta:
        backend_url_meta.value = backend_url
    else:
        backend_url_meta = Metadata(key="backend_url", value=backend_url)
        db.add(backend_url_meta)
    
    db.commit()
    
    return {"status": "success", "battle_id": battle_id, "backend_url": backend_url}


@router.get("/metadata")
def get_battle_metadata(
    db: Session = Depends(get_db),
) -> dict:
    """Retrieve battle context metadata. No auth required so agents can read it."""
    battle_id_meta = db.query(Metadata).filter(Metadata.key == "battle_id").first()
    backend_url_meta = db.query(Metadata).filter(Metadata.key == "backend_url").first()
    
    return {
        "battle_id": battle_id_meta.value if battle_id_meta else None,
        "backend_url": backend_url_meta.value if backend_url_meta else None
    }


@router.post("/metadata/seller_names")
def store_seller_names(
    data: dict,
    _: None = Depends(ensure_admin_key),
    db: Session = Depends(get_db),
) -> dict:
    """Store seller ID to name mapping."""
    import json
    seller_names = data.get("seller_names", {})
    
    # Store as JSON string in metadata
    seller_names_meta = db.query(Metadata).filter(Metadata.key == "seller_names").first()
    if seller_names_meta:
        seller_names_meta.value = json.dumps(seller_names)
    else:
        seller_names_meta = Metadata(key="seller_names", value=json.dumps(seller_names))
        db.add(seller_names_meta)
    
    db.commit()
    
    return {"status": "success", "seller_names": seller_names}


@router.get("/metadata/seller_names")
def get_seller_names(
    db: Session = Depends(get_db),
) -> dict:
    """Retrieve seller ID to name mapping. No auth required so agents can read it."""
    import json
    seller_names_meta = db.query(Metadata).filter(Metadata.key == "seller_names").first()
    
    if seller_names_meta:
        return {"seller_names": json.loads(seller_names_meta.value)}
    else:
        return {"seller_names": {}}
