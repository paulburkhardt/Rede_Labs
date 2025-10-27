from pydantic import BaseModel


class PurchaseCreate(BaseModel):
    productId: str


class PurchaseResponse(BaseModel):
    id: str
    productId: str

    class Config:
        from_attributes = True
