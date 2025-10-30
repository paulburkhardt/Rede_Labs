from sqlalchemy import Column, String, ForeignKey, Table
from app.database import Base


# Association table for many-to-many relationship between products and images
product_images = Table(
    'product_images',
    Base.metadata,
    Column('product_id', String, ForeignKey('products.id'), primary_key=True),
    Column('image_id', String, ForeignKey('images.id'), primary_key=True)
)
