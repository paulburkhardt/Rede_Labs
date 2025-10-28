from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.seller import SellerResponse, SalesStatsResponse, PurchaseInfo
from app.models.seller import Seller
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.buyer import Buyer

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


@router.get("/getSalesStats", response_model=SalesStatsResponse)
def get_sales_stats(
    authorization: str = Header(..., description="Bearer token for seller"),
    db: Session = Depends(get_db)
):
    """
    Get sales statistics for the authenticated seller.
    Returns all purchases made for the seller's products.
    Requires Authorization header with seller token.
    """
    # Extract token from Authorization header
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # Verify seller exists and token is valid
    seller = db.query(Seller).filter(Seller.auth_token == token).first()
    if not seller:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    # Get all products for this seller
    seller_products = db.query(Product).filter(Product.seller_id == seller.id).all()
    product_ids = [product.id for product in seller_products]
    
    # Get all purchases for these products
    purchases = db.query(Purchase).filter(Purchase.product_id.in_(product_ids)).all()
    
    # Calculate statistics
    total_sales = len(purchases)
    total_revenue = 0
    purchase_infos = []
    
    for purchase in purchases:
        # Get product and buyer details
        product = db.query(Product).filter(Product.id == purchase.product_id).first()
        buyer = db.query(Buyer).filter(Buyer.id == purchase.buyer_id).first()
        
        if product and buyer:
            total_revenue += product.price_in_cent
            purchase_infos.append(PurchaseInfo(
                id=purchase.id,
                product_id=product.id,
                product_name=product.name,
                buyer_id=buyer.id,
                buyer_name=buyer.name,
                price_in_cent=product.price_in_cent,
                currency=product.currency,
                purchased_at=purchase.purchased_at
            ))
    
    return SalesStatsResponse(
        seller_id=seller.id,
        total_sales=total_sales,
        total_revenue_in_cent=total_revenue,
        purchases=purchase_infos
    )
