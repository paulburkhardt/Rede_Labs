from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.buyer import BuyerCreateRequest, BuyerResponse
from app.models.buyer import Buyer
from app.config import settings

router = APIRouter(prefix="", tags=["buyers"])


def _extract_bearer_token(authorization: str) -> str:
    """Return the bare token from an Authorization header."""
    if not authorization:
        return authorization
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return authorization


@router.post("/createBuyer", response_model=BuyerResponse)
def create_buyer(
    buyer_in: BuyerCreateRequest,
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
    db_buyer = Buyer(name=buyer_in.name)
    db.add(db_buyer)
    db.commit()
    db.refresh(db_buyer)
    
    return db_buyer


@router.get("/buyer/me", response_model=BuyerResponse)
def get_buyer_profile(
    authorization: str = Header(..., alias="Authorization", description="Bearer token for buyer"),
    db: Session = Depends(get_db),
):
    """
    Return the authenticated buyer based on the provided auth token.
    """
    token = _extract_bearer_token(authorization)
    buyer = db.query(Buyer).filter(Buyer.auth_token == token).first()

    if not buyer:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    return buyer
