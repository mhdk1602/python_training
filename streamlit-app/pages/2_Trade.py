"""
Trade: Buy/Sell stocks with real-time price lookup, sparkline preview, and order confirmation.
"""

import streamlit as st
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import get_all_tickers, get_holdings, insert_trade, init_db
from market import get_price, get_sparkline, get_company_info

init_db()

st.header("Trade")

with st.expander("How this page works"):
    st.markdown("""
This page demonstrates:

- **`st.form`** groups multiple inputs and submits them atomically. Without a form,
  every widget change triggers a Streamlit rerun. The form batches all inputs and only
  reruns on submit.
- **`st.selectbox`** with a computed options list (seeded tickers + any custom entries).
- **`st.session_state`** tracks the confirmation dialog state across reruns.
  Streamlit reruns the entire script on every interaction, so stateful workflows
  (like "click trade, then confirm") require explicit session state management.
- **Plotly sparkline**: a minimal line chart with no axes, grid, or margins, created
  by disabling all layout chrome. Useful for inline data previews.

The trade flow: select ticker, choose action and quantity, preview the order,
confirm, then `db.insert_trade()` writes to SQLite.
""")

# ── Ticker selection ──
tickers = get_all_tickers()
ticker_list = [t["ticker"] for t in tickers]
ticker_map = {t["ticker"]: t["name"] for t in tickers}

col_select, col_custom = st.columns([3, 1])
with col_select:
    selected = st.selectbox("Select Ticker", ticker_list, index=0)
with col_custom:
    custom = st.text_input("Or enter custom", placeholder="e.g. AMZN").upper().strip()

ticker = custom if custom else selected

# ── Live price and company preview ──
price_data = get_price(ticker)
info = get_company_info(ticker)

col_price, col_spark = st.columns([2, 1])

with col_price:
    st.metric(
        label=f"{price_data['name']} ({ticker})",
        value=f"${price_data['price']:.2f}",
        delta=f"{price_data['change_pct']:+.2f}%",
    )
    st.caption(f"{info['sector']}  |  {info['industry']}  |  Mkt Cap: {info['market_cap']}")

with col_spark:
    sparkline_data = get_sparkline(ticker, days=5)
    if sparkline_data and len(sparkline_data) > 1:
        color = "#00d4aa" if sparkline_data[-1] >= sparkline_data[0] else "#ef4444"
        fill = "rgba(0,212,170,0.1)" if color == "#00d4aa" else "rgba(239,68,68,0.1)"
        fig = go.Figure(go.Scatter(
            y=sparkline_data, mode="lines",
            line=dict(color=color, width=2),
            fill="tozeroy", fillcolor=fill,
        ))
        fig.update_layout(
            height=80, margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.caption("Sparkline unavailable")

st.markdown("---")

# ── Current holdings context ──
holdings = get_holdings()
current_holding = next((h for h in holdings if h["ticker"] == ticker), None)
if current_holding:
    st.info(f"You currently hold **{current_holding['shares']}** shares of {ticker} at avg cost **${current_holding['avg_cost']:.2f}**")

# ── Trade form ──
with st.form("trade_form", clear_on_submit=True):
    col_action, col_qty = st.columns(2)
    with col_action:
        action = st.radio("Action", ["Buy", "Sell"], horizontal=True)
    with col_qty:
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)

    total = round(price_data["price"] * quantity, 2)

    st.html(
        f'<p style="margin:0;color:#e2e8f0"><strong>Order preview:</strong> '
        f'{action} {quantity} x {ticker} @ ${price_data["price"]:.2f} = '
        f'<strong>${total:,.2f}</strong></p>'
    )

    if action == "Sell" and current_holding and quantity > current_holding["shares"]:
        st.warning(f"You only hold {current_holding['shares']} shares. This order would exceed your position.")

    submitted = st.form_submit_button(
        f"Execute {action}",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if price_data["price"] <= 0:
        st.error("Cannot execute trade: unable to fetch a valid price for this ticker.")
    elif action == "Sell" and (not current_holding or quantity > current_holding["shares"]):
        st.error("Insufficient shares for this sell order.")
    else:
        insert_trade(
            ticker=ticker,
            name=price_data["name"],
            action=action,
            volume=quantity,
            close=price_data["price"],
        )
        st.success(f"{action} order executed: {quantity} shares of {ticker} @ ${price_data['price']:.2f}")
        st.balloons()
        get_price.clear()
