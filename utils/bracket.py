"""
Tournament bracket visualization — symmetric knockout bracket with SVG connectors.
"""
from __future__ import annotations

import html
import pandas as pd


ROUND_ORDER = [
    "Round of 32",
    "Round of 16",
    "Quarter-finals",
    "Semi-finals",
    "Final",
]

ROUND_LABELS = {
    "Round of 32": "Round of 32",
    "Round of 16": "Round of 16",
    "Quarter-finals": "Quarter-finals",
    "Semi-finals": "Semi-finals",
    "Final": "Final",
    "Third-place match": "3rd Place",
}

# Layout constants
COL_W = 164
COL_GAP = 40
FINAL_W = 180
CARD_H = 54
UNIT = 72
PAD_TOP = 40
PAD_X = 16


def _winner_side(match: pd.Series) -> str | None:
    hs = match.get("home_score")
    as_ = match.get("away_score")
    if pd.isna(hs) or pd.isna(as_):
        return None
    hs, as_ = int(hs), int(as_)
    if hs > as_:
        return "home"
    if as_ > hs:
        return "away"
    hp = match.get("home_penalty_score")
    ap = match.get("away_penalty_score")
    if pd.notna(hp) and pd.notna(ap):
        return "home" if int(hp) > int(ap) else "away"
    return None


def _winner_name(match: pd.Series) -> str | None:
    side = _winner_side(match)
    if side == "home":
        return str(match["home_name"])
    if side == "away":
        return str(match["away_name"])
    return None


def _short_name(name: str, max_len: int = 17) -> str:
    return name if len(name) <= max_len else name[: max_len - 1] + "…"


def _organize_knockout(matches: pd.DataFrame) -> tuple[dict[str, list[pd.Series]], pd.Series | None]:
    ko = matches[matches["is_knockout"] == True].copy()
    if ko.empty:
        return {}, None

    order_map = {n: i for i, n in enumerate(ROUND_ORDER + ["Third-place match"])}
    ko["round_order"] = ko["stage_name"].map(order_map)
    ko = ko.sort_values(["round_order", "match_id"]).reset_index(drop=True)

    rounds: dict[str, list[pd.Series]] = {}
    for rnd in ROUND_ORDER:
        rnd_df = ko[ko["stage_name"] == rnd]
        if not rnd_df.empty:
            rounds[rnd] = [row for _, row in rnd_df.iterrows()]

    third_df = ko[ko["stage_name"] == "Third-place match"]
    third_place = third_df.iloc[0] if not third_df.empty else None
    return rounds, third_place


def _y_center(round_idx: int, local_idx: int, leaf_count: int) -> float:
    """Vertical center for match local_idx within a side tree."""
    return (2 * local_idx + 1) * UNIT * (2 ** round_idx) / 2 + PAD_TOP


def _match_card(match: pd.Series, theme: dict, *, highlight: bool = False) -> str:
    winner = _winner_side(match)
    home = html.escape(_short_name(str(match["home_name"])))
    away = html.escape(_short_name(str(match["away_name"])))
    hs = "?" if pd.isna(match.get("home_score")) else int(match["home_score"])
    as_ = "?" if pd.isna(match.get("away_score")) else int(match["away_score"])
    card_cls = "bracket-match bracket-match--final" if highlight else "bracket-match"
    home_cls = "bracket-team bracket-team--winner" if winner == "home" else "bracket-team"
    away_cls = "bracket-team bracket-team--winner" if winner == "away" else "bracket-team"
    return (
        f'<div class="{card_cls}">'
        f'<div class="{home_cls}"><span class="bracket-team-name">{home}</span>'
        f'<span class="bracket-team-score">{hs}</span></div>'
        f'<div class="{away_cls}"><span class="bracket-team-name">{away}</span>'
        f'<span class="bracket-team-score">{as_}</span></div>'
        f"</div>"
    )


def _side_indices(rounds: dict[str, list[pd.Series]], side: str) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for rnd in ROUND_ORDER:
        if rnd not in rounds or rnd == "Final":
            continue
        n = len(rounds[rnd])
        half = n // 2
        if side == "left":
            out[rnd] = list(range(half))
        else:
            out[rnd] = list(range(n - 1, half - 1, -1))
    return out


def _h_connector(x0: float, y0: float, x1: float, y1: float) -> str:
    mid = (x0 + x1) / 2
    return (
        f'<path d="M {x0:.1f},{y0:.1f} H {mid:.1f} V {y1:.1f} H {x1:.1f}" '
        f'class="bracket-connector"/>'
    )


def build_bracket_html(
    matches: pd.DataFrame,
    teams: pd.DataFrame | None = None,
    theme: dict | None = None,
) -> str | None:
    """Build a symmetric HTML/SVG knockout bracket."""
    if theme is None:
        theme = {
            "bg_card": "#ffffff",
            "bg_subtle": "#fafafa",
            "text": "#09090b",
            "text_secondary": "#3f3f46",
            "text_muted": "#71717a",
            "border": "#e4e4e7",
            "border_subtle": "#d4d4d8",
            "accent": "#0891b2",
            "accent_soft": "rgba(8, 145, 178, 0.12)",
            "shadow_sm": "0 2px 8px rgba(0,0,0,0.04)",
        }

    rounds, third_place = _organize_knockout(matches)
    if not rounds or "Round of 32" not in rounds:
        return None

    leaf_count = len(rounds["Round of 32"]) // 2
    if leaf_count < 1:
        return None

    side_rounds = [r for r in ROUND_ORDER if r in rounds and r != "Final"]
    n_cols = len(side_rounds)
    side_height = leaf_count * UNIT

    left_idx = _side_indices(rounds, "left")
    right_idx = _side_indices(rounds, "right")

    left_width = n_cols * (COL_W + COL_GAP)
    final_x = PAD_X + left_width + COL_GAP
    right_start = final_x + FINAL_W + COL_GAP
    total_width = right_start + n_cols * (COL_W + COL_GAP) + PAD_X
    total_height = side_height + PAD_TOP + 180
    final_yc = PAD_TOP + side_height / 2

    cols_html: list[str] = []
    svg_parts: list[str] = []

    def render_side(side: str, x_start: float, indices: dict[str, list[int]], col_order: list[str]):
        for col_i, rnd in enumerate(col_order):
            if rnd not in indices:
                continue
            x = x_start + col_i * (COL_W + COL_GAP)
            round_idx = ROUND_ORDER.index(rnd)
            idx_list = indices[rnd]

            cards = [
                f'<div class="bracket-col-label">{ROUND_LABELS[rnd]}</div>'
            ]
            for local_j, match_idx in enumerate(idx_list):
                match = rounds[rnd][match_idx]
                yc = _y_center(round_idx, local_j, leaf_count)
                y = yc - CARD_H / 2
                cards.append(
                    f'<div class="bracket-slot" style="top:{y:.0f}px;">'
                    f"{_match_card(match, theme)}</div>"
                )

                if col_i < len(col_order) - 1:
                    next_rnd = col_order[col_i + 1]
                    next_round_idx = ROUND_ORDER.index(next_rnd)
                    next_local = local_j // 2
                    next_yc = _y_center(next_round_idx, next_local, leaf_count)
                    x_out = x + COL_W
                    x_in = x + COL_W + COL_GAP
                    if local_j % 2 == 0:
                        sib_yc = _y_center(round_idx, local_j + 1, leaf_count)
                        svg_parts.append(_h_connector(x_out, yc, x_in, next_yc))
                        mid = (x_out + x_in) / 2
                        svg_parts.append(
                            f'<path d="M {x_out:.1f},{sib_yc:.1f} H {mid:.1f}" class="bracket-connector"/>'
                        )

            cols_html.append(
                f'<div class="bracket-col" style="left:{x:.0f}px;width:{COL_W}px;">'
                f"{''.join(cards)}</div>"
            )

    render_side("left", PAD_X, left_idx, side_rounds)
    render_side("right", right_start, right_idx, list(reversed(side_rounds)))

    # SF → Final bridges
    if "Semi-finals" in rounds and "Final" in rounds:
        sf_round_idx = ROUND_ORDER.index("Semi-finals")
        sf_yc = _y_center(sf_round_idx, 0, leaf_count)
        sf_left_x = PAD_X + (n_cols - 1) * (COL_W + COL_GAP) + COL_W
        sf_right_x = right_start + COL_W
        svg_parts.append(
            f'<path d="M {sf_left_x:.1f},{sf_yc:.1f} H {final_x - 8:.1f} V {final_yc:.1f} H {final_x:.1f}" '
            f'class="bracket-connector bracket-connector--final"/>'
        )
        svg_parts.append(
            f'<path d="M {sf_right_x:.1f},{sf_yc:.1f} H {final_x + FINAL_W + 8:.1f} V {final_yc:.1f} H {final_x + FINAL_W:.1f}" '
            f'class="bracket-connector bracket-connector--final"/>'
        )

    # Final column
    final_y = final_yc - CARD_H / 2 - 8
    final_html = (
        f'<div class="bracket-col bracket-col--center" style="left:{final_x:.0f}px;width:{FINAL_W}px;">'
        f'<div class="bracket-col-label bracket-col-label--final">🏆 Final</div>'
    )
    if "Final" in rounds:
        fm = rounds["Final"][0]
        final_html += (
            f'<div class="bracket-slot" style="top:{final_y:.0f}px;">'
            f"{_match_card(fm, theme, highlight=True)}</div>"
        )
        champ = _winner_name(fm)
        if champ:
            final_html += (
                f'<div class="bracket-champion" style="top:{final_y + CARD_H + 8:.0f}px;">'
                f"Champion: <strong>{html.escape(champ)}</strong></div>"
            )
    final_html += "</div>"
    cols_html.append(final_html)

    if third_place is not None:
        tp_y = final_y + CARD_H + 52
        cols_html.append(
            f'<div class="bracket-third-label" style="left:{final_x:.0f}px;width:{FINAL_W}px;top:{tp_y - 20:.0f}px;">'
            f"{ROUND_LABELS['Third-place match']}</div>"
            f'<div class="bracket-col" style="left:{final_x:.0f}px;width:{FINAL_W}px;">'
            f'<div class="bracket-slot" style="top:{tp_y:.0f}px;">'
            f"{_match_card(third_place, theme)}</div></div>"
        )

    css = f"""
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: transparent;
        color: {theme['text']};
    }}
    .bracket-wrap {{
        width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        padding: 4px 0 8px;
        -webkit-overflow-scrolling: touch;
    }}
    .bracket-stage {{
        position: relative;
        width: {total_width:.0f}px;
        height: {total_height:.0f}px;
    }}
    .bracket-svg {{
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
    }}
    .bracket-connector {{
        fill: none;
        stroke: {theme['border_subtle']};
        stroke-width: 1.5;
        stroke-linecap: round;
        stroke-linejoin: round;
    }}
    .bracket-connector--final {{
        stroke: {theme['accent']};
        stroke-width: 2;
        opacity: 0.6;
    }}
    .bracket-col {{
        position: absolute;
        top: 0;
        height: 100%;
    }}
    .bracket-col--center {{ z-index: 2; }}
    .bracket-col-label {{
        position: absolute;
        top: 8px;
        left: 0; right: 0;
        text-align: center;
        font-size: 0.67rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: {theme['text_muted']};
        white-space: nowrap;
    }}
    .bracket-col-label--final {{
        color: {theme['accent']};
        font-size: 0.74rem;
    }}
    .bracket-third-label {{
        position: absolute;
        text-align: center;
        font-size: 0.64rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {theme['text_muted']};
    }}
    .bracket-slot {{
        position: absolute;
        left: 0; right: 0;
        height: {CARD_H}px;
    }}
    .bracket-match {{
        background: {theme['bg_card']};
        border: 1px solid {theme['border']};
        border-radius: 10px;
        overflow: hidden;
        box-shadow: {theme['shadow_sm']};
        height: 100%;
        display: flex;
        flex-direction: column;
    }}
    .bracket-match--final {{
        border-color: {theme['accent']};
        box-shadow: 0 0 0 3px {theme['accent_soft']}, {theme['shadow_sm']};
    }}
    .bracket-team {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 6px;
        padding: 0 10px;
        flex: 1;
        font-size: 0.77rem;
        color: {theme['text_secondary']};
        min-height: 0;
    }}
    .bracket-team + .bracket-team {{
        border-top: 1px solid {theme['border']};
    }}
    .bracket-team--winner {{
        background: {theme['accent_soft']};
        color: {theme['text']};
        font-weight: 600;
    }}
    .bracket-team--winner .bracket-team-score {{
        color: {theme['accent']};
        font-weight: 700;
    }}
    .bracket-team-name {{
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }}
    .bracket-team-score {{
        font-variant-numeric: tabular-nums;
        font-weight: 600;
        flex-shrink: 0;
    }}
    .bracket-champion {{
        position: absolute;
        left: 0; right: 0;
        text-align: center;
        font-size: 0.78rem;
        color: {theme['text_muted']};
    }}
    .bracket-champion strong {{ color: {theme['accent']}; }}
    """

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{css}</style></head>
<body>
<div class="bracket-wrap">
  <div class="bracket-stage">
    <svg class="bracket-svg" viewBox="0 0 {total_width:.0f} {total_height:.0f}" preserveAspectRatio="xMinYMin meet">
      {''.join(svg_parts)}
    </svg>
    {''.join(cols_html)}
  </div>
</div>
</body></html>"""


def bracket_height(matches: pd.DataFrame) -> int:
    rounds, third = _organize_knockout(matches)
    if not rounds or "Round of 32" not in rounds:
        return 420
    leaf = len(rounds["Round of 32"]) // 2
    h = leaf * UNIT + PAD_TOP + 160
    if third is not None:
        h += 90
    return max(500, min(h, 880))


def build_bracket(matches: pd.DataFrame, teams: pd.DataFrame | None = None, theme: dict | None = None):
    """Build bracket visualization. Returns HTML string or None."""
    return build_bracket_html(matches, teams, theme)
