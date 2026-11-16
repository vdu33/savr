# Local Bites — Deal Parsing Pipeline

Step 1 of the Local Bites project: an AI pipeline that turns messy,
unstructured restaurant text into clean, structured deal data. This is
the foundation everything else (backend, mobile app, recommendations)
builds on.

## Why this exists

Restaurants don't publish "this week's discounts" in a structured
format anywhere. They put it in an Instagram caption, a sentence on
their homepage, a sign in the window. To build a real deals database,
something has to read that messy text and turn it into consistent,
queryable data. That's what this pipeline does — and it's the part of
the project most worth talking about on a resume, since it's real
information extraction, not just a chatbot wrapper.

## Files

- `models.py` — the `Business` and `Deal` schemas (Pydantic). This is
  the contract the whole app will share.
- `parser.py` — sends raw text to Claude with a strict extraction
  prompt, validates the response against the schema, and skips
  malformed items instead of crashing.
- `sample_data.py` — realistic messy example text standing in for
  real scraped/submitted content.
- `test_parser.py` — runs the pipeline end-to-end and writes results
  to `parsed_deals.json`.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python test_parser.py
```

You'll see each sample business's raw text, the deals extracted from
it, and a confidence score per deal. Low-confidence or ambiguous
parses are flagged `needs_review` — in the real app, those would go to
a moderation queue instead of straight to users.

## Design decisions worth knowing (and mentioning in interviews)

- **Confidence scoring + needs_review flag**: rather than trusting
  every LLM output blindly, each deal carries a confidence score and a
  review flag, so low-quality extractions can be caught before they
  reach users. This is the difference between "called an API" and
  "built a pipeline with a quality gate."
- **Provenance (`source_text`)**: every parsed deal keeps its original
  raw text, so a human (or you, debugging) can always check what the
  model saw.
- **Fail gracefully per-item, not per-batch**: one malformed deal in a
  batch of ten doesn't take down the other nine.

## Next steps

1. Swap `sample_data.py` for real text — pull specials pages from 10–15
   real local restaurants near you and run the pipeline on that.
2. Wrap this in a small script that runs weekly (cron/GitHub Actions)
   against your real source list.
3. Move on to the backend: a FastAPI service with a Postgres database
   that stores these Deal objects and exposes a `/deals` endpoint for
   the mobile app to query.
