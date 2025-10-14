# -*- coding: utf-8 -*-
"""
MarketArena Marketplace API

FastAPI backend for e-commerce marketplace simulation.
Run with: uvicorn main:app --host 0.0.0.0 --port 8100 --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
import uuid
from datetime import datetime

app = FastAPI(
    title="MarketArena Marketplace API",
    description="E-commerce marketplace for AI agent competition",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================

class PhaseEnum(str, Enum):
    EDIT = "edit"
    BUY = "buy"
    IDLE = "idle"


class OrganizationCreate(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    id: str
    name: str


class ImageData(BaseModel):
    url: str
    alternativeText: Optional[str] = None


class ProductCreate(BaseModel):
    name: str
    shortDescription: str
    longDescription: str
    price: int  # Price in cents
    image: ImageData


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    shortDescription: Optional[str] = None
    longDescription: Optional[str] = None
    price: Optional[int] = None
    image: Optional[ImageData] = None


class CompanyInfo(BaseModel):
    name: str
    id: str


class ProductSearchResult(BaseModel):
    id: str
    name: str
    company: CompanyInfo
    priceInCent: int
    currency: str = "USD"
    bestseller: bool
    shortDescription: str
    image: ImageData


class ProductDetail(ProductSearchResult):
    longDescription: str


# ============================================================================
# In-Memory Database
# ============================================================================

class InMemoryDB:
    def __init__(self):
        self.organizations: Dict[str, dict] = {}
        self.products: Dict[str, dict] = {}
        self.purchases: List[dict] = []
        self.current_phase = PhaseEnum.IDLE
        self.current_day = 0
    
    def reset(self):
        """Reset all data"""
        self.organizations.clear()
        self.products.clear()
        self.purchases.clear()
        self.current_phase = PhaseEnum.IDLE
        self.current_day = 0
    
    def calculate_bestsellers(self) -> set:
        """Mark top 20% of products by sales as bestsellers"""
        sales_count = {}
        for purchase in self.purchases:
            pid = purchase['product_id']
            sales_count[pid] = sales_count.get(pid, 0) + 1
        
        if not sales_count:
            return set()
        
        sorted_products = sorted(sales_count.items(), key=lambda x: x[1], reverse=True)
        bestseller_count = max(1, len(sorted_products) // 5)
        return {pid for pid, _ in sorted_products[:bestseller_count]}
    
    def calculate_product_rank_score(self, product_id: str) -> float:
        """Calculate ranking score (higher = better rank)"""
        product = self.products.get(product_id)
        if not product:
            return 0.0
        
        score = 0.0
        
        # Sales count (40%)
        sales = sum(1 for p in self.purchases if p['product_id'] == product_id)
        score += min(sales / 10, 1.0) * 0.4
        
        # Price competitiveness (30%)
        avg_price_cents = 5000
        price_score = max(0, 1.0 - abs(product['price'] - avg_price_cents) / avg_price_cents)
        score += price_score * 0.3
        
        # Description quality (20%)
        desc_length = len(product.get('short_description', ''))
        desc_score = min(desc_length / 200, 1.0)
        score += desc_score * 0.2
        
        # Recency (10%)
        score += 0.1
        
        return score


db = InMemoryDB()


# ============================================================================
# Helper Functions
# ============================================================================

def check_edit_phase():
    if db.current_phase != PhaseEnum.EDIT:
        raise HTTPException(
            status_code=403,
            detail=f"Cannot edit products. Current phase: {db.current_phase}"
        )


def check_buy_phase():
    if db.current_phase != PhaseEnum.BUY:
        raise HTTPException(
            status_code=403,
            detail=f"Cannot make purchases. Current phase: {db.current_phase}"
        )


# ============================================================================
# Public Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "MarketArena Marketplace API",
        "version": "1.0.0",
        "status": "running",
        "current_phase": db.current_phase,
        "current_day": db.current_day
    }


@app.post("/createOrganization", response_model=OrganizationResponse)
async def create_organization(org_data: OrganizationCreate):
    """Create seller organization"""
    org_id = f"org-{uuid.uuid4().hex[:8]}"
    
    db.organizations[org_id] = {
        "id": org_id,
        "name": org_data.name
    }
    
    return OrganizationResponse(id=org_id, name=org_data.name)


@app.post("/product")
async def create_product(product_data: ProductCreate):
    """Create product listing"""
    product_id = f"product-{uuid.uuid4().hex[:8]}"
    
    # TODO: Get org_id from authentication
    if not db.organizations:
        org_id = "org-default"
        db.organizations[org_id] = {"id": org_id, "name": "Default Seller"}
    else:
        org_id = list(db.organizations.keys())[0]
    
    db.products[product_id] = {
        "id": product_id,
        "name": product_data.name,
        "org_id": org_id,
        "price": product_data.price,
        "short_description": product_data.shortDescription,
        "long_description": product_data.longDescription,
        "image": product_data.image.dict(),
        "created_at": datetime.now()
    }
    
    return {"id": product_id, "message": "Product created successfully"}


@app.patch("/product/{product_id}")
async def update_product(product_id: str, updates: ProductUpdate):
    """Update product listing (only during edit phase)"""
    check_edit_phase()
    
    if product_id not in db.products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = db.products[product_id]
    
    if updates.name is not None:
        product['name'] = updates.name
    if updates.shortDescription is not None:
        product['short_description'] = updates.shortDescription
    if updates.longDescription is not None:
        product['long_description'] = updates.longDescription
    if updates.price is not None:
        product['price'] = updates.price
    if updates.image is not None:
        product['image'] = updates.image.dict()
    
    return {"id": product_id, "message": "Product updated successfully"}


@app.get("/search", response_model=List[ProductSearchResult])
async def search_products(q: str):
    """Search products, returns ranked list"""
    bestsellers = db.calculate_bestsellers()
    
    # Filter by query
    matching_products = [
        p for p in db.products.values()
        if q.lower() in p['name'].lower()
    ]
    
    # Calculate scores and sort
    scored_products = [
        (p, db.calculate_product_rank_score(p['id']))
        for p in matching_products
    ]
    scored_products.sort(key=lambda x: x[1], reverse=True)
    
    # Convert to response format
    results = []
    for product, score in scored_products:
        org = db.organizations.get(product['org_id'], {"id": "unknown", "name": "Unknown"})
        
        results.append(ProductSearchResult(
            id=product['id'],
            name=product['name'],
            company=CompanyInfo(name=org['name'], id=org['id']),
            priceInCent=product['price'],
            currency="USD",
            bestseller=product['id'] in bestsellers,
            shortDescription=product['short_description'],
            image=ImageData(**product['image'])
        ))
    
    return results


@app.get("/product/{product_id}", response_model=ProductDetail)
async def get_product_detail(product_id: str):
    """Get detailed product information"""
    if product_id not in db.products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = db.products[product_id]
    org = db.organizations.get(product['org_id'], {"id": "unknown", "name": "Unknown"})
    bestsellers = db.calculate_bestsellers()
    
    return ProductDetail(
        id=product['id'],
        name=product['name'],
        company=CompanyInfo(name=org['name'], id=org['id']),
        priceInCent=product['price'],
        currency="USD",
        bestseller=product['id'] in bestsellers,
        shortDescription=product['short_description'],
        longDescription=product['long_description'],
        image=ImageData(**product['image'])
    )


@app.post("/buy/{product_id}")
async def purchase_product(product_id: str):
    """Purchase product (only during buy phase)"""
    check_buy_phase()
    
    if product_id not in db.products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = db.products[product_id]
    
    purchase_record = {
        "product_id": product_id,
        "org_id": product['org_id'],
        "price": product['price'],
        "timestamp": datetime.now()
    }
    db.purchases.append(purchase_record)
    
    return {
        "success": True,
        "product_id": product_id,
        "price": product['price'],
        "message": "Purchase completed"
    }


# ============================================================================
# Admin Endpoints (Green Agent Control)
# ============================================================================

@app.post("/admin/reset")
async def admin_reset():
    """Reset marketplace"""
    db.reset()
    return {
        "success": True,
        "message": "Marketplace reset",
        "phase": db.current_phase,
        "day": db.current_day
    }


@app.post("/admin/start_edit_phase")
async def admin_start_edit_phase():
    """Start edit phase"""
    db.current_phase = PhaseEnum.EDIT
    db.current_day += 1
    return {
        "success": True,
        "phase": db.current_phase,
        "day": db.current_day,
        "message": f"Edit phase started for day {db.current_day}"
    }


@app.post("/admin/start_buy_phase")
async def admin_start_buy_phase():
    """Start buy phase"""
    db.current_phase = PhaseEnum.BUY
    return {
        "success": True,
        "phase": db.current_phase,
        "day": db.current_day,
        "message": f"Buy phase started for day {db.current_day}"
    }


@app.get("/admin/stats")
async def admin_get_stats():
    """Get revenue statistics"""
    org_stats = {}
    
    for purchase in db.purchases:
        org_id = purchase['org_id']
        if org_id not in org_stats:
            org = db.organizations.get(org_id, {"name": "Unknown"})
            org_stats[org_id] = {
                "org_id": org_id,
                "name": org['name'],
                "total_revenue": 0,
                "units_sold": 0
            }
        
        org_stats[org_id]['total_revenue'] += purchase['price']
        org_stats[org_id]['units_sold'] += 1
    
    # Calculate averages
    for stats in org_stats.values():
        if stats['units_sold'] > 0:
            stats['avg_price'] = stats['total_revenue'] // stats['units_sold']
        else:
            stats['avg_price'] = 0
    
    sellers = sorted(org_stats.values(), key=lambda x: x['total_revenue'], reverse=True)
    
    total_revenue = sum(s['total_revenue'] for s in sellers)
    total_units = sum(s['units_sold'] for s in sellers)
    
    return {
        "sellers": sellers,
        "marketplace_totals": {
            "total_revenue": total_revenue,
            "total_units_sold": total_units,
            "num_sellers": len(sellers)
        },
        "current_day": db.current_day,
        "current_phase": db.current_phase
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting MarketArena Marketplace API...")
    print("API at: http://localhost:8100")
    print("Docs at: http://localhost:8100/docs")
    uvicorn.run(app, host="0.0.0.0", port=8100)
