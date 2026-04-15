# Stock Trading Dashboard (Streamlit)

A standalone Python trading dashboard that mirrors the React app's functionality using only `yfinance` + SQLite. No Docker required.

## Quick Start

```bash
cd streamlit-app
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. A local SQLite database (`portfolio.db`) is created automatically on first run with 17 pre-seeded tickers.

## Pages

| Page | What It Does |
|------|-------------|
| Dashboard | Portfolio overview with live prices, holdings table, P&L metrics |
| Trade | Buy/Sell stocks with real-time price lookup and order confirmation |
| Analysis | Interactive candlestick charts with SMA, EMA, RSI overlays |
| Ask Warren | AI investment advisor powered by Anthropic Claude |
| Learn | Tiered coding exercises to extend the dashboard yourself |

## Ask Warren (Optional)

The chatbot requires an Anthropic API key. Set it as an environment variable or paste it in the sidebar:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
streamlit run app.py
```

Without a key, the page shows setup instructions and the rest of the app works normally.

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Point it at `streamlit-app/app.py`
4. Add `ANTHROPIC_API_KEY` in the Secrets panel (optional)

## Teaching Architecture

This app is designed as a teaching tool. Each module demonstrates a specific pattern:

```
 app.py (entry point)
   │
   ├── db.py         ─── SQLite CRUD, schema design, seed data
   │                     Teaches: relational modeling without Docker
   │
   ├── market.py     ─── yfinance wrapper with @st.cache_data
   │                     Teaches: external API integration, TTL caching
   │
   ├── warren.py     ─── Anthropic Claude with prompt reuse
   │                     Teaches: LLM integration, prompt versioning
   │
   └── pages/
       ├── 1_Dashboard.py  ─── st.metric, st.dataframe, column_config
       ├── 2_Trade.py      ─── Forms, validation, sparkline charts
       ├── 3_Analysis.py   ─── Plotly candlestick, SMA/EMA/RSI
       ├── 4_Ask_Warren.py ─── Chat interface, session state
       └── 5_Learn.py      ─── Tiered exercises with solutions
```

The `5_Learn.py` page contains 6 coding exercises at Beginner, Intermediate, and Advanced levels. Each exercise directly extends the dashboard's functionality, reinforcing the patterns used in the other pages.

## Relationship to Other Modules

This is the **Python-native** learning track. The repo also contains:

- `react-app/` for the React/GraphQL/Tailwind learning track
- `flask-app/` for the Flask API learning track
- `docker-compose.yaml` for the Docker orchestration learning track

Each track teaches the same trading platform concept using different technology stacks.
