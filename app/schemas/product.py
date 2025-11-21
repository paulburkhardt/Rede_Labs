from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict
from app.models.towel_specs import TowelVariant


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
    image_ids: List[str]  # List of image IDs from the database (REQUIRED - at least one image)
    towel_variant: Optional[TowelVariant] = None  # Towel variant (budget, mid_tier, premium) - Optional for backward compatibility
    
    @field_validator('towel_variant', mode='before')
    @classmethod
    def normalize_towel_variant(cls, v):
        """Normalize towel_variant to handle uppercase enum names"""
        if v is None:
            return v
        if isinstance(v, str):
            # Convert uppercase enum names to lowercase values
            v_upper = v.upper()
            if v_upper == 'BUDGET':
                return 'budget'
            elif v_upper == 'MID_TIER':
                return 'mid_tier'
            elif v_upper == 'PREMIUM':
                return 'premium'
            # If already lowercase, return as-is
            return v.lower()
        return v
    
    @field_validator('image_ids')
    @classmethod
    def validate_image_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one image_id is required. Products must have images.')
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0. Negative or zero prices are not allowed.')
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    price: Optional[int] = None
    image_ids: Optional[List[str]] = None  # List of image IDs from the database
    ranking: Optional[int] = None
    towel_variant: Optional[TowelVariant] = None  # Towel variant (budget, mid_tier, premium)
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0. Negative or zero prices are not allowed.')
        return v


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
    towel_variant: Optional[TowelVariant] = None
    gsm: Optional[int] = None
    width_inches: Optional[int] = None
    length_inches: Optional[int] = None
    material: Optional[str] = None

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
    towel_variant: Optional[TowelVariant] = None
    gsm: Optional[int] = None
    width_inches: Optional[int] = None
    length_inches: Optional[int] = None
    material: Optional[str] = None

    class Config:
        from_attributes = True


class ProductRankingUpdate(BaseModel):
    product_id: str
    ranking: int


class BatchRankingUpdate(BaseModel):
    rankings: List[ProductRankingUpdate]
