from __future__ import annotations

from html import escape

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analyzer import format_duration
from heroes import get_hero_icon_url, get_hero_name
from models import Match, PlayerStats


def hero_stats_dataframe(stats: PlayerStats) -> pd.DataFrame:
    rows = [
        {
            "icon": get_hero_icon_url(hero.hero_id),
            "hero": get_hero_name(hero.hero_id),
            "games": hero.games,
            "wins": hero.wins,
            "losses": hero.losses,
            "winrate": round(hero.winrate, 1),
        }
        for hero in stats.top_heroes
    ]
    return pd.DataFrame(
        rows,
        columns=["icon", "hero", "games", "wins", "losses", "winrate"],
    )


def recent_matches_dataframe(matches: list[Match]) -> pd.DataFrame:
    rows = [
        {
            "match_id": match.match_id,
            "icon": get_hero_icon_url(match.hero_id),
            "hero": get_hero_name(match.hero_id),
            "duration": format_duration(match.duration),
            "result": "Win" if match.won else "Loss",
        }
        for match in matches
    ]
    return pd.DataFrame(
        rows,
        columns=["match_id", "icon", "hero", "duration", "result"],
    )


def _hero_cell(hero_name: str, icon_url: str | None) -> str:
    name = escape(hero_name)
    if not icon_url:
        return f'<span class="hero-name">{name}</span>'

    return (
        '<span class="hero-cell">'
        f'<img src="{escape(icon_url, quote=True)}" alt="" loading="lazy">'
        f'<span class="hero-name">{name}</span>'
        "</span>"
    )


def _table_html(headers: list[str], rows: list[list[str]]) -> str:
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    rows_html = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return (
        '<div class="data-table-wrap"><table class="data-table">'
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table></div>"
    )


def hero_stats_table_html(hero_stats: pd.DataFrame) -> str:
    rows = [
        [
            _hero_cell(row.hero, row.icon),
            str(row.games),
            str(row.wins),
            str(row.losses),
            f"{row.winrate:.1f}%",
        ]
        for row in hero_stats.itertuples(index=False)
    ]
    return _table_html(
        ["Герой", "Игр", "Побед", "Поражений", "Винрейт"],
        rows,
    )


def recent_matches_table_html(recent_matches: pd.DataFrame) -> str:
    rows = [
        [
            str(row.match_id),
            _hero_cell(row.hero, row.icon),
            escape(str(row.duration)),
            escape(str(row.result)),
        ]
        for row in recent_matches.itertuples(index=False)
    ]
    return _table_html(
        ["Match ID", "Герой", "Длительность", "Результат"],
        rows,
    )


def _add_hero_axis(figure: go.Figure, hero_stats: pd.DataFrame) -> None:
    figure.update_xaxes(showticklabels=False, title_text=None)
    for row in hero_stats.itertuples(index=False):
        if row.icon:
            figure.add_layout_image(
                source=row.icon,
                xref="x",
                yref="paper",
                x=row.hero,
                y=-0.08,
                sizex=0.58,
                sizey=0.12,
                xanchor="center",
                yanchor="top",
                layer="above",
            )
        figure.add_annotation(
            x=row.hero,
            y=-0.22,
            xref="x",
            yref="paper",
            text=escape(row.hero),
            showarrow=False,
            xanchor="center",
            yanchor="top",
            font=dict(size=11),
        )


def games_by_hero_chart(hero_stats: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        hero_stats,
        x="hero",
        y="games",
        color="games",
        color_continuous_scale=["#2b2d31", "#d65a4a"],
        labels={"hero": "Hero", "games": "Games"},
    )
    figure.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=8, r=8, t=12, b=92),
        xaxis=dict(type="category"),
    )
    _add_hero_axis(figure, hero_stats)
    return figure


def winrate_by_hero_chart(hero_stats: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        hero_stats,
        x="hero",
        y="winrate",
        color="winrate",
        color_continuous_scale=["#b94a48", "#e0a458", "#4c956c"],
        range_y=[0, 100],
        labels={"hero": "Hero", "winrate": "Winrate (%)"},
    )
    figure.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=8, r=8, t=12, b=92),
        xaxis=dict(type="category"),
    )
    _add_hero_axis(figure, hero_stats)
    return figure
