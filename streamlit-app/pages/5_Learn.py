"""
Learn: Tiered coding exercises to extend the trading dashboard.

Each exercise is self-contained with a problem statement, hints,
and an expandable solution. Exercises reference actual code in this app
so learners are modifying a real, working system.
"""

import streamlit as st

st.header("Learning Exercises")
st.caption("Hands-on challenges to extend this dashboard. Each exercise builds on the app you're running right now.")

with st.expander("How this page works"):
    st.markdown("""
This page is purely educational content rendered with Streamlit's markdown and
expander components. The exercises are designed in three tiers:

- **Beginner**: Small, focused changes to a single file. Builds confidence
  with Streamlit widgets and pandas operations.
- **Intermediate**: Multi-file changes that combine the data, market, and UI layers.
  Introduces new Plotly chart types and Streamlit patterns.
- **Advanced**: Open-ended design challenges that require architectural decisions.
  Closer to real-world feature work.

Each exercise follows the same structure: problem statement, which files to modify,
hints (collapsed), and a reference solution (collapsed). Try to solve the problem
before looking at the solution.
""")

st.markdown("---")

# ═══════════════════════════════════════════════════════════
# BEGINNER EXERCISES
# ═══════════════════════════════════════════════════════════
st.subheader("Beginner")

st.markdown("#### Exercise 1: Add a 'Sector' Column to the Dashboard Holdings Table")
st.markdown("""
**Goal:** The Dashboard page shows holdings with ticker, name, shares, and prices.
Add a "Sector" column by fetching company info for each holding.

**Files to modify:** `pages/1_Dashboard.py`

**Skills practiced:** Calling functions from other modules, adding columns to a DataFrame.
""")

with st.expander("Hints"):
    st.markdown("""
1. Import `get_company_info` from `market.py` (it's already available in the module).
2. Inside the loop where `enriched` rows are built, call `get_company_info(h["ticker"])`.
3. Add a `"Sector": info["sector"]` key to the dictionary being appended.
4. The `st.dataframe` call will automatically pick up the new column.
""")

with st.expander("Solution"):
    st.code("""
# In pages/1_Dashboard.py, add to the imports:
from market import get_price, get_company_info

# Inside the enrichment loop, after getting price_data:
for h in holdings:
    price_data = get_price(h["ticker"])
    info = get_company_info(h["ticker"])  # <-- add this line
    current_price = price_data["price"]
    # ... existing P&L calculations ...

    enriched.append({
        "Ticker": h["ticker"],
        "Name": h["name"],
        "Sector": info["sector"],       # <-- add this field
        "Shares": h["shares"],
        # ... rest of the fields ...
    })
""", language="python")

st.markdown("---")

st.markdown("#### Exercise 2: Add a Portfolio Allocation Pie Chart")
st.markdown("""
**Goal:** Below the holdings table on the Dashboard, add a pie chart showing
what percentage of total portfolio value each stock represents.

**Files to modify:** `pages/1_Dashboard.py`

**Skills practiced:** Plotly pie charts, computing proportions from a DataFrame.
""")

with st.expander("Hints"):
    st.markdown("""
1. After creating the `df` DataFrame, you already have a "Market Value" column.
2. Use `plotly.express.pie(df, values="Market Value", names="Ticker")`.
3. Render with `st.plotly_chart(fig, use_container_width=True)`.
4. Set `hole=0.4` for a donut chart variant.
""")

with st.expander("Solution"):
    st.code("""
import plotly.express as px

# After the holdings table section:
st.subheader("Allocation")
fig = px.pie(
    df, values="Market Value", names="Ticker",
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Set3,
)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0"),
)
st.plotly_chart(fig, use_container_width=True)
""", language="python")

st.markdown("---")

# ═══════════════════════════════════════════════════════════
# INTERMEDIATE EXERCISES
# ═══════════════════════════════════════════════════════════
st.subheader("Intermediate")

st.markdown("#### Exercise 3: Add Bollinger Bands to the Analysis Chart")
st.markdown("""
**Goal:** On the Analysis page, add Bollinger Bands as a new overlay option.
Bollinger Bands consist of three lines: a 20-period SMA (the middle band),
an upper band at SMA + 2 standard deviations, and a lower band at SMA - 2
standard deviations.

**Files to modify:** `pages/3_Analysis.py`

**Skills practiced:** Pandas rolling statistics, Plotly filled area traces, multi-select integration.
""")

with st.expander("Hints"):
    st.markdown("""
1. Add `"Bollinger Bands"` to the `overlays` multiselect options list.
2. Compute: `sma = df['Close'].rolling(20).mean()` and `std = df['Close'].rolling(20).std()`.
3. Upper = `sma + 2*std`, Lower = `sma - 2*std`.
4. Add the middle band as a line trace, and the upper/lower as a filled area using
   `go.Scatter` with `fill='tonexty'` and a semi-transparent color.
""")

with st.expander("Solution"):
    st.code("""
# Add "Bollinger Bands" to the multiselect:
overlays = st.multiselect(
    "Overlays",
    ["SMA-20", "SMA-50", "EMA-12", "EMA-26", "RSI-14", "Bollinger Bands"],
    default=["SMA-20"],
)

# After the moving average overlay loop, add:
if "Bollinger Bands" in overlays:
    sma20 = df["Close"].rolling(window=20).mean()
    std20 = df["Close"].rolling(window=20).std()
    upper = sma20 + 2 * std20
    lower = sma20 - 2 * std20

    fig.add_trace(go.Scatter(
        x=df.index, y=upper, mode="lines",
        name="BB Upper", line=dict(color="#6366f1", width=1, dash="dot"),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=lower, mode="lines",
        name="BB Lower", line=dict(color="#6366f1", width=1, dash="dot"),
        fill="tonexty", fillcolor="rgba(99,102,241,0.08)",
    ), row=1, col=1)
""", language="python")

st.markdown("---")

st.markdown("#### Exercise 4: Add a Watchlist Feature")
st.markdown("""
**Goal:** Create a watchlist that persists across sessions. Users should be able
to add tickers to a watchlist on the Dashboard page and see live prices for
just their watched tickers, separate from their portfolio holdings.

**Files to modify:** `db.py` (new table), `pages/1_Dashboard.py` (new section)

**Skills practiced:** SQLite DDL, new CRUD operations, Streamlit session state, multi-file changes.
""")

with st.expander("Hints"):
    st.markdown("""
1. In `db.py`, add a `watchlist` table: `CREATE TABLE IF NOT EXISTS watchlist (ticker TEXT PRIMARY KEY)`.
2. Add `add_to_watchlist(ticker)`, `remove_from_watchlist(ticker)`, `get_watchlist()` functions.
3. In `pages/1_Dashboard.py`, add a new section after the holdings table.
4. Use `st.multiselect` pre-populated with the current watchlist, and a button to save changes.
5. Loop through watchlist tickers and display with `st.metric` in a grid.
""")

with st.expander("Solution"):
    st.code("""
# In db.py, add to init_db():
conn.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS watchlist (
        ticker TEXT PRIMARY KEY REFERENCES stocks(ticker)
    )
\"\"\")

# New functions in db.py:
def add_to_watchlist(ticker: str) -> None:
    conn = _get_conn()
    conn.execute("INSERT OR IGNORE INTO watchlist (ticker) VALUES (?)", (ticker,))
    conn.commit()
    conn.close()

def remove_from_watchlist(ticker: str) -> None:
    conn = _get_conn()
    conn.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker,))
    conn.commit()
    conn.close()

def get_watchlist() -> list[str]:
    conn = _get_conn()
    rows = conn.execute("SELECT ticker FROM watchlist ORDER BY ticker").fetchall()
    conn.close()
    return [r["ticker"] for r in rows]

# In pages/1_Dashboard.py, add after the transactions section:
st.subheader("Watchlist")
from db import get_watchlist, add_to_watchlist, remove_from_watchlist

watchlist = get_watchlist()
new_watch = st.selectbox("Add to watchlist", [t for t in ticker_list if t not in watchlist])
if st.button("Add"):
    add_to_watchlist(new_watch)
    st.rerun()

if watchlist:
    cols = st.columns(min(len(watchlist), 4))
    for i, t in enumerate(watchlist):
        with cols[i % 4]:
            p = get_price(t)
            st.metric(t, f"${p['price']:.2f}", f"{p['change_pct']:+.2f}%")
""", language="python")

st.markdown("---")

# ═══════════════════════════════════════════════════════════
# ADVANCED EXERCISES
# ═══════════════════════════════════════════════════════════
st.subheader("Advanced")

st.markdown("#### Exercise 5: Implement a Stop-Loss / Take-Profit Alert System")
st.markdown("""
**Goal:** Build an alert system where users can set price thresholds on their holdings.
When the live price crosses a threshold, display a prominent notification on the Dashboard.

This is an open-ended design challenge. Consider:
- Where to store alerts (new SQLite table? session state?)
- How to check thresholds (during the price fetch loop? separate polling?)
- How to display notifications (st.warning? st.toast? sidebar badge?)
- Should alerts be one-time or persistent?

**Files to modify:** `db.py`, `pages/1_Dashboard.py`, possibly a new `pages/` file

**Skills practiced:** Database design, background state management, Streamlit notifications, UX decisions.
""")

with st.expander("Design Scaffold"):
    st.code("""
# Suggested schema for db.py:
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT REFERENCES stocks(ticker),
    alert_type TEXT CHECK(alert_type IN ('stop_loss', 'take_profit')),
    threshold REAL,
    created_at TEXT,
    triggered_at TEXT,  -- NULL until fired
    active INTEGER DEFAULT 1
);

# Suggested functions:
def create_alert(ticker, alert_type, threshold): ...
def get_active_alerts(): ...
def trigger_alert(alert_id): ...

# In the Dashboard's price-fetch loop, check alerts:
active_alerts = get_active_alerts()
for alert in active_alerts:
    price = prices.get(alert["ticker"], 0)
    if alert["alert_type"] == "stop_loss" and price <= alert["threshold"]:
        trigger_alert(alert["id"])
        st.toast(f"STOP LOSS: {alert['ticker']} hit ${price:.2f}")
    elif alert["alert_type"] == "take_profit" and price >= alert["threshold"]:
        trigger_alert(alert["id"])
        st.toast(f"TAKE PROFIT: {alert['ticker']} hit ${price:.2f}")
""", language="python")

st.markdown("---")

st.markdown("#### Exercise 6: Add a Backtesting Engine")
st.markdown("""
**Goal:** Build a page where users can define a simple trading strategy
(e.g., "buy when RSI < 30, sell when RSI > 70") and backtest it against
historical data for any ticker.

Display:
- Equity curve (portfolio value over time)
- Total return vs. buy-and-hold
- Max drawdown
- Win rate (percentage of profitable trades)

**Files to create:** `pages/6_Backtest.py`

**Skills practiced:** Financial modeling, vectorized pandas operations, strategy pattern, Plotly time series.
""")

with st.expander("Design Scaffold"):
    st.code("""
# pages/6_Backtest.py skeleton:
import streamlit as st
import pandas as pd
from market import get_history

st.header("Strategy Backtester")

ticker = st.selectbox("Ticker", [...])
period = st.selectbox("Backtest Period", ["1y", "2y", "5y"])

# Strategy parameters
rsi_buy = st.slider("Buy when RSI below", 10, 50, 30)
rsi_sell = st.slider("Sell when RSI above", 50, 90, 70)
initial_capital = st.number_input("Starting Capital ($)", value=10000)

df = get_history(ticker, period)

# Compute RSI (reuse from Analysis page)
# Generate signals: 1 = buy, -1 = sell, 0 = hold
# Simulate trades with a position tracker
# Compute equity curve, drawdown, win rate

# Compare to buy-and-hold:
# buy_hold_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100

# Display results with st.metric and plotly
""", language="python")

st.markdown("---")

st.subheader("Contribution Guide")
st.markdown("""
Completed an exercise? Consider submitting a PR to the repository.

1. Create a branch: `git checkout -b exercise/your-name/exercise-N`
2. Implement your solution
3. Add a brief writeup in the PR description explaining your approach
4. Tag it with the `learning-exercise` label

Good solutions may be featured as alternative implementations in future versions of this page.
""")
