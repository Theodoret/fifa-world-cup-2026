# FIFA World Cup 2026 Analytics Dashboard

Interactive Streamlit dashboard for exploring FIFA World Cup 2026 tournament data — matches, teams, players, continents, environmental factors, and more.

## Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repository to [GitHub](https://github.com/Theodoret/fifa-world-cup-2026).
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and connect the repo.
3. Set **Main file path** to `streamlit_app.py`.
4. Deploy — data files under `data/raw/` are bundled in the repo.

## Project structure

| Path | Description |
|------|-------------|
| `streamlit_app.py` | Cloud entry point |
| `app.py` | Navigation shell and sidebar |
| `pages/` | Dashboard pages |
| `analytics/` | Metric and analysis logic |
| `utils/` | Loaders, styling, state |
| `data/raw/` | CSV datasets |
