#models.py

from dataclasses import dataclass
from typing import List

@dataclass
class Match:
    match_id: int
    hero_id: int
    player_slot: int
    radiant_win: bool
    duration: int  #секунды
    win: bool

    @classmethod
    def from_dict(cls,  dict) -> 'Match':
        # Определяем победу: если игрок в радианте и радиант выиграл, или наоборот
        player_team_radiant = data['player_slot'] < 100
        win = data['radiant_win'] == player_team_radiant
        return cls(
            match_id=data['match_id'],
            hero_id=data['hero_id'],
            player_slot=data['player_slot'],
            radiant_win=data['radiant_win'],
            duration=data['duration'],
            win=win
        )

@dataclass
class PlayerStats:
    win_rate: float
    total_matches: int
    avg_duration: float
    top_heroes: List[dict]  # [{'name': 'Bane', 'games': 5, 'wins': 4}, ...]

    def __str__(self):
        lines = [
            f"Статистика игрока",
            f"Всего матчей: {self.total_matches}",
            f"Винрейт: {self.win_rate:.1f}%",
            f"Средняя длительность игры: {self.avg_duration:.0f} мин",
            f"Топ героев:"
        ]
        for hero in self.top_heroes:
            lines.append(f"{hero['name']} — {hero['games']} игр, {hero['wins']} побед")
        return "\n".join(lines)