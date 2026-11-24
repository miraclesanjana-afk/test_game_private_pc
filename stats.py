"""Persisted game statistics."""

from __future__ import annotations

import json
from typing import Any, Dict

from config import BASE_DIR

STATS_FILE = BASE_DIR / "data" / "stats.json"


class Stats:
    def __init__(self) -> None:
        self.total_played = 0
        self.total_correct = 0
        self.best_score = 0

    @classmethod
    def load(cls) -> "Stats":
        stats = cls()
        try:
            data = json.loads(STATS_FILE.read_text(encoding="utf-8"))
            stats.total_played = int(data.get("total_played", 0))
            stats.total_correct = int(data.get("total_correct", 0))
            stats.best_score = int(data.get("best_score", 0))
        except Exception:
            pass
        return stats

    def save(self) -> None:
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload: Dict[str, Any] = {
            "total_played": self.total_played,
            "total_correct": self.total_correct,
            "best_score": self.best_score,
        }
        STATS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def record(self, score: int, rounds: int) -> None:
        self.total_played += 1
        self.total_correct += rounds
        self.best_score = max(self.best_score, score)
        self.save()
