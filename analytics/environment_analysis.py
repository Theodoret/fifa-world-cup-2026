"""
Environmental analysis — venue, stadium, and weather-related factors.
"""
import pandas as pd
import numpy as np


def venue_summary(venues: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize matches per venue with goals scored.
    """
    # Merge venue info with match results
    match_venue = matches.merge(venues, left_on="venue_id", right_on="venue_id", how="left")
    summary = match_venue.groupby(["stadium_name", "city", "country"]).agg(
        matches_played=("match_id", "count"),
        total_goals=("home_score", lambda x: x.sum() + matches.loc[x.index, "away_score"].sum()),
    ).reset_index()
    return summary


def elevation_analysis(venues: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze match outcomes by venue elevation.
    """
    match_venue = matches.merge(venues, on="venue_id", how="left")
    match_venue["total_goals"] = match_venue["home_score"] + match_venue["away_score"]
    agg = match_venue.groupby(pd.cut(match_venue["elevation_meters"], bins=5)).agg(
        matches=("match_id", "count"),
        avg_goals=("total_goals", "mean"),
        avg_home_score=("home_score", "mean"),
        avg_away_score=("away_score", "mean"),
        avg_elevation=("elevation_meters", "mean")
    ).reset_index()
    return agg

def estimated_air_pressure(elevation_m: float) -> float:
    """
    Estimate air pressure (hPa) from elevation using the ISA standard atmosphere.

    Formula: P = P0 * (1 - 0.0065*h / 288.15) ** 5.255, P0 = 1013.25 hPa.
    ESTIMATE — no temperature/humidity/weather data available.
    """
    if elevation_m is None or np.isnan(elevation_m):
        return np.nan
    p0 = 1013.25  # hPa
    return p0 * (1 - 0.0065 * elevation_m / 288.15) ** 5.255


def estimated_oxygen_availability(elevation_m: float) -> float:
    """
    Estimate oxygen availability as % of sea level from elevation.

    Formula: O2 = 20.9% * (P / P0), where P is estimated pressure.
    ESTIMATE — assumes constant oxygen fraction; scales with pressure.
    """
    pressure = estimated_air_pressure(elevation_m)
    if np.isnan(pressure):
        return np.nan
    return 20.9 * (pressure / 1013.25)


def venue_environment(venues: pd.DataFrame) -> pd.DataFrame:
    """
    Add estimated pressure and oxygen columns to the venues table.
    """
    df = venues.copy()
    df["estimated_pressure_hpa"] = df["elevation_meters"].apply(estimated_air_pressure)
    df["estimated_oxygen_pct"] = df["elevation_meters"].apply(estimated_oxygen_availability)
    return df


def climate_analysis(venues: pd.DataFrame, matches: pd.DataFrame,
                     team_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze relationships between venue elevation/pressure/oxygen and
    match metrics (possession, shots, goals).

    NOTE: Correlation only — work_plan.txt instructs NOT to claim causation.
    """
    env = venue_environment(venues)
    match_venue = matches.merge(env, on="venue_id", how="left")
    stat = team_stats.copy()
    merged = stat.merge(match_venue[["match_id", "venue_id", "elevation_meters",
                                     "estimated_pressure_hpa", "estimated_oxygen_pct"]],
                        on="match_id", how="left")
    # Aggregate per venue
    agg = merged.groupby("venue_id").agg(
        avg_elevation=("elevation_meters", "mean"),
        avg_pressure=("estimated_pressure_hpa", "mean"),
        avg_oxygen=("estimated_oxygen_pct", "mean"),
        avg_possession=("possession_pct", "mean"),
        avg_shots=("total_shots", "mean"),
        matches=("match_id", "count"),
    ).reset_index()
    agg = agg.merge(env[["venue_id", "stadium_name", "city"]], on="venue_id", how="left")
    return agg


def venue_climate_profile(venues: pd.DataFrame) -> pd.DataFrame:
    """
    Simple climate classification per venue based on elevation.
    (Temperature/humidity data are not available; classification is by elevation.)
    """
    env = venue_environment(venues)
    def classify(elev):
        if elev is None or np.isnan(elev):
            return "Unknown"
        if elev < 300:
            return "Lowland"
        if elev < 1000:
            return "Mid-altitude"
        if elev < 2000:
            return "High-altitude"
        return "Very high-altitude"
    env["climate_class"] = env["elevation_meters"].apply(classify)
    return env
