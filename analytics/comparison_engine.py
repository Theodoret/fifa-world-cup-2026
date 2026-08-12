"""
Comparison engine — head-to-head team and player comparisons.
"""
import pandas as pd
import numpy as np


def compare_two_teams(team1_id: int, team2_id: int, matches: pd.DataFrame,
                       team_stats: pd.DataFrame, teams: pd.DataFrame) -> dict:
    """
    Compare two teams side by side.

    Returns a dict with two keys: 'team1' and 'team2', each containing
    aggregate metrics.
    """
    from analytics.team_analysis import team_aggregate
    t1 = team_aggregate(team1_id, matches, team_stats)
    t2 = team_aggregate(team2_id, matches, team_stats)
    t1_name = teams.loc[teams["team_id"] == team1_id, "team_name"].values
    t2_name = teams.loc[teams["team_id"] == team2_id, "team_name"].values
    t1["team_name"] = t1_name[0] if len(t1_name) > 0 else f"Team {team1_id}"
    t2["team_name"] = t2_name[0] if len(t2_name) > 0 else f"Team {team2_id}"
    return {"team1": t1, "team2": t2}


def compare_two_players(player1_id: int, player2_id: int,
                         player_stats: pd.DataFrame, teams: pd.DataFrame) -> dict:
    """
    Compare two players side by side.
    """
    from analytics.player_analysis import player_summary
    summary = player_summary(player_stats, teams)
    p1 = summary[summary["player_id"] == player1_id]
    p2 = summary[summary["player_id"] == player2_id]
    return {"player1": p1.to_dict("records")[0] if not p1.empty else {},
            "player2": p2.to_dict("records")[0] if not p2.empty else {}}