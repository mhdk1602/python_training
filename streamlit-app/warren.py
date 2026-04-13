"""
Ask Warren: Anthropic Claude chat wrapper.

Reuses the same prompt structure from flask-app/prompts/base_prompt.txt,
enriching it with live yfinance context before each call.
"""

import os
import json
from pathlib import Path
from typing import Generator

PROMPT_PATH = Path(__file__).resolve().parent.parent / "flask-app" / "prompts" / "base_prompt.txt"

SYSTEM_PROMPT = """You are Warren, an investment portfolio assistant modeled after value-investing \
principles. You provide concise, data-driven investment analysis.

Rules:
- Keep responses under 200 words unless the user asks for detail.
- Cite specific numbers from the provided context (price, market cap, P/E, news headlines).
- When predicting price movement, state your confidence level and reasoning.
- If you lack sufficient data, say so honestly rather than guessing.
- Never recommend specific dollar amounts to invest. Frame advice as considerations."""


def _load_base_prompt() -> str:
    """Load the XML prompt template from the Flask app's prompts directory."""
    try:
        return PROMPT_PATH.read_text()
    except FileNotFoundError:
        return ""


def _build_context(ticker: str, ticker_info: dict, ticker_news: list[dict]) -> str:
    """Format ticker data into the prompt template's expected variables."""
    base = _load_base_prompt()

    news_text = "\n".join(
        f"- {n.get('title', 'No title')}" for n in ticker_news
    ) or "No recent news available."

    info_text = json.dumps(
        {k: v for k, v in ticker_info.items() if k != "description"},
        indent=2, default=str,
    )

    if base:
        filled = base.replace("{ticker}", ticker)
        filled = filled.replace("{ticker_news}", news_text)
        filled = filled.replace("{ticker_info}", info_text)
        filled = filled.replace("{user_question}", "{{user_question}}")
        return filled

    return f"Ticker: {ticker}\n\nInfo:\n{info_text}\n\nRecent News:\n{news_text}"


def get_api_key() -> str | None:
    """Check environment, then Streamlit secrets, then session state."""
    import streamlit as st
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return st.session_state.get("anthropic_api_key")


def chat(
    user_message: str,
    ticker: str,
    ticker_info: dict,
    ticker_news: list[dict],
    history: list[dict],
    api_key: str | None = None,
) -> str:
    """
    Send a message to Claude with full ticker context.
    Returns the assistant's response text.
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        return "The `anthropic` package is not installed. Run `pip install anthropic`."

    key = api_key or get_api_key()
    if not key:
        return "No API key found. Set ANTHROPIC_API_KEY or enter it in the sidebar."

    context = _build_context(ticker, ticker_info, ticker_news)

    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    final_question = f"Context:\n{context}\n\nUser question: {user_message}"
    messages.append({"role": "user", "content": final_question})

    try:
        client = Anthropic(api_key=key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        return f"Error calling Claude: {e}"
