# FIFA World Cup 2026 Analytics Dashboard

Interactive Streamlit dashboard for exploring FIFA World Cup 2026 tournament data — matches, teams, players, continents, environmental factors, and more.

## Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Project structure

| Path | Description |
|------|-------------|
| `streamlit_app.py` | Cloud entry point |
| `app.py` | Navigation shell and sidebar |
| `views/` | Dashboard pages |
| `analytics/` | Metric and analysis logic |
| `utils/` | Loaders, styling, state |
| `data/raw/` | CSV datasets |

## Disclaimer
AI was used in this website production as follows:
- ChatGPT with GPT-5.6 Luna model for work plan planning
- Mystrial Vibe with DeepSeek V4 Flash 0423 model for plan execution
- Cursor with Cursor Grok 4.6, Composer 2.5, Opus 5, GPT-5.6 Sol, and Cursor Grok 4.5 for UI finalization and debugging
