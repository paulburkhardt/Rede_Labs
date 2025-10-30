from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ImageDescriptionSchema, ProductSearchResult

router = APIRouter(prefix="", tags=["search"])


@router.get("/search", response_model=List[ProductSearchResult])
def search_products(
    q: str = Query("", description="Product name to search for (empty returns all products)"),
    seller_id: str = Query(None, description="Filter by seller ID"),
    db: Session = Depends(get_db)
):
    """
    Search for products by name.
    Shared search endpoint returning ranked product lists.
    Products are ranked by bestseller status first, then by name match.
    If q is empty, returns all products.
    """
    # Start with base query
    query = db.query(Product)
    
    # Apply seller filter if provided
    if seller_id:
        query = query.filter(Product.seller_id == seller_id)
    
    # Apply search filter if q is not empty
    if q:
        query = query.filter(
            (Product.name.ilike(f"%{q}%")) |
            (Product.short_description.ilike(f"%{q}%")) |
            (Product.long_description.ilike(f"%{q}%"))
        )
    
    # Order by ranking (lowest number = best rank = rank 1 comes first)
    # Then by bestseller status, then by name
    if q:
        products = query.order_by(
            Product.ranking.asc().nullslast(), 
            Product.bestseller.desc(),
            Product.name
        ).all()
    else:
        # When no search query, just order by ranking
        products = query.order_by(
            Product.ranking.asc().nullslast(),
            Product.bestseller.desc(),
            Product.name
        ).all()
    
    # Format results with image descriptions (no base64)
    results = []
    for product in products:
        images_data = [
            ImageDescriptionSchema(
                id=img.id,
                image_description=img.image_description,
                product_number=img.product_number
            )
            for img in product.images
        ]
        results.append(ProductSearchResult(
            id=product.id,
            name=product.name,
            seller_id=product.seller_id,
            price_in_cent=product.price_in_cent,
            currency=product.currency,
            bestseller=product.bestseller,
            short_description=product.short_description,
            images=images_data,
            ranking=product.ranking
        ))
    
    return results
