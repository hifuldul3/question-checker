"""
EduGuard AI - Question Details & Review View
"""
import streamlit as st
from models import TeacherDecision


def render_question_details_page(questions, analyses, db_handler):
    st.title("Question Analysis & AI Recommendation Review")
    st.markdown("Inspect individual question diagnostics, AI evidence, and record teacher decisions.")

    if not questions:
        st.info("No questions loaded. Please upload a question bank or load demo data.")
        return

    q_options = [f"{q.id}: {q.text[:60]}..." for q in questions]
    selected_option = st.selectbox("Select Question to Inspect", q_options)

    if selected_option:
        q_id = selected_option.split(":")[0].strip()
        q = next((item for item in questions if item.id == q_id), None)
        a = analyses.get(q_id)

        if not q or not a:
            st.error("Question details not found.")
            return

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("### Original Question")
            st.info(f"**[{q.id}]** {q.text}")
            st.markdown(f"**Topic:** {q.topic} | **Marks:** {q.marks} | **Type:** {q.question_type}")

            st.markdown("---")
            st.markdown("### Quality Breakdown")
            q_cols = st.columns(3)
            q_cols[0].metric("Clarity", f"{a.quality_breakdown.get('clarity', 80)}/100")
            q_cols[1].metric("Grammar", f"{a.quality_breakdown.get('grammar', 100)}/100")
            q_cols[2].metric("Relevance", f"{a.quality_breakdown.get('relevance', 100)}/100")

            st.metric("Overall Quality Score", f"{a.quality_score} / 100")

        with col_right:
            st.markdown("### AI Diagnostic Flags & Evidence")

            # Duplicate Status Card
            if a.duplicate_status != "Unique":
                st.error(f"**Issue:** {a.duplicate_status}")
                st.write(f"**Evidence:** Cosine Similarity {a.similarity_score}% with question **{a.similar_question_id}**.")
                st.write(f"**Reason:** Both questions test identical or near-identical concepts.")
            else:
                st.success("✔ Unique Question (No duplicates found)")

            # Ambiguity Card
            if a.ambiguity_score > 0:
                st.warning(f"**Ambiguity Issue:** {a.ambiguity_issue} (Score: {a.ambiguity_score}%)")
                st.write(f"**Reason:** {a.ambiguity_reason}")

            # Grammar Card
            if a.grammar_score < 100:
                st.warning(f"**Grammar / Structure Issue:** {a.grammar_issue}")
                st.write(f"**Suggestion:** {a.grammar_suggestion}")

            # Cognitive & Difficulty Ratings
            st.markdown(f"**Bloom Level:** {a.bloom_level} (Confidence: {int(a.bloom_confidence*100)}%)")
            st.markdown(f"**Estimated Difficulty:** {a.difficulty} (Confidence: {int(a.difficulty_confidence*100)}%)")
            st.markdown(f"**Mapped CO:** {a.mapped_co} (Confidence: {int(a.co_confidence*100)}%)")

        st.markdown("---")

        # Section 3: AI Improvement & Teacher Decision (Requirement 3: AI ASSISTS TEACHER NEVER REPLACES)
        st.subheader("🤖 AI Suggested Improvement")
        edited_suggestion = st.text_area(
            "Review or Edit AI Suggested Improvement:",
            value=a.suggested_improvement,
            height=100
        )

        st.markdown("#### Teacher Review Action")
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

        with col_btn1:
            if st.button("✅ Accept Suggestion", key=f"acc_{q.id}", type="primary"):
                db_handler.record_decision(TeacherDecision(
                    question_id=q.id,
                    recommendation_type="AI Improvement",
                    decision="Accept",
                    edited_content=edited_suggestion
                ))
                st.success("Decision recorded: Accepted suggestion!")

        with col_btn2:
            if st.button("✏ Edit & Accept", key=f"edt_{q.id}"):
                db_handler.record_decision(TeacherDecision(
                    question_id=q.id,
                    recommendation_type="AI Improvement",
                    decision="Edit",
                    edited_content=edited_suggestion
                ))
                st.success("Decision recorded: Edited & accepted!")

        with col_btn3:
            if st.button("❌ Reject Suggestion", key=f"rej_{q.id}"):
                db_handler.record_decision(TeacherDecision(
                    question_id=q.id,
                    recommendation_type="AI Improvement",
                    decision="Reject",
                    edited_content=None
                ))
                st.warning("Decision recorded: Rejected suggestion.")

        with col_btn4:
            if st.button("👁 Ignore Flag", key=f"ign_{q.id}"):
                db_handler.record_decision(TeacherDecision(
                    question_id=q.id,
                    recommendation_type="Quality Flag",
                    decision="Ignore",
                    edited_content=None
                ))
                st.info("Decision recorded: Ignored flag.")
