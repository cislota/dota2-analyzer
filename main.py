from __future__ import annotations

import argparse
import sys

from analyzer import analyze_matches, format_duration
from api_client import DEFAULT_LIMIT, get_recent_matches
from models import Match, PlayerStats, parse_matches
from storage import (
    load_raw_matches,
    save_analysis_csv,
    save_analysis_json,
    save_raw_matches,
)
from utils.exceptions import DataLoadError, OpenDotaAPIError


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc

    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")

    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Dota 2 Match Analyzer",
        description="Analyze recent Dota 2 matches through OpenDota API.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch", help="Fetch recent player matches")
    fetch_parser.add_argument("account_id", type=positive_int, help="Dota 2 account ID")
    fetch_parser.add_argument(
        "--limit",
        type=positive_int,
        default=DEFAULT_LIMIT,
        help=f"Number of recent matches to fetch, default: {DEFAULT_LIMIT}",
    )

    analyze_parser = subparsers.add_parser("analyze", help="Analyze recent player matches")
    analyze_parser.add_argument("account_id", type=positive_int, help="Dota 2 account ID")
    analyze_parser.add_argument(
        "--limit",
        type=positive_int,
        default=DEFAULT_LIMIT,
        help=f"Number of recent matches to analyze, default: {DEFAULT_LIMIT}",
    )
    analyze_parser.add_argument(
        "--save",
        choices=("json", "csv"),
        help="Save analysis result to data/processed",
    )

    return parser


def print_match_preview(matches: list[Match], count: int = 2) -> None:
    print("\nFetched matches preview:")
    for match in matches[:count]:
        result = "win" if match.won else "loss"
        print(
            f"- match_id={match.match_id}, hero_id={match.hero_id}, "
            f"result={result}, duration={format_duration(match.duration)}"
        )


def print_stats(account_id: int, stats: PlayerStats) -> None:
    print("\nDota 2 Match Analyzer\n")
    print(f"Player ID: {account_id}")
    print(f"Matches analyzed: {stats.total_matches}\n")
    print(f"Winrate: {stats.winrate:.1f}%")
    print(f"Wins: {stats.wins}")
    print(f"Losses: {stats.losses}\n")
    print(f"Average match duration: {format_duration(round(stats.average_duration))}\n")
    print("Top heroes:")

    for index, hero in enumerate(stats.top_heroes, start=1):
        win_word = "win" if hero.wins == 1 else "wins"
        game_word = "game" if hero.games == 1 else "games"
        print(
            f"{index}. Hero ID {hero.hero_id} - {hero.games} {game_word}, "
            f"{hero.wins} {win_word}, winrate {hero.winrate:.1f}%"
        )


def fetch_command(account_id: int, limit: int) -> int:
    raw_matches = get_recent_matches(account_id, limit=limit)
    if not raw_matches:
        print("No matches found for this account.", file=sys.stderr)
        return 1

    path = save_raw_matches(account_id, raw_matches)
    matches = parse_matches(raw_matches)
    print(f"Saved {len(matches)} raw matches to {path}")
    print_match_preview(matches)
    return 0


def load_or_fetch_matches(account_id: int, limit: int) -> list[dict]:
    try:
        raw_matches = get_recent_matches(account_id, limit=limit)
        if not raw_matches:
            raise OpenDotaAPIError("OpenDota returned an empty matches list")
        save_raw_matches(account_id, raw_matches)
        return raw_matches
    except OpenDotaAPIError as exc:
        print(f"OpenDota API warning: {exc}", file=sys.stderr)
        print("Trying to load saved matches from data/raw...", file=sys.stderr)
        raw_matches = load_raw_matches(account_id)
        return raw_matches[:limit]


def analyze_command(account_id: int, limit: int, save_format: str | None) -> int:
    raw_matches = load_or_fetch_matches(account_id, limit)
    if not raw_matches:
        print("No matches available for analysis.", file=sys.stderr)
        return 1

    matches = parse_matches(raw_matches)
    stats = analyze_matches(matches)
    print_stats(account_id, stats)

    if save_format == "json":
        path = save_analysis_json(account_id, stats)
        print(f"\nSaved analysis to {path}")
    elif save_format == "csv":
        path = save_analysis_csv(account_id, stats)
        print(f"\nSaved analysis to {path}")

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "fetch":
            return fetch_command(args.account_id, args.limit)
        if args.command == "analyze":
            return analyze_command(args.account_id, args.limit, args.save)
    except (OpenDotaAPIError, DataLoadError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
