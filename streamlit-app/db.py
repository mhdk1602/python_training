"""
SQLite persistence layer for the trading dashboard.

Schema mirrors postgres/init/02_init.sql so learners can compare
the two implementations side-by-side. Uses stdlib sqlite3 only.
"""

import sqlite3
import os
from datetime import datetime, date
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db")

SEED_TICKERS = {
    "AAPL": "Apple Inc.",
    "AMD": "Advanced Micro Devices Inc.",
    "GE": "GE Aerospace",
    "GOOG": "Alphabet Inc.",
    "INTC": "Intel Corporation",
    "JBLU": "JetBlue Airways Corporation",
    "META": "Meta Platforms Inc.",
    "MSFT": "Microsoft Corporation",
    "MSTR": "MicroStrategy Incorporated",
    "NFLX": "Netflix Inc.",
    "NVDA": "NVIDIA Corporation",
    "ORCL": "Oracle Corporation",
    "SNOW": "Snowflake Inc.",
    "TSLA": "Tesla Inc.",
    "TSM": "Taiwan Semiconductor Manufacturing",
    "VOO": "Vanguard S&P 500 ETF",
    "VTI": "Vanguard Total Stock Market ETF",
}


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables and seed tickers if the database is fresh."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT PRIMARY KEY,
            name   TEXT
        );

        CREATE TABLE IF NOT EXISTS portfolio (
            id                       INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker                   TEXT REFERENCES stocks(ticker),
            transaction_date         TEXT,
            action                   TEXT,
            volume                   INTEGER,
            close                    REAL,
            total_transaction_amount REAL
        );

        CREATE TABLE IF NOT EXISTS company_overview (
            ticker      TEXT PRIMARY KEY REFERENCES stocks(ticker),
            sector      TEXT,
            industry    TEXT,
            market_cap  TEXT,
            description TEXT,
            as_of_date  TEXT
        );
    """)

    existing = {r[0] for r in conn.execute("SELECT ticker FROM stocks").fetchall()}
    for ticker, name in SEED_TICKERS.items():
        if ticker not in existing:
            conn.execute("INSERT INTO stocks (ticker, name) VALUES (?, ?)", (ticker, name))
    conn.commit()
    conn.close()


def get_all_tickers() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("SELECT ticker, name FROM stocks ORDER BY ticker").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_trade(ticker: str, name: str, action: str, volume: int, close: float) -> None:
    """Record a buy/sell transaction. Creates the stock row if it doesn't exist."""
    conn = _get_conn()
    existing = conn.execute("SELECT 1 FROM stocks WHERE ticker = ?", (ticker,)).fetchone()
    if not existing:
        conn.execute("INSERT INTO stocks (ticker, name) VALUES (?, ?)", (ticker, name))

    conn.execute(
        """INSERT INTO portfolio (ticker, transaction_date, action, volume, close, total_transaction_amount)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (ticker, datetime.utcnow().isoformat(), action, volume, close, round(close * volume, 2)),
    )
    conn.commit()
    conn.close()


def get_holdings() -> list[dict]:
    """
    Aggregate portfolio into net holdings per ticker.
    Buy adds shares, Sell subtracts. Returns only tickers with positive share count.
    """
    conn = _get_conn()
    rows = conn.execute("""
        SELECT
            p.ticker,
            s.name,
            SUM(CASE WHEN p.action = 'Buy' THEN p.volume ELSE -p.volume END) AS total_shares,
            SUM(CASE WHEN p.action = 'Buy' THEN p.total_transaction_amount ELSE 0 END) AS total_cost_basis,
            SUM(CASE WHEN p.action = 'Buy' THEN p.volume ELSE 0 END) AS total_bought
        FROM portfolio p
        JOIN stocks s ON s.ticker = p.ticker
        GROUP BY p.ticker
        HAVING total_shares > 0
        ORDER BY p.ticker
    """).fetchall()
    conn.close()

    holdings = []
    for r in rows:
        total_bought = r["total_bought"] or 1
        holdings.append({
            "ticker": r["ticker"],
            "name": r["name"],
            "shares": r["total_shares"],
            "avg_cost": round(r["total_cost_basis"] / total_bought, 2) if total_bought else 0,
        })
    return holdings


def get_transactions(ticker: Optional[str] = None) -> list[dict]:
    conn = _get_conn()
    if ticker:
        rows = conn.execute(
            """SELECT p.*, s.name FROM portfolio p
               JOIN stocks s ON s.ticker = p.ticker
               WHERE p.ticker = ? ORDER BY p.transaction_date DESC""",
            (ticker,),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT p.*, s.name FROM portfolio p
               JOIN stocks s ON s.ticker = p.ticker
               ORDER BY p.transaction_date DESC""",
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_portfolio_value_series() -> list[dict]:
    """Daily total transaction amounts for portfolio value tracking."""
    conn = _get_conn()
    rows = conn.execute("""
        SELECT DATE(transaction_date) as trade_date,
               SUM(CASE WHEN action = 'Buy' THEN total_transaction_amount ELSE -total_transaction_amount END) as net_flow
        FROM portfolio
        GROUP BY DATE(transaction_date)
        ORDER BY trade_date
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_company_overview(ticker: str, sector: str, industry: str,
                             market_cap: str, description: str) -> None:
    conn = _get_conn()
    conn.execute(
        """INSERT INTO company_overview (ticker, sector, industry, market_cap, description, as_of_date)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(ticker) DO UPDATE SET
               sector=excluded.sector, industry=excluded.industry,
               market_cap=excluded.market_cap, description=excluded.description,
               as_of_date=excluded.as_of_date""",
        (ticker, sector, industry, market_cap, description, date.today().isoformat()),
    )
    conn.commit()
    conn.close()
