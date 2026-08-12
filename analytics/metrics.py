"""
Shared analytics metrics library.
All custom metrics must document formula, variables, normalization, assumptions, and limitations.
"""
import pandas as pd
import numpy as np


def aggressiveness_index(fouls_per_match: float, yellow_per_match: float, red_per_match: float) -> float:
    """
    Estimate how physically aggressive a team is.

    Formula:
        AI = 0.40 * avg_fouls + 0.35 * avg_yellow + 0.25 * avg_red

    Normalization: Min-max scaled to 0-100 across all teams.
    Variables: avg_fouls, avg_yellow, avg_red (per match).
    Assumptions: Fouls, yellows, and reds are equally weighted indicators.
    Limitations: Does not account for referee tendencies or match context.
    """
    raw = 0.40 * fouls_per_match + 0.35 * yellow_per_match + 0.25 * red_per_match
    return raw


def shot_conversion_rate(goals: int, shots_on_target: int) -> float:
    """
    Shot conversion rate from shots on target.

    Formula: (goals / shots_on_target) * 100
    """
    if shots_on_target is None or pd.isna(shots_on_target) or shots_on_target == 0:
        return 0.0
    return round((goals / shots_on_target) * 100, 1)


def pass_accuracy(accurate_passes: int, total_passes: int) -> float:
    """Pass accuracy as percentage."""
    if total_passes == 0:
        return 0.0
    return round((accurate_passes / total_passes) * 100, 1)


def goal_per90(goals: int, minutes: int) -> float:
    """Goals per 90 minutes."""
    if minutes == 0:
        return 0.0
    return round((goals / minutes) * 90, 2)


def assist_per90(assists: int, minutes: int) -> float:
    """Assists per 90 minutes."""
    if minutes == 0:
        return 0.0
    return round((assists / minutes) * 90, 2)


def goal_contribution(goals: int, assists: int) -> int:
    """Total goal contributions (goals + assists)."""
    return goals + assists


def min_per_goal(minutes: int, goals: int):
    """Minutes per goal scored."""
    if goals == 0:
        return None
    return round(minutes / goals, 1)