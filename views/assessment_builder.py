"""
EduGuard AI - Assessment Builder View
"""
import streamlit as st
import pandas as pd
from models import AssessmentConstraint
from modules.assessment_builder import build_assessment_paper
from modules.assessment_health import calculate_assessment_health


def render_assessment_builder_page(questions, analyses, db_handler):
    st.title("Interactive Assessment Builder")
    st.markdown("Specify target examination constraints and construct a balanced assessment paper.")

    if not questions:
        st.info("No questions loaded. Please upload a question bank or load demo data.")
        return

    col_cfg, col_paper = st.columns([1, 1])

    with col_cfg:
        st.subheader("1. Assessment Target Constraints")
        title = st.text_input("Assessment Title", "End Semester Examination - DBMS")
        num_q = st.number_input("Number of Questions", min_value=1, max_value=len(questions), value=min(10, len(questions)))
        total_m = st.number_input("Total Target Marks", min_value=10.0, max_value=100.0, value=50.0)

        st.markdown("#### Desired Bloom's Taxonomy Distribution (%)")
        b_rem = st.slider("Remember (%)", 0, 100, 20)
        b_und = st.slider("Understand (%)", 0, 100, 25)
        b_app = st.slider("Apply (%)", 0, 100, 25)
        b_ana = st.slider("Analyze (%)", 0, 100, 15)
        b_eva = st.slider("Evaluate (%)", 0, 100, 10)
        b_cre = st.slider("Create (%)", 0, 100, 5)

        st.markdown("#### Desired Difficulty Distribution (%)")
        d_easy = st.slider("Easy (%)", 0, 100, 30)
        d_med = st.slider("Medium (%)", 0, 100, 50)
        d_hard = st.slider("Hard (%)", 0, 100, 20)

        constraints = AssessmentConstraint(
            title=title,
            num_questions=num_q,
            total_marks=total_m,
            bloom_distribution={
                "Remember": b_rem, "Understand": b_und, "Apply": b_app,
                "Analyze": b_ana, "Evaluate": b_eva, "Create": b_cre
            },
            difficulty_distribution={
                "Easy": d_easy, "Medium": d_med, "Hard": d_hard
            }
        )

        if st.button("🔨 Build / Rebuild Assessment Paper", type="primary"):
            selected_qs = build_assessment_paper(questions, analyses, constraints)
            st.session_state["active_assessment"] = selected_qs
            st.session_state["assessment_constraints"] = constraints

            # Calculate health score
            syllabus_text = st.session_state.get("syllabus_text", "")
            health = calculate_assessment_health(selected_qs, analyses, constraints, syllabus_text)
            st.session_state["assessment_health"] = health

            st.success(f"Built assessment paper with {len(selected_qs)} questions! Calculated Health Score: {health.total_health}/100")
            st.rerun()

    with col_paper:
        st.subheader("2. Selected Assessment Paper")
        active_qs = st.session_state.get("active_assessment", [])

        if not active_qs:
            st.warning("No assessment paper constructed yet. Click 'Build Assessment Paper' on the left.")
        else:
            total_paper_marks = sum(q.marks for q in active_qs)
            st.info(f"**Title:** {st.session_state.get('assessment_constraints').title} | **Questions:** {len(active_qs)} | **Total Marks:** {total_paper_marks}")

            paper_data = []
            for idx, q in enumerate(active_qs):
                a = analyses.get(q.id)
                paper_data.append({
                    "#": idx + 1,
                    "Q ID": q.id,
                    "Question Text": q.text[:50] + "...",
                    "Marks": q.marks,
                    "Topic": q.topic,
                    "Bloom": a.bloom_level if a else "Understand",
                    "Difficulty": a.difficulty if a else "Medium",
                    "Quality": a.quality_score if a else 80.0
                })
            st.dataframe(pd.DataFrame(paper_data), use_container_width=True, hide_index=True)
