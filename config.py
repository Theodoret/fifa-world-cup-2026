"""
Dashboard configuration and settings.
"""
import os
from pathlib import Path

# Project paths
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXTERNAL_DIR = DATA_DIR / "external"
DOCS_DIR = ROOT / "docs"

# App settings
APP_TITLE = "FIFA World Cup 2026 Analytics Dashboard"
APP_ICON = "⚽"
PAGE_ICONS = {
    "Home": "🏠",
    "01_Tournament": "🏆",
    "02_Matches": "📋",
    "03_Continents": "🌍",
    "04_Teams": "👥",
    "05_Players": "⭐",
    "06_Comparison": "⚖️",
    "07_Environmental": "🌡️",
    "08_Data_Explorer": "🔍",
}

NAVIGATION = [
    "01_Tournament.py",
    "02_Matches.py",
    "03_Continents.py",
    "04_Teams.py",
    "05_Players.py",
    "06_Comparison.py",
    "07_Environmental.py",
    "08_Data_Explorer.py",
]

# CSV files in raw data
RAW_CSV_FILES = [
    "matches.csv",
    "matches_detailed.csv",
    "match_events.csv",
    "match_lineups.csv",
    "match_team_stats.csv",
    "player_stats.csv",
    "referees.csv",
    "squads_and_players.csv",
    "teams.csv",
    "tournament_stages.csv",
    "venues.csv",
    "match_prediction_features.csv",
]

# Processing
RANDOM_SEED = 42