"""
Data preprocessing and cleaning pipeline.
"""
import pandas as pd
import numpy as np
from config import RANDOM_SEED


def clean_matches(df: pd.DataFrame) -> pd.DataFrame:
    """Clean matches dataframe: fill missing scores, ensure types."""
    df = df.copy()
    df["home_score"] = pd.to_numeric(df["home_score"], errors="coerce").fillna(0).astype(int)
    df["away_score"] = pd.to_numeric(df["away_score"], errors="coerce").fillna(0).astype(int)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def clean_team_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Clean match_team_stats: fill missing numeric columns."""
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    return df


def clean_player_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Clean player_stats: fill missing values."""
    df = df.copy()
    df["minutes_played"] = pd.to_numeric(df["minutes_played"], errors="coerce").fillna(0).astype(int)
    df["goals"] = pd.to_numeric(df["goals"], errors="coerce").fillna(0).astype(int)
    df["assists"] = pd.to_numeric(df["assists"], errors="coerce").fillna(0).astype(int)
    return df


def merge_match_with_teams(matches: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """Merge matches with team names for home and away."""
    home = teams[["team_id", "team_name", "fifa_code", "group_letter", "confederation"]].rename(
        columns={"team_name": "home_name", "fifa_code": "home_fifa_code",
                 "group_letter": "home_group", "confederation": "home_confederation"}
    )
    away = teams[["team_id", "team_name", "fifa_code", "group_letter", "confederation"]].rename(
        columns={"team_name": "away_name", "fifa_code": "away_fifa_code",
                 "group_letter": "away_group", "confederation": "away_confederation"}
    )
    df = matches.merge(home, left_on="home_team_id", right_on="team_id", how="left")
    df = df.merge(away, left_on="away_team_id", right_on="team_id", how="left", suffixes=("_home", "_away"))
    return df


def merge_match_with_stages(matches: pd.DataFrame, stages: pd.DataFrame) -> pd.DataFrame:
    """Merge matches with tournament stage names."""
    return matches.merge(stages, left_on="stage_id", right_on="stage_id", how="left")