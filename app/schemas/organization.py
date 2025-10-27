from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    id: str
    name: str
    auth_token: str

    class Config:
        from_attributes = True
