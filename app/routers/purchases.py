from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.purchase import PurchaseCreate, PurchaseResponse
from app.models.purchase import Purchase
from app.models.product import Product
from app.models.buyer import Buyer

router = APIRouter(prefix="/buy", tags=["purchases"])


@router.post("/{productId}", response_model=PurchaseResponse)
def create_purchase(
    productId: str,
    purchase: PurchaseCreate,
    authorization: str = Header(..., description="Bearer token for buyer"),
    db: Session = Depends(get_db)
):
    """
    Simulate a product purchase.
    Customer agents use this endpoint to purchase products.
    Requires Authorization header with buyer token.
    """
    # Extract token from Authorization header
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # Verify buyer exists and token is valid
    buyer = db.query(Buyer).filter(Buyer.auth_token == token).first()
    if not buyer:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    # Verify product exists
    product = db.query(Product).filter(Product.id == productId).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create purchase record
    db_purchase = Purchase(
        product_id=productId,
        buyer_id=buyer.id
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    return PurchaseResponse(
        id=db_purchase.id,
        productId=db_purchase.product_id
    )
