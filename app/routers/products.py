from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductSearchResult,
    ProductDetail,
    BatchRankingUpdate,
    ImageDescriptionSchema
)
from app.models.product import Product
from app.models.seller import Seller
from app.models.image import Image
from app.services.phase_manager import ensure_phase, Phase

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

    ensure_phase(db, [Phase.SELLER_MANAGEMENT])
    
    # Check if product with this ID already exists
    existing_product = db.query(Product).filter(Product.id == id).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this ID already exists")
    
    # Validate image IDs
    if not product.image_ids or len(product.image_ids) == 0:
        raise HTTPException(status_code=400, detail="At least one image_id is required")
    
    # Fetch all images (deduplicate IDs first)
    unique_image_ids = list(set(product.image_ids))
    images = db.query(Image).filter(Image.id.in_(unique_image_ids)).all()
    
    if len(images) != len(unique_image_ids):
        found_ids = {img.id for img in images}
        missing_ids = set(unique_image_ids) - found_ids
        raise HTTPException(
            status_code=404,
            detail=f"Images not found: {', '.join(missing_ids)}"
        )
    
    # Validate all images are from the same product_number
    product_numbers = {img.product_number for img in images if img.product_number}
    if len(product_numbers) > 1:
        raise HTTPException(
            status_code=400,
            detail=f"All images must be from the same product_number. Found: {', '.join(product_numbers)}"
        )
    if len(product_numbers) == 0:
        raise HTTPException(
            status_code=400,
            detail="Images must have a product_number assigned"
        )
    
    # Create new product
    db_product = Product(
        id=id,
        name=product.name,
        short_description=product.short_description,
        long_description=product.long_description,
        price_in_cent=product.price,
        seller_id=seller.id
    )
    
    # Associate images with product
    db_product.images = images
    
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

    ensure_phase(db, [Phase.SELLER_MANAGEMENT])
    
    # Update fields if provided
    if product.name is not None:
        db_product.name = product.name
    if product.short_description is not None:
        db_product.short_description = product.short_description
    if product.long_description is not None:
        db_product.long_description = product.long_description
    if product.price is not None:
        db_product.price_in_cent = product.price
    if product.image_ids is not None:
        # Validate image IDs
        if len(product.image_ids) == 0:
            raise HTTPException(status_code=400, detail="At least one image_id is required")
        
        # Fetch all images (deduplicate IDs first)
        unique_image_ids = list(set(product.image_ids))
        images = db.query(Image).filter(Image.id.in_(unique_image_ids)).all()
        
        if len(images) != len(unique_image_ids):
            found_ids = {img.id for img in images}
            missing_ids = set(unique_image_ids) - found_ids
            raise HTTPException(
                status_code=404,
                detail=f"Images not found: {', '.join(missing_ids)}"
            )
        
        # Validate all images are from the same product_number
        product_numbers = {img.product_number for img in images if img.product_number}
        if len(product_numbers) > 1:
            raise HTTPException(
                status_code=400,
                detail=f"All images must be from the same product_number. Found: {', '.join(product_numbers)}"
            )
        if len(product_numbers) == 0:
            raise HTTPException(
                status_code=400,
                detail="Images must have a product_number assigned"
            )
        
        # Update product images
        db_product.images = images
    
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
    
    # Format response with image descriptions (no base64)
    images_data = [
        ImageDescriptionSchema(
            id=img.id,
            image_description=img.image_description,
            product_number=img.product_number
        )
        for img in db_product.images
    ]
    
    return ProductDetail(
        id=db_product.id,
        name=db_product.name,
        seller_id=db_product.seller_id,
        price_in_cent=db_product.price_in_cent,
        currency=db_product.currency,
        bestseller=db_product.bestseller,
        short_description=db_product.short_description,
        long_description=db_product.long_description,
        images=images_data
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
