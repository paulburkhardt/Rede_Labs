from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.buyer import BuyerCreate, BuyerResponse
from app.models.buyer import Buyer

router = APIRouter(prefix="", tags=["buyers"])


@router.post("/createBuyer", response_model=BuyerResponse)
def create_buyer(
    buyer: BuyerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new buyer account.
    Returns the buyer with an auth_token for making purchases.
    """
    # Create new buyer
    db_buyer = Buyer(name=buyer.name)
    db.add(db_buyer)
    db.commit()
    db.refresh(db_buyer)
    
    return db_buyer
