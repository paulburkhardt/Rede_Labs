from pydantic import BaseModel


class PurchaseCreate(BaseModel):
    purchased_at: int


class PurchaseResponse(BaseModel):
    id: str
    product_id: str

    class Config:
        from_attributes = True
