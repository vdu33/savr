# Savr (working title)

A mobile app that surfaces local food businesses' weekly discounts, so people can choose where to eat based on deals and small businesses get discovered.

**Status:** working prototype running on a small sample dataset. Not publicly launched.

## How it works

Restaurants announce deals in messy, unstructured formats (website blurbs, social captions, signs). Savr uses an LLM extraction pipeline to turn that text into structured data, stores it in a database, serves it through an API, and displays it in a mobile app.

    raw promo text -> Claude extraction -> validated deal records -> PostgreSQL -> FastAPI -> React Native app

## Components

- **parser/** - Python pipeline that sends raw restaurant text to the Claude API and returns validated, structured deals (title, discount type, days, times, category) with a confidence score for each.
- **backend/** - FastAPI service with SQLAlchemy. Stores businesses and deals and exposes a REST API with filtering by day, category, discount type, and minimum confidence. Deployed on Railway with PostgreSQL.
- **mobile/** - React Native (Expo) app that fetches deals from the hosted API and displays them in a scrollable, refreshable list.

## Design decisions

- **Confidence scores and a needs_review flag.** Every extracted deal carries a confidence value, and ambiguous parses are flagged so they can be reviewed before reaching users instead of being trusted blindly.
- **Provenance.** Each deal keeps the original source text it was extracted from, for auditing and debugging bad parses.
- **Per-item failure handling.** One malformed deal in a batch is skipped without breaking the rest.
- **Separate storage and API models.** Database models and API schemas are kept apart so each can change independently.
- **Environment-based database config.** SQLite for local development, PostgreSQL in production, switched by a single DATABASE_URL variable.

## Running locally

Parser:

    cd parser
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=your_key_here
    python3 test_parser.py

Backend:

    cd backend
    pip install -r requirements.txt
    python3 seed_from_parsed_deals.py
    uvicorn main:app --reload --host 0.0.0.0

Mobile (point API_URL in src/app/index.js at your own backend first):

    cd mobile
    npm install
    npx expo start

## Roadmap

- Replace sample data with real local restaurants
- Measure parser accuracy against a hand-labeled test set
- Business self-signup so owners can post their own deals
- Semantic search ("cheap spicy food tonight")
- Scheduled weekly data refresh

## Tech

Python, FastAPI, SQLAlchemy, PostgreSQL, Claude API (Anthropic), React Native (Expo), Railway.
