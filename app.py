"""
app.py
------
FitBlueprint: Precision CSCS Workout Architect.
Two-Row Layout:
  Row 1: Full-page width horizontal top banner.
  Row 2: Left Navigation column + Main Content column.
"""

import os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from workout_generator import generate_workout_plan, swap_exercise, DEFAULT_MODEL

load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Workout Plan Generator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Environment Configuration ---
API_KEY = os.getenv("GROQ_API_KEY", "").strip()
MODEL_NAME = os.getenv("GROQ_MODEL", DEFAULT_MODEL).strip()

# --- Custom CSS Design System ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("styles.css")

# ==============================================================================
# ROW 1: FULL-PAGE WIDTH TOP HORIZONTAL BANNER
# ==============================================================================
st.markdown(
    f"""
    <div class="top-banner">
        <div class="banner-content">
            <div class="banner-brand">
                <span class="banner-icon">📐</span>
                <div>
                    <h1 class="banner-title">FitBlueprint</h1>
                    <p class="banner-subtitle">Precision CSCS Workout Architect • Science-Backed Protocols</p>
                </div>
            </div>
            <div class="banner-tags">
                <span class="banner-pill">🏋️ CSCS Standards</span>
                <span class="banner-pill">🔬 Science-Backed</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Session State Initialization ---
st.session_state.setdefault("workout_plan", "")
st.session_state.setdefault("active_metadata", {})
st.session_state.setdefault("saved_routines", [])
st.session_state.setdefault("nav_selection", "📋 Current Routine")

# --- Preset Definitions ---
PRESETS = {
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

# ==============================================================================
# ROW 2: TWO COLUMNS (LEFT NAVIGATION + MAIN CONTENT)
# ==============================================================================
nav_col, content_col = st.columns([1, 3.5], gap="large")

with nav_col:
    with st.container(border=True):
        st.markdown('<div class="nav-header">Navigation</div>', unsafe_allow_html=True)

        nav_items = [
            ("📋", "Current Routine"),
            ("⚡", "Generate Routine"),
            ("🏋️", "Curated"),
            ("📂", "Saved Routines"),
        ]

        current_nav = st.session_state.nav_selection
        for icon, label in nav_items:
            full_label = f"{icon} {label}"
            is_active = current_nav == full_label
            if st.button(f"{icon}  {label}", key=f"nav_btn_{label}", use_container_width=True):
                st.session_state.nav_selection = full_label
                st.rerun()
            # Show a green underline bar below the active item
            if is_active:
                st.markdown('<div class="nav-active-bar"></div>', unsafe_allow_html=True)

    # Active Blueprint Snapshot Card in Left Column
    meta = st.session_state.get("active_metadata", {})
    if meta:
        with st.container(border=True):
            st.markdown('<div class="nav-header">Active Blueprint</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="margin-bottom: 8px;">
                    <span class="badge-pill">🎯 {meta.get('goal', 'Custom')}</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <span class="badge-pill">📅 {meta.get('days', 0)} Days/Wk</span>
                </div>
                <div>
                    <span class="badge-pill">⏱️ {meta.get('duration', 45)} Mins</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


with content_col:
    _nav = st.session_state.nav_selection

    # ==============================================================================
    # VIEW 1: CURRENT ROUTINE
    # ==============================================================================
    if _nav == "📋 Current Routine":
        st.title("📋 Current Workout Routine")

        if plan := st.session_state.get("workout_plan"):
            meta = st.session_state.get("active_metadata", {})
            goal = meta.get("goal", "Build muscle")
            days = meta.get("days", 3)
            duration = meta.get("duration", 45)
            equipment = meta.get("equipment", "Home dumbbells")
            limitations = meta.get("limitations", "")

            # Summary Metrics Bar
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f'<div class="stat-box"><div class="stat-label">Goal</div><div class="stat-value">{goal}</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="stat-box"><div class="stat-label">Frequency</div><div class="stat-value">{days} Days / Wk</div></div>', unsafe_allow_html=True)
            m3.markdown(f'<div class="stat-box"><div class="stat-label">Target Session</div><div class="stat-value">{duration} Mins</div></div>', unsafe_allow_html=True)
            m4.markdown(f'<div class="stat-box"><div class="stat-label">Equipment</div><div class="stat-value">{equipment}</div></div>', unsafe_allow_html=True)

            tab_plan, tab_swap, tab_guidelines, tab_export = st.tabs([
                "📅 Workout Schedule",
                "🔄 Exercise Substitution",
                "🛡️ CSCS Guidelines & Cues",
                "📥 Export & Save",
            ])

            with tab_plan:
                st.markdown(plan)

            with tab_swap:
                st.subheader("🔄 Biomechanical Exercise Swap Assistant")
                st.caption("Need to replace an exercise in this routine due to discomfort or equipment?")
                swap_c1, swap_c2 = st.columns(2)
                ex_name = swap_c1.text_input("Exercise to Replace", placeholder="e.g. Barbell Squat, Pull-ups, Bench Press")
                swap_reason = swap_c2.selectbox(
                    "Reason for Swap",
                    ["Joint discomfort / Pain", "Equipment unavailable", "Movement too advanced", "Variety / Plateau"],
                )

                if st.button("🔍 Find Substitutions", type="primary", use_container_width=True):
                    if not ex_name.strip():
                        st.warning("Please specify an exercise to substitute.")
                    else:
                        with st.spinner("Finding biomechanically sound CSCS substitutes..."):
                            success, sub_res = swap_exercise(
                                current_exercise=ex_name,
                                reason_or_preference=swap_reason,
                                equipment_access=equipment,
                                injuries_or_limitations=limitations,
                                api_key=API_KEY,
                                model=MODEL_NAME,
                            )
                            if success:
                                st.markdown(sub_res)
                            else:
                                st.error(sub_res)

            with tab_guidelines:
                st.subheader("🛡️ Training Principles & Recovery Guidance")
                st.info(
                    f"""
                    **Program Guidelines**:
                    - **Warm-Up**: 5–8 minutes of dynamic mobility tailored to the day's primary movement patterns.
                    - **Rest Intervals**: Strictly adhere to the rest parameters (e.g. 60–90s for hypertrophy, 2–3m for heavy compounds).
                    - **Progression**: Add 1 repetition or 2.5–5% load once you can complete all target sets with clean technique.
                    - **Injury Protocol**: {'Movements adapted for: ' + (limitations or 'None') + '. Stop immediately if sharp joint pain occurs.' if limitations else 'Follow progressive overload within pain-free active range of motion.'}
                    """
                )

            with tab_export:
                st.subheader("📥 Export & Save Blueprint")
                e_col1, e_col2, e_col3 = st.columns(3)
                with e_col1:
                    st.download_button(
                        "📥 Download Markdown (.md)",
                        data=plan,
                        file_name=f"fitblueprint_{days}day_{goal.lower().replace(' ', '_')}.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )
                with e_col2:
                    st.download_button(
                        "📄 Download Plain Text (.txt)",
                        data=plan,
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
                            "plan": plan,
                        }
                        st.session_state.saved_routines.insert(0, entry)
                        st.toast("Blueprint saved to Saved Routines!", icon="💾")

        else:
            with st.container(border=True):
                st.markdown("### 🏃 No Routine Currently Active")
                st.write("Design a personalized training blueprint or load a battle-tested curated program to view it here.")
                col_act1, col_act2 = st.columns(2)
                if col_act1.button("⚡ Generate Custom Routine", type="primary", use_container_width=True):
                    st.session_state.nav_selection = "⚡ Generate Routine"
                    st.rerun()
                if col_act2.button("🏋️ Browse Curated Blueprints", use_container_width=True):
                    st.session_state.nav_selection = "🏋️ Curated"
                    st.rerun()


    # ==============================================================================
    # VIEW 2: GENERATE ROUTINE
    # ==============================================================================
    elif _nav == "⚡ Generate Routine":
        st.title("⚡ Generate Custom Routine")
        st.caption("Personalized personal training intake form backed by CSCS biomechanics")

        # Quick template populator
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
            goal = col1.selectbox(
                "Fitness Goal *",
                ["Build muscle", "Lose fat", "General fitness", "Improve endurance"],
                index=["Build muscle", "Lose fat", "General fitness", "Improve endurance"].index(
                    st.session_state.get("f_goal", "Build muscle")
                ),
            )
            experience = col1.selectbox(
                "Experience Level *",
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(
                    st.session_state.get("f_exp", "Intermediate")
                ),
            )

            days = col2.slider("Days Available per Week *", 1, 7, st.session_state.get("f_days", 3))
            duration = col2.select_slider(
                "Target Session Duration (Minutes) *",
                options=[20, 30, 45, 60, 75, 90],
                value=st.session_state.get("f_duration", 45),
            )

            col3, col4 = st.columns(2)
            equipment = col3.selectbox(
                "Equipment Access *",
                ["No equipment", "Home dumbbells", "Full gym"],
                index=["No equipment", "Home dumbbells", "Full gym"].index(
                    st.session_state.get("f_equip", "Home dumbbells")
                ),
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
            if not API_KEY:
                st.error("⚠️ GROQ_API_KEY is not configured in your `.env` file. Please check `.env`.")
            else:
                with st.spinner("Analyzing biomechanics and generating your CSCS routine..."):
                    success, result = generate_workout_plan(
                        fitness_goal=goal,
                        experience_level=experience,
                        days_per_week=days,
                        equipment_access=equipment,
                        injuries_or_limitations=limitations,
                        api_key=API_KEY,
                        session_duration_mins=duration,
                        model=MODEL_NAME,
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

    # ==============================================================================
    # VIEW 3: CURATED
    # ==============================================================================
    elif _nav == "🏋️ Curated":
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
                    if st.button("⚡ Set as Current Routine", key=f"set_active_{title}", type="primary", use_container_width=True):
                        if not API_KEY:
                            st.error("⚠️ GROQ_API_KEY is not configured in `.env`.")
                        else:
                            with st.spinner(f"Synthesizing {title}..."):
                                success, result = generate_workout_plan(
                                    fitness_goal=data["goal"],
                                    experience_level=data["experience"],
                                    days_per_week=data["days"],
                                    equipment_access=data["equipment"],
                                    injuries_or_limitations=data["limitations"],
                                    api_key=API_KEY,
                                    session_duration_mins=data["duration"],
                                    model=MODEL_NAME,
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

                    if st.button("🛠️ Customize in Generator", key=f"cust_{title}", use_container_width=True):
                        st.session_state["f_goal"] = data["goal"]
                        st.session_state["f_exp"] = data["experience"]
                        st.session_state["f_days"] = data["days"]
                        st.session_state["f_equip"] = data["equipment"]
                        st.session_state["f_duration"] = data["duration"]
                        st.session_state["f_limit"] = data["limitations"]
                        st.session_state.nav_selection = "⚡ Generate Routine"
                        st.rerun()

    # ==============================================================================
    # VIEW 4: SAVED ROUTINES
    # ==============================================================================
    elif _nav == "📂 Saved Routines":
        st.title("📂 Saved Routines & History")
        st.caption("Review, reload, and export previously generated workout routines")

        saved = st.session_state.get("saved_routines", [])
        if not saved:
            st.info("No saved routines yet. Generate a routine and click '💾 Save to Saved Routines' in **Current Routine**.")
        else:
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
                    st.markdown(item["plan"])
                    d_col1, d_col2 = st.columns([1, 1])
                    d_col1.download_button(
                        "📥 Download Markdown",
                        data=item["plan"],
                        file_name=f"saved_routine_{item['id']}.md",
                        key=f"dl_md_{item['id']}",
                        use_container_width=True,
                    )
                    if d_col2.button("⚡ Set as Current Routine", key=f"load_active_{item['id']}", type="primary", use_container_width=True):
                        st.session_state.workout_plan = item["plan"]
                        st.session_state.active_metadata = {
                            "goal": item["goal"],
                            "days": item["days"],
                            "equipment": item["equipment"],
                            "duration": item["duration"],
                        }
                        st.session_state.nav_selection = "📋 Current Routine"
                        st.toast("Loaded as Current Routine!", icon="✅")
                        st.rerun()

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 20px; color: #b3b3b3;">
        <p style="margin: 0; font-size: 0.9rem;">
            <strong>FitBlueprint</strong> • Precision CSCS Workout Architect
        </p>
        <p style="margin: 8px 0 0 0; font-size: 0.85rem;">
            Questions or support? Contact us at <a href="mailto:sales@fitblueprint.com" style="color: #1DB954;">sales@fitblueprint.com</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
