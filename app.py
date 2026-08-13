"""
FIFA World Cup 2026 Analytics Dashboard
Main entry point — Streamlit navigation-based app with global filters sidebar.

Note: page scripts live in ``views/`` (not ``pages/``). Streamlit auto-discovers
a ``pages/`` folder and that conflicts with ``st.navigation``, causing blank
screens when switching pages.
"""
import streamlit as st
from config import APP_TITLE, APP_ICON, NAVIGATION, PAGE_ICONS
from utils.styles import apply_custom_css, render_theme_toggle

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")
apply_custom_css()


def _page_title(page: str) -> str:
    key = page.replace(".py", "")
    emoji = PAGE_ICONS.get(key, "")
    name = key.split("_", 1)[1].replace("_", " ") if "_" in key else key
    return f"{emoji} {name}" if emoji else name


pages = [
    st.Page(f"views/{page}", title=_page_title(page))
    for page in sorted(NAVIGATION)
]

# Register navigation before drawing widgets / running a page.
nav = st.navigation(pages, position="hidden")

# Sidebar must render before nav.run() — pages that call st.stop() would
# otherwise halt the script before these widgets are drawn.
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">⚽</div>
            <div class="sidebar-brand-title">FIFA World Cup 2026</div>
            <div class="sidebar-brand-sub">Analytics Dashboard</div>
        </div>
        <div class="sidebar-nav-label">Navigation</div>
        """,
        unsafe_allow_html=True,
    )
    for p in pages:
        # Empty query_params clears leftover drill-down state from other pages.
        st.page_link(p, width="stretch", query_params={})
    st.markdown("<div class='sidebar-footer'>", unsafe_allow_html=True)
    render_theme_toggle()
    st.markdown("</div>", unsafe_allow_html=True)

nav.run()
