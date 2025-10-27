from pydantic import BaseModel


class BuyerCreate(BaseModel):
    name: str


class BuyerResponse(BaseModel):
    id: str
    name: str
    auth_token: str

    class Config:
        from_attributes = True
