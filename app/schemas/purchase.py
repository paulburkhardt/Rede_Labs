from pydantic import BaseModel


class PurchaseCreate(BaseModel):
    purchased_at: int


class PurchaseResponse(BaseModel):
    id: str
    product_id: str
    price_of_purchase: int
    wholesale_cost_at_purchase: int

    class Config:
        from_attributes = True
