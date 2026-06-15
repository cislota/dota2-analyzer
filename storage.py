from __future__ import annotations

import csv
import json
from pathlib import Path

from analyzer import format_duration
from models import PlayerStats
from utils.exceptions import DataLoadError

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def ensure_data_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def get_raw_matches_path(account_id: int) -> Path:
    return RAW_DIR / f"{account_id}_matches.json"


def get_analysis_json_path(account_id: int) -> Path:
    return PROCESSED_DIR / f"{account_id}_stats.json"


def get_analysis_csv_path(account_id: int) -> Path:
    return PROCESSED_DIR / f"{account_id}_stats.csv"


def save_raw_matches(account_id: int, matches: list[dict]) -> Path:
    ensure_data_dirs()
    path = get_raw_matches_path(account_id)
    with path.open("w", encoding="utf-8") as file:
        json.dump(matches, file, ensure_ascii=False, indent=2)
    return path


def load_raw_matches(account_id: int) -> list[dict]:
    path = get_raw_matches_path(account_id)
    if not path.exists():
        raise DataLoadError(f"Saved matches file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except OSError as exc:
        raise DataLoadError(f"Failed to read saved matches: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise DataLoadError(f"Saved matches file contains invalid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise DataLoadError("Saved matches file must contain a list")

    return data


def save_analysis_json(account_id: int, stats: PlayerStats) -> Path:
    ensure_data_dirs()
    path = get_analysis_json_path(account_id)
    payload = stats.to_dict()
    payload["average_duration_formatted"] = format_duration(round(stats.average_duration))

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    return path


def save_analysis_csv(account_id: int, stats: PlayerStats) -> Path:
    ensure_data_dirs()
    path = get_analysis_csv_path(account_id)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["metric", "value"])
        writer.writerow(["total_matches", stats.total_matches])
        writer.writerow(["wins", stats.wins])
        writer.writerow(["losses", stats.losses])
        writer.writerow(["winrate", f"{stats.winrate:.1f}%"])
        writer.writerow(["average_duration", format_duration(round(stats.average_duration))])
        writer.writerow([])
        writer.writerow(["hero_id", "games", "wins", "losses", "winrate"])
        for hero in stats.top_heroes:
            writer.writerow(
                [
                    hero.hero_id,
                    hero.games,
                    hero.wins,
                    hero.losses,
                    f"{hero.winrate:.1f}%",
                ]
            )

    return path
