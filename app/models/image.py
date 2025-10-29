from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
import uuid

from app.database import Base
from app.models.product_image import product_images


class Image(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    base64 = Column(Text, nullable=False)  # Store base64 encoded image data
    image_description = Column(String, nullable=True)
    product_number = Column(String, nullable=True)  # Product number from folder name (e.g., "01", "02")

    # Relationship - one image can be used by multiple products (many-to-many)
    products = relationship("Product", secondary=product_images, back_populates="images")
