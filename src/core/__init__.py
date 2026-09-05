"""src/core/__init__.py — public API for the core package."""
from .config import DEFAULT_MODEL, SUPPORTED_MODELS, get_api_key, get_model_name
from .generator import WorkoutGenerator

__all__ = [
    "DEFAULT_MODEL",
    "SUPPORTED_MODELS",
    "get_api_key",
    "get_model_name",
    "WorkoutGenerator",
]
