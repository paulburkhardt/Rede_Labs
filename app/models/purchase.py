from sqlalchemy import Column, String, Integer, ForeignKey
import uuid

from app.database import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    buyer_id = Column(String, ForeignKey("buyers.id"), nullable=False)
    purchased_at = Column(Integer, nullable=False)
    price_of_purchase = Column(Integer, nullable=False)
