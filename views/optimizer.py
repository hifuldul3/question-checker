"""
EduGuard AI - What-If Optimizer View
"""
import streamlit as st
from modules.optimizer import run_what_if_optimizer
from modules.assessment_health import calculate_assessment_health
from models import TeacherDecision


def render_optimizer_page(question_bank, analyses, db_handler):
    st.title("What-If Assessment Optimizer")
    st.markdown("Simulate question replacements from the bank to optimize examination balance and maximize Assessment Health Score.")

    active_qs = st.session_state.get("active_assessment", [])
    constraints = st.session_state.get("assessment_constraints")

    if not active_qs or not constraints:
        st.info("No active assessment found. Please construct an assessment paper first.")
        return

    syllabus_text = st.session_state.get("syllabus_text", "")
    current_health_obj = calculate_assessment_health(active_qs, analyses, constraints, syllabus_text)
    current_health = current_health_obj.total_health

    st.subheader(f"Current Assessment Health: {current_health} / 100")

    if st.button("🔄 Run What-If Optimization Simulation", type="primary"):
        cands = run_what_if_optimizer(active_qs, question_bank, analyses, constraints, syllabus_text)
        st.session_state["optimization_candidates"] = cands
        st.success(f"Simulation completed! Found {len(cands)} potential replacement recommendations.")

    candidates = st.session_state.get("optimization_candidates", [])

    if not candidates:
        st.info("Click 'Run What-If Optimization Simulation' above to search for replacement candidates.")
        return

    st.markdown(f"### Recommended Replacements ({len(candidates)} Available)")

    for idx, cand in enumerate(candidates):
        orig_q = next((q for q in active_qs if q.id == cand.original_question_id), None)
        cand_q = next((q for q in question_bank if q.id == cand.candidate_question_id), None)

        if not orig_q or not cand_q:
            continue

        with st.expander(f"Recommendation #{idx+1}: Replace [{orig_q.id}] with [{cand_q.id}] (Health Improvement: +{cand.improvement_delta})", expanded=(idx==0)):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### CURRENT QUESTION")
                st.info(f"**[{orig_q.id}]** {orig_q.text}")
                st.markdown(f"**Problem Identified:** {cand.reason}")

            with col2:
                st.markdown("#### RECOMMENDED ALTERNATIVE")
                st.success(f"**[{cand_q.id}]** {cand_q.text}")
                st.markdown(f"**Topic:** {cand_q.topic} | **Marks:** {cand_q.marks}")

            st.markdown("---")
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Current Health", f"{cand.current_health} / 100")
            m_col2.metric("Predicted Health", f"{cand.predicted_health} / 100", delta=f"+{cand.improvement_delta}")
            m_col3.metric("Expected Delta", f"+{cand.improvement_delta} points")

            st.markdown("#### Teacher Optimization Review Action")
            btn_col1, btn_col2, btn_col3 = st.columns(3)

            with btn_col1:
                if st.button(f"✅ Accept Replacement ({cand.original_question_id} → {cand.candidate_question_id})", key=f"opt_acc_{idx}", type="primary"):
                    # Apply substitution to active assessment
                    q_idx = next(i for i, q in enumerate(active_qs) if q.id == cand.original_question_id)
                    active_qs[q_idx] = cand_q
                    st.session_state["active_assessment"] = active_qs

                    # Record decision audit trail
                    db_handler.record_decision(TeacherDecision(
                        question_id=cand.original_question_id,
                        recommendation_type="What-If Optimization",
                        decision="Accept",
                        edited_content=f"Replaced {cand.original_question_id} with {cand.candidate_question_id}"
                    ))
                    st.success(f"Applied replacement! Active assessment updated.")
                    st.rerun()

            with btn_col2:
                if st.button(f"✏ Edit Candidate Question", key=f"opt_edt_{idx}"):
                    db_handler.record_decision(TeacherDecision(
                        question_id=cand.candidate_question_id,
                        recommendation_type="What-If Optimization",
                        decision="Edit",
                        edited_content=cand_q.text
                    ))
                    st.info("Recorded edit request for candidate question.")

            with btn_col3:
                if st.button(f"❌ Reject Replacement", key=f"opt_rej_{idx}"):
                    db_handler.record_decision(TeacherDecision(
                        question_id=cand.original_question_id,
                        recommendation_type="What-If Optimization",
                        decision="Reject",
                        edited_content=None
                    ))
                    st.warning("Replacement rejected. Original question retained.")
