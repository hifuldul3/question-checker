"""
EduGuard AI - Assessment Health View
"""
import streamlit as st
import pandas as pd
from modules.assessment_health import calculate_assessment_health


def render_assessment_health_page(analyses):
    st.title("Assessment Health Score & Balance Diagnostics")
    st.markdown("Detailed breakdown of the active examination paper's overall quality and pedagogical balance.")

    active_qs = st.session_state.get("active_assessment", [])
    constraints = st.session_state.get("assessment_constraints")

    if not active_qs or not constraints:
        st.info("No active assessment found. Please construct an assessment in the Assessment Builder first.")
        return

    syllabus_text = st.session_state.get("syllabus_text", "")
    health = calculate_assessment_health(active_qs, analyses, constraints, syllabus_text)
    st.session_state["assessment_health"] = health

    # Health Score Metric Card
    col_score, col_warn = st.columns([1, 2])

    with col_score:
        st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>ASSESSMENT HEALTH</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 64px; color: #3b82f6;'>{health.total_health} / 100</h1>", unsafe_allow_html=True)

    with col_warn:
        st.subheader("Pedagogical Balance Diagnostics")
        if health.warnings:
            for w in health.warnings:
                st.warning(w)
        else:
            st.success("✔ Assessment is perfectly balanced across Bloom levels, difficulty, and CO coverage!")

    st.markdown("---")
    st.subheader("Component Health Score Breakdown")

    comp_data = [
        {"Component": "Question Quality Score (20%)", "Score / 100": health.quality_score, "Weight": "20%"},
        {"Component": "Syllabus Coverage (15%)", "Score / 100": health.syllabus_coverage, "Weight": "15%"},
        {"Component": "Concept Coverage (15%)", "Score / 100": health.concept_coverage, "Weight": "15%"},
        {"Component": "CO Alignment (15%)", "Score / 100": health.co_alignment, "Weight": "15%"},
        {"Component": "Bloom Balance (15%)", "Score / 100": health.bloom_balance, "Weight": "15%"},
        {"Component": "Difficulty Balance (10%)", "Score / 100": health.difficulty_balance, "Weight": "10%"},
        {"Component": "Question Diversity (10%)", "Score / 100": health.diversity_score, "Weight": "10%"}
    ]

    st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)
