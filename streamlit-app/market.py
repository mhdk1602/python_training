"""
Market data layer wrapping yfinance.

All functions use @st.cache_data with a TTL so repeated renders
within the same minute hit the cache instead of the yfinance API.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime


def format_market_cap(market_cap: float | None) -> str:
    if market_cap is None:
        return "N/A"
    if market_cap >= 1e12:
        return f"{market_cap / 1e12:.2f}T"
    if market_cap >= 1e9:
        return f"{market_cap / 1e9:.2f}B"
    if market_cap >= 1e6:
        return f"{market_cap / 1e6:.2f}M"
    return f"{market_cap:.2f}"


@st.cache_data(ttl=60, show_spinner=False)
def get_price(ticker: str) -> dict:
    """
    Fetch the current price for a single ticker.
    Returns {"price": float, "change": float, "change_pct": float, "name": str}.
    """
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="2d")
        if hist.empty:
            return {"price": 0, "change": 0, "change_pct": 0, "name": ticker}

        current = hist["Close"].iloc[-1]
        previous = hist["Close"].iloc[-2] if len(hist) >= 2 else current
        change = current - previous
        change_pct = (change / previous * 100) if previous else 0

        info = t.info
        name = info.get("longName") or info.get("shortName") or ticker

        return {
            "price": round(current, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "name": name,
        }
    except Exception:
        return {"price": 0, "change": 0, "change_pct": 0, "name": ticker}


@st.cache_data(ttl=300, show_spinner=False)
def get_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """OHLCV history. period accepts yfinance strings like 1mo, 3mo, 6mo, 1y, 5y, max."""
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period)
        df.index = df.index.tz_localize(None)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_company_info(ticker: str) -> dict:
    """Sector, industry, market cap, description, and basic stats."""
    try:
        info = yf.Ticker(ticker).info
        return {
            "name": info.get("longName") or info.get("shortName") or ticker,
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": format_market_cap(info.get("marketCap")),
            "market_cap_raw": info.get("marketCap", 0),
            "description": info.get("longBusinessSummary", "No description available."),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": info.get("dividendYield"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
        }
    except Exception:
        return {
            "name": ticker, "sector": "N/A", "industry": "N/A",
            "market_cap": "N/A", "market_cap_raw": 0,
            "description": "Unable to fetch data.", "pe_ratio": None,
            "dividend_yield": None, "52w_high": None, "52w_low": None,
        }


@st.cache_data(ttl=1800, show_spinner=False)
def get_news(ticker: str, max_items: int = 5) -> list[dict]:
    """Recent news headlines from yfinance."""
    try:
        items = yf.Ticker(ticker).news or []
        results = []
        for item in items[:max_items]:
            results.append({
                "title": item.get("content", {}).get("title", item.get("title", "No title")),
                "publisher": item.get("content", {}).get("provider", {}).get("displayName", ""),
                "link": item.get("content", {}).get("canonicalUrl", {}).get("url", item.get("link", "")),
            })
        return results
    except Exception:
        return []


def get_sparkline(ticker: str, days: int = 5) -> list[float]:
    """Small list of closing prices for a mini chart."""
    try:
        hist = yf.Ticker(ticker).history(period=f"{days}d")
        return hist["Close"].tolist()
    except Exception:
        return []
