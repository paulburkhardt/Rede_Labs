from pydantic import BaseModel

class BuyerResponse(BaseModel):
    id: str
    auth_token: str

    class Config:
        from_attributes = True
