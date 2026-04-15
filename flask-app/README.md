# Flask API Backend

> **Learning track:** Python API Development, Market Data Integration, and LLM Integration

## What This Teaches

This is the API layer that bridges the frontend (React and Streamlit) to external data sources (yfinance for market data, Anthropic Claude for the chatbot). It demonstrates patterns common in production data applications: REST endpoints, external API wrapping, prompt management, and file-based caching.

| Concept | Where to Look |
|---------|--------------|
| Flask REST API | `pg-app.py` (routes: `/api/stock-price`, `/api/ask-warren`, etc.) |
| External API wrapping | `pg-app.py` yfinance calls with error handling and formatting |
| LLM prompt management | `prompts/base_prompt.txt` (single source of truth for chatbot behavior) |
| File-based caching | `news/` directory (JSON files keyed by `{TICKER}_news_{DATE}.json`) |
| Docker deployment | `Dockerfile` (Python 3.9 slim image with gunicorn) |

## Architecture

```
                ┌──────────────────────────┐
                │     Flask API :5002      │
                │                          │
                │  /api/stock-price/:tick  │──▶ yfinance
                │  /api/stock-history      │──▶ yfinance
                │  /api/company-overview   │──▶ yfinance
                │  /api/ask-warren         │──▶ Anthropic Claude
                │  /api/news/:ticker       │──▶ cached JSON / yfinance
                │                          │
                └──────────┬───────────────┘
                           │
              ┌────────────┼────────────────┐
              ▼            ▼                ▼
        React App    Streamlit App    prompts/base_prompt.txt
        (consumer)   (reuses prompt)  (shared behavior config)
```

## Key Files

**`pg-app.py`** is the main application file. Despite the name (a remnant of the Postgraphile era), it is a straightforward Flask app with five route groups. The `format_market_cap()` utility converts raw numbers to human-readable strings ("$1.2T") and is reused by the Streamlit app's `market.py`.

**`prompts/base_prompt.txt`** defines the "Ask Warren" chatbot persona. It caps responses at 150 words and instructs the model to ground advice in the provided market data. Both the Flask endpoint and Streamlit's `warren.py` read this file, ensuring consistent chatbot behavior across both frontends.

**`news/`** contains pre-fetched news JSON files for 17 tickers across 3 dates. This acts as a local cache so the chatbot can provide news context without hitting the yfinance API on every request.

## Running Locally

As part of the Docker Compose stack:

```bash
cd python_training
docker compose up
# Flask API at localhost:5002
```

Standalone (without Docker):

```bash
cd flask-app
pip install -r requirements.txt
python pg-app.py
```

## Patterns Worth Studying

**Prompt as a versioned artifact.** The `base_prompt.txt` file is checked into Git. Any change to the chatbot's behavior is visible in the commit history. This is a lightweight alternative to prompt management platforms, and it works well for single-prompt applications.

**File-based caching.** The `news/` directory stores API responses as individual JSON files with a predictable naming convention. This is the simplest caching pattern: no Redis, no TTL logic, just files on disk. It works for data that changes infrequently. For more volatile data (prices), the Streamlit app uses in-memory TTL caching instead.

**API as a translation layer.** The Flask routes do not contain business logic. They translate between the frontend's data needs and the external APIs' response formats. This thin-API pattern keeps the backend simple and pushes complexity to the frontend (for rendering) or the data source (for computation).

## Relationship to Other Modules

- `react-app/` consumes this API for prices, company data, and the chatbot
- `streamlit-app/warren.py` reads `prompts/base_prompt.txt` directly (no API call needed since both are Python)
- `notebooks/06-apis-and-frontend/6.1-6.6` walk through building and extending this API
