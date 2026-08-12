"""
Page 4: Team Analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.loader import load_matches, load_teams, load_match_team_stats, load_match_events, load_player_stats
from utils.styles import apply_custom_css, style_plotly_fig
from utils.state import render_breadcrumbs, get_param, set_params, safe_page_link
from utils.methodology import annotate_chart, render_metric_methodology
from analytics.team_analysis import (all_teams_summary, team_aggregate, team_radar_data, rolling_team_trend)
from analytics.advanced_metrics import aggr_index_summary

st.set_page_config(page_title="Teams", page_icon="👥", layout="wide")
apply_custom_css()

matches = load_matches()
teams = load_teams()
team_stats = load_match_team_stats()
events = load_match_events()
player_stats = load_player_stats()

team_names = sorted(teams["team_name"].unique())
team_id = get_param("team_id")

# Read live widget state before breadcrumb so it can show the correct team
# even on the first interaction (URL hasn't been updated yet).
_live_team = st.session_state.get("team_sel")
if _live_team and _live_team in team_names:
    _live_id = teams.loc[teams["team_name"] == _live_team, "team_id"].values[0]
    render_breadcrumbs("Teams", team_name_override=_live_team, team_id_override=int(_live_id))
else:
    render_breadcrumbs("Teams")

st.markdown("<h1 class='main-header'>👥 Team Analysis</h1>", unsafe_allow_html=True)

# Use the URL team_id to set the selectbox default (only applies when the
# widget has no session state yet, i.e. first visit to this page).
if team_id:
    cur_names = teams.loc[teams["team_id"] == team_id, "team_name"].tolist()
    cur_name = cur_names[0] if cur_names else team_names[0]
else:
    cur_name = team_names[0]

sel_name = st.selectbox("Select Team", team_names,
                        index=team_names.index(cur_name),
                        key="team_sel")
team_id = teams.loc[teams["team_name"] == sel_name, "team_id"].values[0]
set_params(team_id=team_id, team_name=sel_name)

team_row = teams[teams["team_id"] == team_id]
team_name = team_row["team_name"].values[0]
set_params(team_id=team_id, team_name=team_name)

st.subheader(f"⭐ {team_name}")
agg = team_aggregate(team_id, matches, team_stats)

col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Matches", agg.get("matches_played", 0))
with col2: st.metric("Points", agg.get("points", 0))
with col3: st.metric("Goals For", agg.get("goals_for", 0))
with col4: st.metric("Goals Against", agg.get("goals_against", 0))
with col5: st.metric("GD", agg.get("goal_difference", 0))
annotate_chart("Matches, points, goals are TOTALS over the tournament.")

st.subheader("Radar Chart (vs Tournament Average)")
radar = team_radar_data(team_id, matches, team_stats, teams)
if radar:
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=radar["team_values"], theta=radar["categories"], fill='toself', name=radar["team"]))
    fig.add_trace(go.Scatterpolar(r=radar["tournament_values"], theta=radar["categories"], fill='toself', name="Tournament Average"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, height=500)
    st.plotly_chart(style_plotly_fig(fig), width="stretch")
    annotate_chart("Radar values NORMALIZED 0-100 across all tournament teams (min-max).", "chance_creation")
    with st.expander("Raw values (per-match averages)"):
        raw = pd.DataFrame({"Metric": radar["categories"][:6],
                            f"{radar['team']}": [radar["team_raw"][k] for k in ["Possession","Shots","Shots on Target","Goals per Match","Goal Difference","Goals Conceded per Match"]],
                            "Tournament avg": [radar["tournament_raw"][k] for k in ["Possession","Shots","Shots on Target","Goals per Match","Goal Difference","Goals Conceded per Match"]]})
        st.dataframe(raw, hide_index=True, width="stretch")

st.subheader("Attack")
c1, c2, c3 = st.columns(3)
with c1: st.metric("Avg Shots/Match", agg.get("avg_shots", 0))
with c2: st.metric("Avg SOT/Match", agg.get("avg_shots_on_target", 0))
with c3: st.metric("Goals/Match", agg.get("goals_per_match", 0))
annotate_chart("PER-MATCH AVERAGES.")

st.subheader("Defense")
c1, c2, c3 = st.columns(3)
with c1: st.metric("Conceded/Match", agg.get("goals_conceded_per_match", 0))
with c2: st.metric("Avg Saves/Match", agg.get("avg_saves", 0))
with c3: st.metric("Avg Offsides/Match", agg.get("avg_offsides", 0))
annotate_chart("PER-MATCH AVERAGES.")

st.subheader("Discipline (Aggressiveness Index)")
aggr = aggr_index_summary(team_stats, events)
if not aggr.empty:
    a_row = aggr[aggr["team_id"] == team_id]
    if not a_row.empty:
        st.metric("Aggressiveness Index (normalized)", round(a_row.iloc[0]["aggressiveness_index_norm"], 1))
        render_metric_methodology("aggressiveness_index")

st.subheader("Rolling Trends")
trend = rolling_team_trend(team_id, matches, team_stats)
if not trend.empty:
    fig = px.line(trend, x="match_number", y=["cum_goals", "cum_xg"],
                  labels={"value": "Cumulative", "match_number": "Match", "variable": "Series"},
                  title="Cumulative Goals vs xG")
    st.plotly_chart(style_plotly_fig(fig), width="stretch")
    annotate_chart("Cumulative TOTALS across matches.")

st.subheader("Comparisons")
tab1, tab2 = st.tabs(["Team vs Team", "Team vs Tournament Average"])
with tab1:
    other_names = [n for n in sorted(teams["team_name"].unique()) if n != team_name]
    other = st.selectbox("Compare with", other_names, key="team_vs_team")
    other_id = teams[teams["team_name"] == other]["team_id"].values[0]
    other_agg = team_aggregate(other_id, matches, team_stats)
    comp_df = pd.DataFrame({
        "Metric": ["Points", "Matches", "Goals For", "Goals Against", "GD", "Avg Possession", "Avg Shots/Match", "Goals/Match"],
        team_name: [agg.get("points"), agg.get("matches_played"), agg.get("goals_for"), agg.get("goals_against"), agg.get("goal_difference"), agg.get("avg_possession"), agg.get("avg_shots"), agg.get("goals_per_match")],
        other: [other_agg.get("points"), other_agg.get("matches_played"), other_agg.get("goals_for"), other_agg.get("goals_against"), other_agg.get("goal_difference"), other_agg.get("avg_possession"), other_agg.get("avg_shots"), other_agg.get("goals_per_match")],
    })
    st.dataframe(comp_df, hide_index=True, width="stretch")
    annotate_chart("Points/goals are TOTALS; avg* are PER-MATCH AVERAGES.")
with tab2:
    summary = all_teams_summary(matches, team_stats, teams)
    if not summary.empty:
        tavg = {"Points": summary["points"].mean(), "Goals For": summary["goals_for"].mean(), "Goals Against": summary["goals_against"].mean(), "Avg Possession": summary["avg_possession"].mean(), "Avg Shots/Match": summary["avg_shots"].mean(), "Goals/Match": summary["goals_per_match"].mean()}
        tdf = pd.DataFrame({"Metric": list(tavg.keys()), team_name: [agg.get(k, 0) for k in ["points", "goals_for", "goals_against", "avg_possession", "avg_shots", "goals_per_match"]], "Tournament Avg": list(tavg.values())})
        st.dataframe(tdf, hide_index=True, width="stretch")
        annotate_chart("Team values are TOTALS/per-match as labelled; tournament avg for totals is a MEAN of team totals.")

# Player links
st.subheader("Squad")
team_players = player_stats[player_stats["team_id"] == team_id]
if not team_players.empty:
    from_page = get_param("_from") or "Teams"
    continent = get_param("continent")
    for _, p in team_players.iterrows():
        player_params = {
            "player_id": p["player_id"],
            "player_name": p["player_name"],
            "team_id": team_id,
            "team_name": team_name,
            "_from": from_page,
        }
        if continent:
            player_params["continent"] = continent
        safe_page_link("pages/05_Players.py", f"⭐ {p['player_name']} ({p['position']})",
                     query_params=player_params)
