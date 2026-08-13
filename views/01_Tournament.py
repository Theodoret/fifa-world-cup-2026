"""
Page 1: Tournament Overview
Breadcrumb root. Uses query params for navigation to team/continent pages.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.loader import load_matches, load_teams, load_tournament_stages, load_match_team_stats, load_match_events
from utils.preprocessing import clean_matches, merge_match_with_teams, merge_match_with_stages
from utils.styles import apply_custom_css, get_theme_colors
from utils.state import render_breadcrumbs, get_param, safe_page_link
from utils.methodology import annotate_chart
from utils.bracket import build_bracket_html, bracket_height
from utils.embed import embed_html
from analytics.team_analysis import all_teams_summary
from analytics.continent_analysis import continent_summary
from analytics.advanced_metrics import aggr_index_summary
from analytics.player_analysis import player_summary, top_players
from utils.loader import load_player_stats

apply_custom_css()
render_breadcrumbs("Tournament")
st.markdown("<h1 class='main-header'>🏆 Tournament Overview</h1>", unsafe_allow_html=True)

matches = load_matches()
teams = load_teams()
stages = load_tournament_stages()
team_stats = load_match_team_stats()
events = load_match_events()

matches = clean_matches(matches)
matches = merge_match_with_stages(matches, stages)
matches_enriched = merge_match_with_teams(matches, teams)
team_stats_m = team_stats.merge(teams[["team_id", "confederation", "team_name"]], on="team_id", how="left")

st.subheader("Tournament at a Glance")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Matches", len(matches_enriched))
with col2:
    st.metric("Total Teams", teams["team_id"].nunique())
with col3:
    total_goals = matches_enriched["home_score"].sum() + matches_enriched["away_score"].sum()
    st.metric("Total Goals", total_goals)
with col4:
    avg_goals = round(total_goals / len(matches_enriched), 2) if len(matches_enriched) else 0
    st.metric("Avg Goals/Match", avg_goals)
annotate_chart("Goals are TOTALS. Avg goals per match is a PER-MATCH AVERAGE.")

st.subheader("Group Standings")
team_summary = all_teams_summary(matches, team_stats, teams)
if not team_summary.empty:
    groups = sorted(teams["group_letter"].dropna().unique())
    # Arrange groups in 3 columns
    cols = st.columns(3)
    for idx, group in enumerate(groups):
        group_df = team_summary[team_summary["group_letter"] == group].copy()
        if group_df.empty:
            continue
        group_df = group_df.sort_values(["points", "goal_difference", "goals_for"], ascending=False)
        with cols[idx % 3]:
            st.markdown(f"**Group {group}**")
            subgroup = group_df[["team_name", "matches_played", "wins", "draws", "losses",
                                 "goals_for", "goals_against", "goal_difference", "points"]]
            # Header row
            hcols = st.columns([2, 1, 1, 1, 1, 1, 1, 1, 1])
            headers = ["", "MP", "W", "D", "L", "GF", "GA", "GD", "Pts"]
            for hi, h in enumerate(headers):
                with hcols[hi]:
                    st.markdown(f"**{h}**")
            for _, row in subgroup.iterrows():
                tname = row["team_name"]
                tid = teams[teams["team_name"] == tname]["team_id"].values[0]
                rcols = st.columns([2, 1, 1, 1, 1, 1, 1, 1, 1])
                with rcols[0]:
                    safe_page_link("views/04_Teams.py", tname,
                                   query_params={"team_id": tid, "team_name": tname, "_from": "Tournament"})
                with rcols[1]: st.write(str(int(row["matches_played"])))
                with rcols[2]: st.write(str(int(row["wins"])))
                with rcols[3]: st.write(str(int(row["draws"])))
                with rcols[4]: st.write(str(int(row["losses"])))
                with rcols[5]: st.write(str(int(row["goals_for"])))
                with rcols[6]: st.write(str(int(row["goals_against"])))
                with rcols[7]: st.write(str(int(row["goal_difference"])))
                with rcols[8]: st.write(str(int(row["points"])))
else:
    st.info("No team data available yet.")

st.subheader("Tournament Bracket")
bracket_html = build_bracket_html(matches_enriched, teams, theme=get_theme_colors())
if bracket_html:
    embed_html(bracket_html, height=bracket_height(matches_enriched))
else:
    st.info("Knockout bracket data not available.")

st.subheader("Confederation Performance")
continent_df = continent_summary(teams, matches, team_stats)
if not continent_df.empty:
    st.markdown("""
    **Total Points by Confederation** — sum of all points earned by every team in each confederation.
    Points are awarded as: **3 for a win, 1 for a draw, 0 for a loss**.
    The bar labels show the confederation's **win rate** (total wins / total matches played, as a percentage).
    """)
    fig = px.bar(continent_df, x="confederation", y="total_points",
                 color="confederation", text="win_rate",
                 labels={"total_points": "Points", "confederation": ""})
    fig.update_traces(texttemplate="%{text}% WR", textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")
    annotate_chart("Points are TOTALS. Win rate is a PERCENTAGE.")

    # Confederation links in one row
    link_cols = st.columns(len(continent_df))
    for ci, (_, row) in enumerate(continent_df.iterrows()):
        with link_cols[ci]:
            safe_page_link("views/03_Continents.py", f"🌍 {row['confederation']}",
                           query_params={"continent": row["confederation"], "_from": "Tournament"})
else:
    st.info("No continent data available.")

st.subheader("Aggressiveness Index")
aggr = aggr_index_summary(team_stats, events)
if not aggr.empty:
    aggr = aggr.merge(teams[["team_id", "team_name"]], on="team_id", how="left")
    aggr = aggr.sort_values("aggressiveness_index_norm", ascending=False)
    fig = px.bar(aggr, x="team_name", y="aggressiveness_index_norm", color="team_name",
                 title="Normalized Aggressiveness Index (0-100)", labels={"aggressiveness_index_norm": "Index"})
    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig, width="stretch")
    annotate_chart("Index NORMALIZED 0-100 across teams. Per-match averages of fouls/yellows/reds.",
                   metric_key="aggressiveness_index")
else:
    st.info("Aggressiveness data unavailable.")

st.subheader("Top Players")
player_stats = load_player_stats()
col_m, col_n = st.columns([2, 1])
with col_m:
    top_metric = st.selectbox("Sort by", ["Goals", "Goals per 90", "Assists", "Assists per 90",
                                          "Goal Contributions per 90", "Shot Conversion %", "Average Rating"],
                              key="tourn_top_metric")
    _metric_map = {
        "Goals": "goals",
        "Goals per 90": "goals_per90",
        "Assists": "assists",
        "Assists per 90": "assists_per90",
        "Goal Contributions per 90": "goal_contrib_per90",
        "Shot Conversion %": "shot_conversion_pct",
        "Average Rating": "average_rating",
    }
    top_metric_key = _metric_map[top_metric]
with col_n:
    top_n = st.number_input("Number of players", min_value=5, max_value=100, value=10, step=1,
                            key="tourn_top_n")
top = top_players(player_stats, teams, metric=top_metric_key, n=top_n)
if not top.empty:
    display_cols = ["player_name", "team_name", "position", "goals", "assists", "goals_per90", "assists_per90"]
    if top_metric_key not in display_cols:
        display_cols.append(top_metric_key)
    existing = [c for c in display_cols if c in top.columns]
    # Header row
    col_widths = [2] + [1] * (len(existing) - 1)
    cols = st.columns(col_widths)
    for i, h in enumerate(existing):
        with cols[i]:
            st.markdown(f"**{h.replace('_', ' ').title()}**")
    # Data rows with clickable player name
    for _, r in top[existing + ["player_id"]].iterrows():
        cols = st.columns(col_widths)
        with cols[0]:
            safe_page_link("views/05_Players.py", f"⭐ {r['player_name']}",
                           query_params={"player_id": r["player_id"], "player_name": r["player_name"],
                                         "_from": "Tournament"})
        for j, c in enumerate(existing[1:], 1):
            with cols[j]:
                val = r[c]
                if isinstance(val, float):
                    st.write(f"{val:.2f}" if val < 10 else f"{val:.1f}")
                else:
                    st.write(str(val))
