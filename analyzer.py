from __future__ import annotations

from collections import defaultdict

from models import HeroStats, Match, PlayerStats

#heros name from id:
#HEROS = пока что впадлу 

def format_duration(seconds: int) -> str:
    minutes, remaining_seconds = divmod(int(seconds), 60)
    return f"{minutes}:{remaining_seconds:02d}"


def analyze_matches(matches: list[Match]) -> PlayerStats:
    if not matches:
        raise ValueError("No matches to analyze")

    total_matches = len(matches)
    wins = sum(1 for match in matches if match.won)
    losses = total_matches - wins
    winrate = wins / total_matches * 100
    average_duration = sum(match.duration for match in matches) / total_matches

    hero_totals: dict[int, dict[str, int]] = defaultdict(lambda: {"games": 0, "wins": 0})
    for match in matches:
        hero_totals[match.hero_id]["games"] += 1
        if match.won:
            hero_totals[match.hero_id]["wins"] += 1

    top_heroes = [
        HeroStats(hero_id=hero_id, games=stats["games"], wins=stats["wins"])
        for hero_id, stats in hero_totals.items()
    ]
    top_heroes.sort(key=lambda hero: (-hero.games, -hero.wins, hero.hero_id))

    return PlayerStats(
        total_matches=total_matches,
        wins=wins,
        losses=losses,
        winrate=winrate,
        average_duration=average_duration,
        top_heroes=top_heroes,
    )
