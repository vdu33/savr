"""
Pydantic schemas — define what the API accepts and returns.
Separate from the ORM models in models.py on purpose (see that file's
docstring).
"""

from typing import List, Optional

from pydantic import BaseModel


class BusinessOut(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    cuisine: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class BusinessCreate(BaseModel):
    name: str
    address: Optional[str] = None
    cuisine: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    source: str = "manual"


class DealOut(BaseModel):
    id: str
    business_id: Optional[str] = None
    business_name: str
    title: str
    description: Optional[str] = None
    discount_type: str
    discount_value: Optional[str] = None
    days_valid: List[str] = []
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    category: Optional[str] = None
    confidence: Optional[float] = None
    needs_review: bool = False

    class Config:
        from_attributes = True
