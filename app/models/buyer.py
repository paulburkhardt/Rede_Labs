from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
import uuid
import secrets

from app.database import Base


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    battle_id = Column(String, nullable=False, index=True)
    auth_token = Column(String, nullable=False, unique=True)

    # Relationship to purchases
    purchases = relationship("Purchase", backref="buyer")
    
    @staticmethod
    def generate_auth_token(buyer_id: str, battle_id: str) -> str:
        """Generate auth token encoding buyer_id, battle_id, and a secret."""
        secret = secrets.token_urlsafe(32)
        return f"{buyer_id}:{battle_id}:{secret}"
    
    @staticmethod
    def decode_auth_token(token: str) -> tuple[str, str] | None:
        """Decode auth token to extract buyer_id and battle_id.
        Returns (buyer_id, battle_id) or None if invalid format."""
        parts = token.split(":")
        if len(parts) != 3:
            return None
        return (parts[0], parts[1])
