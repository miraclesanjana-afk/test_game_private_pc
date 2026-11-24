"""Configuration: load and validate API keys for the game.

Keys come from the environment or from the local `.env` file next to this
script. Key values are never printed by this module.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def _read_env_file(path: Path = ENV_FILE) -> Dict[str, str]:
    values: Dict[str, str] = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                values[key] = value
    except FileNotFoundError:
        pass
    return values


def load_env() -> Dict[str, str]:
    """Fill missing environment variables from `.env`; return what was loaded."""
    loaded: Dict[str, str] = {}
    for key, value in _read_env_file().items():
        if not os.environ.get(key):
            os.environ[key] = value
            loaded[key] = value
    return loaded


def save_env(key: str, value: str, path: Path = ENV_FILE) -> None:
    """Add or update `key=value` in the local `.env` file."""
    values = _read_env_file(path)
    values[key] = value
    path.write_text(
        "\n".join(f"{k}={v}" for k, v in values.items()) + "\n", encoding="utf-8"
    )


def get_key(name: str) -> Optional[str]:
    """Return the value of a key, or None when it is not set anywhere."""
    load_env()
    value = os.environ.get(name) or _read_env_file().get(name)
    return value or None


def key_status() -> Dict[str, bool]:
    """Report which keys are present. Values themselves are never returned."""
    return {
        "GEMINI_API_KEY": bool(get_key("GEMINI_API_KEY")),
        "OXFORD_APP_ID": bool(get_key("OXFORD_APP_ID")),
        "OXFORD_APP_KEY": bool(get_key("OXFORD_APP_KEY")),
    }
