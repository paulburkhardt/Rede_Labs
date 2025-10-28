from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func

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


@router.get("/stats/by-seller")
def get_purchases_per_seller(db: Session = Depends(get_db)):
    """
    Get the number of purchases per seller.
    Returns a list of sellers with their purchase counts.
    """
    from app.models.seller import Seller
    
    # Query to count purchases per seller
    results = (
        db.query(
            Seller.id,
            func.count(Purchase.id).label("purchase_count")
        )
        .outerjoin(Product, Product.seller_id == Seller.id)
        .outerjoin(Purchase, Purchase.product_id == Product.id)
        .group_by(Seller.id)
        .all()
    )
    
    return [
        {
            "seller_id": result.id,
            "purchase_count": result.purchase_count
        }
        for result in results
    ]
