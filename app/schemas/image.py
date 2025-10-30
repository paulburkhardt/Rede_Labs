from pydantic import BaseModel
from typing import Optional


class ImageCreate(BaseModel):
    base64: str
    image_description: Optional[str] = None
    product_number: Optional[str] = None


class ImageResponse(BaseModel):
    id: str
    base64: str
    image_description: Optional[str] = None
    product_number: Optional[str] = None

    class Config:
        from_attributes = True
