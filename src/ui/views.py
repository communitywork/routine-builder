"""
src/ui/views.py
---------------
Top-level view renderers for each navigation section.
Each render_*_view() function is responsible for all Streamlit output
within its page, keeping app.py a clean router.
"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from ..core.generator import WorkoutGenerator
from ..utils.formatting import format_plan_as_markdown, format_plan_as_text
from .components import display_workout_plan
from .state import PRESETS, archive_current_routine


# ── View 1: Current Routine ────────────────────────────────────────────────────
def render_current_routine_view(generator: WorkoutGenerator) -> None:
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.title("📋 Current Workout Routine")

    plan: str = st.session_state.get("workout_plan", "")
    if not plan:
        _render_no_routine_placeholder()
        return

    meta = st.session_state.get("active_metadata", {})
    goal = meta.get("goal", "Build muscle")
    days = meta.get("days", 3)
    duration = meta.get("duration", 45)
    equipment = meta.get("equipment", "Home dumbbells")
    limitations = meta.get("limitations", "")

    # Regenerate button in the title row
    with col_t2:
        st.write("")
        st.write("")
        if st.button("🔄 Regenerate Version", type="secondary", use_container_width=True):
            archive_current_routine()
            with st.spinner("Analyzing biomechanics and generating new variation..."):
                success, result = generator.generate_plan(
                    fitness_goal=goal,
                    experience_level=meta.get("experience", "Intermediate"),
                    days_per_week=days,
                    equipment_access=equipment,
                    injuries_or_limitations=limitations,
                    session_duration_mins=duration,
                    variation_seed_hint="Use completely different exercises for variety",
                )
            if success:
                st.session_state.workout_plan = result
                st.toast("Generated new variation!", icon="✅")
                st.rerun()
            else:
                st.error(result)

    # Metrics bar
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(
        f'<div class="stat-box"><div class="stat-label">Goal</div>'
        f'<div class="stat-value">{goal}</div></div>',
        unsafe_allow_html=True,
    )
    m2.markdown(
        f'<div class="stat-box"><div class="stat-label">Frequency</div>'
        f'<div class="stat-value">{days} Days / Wk</div></div>',
        unsafe_allow_html=True,
    )
    m3.markdown(
        f'<div class="stat-box"><div class="stat-label">Target Session</div>'
        f'<div class="stat-value">{duration} Mins</div></div>',
        unsafe_allow_html=True,
    )
    m4.markdown(
        f'<div class="stat-box"><div class="stat-label">Equipment</div>'
        f'<div class="stat-value">{equipment}</div></div>',
        unsafe_allow_html=True,
    )

    tab_plan, tab_guidelines, tab_export = st.tabs(
        ["📅 Workout Schedule", "🛡️ CSCS Guidelines & Cues", "📥 Export & Save"]
    )

    with tab_plan:
        display_workout_plan(plan, generator=generator, allow_swap=True)

    with tab_guidelines:
        st.subheader("🛡️ Training Principles & Recovery Guidance")
        injury_note = (
            f"Movements adapted for: {limitations}. Stop immediately if sharp joint pain occurs."
            if limitations
            else "Follow progressive overload within pain-free active range of motion."
        )
        st.info(
            f"""
            **Program Guidelines**:
            - **Warm-Up**: 5–8 minutes of dynamic mobility tailored to the day's primary movement patterns.
            - **Rest Intervals**: Strictly adhere to the rest parameters (e.g. 60–90s for hypertrophy, 2–3m for heavy compounds).
            - **Progression**: Add 1 repetition or 2.5–5% load once you can complete all target sets with clean technique.
            - **Injury Protocol**: {injury_note}
            """
        )

    with tab_export:
        st.subheader("📥 Export & Save Blueprint")
        e_col1, e_col2, e_col3 = st.columns(3)
        with e_col1:
            st.download_button(
                "📥 Download Markdown (.md)",
                data=format_plan_as_markdown(plan),
                file_name=f"fitblueprint_{days}day_{goal.lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with e_col2:
            st.download_button(
                "📄 Download Plain Text (.txt)",
                data=format_plan_as_text(plan),
                file_name=f"fitblueprint_{days}day_{goal.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with e_col3:
            if st.button("💾 Save to Saved Routines", use_container_width=True):
                entry = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "timestamp": datetime.now().strftime("%b %d, %Y - %I:%M %p"),
                    "title": f"{days}-Day {goal} ({equipment})",
                    "goal": goal,
                    "days": days,
                    "equipment": equipment,
                    "duration": duration,
                    "experience": meta.get("experience", "Intermediate"),
                    "limitations": limitations,
                    "plan": plan,
                }
                st.session_state.saved_routines.insert(0, entry)
                st.toast("Blueprint saved to Saved Routines!", icon="💾")


def _render_no_routine_placeholder() -> None:
    with st.container(border=True):
        st.markdown("### 🏃 No Routine Currently Active")
        st.write(
            "Design a personalized training blueprint or load a battle-tested "
            "curated program to view it here."
        )
        col_act1, col_act2 = st.columns(2)
        if col_act1.button("⚡ Generate Custom Routine", type="primary", use_container_width=True):
            st.session_state.nav_selection = "⚡ Generate Routine"
            st.rerun()
        if col_act2.button("🏋️ Browse Curated Blueprints", use_container_width=True):
            st.session_state.nav_selection = "🏋️ Curated"
            st.rerun()


# ── View 2: Generate Routine ───────────────────────────────────────────────────
def render_generate_routine_view(generator: WorkoutGenerator) -> None:
    st.title("⚡ Generate Custom Routine")
    st.caption("Personalized personal training intake form backed by CSCS biomechanics")

    # Template populator
    preset_col1, preset_col2 = st.columns([3, 1])
    with preset_col1:
        chosen_preset = st.selectbox(
            "⚡ Quick Load Template (Optional)",
            ["Select a template..."] + list(PRESETS.keys()),
            help="Choose a pre-configured training split to populate the inputs below.",
        )
    with preset_col2:
        st.write("")
        st.write("")
        if st.button("Apply Template", use_container_width=True) and chosen_preset in PRESETS:
            p = PRESETS[chosen_preset]
            st.session_state["f_goal"] = p["goal"]
            st.session_state["f_exp"] = p["experience"]
            st.session_state["f_days"] = p["days"]
            st.session_state["f_equip"] = p["equipment"]
            st.session_state["f_duration"] = p["duration"]
            st.session_state["f_limit"] = p["limitations"]
            st.toast(f"Applied '{chosen_preset}'!", icon="⚡")
            st.rerun()

    with st.container(border=True):
        st.subheader("📋 Trainee Profile & Parameters")

        col1, col2 = st.columns(2)
        goal_options = ["Build muscle", "Lose fat", "General fitness", "Improve endurance"]
        goal = col1.selectbox(
            "Fitness Goal *",
            goal_options,
            index=goal_options.index(st.session_state.get("f_goal", "Build muscle")),
        )
        exp_options = ["Beginner", "Intermediate", "Advanced"]
        experience = col1.selectbox(
            "Experience Level *",
            exp_options,
            index=exp_options.index(st.session_state.get("f_exp", "Intermediate")),
        )
        days = col2.slider("Days Available per Week *", 1, 7, st.session_state.get("f_days", 3))
        duration = col2.select_slider(
            "Target Session Duration (Minutes) *",
            options=[20, 30, 45, 60, 75, 90],
            value=st.session_state.get("f_duration", 45),
        )

        col3, col4 = st.columns(2)
        equip_options = ["No equipment", "Home dumbbells", "Full gym"]
        equipment = col3.selectbox(
            "Equipment Access *",
            equip_options,
            index=equip_options.index(st.session_state.get("f_equip", "Home dumbbells")),
        )
        limitations = col4.text_input(
            "Injuries / Physical Limitations",
            value=st.session_state.get("f_limit", ""),
            placeholder="e.g. bad knees, lower back pain, no overhead pressing",
        )

        st.caption("Quick Add Limitation:")
        quick_tags = ["Bad knees", "Lower back pain", "Shoulder impingement", "No jumping / wrist pain"]
        tag_cols = st.columns(len(quick_tags))
        for idx, tag in enumerate(quick_tags):
            if tag_cols[idx].button(f"+ {tag}", key=f"quick_tag_{idx}", use_container_width=True):
                current = limitations.strip()
                st.session_state["f_limit"] = f"{current}, {tag}".strip(", ") if current else tag
                st.rerun()

    if st.button("🚀 Generate Science-Backed Routine", type="primary", use_container_width=True):
        with st.spinner("Analyzing biomechanics and generating your CSCS routine..."):
            success, result = generator.generate_plan(
                fitness_goal=goal,
                experience_level=experience,
                days_per_week=days,
                equipment_access=equipment,
                injuries_or_limitations=limitations,
                session_duration_mins=duration,
            )
        if success:
            st.session_state.workout_plan = result
            st.session_state.active_metadata = {
                "goal": goal,
                "experience": experience,
                "days": days,
                "equipment": equipment,
                "duration": duration,
                "limitations": limitations,
            }
            st.toast("Workout routine generated! Switched to Current Routine.", icon="✅")
            st.session_state.nav_selection = "📋 Current Routine"
            st.rerun()
        else:
            st.error(result)


# ── View 3: Curated Blueprints ─────────────────────────────────────────────────
def render_curated_view(generator: WorkoutGenerator) -> None:
    st.title("🏋️ Curated CSCS Blueprints")
    st.caption("Pre-engineered training splits designed for muscle building, fat loss, and lifestyle balance")

    for title, data in PRESETS.items():
        with st.container(border=True):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.subheader(title)
                st.markdown(
                    f"""
                    <span class="badge-pill">🎯 {data['goal']}</span>
                    <span class="badge-pill">📊 {data['experience']}</span>
                    <span class="badge-pill">📅 {data['days']} Days/Wk</span>
                    <span class="badge-pill">⏱️ {data['duration']} Min/Session</span>
                    <span class="badge-pill">🏋️ {data['equipment']}</span>
                    """,
                    unsafe_allow_html=True,
                )
                if data["limitations"]:
                    st.caption(f"Special Focus: {data['limitations']}")

            with col_b:
                st.write("")
                if st.button(
                    "⚡ Set as Current Routine",
                    key=f"set_active_{title}",
                    type="primary",
                    use_container_width=True,
                ):
                    with st.spinner(f"Synthesizing {title}..."):
                        success, result = generator.generate_plan(
                            fitness_goal=data["goal"],
                            experience_level=data["experience"],
                            days_per_week=data["days"],
                            equipment_access=data["equipment"],
                            injuries_or_limitations=data["limitations"],
                            session_duration_mins=data["duration"],
                        )
                    if success:
                        st.session_state.workout_plan = result
                        st.session_state.active_metadata = {
                            "goal": data["goal"],
                            "experience": data["experience"],
                            "days": data["days"],
                            "equipment": data["equipment"],
                            "duration": data["duration"],
                            "limitations": data["limitations"],
                        }
                        st.session_state.nav_selection = "📋 Current Routine"
                        st.toast(f"Loaded '{title}' into Current Routine!", icon="✅")
                        st.rerun()
                    else:
                        st.error(result)

                if st.button(
                    "🛠️ Customize in Generator",
                    key=f"cust_{title}",
                    use_container_width=True,
                ):
                    st.session_state["f_goal"] = data["goal"]
                    st.session_state["f_exp"] = data["experience"]
                    st.session_state["f_days"] = data["days"]
                    st.session_state["f_equip"] = data["equipment"]
                    st.session_state["f_duration"] = data["duration"]
                    st.session_state["f_limit"] = data["limitations"]
                    st.session_state.nav_selection = "⚡ Generate Routine"
                    st.rerun()


# ── View 4: Saved Routines ─────────────────────────────────────────────────────
def render_saved_routines_view() -> None:
    st.title("📂 Saved Routines & History")
    st.caption("Review, reload, and export previously generated workout routines")

    saved = st.session_state.get("saved_routines", [])
    if not saved:
        st.info(
            "No saved routines yet. Generate a routine and click "
            "'💾 Save to Saved Routines' in **Current Routine**."
        )
        return

    if st.button("🗑️ Clear All Saved Routines", type="secondary"):
        st.session_state.saved_routines = []
        st.toast("Saved routines cleared.", icon="🗑️")
        st.rerun()

    for idx, item in enumerate(saved):
        with st.expander(f"📋 {item['title']} — {item['timestamp']}", expanded=(idx == 0)):
            st.markdown(
                f"""
                <span class="badge-pill">🎯 {item['goal']}</span>
                <span class="badge-pill">📅 {item['days']} Days</span>
                <span class="badge-pill">⏱️ {item['duration']} Mins</span>
                <span class="badge-pill">🏋️ {item['equipment']}</span>
                """,
                unsafe_allow_html=True,
            )
            display_workout_plan(item["plan"])

            d_col1, d_col2, d_col3 = st.columns(3)

            if d_col1.button("⚡ Set Current", key=f"set_active_{item['id']}", use_container_width=True):
                st.session_state.workout_plan = item["plan"]
                st.session_state.active_metadata = {
                    "goal": item["goal"],
                    "days": item["days"],
                    "equipment": item["equipment"],
                    "duration": item["duration"],
                    "experience": item.get("experience", "Intermediate"),
                    "limitations": item.get("limitations", ""),
                }
                st.toast("Set as Current Routine!", icon="✅")

            if d_col2.button(
                "✏️ Modify (Swap/Regenerate)",
                key=f"modify_{item['id']}",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.workout_plan = item["plan"]
                st.session_state.active_metadata = {
                    "goal": item["goal"],
                    "days": item["days"],
                    "equipment": item["equipment"],
                    "duration": item["duration"],
                    "experience": item.get("experience", "Intermediate"),
                    "limitations": item.get("limitations", ""),
                }
                st.session_state.nav_selection = "📋 Current Routine"
                st.toast("Loaded for modification!", icon="✅")
                st.rerun()

            d_col3.download_button(
                "📥 Download MD",
                data=format_plan_as_markdown(item["plan"]),
                file_name=f"saved_routine_{item['id']}.md",
                key=f"dl_md_{item['id']}",
                use_container_width=True,
            )
