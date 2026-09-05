"""
src/ui/state.py
---------------
Session-state initialisation, type definitions for saved routines,
and helper logic for archiving the active routine to history.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st


# ── Type alias ─────────────────────────────────────────────────────────────────
RoutineEntry = Dict[str, Any]

# ── Presets ───────────────────────────────────────────────────────────────────
PRESETS: Dict[str, Dict[str, Any]] = {
    "⚡ 5-Day Push/Pull/Legs (Hypertrophy)": {
        "goal": "Build muscle",
        "experience": "Intermediate",
        "days": 5,
        "equipment": "Full gym",
        "duration": 60,
        "limitations": "",
    },
    "🎯 4-Day Upper/Lower Strength Split": {
        "goal": "Build muscle",
        "experience": "Intermediate",
        "days": 4,
        "equipment": "Full gym",
        "duration": 60,
        "limitations": "",
    },
    "🏠 3-Day Home Dumbbell Recomp": {
        "goal": "Build muscle",
        "experience": "Beginner",
        "days": 3,
        "equipment": "Home dumbbells",
        "duration": 45,
        "limitations": "",
    },
    "⏱️ 3-Day Busy Executive (30-Min)": {
        "goal": "General fitness",
        "experience": "Beginner",
        "days": 3,
        "equipment": "Home dumbbells",
        "duration": 30,
        "limitations": "Short rest periods, compound density",
    },
    "🧘 3-Day Desk Worker Posture & Core": {
        "goal": "General fitness",
        "experience": "Beginner",
        "days": 3,
        "equipment": "No equipment",
        "duration": 30,
        "limitations": "Tight hip flexors, forward head posture, avoid high impact",
    },
}


def init_session_state() -> None:
    """Initialise all required session-state keys with safe defaults."""
    st.session_state.setdefault("workout_plan", "")
    st.session_state.setdefault("active_metadata", {})
    st.session_state.setdefault("saved_routines", [])
    st.session_state.setdefault("nav_selection", "📋 Current Routine")


def archive_current_routine() -> None:
    """
    Auto-save the currently active routine into the saved-routines history.
    No-op when there is no active plan or metadata.
    """
    plan: str = st.session_state.get("workout_plan", "")
    meta: Dict[str, Any] = st.session_state.get("active_metadata", {})
    if not plan or not meta:
        return

    entry: RoutineEntry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.now().strftime("%b %d, %Y - %I:%M %p"),
        "title": (
            f"{meta.get('days', 3)}-Day {meta.get('goal', 'Custom')} "
            f"({meta.get('equipment', 'Mixed')})"
        ),
        "goal": meta.get("goal", ""),
        "days": meta.get("days", 0),
        "equipment": meta.get("equipment", ""),
        "duration": meta.get("duration", 0),
        "experience": meta.get("experience", "Intermediate"),
        "limitations": meta.get("limitations", ""),
        "plan": plan,
    }
    st.session_state.saved_routines.insert(0, entry)
