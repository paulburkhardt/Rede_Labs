from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductSearchResult,
    ProductDetail
)
from app.models.product import Product
from app.models.organization import Organization

router = APIRouter(prefix="/product", tags=["products"])


@router.post("/{id}")
def create_product(
    id: str,
    product: ProductCreate,
    authorization: str = Header(..., description="Bearer token for organization"),
    db: Session = Depends(get_db)
):
    """
    Create a new product.
    White agents use this endpoint to create their product listings.
    Requires Authorization header with organization token.
    """
    # Extract token from Authorization header
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # Verify organization exists and token is valid
    organization = db.query(Organization).filter(Organization.auth_token == token).first()
    if not organization:
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
        organization_id=organization.id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return {"message": "Product created successfully", "product_id": db_product.id}


@router.patch("/{id}")
def update_product(
    id: str,
    product: ProductUpdate,
    authorization: str = Header(..., description="Bearer token for organization"),
    db: Session = Depends(get_db)
):
    """
    Update an existing product.
    White agents use this endpoint to update their own product listings.
    Requires Authorization header with organization token.
    """
    # Extract token from Authorization header
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # Verify organization exists and token is valid
    organization = db.query(Organization).filter(Organization.auth_token == token).first()
    if not organization:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    # Get the product
    db_product = db.query(Product).filter(Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verify the product belongs to this organization
    if db_product.organization_id != organization.id:
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
    # Get the product with organization info
    db_product = db.query(Product).filter(Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Format response
    return ProductDetail(
        id=db_product.id,
        name=db_product.name,
        company={
            "id": db_product.organization.id,
            "name": db_product.organization.name
        },
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
