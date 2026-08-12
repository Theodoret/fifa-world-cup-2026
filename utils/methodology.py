"""
Methodology transparency renderer.

Every custom metric shown in the dashboard can expose its formula, variables,
weighting, normalization, assumptions and limitations (work_plan.txt CORE
PRINCIPLES: Transparency).
"""
import streamlit as st

# Registry of metric methodology documentation.
# Each entry: metric_name -> dict with keys formula, variables, weighting,
# normalization, assumptions, limitations, unit.
METHODOLOGY = {
    "aggressiveness_index": {
        "formula": "AI = 0.40 * avg_fouls_per_match + 0.35 * avg_yellow_per_match + 0.25 * avg_red_per_match",
        "variables": ["avg_fouls_per_match", "avg_yellow_per_match", "avg_red_per_match"],
        "weighting": "Fouls 0.40, Yellows 0.35, Reds 0.25",
        "normalization": "Raw score; min-max scaled to 0-100 across teams in the summary view.",
        "assumptions": "Fouls, yellows and reds are equally meaningful indicators of physical aggression.",
        "limitations": "Ignores referee tendencies, match context and simulation.",
        "unit": "Index (0-100 in summary)",
    },
    "shot_conversion_rate": {
        "formula": "SCR = (goals / shots_on_target) * 100",
        "variables": ["goals", "shots_on_target"],
        "weighting": "None",
        "normalization": "Percentage",
        "assumptions": "Shots on target are the relevant denominator.",
        "limitations": "Does not account for shot quality or xG.",
        "unit": "%",
    },
    "pass_accuracy": {
        "formula": "PA = (accurate_passes / total_passes) * 100",
        "variables": ["accurate_passes", "total_passes"],
        "weighting": "None",
        "normalization": "Percentage",
        "assumptions": "All passes carry equal weight.",
        "limitations": "Ignores pass difficulty and direction.",
        "unit": "%",
    },
    "goals_per90": {
        "formula": "g90 = (goals / minutes_played) * 90",
        "variables": ["goals", "minutes_played"],
        "weighting": "None",
        "normalization": "Per 90 minutes",
        "assumptions": "Uniform scoring rate across minutes.",
        "limitations": "Small-sample teams/players can be noisy.",
        "unit": "Goals per 90",
    },
    "chance_creation": {
        "formula": "CC = shot_opportunities + xG + assists (per match)",  # qualitative composite
        "variables": ["shots", "shots_on_target", "xG", "assists", "crosses", "corners"],
        "weighting": "Composite; individual components shown separately.",
        "normalization": "Per-match averages",
        "assumptions": "Volume roughly tracks creative output.",
        "limitations": "xG is estimated; no key-pass data available.",
        "unit": "Composite (per match)",
    },
    "finishing_efficiency": {
        "formula": "FE = (goals / shots) * 100  (and goals vs xG)",
        "variables": ["goals", "shots", "xG"],
        "weighting": "None",
        "normalization": "Percentage",
        "assumptions": "Shot count is a reasonable exposure measure.",
        "limitations": "No shot location data; xG is an estimate.",
        "unit": "%",
    },
    "defensive_efficiency": {
        "formula": "DE = goals_conceded and tackles+interceptions per match; adjusted for possession",
        "variables": ["goals_conceded", "tackles", "interceptions", "saves", "possession"],
        "weighting": "Composite; raw metrics shown.",
        "normalization": "Per-match averages",
        "assumptions": "Lower concession and more defensive actions indicate better defense.",
        "limitations": "Team style and opponent strength not controlled.",
        "unit": "Composite (per match)",
    },
    "goalkeeper_efficiency": {
        "formula": "GKE = saves / shots_on_target_against; goals_conceded per 90",
        "variables": ["saves", "goals_conceded", "shots_on_target_against"],
        "weighting": "None",
        "normalization": "Ratio and per-90",
        "assumptions": "Saves measure shot-stopping only.",
        "limitations": "No expected-goals-on-target available.",
        "unit": "Ratio / per 90",
    },
    "match_momentum": {
        "formula": "Momentum = rolling sum of goals/cards/shots within time windows",
        "variables": ["event minute", "event_type", "team_id"],
        "weighting": "Goals weighted higher than cards/shots.",
        "normalization": "Per 15-minute interval",
        "assumptions": "Temporal clustering of events indicates momentum swings.",
        "limitations": "Discrete event timestamps only (no continuous pressure).",
        "unit": "Events per interval",
    },
    "playing_style": {
        "formula": "Rule-based classification from possession, passes, fouls, shots",
        "variables": ["possession_pct", "passes", "total_shots", "fouls"],
        "weighting": "Decision thresholds (see match_analysis.classify_playing_style)",
        "normalization": "Categorical label",
        "assumptions": "Style is inferable from match aggregates.",
        "limitations": "No pressing/positional data; heuristic only.",
        "unit": "Category",
    },
    "estimated_air_pressure": {
        "formula": "P = P0 * (1 - 0.0065*h / 288.15) ** 5.255",
        "variables": ["elevation_meters (h)", "P0 = 101325 Pa"],
        "weighting": "Standard atmosphere model",
        "normalization": "Pa or hPa",
        "assumptions": "ISA standard atmosphere, dry air, no weather variation.",
        "limitations": "Ignores temperature/humidity effect on pressure; ESTIMATED.",
        "unit": "hPa",
    },
    "estimated_oxygen_availability": {
        "formula": "O2 = 20.9% * (P / P0)",
        "variables": ["estimated pressure (P)", "sea-level O2 20.9%"],
        "weighting": "Proportional to pressure ratio",
        "normalization": "Percentage of sea-level oxygen",
        "assumptions": "Oxygen fraction constant; density scales with pressure.",
        "limitations": "ESTIMATED; does not model acclimatization.",
        "unit": "% of sea level",
    },
}


def render_metric_methodology(metric_key: str):
    """Render the methodology for a metric in an expander."""
    info = METHODOLOGY.get(metric_key)
    if info is None:
        st.caption("Methodology not documented for this metric.")
        return
    with st.expander(f"📐 Methodology: {metric_key.replace('_', ' ').title()}"):
        st.markdown(f"**Formula:** `{info['formula']}`")
        st.markdown(f"**Variables:** {', '.join(info['variables'])}")
        st.markdown(f"**Weighting:** {info['weighting']}")
        st.markdown(f"**Normalization:** {info['normalization']}")
        st.markdown(f"**Assumptions:** {info['assumptions']}")
        st.markdown(f"**Limitations:** {info['limitations']}")
        st.markdown(f"**Unit:** {info['unit']}")


def annotate_chart(caption: str, metric_key: str = None):
    """
    Render a small caption under a chart identifying the value type
    (totals, per-match averages, percentages, per-90, normalized).
    """
    st.caption(caption)
    if metric_key and metric_key in METHODOLOGY:
        render_metric_methodology(metric_key)