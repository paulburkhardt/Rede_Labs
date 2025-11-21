from sqlalchemy import Column, String, PrimaryKeyConstraint

from app.database import Base


class Metadata(Base):
    __tablename__ = "metadata"

    key = Column(String, nullable=False)
    battle_id = Column(String, nullable=False, index=True)
    value = Column(String, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('key', 'battle_id'),
    )

