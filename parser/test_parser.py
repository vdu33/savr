"""
Run this to see the AI parsing pipeline in action against realistic
messy sample text.

Usage:
    export ANTHROPIC_API_KEY=your_key_here
    python test_parser.py
"""

import json

from parser import get_client, parse_deals_from_text
from sample_data import SAMPLES


def main():
    client = get_client()
    all_deals = []

    for business_name, raw_text in SAMPLES:
        print(f"\n=== {business_name} ===")
        print(f"Raw: {raw_text[:80]}...")

        deals = parse_deals_from_text(client, business_name, raw_text)

        if not deals:
            print("  No deals extracted.")
            continue

        for deal in deals:
            flag = " [NEEDS REVIEW]" if deal.needs_review else ""
            print(
                f"  -> {deal.title} "
                f"({deal.discount_type.value}, conf={deal.confidence:.2f}){flag}"
            )
        all_deals.extend(deals)

    print(f"\n\nTotal deals extracted: {len(all_deals)}")

    out_path = "parsed_deals.json"
    with open(out_path, "w") as f:
        json.dump([d.model_dump() for d in all_deals], f, indent=2, default=str)
    print(f"Full structured output written to {out_path}")


if __name__ == "__main__":
    main()
