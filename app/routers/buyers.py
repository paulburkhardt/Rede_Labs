from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.database import get_db
from app.schemas.buyer import BuyerResponse
from app.models.buyer import Buyer
from app.config import settings

router = APIRouter(prefix="", tags=["buyers"])


class CreateBuyerRequest(BaseModel):
    battle_id: str


@router.post("/createBuyer", response_model=BuyerResponse)
def create_buyer(
    request: CreateBuyerRequest,
    db: Session = Depends(get_db),
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
):
    """
    Create a new buyer account for a specific battle.
    Returns the buyer with an auth_token encoding buyer_id and battle_id.
    """
    # Validate admin key
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing admin key")
    
    # Generate buyer ID upfront
    buyer_id = str(uuid.uuid4())
    
    # Generate auth token encoding buyer_id and battle_id
    auth_token = Buyer.generate_auth_token(buyer_id, request.battle_id)
    
    # Create new buyer with ID and token
    db_buyer = Buyer(
        id=buyer_id,
        battle_id=request.battle_id,
        auth_token=auth_token
    )
    db.add(db_buyer)
    db.commit()
    db.refresh(db_buyer)
    
    return db_buyer

