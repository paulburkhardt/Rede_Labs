from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.database import get_db
from app.schemas.seller import SellerResponse, SalesStatsResponse, PurchaseInfo
from app.models.seller import Seller
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.buyer import Buyer
from app.config import settings
from app.services.round_manager import get_current_round

router = APIRouter(prefix="", tags=["sellers"])


class CreateSellerRequest(BaseModel):
    battle_id: str


@router.post("/createSeller", response_model=SellerResponse)
def create_seller(
    request: CreateSellerRequest,
    db: Session = Depends(get_db),
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")
):
    """
    Create a new seller for a specific battle.
    White agents use this endpoint to create their seller.
    Returns the seller with an auth_token encoding seller_id and battle_id.
    """
    # Validate admin key
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing admin key")
    
    print(f"Creating seller for battle {request.battle_id}")
    
    # Generate seller ID upfront
    seller_id = str(uuid.uuid4())
    
    # Generate auth token encoding seller_id and battle_id
    auth_token = Seller.generate_auth_token(seller_id, request.battle_id)
    
    # Create new seller with ID and token
    db_seller = Seller(
        id=seller_id,
        battle_id=request.battle_id,
        auth_token=auth_token
    )
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
    Returns all purchases made for the seller's products in the current battle.
    Requires Authorization header with seller token.
    """
    # Extract token from Authorization header
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # Decode token to get seller_id and battle_id
    decoded = Seller.decode_auth_token(token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid authentication token format")
    
    seller_id, battle_id = decoded
    
    # Verify seller exists and token is valid
    seller = db.query(Seller).filter(
        Seller.id == seller_id,
        Seller.battle_id == battle_id,
        Seller.auth_token == token
    ).first()
    if not seller:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    current_round = get_current_round(db, battle_id)

    seller_products = db.query(Product).filter(
        Product.seller_id == seller.id,
        Product.battle_id == battle_id
    ).all()
    product_ids = [product.id for product in seller_products]

    if not product_ids:
        return SalesStatsResponse(
            seller_id=seller.id,
            total_sales=0,
            total_revenue_in_cent=0,
            purchases=[],
        )

    purchases = (
        db.query(Purchase)
        .filter(
            Purchase.product_id.in_(product_ids),
            Purchase.battle_id == battle_id,
            Purchase.round == current_round,
        )
        .all()
    )

    products_by_id = {product.id: product for product in seller_products}
    buyer_ids = {purchase.buyer_id for purchase in purchases}
    buyers_by_id = {
        buyer.id: buyer
        for buyer in db.query(Buyer).filter(
            Buyer.id.in_(buyer_ids),
            Buyer.battle_id == battle_id
        ).all()
    } if buyer_ids else {}

    total_revenue = 0
    purchase_infos = []

    for purchase in purchases:
        product = products_by_id.get(purchase.product_id)
        buyer = buyers_by_id.get(purchase.buyer_id)

        if not product or not buyer:
            continue

        total_revenue += purchase.price_of_purchase
        purchase_infos.append(
            PurchaseInfo(
                id=purchase.id,
                product_id=product.id,
                product_name=product.name,
                buyer_id=buyer.id,
                price_in_cent=purchase.price_of_purchase,
                currency=product.currency,
                purchased_at=purchase.purchased_at,
                round=purchase.round,
            )
        )
    
    return SalesStatsResponse(
        seller_id=seller.id,
        total_sales=len(purchase_infos),
        total_revenue_in_cent=total_revenue,
        purchases=purchase_infos
    )

