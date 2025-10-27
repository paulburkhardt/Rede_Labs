from pydantic import BaseModel
from typing import Optional


class ImageSchema(BaseModel):
    url: str
    alternativText: Optional[str] = None


class CompanySchema(BaseModel):
    id: str
    name: str = ""


class ProductCreate(BaseModel):
    name: str
    shortDescription: str
    longDescription: str
    price: int
    image: ImageSchema


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    shortDescription: Optional[str] = None
    longDescription: Optional[str] = None
    price: Optional[int] = None
    image: Optional[ImageSchema] = None


class ProductSearchResult(BaseModel):
    id: str
    name: str
    seller_id: str
    priceInCent: int
    currency: str
    bestseller: bool
    shortDescription: str
    image: ImageSchema

    class Config:
        from_attributes = True


class ProductDetail(BaseModel):
    id: str
    name: str
    seller_id: str
    priceInCent: int
    currency: str
    bestseller: bool
    shortDescription: str
    longDescription: str
    image: ImageSchema

    class Config:
        from_attributes = True
