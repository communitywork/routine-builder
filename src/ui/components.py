"""
src/ui/components.py
--------------------
Reusable, self-contained Streamlit UI components:
  - display_workout_plan()  — renders the full JSON plan as styled cards
  - swap_exercise_dialog()  — @st.dialog modal for inline exercise swapping
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from ..utils.formatting import format_plan_as_markdown
from .state import archive_current_routine

if TYPE_CHECKING:
    from ..core.generator import WorkoutGenerator


# ── Swap Dialog ────────────────────────────────────────────────────────────────
@st.dialog("🔄 Swap Exercise")
def swap_exercise_dialog(generator: "WorkoutGenerator", plan: str, ex_name: str) -> None:
    """
    Modal dialog for swapping a single exercise.

    Parameters:
        generator: Initialised WorkoutGenerator instance.
        plan: Current workout plan JSON string.
        ex_name: Name of the exercise to replace.
    """
    st.write(f"Swapping out: **{ex_name}**")
    swap_reason = st.selectbox(
        "Reason for Swap",
        [
            "Joint discomfort / Pain",
            "Equipment unavailable",
            "Movement too advanced",
            "Variety / Plateau",
        ],
    )
    if st.button("Confirm Swap", type="primary", use_container_width=True):
        with st.spinner("Analyzing biomechanics and swapping exercise..."):
            meta = st.session_state.get("active_metadata", {})
            success, new_plan = generator.replace_exercise(
                current_plan_json=plan,
                exercise_to_replace=ex_name,
                reason_or_preference=swap_reason,
                equipment_access=meta.get("equipment", "Home dumbbells"),
                injuries_or_limitations=meta.get("limitations", ""),
            )
        if success:
            archive_current_routine()
            st.session_state.workout_plan = new_plan
            st.toast(f"Successfully swapped {ex_name}!", icon="✅")
            st.rerun()
        else:
            st.error(new_plan)


# ── Plan Display ───────────────────────────────────────────────────────────────
def display_workout_plan(
    plan: str,
    generator: "WorkoutGenerator | None" = None,
    allow_swap: bool = False,
) -> None:
    """
    Render the workout plan.  Handles both JSON plans and legacy markdown strings.

    Parameters:
        plan: JSON or markdown string of the workout plan.
        generator: WorkoutGenerator instance (required when allow_swap=True).
        allow_swap: Whether to render inline Swap buttons.
    """
    import json

    try:
        data = json.loads(plan)
    except json.JSONDecodeError:
        st.markdown(plan)
        return

    st.markdown(f"### {data.get('program_name', 'Workout Plan')}")
    st.markdown(f"*{data.get('split_rationale', '')}*")
    st.markdown("---")

    for day in data.get("days", []):
        st.markdown(f"#### Day {day.get('day_number', '')}: {day.get('title', '')}")

        if day.get("warmup"):
            st.markdown("**Warm-up:**")
            for item in day["warmup"]:
                st.markdown(f"- {item}")

        if day.get("exercises"):
            st.markdown("**Exercises:**")
            for ex in day["exercises"]:
                col1, col2 = st.columns([0.85, 0.15])

                with col1:
                    st.markdown(
                        f"""
                        <div class="exercise-card" style="margin-bottom: 0;">
                            <div class="exercise-header">
                                <div class="exercise-number">{ex.get('number', '')}</div>
                                <div class="exercise-name">{ex.get('name', '')}</div>
                            </div>
                            <div class="exercise-details">
                                <div class="exercise-stat">
                                    <span class="stat-lbl">Sets</span>
                                    <span class="stat-val">{ex.get('sets', '')}</span>
                                </div>
                                <div class="exercise-stat">
                                    <span class="stat-lbl">Reps</span>
                                    <span class="stat-val">{ex.get('reps', '')}</span>
                                </div>
                                <div class="exercise-stat">
                                    <span class="stat-lbl">Rest</span>
                                    <span class="stat-val">{ex.get('rest', '')}</span>
                                </div>
                                <div class="exercise-cue">
                                    💡 <em>{ex.get('form_cue', '')}</em>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col2:
                    if allow_swap and generator is not None:
                        if st.button(
                            "🔄 Swap",
                            key=f"btn_swap_{day.get('day_number')}_{ex.get('number')}",
                            use_container_width=True,
                        ):
                            swap_exercise_dialog(generator, plan, ex.get("name", ""))

        if day.get("cooldown"):
            st.markdown("**Cool-down:**")
            for item in day["cooldown"]:
                st.markdown(f"- {item}")

        st.markdown("---")

    if data.get("progression_guidelines"):
        st.markdown("### Progression Guidelines")
        st.info(data["progression_guidelines"])

    if data.get("recovery_tips"):
        st.markdown("### Recovery Tips")
        st.info(data["recovery_tips"])

    if data.get("disclaimer"):
        st.markdown("### Disclaimer")
        st.warning(data["disclaimer"])
