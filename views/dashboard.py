"""
EduGuard AI - Dashboard View
"""
import streamlit as st
import pandas as pd
from utils.helpers import create_bloom_chart, create_difficulty_chart


def render_dashboard(questions, analyses, coverage_metrics, health_metrics):
    st.title("EduGuard AI Dashboard")
    st.subheader("Question Bank Quality Assurance & Assessment Optimization")

    if not questions:
        st.info("No questions loaded. Please upload a question bank or load demo data in Upload & Config.")
        return

    # Metric Cards Row 1
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Questions", coverage_metrics.get("total_questions", 0))
    with col2:
        st.metric("Avg Quality Score", f"{coverage_metrics.get('average_quality', 0)} / 100")
    with col3:
        st.metric("Duplicates", f"{coverage_metrics.get('duplicate_pct', 0)}%")
    with col4:
        st.metric("Low Quality (<70)", f"{coverage_metrics.get('low_quality_pct', 0)}%")
    with col5:
        health_val = f"{health_metrics.total_health} / 100" if health_metrics else "Not Built"
        st.metric("Assessment Health", health_val)

    st.markdown("---")

    # Visualizations Row
    col_left, col_right = st.columns(2)
    with col_left:
        bloom_fig = create_bloom_chart(coverage_metrics.get("bloom_distribution", {}))
        st.plotly_chart(bloom_fig, use_container_width=True)

    with col_right:
        diff_fig = create_difficulty_chart(coverage_metrics.get("difficulty_distribution", {}))
        st.plotly_chart(diff_fig, use_container_width=True)

    # Section 2: Recent Quality Warnings & Topic Coverage Summary
    col_t, col_w = st.columns([1, 1])

    with col_t:
        st.markdown("### Top Topic Coverage")
        top_topics = coverage_metrics.get("topic_coverage", {})
        if top_topics:
            topic_df = pd.DataFrame([{"Topic": k, "Coverage (%)": v} for k, v in top_topics.items()])
            st.dataframe(topic_df, use_container_width=True, hide_index=True)

    with col_w:
        st.markdown("### Recent Quality Warnings")
        warnings_found = False
        for q in questions[:15]:
            a = analyses.get(q.id)
            if a:
                if a.duplicate_status != "Unique":
                    st.warning(f"**{q.id}**: {a.duplicate_status} (Matches {a.similar_question_id})")
                    warnings_found = True
                elif a.quality_score < 70:
                    st.error(f"**{q.id}**: Low Quality Score ({a.quality_score}/100)")
                    warnings_found = True
                elif a.relevance_status == "Potentially Out of Syllabus":
                    st.info(f"**{q.id}**: Potentially Out of Syllabus ({a.relevance_score}%)")
                    warnings_found = True
        if not warnings_found:
            st.success("No critical quality warnings detected in recent sample!")
