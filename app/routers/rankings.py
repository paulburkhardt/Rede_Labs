import random
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product import Product
from app.models.purchase import Purchase
from app.services.round_manager import get_current_round

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.post("/initialize")
def initialize_rankings(
    battle_id: str,
    db: Session = Depends(get_db)
):
    """
    Initialize product rankings with random values for a specific battle.
    Used at the start of a battle before any purchases are made.
    """
    # Get all products in this battle
    products = db.query(Product).filter(Product.battle_id == battle_id).all()
    
    if not products:
        return {"message": "No products to rank", "updated_count": 0}
    
    # Generate random rankings
    random_rankings = list(range(1, len(products) + 1))
    random.shuffle(random_rankings)
    
    # Assign rankings to products
    for i, product in enumerate(products):
        product.ranking = random_rankings[i]
    
    db.commit()
    
    return {
        "message": f"Initialized {len(products)} product rankings randomly",
        "updated_count": len(products)
    }


@router.post("/update-by-sales")
def update_rankings_by_sales(
    battle_id: str,
    db: Session = Depends(get_db)
):
    """
    Update product rankings based on sales performance for a specific battle.
    Products with more purchases get better rankings (lower numbers).
    Rank 1 = most sales, Rank 2 = second most sales, etc.
    """
    # Get all products in this battle
    products = db.query(Product).filter(Product.battle_id == battle_id).all()
    
    if not products:
        return {"message": "No products to rank", "updated_count": 0}
    
    # Count purchases per product in this battle
    current_round = get_current_round(db, battle_id)

    purchase_counts = (
        db.query(
            Purchase.product_id,
            func.count(Purchase.id).label("purchase_count")
        )
        .filter(
            Purchase.battle_id == battle_id,
            Purchase.round == current_round
        )
        .group_by(Purchase.product_id)
        .all()
    )
    
    # Create a mapping of product_id to purchase count
    product_sales = {result.product_id: result.purchase_count for result in purchase_counts}
    
    # Create list of products with their sales counts
    products_with_sales = [
        {"product": product, "sales_count": product_sales.get(product.id, 0)}
        for product in products
    ]
    
    # Sort by sales count (descending) - most sales first
    sorted_products = sorted(
        products_with_sales, 
        key=lambda x: x["sales_count"], 
        reverse=True
    )
    
    # Assign rankings: rank 1 = most sales
    for rank, item in enumerate(sorted_products, start=1):
        item["product"].ranking = rank
    
    db.commit()
    
    return {
        "message": f"Updated {len(products)} product rankings based on sales",
        "updated_count": len(products),
        "top_products": [
            {
                "product_id": item["product"].id,
                "product_name": item["product"].name,
                "sales_count": item["sales_count"],
                "ranking": rank
            }
            for rank, item in enumerate(sorted_products[:5], start=1)
        ]
    }
