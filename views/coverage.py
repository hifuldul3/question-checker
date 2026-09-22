"""
EduGuard AI - Coverage View
"""
import streamlit as st
import pandas as pd
from utils.helpers import create_bloom_chart, create_difficulty_chart


def render_coverage_page(questions, analyses, coverage_metrics, db_handler):
    st.title("Coverage & Learning Outcome Mapping")
    st.markdown("Analyze Topic Coverage, Concept Coverage, Bloom Distribution, and Course Outcome (CO) Alignments.")

    if not questions:
        st.info("No questions loaded. Please upload a question bank or load demo data.")
        return

    st.metric("Overall Question Diversity Score", f"{coverage_metrics.get('question_diversity_score', 0)} / 100")

    tab1, tab2, tab3, tab4 = st.tabs([
        "CO Semantic Mapping", 
        "Topic & Concept Coverage", 
        "Taxonomy Distributions", 
        "🧠 Syllabus Analysis & AI Question Suggestions"
    ])

    with tab1:
        st.subheader("Course Outcome (CO) Alignment & Manual Override")
        st.write("AI automatically maps questions to Course Outcomes using semantic similarity. Teachers can manually override any mapping.")

        cos = st.session_state.get("course_outcomes", [])
        co_options = [co.code for co in cos] if cos else ["CO1", "CO2", "CO3", "CO4", "CO5"]

        co_rows = []
        for q in questions:
            a = analyses.get(q.id)
            co_rows.append({
                "Q ID": q.id,
                "Question Text": q.text[:55] + "...",
                "Topic": q.topic,
                "Current Mapped CO": a.mapped_co if a else "CO1",
                "Confidence": f"{int(a.co_confidence*100)}%" if a else "80%",
                "Source": "Manual Override" if a and a.co_is_manual else "AI Semantic Map"
            })

        df_co = pd.DataFrame(co_rows)
        st.dataframe(df_co, use_container_width=True, hide_index=True)

        st.markdown("#### Manual CO Override Form")
        col_q, col_co, col_btn = st.columns([2, 1, 1])
        with col_q:
            override_q_id = st.selectbox("Select Question ID", [q.id for q in questions], key="cov_override_q_select")
        with col_co:
            new_co = st.selectbox("Select Target CO", co_options, key="cov_override_co_select")
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Apply Manual CO Override", key="btn_apply_co_override"):
                if override_q_id in analyses:
                    analyses[override_q_id].mapped_co = new_co
                    analyses[override_q_id].co_is_manual = True
                    db_handler.save_analysis(list(analyses.values()))
                    st.success(f"Updated {override_q_id} mapping to {new_co}!")
                    st.rerun()

    with tab2:
        col_t, col_c = st.columns(2)
        with col_t:
            st.subheader("Topic Coverage (%)")
            top_df = pd.DataFrame([{"Topic": k, "Coverage %": v} for k, v in coverage_metrics.get("topic_coverage", {}).items()])
            st.dataframe(top_df, use_container_width=True, hide_index=True)

        with col_c:
            st.subheader("Concept Coverage (%)")
            con_df = pd.DataFrame([{"Concept": k, "Coverage %": v} for k, v in coverage_metrics.get("concept_coverage", {}).items()])
            st.dataframe(con_df, use_container_width=True, hide_index=True)

    with tab3:
        col_b, col_d = st.columns(2)
        with col_b:
            b_fig = create_bloom_chart(coverage_metrics.get("bloom_distribution", {}))
            st.plotly_chart(b_fig, use_container_width=True)
        with col_d:
            d_fig = create_difficulty_chart(coverage_metrics.get("difficulty_distribution", {}))
            st.plotly_chart(d_fig, use_container_width=True)

    with tab4:
        st.subheader("🧠 Syllabus Analysis & Smart AI Question Recommender")
        st.caption("AI analyzes your uploaded course syllabus and suggests high-quality questions unit-by-unit.")

        syllabus_text = st.session_state.get("syllabus_text", "")
        if not syllabus_text.strip():
            st.warning("No syllabus loaded yet. Please upload a syllabus in 'Upload & Config' -> Tab 4.")
        else:
            from modules.syllabus_analyzer import analyze_and_suggest_questions_for_syllabus
            res = analyze_and_suggest_questions_for_syllabus(syllabus_text)

            col_syl_info1, col_syl_info2 = st.columns(2)
            with col_syl_info1:
                st.info(f"📘 **Syllabus Units Detected**: {res['units_count']} Units")
            with col_syl_info2:
                st.info(f"🎯 **Total Extracted Topics**: {res['total_topics']} Key Topics")

            st.markdown("---")

            for unit in res.get("unit_data", []):
                st.markdown(f"### 📚 {unit['unit_name']} ({unit['topics_count']} Topics)")
                
                for s in unit.get("suggestions", []):
                    with st.expander(f"[{s['id']}] {s['topic']} — {s['bloom']} ({int(s['marks'])}M {s['type']})"):
                        st.markdown(f"**Question Prompt:**")
                        st.code(s["text"], language="text")
                        st.markdown(f"💡 **AI Rationale:** {s['rationale']}")
                        
                        col_act1, col_act2 = st.columns([1, 3])
                        with col_act1:
                            if st.button(f"➕ Add {s['id']} to Bank", key=f"add_syl_q_{s['id']}", type="secondary", use_container_width=True):
                                from models import Question
                                new_q = Question(
                                    id=f"SQ_{len(questions)+1:03d}",
                                    text=s["text"],
                                    marks=s["marks"],
                                    topic=s["topic"],
                                    question_type=s["type"]
                                )
                                questions.append(new_q)
                                st.session_state["questions"] = questions
                                st.success(f"Added {new_q.id} to question bank!")
                                st.rerun()

                st.markdown("---")

