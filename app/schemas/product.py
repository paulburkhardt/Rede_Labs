from pydantic import BaseModel
from typing import Optional, List, Dict


class ImageDescriptionSchema(BaseModel):
    """Schema for returning image descriptions (without base64)"""
    id: str
    image_description: Optional[str] = None
    product_number: Optional[str] = None


class ImageSchema(BaseModel):
    """Legacy schema with base64 - only used internally"""
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
    image_ids: List[str]  # List of image IDs from the database


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    price: Optional[int] = None
    image_ids: Optional[List[str]] = None  # List of image IDs from the database
    ranking: Optional[int] = None


class ProductSearchResult(BaseModel):
    id: str
    name: str
    seller_id: str
    price_in_cent: int
    currency: str
    bestseller: bool
    short_description: str
    images: List[ImageDescriptionSchema]  # List of image descriptions
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
    images: List[ImageDescriptionSchema]  # List of image descriptions

    class Config:
        from_attributes = True


class ProductRankingUpdate(BaseModel):
    product_id: str
    ranking: int


class BatchRankingUpdate(BaseModel):
    rankings: List[ProductRankingUpdate]
