"""
Match analysis module.
"""
import pandas as pd
import numpy as np


def match_basic_stats(match: pd.Series, home_stats: pd.Series = None, away_stats: pd.Series = None) -> dict:
    """Return basic match statistics."""
    stats = {
        "score": f"{int(match['home_score'])}-{int(match['away_score'])}",
        "home_team": match.get("home_name", ""),
        "away_team": match.get("away_name", ""),
        "stage": match.get("stage_name", ""),
        "date": str(match.get("date", "")),
        "venue": match.get("stadium_name", ""),
    }
    if home_stats is not None and away_stats is not None:
        stats["home_possession"] = home_stats.get("possession_pct", None)
        stats["away_possession"] = away_stats.get("possession_pct", None)
        stats["home_shots"] = home_stats.get("total_shots", None)
        stats["away_shots"] = away_stats.get("total_shots", None)
        stats["home_sot"] = home_stats.get("shots_on_target", None)
        stats["away_sot"] = away_stats.get("shots_on_target", None)
        stats["home_passes"] = home_stats.get("passes", None)
        stats["away_passes"] = away_stats.get("passes", None)
        stats["home_pass_acc"] = home_stats.get("pass_accuracy_pct", None)
        stats["away_pass_acc"] = away_stats.get("pass_accuracy_pct", None)
        stats["home_fouls"] = home_stats.get("fouls", None)
        stats["away_fouls"] = away_stats.get("fouls", None)
        stats["home_yellow"] = home_stats.get("yellow_cards", None)
        stats["away_yellow"] = away_stats.get("yellow_cards", None)
        stats["home_red"] = home_stats.get("red_cards", None)
        stats["away_red"] = away_stats.get("red_cards", None)
        stats["home_offsides"] = home_stats.get("offsides", None)
        stats["away_offsides"] = away_stats.get("offsides", None)
        stats["home_corners"] = home_stats.get("corners", None)
        stats["away_corners"] = away_stats.get("corners", None)
        stats["home_saves"] = home_stats.get("saves", None)
        stats["away_saves"] = away_stats.get("saves", None)
    return stats


def momentum_intervals(match_stats_df: pd.DataFrame, interval_minutes: int = 15) -> pd.DataFrame:
    """
    Split match into intervals and calculate per-interval stats.
    Requires match event data with minute timestamps.
    """
    # Placeholder — requires event data with timestamps
    return pd.DataFrame()


def classify_playing_style(stats: dict) -> str:
    """
    Classify team playing style based on match statistics.
    Returns one of: Possession, Counter Attack, High Press, Direct Play, Defensive Block.
    """
    possession = stats.get("possession_pct", 50)
    passes = stats.get("passes", 0)
    fouls = stats.get("fouls", 0)
    shots = stats.get("total_shots", 0)

    if possession >= 60:
        return "Possession"
    if possession <= 40 and passes <= 300:
        return "Direct Play"
    if fouls >= 15:
        return "High Press"
    if shots <= 5 and possession <= 45:
        return "Defensive Block"
    return "Counter Attack"