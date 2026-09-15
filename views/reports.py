"""
EduGuard AI - Reports View
"""
import streamlit as st
import pandas as pd
from utils.export import get_export_bytes


def render_reports_page(questions, analyses, coverage_metrics, db_handler):
    st.title("Final Reports & Audit Trail Export Center")
    st.markdown("Generate comprehensive documentation and export teacher decision audit logs.")

    if not questions:
        st.info("No questions loaded. Please upload a question bank or load demo data.")
        return

    st.subheader("1. Download Quality & Optimization Reports")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### HTML Executive Report")
        st.caption("Complete interactive web report containing executive summaries, quality charts, and findings.")
        data, fname, mime = get_export_bytes("html", questions, analyses, coverage_metrics)
        st.download_button("📥 Download HTML Report", data, fname, mime, use_container_width=True)

    with col2:
        st.markdown("#### CSV Data Export")
        st.caption("Raw question bank metrics, duplicate statuses, quality scores, and CO mappings.")
        data, fname, mime = get_export_bytes("csv", questions, analyses, coverage_metrics)
        st.download_button("📥 Download CSV Analysis", data, fname, mime, use_container_width=True)

    with col3:
        st.markdown("#### PDF Summary Document")
        st.caption("Printable PDF document summarizing question bank metrics and quality tables.")
        data, fname, mime = get_export_bytes("pdf", questions, analyses, coverage_metrics)
        st.download_button("📥 Download PDF Report", data, fname, mime, use_container_width=True)

    st.markdown("---")

    # Section 2: Teacher Decision Audit Logs
    st.subheader("2. Teacher Action & Decision Audit Log")
    decisions = db_handler.get_decisions()

    if decisions:
        dec_data = []
        for d in decisions:
            dec_data.append({
                "Timestamp": d.timestamp,
                "Question ID": d.question_id,
                "Recommendation Type": d.recommendation_type,
                "Teacher Decision": d.decision,
                "Edited Content": d.edited_content or "-"
            })
        st.dataframe(pd.DataFrame(dec_data), use_container_width=True, hide_index=True)
    else:
        st.info("No teacher decisions recorded in audit log yet. Review questions or What-If optimizations to populate decision logs.")
