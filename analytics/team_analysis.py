"""
Team-level analytics.
Per-match averages are used for fair comparison across teams that
played different numbers of matches.
"""
import pandas as pd
import numpy as np
from analytics.metrics import shot_conversion_rate, goal_per90


def team_performance(team_id: int, matches: pd.DataFrame, team_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate per-match performance for a team.

    Returns a DataFrame with one row per match containing the team's stats.
    `matches` must have home_team_id/away_team_id and home_score/away_score.
    `team_stats` is match_team_stats (one row per team per match).
    """
    stats = team_stats[team_stats["team_id"] == team_id].copy()
    stats = stats.merge(matches[["match_id", "home_team_id", "away_team_id",
                                 "home_score", "away_score"]], on="match_id", how="left")
    # Determine if team was home or away
    is_home = stats["home_team_id"] == team_id
    stats["is_home"] = is_home
    stats["team_goals"] = np.where(is_home, stats["home_score"], stats["away_score"])
    stats["opponent_goals"] = np.where(is_home, stats["away_score"], stats["home_score"])
    stats["result"] = np.where(stats["team_goals"] > stats["opponent_goals"], "W",
                    np.where(stats["team_goals"] < stats["opponent_goals"], "L", "D"))
    return stats


def team_aggregate(team_id: int, matches: pd.DataFrame, team_stats: pd.DataFrame) -> dict:
    """Summarize a team's whole tournament into a dictionary of metrics."""
    perf = team_performance(team_id, matches, team_stats)
    if perf.empty:
        return {"team_id": team_id, "matches_played": 0}

    n = len(perf)
    agg = {
        "team_id": team_id,
        "matches_played": n,
        "wins": int((perf["result"] == "W").sum()),
        "draws": int((perf["result"] == "D").sum()),
        "losses": int((perf["result"] == "L").sum()),
        "goals_for": int(perf["team_goals"].sum()),
        "goals_against": int(perf["opponent_goals"].sum()),
        "goal_difference": int(perf["team_goals"].sum() - perf["opponent_goals"].sum()),
        "avg_possession": round(perf["possession_pct"].mean(), 1),
        "avg_shots": round(perf["total_shots"].mean(), 1),
        "avg_shots_on_target": round(perf["shots_on_target"].mean(), 1),
        "avg_corners": round(perf["corners"].mean(), 1),
        "avg_fouls": round(perf["fouls"].mean(), 1),
        "avg_offsides": round(perf["offsides"].mean(), 1),
        "avg_saves": round(perf["saves"].mean(), 1),
        "goals_per_match": round(perf["team_goals"].mean(), 2),
        "goals_conceded_per_match": round(perf["opponent_goals"].mean(), 2),
        "points": int((perf["result"] == "W").sum() * 3 + (perf["result"] == "D").sum()),
    }
    return agg


def all_teams_summary(matches: pd.DataFrame, team_stats: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """Build a summary table for every team in the tournament."""
    rows = []
    for team_id in team_stats["team_id"].unique():
        agg = team_aggregate(team_id, matches, team_stats)
        if agg.get("matches_played", 0) == 0:
            continue
        rows.append(agg)
    summary = pd.DataFrame(rows)
    if not summary.empty:
        summary = summary.merge(teams[["team_id", "team_name", "fifa_code",
                                       "group_letter", "confederation"]],
                                on="team_id", how="left")
        # Shot conversion rate at aggregate level
        summary["shot_conversion_pct"] = summary.apply(
            lambda r: shot_conversion_rate(r["goals_for"], r["avg_shots_on_target"] * r["matches_played"]),
            axis=1)
    return summary

def team_radar_data(team_id: int, matches: pd.DataFrame, team_stats: pd.DataFrame,
                    teams: pd.DataFrame) -> dict:
    """
    Build radar chart data for a team vs tournament average.
    Returns dict with keys: team (name), categories, team_values, tournament_values.
    Values are per-match averages or percentages, normalized to a common 0-100 showcase scale.
    """
    tm = teams[teams["team_id"] == team_id]
    if tm.empty:
        return {}
    team_name = tm["team_name"].values[0]

    agg = team_aggregate(team_id, matches, team_stats)
    summary = all_teams_summary(matches, team_stats, teams)
    if agg.get("matches_played", 0) == 0 or summary.empty:
        return {}

    categories = ["Possession", "Shots", "Shots on Target",
                  "Goals per Match", "Goal Difference", "Defensive (lower=better)"]
    # Team raw values
    team_raw = {
        "Possession": agg["avg_possession"],
        "Shots": agg["avg_shots"],
        "Shots on Target": agg["avg_shots_on_target"],
        "Goals per Match": agg["goals_per_match"],
        "Goal Difference": agg["goal_difference"],
        "Goals Conceded per Match": agg["goals_conceded_per_match"],
    }
    # Tournament raw values (averaged across all teams)
    avg_raw = {
        "Possession": summary["avg_possession"].mean(),
        "Shots": summary["avg_shots"].mean(),
        "Shots on Target": summary["avg_shots_on_target"].mean(),
        "Goals per Match": summary["goals_per_match"].mean(),
        "Goal Difference": summary["goal_difference"].mean(),
        "Goals Conceded per Match": summary["goals_conceded_per_match"].mean(),
    }
    def norm(value, col, invert=False):
        lo = summary[col].min()
        hi = summary[col].max()
        if hi <= lo:
            return 50.0
        scaled = (value - lo) / (hi - lo) * 100
        return 100 - scaled if invert else scaled

    team_values = [
        norm(team_raw["Possession"], "avg_possession"),
        norm(team_raw["Shots"], "avg_shots"),
        norm(team_raw["Shots on Target"], "avg_shots_on_target"),
        norm(team_raw["Goals per Match"], "goals_per_match"),
        norm(team_raw["Goal Difference"], "goal_difference"),
        norm(team_raw["Goals Conceded per Match"], "goals_conceded_per_match", invert=True),
    ]
    tournament_values = [
        norm(avg_raw["Possession"], "avg_possession"),
        norm(avg_raw["Shots"], "avg_shots"),
        norm(avg_raw["Shots on Target"], "avg_shots_on_target"),
        norm(avg_raw["Goals per Match"], "goals_per_match"),
        norm(avg_raw["Goal Difference"], "goal_difference"),
        norm(avg_raw["Goals Conceded per Match"], "goals_conceded_per_match", invert=True),
    ]
    return {
        "team": team_name,
        "categories": categories,
        "team_values": team_values,
        "tournament_values": tournament_values,
        "team_raw": team_raw,
        "tournament_raw": avg_raw,
    }


def rolling_team_trend(team_id: int, matches: pd.DataFrame, team_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Rolling (per-match cumulative) trend for a team: goals, xG, shots.
    Returns a DataFrame with one row per match in chronological order.
    """
    perf = team_performance(team_id, matches, team_stats)
    if perf.empty:
        return pd.DataFrame()
    perf = perf.sort_values("match_id").reset_index(drop=True)
    # Merge xG from matches
    xg = matches[["match_id", "home_team_id", "home_xg", "away_xg"]].copy()
    perf = perf.merge(xg, on="match_id", how="left")
    perf["team_xg"] = perf.apply(
        lambda r: r["home_xg"] if r["is_home"] else r["away_xg"], axis=1)
    perf["cum_goals"] = perf["team_goals"].cumsum()
    perf["cum_xg"] = perf["team_xg"].fillna(0).cumsum()
    perf["cum_shots"] = perf["total_shots"].cumsum()
    perf["match_number"] = perf.index + 1
    return perf[["match_number", "team_goals", "team_xg", "total_shots",
                 "opponent_goals", "cum_goals", "cum_xg", "cum_shots"]]
