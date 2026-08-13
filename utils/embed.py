"""Embed raw HTML in an iframe (bracket, scoreboard, etc.)."""
from __future__ import annotations

import streamlit as st


def embed_html(html: str, *, height: int) -> None:
    """Render an HTML document inside an iframe with a fixed height."""
    st.iframe(html, height=height, width="stretch")
