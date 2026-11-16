"""
Local Bites API.

Run with:
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs in a browser for interactive,
auto-generated API docs where you can try every endpoint by hand.
"""

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Local Bites API",
    description="Backend serving weekly local food business deals",
)

# Allows the mobile app (and anything else) to call this API during
# development. Fine for local dev; you'd lock this down before a real
# public launch.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Local Bites API is running"}


@app.get("/deals", response_model=List[schemas.DealOut])
def list_deals(
    category: Optional[str] = None,
    day: Optional[str] = Query(None, description="e.g. 'monday'"),
    discount_type: Optional[str] = None,
    min_confidence: float = 0.0,
    db: Session = Depends(get_db),
):
    """
    List deals, optionally filtered by category, day of week, discount
    type, and a minimum confidence score (useful for hiding low-quality
    parses from end users while still keeping them in the database for
    review).
    """
    query = db.query(models.DealORM).filter(
        models.DealORM.confidence >= min_confidence
    )
    if category:
        query = query.filter(models.DealORM.category == category)
    if discount_type:
        query = query.filter(models.DealORM.discount_type == discount_type)

    deals = query.all()

    if day:
        day = day.lower()
        deals = [d for d in deals if not d.days_valid or day in d.days_valid]

    return deals


@app.get("/deals/{deal_id}", response_model=schemas.DealOut)
def get_deal(deal_id: str, db: Session = Depends(get_db)):
    deal = db.query(models.DealORM).filter(models.DealORM.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@app.get("/businesses", response_model=List[schemas.BusinessOut])
def list_businesses(db: Session = Depends(get_db)):
    return db.query(models.BusinessORM).all()


@app.post("/businesses", response_model=schemas.BusinessOut)
def create_business(business: schemas.BusinessCreate, db: Session = Depends(get_db)):
    """
    This is the seed of the future business self-signup flow — right
    now it just creates a record, but this is where a real signup form
    would eventually post its data.
    """
    b = models.BusinessORM(**business.model_dump())
    db.add(b)
    db.commit()
    db.refresh(b)
    return b
