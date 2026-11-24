"""Core scramble-game logic (shared by the CLI and the Streamlit app)."""

from __future__ import annotations

import random
from typing import Any, Dict, Optional, Tuple

from oxford_client import WordBank


def scramble_word(word: str, max_tries: int = 50) -> str:
    """Return a shuffled version of `word` that differs from it when possible."""
    letters = list(word)
    for _ in range(max_tries):
        random.shuffle(letters)
        candidate = "".join(letters)
        if candidate != word or len(letters) <= 1:
            return candidate
    return "".join(sorted(letters, reverse=True))


class ScrambleGame:
    """A round-based word scramble game."""

    SCORE_PER_ROUND = 10

    def __init__(self, word_bank: WordBank, difficulty: str = "medium", rounds: int = 8):
        self.word_bank = word_bank
        self.difficulty = difficulty
        self.rounds = rounds
        self.reset()

    def reset(self) -> None:
        self.round_no = 0
        self.score = 0
        self.current: Optional[Dict[str, Any]] = None
        self.scrambled = ""
        self._awaiting_next = False
        self._start_round()

    def _start_round(self) -> None:
        word = self.word_bank.random_word(self.difficulty)
        self.current = word
        self.scrambled = scramble_word(word.get("word", ""))
        self.round_no += 1

    @property
    def is_finished(self) -> bool:
        """True once the last round has been completed."""
        return self._awaiting_next and self.round_no >= self.rounds

    def next_round(self) -> None:
        if not self._awaiting_next:
            return
        self._awaiting_next = False
        self._start_round()

    def submit_guess(self, guess: str) -> Tuple[bool, str]:
        """Check a guess. Returns (correct, message)."""
        guess = (guess or "").strip().lower()
        if not guess:
            return False, "Enter a guess first."
        current = self.current or {}
        if guess == str(current.get("word", "")).lower():
            self.score += self.SCORE_PER_ROUND
            self._awaiting_next = True
            return True, f"Correct! Score: {self.score}"
        return False, "Not quite; try again."

    def get_hint(self) -> str:
        """Return a definition hint for the current word."""
        definitions = (self.current or {}).get("definitions") or []
        return "; ".join(definitions) if definitions else "Think about the scrambled letters."
