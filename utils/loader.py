"""
Data loading module with caching.
All raw CSV access goes through this module.
"""
import pandas as pd
import streamlit as st
from pathlib import Path
from config import RAW_DIR


@st.cache_data(ttl=3600, show_spinner="Loading data...")
def load_csv(filename: str, dtype_backend: str = "numpy_nullable") -> pd.DataFrame:
    """
    Load a raw CSV file with caching.

    Parameters
    ----------
    filename : str
        CSV filename (e.g. "matches.csv").
    dtype_backend : str
        Backend for pandas dtype inference.

    Returns
    -------
    pd.DataFrame

    Raises
    ------
    FileNotFoundError
        If the file does not exist in RAW_DIR.
    """
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found: {path}")
    return pd.read_csv(path, dtype_backend=dtype_backend)


# --- Convenience loaders ---

@st.cache_data(ttl=3600)
def load_matches() -> pd.DataFrame:
    return load_csv("matches.csv")


@st.cache_data(ttl=3600)
def load_teams() -> pd.DataFrame:
    return load_csv("teams.csv")


@st.cache_data(ttl=3600)
def load_match_team_stats() -> pd.DataFrame:
    return load_csv("match_team_stats.csv")


@st.cache_data(ttl=3600)
def load_player_stats() -> pd.DataFrame:
    return load_csv("player_stats.csv")


@st.cache_data(ttl=3600)
def load_tournament_stages() -> pd.DataFrame:
    return load_csv("tournament_stages.csv")


@st.cache_data(ttl=3600)
def load_venues() -> pd.DataFrame:
    return load_csv("venues.csv")


@st.cache_data(ttl=3600)
def load_referees() -> pd.DataFrame:
    return load_csv("referees.csv")


@st.cache_data(ttl=3600)
def load_squads_and_players() -> pd.DataFrame:
    return load_csv("squads_and_players.csv")


@st.cache_data(ttl=3600)
def load_matches_detailed() -> pd.DataFrame:
    return load_csv("matches_detailed.csv")


@st.cache_data(ttl=3600)
def load_match_events() -> pd.DataFrame:
    return load_csv("match_events.csv")


@st.cache_data(ttl=3600)
def load_match_lineups() -> pd.DataFrame:
    return load_csv("match_lineups.csv")


@st.cache_data(ttl=3600)
def load_prediction_features() -> pd.DataFrame:
    return load_csv("match_prediction_features.csv")