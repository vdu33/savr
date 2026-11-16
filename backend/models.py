"""
SQLAlchemy ORM models — these define the actual database tables.

Kept separate from the Pydantic schemas in schemas.py: ORM models
describe how data is stored, schemas describe how data looks going
in/out of the API. Mixing the two gets messy fast as a project grows.
"""

import uuid

from sqlalchemy import JSON, Boolean, Column, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from database import Base


def gen_id() -> str:
    return str(uuid.uuid4())


class BusinessORM(Base):
    __tablename__ = "businesses"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    cuisine = Column(String, nullable=True)
    website = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    source = Column(String, nullable=False, default="manual")

    deals = relationship("DealORM", back_populates="business")


class DealORM(Base):
    __tablename__ = "deals"

    id = Column(String, primary_key=True, default=gen_id)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=True)
    business_name = Column(String, nullable=False)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    discount_type = Column(String, nullable=False)
    discount_value = Column(String, nullable=True)

    days_valid = Column(JSON, default=list)
    start_time = Column(String, nullable=True)
    end_time = Column(String, nullable=True)

    category = Column(String, nullable=True)

    source_text = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    needs_review = Column(Boolean, default=False)

    business = relationship("BusinessORM", back_populates="deals")
