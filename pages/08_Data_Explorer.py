"""
Page 8: Data Explorer
"""
import streamlit as st
import pandas as pd

from utils.loader import (
    load_matches, load_teams, load_match_team_stats, load_player_stats,
    load_tournament_stages, load_venues, load_referees, load_squads_and_players,
    load_matches_detailed, load_match_events, load_match_lineups, load_prediction_features
)
from utils.styles import apply_custom_css
from utils.state import render_breadcrumbs
st.set_page_config(page_title="Data Explorer", page_icon="🔍", layout="wide")
apply_custom_css()
render_breadcrumbs("Data Explorer")

st.markdown("<h1 class='main-header'>🔍 Data Explorer</h1>", unsafe_allow_html=True)

datasets = {
    "matches": load_matches, "teams": load_teams, "match_team_stats": load_match_team_stats,
    "player_stats": load_player_stats, "tournament_stages": load_tournament_stages,
    "venues": load_venues, "referees": load_referees, "squads_and_players": load_squads_and_players,
    "matches_detailed": load_matches_detailed, "match_events": load_match_events,
    "match_lineups": load_match_lineups, "match_prediction_features": load_prediction_features,
}

selected = st.selectbox("Select Dataset", sorted(datasets.keys()))
try:
    df = datasets[selected]()
    st.success(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Rows", len(df))
    with c2: st.metric("Columns", len(df.columns))
    with c3: st.metric("Missing Cells", df.isna().sum().sum())
    with c4: st.metric("Duplicate PK", len(df[df.duplicated()]) if not df.empty else 0)

    st.subheader("Preview")
    st.dataframe(df.head(100), width="stretch")

    st.subheader("Data Types")
    dtypes = df.dtypes.astype(str).reset_index()
    dtypes.columns = ["Column", "Type"]
    st.dataframe(dtypes, hide_index=True, width="stretch")

    st.subheader("Summary Statistics")
    st.dataframe(df.describe(include="all").transpose(), width="stretch")

    st.subheader("Missing Values")
    missing = df.isna().sum().reset_index()
    missing.columns = ["Column", "Missing"]
    missing = missing[missing["Missing"] > 0].sort_values("Missing", ascending=False)
    if not missing.empty:
        st.dataframe(missing, hide_index=True, width="stretch")
    else:
        st.info("No missing values.")
except Exception as e:
    st.error(f"Error loading dataset: {e}")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: var(--text-muted); font-size: 0.85rem;'>"
    "📦 Data source: "
    "<a href='https://github.com/mominullptr/FIFA-World-Cup-2026-Dataset' "
    "target='_blank' style='color: var(--accent);'>"
    "FIFA-World-Cup-2026-Dataset</a></div>",
    unsafe_allow_html=True)
