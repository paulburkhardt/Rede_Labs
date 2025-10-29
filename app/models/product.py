from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    short_description = Column(String, nullable=False)
    long_description = Column(String, nullable=False)
    price_in_cent = Column(Integer, nullable=False)
    currency = Column(String, default="USD")
    bestseller = Column(Boolean, default=False)
    ranking = Column(Integer, nullable=True)

    # Foreign keys
    seller_id = Column(String, ForeignKey("sellers.id"), nullable=False)
    image_id = Column(String, ForeignKey("images.id"), nullable=True)

    # Relationships
    seller = relationship("Seller", back_populates="products")
    image = relationship("Image", back_populates="products")
