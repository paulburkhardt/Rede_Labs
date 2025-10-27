from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.seller import SellerResponse
from app.models.seller import Seller

router = APIRouter(prefix="", tags=["sellers"])


@router.post("/createSeller", response_model=SellerResponse)
def create_seller(
    db: Session = Depends(get_db)
):
    """
    Create a new seller.
    White agents use this endpoint to create their seller.
    Returns the seller with an auth_token for future API calls.
    """
    # Create new seller
    db_seller = Seller()
    db.add(db_seller)
    db.commit()
    db.refresh(db_seller)
    
    return db_seller
