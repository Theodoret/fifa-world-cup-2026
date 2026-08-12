"""
Advanced match metrics (work_plan.txt MATCH EXPLORER - Advanced).
Chance Creation, Finishing Efficiency, Defensive Efficiency, Goalkeeper
Efficiency, Match Momentum, Playing Style, Aggressiveness Index.
All composite metrics expose their methodology via utils/methodology.py.
"""
import pandas as pd
import numpy as np

from analytics.metrics import aggressiveness_index, shot_conversion_rate
from analytics.match_analysis import classify_playing_style


def chance_creation(stats: pd.DataFrame) -> pd.DataFrame:
    """
    Composite chance creation score per team per match.

    Requires match_team_stats rows with possession, shots, shots_on_target.
    """
    df = stats.copy()
    df["chance_creation_score"] = (
        df["shots_on_target"] * 1.0
        + df["total_shots"] * 0.5
        + (df["possession_pct"] / 10.0)
    )
    return df


def finishing_efficiency(stats: pd.DataFrame, xg: pd.Series = None) -> pd.DataFrame:
    """
    Finishing efficiency = goals vs shots and goals vs xG.

    `stats` must include total_shots and goals (merged from matches).
    `xg` is an optional Series of expected goals keyed by (match_id, team_id).
    """
    df = stats.copy()
    df["finishing_efficiency_pct"] = df.apply(
        lambda r: shot_conversion_rate(r.get("goals", 0), r.get("total_shots", 0)), axis=1)
    if xg is not None and "goals" in df.columns:
        df["over_performance"] = df["goals"] - df["xG"]
    return df


def defensive_efficiency(stats: pd.DataFrame, goals_conceded: pd.Series = None) -> pd.DataFrame:
    """
    Defensive efficiency composite using goals conceded and saves.

    Higher = worse (more conceded). Requires a goals_conceded series aligned
    to stats rows (opponent goals per match).
    """
    df = stats.copy()
    if goals_conceded is not None:
        df["goals_conceded"] = goals_conceded.values
        df["defensive_efficiency"] = df["goals_conceded"] - df["saves"] * 0.05
    else:
        df["defensive_efficiency"] = np.nan
    return df


def goalkeeper_efficiency(player_stats_row: pd.Series) -> float:
    """
    Goalkeeper efficiency from a player_stats row (GK only).

    Returns save ratio (saves / shots faced proxy) or NaN if unavailable.
    """
    goals_conceded = player_stats_row.get("goals_conceded", 0)
    saves = player_stats_row.get("saves", 0)
    total_faced = goals_conceded + saves
    if total_faced == 0:
        return np.nan
    return round(saves / total_faced, 3)


def match_momentum(events: pd.DataFrame, match_id: int, interval_minutes: int = 15) -> pd.DataFrame:
    """
    Compute per-interval event counts (momentum) for a match.

    Weighting: Goals=3, Cards=1, Others=1.
    """
    if events.empty:
        return pd.DataFrame()
    ev = events[events["match_id"] == match_id].copy()
    if ev.empty:
        return pd.DataFrame()

    def weight(event_type):
        t = str(event_type).lower()
        if "goal" in t:
            return 3.0
        if "card" in t:
            return 1.0
        return 1.0

    ev["weight"] = ev["event_type"].apply(weight)
    ev["minute"] = pd.to_numeric(ev["minute"], errors="coerce").fillna(0).astype(int)
    ev["interval"] = (ev["minute"] // interval_minutes) * interval_minutes
    agg = ev.groupby(["interval", "team_id"]).agg(
        momentum=("weight", "sum"),
        events=("event_id", "count"),
    ).reset_index()
    return agg


def aggr_index_summary(team_stats_per_match: pd.DataFrame, events: pd.DataFrame = None) -> pd.DataFrame:
    """
    Aggressiveness index per team (per-match averages of fouls, yellows, reds).

    Fouls come from match_team_stats. Yellow/red cards are counted from
    match_events when provided (match_team_stats has no card columns).
    """
    agg = team_stats_per_match.groupby("team_id").agg(
        avg_fouls=("fouls", "mean"),
        matches=("match_id", "count"),
    ).reset_index()
    agg["avg_yellow"] = 0.0
    agg["avg_red"] = 0.0

    if events is not None and not events.empty:
        cards = events[events["event_type"].isin(["Yellow Card", "Red Card"])].copy()
        cards["is_red"] = cards["event_type"].str.contains("Red")
        cards["is_yellow"] = cards["event_type"].str.contains("Yellow")
        card_agg = cards.groupby("team_id").agg(
            yellows=("is_yellow", "sum"),
            reds=("is_red", "sum"),
            card_matches=("match_id", "nunique"),
        ).reset_index()
        agg = agg.merge(card_agg[["team_id", "yellows", "reds"]], on="team_id", how="left")
        agg["avg_yellow"] = agg["yellows"].fillna(0) / agg["matches"].replace(0, 1)
        agg["avg_red"] = agg["reds"].fillna(0) / agg["matches"].replace(0, 1)

    agg["aggressiveness_index"] = agg.apply(
        lambda r: aggressiveness_index(r["avg_fouls"], r["avg_yellow"], r["avg_red"]), axis=1)
    # Min-max normalize to 0-100
    mn, mx = agg["aggressiveness_index"].min(), agg["aggressiveness_index"].max()
    agg["aggressiveness_index_norm"] = np.where(
        mx > mn, (agg["aggressiveness_index"] - mn) / (mx - mn) * 100, 50)
    return agg


def style_per_match(stats: pd.DataFrame) -> pd.DataFrame:
    """Assign a playing style label to each team-per-match row."""
    df = stats.copy()
    df["playing_style"] = df.apply(classify_playing_style, axis=1)
    return df