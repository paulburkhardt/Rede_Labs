from pydantic import BaseModel
from typing import List
from datetime import datetime


class SellerResponse(BaseModel):
    id: str
    auth_token: str

    class Config:
        from_attributes = True


class PurchaseInfo(BaseModel):
    id: str
    product_id: str
    product_name: str
    buyer_id: str
    buyer_name: str
    price_in_cent: int
    currency: str
    purchased_at: datetime

    class Config:
        from_attributes = True


class SalesStatsResponse(BaseModel):
    seller_id: str
    total_sales: int
    total_revenue_in_cent: int
    purchases: List[PurchaseInfo]
