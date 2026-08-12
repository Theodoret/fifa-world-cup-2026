"""
Page 3: Continent Analysis
Click any confederation name in the table to drill into its stats.
Radar chart vs tournament average, plus comparison to other confederations.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.loader import load_matches, load_teams, load_match_team_stats
from utils.styles import apply_custom_css, style_plotly_fig, get_theme_colors
from utils.state import render_breadcrumbs, get_param, set_params, safe_page_link
from utils.methodology import annotate_chart
from analytics.continent_analysis import continent_summary, continent_best_performers

st.set_page_config(page_title="Continents", page_icon="🌍", layout="wide")
apply_custom_css()
render_breadcrumbs("Continents")

st.markdown("<h1 class='main-header'>🌍 Continent Analysis</h1>", unsafe_allow_html=True)

matches = load_matches()
teams = load_teams()
team_stats = load_match_team_stats()

conf_df = continent_summary(teams, matches, team_stats)
if conf_df.empty:
    st.info("No continent data available.")
    st.stop()

# --- Summary table with clickable confederation names ---
st.subheader("Confederation Overview")
col_ratios = [1.5] + [1] * (len(conf_df.columns) - 1)
headers = list(conf_df.columns)
# Header row
cols = st.columns(col_ratios)
for i, h in enumerate(headers):
    cols[i].markdown(f"**{h.replace('_', ' ').title()}**")
# Data rows
for _, row in conf_df.iterrows():
    vals = row.tolist()
    cols = st.columns(col_ratios)
    for i, v in enumerate(vals):
        with cols[i]:
            if i == 0:
                safe_page_link("pages/03_Continents.py", f"🌍 {v}",
                               query_params={"continent": v})
            elif isinstance(v, float):
                st.write(f"{v:.1f}")
            else:
                st.write(str(v))

# --- Selected confederation drill-down ---
sel_confed = get_param("continent")
if sel_confed and sel_confed in conf_df["confederation"].values:
    st.subheader(f"🌍 {sel_confed}")

    # Radar chart: selected confederation vs tournament average
    radar_metrics = ["avg_possession", "avg_shots", "win_rate", "goal_difference", "total_wins", "total_points"]
    radar_labels = ["Avg Possession", "Avg Shots", "Win Rate", "Goal Diff", "Total Wins", "Total Points"]

    sel_row = conf_df[conf_df["confederation"] == sel_confed].iloc[0]
    tourn_avg = {m: conf_df[m].mean() for m in radar_metrics}

    # Normalize 0-100 for the radar
    def normalize(val, min_val, max_val):
        if max_val == min_val:
            return 50
        return (val - min_val) / (max_val - min_val) * 100

    radar_ranges = {m: (conf_df[m].min(), conf_df[m].max()) for m in radar_metrics}
    sel_values = [normalize(sel_row[m], *radar_ranges[m]) for m in radar_metrics]
    avg_values = [normalize(tourn_avg[m], *radar_ranges[m]) for m in radar_metrics]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=sel_values + [sel_values[0]],
                                  theta=radar_labels + [radar_labels[0]],
                                  fill='toself', name=sel_confed))
    fig.add_trace(go.Scatterpolar(r=avg_values + [avg_values[0]],
                                  theta=radar_labels + [radar_labels[0]],
                                  fill='toself', name="Tournament Avg"))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True, height=450
    )
    st.plotly_chart(style_plotly_fig(fig), width="stretch")
    annotate_chart("Radar values NORMALIZED 0-100 across all confederations (min-max).")

    # Raw values table
    raw_data = pd.DataFrame({
        "Metric": radar_labels,
        sel_confed: [sel_row[m] for m in radar_metrics],
        "Tournament Avg": [round(tourn_avg[m], 2) for m in radar_metrics],
    })
    st.dataframe(raw_data, hide_index=True, width="stretch")

    # Teams in this confederation
    st.subheader(f"Teams in {sel_confed}")
    best = continent_best_performers(teams, matches, team_stats, sel_confed)
    if not best.empty:
        for _, row in best.iterrows():
            safe_page_link("pages/04_Teams.py", f"👥 {row['team_name']}",
                         query_params={"team_id": row["team_id"], "team_name": row["team_name"],
                                       "continent": sel_confed, "_from": "Continents"})

# --- Metric comparison across all confederations (always visible) ---
st.subheader("Metric Comparison")
radar_metrics = ["avg_possession", "avg_shots", "win_rate", "goal_difference", "total_wins", "total_points"]
metric = st.selectbox("Metric", radar_metrics,
                      format_func=lambda x: x.replace("_", " ").title(),
                      key="conf_metric")
fig2 = px.bar(conf_df, x="confederation", y=metric, color="confederation",
              title=f"{metric.replace('_', ' ').title()} by Confederation",
              labels={metric: metric.replace("_", " ").title()})
fig2.update_layout(showlegend=False)
# Highlight the selected confederation (if any)
tc = get_theme_colors()
colors = [tc["accent"] if c == sel_confed else tc["text_muted"] for c in conf_df["confederation"]]
fig2.update_traces(marker_color=colors)
st.plotly_chart(style_plotly_fig(fig2), width="stretch")
annotate_chart("Selected confederation is highlighted in blue.")
