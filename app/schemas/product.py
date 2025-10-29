from pydantic import BaseModel
from typing import Optional, List, Dict


class ImageSchema(BaseModel):
    base64: str
    image_description: Optional[str] = None


class CompanySchema(BaseModel):
    id: str
    name: str = ""


class ProductCreate(BaseModel):
    name: str
    short_description: str
    long_description: str
    price: int
    image: ImageSchema


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    price: Optional[int] = None
    image: Optional[ImageSchema] = None
    ranking: Optional[int] = None


class ProductSearchResult(BaseModel):
    id: str
    name: str
    seller_id: str
    price_in_cent: int
    currency: str
    bestseller: bool
    short_description: str
    image: ImageSchema
    ranking: Optional[int] = None

    class Config:
        from_attributes = True


class ProductDetail(BaseModel):
    id: str
    name: str
    seller_id: str
    price_in_cent: int
    currency: str
    bestseller: bool
    short_description: str
    long_description: str
    image: ImageSchema

    class Config:
        from_attributes = True


class ProductRankingUpdate(BaseModel):
    product_id: str
    ranking: int


class BatchRankingUpdate(BaseModel):
    rankings: List[ProductRankingUpdate]
