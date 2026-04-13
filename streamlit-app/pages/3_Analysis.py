"""
Analysis: Interactive candlestick charts with volume, moving averages, and RSI.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import get_all_tickers, init_db
from market import get_history, get_company_info, get_price

init_db()

st.header("Technical Analysis")

with st.expander("How this page works"):
    st.markdown("""
This page demonstrates:

- **Plotly `make_subplots`** with `row_heights` and `shared_xaxes` to stack a candlestick
  chart, volume bars, and an RSI oscillator into a single coordinated figure. Zooming or
  panning one subplot automatically adjusts the others.
- **Technical indicators** computed with pure pandas/numpy (no TA-Lib dependency):
  - **SMA** (Simple Moving Average): `df['Close'].rolling(window=N).mean()`
  - **EMA** (Exponential Moving Average): `df['Close'].ewm(span=N).mean()`
  - **RSI** (Relative Strength Index): measures momentum by comparing the magnitude
    of recent gains to recent losses on a 0-100 scale. Values above 70 suggest
    overbought conditions; below 30 suggests oversold.
- **`st.multiselect`** lets users toggle overlays without reloading data.
- **`st.plotly_chart(use_container_width=True)`** makes the chart responsive.

All market data comes from `yfinance` via `market.get_history()`, cached for 5 minutes.
""")


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ── Controls ──
tickers = get_all_tickers()
ticker_list = [t["ticker"] for t in tickers]

col_ticker, col_period = st.columns([2, 1])
with col_ticker:
    ticker = st.selectbox("Ticker", ticker_list, index=ticker_list.index("NVDA") if "NVDA" in ticker_list else 0)
with col_period:
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

overlays = st.multiselect(
    "Overlays",
    ["SMA-20", "SMA-50", "EMA-12", "EMA-26", "RSI-14"],
    default=["SMA-20"],
)

# ── Fetch data ──
df = get_history(ticker, period)

if df.empty:
    st.warning(f"No historical data available for {ticker}.")
    st.stop()

# ── Company context ──
price_data = get_price(ticker)
info = get_company_info(ticker)

col_info1, col_info2, col_info3, col_info4 = st.columns(4)
col_info1.metric(ticker, f"${price_data['price']:.2f}", f"{price_data['change_pct']:+.2f}%")
col_info2.metric("52W High", f"${info['52w_high']:.2f}" if info["52w_high"] else "N/A")
col_info3.metric("52W Low", f"${info['52w_low']:.2f}" if info["52w_low"] else "N/A")
col_info4.metric("P/E Ratio", f"{info['pe_ratio']:.1f}" if info["pe_ratio"] else "N/A")

# ── Compute indicators ──
show_rsi = "RSI-14" in overlays
num_rows = 3 if show_rsi else 2
row_heights = [0.5, 0.2, 0.3] if show_rsi else [0.7, 0.3]

fig = make_subplots(
    rows=num_rows, cols=1, shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=row_heights,
    subplot_titles=([ticker, "Volume"] + (["RSI(14)"] if show_rsi else [])),
)

# ── Candlestick ──
fig.add_trace(go.Candlestick(
    x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
    name="OHLC",
    increasing_line_color="#00d4aa", decreasing_line_color="#ef4444",
    increasing_fillcolor="#00d4aa", decreasing_fillcolor="#ef4444",
), row=1, col=1)

# ── Moving average overlays ──
overlay_colors = {
    "SMA-20": ("#fbbf24", 20, "sma"),
    "SMA-50": ("#f97316", 50, "sma"),
    "EMA-12": ("#818cf8", 12, "ema"),
    "EMA-26": ("#c084fc", 26, "ema"),
}

for name in overlays:
    if name in overlay_colors:
        color, window, ma_type = overlay_colors[name]
        if ma_type == "sma":
            values = df["Close"].rolling(window=window).mean()
        else:
            values = df["Close"].ewm(span=window, adjust=False).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=values, mode="lines",
            name=name, line=dict(color=color, width=1.5),
        ), row=1, col=1)

# ── Volume bars ──
colors = ["#00d4aa" if c >= o else "#ef4444" for c, o in zip(df["Close"], df["Open"])]
fig.add_trace(go.Bar(
    x=df.index, y=df["Volume"], name="Volume",
    marker_color=colors, opacity=0.6,
), row=2, col=1)

# ── RSI subplot ──
if show_rsi:
    rsi = compute_rsi(df["Close"])
    fig.add_trace(go.Scatter(
        x=df.index, y=rsi, mode="lines",
        name="RSI(14)", line=dict(color="#00d4aa", width=1.5),
    ), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", opacity=0.5, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#22c55e", opacity=0.5, row=3, col=1)
    fig.update_yaxes(range=[0, 100], row=3, col=1)

# ── Layout ──
fig.update_layout(
    height=700 if show_rsi else 550,
    xaxis_rangeslider_visible=False,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,14,23,0.8)",
    font=dict(color="#e2e8f0"),
    margin=dict(l=60, r=20, t=40, b=20),
)
fig.update_xaxes(gridcolor="rgba(0,212,170,0.06)")
fig.update_yaxes(gridcolor="rgba(0,212,170,0.06)")

st.plotly_chart(fig, use_container_width=True)

# ── Data table ──
with st.expander("Raw OHLCV Data"):
    st.dataframe(
        df.tail(30).sort_index(ascending=False)[["Open", "High", "Low", "Close", "Volume"]],
        column_config={
            "Open": st.column_config.NumberColumn(format="$%.2f"),
            "High": st.column_config.NumberColumn(format="$%.2f"),
            "Low": st.column_config.NumberColumn(format="$%.2f"),
            "Close": st.column_config.NumberColumn(format="$%.2f"),
            "Volume": st.column_config.NumberColumn(format="%d"),
        },
        use_container_width=True,
    )
