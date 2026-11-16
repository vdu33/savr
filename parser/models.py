"""
Core data models for the Local Bites deal-tracking app.

These schemas are the contract between every part of the system:
the AI parser produces Deal objects, the backend API stores and
serves them, and the mobile app renders them. Keeping this in one
place means all three stay in sync as the project grows.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class DiscountType(str, Enum):
    PERCENT_OFF = "percent_off"
    DOLLAR_OFF = "dollar_off"
    BOGO = "bogo"
    FIXED_PRICE = "fixed_price"
    FREE_ITEM = "free_item"
    HAPPY_HOUR = "happy_hour"
    OTHER = "other"


class DayOfWeek(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class Business(BaseModel):
    id: Optional[str] = None
    name: str
    address: Optional[str] = None
    cuisine: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    source: str = Field(
        description="Where this record came from, e.g. 'manual', "
        "'google_places', 'scrape:website'"
    )


class Deal(BaseModel):
    id: Optional[str] = None
    business_id: Optional[str] = None
    business_name: str

    title: str = Field(
        description="Short human-readable summary, e.g. "
        "'Taco Tuesday — $2 off all tacos'"
    )
    description: Optional[str] = None

    discount_type: DiscountType
    discount_value: Optional[str] = Field(
        default=None, description="e.g. '20%', '$5 off', 'buy one get one free'"
    )

    days_valid: List[DayOfWeek] = Field(default_factory=list)
    start_time: Optional[str] = Field(
        default=None, description="24h HH:MM, e.g. '16:00'"
    )
    end_time: Optional[str] = Field(default=None, description="24h HH:MM")

    category: Optional[str] = Field(
        default=None, description="e.g. 'drinks', 'entrees', 'dessert', 'brunch'"
    )

    # Provenance + quality — this is what makes the pipeline trustworthy
    # rather than a black box.
    source_text: str = Field(
        description="The raw original text this deal was extracted from, "
        "kept for auditing and debugging bad parses"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Model's self-rated confidence in this parse"
    )
    needs_review: bool = Field(
        default=False,
        description="True when confidence is low or the source text was "
        "ambiguous — surfaced to a human before the deal goes live",
    )
