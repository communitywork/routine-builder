"""
app.py
------
FitBlueprint — Precision CSCS Workout Architect.
Minimal entry point: page config, CSS injection, banner, nav, and view routing.
All business logic lives in src/.
"""
from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from src.core import WorkoutGenerator, get_api_key, get_model_name
from src.ui import (
    init_session_state,
    render_current_routine_view,
    render_curated_view,
    render_generate_routine_view,
    render_saved_routines_view,
)

# ── Bootstrap ──────────────────────────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="FitBlueprint — Workout Plan Generator",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
def _load_css(path: str) -> None:
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

_load_css("styles.css")

# ── State & Generator ──────────────────────────────────────────────────────────
init_session_state()

generator = WorkoutGenerator(api_key=get_api_key(), model=get_model_name())

# ── Top Banner ─────────────────────────────────────────────────────────────────
st.markdown(
    """
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

# ── Layout: Nav + Content ──────────────────────────────────────────────────────
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
            if is_active:
                st.markdown('<div class="nav-active-bar"></div>', unsafe_allow_html=True)

    # Active Blueprint snapshot
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

# ── View Router ────────────────────────────────────────────────────────────────
with content_col:
    _nav = st.session_state.nav_selection

    if _nav == "📋 Current Routine":
        render_current_routine_view(generator)
    elif _nav == "⚡ Generate Routine":
        render_generate_routine_view(generator)
    elif _nav == "🏋️ Curated":
        render_curated_view(generator)
    elif _nav == "📂 Saved Routines":
        render_saved_routines_view()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 20px; color: #b3b3b3;">
        <p style="margin: 0; font-size: 0.9rem;">
            <strong>FitBlueprint</strong> • Precision CSCS Workout Architect
        </p>
        <p style="margin: 8px 0 0 0; font-size: 0.85rem;">
            Questions or support? Contact us at
            <a href="mailto:sales@fitblueprint.com" style="color: #1DB954;">sales@fitblueprint.com</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
