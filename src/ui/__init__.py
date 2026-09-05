"""src/ui/__init__.py — public API for the ui package."""
from .components import display_workout_plan, swap_exercise_dialog
from .state import PRESETS, archive_current_routine, init_session_state
from .views import (
    render_current_routine_view,
    render_curated_view,
    render_generate_routine_view,
    render_saved_routines_view,
)

__all__ = [
    "PRESETS",
    "archive_current_routine",
    "init_session_state",
    "display_workout_plan",
    "swap_exercise_dialog",
    "render_current_routine_view",
    "render_generate_routine_view",
    "render_curated_view",
    "render_saved_routines_view",
]
