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
    image_url = Column(String, nullable=True)
    image_alternative_text = Column(String, nullable=True)
    
    # Foreign key to organization
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Relationship
    organization = relationship("Organization", back_populates="products")
