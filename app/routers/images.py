"""
Image endpoints for querying available images
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from collections import defaultdict

from app.database import get_db
from app.models import Image
from app.schemas.product import ImageDescriptionSchema

router = APIRouter()


@router.get("/images", response_model=Dict[str, List[ImageDescriptionSchema]])
def get_available_images(db: Session = Depends(get_db)):
    """
    Get all available images grouped by product_number.
    Returns image descriptions (not base64) organized by category.
    
    Response format:
    {
        "01": [
            {"id": "img-1", "image_description": "Front view", "product_number": "01"},
            {"id": "img-2", "image_description": "Side view", "product_number": "01"}
        ],
        "02": [
            {"id": "img-3", "image_description": "Top view", "product_number": "02"}
        ]
    }
    """
    # Query all images
    images = db.query(Image).all()
    
    # Group by product_number
    grouped_images = defaultdict(list)
    for image in images:
        product_num = image.product_number or "uncategorized"
        grouped_images[product_num].append(
            ImageDescriptionSchema(
                id=image.id,
                image_description=image.image_description,
                product_number=image.product_number
            )
        )
    
    return dict(grouped_images)


@router.get("/images/product-number/{product_number}", response_model=List[ImageDescriptionSchema])
def get_images_by_product_number(
    product_number: str,
    db: Session = Depends(get_db)
):
    """
    Get all images for a specific product_number.
    Returns image descriptions (not base64).
    
    Args:
        product_number: The product number category (e.g., "01", "02")
    
    Returns:
        List of image descriptions for that product number
    """
    images = db.query(Image).filter(Image.product_number == product_number).all()
    
    if not images:
        raise HTTPException(
            status_code=404,
            detail=f"No images found for product_number: {product_number}"
        )
    
    return [
        ImageDescriptionSchema(
            id=image.id,
            image_description=image.image_description,
            product_number=image.product_number
        )
        for image in images
    ]


@router.get("/images/product-numbers", response_model=List[str])
def get_available_product_numbers(db: Session = Depends(get_db)):
    """
    Get list of all available product_numbers (categories).
    
    Returns:
        List of product numbers that have images
    """
    product_numbers = db.query(Image.product_number)\
        .filter(Image.product_number.isnot(None))\
        .distinct()\
        .all()
    
    return [pn[0] for pn in product_numbers]
