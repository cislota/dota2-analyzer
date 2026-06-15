from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Match:
    match_id: int
    hero_id: int
    player_slot: int
    radiant_win: bool
    duration: int

    @property
    def is_radiant(self) -> bool:
        return self.player_slot < 128

    @property
    def won(self) -> bool:
        return self.radiant_win == self.is_radiant

    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        required_fields = ("match_id", "hero_id", "player_slot", "radiant_win", "duration")
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Match data is missing fields: {', '.join(missing_fields)}")

        return cls(
            match_id=int(data["match_id"]),
            hero_id=int(data["hero_id"]),
            player_slot=int(data["player_slot"]),
            radiant_win=bool(data["radiant_win"]),
            duration=int(data["duration"]),
        )


@dataclass
class HeroStats:
    hero_id: int
    games: int
    wins: int

    @property
    def losses(self) -> int:
        return self.games - self.wins

    @property
    def winrate(self) -> float:
        if self.games == 0:
            return 0.0
        return self.wins / self.games * 100


@dataclass
class PlayerStats:
    total_matches: int
    wins: int
    losses: int
    winrate: float
    average_duration: float
    top_heroes: list[HeroStats]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["top_heroes"] = [asdict(hero) for hero in self.top_heroes]
        return data


def parse_matches(raw_matches: list[dict]) -> list[Match]:
    return [Match.from_dict(match) for match in raw_matches]
