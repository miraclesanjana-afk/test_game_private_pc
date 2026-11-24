"""HTTP clients for the word sources used by the game.

The Gemini API is the primary source for Oxford-style dictionary entries;
the Oxford Dictionaries API is used when app_id/app_key are configured.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional

import requests

from config import get_key

GEMINI_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_DEFAULT_MODEL = "gemma-4-26b-a4b-it"
# Models that answer generateContent, newest working first.
GEMINI_MODEL_FALLBACKS = [
    "gemini-flash-lite-latest",
    "gemma-4-26b-a4b-it",
    "gemma-4-31b-it",
    "gemini-flash-latest",
    "gemini-3-flash-preview",
    "gemini-pro-latest",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
]
GEMINI_RETRIES_PER_MODEL = 2
OXFORD_ENTRIES_URL = "https://api.oxforddictionaries.com/api/v2/entries/en-gb/{word}"


def gemini_generate(
    prompt: str, api_key: str, model: str | None = None
) -> str:
    """Send a prompt to the Gemini API and return the model's text.

    Tries the requested model first, then the fallback list until one
    answers successfully.
    """
    names = [model] if model else GEMINI_MODEL_FALLBACKS
    last_error: Exception | None = None
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    for name in names:
        for _attempt in range(GEMINI_RETRIES_PER_MODEL):
            try:
                response = requests.post(
                    f"{GEMINI_MODELS_URL}/{name}:generateContent",
                    params={"key": api_key},
                    json=payload,
                    timeout=30,
                )
            except Exception as exc:  # network error: try again/next model
                last_error = exc
                continue
            if response.status_code == 200:
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            last_error = requests.HTTPError(
                f"{response.status_code} for model {name}", response=response
            )
    raise last_error or RuntimeError("No Gemini model answered.")


def gemini_models(api_key: str) -> List[str]:
    """List available Gemini models (validates the key)."""
    response = requests.get(GEMINI_MODELS_URL, params={"key": api_key}, timeout=30)
    response.raise_for_status()
    return [m["name"] for m in response.json().get("models", [])]


def _strip_code_fences(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(.*?)```", text.strip(), re.DOTALL)
    if match:
        text = match.group(1)
    return text.strip()


def words_from_gemini_response(text: str) -> List[Dict[str, Any]]:
    """Parse and normalize the JSON word list returned by Gemini."""
    words: List[Dict[str, Any]] = []
    for entry in json.loads(_strip_code_fences(text)):
        if not isinstance(entry, dict):
            continue
        word = str(entry.get("word", "")).strip()
        if not word:
            continue
        definitions = [
            str(d).strip() for d in (entry.get("definitions") or []) if str(d).strip()
        ]
        part_of_speech = str(entry.get("part_of_speech") or "").strip()
        words.append(
            {
                "word": word,
                "definitions": definitions,
                "part_of_speech": part_of_speech,
                "length": len(word),
            }
        )
    return words


def ask_gemini_for_words(
    count: int, difficulty: str, api_key: str
) -> List[Dict[str, Any]]:
    """Ask Gemini for `count` Oxford-dictionary style words of a difficulty."""
    prompt = (
        f"Return a JSON array of exactly {count} distinct English words from the "
        f"Oxford dictionary, mostly {difficulty} difficulty. Each object must "
        f"have: \"word\" (string), \"definitions\" (array of up to 3 strings), "
        f"\"part_of_speech\" (string), \"length\" (number). "
        f"Return only the JSON array, nothing else."
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            text = gemini_generate(prompt, api_key)
            words = words_from_gemini_response(text)
            if words:
                return words
        except Exception as exc:
            last_error = exc
        if attempt < 2:
            time.sleep(2 * (attempt + 1))
    if last_error is not None:
        raise last_error
    raise RuntimeError("Gemini did not return any words.")


def oxford_definitions(
    word: str, app_id: str, app_key: str
) -> Optional[List[str]]:
    """Best-effort lookup of definitions via the Oxford Dictionaries API."""
    try:
        response = requests.get(
            OXFORD_ENTRIES_URL.format(word=word.lower()),
            headers={"app_id": app_id, "app_key": app_key},
            params={"fields": "definitions"},
            timeout=30,
        )
        if response.status_code != 200:
            return None
        data = response.json()
        definitions: List[str] = []
        for result in data.get("results", []):
            for lexical in result.get("lexicalEntries", []):
                for sense in lexical.get("senses", []):
                    for definition in sense.get("definitions") or []:
                        text = definition.get("text")
                        if text and text not in definitions:
                            definitions.append(text)
        return definitions[:5] or None
    except Exception:
        return None
