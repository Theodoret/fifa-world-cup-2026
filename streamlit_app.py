"""
Streamlit Community Cloud entry point.

Must call the dashboard ``run()`` on every script rerun. A bare ``import app``
only executes module-level code once per process in some Cloud setups, so
``st.navigation`` never re-registers after a page switch — blank UI, no error.
"""
from app import run

run()
