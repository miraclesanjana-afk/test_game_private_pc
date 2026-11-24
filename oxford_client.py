"""Word bank for the game.

Primary source: Gemini, asked to produce Oxford-style dictionary entries
(word, definitions, part of speech, length). Optional: the Oxford
Dictionaries API when app_id/app_key are set. Final fallback: a small
embedded list of common English words, so the game works offline.
"""

from __future__ import annotations

import json
import random
from typing import Dict, List, Optional

from api_client import ask_gemini_for_words, oxford_definitions
from config import BASE_DIR, get_key

CACHE_FILE = BASE_DIR / "data" / "words_cache.json"
GEMINI_WORDS_COUNT = 60
DIFFICULTY_RANGES = {"easy": (1, 5), "medium": (6, 8), "hard": (9, 99)}
OXFORD_SEED_WORDS = [
    "accept", "achieve", "adapt", "accurate", "advice", "beautiful", "believe",
    "benefit", "courage", "dangerous", "discover", "education", "freedom",
    "generous", "government", "important", "interesting", "knowledge",
    "language", "learning", "meaningful", "necessary", "opinion", "opportunity",
    "performance", "practice", "responsible", "strategy", "surprising",
    "traditional", "understand", "unique", "variety", "valuable",
]


def _entry(word: str, definitions: List[str], part_of_speech: str = "") -> Dict:
    return {
        "word": word,
        "definitions": definitions,
        "part_of_speech": part_of_speech,
        "length": len(word),
    }


# Fallback word list used when no API source is available.
EMBEDDED_WORDS = [
    _entry("accept", ["agree to receive or take"], "verb"),
    _entry("absolutely", ["in a way that cannot be denied or doubted"], "adverb"),
    _entry("account", ["a record or statement of financial expenditure"], "noun"),
    _entry("achieve", ["accomplish or obtain by effort", "reach a successful result"], "verb"),
    _entry("adapt", ["adjust to new conditions"], "verb"),
    _entry("accurate", ["correct in detail", "free from error"], "adjective"),
    _entry("advice", ["guidance or recommendations offered"], "noun"),
    _entry("beautiful", ["pleasing to the senses or mind"], "adjective"),
    _entry("believe", ["have faith in or trust", "accept that something is true"], "verb"),
    _entry("benefit", ["an advantage or profit gained"], "noun"),
    _entry("courage", ["the ability to face fear or danger"], "noun"),
    _entry("dangerous", ["likely to cause harm or injury"], "adjective"),
    _entry("discover", ["find or learn something"], "verb"),
    _entry("education", ["the process of receiving or giving instruction"], "noun"),
    _entry("freedom", ["the power or right to act, speak or think without hindrance"], "noun"),
    _entry("generous", ["ready to give and share", "not putting others to inconvenience"], "adjective"),
    _entry("government", ["the governing body of a nation, state or community"], "noun"),
    _entry("important", ["of great significance or consequence"], "adjective"),
    _entry("interesting", ["giving rise to curiosity"], "adjective"),
    _entry("knowledge", ["information, understanding or skill gained through experience or education"], "noun"),
    _entry("language", ["a system of communication used by a community"], "noun"),
    _entry("learning", ["the acquisition of knowledge or skill by study"], "noun"),
    _entry("meaningful", ["having meaning", "significant in value or effect"], "adjective"),
    _entry("necessary", ["required to be done"], "adjective"),
    _entry("opinion", ["a view or judgment formed about something"], "noun"),
    _entry("opportunity", ["a set of circumstances that makes it possible to do something"], "noun"),
    _entry("performance", ["an act or instance of showing how something works"], "noun"),
    _entry("practice", ["the application or use of an idea, belief or method", "repeated exercise"], "noun"),
    _entry("responsible", ["having an obligation to do something or answer for something"], "adjective"),
    _entry("strategy", ["a plan of action designed to achieve a long-term or overall aim"], "noun"),
    _entry("surprising", ["causing surprise or wonder"], "adjective"),
    _entry("traditional", ["existing in and handed down from the past"], "adjective"),
    _entry("understand", ["perceive the meaning of", "comprehend"], "verb"),
    _entry("unique", ["being the only one of its kind"], "adjective"),
    _entry("variety", ["a range of different types or kinds"], "noun"),
    _entry("valuable", ["having great value or worth"], "adjective"),
]


class WordBank:
    """The set of words the game draws from."""

    def __init__(self, words: List[Dict], source: str):
        self.words = words
        self.source = source
        self._by_lower = {w["word"].lower(): w for w in words}

    def __len__(self) -> int:
        return len(self.words)

    @classmethod
    def load(cls, force_refresh: bool = False) -> "WordBank":
        """Load a word bank: cache, then Gemini, then Oxford, then embedded."""
        if not force_refresh:
            bank = cls._from_cache()
            if bank is not None:
                return bank

        api_key = get_key("GEMINI_API_KEY")
        if api_key:
            for _attempt in range(3):
                try:
                    words = [w for w in ask_gemini_for_words(GEMINI_WORDS_COUNT, "common", api_key) if w.get("word")]
                    if len(words) >= 5:
                        cls._save_cache(words, "gemini")
                        return cls(words, "gemini")
                except Exception:
                    pass

        app_id, app_key = get_key("OXFORD_APP_ID"), get_key("OXFORD_APP_KEY")
        if app_id and app_key:
            try:
                words = [
                    _entry(seed, defs)
                    for seed in OXFORD_SEED_WORDS
                    if (defs := oxford_definitions(seed, app_id, app_key))
                ]
                if len(words) >= 10:
                    cls._save_cache(words, "oxford")
                    return cls(words, "oxford")
            except Exception:
                pass

        return cls(EMBEDDED_WORDS, "embedded")

    @classmethod
    def _from_cache(cls) -> Optional["WordBank"]:
        try:
            data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            words = [w for w in data.get("words", []) if isinstance(w, dict) and w.get("word")]
            if len(words) >= 10:
                return cls(words, str(data.get("source", "cache")))
        except Exception:
            pass
        return None

    @classmethod
    def _save_cache(cls, words: List[Dict], source: str) -> None:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(
            json.dumps({"source": source, "words": words}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def is_word(self, word: str) -> bool:
        """True when `word` is a known word in the bank (case-insensitive)."""
        return (word or "").strip().lower() in self._by_lower

    def words_by_difficulty(self, difficulty: str) -> List[Dict]:
        lo, hi = DIFFICULTY_RANGES.get(difficulty, DIFFICULTY_RANGES["medium"])
        candidates = [w for w in self.words if lo <= len(w.get("word", "")) <= hi]
        return candidates or self.words

    def random_word(self, difficulty: str = "medium") -> Dict:
        return random.choice(self.words_by_difficulty(difficulty))
