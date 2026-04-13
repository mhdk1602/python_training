"""
Dashboard: Portfolio overview with live prices, holdings, and P&L metrics.
"""

import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import get_holdings, get_all_tickers, get_transactions, init_db
from market import get_price

init_db()

st.header("Portfolio Dashboard")

with st.expander("How this page works"):
    st.markdown("""
This page demonstrates several Streamlit patterns:

- **`st.metric`** renders KPI cards with built-in delta indicators (green/red arrows).
- **`st.dataframe`** with `column_config` enables typed columns: `NumberColumn` for currency
  formatting, `ProgressColumn` for visual weight bars.
- **`@st.cache_data(ttl=60)`** in `market.py` ensures `yfinance` calls are memoized.
  The TTL (time-to-live) of 60 seconds means prices refresh at most once per minute,
  preventing API rate limits during rapid Streamlit rerenders.
- **`st.columns`** creates a responsive grid layout that adapts to screen width.

The data flow: `db.get_holdings()` returns aggregated share counts from SQLite,
then `market.get_price()` enriches each row with live prices from yfinance.
""")

# ── Fetch holdings and enrich with live prices ──
holdings = get_holdings()
tickers = get_all_tickers()

if not holdings:
    st.info(
        "Your portfolio is empty. Head to the **Trade** page to make your first purchase."
    )
    st.markdown("### Tracked Tickers")
    st.markdown(
        "These tickers are pre-loaded and available for trading:"
    )
    ticker_df = pd.DataFrame(tickers)
    if not ticker_df.empty:
        cols = st.columns(4)
        for i, row in ticker_df.iterrows():
            with cols[i % 4]:
                price_data = get_price(row["ticker"])
                delta_color = "normal"
                st.metric(
                    label=f"{row['ticker']}",
                    value=f"${price_data['price']:.2f}",
                    delta=f"{price_data['change_pct']:+.2f}%",
                )
    st.stop()

# ── Enrich holdings with live market data ──
enriched = []
total_value = 0
total_cost = 0

with st.spinner("Fetching live prices..."):
    for h in holdings:
        price_data = get_price(h["ticker"])
        current_price = price_data["price"]
        market_value = current_price * h["shares"]
        cost_basis = h["avg_cost"] * h["shares"]
        pnl = market_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100) if cost_basis else 0

        total_value += market_value
        total_cost += cost_basis

        enriched.append({
            "Ticker": h["ticker"],
            "Name": h["name"],
            "Shares": h["shares"],
            "Avg Cost": h["avg_cost"],
            "Price": current_price,
            "Day Change": price_data["change_pct"],
            "Market Value": round(market_value, 2),
            "P&L": round(pnl, 2),
            "P&L %": round(pnl_pct, 2),
        })

# ── Summary metrics ──
total_pnl = total_value - total_cost
total_pnl_pct = (total_pnl / total_cost * 100) if total_cost else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Portfolio Value", f"${total_value:,.2f}")
col2.metric("Total P&L", f"${total_pnl:,.2f}", delta=f"{total_pnl_pct:+.2f}%")
col3.metric("Cost Basis", f"${total_cost:,.2f}")
col4.metric("Positions", str(len(holdings)))

st.markdown("---")

# ── Holdings table ──
st.subheader("Holdings")
df = pd.DataFrame(enriched)

st.dataframe(
    df,
    column_config={
        "Avg Cost": st.column_config.NumberColumn(format="$%.2f"),
        "Price": st.column_config.NumberColumn(format="$%.2f"),
        "Day Change": st.column_config.NumberColumn(format="%.2f%%"),
        "Market Value": st.column_config.NumberColumn(format="$%.2f"),
        "P&L": st.column_config.NumberColumn(format="$%.2f"),
        "P&L %": st.column_config.NumberColumn(format="%.2f%%"),
    },
    use_container_width=True,
    hide_index=True,
)

# ── Recent transactions ──
st.markdown("---")
st.subheader("Recent Transactions")

txns = get_transactions()
if txns:
    tx_df = pd.DataFrame(txns[:20])
    display_cols = ["transaction_date", "ticker", "name", "action", "volume", "close", "total_transaction_amount"]
    available_cols = [c for c in display_cols if c in tx_df.columns]
    st.dataframe(
        tx_df[available_cols].rename(columns={
            "transaction_date": "Date",
            "ticker": "Ticker",
            "name": "Name",
            "action": "Action",
            "volume": "Shares",
            "close": "Price",
            "total_transaction_amount": "Total",
        }),
        column_config={
            "Price": st.column_config.NumberColumn(format="$%.2f"),
            "Total": st.column_config.NumberColumn(format="$%.2f"),
        },
        use_container_width=True,
        hide_index=True,
    )
else:
    st.caption("No transactions yet.")
