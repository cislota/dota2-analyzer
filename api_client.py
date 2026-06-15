from __future__ import annotations

import requests

from utils.exceptions import OpenDotaAPIError

OPENDOTA_API_URL = "https://api.opendota.com/api"
DEFAULT_LIMIT = 20
REQUEST_TIMEOUT = 15


def get_recent_matches(account_id: int, limit: int = DEFAULT_LIMIT) -> list[dict]:
    """Fetch recent Dota 2 matches for a player from OpenDota."""
    if account_id <= 0:
        raise ValueError("account_id must be a positive integer")
    if limit <= 0:
        raise ValueError("limit must be a positive integer")

    url = f"{OPENDOTA_API_URL}/players/{account_id}/recentMatches"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise OpenDotaAPIError(f"Failed to fetch matches from OpenDota: {exc}") from exc

    try:
        matches = response.json()
    except ValueError as exc:
        raise OpenDotaAPIError("OpenDota returned invalid JSON") from exc

    if not isinstance(matches, list):
        raise OpenDotaAPIError("OpenDota returned an unexpected response format")

    return matches[:limit]


if __name__ == "__main__":
    sample_matches = get_recent_matches(1149785629, limit=2)
    for match in sample_matches:
        print(
            "Match ID: {match_id}, Hero ID: {hero_id}, Duration: {duration}s, "
            "Radiant win: {radiant_win}, Player slot: {player_slot}".format(**match)
        )
