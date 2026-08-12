"""
Global filters (work_plan.txt GLOBAL FILTERS section).
Applied across the dashboard via the sidebar. Filters include stage, match,
team, player, continent, position, venue, referee, temperature, elevation,
humidity. Temperature/humidity are not present in the dataset and are shown
as disabled placeholders.
"""
import pandas as pd
import streamlit as st
from utils.loader import (load_matches, load_teams, load_tournament_stages,
                          load_venues, load_referees, load_player_stats)


def render_global_filters():
    """
    Render the global filter widget set in the sidebar.
    Returns a dict of active filter selections.
    """
    with st.sidebar:
        st.markdown("## 🌍 Global Filters")
        filters = {"stage": "All", "team": "All", "continent": "All",
                   "position": "All", "venue": "All", "referee": "All",
                   "temperature": "All", "elevation": "All", "humidity": "All"}

        stages = load_tournament_stages()["stage_name"].unique().tolist()
        filters["stage"] = st.selectbox("Stage", ["All"] + stages, key="gf_stage")

        teams = load_teams()
        filters["team"] = st.selectbox("Team", ["All"] + sorted(teams["team_name"].unique()),
                                       key="gf_team")
        filters["continent"] = st.selectbox(
            "Continent", ["All"] + sorted(teams["confederation"].dropna().unique()),
            key="gf_continent")

        positions = ["GK", "DEF", "MID", "FWD"]
        filters["position"] = st.selectbox("Position", ["All"] + positions, key="gf_position")

        filters["venue"] = st.selectbox(
            "Venue", ["All"] + sorted(load_venues()["stadium_name"].unique()),
            key="gf_venue")
        filters["referee"] = st.selectbox(
            "Referee", ["All"] + sorted(load_referees()["name"].unique()),
            key="gf_referee")

        # Temperature / humidity are not available in the dataset.
        filters["temperature"] = st.selectbox("Temperature", ["All"],
                                              disabled=True, key="gf_temp")
        filters["humidity"] = st.selectbox("Humidity", ["All"],
                                           disabled=True, key="gf_humidity")
        filters["elevation"] = st.selectbox(
            "Elevation", ["All", "Low (<300m)", "Mid (300-1000m)", "High (1000m+)"],
            key="gf_elev")

        st.caption("Temperature & humidity are not present in the raw dataset; "
                   "they are shown as placeholders (work_plan GLOBAL FILTERS).")
    return filters


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply commonly supported filters to a dataframe that has the matching
    columns. Unknown filter targets are ignored gracefully.
    """
    result = df.copy()
    mapping = {
        "stage": "stage_name",
        "team": "team_name",
        "continent": "confederation",
        "position": "position",
        "venue": "stadium_name",
    }
    for key, col in mapping.items():
        val = filters.get(key)
        if val and val != "All" and col in result.columns:
            result = result[result[col] == val]
    return result