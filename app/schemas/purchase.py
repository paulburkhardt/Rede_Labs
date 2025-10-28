from pydantic import BaseModel


class PurchaseCreate(BaseModel):
    product_id: str


class PurchaseResponse(BaseModel):
    id: str
    product_id: str

    class Config:
        from_attributes = True
