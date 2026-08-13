"""
Query-param-based drill-down navigation.

Replaces the session-state approach that leaked context across pages.
Each page reads its context from st.query_params at the top.
Navigation is done via st.page_link with query_params.
"""
import streamlit as st


def safe_page_link(page, label, query_params=None):
    """Render a page_link, falling back to plain text when the target page
    is not registered (e.g. running a page standalone in AppTest)."""
    try:
        return st.page_link(page, label=label, query_params=query_params or None,
                            width="stretch")
    except Exception:
        return st.write(label)


def get_param(key: str, default=None):
    """Read a query parameter value."""
    params = st.query_params
    if key in params:
        val = params[key]
        if isinstance(val, list):
            val = val[0]
        try:
            return int(val)
        except (ValueError, TypeError):
            return val
    return default


def set_params(**kwargs):
    """Set query parameters (appends to existing)."""
    params = st.query_params
    for key, value in kwargs.items():
        if value is not None:
            params[key] = str(value)
        elif key in params:
            del params[key]


def clear_params():
    """Clear all navigation-related query params."""
    for key in ["team_id", "team_name", "player_id", "player_name",
                "continent", "match_id", "group", "_from"]:
        if key in st.query_params:
            del st.query_params[key]


def get_root_section(page_name: str) -> str:
    """Return the root section for breadcrumbs — ``_from`` if set, else the current page."""
    from_page = get_param("_from")
    return from_page or page_name


# Map page names to their file paths for breadcrumb links
PAGE_FILE_MAP = {
    "Tournament": "views/01_Tournament.py",
    "Matches": "views/02_Matches.py",
    "Continents": "views/03_Continents.py",
    "Teams": "views/04_Teams.py",
    "Players": "views/05_Players.py",
    "Comparison": "views/06_Comparison.py",
    "Environmental": "views/07_Environmental.py",
    "Data Explorer": "views/08_Data_Explorer.py",
}

# Each page's primary drill-down param (used to detect stale _from)
_PRIMARY_PARAM = {
    "Tournament": None,
    "Matches": "match_id",
    "Continents": "continent",
    "Teams": "team_id",
    "Players": "player_id",
    "Comparison": None,
    "Environmental": None,
    "Data Explorer": None,
}


def render_breadcrumbs(page_name: str = "Tournament",
                       team_name_override=None, team_id_override=None,
                       player_name_override=None, player_id_override=None):
    """
    Render breadcrumb-style page links at the top of each page.

    The first crumb is the current page section (e.g. Tournament, Matches).
    When the user drills down via links that pass ``_from``, the root crumb
    stays on the origin section.  Clicking any crumb navigates to that page
    with only the params needed for that level.

    Sidebar navigation resets the breadcrumb to just the current section.

    Parameters
    ----------
    team_name_override, team_id_override :
        Live values from the page's selectbox widget, used instead of the
        (possibly stale) URL query params so the breadcrumb stays in sync.
    """
    # Detect stale _from — user navigated via sidebar but old query params
    # leaked into the URL.  If the current page's primary param is missing
    # the _from is stale and should be cleared.
    from_page = get_param("_from")
    if from_page:
        primary = _PRIMARY_PARAM.get(page_name)
        if primary is None or get_param(primary) is None:
            # Stale — user came via sidebar, reset everything
            clear_params()
            if "_from" in st.query_params:
                del st.query_params["_from"]
            from_page = None

    root = from_page or page_name
    root_file = PAGE_FILE_MAP.get(root, "views/01_Tournament.py")
    crumbs = [(root, root_file, {})]

    continent = get_param("continent")
    if continent:
        crumbs.append((f"🌍 {continent}", "views/03_Continents.py", {"continent": continent}))

    # Use live widget overrides when available (avoids stale URL on first interaction)
    team_id = team_id_override if team_id_override is not None else get_param("team_id")
    team_name = team_name_override or get_param("team_name")
    if team_name:
        crumbs.append((f"👥 {team_name}", "views/04_Teams.py",
                       {"team_id": team_id, "team_name": team_name}))

    player_id = player_id_override if player_id_override is not None else get_param("player_id")
    player_name = player_name_override or get_param("player_name")
    if player_name:
        crumbs.append((f"⭐ {player_name}", "views/05_Players.py",
                       {"player_id": player_id, "player_name": player_name}))

    match_id = get_param("match_id")
    if match_id:
        crumbs.append((f"📋 Match {match_id}", "views/02_Matches.py", {"match_id": match_id}))

    if len(crumbs) > 1:
        cols = st.columns(len(crumbs))
        for i, (label, page, params) in enumerate(crumbs):
            with cols[i]:
                safe_page_link(page, label, query_params=params)
        st.divider()
    return False


def team_link(team_name, team_id, from_page=None):
    """Build a page_link to the team page."""
    params = {"team_id": team_id, "team_name": team_name}
    if from_page:
        params["_from"] = from_page
    safe_page_link("views/04_Teams.py", team_name, query_params=params)


def player_link(player_name, player_id, from_page=None):
    """Build a page_link to the player page."""
    params = {"player_id": player_id, "player_name": player_name}
    if from_page:
        params["_from"] = from_page
    safe_page_link("views/05_Players.py", player_name, query_params=params)


def continent_link(continent, from_page=None):
    """Build a page_link to the continent page."""
    params = {"continent": continent}
    if from_page:
        params["_from"] = from_page
    safe_page_link("views/03_Continents.py", continent, query_params=params)


def match_link(match_id, label, from_page=None):
    """Build a page_link to the match page."""
    params = {"match_id": match_id}
    if from_page:
        params["_from"] = from_page
    safe_page_link("views/02_Matches.py", label, query_params=params)
