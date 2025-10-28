from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.schemas.purchase import PurchaseCreate, PurchaseResponse
from app.models.purchase import Purchase
from app.models.product import Product
from app.models.buyer import Buyer

router = APIRouter(prefix="/buy", tags=["purchases"])

# todo: make sure api endpoints only get called if the phase where they are allowed (seller & buyer phase)

@router.post("/{product_id}", response_model=PurchaseResponse)
def create_purchase(
    product_id: str,
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
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create purchase record
    db_purchase = Purchase(
        product_id=product_id,
        buyer_id=buyer.id,
        purchased_at=purchase.purchased_at
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    return PurchaseResponse(
        id=db_purchase.id,
        product_id=db_purchase.product_id
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


@router.get("/stats/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    """
    Get the leaderboard with total revenue and purchase count per seller.
    Returns a list of sellers sorted by total revenue (descending).
    """
    from app.models.seller import Seller
    from sqlalchemy import case
    
    # Query to calculate total revenue and purchase count per seller
    # Only sum prices where there's an actual purchase (Purchase.id is not null)
    results = (
        db.query(
            Seller.id,
            func.count(Purchase.id).label("purchase_count"),
            func.coalesce(
                func.sum(
                    case(
                        (Purchase.id.isnot(None), Product.price_in_cent),
                        else_=0
                    )
                ),
                0
            ).label("total_revenue_cents")
        )
        .outerjoin(Product, Product.seller_id == Seller.id)
        .outerjoin(Purchase, Purchase.product_id == Product.id)
        .group_by(Seller.id)
        .order_by(
            func.coalesce(
                func.sum(
                    case(
                        (Purchase.id.isnot(None), Product.price_in_cent),
                        else_=0
                    )
                ),
                0
            ).desc()
        )
        .all()
    )
    
    return [
        {
            "seller_id": result.id,
            "purchase_count": result.purchase_count,
            "total_revenue_cents": result.total_revenue_cents,
            "total_revenue_dollars": result.total_revenue_cents / 100.0
        }
        for result in results
    ]
