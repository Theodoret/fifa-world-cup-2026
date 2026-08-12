"""
CSS and theming for the dashboard.
Dark/light mode toggle via session state.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio


def is_dark_mode() -> bool:
    return st.session_state.get("dark_mode", False)


def get_theme_colors() -> dict:
    """Return the active theme palette for use in inline HTML / charts."""
    if is_dark_mode():
        return {
            "bg": "#09090b",
            "bg_elevated": "#111114",
            "bg_card": "#18181b",
            "bg_hover": "#27272a",
            "bg_subtle": "#1c1c1f",
            "text": "#fafafa",
            "text_secondary": "#d4d4d8",
            "text_muted": "#71717a",
            "border": "#27272a",
            "border_subtle": "#3f3f46",
            "accent": "#22d3ee",
            "accent_hover": "#06b6d4",
            "accent_soft": "rgba(34, 211, 238, 0.12)",
            "accent_gradient": "linear-gradient(135deg, #22d3ee 0%, #6366f1 100%)",
            "success": "#4ade80",
            "warning": "#fbbf24",
            "danger": "#f87171",
            "home": "#38bdf8",
            "away": "#fb7185",
            "shadow": "0 4px 24px rgba(0, 0, 0, 0.45)",
            "shadow_sm": "0 2px 8px rgba(0, 0, 0, 0.35)",
            "plotly_template": "fifa_dark",
        }
    return {
        "bg": "#f4f4f5",
        "bg_elevated": "#ffffff",
        "bg_card": "#ffffff",
        "bg_hover": "#f4f4f5",
        "bg_subtle": "#fafafa",
        "text": "#09090b",
        "text_secondary": "#3f3f46",
        "text_muted": "#71717a",
        "border": "#e4e4e7",
        "border_subtle": "#d4d4d8",
        "accent": "#0891b2",
        "accent_hover": "#0e7490",
        "accent_soft": "rgba(8, 145, 178, 0.10)",
        "accent_gradient": "linear-gradient(135deg, #0891b2 0%, #6366f1 100%)",
        "success": "#16a34a",
        "warning": "#d97706",
        "danger": "#dc2626",
        "home": "#0284c7",
        "away": "#e11d48",
        "shadow": "0 4px 24px rgba(0, 0, 0, 0.06)",
        "shadow_sm": "0 2px 8px rgba(0, 0, 0, 0.04)",
        "plotly_template": "fifa_light",
    }


def _register_plotly_templates():
    """Register custom Plotly templates aligned with the dashboard palette."""
    light = {
        "text": "#09090b", "text_muted": "#71717a", "border": "#e4e4e7",
    }
    dark = {
        "text": "#fafafa", "text_muted": "#71717a", "border": "#27272a",
    }

    axis_style = lambda pal: dict(
        gridcolor=pal["border"],
        linecolor=pal["border"],
        tickfont=dict(color=pal["text_muted"]),
    )
    polar_style = lambda pal: dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(
            gridcolor=pal["border"],
            linecolor=pal["border"],
            tickfont=dict(color=pal["text_muted"]),
        ),
        angularaxis=dict(
            gridcolor=pal["border"],
            linecolor=pal["border"],
            tickfont=dict(color=pal["text"]),
        ),
    )

    pio.templates["fifa_light"] = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color=light["text"], size=13),
            colorway=["#0891b2", "#6366f1", "#8b5cf6", "#ec4899", "#f59e0b",
                      "#10b981", "#ef4444", "#06b6d4"],
            xaxis=axis_style(light),
            yaxis=axis_style(light),
            polar=polar_style(light),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=light["text"])),
            margin=dict(l=40, r=20, t=50, b=40),
        )
    )
    pio.templates["fifa_dark"] = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color=dark["text"], size=13),
            colorway=["#22d3ee", "#818cf8", "#a78bfa", "#f472b6", "#fbbf24",
                      "#4ade80", "#f87171", "#38bdf8"],
            xaxis=axis_style(dark),
            yaxis=axis_style(dark),
            polar=polar_style(dark),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=dark["text"])),
            margin=dict(l=40, r=20, t=50, b=40),
        )
    )


def style_plotly_fig(fig):
    """Apply the active dashboard theme to a Plotly figure."""
    c = get_theme_colors()
    _register_plotly_templates()
    fig.update_layout(
        template=c["plotly_template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=c["text"]),
        title_font=dict(color=c["text"]),
        legend=dict(font=dict(color=c["text"])),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                gridcolor=c["border"],
                linecolor=c["border_subtle"],
                tickfont=dict(color=c["text_muted"]),
            ),
            angularaxis=dict(
                gridcolor=c["border"],
                linecolor=c["border_subtle"],
                tickfont=dict(color=c["text_secondary"]),
            ),
        ),
    )
    return fig


def apply_custom_css():
    """Inject a modern CSS design system with dark/light mode support."""
    c = get_theme_colors()
    is_dark = is_dark_mode()

    _register_plotly_templates()
    pio.templates.default = c["plotly_template"]

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ─── Design tokens ─── */
    :root {{
        --bg: {c['bg']};
        --bg-elevated: {c['bg_elevated']};
        --bg-card: {c['bg_card']};
        --bg-hover: {c['bg_hover']};
        --bg-subtle: {c['bg_subtle']};
        --text: {c['text']};
        --text-secondary: {c['text_secondary']};
        --text-muted: {c['text_muted']};
        --border: {c['border']};
        --border-subtle: {c['border_subtle']};
        --accent: {c['accent']};
        --accent-hover: {c['accent_hover']};
        --accent-soft: {c['accent_soft']};
        --accent-gradient: {c['accent_gradient']};
        --success: {c['success']};
        --warning: {c['warning']};
        --danger: {c['danger']};
        --shadow: {c['shadow']};
        --shadow-sm: {c['shadow_sm']};
        --radius: 14px;
        --radius-sm: 10px;
        --radius-xs: 6px;
        --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --transition: 0.18s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* ─── Base ─── */
    .stApp {{
        background: var(--bg);
        color: var(--text);
        font-family: var(--font);
    }}
    .stApp > header {{
        background: var(--bg-elevated) !important;
        border-bottom: 1px solid var(--border) !important;
    }}
    .block-container {{
        padding-top: 2rem !important;
        max-width: 1400px;
    }}
    p, li, span, label {{
        color: var(--text-secondary);
    }}

    /* ─── Sidebar ─── */
    section[data-testid="stSidebar"] {{
        background: var(--bg-elevated) !important;
        border-right: 1px solid var(--border) !important;
    }}
    section[data-testid="stSidebar"] > div {{
        background: var(--bg-elevated) !important;
    }}
    .sidebar-brand {{
        padding: 1.25rem 1rem 1rem;
        margin-bottom: 0.25rem;
    }}
    .sidebar-brand-icon {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.25rem;
        height: 2.25rem;
        border-radius: var(--radius-sm);
        background: var(--accent-soft);
        font-size: 1.15rem;
        margin-bottom: 0.65rem;
    }}
    .sidebar-brand-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.02em;
        line-height: 1.3;
    }}
    .sidebar-brand-sub {{
        font-size: 0.72rem;
        font-weight: 500;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.2rem;
    }}
    .sidebar-nav-label {{
        font-size: 0.68rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 0.75rem 1rem 0.35rem;
    }}
    .sidebar-footer {{
        margin-top: auto;
        padding: 0.75rem 0.5rem 1rem;
        border-top: 1px solid var(--border);
    }}

    /* Sidebar nav links */
    section[data-testid="stSidebar"] [data-testid="stPageLink"] {{
        margin: 0.15rem 0.5rem;
    }}
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a {{
        display: block;
        padding: 0.55rem 0.85rem !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        text-decoration: none !important;
        border: 1px solid transparent !important;
        transition: all var(--transition) !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{
        background: var(--bg-hover) !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stPageLink-Active"] a,
    section[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] a {{
        background: var(--accent-soft) !important;
        color: var(--accent) !important;
        border-color: transparent !important;
        font-weight: 600 !important;
    }}

    /* Theme toggle button */
    section[data-testid="stSidebar"] .stButton button[key="theme_btn"],
    section[data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border) !important;
        background: var(--bg-subtle) !important;
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 1rem !important;
        transition: all var(--transition) !important;
    }}
    section[data-testid="stSidebar"] .stButton button:hover {{
        background: var(--bg-hover) !important;
        border-color: var(--accent) !important;
        color: var(--text) !important;
    }}

    /* ─── Page headers ─── */
    .main-header {{
        font-size: 1.85rem;
        font-weight: 800;
        margin: 0 0 0.25rem;
        color: var(--text);
        letter-spacing: -0.03em;
        line-height: 1.2;
    }}
    .page-subtitle {{
        font-size: 0.95rem;
        color: var(--text-muted);
        margin-bottom: 1.5rem;
        font-weight: 400;
    }}
    h1, h2, h3, h4 {{
        color: var(--text) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }}
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: var(--text) !important;
    }}
    [data-testid="stHeadingWithActionElements"] {{
        color: var(--text) !important;
    }}

    /* ─── Metric cards ─── */
    div[data-testid="stMetric"] {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.1rem 1.25rem;
        box-shadow: var(--shadow-sm);
        transition: transform var(--transition), box-shadow var(--transition),
                    border-color var(--transition);
        position: relative;
        overflow: hidden;
    }}
    div[data-testid="stMetric"]::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--accent-gradient);
        opacity: 0.85;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow);
        border-color: var(--border-subtle);
    }}
    div[data-testid="stMetric"] label {{
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: var(--text) !important;
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {{
        font-weight: 500 !important;
    }}

    /* ─── Glide Data Grid (st.dataframe) ─── */
    /* Streamlit sets inline --gdg-* vars with light defaults; !important overrides them */
    .stApp,
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] > div,
    [data-testid="stDataFrame"] [class*="gdg"] {{
        --gdg-bg-cell: {c['bg_card']} !important;
        --gdg-bg-cell-medium: {c['bg_subtle']} !important;
        --gdg-bg-header: {c['bg_subtle']} !important;
        --gdg-bg-header-hovered: {c['bg_hover']} !important;
        --gdg-bg-header-has-focus: {c['bg_hover']} !important;
        --gdg-bg-group-header: {c['bg_subtle']} !important;
        --gdg-bg-group-header-hovered: {c['bg_hover']} !important;
        --gdg-bg-icon-header: {c['bg_subtle']} !important;
        --gdg-bg-bubble: {c['bg_hover']} !important;
        --gdg-bg-bubble-selected: {c['accent_soft']} !important;
        --gdg-bg-search-result: {c['accent_soft']} !important;
        --gdg-text-dark: {c['text']} !important;
        --gdg-text-medium: {c['text_secondary']} !important;
        --gdg-text-light: {c['text_muted']} !important;
        --gdg-text-header: {c['text_secondary']} !important;
        --gdg-text-header-selected: {c['accent']} !important;
        --gdg-text-group-header: {c['text_muted']} !important;
        --gdg-text-bubble: {c['text']} !important;
        --gdg-border-color: {c['border']} !important;
        --gdg-horizontal-border-color: {c['border']} !important;
        --gdg-header-bottom-border-color: {c['border']} !important;
        --gdg-drilldown-border: {c['border_subtle']} !important;
        --gdg-accent-color: {c['accent']} !important;
        --gdg-accent-light: {c['accent_soft']} !important;
        --gdg-accent-fg: {c['text']} !important;
        --gdg-link-color: {c['accent']} !important;
        --gdg-fg-icon-header: {c['text_muted']} !important;
        --gdg-resize-indicator-color: {c['accent']} !important;
    }}
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] > div,
    [data-testid="stDataFrame"] [class*="gdg-wmyidgi"],
    [data-testid="stDataFrame"] [class*="gdg-s1dgczr6"] {{
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        overflow: hidden !important;
        background: var(--bg-card) !important;
        background-color: var(--bg-card) !important;
        box-shadow: var(--shadow-sm);
        color: var(--text-secondary) !important;
    }}
    [data-testid="stDataFrame"] canvas {{
        background: transparent !important;
    }}

    /* Legacy table fallback */
    [data-testid="stTable"] {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }}
    [data-testid="stTable"] table {{
        background: var(--bg-card) !important;
        color: var(--text-secondary) !important;
    }}
    [data-testid="stTable"] th {{
        background: var(--bg-subtle) !important;
        color: var(--text-muted) !important;
    }}
    [data-testid="stTable"] td {{
        color: var(--text-secondary) !important;
        border-color: var(--border) !important;
    }}

    /* ─── Widget labels ─── */
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {{
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }}

    /* ─── Inputs & filters ─── */
    /* Streamlit 1.61+ selectbox (emotion-based, not baseweb) */
    [data-testid="stSelectbox"] div:has(> input),
    .stSelectbox div:has(> input) {{
        background-color: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
    }}
    [data-testid="stSelectbox"] button,
    .stSelectbox button {{
        color: var(--text-muted) !important;
        background: transparent !important;
    }}
    [data-testid="stSelectbox"] input,
    .stSelectbox input {{
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        background: transparent !important;
    }}
    [data-testid="stSelectbox"] input::placeholder,
    .stSelectbox input::placeholder {{
        color: var(--text-muted) !important;
        -webkit-text-fill-color: var(--text-muted) !important;
    }}
    [data-testid="stSelectboxVirtualDropdown"],
    [data-testid="stMultiSelectVirtualDropdown"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        box-shadow: var(--shadow) !important;
        color: var(--text-secondary) !important;
    }}
    [data-testid="stSelectboxVirtualDropdown"] [role="listbox"],
    [data-testid="stSelectboxVirtualDropdown"] ul,
    [data-testid="stMultiSelectVirtualDropdown"] [role="listbox"],
    [data-testid="stMultiSelectVirtualDropdown"] ul {{
        background-color: var(--bg-card) !important;
        color: var(--text-secondary) !important;
    }}
    [data-testid="stSelectboxVirtualDropdown"] [role="option"],
    [data-testid="stMultiSelectVirtualDropdown"] [role="option"] {{
        color: var(--text-secondary) !important;
        background: transparent !important;
    }}
    [data-testid="stSelectboxVirtualDropdown"] [data-hovered],
    [data-testid="stSelectboxVirtualDropdown"] [data-focused],
    [data-testid="stMultiSelectVirtualDropdown"] [data-hovered],
    [data-testid="stMultiSelectVirtualDropdown"] [data-focused] {{
        background-color: var(--bg-hover) !important;
        color: var(--text) !important;
    }}
    [data-testid="stSelectboxVirtualDropdown"] [data-item-hl],
    [data-testid="stMultiSelectVirtualDropdown"] [data-item-hl] {{
        background-color: var(--accent-soft) !important;
    }}

    /* Legacy baseweb widgets */
    .stSelectbox [data-baseweb="select"] > div,
    .stMultiSelect [data-baseweb="select"] > div,
    .stTextInput > div > div,
    .stNumberInput > div > div,
    .stDateInput > div > div,
    .stTimeInput > div > div {{
        border-radius: var(--radius-sm) !important;
        border-color: var(--border) !important;
        background-color: var(--bg-card) !important;
        background: var(--bg-card) !important;
        transition: border-color var(--transition), box-shadow var(--transition) !important;
    }}
    .stSelectbox [data-baseweb="select"] span,
    .stMultiSelect [data-baseweb="select"] span,
    .stTextInput input,
    .stNumberInput input {{
        color: var(--text) !important;
        font-size: 0.875rem !important;
        background: transparent !important;
        -webkit-text-fill-color: var(--text) !important;
    }}
    .stSelectbox svg,
    .stMultiSelect svg,
    .stDateInput svg {{
        fill: var(--text-muted) !important;
    }}
    .stSelectbox [data-baseweb="select"]:hover > div,
    .stMultiSelect [data-baseweb="select"]:hover > div,
    .stTextInput > div > div:focus-within,
    .stNumberInput > div > div:focus-within,
    .stDateInput > div > div:focus-within {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-soft) !important;
    }}

    /* Dropdown menus (portaled) */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[role="listbox"],
    ul[role="menu"] {{
        background-color: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text-secondary) !important;
    }}
    li[role="option"],
    li[role="menuitem"],
    li[role="menuitemcheckbox"] {{
        color: var(--text-secondary) !important;
        background-color: var(--bg-card) !important;
    }}
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"],
    li[role="menuitem"]:hover,
    li[role="menuitemcheckbox"]:hover {{
        background-color: var(--bg-hover) !important;
        color: var(--text) !important;
    }}
    [data-baseweb="tag"] {{
        background-color: var(--accent-soft) !important;
        color: var(--accent) !important;
        border-color: transparent !important;
    }}
    [data-baseweb="tag"] span {{
        color: var(--accent) !important;
    }}

    /* Slider */
    .stSlider [data-baseweb="slider"] [role="slider"] {{
        background: var(--accent) !important;
    }}
    .stSlider [data-baseweb="slider"] div {{
        background: var(--bg-hover) !important;
    }}
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {{
        color: var(--text-muted) !important;
    }}

    /* Checkbox & radio */
    .stCheckbox label span,
    .stRadio label span {{
        color: var(--text-secondary) !important;
    }}
    .stCheckbox [data-baseweb="checkbox"],
    .stRadio [data-baseweb="radio"] {{
        border-color: var(--border-subtle) !important;
        background: var(--bg-card) !important;
    }}

    /* Disabled inputs */
    .stSelectbox [data-baseweb="select"][aria-disabled="true"] > div,
    .stMultiSelect [data-baseweb="select"][aria-disabled="true"] > div {{
        background: var(--bg-subtle) !important;
        opacity: 0.7;
    }}

    /* ─── Buttons ─── */
    .stButton > button {{
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 1.1rem !important;
        transition: all var(--transition) !important;
        border: 1px solid var(--border) !important;
        background: var(--bg-card) !important;
        color: var(--text-secondary) !important;
    }}
    .stButton > button:hover {{
        background: var(--bg-hover) !important;
        border-color: var(--accent) !important;
        color: var(--text) !important;
        box-shadow: var(--shadow-sm);
    }}
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {{
        background: var(--accent) !important;
        color: {'#09090b' if is_dark else '#ffffff'} !important;
        border: none !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: var(--accent-hover) !important;
        opacity: 1 !important;
    }}

    /* ─── Tabs (pill style) ─── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.35rem;
        background: var(--bg-subtle);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 0.3rem;
        border-bottom: none;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: var(--text-muted) !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 0.45rem 1rem !important;
        border-radius: var(--radius-xs) !important;
        border: none !important;
        background: transparent !important;
        transition: all var(--transition) !important;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: var(--text) !important;
        background: var(--bg-hover) !important;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: var(--accent) !important;
        background: var(--bg-card) !important;
        box-shadow: var(--shadow-sm);
        font-weight: 600 !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        padding-top: 1.25rem;
    }}

    /* ─── Alerts ─── */
    [data-testid="stAlert"] {{
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border) !important;
        background: var(--bg-card) !important;
    }}
    [data-testid="stAlert"] [data-baseweb="notification"] {{
        background: var(--accent-soft) !important;
        color: var(--text) !important;
    }}

    /* ─── Expanders ─── */
    .streamlit-expanderHeader {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text) !important;
        font-weight: 500 !important;
        transition: background var(--transition) !important;
    }}
    .streamlit-expanderHeader:hover {{
        background: var(--bg-hover) !important;
        border-color: var(--border-subtle) !important;
    }}
    .streamlit-expanderContent {{
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
        background: var(--bg-subtle) !important;
    }}

    /* ─── Match page cards (theme-aware via classes) ─── */
    .match-info-bar {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        color: var(--text);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        box-shadow: var(--shadow-sm);
    }}
    .match-info-bar span.label {{
        color: var(--text-muted);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .match-info-bar strong {{
        color: var(--text);
        font-weight: 600;
    }}

    /* ─── Dividers & captions ─── */
    hr {{
        border-color: var(--border) !important;
        margin: 1.5rem 0 !important;
    }}
    .stCaption, [data-testid="stCaptionContainer"] {{
        color: var(--text-muted) !important;
        font-size: 0.8rem !important;
    }}

    /* ─── Breadcrumbs ─── */
    [data-testid="stPageLink"] a {{
        color: var(--accent) !important;
        font-weight: 500 !important;
        text-decoration: none !important;
        transition: opacity var(--transition);
    }}
    [data-testid="stPageLink"] a:hover {{
        opacity: 0.8;
        text-decoration: underline !important;
    }}

    /* ─── Plotly ─── */
    .js-plotly-plot .plotly .main-svg,
    .js-plotly-plot .plotly .bg {{
        background: transparent !important;
    }}
    .js-plotly-plot .plotly .legend {{
        background: transparent !important;
    }}
    .js-plotly-plot .plotly .angularaxis line,
    .js-plotly-plot .plotly .radialaxis line {{
        stroke: var(--border-subtle) !important;
    }}
    .js-plotly-plot .plotly .angularaxis text,
    .js-plotly-plot .plotly .radialaxis text {{
        fill: var(--text-muted) !important;
    }}

    /* ─── Scrollbar ─── */
    ::-webkit-scrollbar {{
        width: 5px;
        height: 5px;
    }}
    ::-webkit-scrollbar-track {{
        background: transparent;
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border-subtle);
        border-radius: 99px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--text-muted);
    }}

    /* Hide Streamlit chrome for cleaner look */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)


def render_theme_toggle():
    """Render a dark/light mode toggle in the sidebar."""
    is_dark = is_dark_mode()
    icon = "🌙" if not is_dark else "☀️"
    label = "Dark mode" if not is_dark else "Light mode"

    if st.button(f"{icon}  {label}", key="theme_btn", use_container_width=True):
        st.session_state.dark_mode = not is_dark
        st.rerun()
