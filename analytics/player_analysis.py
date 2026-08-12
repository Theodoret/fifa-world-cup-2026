"""
Player-level analytics.
All per-match metrics are normalized to per-90-minute or per-game averages.
"""
import pandas as pd
import numpy as np
from analytics.metrics import goal_per90, assist_per90, shot_conversion_rate


def player_summary(player_stats: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """
    Build a summary DataFrame with per-90 metrics for all players.
    """
    df = player_stats.copy()
    df["goals_per90"] = df.apply(lambda r: goal_per90(r["goals"], r["minutes_played"]), axis=1)
    df["assists_per90"] = df.apply(lambda r: assist_per90(r["assists"], r["minutes_played"]), axis=1)
    df["goal_contrib_per90"] = df["goals_per90"] + df["assists_per90"]
    df["shot_conversion_pct"] = df.apply(
        lambda r: shot_conversion_rate(r["goals"], r["shots_on_target"]), axis=1)
    # Goal involvement per match
    df["goal_involvement_per_match"] = (df["goals"] + df["assists"]) / df["matches_played"].replace(0, 1)
    df = df.merge(teams[["team_id", "team_name", "fifa_code"]], on="team_id", how="left")
    return df


def top_players(player_stats: pd.DataFrame, teams: pd.DataFrame,
                metric: str = "goals", n: int = 10) -> pd.DataFrame:
    """
    Return top N players by a given metric.
    """
    df = player_summary(player_stats, teams)
    if metric not in df.columns:
        return df.head(0)
    return df.nlargest(n, metric)


def position_breakdown(player_stats: pd.DataFrame) -> pd.DataFrame:
    """Aggregate stats by position."""
    df = player_stats.groupby("position").agg(
        count=("player_id", "count"),
        total_goals=("goals", "sum"),
        total_assists=("assists", "sum"),
        avg_rating=("average_rating", "mean"),
        avg_minutes=("minutes_played", "mean")
    ).reset_index()
    return df

def player_vs_position_average(player_stats: pd.DataFrame, teams: pd.DataFrame,
                               player_id: int) -> dict:
    """
    Compare a player against the average of their position.
    Returns dict with player and position-average metrics.
    """
    row = player_stats[player_stats["player_id"] == player_id]
    if row.empty:
        return {}
    pos = row["position"].values[0]
    pos_df = player_stats[player_stats["position"] == pos]
    return {
        "player": player_summary(row, teams).iloc[0].to_dict(),
        "position": pos,
        "position_avg": {
            "goals_per90": round(pos_df["goals"].sum() / pos_df["minutes_played"].replace(0, 1).sum() * 90, 2)
            if pos_df["minutes_played"].sum() else 0,
            "assists_per90": round(pos_df["assists"].sum() / pos_df["minutes_played"].replace(0, 1).sum() * 90, 2)
            if pos_df["minutes_played"].sum() else 0,
            "avg_rating": round(pos_df["average_rating"].mean(), 2) if not pos_df["average_rating"].isna().all() else 0,
        },
    }


def player_vs_team_average(player_stats: pd.DataFrame, teams: pd.DataFrame,
                           player_id: int) -> dict:
    """
    Compare a player against their own team's average.
    """
    row = player_stats[player_stats["player_id"] == player_id]
    if row.empty:
        return {}
    team_id = row["team_id"].values[0]
    team_df = player_stats[player_stats["team_id"] == team_id]
    return {
        "player": player_summary(row, teams).iloc[0].to_dict(),
        "team_avg": {
            "goals_per90": round(team_df["goals"].sum() / team_df["minutes_played"].replace(0, 1).sum() * 90, 2)
            if team_df["minutes_played"].sum() else 0,
            "assists_per90": round(team_df["assists"].sum() / team_df["minutes_played"].replace(0, 1).sum() * 90, 2)
            if team_df["minutes_played"].sum() else 0,
            "avg_rating": round(team_df["average_rating"].mean(), 2) if not team_df["average_rating"].isna().all() else 0,
        },
    }


def player_vs_tournament_average(player_stats: pd.DataFrame, teams: pd.DataFrame,
                                 player_id: int) -> dict:
    """
    Compare a player against the tournament-wide average.
    """
    row = player_stats[player_stats["player_id"] == player_id]
    if row.empty:
        return {}
    non_zero = player_stats[player_stats["minutes_played"] > 0]
    return {
        "player": player_summary(row, teams).iloc[0].to_dict(),
        "tournament_avg": {
            "goals_per90": round(non_zero["goals"].sum() / non_zero["minutes_played"].sum() * 90, 2)
            if non_zero["minutes_played"].sum() else 0,
            "assists_per90": round(non_zero["assists"].sum() / non_zero["minutes_played"].sum() * 90, 2)
            if non_zero["minutes_played"].sum() else 0,
            "avg_rating": round(non_zero["average_rating"].mean(), 2) if not non_zero["average_rating"].isna().all() else 0,
        },
    }
