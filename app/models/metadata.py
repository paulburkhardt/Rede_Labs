from sqlalchemy import Column, String

from app.database import Base


class Metadata(Base):
    __tablename__ = "metadata"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)

