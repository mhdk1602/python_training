# React Trading Dashboard

> **Learning track:** Frontend Development with React, GraphQL, and Tailwind CSS

## What This Teaches

This is a full-stack React application that connects to a Postgres database via Hasura GraphQL. It demonstrates modern frontend patterns that data engineers encounter when building user-facing data products.

| Concept | Where to Look |
|---------|--------------|
| Component decomposition | `components/` (10 focused components extracted from a monolithic `index.tsx`) |
| Custom React hooks | `hooks/useStockPrices.ts`, `hooks/useTrade.ts`, `hooks/useWarren.ts` |
| GraphQL queries & mutations | `graphql/getStocks.ts`, `graphql/getPortfolioTransactions.ts` |
| Apollo Client setup | `apollo-client.ts` (Hasura) vs `apollo-client-pg.ts` (Postgraphile, legacy) |
| Tailwind CSS styling | Every component; `tailwind.config.ts` for theme customization |
| Real-time data polling | `hooks/useStockPrices.ts` (30-second price refresh via yfinance) |
| AI chatbot integration | `components/AskWarren.tsx` + `hooks/useWarren.ts` |

## Architecture

```
 ┌──────────────────────────────────────────────────┐
 │  React App (NextJS 14)  :3000                    │
 │                                                  │
 │  pages/index.tsx ──▶ Layout + Header             │
 │       │               │                          │
 │       ├── PortfolioSummary (aggregate metrics)   │
 │       ├── HoldingsTable (live prices via hook)   │
 │       ├── TradeModal (buy/sell via GraphQL)       │
 │       ├── TransactionModal (history view)        │
 │       └── AskWarren (chat with Claude)           │
 │                                                  │
 │  hooks/                                          │
 │       ├── useStockPrices.ts  ──▶ Flask API       │
 │       ├── useTrade.ts        ──▶ Hasura GraphQL  │
 │       └── useWarren.ts       ──▶ Flask API       │
 └──────────────────────────────────────────────────┘
          │                              │
          ▼                              ▼
   Hasura GraphQL :8080           Flask API :5002
          │                              │
          ▼                              ▼
   Postgres :5437                 yfinance + Anthropic
```

## Running Locally

Requires Docker (this app is part of the Docker Compose stack):

```bash
cd python_training
docker compose up
# React app at localhost:3000
# Hasura console at localhost:8080
```

## Key Patterns Worth Studying

**Hook extraction.** `useStockPrices.ts` encapsulates the entire price-polling lifecycle: fetch on mount, re-fetch every 30 seconds, clean up on unmount. The component that uses it (`HoldingsTable`) only cares about the returned `prices` object. This separation between data fetching and rendering is the single most important React pattern for data engineers to learn.

**GraphQL over REST.** Compare the Hasura queries in `graphql/getStocks.ts` with what the equivalent REST calls would look like. GraphQL lets the frontend request exactly the fields it needs. For dashboards displaying data from multiple tables, this eliminates the over-fetching problem that REST APIs create.

**Legacy migration.** The `pages/_legacy/pg-index.tsx` file preserves the original Postgraphile-based implementation. Compare it with the current Hasura-based `pages/index.tsx` to see what changed during the migration, and the `graphql/postgraphile/` directory shows the old query structure.

## Relationship to Other Modules

- `flask-app/` provides the backend API that this app calls for prices and the chatbot
- `streamlit-app/` is the Python-native alternative that teaches the same concepts without React
- `notebooks/06-apis-and-frontend/` walks through building this app step by step
