"""
Page 2: Match Explorer
Local filters (stage, team) before match selection.
Newspaper-style match summary card.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.loader import (load_matches, load_teams, load_tournament_stages,
                          load_match_team_stats, load_match_events, load_matches_detailed,
                          load_venues)
from utils.preprocessing import clean_matches, merge_match_with_teams, merge_match_with_stages
from utils.styles import apply_custom_css, get_theme_colors
from utils.state import render_breadcrumbs, get_param, set_params
from utils.methodology import annotate_chart, render_metric_methodology
from analytics.advanced_metrics import (chance_creation, match_momentum, style_per_match)

st.set_page_config(page_title="Match Explorer", page_icon="📋", layout="wide")
apply_custom_css()
render_breadcrumbs("Matches")

st.markdown("<h1 class='main-header'>📋 Match Explorer</h1>", unsafe_allow_html=True)

matches = load_matches()
teams = load_teams()
stages = load_tournament_stages()
venues = load_venues()
team_stats = load_match_team_stats()
events = load_match_events()
detailed = load_matches_detailed()
matches = clean_matches(matches)
matches = merge_match_with_stages(matches, stages)
matches_enriched = merge_match_with_teams(matches, teams)
matches_enriched = matches_enriched.merge(
    venues[["venue_id", "stadium_name", "city", "country"]], on="venue_id", how="left"
)

# --- Local filters ---
# Stage selectbox first (team options depend on it)
col_f1, col_f2 = st.columns(2)
with col_f1:
    stage_options = ["All Stages"] + sorted(matches_enriched["stage_name"].dropna().unique())
    sel_stage = st.selectbox("Stage", stage_options, key="match_stage")

# Compute team match counts based on the current stage filter
stage_filtered = matches_enriched.copy()
if sel_stage and sel_stage != "All Stages":
    stage_filtered = stage_filtered[stage_filtered["stage_name"] == sel_stage]

team_counts = {}
for _, r in stage_filtered.iterrows():
    team_counts[r["home_name"]] = team_counts.get(r["home_name"], 0) + 1
    team_counts[r["away_name"]] = team_counts.get(r["away_name"], 0) + 1
team_options = ["All Teams"] + [
    f"{t} ({team_counts[t]})" for t in sorted(team_counts.keys())
]

with col_f2:
    sel_team = st.selectbox("Team", team_options, key="match_team")

# Extract base team name from selection (strip count suffix)
if sel_team and sel_team != "All Teams":
    base_team = sel_team.rsplit(" (", 1)[0]
else:
    base_team = sel_team

# Apply local filters
filtered = matches_enriched.copy()
if sel_stage and sel_stage != "All Stages":
    filtered = filtered[filtered["stage_name"] == sel_stage]
if base_team and base_team != "All Teams":
    filtered = filtered[(filtered["home_name"] == base_team) | (filtered["away_name"] == base_team)]

# --- Match selector (always visible, starts empty) ---
match_labels = filtered.apply(
    lambda r: f"{r['stage_name']} | {r['home_name']} vs {r['away_name']} | {r['date'].strftime('%Y-%m-%d') if hasattr(r['date'], 'strftime') else r['date']}",
    axis=1
).tolist()
label_to_id = dict(zip(match_labels, filtered["match_id"].tolist()))

# Track the user's explicit selection so we can detect when it falls out of
# the current filter and reset back to empty.
url_match_id = get_param("match_id")
selected_id = st.session_state.get("_selected_match_id")

# If there is no user selection yet but the URL points to a match that is
# present in the current filter, pre-select it (e.g. drill-down from another
# page). Otherwise the selection stays empty.
if selected_id is None and url_match_id:
    selected_id = url_match_id

# If the current selection is no longer in the filtered set (filters changed),
# reset to empty and force a fresh widget by changing its key.
filter_ids = set(filtered["match_id"].tolist())
if selected_id is not None and selected_id not in filter_ids:
    selected_id = None
    st.session_state["_selected_match_id"] = None
    if "match_id" in st.query_params:
        del st.query_params["match_id"]

# Build options with an empty placeholder as the first entry.
placeholder = "Select a match..."
options = [placeholder] + match_labels
default_idx = 0
if selected_id is not None:
    for lbl, mid in label_to_id.items():
        if mid == selected_id:
            default_idx = options.index(lbl)
            break

# Widget key includes the filter signature so changing the filter resets
# the widget even when the selected match label is no longer in the list.
filter_sig = f"{sel_stage}|{base_team}"
sel_match_label = st.selectbox("Select Match", options, index=default_idx,
                               key=f"match_sel_{filter_sig}")

if sel_match_label == placeholder:
    # Nothing selected yet — show a hint and stop before the summary.
    st.info("Select a match to see its summary and advanced metrics.")
    st.stop()

sel_idx = match_labels.index(sel_match_label)
sel_match = filtered.iloc[sel_idx]
match_id = sel_match["match_id"]
st.session_state["_selected_match_id"] = match_id
set_params(match_id=match_id)

# --- Newspaper-style Match Summary ---
home_name = sel_match["home_name"]
away_name = sel_match["away_name"]
home_score = int(sel_match["home_score"])
away_score = int(sel_match["away_score"])
match_date = sel_match["date"].strftime("%A, %d %B %Y") if hasattr(sel_match["date"], "strftime") else str(sel_match["date"])
match_stage = sel_match["stage_name"]
stadium = sel_match.get("stadium_name", "")
city = sel_match.get("city", "")
country = sel_match.get("country", "")

h_stats = team_stats[(team_stats["match_id"] == match_id) & (team_stats["team_id"] == sel_match["home_team_id"])]
a_stats = team_stats[(team_stats["match_id"] == match_id) & (team_stats["team_id"] == sel_match["away_team_id"])]
hs = h_stats.iloc[0] if not h_stats.empty else None
aw = a_stats.iloc[0] if not a_stats.empty else None

det = detailed[detailed["match_id"] == match_id]
home_xg = det.iloc[0]["home_xg"] if not det.empty else None
away_xg = det.iloc[0]["away_xg"] if not det.empty else None

# Determine result type
result_type = sel_match.get("result_type", "")
if result_type == "Penalties":
    home_pen = int(sel_match.get("home_penalty_score", 0))
    away_pen = int(sel_match.get("away_penalty_score", 0))
    result_line = f"{home_score}–{away_score} (pens: {home_pen}–{away_pen})"
elif result_type == "AET":
    result_line = f"{home_score}–{away_score} (a.e.t.)"
else:
    result_line = f"{home_score}–{away_score}"

# Build the match summary card
st.subheader("Match Summary")

# Match info bar — theme-aware
tc = get_theme_colors()
st.markdown(f"""
<div class="match-info-bar">
    <div><span class="label">Stage</span><br><strong>{match_stage}</strong></div>
    <div><span class="label">Date</span><br><strong>{match_date}</strong></div>
    <div><span class="label">Venue</span><br><strong>{stadium}</strong></div>
    <div><span class="label">Location</span><br><strong>{city}, {country}</strong></div>
</div>
""", unsafe_allow_html=True)

# Scoreboard card — use components.html to avoid Streamlit markdown sanitization
# which strips complex inline-CSS blocks.
import streamlit.components.v1 as components

home_code = sel_match.get("home_fifa_code", "")
away_code = sel_match.get("away_fifa_code", "")

def stat_val(s, key, fmt="{}"):
    if s is None:
        return "-"
    v = s.get(key)
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "-"
    return fmt.format(v)

home_poss = stat_val(hs, "possession_pct", "{}%")
away_poss = stat_val(aw, "possession_pct", "{}%")
home_shots = stat_val(hs, "total_shots")
away_shots = stat_val(aw, "total_shots")
home_sot = stat_val(hs, "shots_on_target")
away_sot = stat_val(aw, "shots_on_target")
home_corners = stat_val(hs, "corners")
away_corners = stat_val(aw, "corners")
home_fouls = stat_val(hs, "fouls")
away_fouls = stat_val(aw, "fouls")
home_saves = stat_val(hs, "saves")
away_saves = stat_val(aw, "saves")
home_offsides = stat_val(hs, "offsides")
away_offsides = stat_val(aw, "offsides")

home_xg_str = f"{home_xg:.2f}" if home_xg is not None else "-"
away_xg_str = f"{away_xg:.2f}" if away_xg is not None else "-"

home_win = home_score > away_score
away_win = away_score > home_score

scoreboard_html = f"""
<div style="
    background: {tc['bg_card']};
    border-radius: 16px;
    padding: 2rem 1.5rem;
    margin-bottom: 2rem;
    box-shadow: {tc['shadow']};
    border: 1px solid {tc['border']};
    font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: {tc['text_secondary']};
">

    <!-- Scoreboard row -->
    <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1.8rem;">
        <div style="text-align: center; flex: 1; max-width: 200px;">
            <div style="font-size: 1.1rem; font-weight: 700; color: {tc['text'] if home_win else tc['text_muted']}; margin-bottom: 0.3rem;">{home_name}</div>
            <div style="font-size: 0.8rem; color: {tc['text_muted']};">{home_code}</div>
        </div>
        <div style="text-align: center; min-width: 100px;">
            <div style="font-size: 3rem; font-weight: 800; color: {tc['text']}; line-height: 1; letter-spacing: -0.03em;">{result_line}</div>
            <div style="font-size: 0.75rem; color: {tc['text_muted']}; margin-top: 0.2rem;">{'Penalty Shootout' if result_type == 'Penalties' else 'After Extra Time' if result_type == 'AET' else 'Full Time'}</div>
        </div>
        <div style="text-align: center; flex: 1; max-width: 200px;">
            <div style="font-size: 1.1rem; font-weight: 700; color: {tc['text'] if away_win else tc['text_muted']}; margin-bottom: 0.3rem;">{away_name}</div>
            <div style="font-size: 0.8rem; color: {tc['text_muted']};">{away_code}</div>
        </div>
    </div>

    <!-- xG bar -->
    <div style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: {tc['text_muted']}; margin-bottom: 0.3rem;">
            <span>xG: <strong style="color:{tc['text']};">{home_xg_str}</strong></span>
            <span>xG: <strong style="color:{tc['text']};">{away_xg_str}</strong></span>
        </div>
        <div style="display: flex; height: 8px; border-radius: 4px; overflow: hidden; background: {tc['border']};">
            <div style="width: {max(5, min(95, (home_xg or 0) / max((home_xg or 0) + (away_xg or 0), 0.01) * 100)):.0f}%; background: {tc['home']};"></div>
            <div style="width: {max(5, min(95, (away_xg or 0) / max((home_xg or 0) + (away_xg or 0), 0.01) * 100)):.0f}%; background: {tc['away']};"></div>
        </div>
    </div>

    <!-- Stats grid -->
    <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 0.4rem 1rem; font-size: 0.9rem;">
        <div style="text-align: right; font-weight: 600; color: {tc['home']};">{home_poss}</div>
        <div style="text-align: center; color: {tc['text_muted']}; font-size: 0.75rem; font-weight: 600;">POSSESSION</div>
        <div style="font-weight: 600; color: {tc['away']};">{away_poss}</div>

        <div style="text-align: right;">{home_shots}</div>
        <div style="text-align: center; color: {tc['text_muted']}; font-size: 0.75rem;">SHOTS</div>
        <div>{away_shots}</div>

        <div style="text-align: right;">{home_sot}</div>
        <div style="text-align: center; color: {tc['text_muted']}; font-size: 0.75rem;">SHOTS ON TARGET</div>
        <div>{away_sot}</div>

        <div style="text-align: right;">{home_corners}</div>
        <div style="text-align: center; color: {tc['text_muted']}; font-size: 0.75rem;">CORNERS</div>
        <div>{away_corners}</div>

        <div style="text-align: right;">{home_fouls}</div>
        <div style="text-align: center; color: {tc['text_muted']}; font-size: 0.75rem;">FOULS</div>
        <div>{away_fouls}</div>

        <div style="text-align: right;">{home_saves}</div>
        <div style="text-align: center; color: {tc['text_muted']}; font-size: 0.75rem;">SAVES</div>
        <div>{away_saves}</div>

        <div style="text-align: right;">{home_offsides}</div>
        <div style="text-align: center; color: {tc['text_muted']}; font-size: 0.75rem;">OFFSIDES</div>
        <div>{away_offsides}</div>
    </div>
</div>
"""
components.html(scoreboard_html, height=380)

# --- Advanced Match Metrics ---
st.subheader("Advanced Match Metrics")
tab1, tab2, tab3, tab4 = st.tabs(["Chance Creation", "Finishing", "Defensive", "Momentum"])
match_stats = team_stats[team_stats["match_id"] == match_id].copy()
match_stats = match_stats.merge(teams[["team_id", "team_name"]], on="team_id", how="left")

with tab1:
    cc = chance_creation(match_stats)
    cc_display = cc[["team_name", "possession_pct", "total_shots", "shots_on_target", "corners", "chance_creation_score"]].copy()
    cc_display = cc_display.rename(columns={
        "possession_pct": "Possession %",
        "total_shots": "Total Shots",
        "shots_on_target": "Shots on Target",
        "corners": "Corners",
        "chance_creation_score": "Chance Creation Score",
    })
    st.dataframe(cc_display, hide_index=True, width="stretch")
    render_metric_methodology("chance_creation")
with tab2:
    if not det.empty:
        d = det.iloc[0]
        fin_data = pd.DataFrame({
            "Team": [home_name, away_name],
            "Goals": [home_score, away_score],
            "xG": [d["home_xg"], d["away_xg"]],
            "Shots": [int(hs["total_shots"]) if hs is not None else 0,
                      int(aw["total_shots"]) if aw is not None else 0],
            "SOT": [int(hs["shots_on_target"]) if hs is not None else 0,
                    int(aw["shots_on_target"]) if aw is not None else 0],
        })
        if fin_data["SOT"].sum() > 0:
            fin_data["Conversion %"] = fin_data.apply(
                lambda r: round(r["Goals"] / r["SOT"] * 100, 1) if r["SOT"] > 0 else 0, axis=1)
        st.dataframe(fin_data, hide_index=True, width="stretch")
    render_metric_methodology("finishing_efficiency")
with tab3:
    if hs is not None and aw is not None:
        def_data = pd.DataFrame({
            "Team": [home_name, away_name],
            "Goals Conceded": [away_score, home_score],
            "Saves": [hs["saves"], aw["saves"]],
            "Fouls": [hs["fouls"], aw["fouls"]],
            "Offsides": [hs["offsides"], aw["offsides"]],
        })
        st.dataframe(def_data, hide_index=True, width="stretch")
    render_metric_methodology("defensive_efficiency")
with tab4:
    moments = match_momentum(events, match_id, interval_minutes=15)
    if not moments.empty:
        moments = moments.merge(teams[["team_id", "team_name"]], on="team_id", how="left")
        fig = px.bar(moments, x="interval", y="momentum", color="team_name",
                     title="Match Momentum (weighted events per interval)",
                     labels={"interval": "Minute", "momentum": "Weighted Events"})
        st.plotly_chart(fig, use_container_width=True)
        render_metric_methodology("match_momentum")
    else:
        st.info("No event data for momentum analysis.")

st.subheader("Playing Style")
style_data = style_per_match(match_stats)
if not style_data.empty:
    style_display = style_data[["team_name", "possession_pct", "total_shots", "fouls", "playing_style"]].copy()
    style_display = style_display.rename(columns={
        "possession_pct": "Possession %",
        "total_shots": "Total Shots",
        "fouls": "Fouls",
        "playing_style": "Playing Style",
    })
    st.dataframe(style_display, hide_index=True, width="stretch")
    annotate_chart("Style CLASSIFICATION based on per-match aggregates.", "playing_style")
