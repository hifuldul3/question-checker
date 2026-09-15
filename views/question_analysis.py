"""
EduGuard AI - Question Analysis View
"""
import streamlit as st
import pandas as pd
from utils.helpers import get_status_badge_html


def render_question_analysis_page(questions, analyses):
    st.title("Question Bank Quality Analysis")
    st.markdown("Detailed itemized AI assessment of all questions in the bank.")

    if not questions:
        st.info("No questions loaded. Please upload a question bank or load demo data.")
        return

    # Filter controls
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_query = st.text_input("🔍 Search Question Text", "")
    with col2:
        status_filter = st.selectbox("Duplicate Status", ["All", "Unique", "Near Duplicate", "Exact Duplicate"])
    with col3:
        bloom_filter = st.selectbox("Bloom Level", ["All", "Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"])
    with col4:
        min_quality = st.slider("Min Quality Score", 0, 100, 0)

    # Build data table rows
    rows = []
    for q in questions:
        a = analyses.get(q.id)
        if not a:
            continue

        # Apply filters
        if search_query and search_query.lower() not in q.text.lower():
            continue
        if status_filter != "All" and a.duplicate_status != status_filter:
            continue
        if bloom_filter != "All" and a.bloom_level != bloom_filter:
            continue
        if a.quality_score < min_quality:
            continue

        rows.append({
            "Q ID": q.id,
            "Question Text": q.text,
            "Marks": q.marks,
            "Topic": q.topic,
            "Type": q.question_type,
            "Duplicate Status": a.duplicate_status,
            "Similar Match": a.similar_question_id or "-",
            "Similarity (%)": f"{a.similarity_score}%" if a.similarity_score > 0 else "-",
            "Bloom Level": a.bloom_level,
            "Difficulty": a.difficulty,
            "Quality Score": a.quality_score,
            "Mapped CO": a.mapped_co
        })

    st.subheader(f"Filtered Results ({len(rows)} / {len(questions)} Questions)")
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No questions match the current filter criteria.")
