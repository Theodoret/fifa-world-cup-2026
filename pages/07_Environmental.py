"""
Page 7: Environmental Analysis
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.loader import load_matches, load_venues, load_match_team_stats
from utils.preprocessing import clean_matches
from utils.styles import apply_custom_css
from utils.state import render_breadcrumbs
from utils.methodology import annotate_chart, render_metric_methodology
from analytics.environment_analysis import (venue_summary, elevation_analysis,
                                            venue_environment, climate_analysis,
                                            venue_climate_profile)

st.set_page_config(page_title="Environmental", page_icon="🌡️", layout="wide")
apply_custom_css()
render_breadcrumbs("Environmental")

st.markdown("<h1 class='main-header'>🌡️ Environmental Analysis</h1>", unsafe_allow_html=True)

matches = load_matches()
venues = load_venues()
team_stats = load_match_team_stats()
matches = clean_matches(matches)

st.info("Temperature and humidity data are NOT present in the raw dataset. Air pressure and oxygen availability are ESTIMATED from elevation using the ISA standard atmosphere model. Correlations shown are ASSOCIATIONS only — do not interpret as causation.")

st.subheader("Venue Environment Profile")
env = venue_environment(venues)
env_display = env[["stadium_name", "city", "country", "elevation_meters", "estimated_pressure_hpa", "estimated_oxygen_pct"]].copy()
env_display = env_display.rename(columns={
    "stadium_name": "Stadium",
    "city": "City",
    "country": "Country",
    "elevation_meters": "Elevation (m)",
    "estimated_pressure_hpa": "Est. Pressure (hPa)",
    "estimated_oxygen_pct": "Est. Oxygen (% sea level)",
})
st.dataframe(env_display, hide_index=True, width="stretch")
render_metric_methodology("estimated_air_pressure")
render_metric_methodology("estimated_oxygen_availability")

st.subheader("Climate Classification (by elevation)")
climate = venue_climate_profile(venues)
if not climate.empty:
    counts = climate["climate_class"].value_counts().reset_index()
    counts.columns = ["Climate Class", "Venues"]
    fig = px.bar(counts, x="Climate Class", y="Venues", color="Climate Class", title="Venues by Climate Class")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Elevation vs Match Outcomes")
elev_df = elevation_analysis(venues, matches)
if not elev_df.empty:
    elev_df["elevation_range"] = elev_df["avg_elevation"].apply(lambda x: f"{x:.0f}m" if pd.notna(x) else "N/A")
    fig = px.line(elev_df, x="elevation_range", y="avg_goals", markers=True, title="Average Goals by Elevation Bracket")
    st.plotly_chart(fig, use_container_width=True)
    annotate_chart("PER-MATCH AVERAGE goals per elevation bracket.")

st.subheader("Relationships: Environment vs Match Metrics")
rel = climate_analysis(venues, matches, team_stats)
if not rel.empty:
    metric = st.selectbox("Match metric", ["avg_possession", "avg_shots"], key="env_metric")
    fig = px.scatter(rel, x="avg_elevation", y=metric, color="stadium_name", hover_data=["city"], title=f"Venue Elevation vs {metric}")
    st.plotly_chart(fig, use_container_width=True)
    annotate_chart("Association only — NOT causation.")

st.subheader("Venue Summary")
ven_summary = venue_summary(venues, matches)
if not ven_summary.empty:
    ven_display = ven_summary.sort_values("matches_played", ascending=False)
    ven_display = ven_display.rename(columns={
        "stadium_name": "Stadium",
        "city": "City",
        "country": "Country",
        "matches_played": "Matches Played",
        "total_goals": "Total Goals",
    })
    st.dataframe(ven_display, hide_index=True, width="stretch")

st.subheader("Venue Locations")
try:
    import folium
    from streamlit_folium import st_folium
    m = folium.Map(location=[39.0, -98.5], zoom_start=4)
    for _, v in env.iterrows():
        if pd.notna(v.get("latitude")) and pd.notna(v.get("longitude")):
            popup = f"{v['stadium_name']}<br>Elev: {v['elevation_meters']}m<br>Est. O2: {v['estimated_oxygen_pct']:.1f}%"
            folium.Marker([v["latitude"], v["longitude"]], popup=popup, tooltip=v["stadium_name"],
                          icon=folium.Icon(icon="info-sign", prefix="glyphicon")).add_to(m)
    st_folium(m, width=1000, height=500)
except ImportError:
    st.info("Install folium and streamlit-folium for the venue map.")
