from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductSearchResult,
    ProductDetail,
    BatchRankingUpdate
)
from app.models.product import Product
from app.models.seller import Seller

router = APIRouter(prefix="/product", tags=["products"])


@router.post("/{id}")
def create_product(
    id: str,
    product: ProductCreate,
    authorization: str = Header(..., description="Bearer token for seller"),
    db: Session = Depends(get_db)
):
    """
    Create a new product.
    White agents use this endpoint to create their product listings.
    Requires Authorization header with seller token.
    """
    # Extract token from Authorization header
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization

    # Verify seller exists and token is valid
    seller = db.query(Seller).filter(Seller.auth_token == token).first()
    if not seller:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    # Check if product with this ID already exists
    existing_product = db.query(Product).filter(Product.id == id).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this ID already exists")
    
    # Create new product
    db_product = Product(
        id=id,
        name=product.name,
        short_description=product.shortDescription,
        long_description=product.longDescription,
        price_in_cent=product.price,
        image_url=product.image.url,
        image_alternative_text=product.image.alternativText,
        seller_id=seller.id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return {"message": "Product created successfully", "product_id": db_product.id}


@router.patch("/{id}")
def update_product(
    id: str,
    product: ProductUpdate,
    authorization: str = Header(..., description="Bearer token for seller"),
    db: Session = Depends(get_db)
):
    """
    Update an existing product.
    White agents use this endpoint to update their own product listings.
    Requires Authorization header with seller token.
    """
    # Extract token from Authorization header
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # Verify seller exists and token is valid
    seller = db.query(Seller).filter(Seller.auth_token == token).first()
    if not seller:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    # Get the product
    db_product = db.query(Product).filter(Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verify the product belongs to this seller
    if db_product.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="You can only update your own products")
    
    # Update fields if provided
    if product.name is not None:
        db_product.name = product.name
    if product.shortDescription is not None:
        db_product.short_description = product.shortDescription
    if product.longDescription is not None:
        db_product.long_description = product.longDescription
    if product.price is not None:
        db_product.price_in_cent = product.price
    if product.image is not None:
        db_product.image_url = product.image.url
        db_product.image_alternative_text = product.image.alternativText
    if product.ranking is not None:
        db_product.ranking = product.ranking
    
    db.commit()
    db.refresh(db_product)
    
    return {"message": "Product updated successfully", "product_id": db_product.id}


@router.get("/{id}", response_model=ProductDetail)
def get_product(
    id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific product.
    """
    # Get the product with seller info
    db_product = db.query(Product).filter(Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Format response
    return ProductDetail(
        id=db_product.id,
        name=db_product.name,
        seller_id=db_product.seller_id,
        priceInCent=db_product.price_in_cent,
        currency=db_product.currency,
        bestseller=db_product.bestseller,
        shortDescription=db_product.short_description,
        longDescription=db_product.long_description,
        image={
            "url": db_product.image_url or "",
            "alternativText": db_product.image_alternative_text
        }
    )

# todo add security so only orchestration service can call this
@router.patch("/{id}/ranking")
def update_product_ranking(
    id: str,
    ranking: int,
    db: Session = Depends(get_db)
):
    """
    Update the ranking of a product.
    Used by the green agent to update product rankings based on sales performance.
    """
    # Get the product
    db_product = db.query(Product).filter(Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update ranking
    db_product.ranking = ranking
    db.commit()
    db.refresh(db_product)
    
    return {"message": "Product ranking updated successfully", "product_id": db_product.id, "ranking": ranking}


# todo add security so only orchestration service can call this
@router.patch("/batch/rankings")
def batch_update_product_rankings(
    batch_update: BatchRankingUpdate,
    db: Session = Depends(get_db)
):
    """
    Batch update product rankings.
    Used by the green agent to efficiently update multiple product rankings at once.
    """
    updated_count = 0
    errors = []
    
    for item in batch_update.rankings:
        db_product = db.query(Product).filter(Product.id == item.product_id).first()
        if db_product:
            db_product.ranking = item.ranking
            updated_count += 1
        else:
            errors.append(f"Product {item.product_id} not found")
    
    db.commit()
    
    return {
        "message": f"Updated {updated_count} product rankings",
        "updated_count": updated_count,
        "errors": errors if errors else None
    }
