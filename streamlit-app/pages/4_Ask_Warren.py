"""
Ask Warren: AI investment advisor powered by Anthropic Claude.

Falls back gracefully if no API key is configured, allowing
the rest of the app to function without it.
"""

import streamlit as st
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import get_all_tickers, init_db
from market import get_price, get_company_info, get_news
from warren import chat, get_api_key

init_db()

st.header("Ask Warren")

with st.expander("How this page works"):
    st.markdown("""
This page demonstrates:

- **`st.chat_message`** and **`st.chat_input`** for a conversational interface.
  Each message is rendered in a bubble with a role icon (user or assistant).
- **`st.session_state`** stores the full chat history list so it persists across
  Streamlit reruns. Without this, the chat would reset on every interaction.
- **Graceful degradation**: the page checks for an Anthropic API key in three
  places (environment variable, Streamlit secrets, sidebar input). If none is found,
  it shows setup instructions instead of crashing.
- **Context enrichment**: before each API call, the page fetches live price data,
  company info, and recent news for the selected ticker via `yfinance`. This context
  is injected into the prompt so Claude can give data-driven answers.

The prompt template is loaded from `flask-app/prompts/base_prompt.txt`, the same
one used by the Flask backend. See `warren.py` for the implementation.
""")

# ── API key check ──
api_key = get_api_key()

if not api_key:
    st.sidebar.markdown("### API Key")
    key_input = st.sidebar.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your key at console.anthropic.com",
    )
    if key_input:
        st.session_state["anthropic_api_key"] = key_input
        api_key = key_input
        st.rerun()

if not api_key:
    st.warning("No Anthropic API key detected. Warren needs Claude to think.")
    st.markdown("""
### Setup Instructions

**Option 1: Environment variable** (recommended for local dev)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
streamlit run app.py
```

**Option 2: Streamlit secrets** (recommended for deployment)

Create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

**Option 3: Sidebar input**

Enter your key in the sidebar field. It persists for the current session only.

Get your API key at [console.anthropic.com](https://console.anthropic.com/).
""")
    st.stop()

# ── Ticker context ──
tickers = get_all_tickers()
ticker_list = [t["ticker"] for t in tickers]

st.sidebar.markdown("### Chat Context")
selected_ticker = st.sidebar.selectbox(
    "Analyze Ticker",
    ticker_list,
    index=ticker_list.index("NVDA") if "NVDA" in ticker_list else 0,
)

price_data = get_price(selected_ticker)
company_info = get_company_info(selected_ticker)
news = get_news(selected_ticker)

st.sidebar.metric(
    selected_ticker,
    f"${price_data['price']:.2f}",
    f"{price_data['change_pct']:+.2f}%",
)
st.sidebar.caption(f"{company_info['sector']} | {company_info['industry']}")

if news:
    st.sidebar.markdown("**Recent News:**")
    for n in news[:3]:
        st.sidebar.caption(f"- {n['title']}")

# ── Chat interface ──
if "warren_history" not in st.session_state:
    st.session_state.warren_history = []
if "warren_ticker" not in st.session_state:
    st.session_state.warren_ticker = selected_ticker

if st.session_state.warren_ticker != selected_ticker:
    st.session_state.warren_history = []
    st.session_state.warren_ticker = selected_ticker

for msg in st.session_state.warren_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.warren_history:
    with st.chat_message("assistant"):
        st.markdown(
            f"I'm Warren, your investment advisor. I'm currently looking at "
            f"**{selected_ticker}** ({company_info['name']}). "
            f"Ask me about price outlook, fundamentals, or whether to buy or sell."
        )

prompt = st.chat_input(f"Ask Warren about {selected_ticker}...")

if prompt:
    st.session_state.warren_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Warren is thinking..."):
            response = chat(
                user_message=prompt,
                ticker=selected_ticker,
                ticker_info=company_info,
                ticker_news=news,
                history=st.session_state.warren_history[:-1],
                api_key=api_key,
            )
        st.markdown(response)

    st.session_state.warren_history.append({"role": "assistant", "content": response})
