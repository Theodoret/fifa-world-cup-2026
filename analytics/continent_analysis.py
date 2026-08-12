"""
Continent/confederation-level analytics.
"""
import pandas as pd
import numpy as np


def continent_summary(teams: pd.DataFrame, matches: pd.DataFrame,
                       team_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate stats by confederation.
    """
    from analytics.team_analysis import all_teams_summary
    team_summary = all_teams_summary(matches, team_stats, teams)
    if team_summary.empty:
        return pd.DataFrame()

    grouped = team_summary.groupby("confederation").agg(
        teams=("team_name", "count"),
        total_matches=("matches_played", "sum"),
        total_wins=("wins", "sum"),
        total_points=("points", "sum"),
        total_goals_for=("goals_for", "sum"),
        total_goals_against=("goals_against", "sum"),
        avg_possession=("avg_possession", "mean"),
        avg_shots=("avg_shots", "mean"),
    ).reset_index()
    grouped["goal_difference"] = grouped["total_goals_for"] - grouped["total_goals_against"]
    grouped["win_rate"] = round(grouped["total_wins"] / grouped["total_matches"] * 100, 1)
    return grouped


def continent_best_performers(teams: pd.DataFrame, matches: pd.DataFrame,
                                team_stats: pd.DataFrame, confederation: str) -> pd.DataFrame:
    """Return best-performing teams within a confederation."""
    from analytics.team_analysis import all_teams_summary
    team_summary = all_teams_summary(matches, team_stats, teams)
    if team_summary.empty:
        return pd.DataFrame()
    subset = team_summary[team_summary["confederation"] == confederation]
    return subset.sort_values("points", ascending=False)