from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.product import ProductSearchResult
from app.models.product import Product

router = APIRouter(prefix="", tags=["search"])


@router.get("/search", response_model=List[ProductSearchResult])
def search_products(
    q: str = Query(..., description="Product name to search for"),
    db: Session = Depends(get_db)
):
    """
    Search for products by name.
    Shared search endpoint returning ranked product lists.
    Products are ranked by bestseller status first, then by name match.
    """
    # Search for products by name (case-insensitive partial match)
    products = db.query(Product).filter(
        Product.name.ilike(f"%{q}%")
    ).order_by(
        Product.bestseller.desc(),  # Bestsellers first
        Product.name  # Then alphabetically
    ).all()
    
    # Format results
    results = []
    for product in products:
        results.append(ProductSearchResult(
            id=product.id,
            name=product.name,
            company={
                "id": product.organization.id,
                "name": product.organization.name
            },
            priceInCent=product.price_in_cent,
            currency=product.currency,
            bestseller=product.bestseller,
            shortDescription=product.short_description,
            image={
                "url": product.image_url or "",
                "alternativText": product.image_alternative_text
            }
        ))
    
    return results
