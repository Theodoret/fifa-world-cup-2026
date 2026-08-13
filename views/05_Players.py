"""
Page 5: Player Analysis
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.loader import load_player_stats, load_teams
from utils.styles import apply_custom_css
from utils.state import render_breadcrumbs, get_param, set_params
from utils.methodology import annotate_chart
from analytics.player_analysis import (player_summary,
                                       player_vs_position_average, player_vs_team_average,
                                       player_vs_tournament_average)

apply_custom_css()

player_stats = load_player_stats()
teams = load_teams()
summary = player_summary(player_stats, teams)
if summary.empty:
    st.info("No player data available.")
    st.stop()

player_id = get_param("player_id")
team_name_from_url = get_param("team_name")

# Look up player's team from URL player_id to auto-select team filter
if player_id and not team_name_from_url:
    p_row = player_stats[player_stats["player_id"] == player_id]
    if not p_row.empty:
        tid = p_row.iloc[0]["team_id"]
        t_row = teams[teams["team_id"] == tid]
        if not t_row.empty:
            team_name_from_url = t_row.iloc[0]["team_name"]

# Breadcrumb at top (like all other pages) — use live widget override
_live_player = st.session_state.get("player_sel")
if _live_player and _live_player != "-- Select a player --":
    render_breadcrumbs("Players", player_name_override=_live_player)
else:
    render_breadcrumbs("Players")

st.markdown("<h1 class='main-header'>⭐ Player Analysis</h1>", unsafe_allow_html=True)

# Team filter before player selection (always visible)
team_names = sorted(teams["team_name"].unique())
team_options = ["All Teams"] + team_names
team_default_idx = 0
if team_name_from_url and team_name_from_url in team_names:
    team_default_idx = team_options.index(team_name_from_url)
sel_team_filter = st.selectbox("Filter by Team", team_options,
                               index=team_default_idx, key="player_team_filter")

# Detect team filter change — clear stale player params from URL
prev_team = st.session_state.get("_prev_team_filter")
if prev_team is not None and prev_team != sel_team_filter:
    if "player_id" in st.query_params:
        del st.query_params["player_id"]
    if "player_name" in st.query_params:
        del st.query_params["player_name"]
    player_id = None
st.session_state["_prev_team_filter"] = sel_team_filter

filtered_players = summary
if sel_team_filter and sel_team_filter != "All Teams":
    filtered_players = summary[summary["team_name"] == sel_team_filter]
player_names = sorted(filtered_players["player_name"].unique())
if not player_names:
    st.info("No players found for the selected team.")
    st.stop()

# Use URL param to set initial default, otherwise placeholder
if player_id:
    cur_names = filtered_players[filtered_players["player_id"] == player_id]["player_name"].tolist()
    cur_name = cur_names[0] if cur_names else None
else:
    cur_name = None

options = ["-- Select a player --"] + player_names
default_idx = 0
if cur_name and cur_name in player_names:
    default_idx = options.index(cur_name)

sel_name = st.selectbox("Select Player", options, index=default_idx,
                        key="player_sel")

if not sel_name or sel_name == "-- Select a player --":
    st.info("Select a player to view their stats.")
    st.stop()

row = player_stats[player_stats["player_name"] == sel_name].iloc[0]
player_id = row["player_id"]
set_params(player_id=player_id, player_name=sel_name)

p_row = player_stats[player_stats["player_id"] == player_id]
if p_row.empty:
    st.warning("Player not found.")
    st.stop()
prow = p_row.iloc[0]
pname = prow["player_name"]
set_params(player_id=player_id, player_name=pname)

st.subheader(f"⭐ {pname}")
p_team = teams[teams["team_id"] == prow["team_id"]]["team_name"].values[0] if len(teams[teams["team_id"] == prow["team_id"]]["team_name"].values) else "?"

col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Team", p_team)
with col2: st.metric("Position", prow["position"])
with col3: st.metric("Goals", prow["goals"])
with col4: st.metric("Assists", prow["assists"])
with col5: st.metric("Minutes", prow["minutes_played"])
annotate_chart("Goals/assists/minutes are TOTALS over the tournament.")

p_sum = summary[summary["player_id"] == player_id]
if not p_sum.empty:
    ps = p_sum.iloc[0]
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Goals/90", ps.get("goals_per90", 0))
    with col2: st.metric("Assists/90", ps.get("assists_per90", 0))
    with col3: st.metric("Shot Conv %", ps.get("shot_conversion_pct", 0))
    rating = ps.get("average_rating")
    with col4: st.metric("Rating", rating if pd.notna(rating) else "-")
    with col5: st.metric("Cards", int(prow.get("yellow_cards", 0) or 0) + int(prow.get("red_cards", 0) or 0))
    annotate_chart("goals/90 and assists/90 are PER-90 VALUES. Shot conv is a PERCENTAGE. Rating is raw.")

st.subheader("Player Comparisons")
tab1, tab2, tab3, tab4 = st.tabs(["vs Player", "vs Team Avg", "vs Position Avg", "vs Tournament Avg"])
with tab1:
    other_names = [n for n in sorted(player_stats["player_name"].unique()) if n != pname]
    other = st.selectbox("Compare with player", other_names, key="p_vs_p")
    other_row = player_stats[player_stats["player_name"] == other].iloc[0]
    p2 = summary[summary["player_id"] == other_row["player_id"]]
    p2s = p2.iloc[0] if not p2.empty else None
    cmp_df = pd.DataFrame({
        "Metric": ["Goals", "Assists", "Minutes", "Goals/90", "Assists/90", "Shot Conv %", "Rating"],
        pname: [prow["goals"], prow["assists"], prow["minutes_played"],
                ps.get("goals_per90", 0), ps.get("assists_per90", 0),
                ps.get("shot_conversion_pct", 0), ps.get("average_rating") if pd.notna(ps.get("average_rating")) else "-"],
        other: [other_row["goals"], other_row["assists"], other_row["minutes_played"],
                p2s.get("goals_per90", 0) if p2s is not None else 0,
                p2s.get("assists_per90", 0) if p2s is not None else 0,
                p2s.get("shot_conversion_pct", 0) if p2s is not None else 0,
                p2s.get("average_rating", "-") if p2s is not None else "-"],
    })
    st.dataframe(cmp_df, hide_index=True, width="stretch")
    annotate_chart("Totals vs per-90 vs percentages as labelled.")
with tab2:
    comp = player_vs_team_average(player_stats, teams, player_id)
    if comp:
        st.markdown(f"**{pname} vs {p_team} average**")
        cdf = pd.DataFrame({"Metric": ["Goals/90", "Assists/90", "Avg Rating"],
                            pname: [ps.get("goals_per90", 0), ps.get("assists_per90", 0), ps.get("average_rating") if pd.notna(ps.get("average_rating")) else "-"],
                            "Team Avg": [comp["team_avg"]["goals_per90"], comp["team_avg"]["assists_per90"], comp["team_avg"]["avg_rating"]]})
        st.dataframe(cdf, hide_index=True, width="stretch")
with tab3:
    comp = player_vs_position_average(player_stats, teams, player_id)
    if comp:
        st.markdown(f"**{pname} vs {comp['position']} average**")
        cdf = pd.DataFrame({"Metric": ["Goals/90", "Assists/90", "Avg Rating"],
                            pname: [ps.get("goals_per90", 0), ps.get("assists_per90", 0), ps.get("average_rating") if pd.notna(ps.get("average_rating")) else "-"],
                            "Position Avg": [comp["position_avg"]["goals_per90"], comp["position_avg"]["assists_per90"], comp["position_avg"]["avg_rating"]]})
        st.dataframe(cdf, hide_index=True, width="stretch")
with tab4:
    comp = player_vs_tournament_average(player_stats, teams, player_id)
    if comp:
        st.markdown(f"**{pname} vs tournament average**")
        cdf = pd.DataFrame({"Metric": ["Goals/90", "Assists/90", "Avg Rating"],
                            pname: [ps.get("goals_per90", 0), ps.get("assists_per90", 0), ps.get("average_rating") if pd.notna(ps.get("average_rating")) else "-"],
                            "Tournament Avg": [comp["tournament_avg"]["goals_per90"], comp["tournament_avg"]["assists_per90"], comp["tournament_avg"]["avg_rating"]]})
        st.dataframe(cdf, hide_index=True, width="stretch")
