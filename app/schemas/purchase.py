from pydantic import BaseModel


class PurchaseResponse(BaseModel):
    id: str
    product_id: str

    class Config:
        from_attributes = True
