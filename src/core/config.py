"""
src/core/config.py
------------------
Application-wide configuration: environment variables, constants, and model registry.
"""
from __future__ import annotations

import os
import sys
import locale
from typing import List

# ── Windows UTF-8 compatibility ────────────────────────────────────────────────
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

# ── Model Registry ─────────────────────────────────────────────────────────────
SUPPORTED_MODELS: List[str] = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]

DEFAULT_MODEL: str = SUPPORTED_MODELS[0]


# ── Environment Helpers ────────────────────────────────────────────────────────
def get_api_key() -> str:
    """Return the Groq API key from the environment."""
    return os.getenv("GROQ_API_KEY", "").strip()


def get_model_name() -> str:
    """Return the configured Groq model, falling back to the default."""
    return os.getenv("GROQ_MODEL", DEFAULT_MODEL).strip()
