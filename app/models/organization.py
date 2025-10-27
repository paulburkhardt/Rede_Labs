from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
import uuid
import secrets

from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    auth_token = Column(String, nullable=False, unique=True, default=lambda: secrets.token_urlsafe(32))

    # Relationship to products
    products = relationship("Product", back_populates="organization")
