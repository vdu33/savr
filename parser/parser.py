"""
AI ingestion pipeline: turns messy, unstructured restaurant text
(scraped from a website, copy-pasted from an Instagram caption, typed
in by a business owner) into clean, structured Deal objects.

This is the core "AI competence" piece of the project — not just
calling an LLM, but building a reliable extraction pipeline with
validation, confidence scoring, and graceful failure handling.
"""

import json
import os
from typing import List

import anthropic

from models import Deal

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a data extraction engine for a local restaurant \
deals app. You will be given raw, messy text describing a restaurant's \
discounts or specials (scraped from a website, social post, or typed by \
the owner). Extract every distinct deal mentioned into structured JSON.

Rules:
- Output ONLY a JSON array. No markdown code fences, no commentary, no \
explanation before or after.
- Each element must be an object with exactly these fields:
  "title" (string, short human-readable summary),
  "description" (string or null, one sentence of extra detail if present),
  "discount_type" (one of: "percent_off", "dollar_off", "bogo", \
"fixed_price", "free_item", "happy_hour", "other"),
  "discount_value" (string or null, e.g. "20%", "$5 off", null if unclear),
  "days_valid" (array of lowercase day names, e.g. ["monday", "tuesday"]; \
empty array if every day or unclear),
  "start_time" (24h "HH:MM" string or null),
  "end_time" (24h "HH:MM" string or null),
  "category" (string or null, e.g. "drinks", "entrees", "dessert", "brunch"),
  "confidence" (float 0.0-1.0, your honest confidence this parse is correct),
  "needs_review" (boolean, true if the text was ambiguous, incomplete, or \
you had to guess at any field).
- If the text mentions no real deals, return an empty array: []
- Never invent details that aren't implied by the text. If a field is \
unknown, use null and lower the confidence score.
- Split compound specials into separate deal objects (e.g. "Taco Tuesday \
AND happy hour daily" is two deals).
"""


def parse_deals_from_text(
    client: anthropic.Anthropic, business_name: str, raw_text: str
) -> List[Deal]:
    """
    Send raw text to Claude and return a list of validated Deal objects.

    Any item that fails schema validation is skipped rather than crashing
    the whole batch — bad data from one messy source shouldn't take down
    the pipeline.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Business: {business_name}\n\nRaw text:\n{raw_text}",
            }
        ],
    )

    raw_output = "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()

    # Defensive cleanup in case the model wraps output in fences anyway.
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        if raw_output.lower().startswith("json"):
            raw_output = raw_output[4:]
        raw_output = raw_output.strip()

    try:
        items = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print(f"  [!] Failed to parse JSON for {business_name}: {e}")
        print(f"      Raw output was: {raw_output[:200]}")
        return []

    deals: List[Deal] = []
    for item in items:
        try:
            deal = Deal(
                business_name=business_name,
                source_text=raw_text,
                **item,
            )
            deals.append(deal)
        except Exception as e:
            print(f"  [!] Skipped malformed deal for {business_name}: {e}")

    return deals


def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set the ANTHROPIC_API_KEY environment variable before running this."
        )
    return anthropic.Anthropic(api_key=api_key)
