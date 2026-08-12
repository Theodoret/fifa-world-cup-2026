"""
Shared filter functions for dashboard pages.
"""
import pandas as pd
import streamlit as st


def team_selector(teams_df: pd.DataFrame, key: str = "team") -> str:
    """Dropdown to select a team by name."""
    names = sorted(teams_df["team_name"].unique())
    return st.selectbox("Select Team", names, key=key)


def stage_selector(stages_df: pd.DataFrame, key: str = "stage") -> str:
    """Dropdown to select a tournament stage."""
    names = stages_df["stage_name"].unique().tolist()
    return st.selectbox("Select Stage", ["All"] + names, key=key)


def group_selector(teams_df: pd.DataFrame, key: str = "group") -> str:
    """Dropdown to select a group letter."""
    groups = sorted(teams_df["group_letter"].dropna().unique())
    return st.selectbox("Select Group", ["All"] + groups, key=key)


def confederation_selector(teams_df: pd.DataFrame, key: str = "confed") -> str:
    """Dropdown to select a confederation."""
    confeds = sorted(teams_df["confederation"].dropna().unique())
    return st.selectbox("Select Confederation", ["All"] + confeds, key=key)