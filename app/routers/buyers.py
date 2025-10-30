from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.buyer import BuyerResponse
from app.models.buyer import Buyer
from app.config import settings

router = APIRouter(prefix="", tags=["buyers"])


@router.post("/createBuyer", response_model=BuyerResponse)
def create_buyer(
    db: Session = Depends(get_db),
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
):
    """
    Create a new buyer account.
    Returns the buyer with an auth_token for making purchases.
    """
    # Validate admin key
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing admin key")
    # Create new buyer
    db_buyer = Buyer()
    db.add(db_buyer)
    db.commit()
    db.refresh(db_buyer)
    
    return db_buyer
