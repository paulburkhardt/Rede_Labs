from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import uuid

from app.database import Base
from app.models.product_image import product_images
from app.models.towel_specs import TowelVariant


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    battle_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    short_description = Column(String, nullable=False)
    long_description = Column(String, nullable=False)
    price_in_cent = Column(Integer, nullable=False)
    currency = Column(String, default="USD")
    bestseller = Column(Boolean, default=False)
    ranking = Column(Integer, nullable=True)
    
    # Towel variant properties
    towel_variant = Column(Enum(TowelVariant, values_callable=lambda x: [e.value for e in x]), nullable=False)
    gsm = Column(Integer, nullable=False)
    width_inches = Column(Integer, nullable=False)
    length_inches = Column(Integer, nullable=False)
    material = Column(String, nullable=False)
    wholesale_cost_cents = Column(Integer, nullable=False)

    # Foreign keys
    seller_id = Column(String, ForeignKey("sellers.id"), nullable=False)

    # Relationships
    seller = relationship("Seller", back_populates="products")
    images = relationship("Image", secondary=product_images, back_populates="products")
