from __future__ import annotations

import streamlit as st

from analyzer import analyze_matches, format_duration
from api_client import get_recent_matches
from models import Match, PlayerStats, parse_matches
from storage import (
    load_raw_matches,
    save_analysis_csv,
    save_analysis_json,
    save_raw_matches,
)
from ui_helpers import (
    games_by_hero_chart,
    hero_stats_dataframe,
    hero_stats_table_html,
    recent_matches_dataframe,
    recent_matches_table_html,
    winrate_by_hero_chart,
)
from utils.exceptions import DataLoadError, OpenDotaAPIError

SAVE_OPTIONS = {
    "Не сохранять": None,
    "JSON": "json",
    "CSV": "csv",
    "JSON и CSV": "both",
}

PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "doubleClick": "reset+autosize",
    "responsive": True,
}

TABLE_STYLES = """
<style>
.data-table-wrap {
    width: 100%;
    overflow-x: auto;
    border: 1px solid rgba(128, 128, 128, 0.24);
    border-radius: 6px;
}
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}
.data-table th {
    background: rgba(128, 128, 128, 0.10);
    color: rgba(250, 250, 250, 0.65);
    font-weight: 500;
    text-align: left;
}
.data-table th,
.data-table td {
    min-width: 110px;
    padding: 0.55rem 0.65rem;
    border-bottom: 1px solid rgba(128, 128, 128, 0.20);
    vertical-align: middle;
}
.data-table tr:last-child td {
    border-bottom: 0;
}
.data-table td:not(:first-child) {
    text-align: right;
}
.data-table td:has(.hero-cell),
.data-table td:has(.hero-name) {
    text-align: left;
}
.hero-cell {
    display: inline-flex;
    align-items: center;
    gap: 0.65rem;
    min-width: 0;
}
.hero-cell img {
    width: 48px;
    height: 28px;
    flex: 0 0 auto;
    object-fit: cover;
    border-radius: 3px;
}
.hero-name {
    color: inherit;
    white-space: nowrap;
}
</style>
"""


def fetch_matches(account_id: int, limit: int) -> tuple[list[dict], bool]:
    try:
        raw_matches = get_recent_matches(account_id, limit)
        if not raw_matches:
            return [], False
        save_raw_matches(account_id, raw_matches)
        return raw_matches, False
    except OpenDotaAPIError:
        cached_matches = load_raw_matches(account_id)
        return cached_matches[:limit], True


def save_results(account_id: int, stats: PlayerStats, save_format: str | None) -> list:
    paths = []
    if save_format in ("json", "both"):
        paths.append(save_analysis_json(account_id, stats))
    if save_format in ("csv", "both"):
        paths.append(save_analysis_csv(account_id, stats))
    return paths


def display_metrics(stats: PlayerStats) -> None:
    columns = st.columns(5)
    columns[0].metric("Матчи", stats.total_matches)
    columns[1].metric("Победы", stats.wins)
    columns[2].metric("Поражения", stats.losses)
    columns[3].metric("Винрейт", f"{stats.winrate:.1f}%")
    columns[4].metric(
        "Средняя длительность",
        format_duration(round(stats.average_duration)),
    )


def display_analysis(matches: list[Match], stats: PlayerStats) -> None:
    display_metrics(stats)

    hero_table = hero_stats_dataframe(stats)
    recent_table = recent_matches_dataframe(matches)

    st.subheader("Топ героев")
    st.markdown(hero_stats_table_html(hero_table), unsafe_allow_html=True)

    chart_columns = st.columns(2)
    with chart_columns[0]:
        st.subheader("Количество игр по героям")
        st.plotly_chart(
            games_by_hero_chart(hero_table),
            width="stretch",
            config=PLOTLY_CONFIG,
        )
    with chart_columns[1]:
        st.subheader("Винрейт по героям")
        st.plotly_chart(
            winrate_by_hero_chart(hero_table),
            width="stretch",
            config=PLOTLY_CONFIG,
        )

    st.subheader("Последние матчи")
    st.markdown(recent_matches_table_html(recent_table), unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="Dota 2 Match Analyzer",
        layout="wide",
    )

    st.title("Dota 2 Match Analyzer")
    st.markdown(TABLE_STYLES, unsafe_allow_html=True)
    st.caption(
        "Инструмент для анализа последних матчей игрока Dota 2 через OpenDota API."
    )

    with st.form("analysis_form"):
        account_id_value = st.text_input(
            "Введите account_id игрока",
            placeholder="Например, 123456789",
        )
        limit = st.number_input(
            "Количество матчей для анализа",
            min_value=1,
            max_value=100,
            value=20,
            step=1,
        )
        save_label = st.selectbox("Сохранить результат", list(SAVE_OPTIONS))
        submitted = st.form_submit_button(
            "Анализировать матчи",
            type="primary",
            width="stretch",
        )

    if not submitted:
        st.info("Введите account_id и запустите анализ.")
        return

    if not account_id_value.strip():
        st.error("Введите account_id игрока.")
        return

    try:
        account_id = int(account_id_value)
        if account_id <= 0:
            raise ValueError
    except ValueError:
        st.error("account_id должен быть положительным целым числом.")
        return

    try:
        with st.spinner("Получаем и анализируем матчи..."):
            raw_matches, used_cache = fetch_matches(account_id, int(limit))
            if not raw_matches:
                st.warning("Для этого аккаунта матчи не найдены.")
                return

            matches = parse_matches(raw_matches)
            stats = analyze_matches(matches)
            saved_paths = save_results(account_id, stats, SAVE_OPTIONS[save_label])
    except DataLoadError:
        st.error(
            "OpenDota API недоступен, а сохраненные матчи для этого аккаунта не найдены."
        )
        return
    except OpenDotaAPIError as exc:
        st.error(f"Не удалось получить данные OpenDota: {exc}")
        return
    except (OSError, ValueError) as exc:
        st.error(f"Не удалось обработать или сохранить данные: {exc}")
        return

    if used_cache:
        st.warning("OpenDota API недоступен. Показаны ранее сохраненные матчи.")
    else:
        st.success(f"Получено матчей: {len(matches)}")

    if saved_paths:
        paths = ", ".join(str(path) for path in saved_paths)
        st.success(f"Результат сохранен: {paths}")

    display_analysis(matches, stats)


if __name__ == "__main__":
    main()
