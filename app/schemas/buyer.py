from pydantic import BaseModel, Field


class BuyerCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class BuyerResponse(BaseModel):
    id: str
    name: str
    auth_token: str

    class Config:
        from_attributes = True
