from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import urljoin

import requests

HEROES_API_URL = "https://api.opendota.com/api/heroes"
HEROES_CACHE_PATH = Path("data") / "heroes.json"
HERO_IMAGE_BASE_URL = "https://cdn.cloudflare.steamstatic.com"
HERO_IMAGE_TEMPLATE = (
    "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/"
    "dota_react/heroes/{hero_name}.png"
)
REQUEST_TIMEOUT = 15


def _hero_icon_url(hero: dict) -> str | None:
    image_path = hero.get("img")
    if isinstance(image_path, str) and image_path.strip():
        if image_path.startswith(("http://", "https://")):
            return image_path
        return urljoin(HERO_IMAGE_BASE_URL, image_path)

    technical_name = hero.get("name")
    if not isinstance(technical_name, str):
        return None

    short_name = technical_name.removeprefix("npc_dota_hero_").strip()
    if not short_name:
        return None
    return HERO_IMAGE_TEMPLATE.format(hero_name=short_name)


def _normalize_heroes(raw_heroes: list[dict]) -> dict[int, dict[str, str | None]]:
    heroes = {}
    for hero in raw_heroes:
        try:
            hero_id = int(hero["id"])
        except (KeyError, TypeError, ValueError):
            continue

        localized_name = hero.get("localized_name")
        name = (
            localized_name.strip()
            if isinstance(localized_name, str) and localized_name.strip()
            else f"Hero ID {hero_id}"
        )
        heroes[hero_id] = {
            "name": name,
            "icon_url": _hero_icon_url(hero),
        }
    return heroes


def _load_cached_heroes() -> dict[int, dict[str, str | None]] | None:
    if not HEROES_CACHE_PATH.exists():
        return None

    try:
        with HEROES_CACHE_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict):
        return None

    heroes = {}
    for hero_id, hero in data.items():
        if not isinstance(hero, dict):
            continue
        try:
            heroes[int(hero_id)] = {
                "name": str(hero["name"]),
                "icon_url": hero.get("icon_url"),
            }
        except (KeyError, TypeError, ValueError):
            continue
    return heroes


def _save_heroes(heroes: dict[int, dict[str, str | None]]) -> None:
    try:
        HEROES_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with HEROES_CACHE_PATH.open("w", encoding="utf-8") as file:
            json.dump(heroes, file, ensure_ascii=False, indent=2)
    except OSError:
        pass


@lru_cache(maxsize=1)
def get_heroes_map() -> dict[int, dict[str, str | None]]:
    cached_heroes = _load_cached_heroes()
    if cached_heroes is not None:
        return cached_heroes

    try:
        response = requests.get(HEROES_API_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        raw_heroes = response.json()
    except (requests.RequestException, ValueError):
        return {}

    if not isinstance(raw_heroes, list):
        return {}

    heroes = _normalize_heroes(raw_heroes)
    if heroes:
        _save_heroes(heroes)
    return heroes


def get_hero_name(hero_id: int) -> str:
    hero = get_heroes_map().get(hero_id)
    if not hero:
        return f"Hero ID {hero_id}"
    return str(hero["name"])


def get_hero_icon_url(hero_id: int) -> str | None:
    hero = get_heroes_map().get(hero_id)
    if not hero:
        return None
    icon_url = hero.get("icon_url")
    return str(icon_url) if icon_url else None
