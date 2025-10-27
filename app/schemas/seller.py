from pydantic import BaseModel


class SellerResponse(BaseModel):
    id: str
    auth_token: str

    class Config:
        from_attributes = True
