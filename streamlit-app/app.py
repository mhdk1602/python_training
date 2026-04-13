"""
Stock Trading Dashboard - Streamlit Entry Point

Run: streamlit run app.py

This file initializes the database, configures the sidebar,
and lets Streamlit's native multipage routing handle pages/ navigation.
"""

import streamlit as st
from db import init_db

st.set_page_config(
    page_title="Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ── Custom CSS to tighten spacing and match the terminal aesthetic ──
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    [data-testid="stMetric"] {
        background-color: rgba(19, 26, 43, 0.6);
        border: 1px solid rgba(0, 212, 170, 0.15);
        border-radius: 8px;
        padding: 12px 16px;
    }
    [data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; }
    .stDataFrame { border: 1px solid rgba(0, 212, 170, 0.15); border-radius: 8px; }
    div[data-testid="stExpander"] details {
        border: 1px solid rgba(0, 212, 170, 0.1);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── Landing page content ──
st.title("Stock Trading Dashboard")
st.caption("A standalone Python trading platform. No Docker required.")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Dashboard")
    st.markdown(
        "Portfolio overview with live prices, holdings table, and P&L metrics. "
        "Navigate using the sidebar."
    )

with col2:
    st.markdown("### Trade & Analyze")
    st.markdown(
        "Execute buy/sell orders with real-time pricing. "
        "Interactive candlestick charts with technical indicators."
    )

with col3:
    st.markdown("### Learn & Ask Warren")
    st.markdown(
        "AI-powered investment advisor and hands-on coding exercises "
        "to extend the dashboard yourself."
    )

st.markdown("---")

with st.expander("How this app works"):
    st.markdown("""
**Architecture overview:**

- **Data layer** (`db.py`): SQLite database for portfolio persistence. Schema mirrors the
  Postgres setup in `docker-compose.yaml` so you can compare the two approaches.
- **Market layer** (`market.py`): Wraps `yfinance` with `@st.cache_data` to avoid
  hammering the API on every Streamlit re-render.
- **Chat layer** (`warren.py`): Anthropic Claude integration reusing the same prompt
  template from `flask-app/prompts/base_prompt.txt`.
- **Pages**: Each file in `pages/` is a self-contained Streamlit page. Streamlit
  auto-discovers them and adds sidebar navigation.

**Key Streamlit patterns used:**

- `st.cache_data` for memoizing expensive API calls with TTL-based expiry
- `st.session_state` for persisting chat history and form state across rerenders
- `st.columns` / `st.metric` / `st.dataframe` for responsive layout
- `st.plotly_chart` for interactive financial charts
- `st.chat_message` / `st.chat_input` for the conversational AI interface
""")

st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit, yfinance, and Plotly")
