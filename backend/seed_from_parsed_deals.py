"""
One-time import script: loads parsed_deals.json (the output from the
deal-parser project's test_parser.py) into this backend's database.

Usage:
    Copy parsed_deals.json from the deal-parser folder into this folder,
    then run:
        python3 seed_from_parsed_deals.py
"""

import json
import os

import models
from database import Base, SessionLocal, engine

PARSED_DEALS_PATH = os.environ.get("PARSED_DEALS_PATH", "parsed_deals.json")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if not os.path.exists(PARSED_DEALS_PATH):
        print(
            f"Couldn't find {PARSED_DEALS_PATH}. Copy it here from the "
            "deal-parser folder first, e.g.:\n"
            f"  cp ../deal-parser/parsed_deals.json ."
        )
        return

    with open(PARSED_DEALS_PATH) as f:
        deals = json.load(f)

    business_cache = {}

    for d in deals:
        name = d["business_name"]
        if name not in business_cache:
            existing = (
                db.query(models.BusinessORM)
                .filter(models.BusinessORM.name == name)
                .first()
            )
            if existing:
                business_cache[name] = existing
            else:
                b = models.BusinessORM(name=name, source="scrape:sample")
                db.add(b)
                db.flush()  # assigns b.id without committing yet
                business_cache[name] = b

        business = business_cache[name]

        deal_row = models.DealORM(
            business_id=business.id,
            business_name=name,
            title=d["title"],
            description=d.get("description"),
            discount_type=d["discount_type"],
            discount_value=d.get("discount_value"),
            days_valid=d.get("days_valid", []),
            start_time=d.get("start_time"),
            end_time=d.get("end_time"),
            category=d.get("category"),
            source_text=d.get("source_text"),
            confidence=d.get("confidence"),
            needs_review=d.get("needs_review", False),
        )
        db.add(deal_row)

    db.commit()
    print(f"Loaded {len(deals)} deals across {len(business_cache)} businesses.")


if __name__ == "__main__":
    main()
