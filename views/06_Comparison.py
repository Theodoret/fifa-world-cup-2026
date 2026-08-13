"""
Page 6: Universal Comparison
"""
import streamlit as st
import pandas as pd

from utils.loader import load_matches, load_teams, load_match_team_stats, load_player_stats
from utils.styles import apply_custom_css, get_theme_colors
from utils.state import render_breadcrumbs
from analytics.comparison_engine import compare_two_teams
from analytics.team_analysis import all_teams_summary

apply_custom_css()
render_breadcrumbs("Comparison")

st.markdown("<h1 class='main-header'>⚖️ Universal Comparison</h1>", unsafe_allow_html=True)

tc = get_theme_colors()
_highlight = f"background-color: {tc['accent_soft']}; border-radius: 6px; padding: 4px 8px;"

matches = load_matches()
teams = load_teams()
team_stats = load_match_team_stats()
player_stats = load_player_stats()

tab1, tab2, tab3 = st.tabs(["Team vs Team", "Player vs Player", "Team vs Continent"])

with tab1:
    st.subheader("Team vs Team")
    team_names = sorted(teams["team_name"].unique())
    c1, c2 = st.columns(2)
    with c1: t1_name = st.selectbox("Team 1", team_names, key="u_t1")
    with c2: t2_name = st.selectbox("Team 2", team_names, key="u_t2")
    if st.button("Compare Teams", type="primary", key="u_btn_t"):
        t1_id = teams[teams["team_name"] == t1_name]["team_id"].values[0]
        t2_id = teams[teams["team_name"] == t2_name]["team_id"].values[0]
        result = compare_two_teams(t1_id, t2_id, matches, team_stats, teams)
        rows = ["Matches Played", "Wins", "Draws", "Losses", "Goals For", "Goals Against", "Goal Difference", "Points", "Avg Possession", "Avg Shots", "Avg Shots on Target", "Avg Fouls"]
        keys = ["matches_played", "wins", "draws", "losses", "goals_for", "goals_against", "goal_difference", "points", "avg_possession", "avg_shots", "avg_shots_on_target", "avg_fouls"]
        higher_better = {
            "Matches Played": True, "Wins": True, "Draws": None,
            "Losses": False, "Goals For": True, "Goals Against": False,
            "Goal Difference": True, "Points": True, "Avg Possession": True,
            "Avg Shots": True, "Avg Shots on Target": True, "Avg Fouls": False,
        }
        def _fmt(v):
            try:
                f = float(v)
                return int(f) if f == int(f) else round(f, 1)
            except (ValueError, TypeError):
                return v
        t1_vals = [_fmt(result["team1"].get(k, "-")) for k in keys]
        t2_vals = [_fmt(result["team2"].get(k, "-")) for k in keys]
        # Header
        cols = st.columns([1, 2, 1])
        cols[0].markdown(f"<div style='text-align: center; font-weight: bold;'>{t1_name}</div>", unsafe_allow_html=True)
        cols[1].markdown("<div style='text-align: center; font-weight: bold;'>Metric</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div style='text-align: center; font-weight: bold;'>{t2_name}</div>", unsafe_allow_html=True)
        for i, metric in enumerate(rows):
            v1, v2 = t1_vals[i], t2_vals[i]
            direction = higher_better.get(metric)
            bg1 = bg2 = ""
            if direction is not None:
                try:
                    a, b = float(v1), float(v2)
                    if a != b:
                        better = max(a, b) if direction else min(a, b)
                        if float(v1) == better:
                            bg1 = _highlight
                        if float(v2) == better:
                            bg2 = _highlight
                except (ValueError, TypeError):
                    pass
            cols = st.columns([1, 2, 1])
            cols[0].markdown(f"<div style='text-align: center; {bg1}'>{v1}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div style='text-align: center;'>{metric}</div>", unsafe_allow_html=True)
            cols[2].markdown(f"<div style='text-align: center; {bg2}'>{v2}</div>", unsafe_allow_html=True)
        st.caption("Totals: matches, wins, draws, losses, goals, points. Averages: possession, shots, SOT, fouls (per-match). Highlighted = better value.")

with tab2:
    st.subheader("Player vs Player")
    player_names = sorted(player_stats["player_name"].unique())
    c1, c2 = st.columns(2)
    with c1: p1_name = st.selectbox("Player 1", player_names, key="u_p1")
    with c2: p2_name = st.selectbox("Player 2", player_names, key="u_p2")
    if st.button("Compare Players", type="primary", key="u_btn_p"):
        p1 = player_stats[player_stats["player_name"] == p1_name].iloc[0]
        p2 = player_stats[player_stats["player_name"] == p2_name].iloc[0]
        def p90(g, m):
            try:
                v = round(float(g) / float(m) * 90, 2) if float(m) else 0
                return int(v) if v == int(v) else v
            except (ValueError, TypeError):
                return 0
        def conv(g, s):
            try:
                v = round(float(g) / float(s) * 100, 1) if float(s) else 0
                return int(v) if v == int(v) else v
            except (ValueError, TypeError):
                return 0
        def _int(v):
            try:
                return int(v)
            except (ValueError, TypeError):
                return 0
        def _rating(r):
            return round(r, 2) if pd.notna(r) else "-"
        p_rows = ["Matches", "Minutes", "Goals", "Assists", "Goals/90", "Assists/90", "Shots", "SOT", "Shot Conv %", "Rating"]
        p1_vals = [_int(p1["matches_played"]), _int(p1["minutes_played"]), _int(p1["goals"]), _int(p1["assists"]),
                   p90(p1["goals"], p1["minutes_played"]), p90(p1["assists"], p1["minutes_played"]),
                   _int(p1["shots"]), _int(p1["shots_on_target"]), conv(p1["goals"], p1["shots_on_target"]),
                   _rating(p1["average_rating"])]
        p2_vals = [_int(p2["matches_played"]), _int(p2["minutes_played"]), _int(p2["goals"]), _int(p2["assists"]),
                   p90(p2["goals"], p2["minutes_played"]), p90(p2["assists"], p2["minutes_played"]),
                   _int(p2["shots"]), _int(p2["shots_on_target"]), conv(p2["goals"], p2["shots_on_target"]),
                   _rating(p2["average_rating"])]
        p_higher_better = {
            "Matches": True, "Minutes": True, "Goals": True, "Assists": True,
            "Goals/90": True, "Assists/90": True, "Shots": True, "SOT": True,
            "Shot Conv %": True, "Rating": True,
        }
        cols = st.columns([1, 2, 1])
        cols[0].markdown(f"<div style='text-align: center; font-weight: bold;'>{p1_name}</div>", unsafe_allow_html=True)
        cols[1].markdown("<div style='text-align: center; font-weight: bold;'>Metric</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div style='text-align: center; font-weight: bold;'>{p2_name}</div>", unsafe_allow_html=True)
        for i, metric in enumerate(p_rows):
            v1, v2 = p1_vals[i], p2_vals[i]
            direction = p_higher_better.get(metric)
            bg1 = bg2 = ""
            if direction is not None:
                try:
                    a, b = float(v1), float(v2)
                    if a != b:
                        better = max(a, b) if direction else min(a, b)
                        if float(v1) == better:
                            bg1 = _highlight
                        if float(v2) == better:
                            bg2 = _highlight
                except (ValueError, TypeError):
                    pass
            cols = st.columns([1, 2, 1])
            cols[0].markdown(f"<div style='text-align: center; {bg1}'>{v1}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div style='text-align: center;'>{metric}</div>", unsafe_allow_html=True)
            cols[2].markdown(f"<div style='text-align: center; {bg2}'>{v2}</div>", unsafe_allow_html=True)
        st.caption("Goals/90 are PER-90. Shot conv is a PERCENTAGE. Others are TOTALS.")

with tab3:
    st.subheader("Team vs Continent")
    summary = all_teams_summary(matches, team_stats, teams)
    if not summary.empty:
        team_names = sorted(summary["team_name"].unique())
        sel_team = st.selectbox("Team", team_names, key="u_tc_team")
        team_row = summary[summary["team_name"] == sel_team]
        if not team_row.empty:
            tr = team_row.iloc[0]
            confed = tr["confederation"]
            confed_avg = summary[summary["confederation"] == confed].mean(numeric_only=True)
            def _fmt2(v):
                try:
                    f = float(v)
                    return int(f) if f == int(f) else round(f, 1)
                except (ValueError, TypeError):
                    return v
            tc_rows = ["Points", "Goals For", "Goals Against", "GD", "Avg Possession", "Avg Shots/Match"]
            tc_team_vals = [_fmt2(tr["points"]), _fmt2(tr["goals_for"]), _fmt2(tr["goals_against"]),
                            _fmt2(tr["goal_difference"]), _fmt2(tr["avg_possession"]), _fmt2(tr["avg_shots"])]
            tc_confed_vals = [_fmt2(confed_avg["points"]), _fmt2(confed_avg["goals_for"]),
                              _fmt2(confed_avg["goals_against"]), _fmt2(confed_avg["goal_difference"]),
                              _fmt2(confed_avg["avg_possession"]), _fmt2(confed_avg["avg_shots"])]
            tc_higher_better = {
                "Points": True, "Goals For": True, "Goals Against": False,
                "GD": True, "Avg Possession": True, "Avg Shots/Match": True,
            }
            cols = st.columns([1, 2, 1])
            cols[0].markdown(f"<div style='text-align: center; font-weight: bold;'>{sel_team}</div>", unsafe_allow_html=True)
            cols[1].markdown("<div style='text-align: center; font-weight: bold;'>Metric</div>", unsafe_allow_html=True)
            cols[2].markdown(f"<div style='text-align: center; font-weight: bold;'>{confed} Avg</div>", unsafe_allow_html=True)
            for i, metric in enumerate(tc_rows):
                v1, v2 = tc_team_vals[i], tc_confed_vals[i]
                direction = tc_higher_better.get(metric)
                bg1 = bg2 = ""
                if direction is not None:
                    try:
                        a, b = float(v1), float(v2)
                        if a != b:
                            better = max(a, b) if direction else min(a, b)
                            if float(v1) == better:
                                bg1 = _highlight
                            if float(v2) == better:
                                bg2 = _highlight
                    except (ValueError, TypeError):
                        pass
                cols = st.columns([1, 2, 1])
                cols[0].markdown(f"<div style='text-align: center; {bg1}'>{v1}</div>", unsafe_allow_html=True)
                cols[1].markdown(f"<div style='text-align: center;'>{metric}</div>", unsafe_allow_html=True)
                cols[2].markdown(f"<div style='text-align: center; {bg2}'>{v2}</div>", unsafe_allow_html=True)
            st.caption("Points/goals are TOTALS; avg* are PER-MATCH AVERAGES.")
