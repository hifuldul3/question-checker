"""
EduGuard AI - Question Bank & Syllabus Upload Interface View
"""
import streamlit as st
import io
import pandas as pd
from modules.file_loader import (
    load_question_bank_csv,
    load_question_bank_xlsx,
    load_question_bank_pdf,
    load_course_outcomes
)
from utils.validators import validate_question_bank
from eduguard_config import SAMPLE_CSV_PATH, SAMPLE_SYLLABUS_PATH, SAMPLE_COS_PATH, DATA_DIR


def render_upload_page(on_new_data_loaded_callback, load_demo_callback):
    st.title("Question Bank & Configuration Upload")
    st.markdown("Upload custom question banks (CSV, XLSX, PDF), course syllabus, and course outcomes.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Question Bank Upload", 
        "Direct Input (Quick Add)", 
        "Syllabus & CO Upload", 
        "Demo Data Quick Start"
    ])

    with tab1:
        st.subheader("1. Upload Question Bank File")

        col_up, col_dl = st.columns([2, 1])

        with col_up:
            uploaded_file = st.file_uploader(
                "Choose a CSV, XLSX, or PDF Question Bank file",
                type=["csv", "xlsx", "pdf"]
            )

        with col_dl:
            st.markdown("#### 📥 Download Sample Files")
            st.caption("Download pre-formatted sample files to test custom file upload functionality.")
            if SAMPLE_CSV_PATH.exists():
                st.download_button(
                    "📄 Download Sample CSV Bank",
                    data=SAMPLE_CSV_PATH.read_bytes(),
                    file_name="sample_question_bank.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            xlsx_path = DATA_DIR / "sample_question_bank.xlsx"
            if xlsx_path.exists():
                st.download_button(
                    "📊 Download Sample XLSX Bank",
                    data=xlsx_path.read_bytes(),
                    file_name="sample_question_bank.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        if uploaded_file is not None:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            try:
                if file_ext == "csv":
                    raw_questions = load_question_bank_csv(uploaded_file)
                elif file_ext == "xlsx":
                    raw_questions = load_question_bank_xlsx(uploaded_file)
                elif file_ext == "pdf":
                    raw_questions = load_question_bank_pdf(uploaded_file.getvalue())
                else:
                    st.error("Unsupported file format.")
                    raw_questions = []

                if raw_questions:
                    valid_questions, val_errors = validate_question_bank(raw_questions)

                    if val_errors:
                        st.warning(f"Validation encountered {len(val_errors)} warnings:")
                        for err in val_errors:
                            st.write(err)

                    if st.button("Process & Analyze Uploaded Question Bank", type="primary"):
                        with st.spinner("⚡ Processing & Analyzing Question Bank..."):
                            on_new_data_loaded_callback(valid_questions, uploaded_file.name)
                        st.success(f"Successfully loaded and analyzed {len(valid_questions)} questions from {uploaded_file.name}!")
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    with tab2:
        st.subheader("2. Direct Question Input & Instant Analysis")
        st.caption("Type or paste custom questions directly to get immediate quality metrics and AI feedback.")
        
        with st.form("direct_input_form"):
            col_q1, col_q2 = st.columns([1, 1])
            with col_q1:
                q_id_input = st.text_input("Question ID", value=f"Q{len(st.session_state.get('questions', [])) + 1}")
                q_marks_input = st.number_input("Marks", min_value=1.0, max_value=100.0, value=5.0, step=1.0)
            with col_q2:
                q_topic_input = st.text_input("Topic / Unit", value="Data Structures & Algorithms")
                q_type_input = st.selectbox("Question Type", ["Descriptive", "Multiple Choice", "Numerical", "Code"])

            q_text_input = st.text_area(
                "Enter Question Text", 
                value="What is a Binary Search Tree? Explain its insertion and deletion algorithms with time complexity.",
                height=100
            )

            submit_direct = st.form_submit_button("⚡ Analyze Question Instantly", type="primary", use_container_width=True)

        if submit_direct:
            if not q_text_input.strip():
                st.error("Please enter a question text.")
            else:
                from models import Question
                new_q = Question(
                    id=q_id_input.strip(),
                    text=q_text_input.strip(),
                    marks=q_marks_input,
                    topic=q_topic_input.strip(),
                    question_type=q_type_input
                )
                existing_qs = list(st.session_state.get("questions", []))
                # Add or replace question in session state list
                updated_qs = [q for q in existing_qs if q.id != new_q.id] + [new_q]
                with st.spinner("⚡ Running AI quality analysis..."):
                    on_new_data_loaded_callback(updated_qs, "Custom Input Question Bank")
                st.success(f"Question {new_q.id} analyzed successfully!")
                st.rerun()

    with tab3:
        st.subheader("3. Upload Syllabus & Course Outcomes (Optional)")

        col_s, col_co = st.columns(2)
        with col_s:
            st.markdown("#### Course Syllabus")
            if SAMPLE_SYLLABUS_PATH.exists():
                st.download_button(
                    "📥 Download Sample Syllabus (.txt)",
                    data=SAMPLE_SYLLABUS_PATH.read_bytes(),
                    file_name="sample_syllabus.txt",
                    mime="text/plain"
                )
            syllabus_file = st.file_uploader("Upload Syllabus (.txt)", type=["txt"])
            syllabus_text_input = st.text_area("Or Paste Syllabus Text", height=150)
            if st.button("Update Syllabus"):
                s_text = ""
                if syllabus_file:
                    s_text = syllabus_file.getvalue().decode("utf-8", errors="ignore")
                elif syllabus_text_input:
                    s_text = syllabus_text_input
                if s_text:
                    st.session_state["syllabus_text"] = s_text
                    st.success("Syllabus updated successfully!")

        with col_co:
            st.markdown("#### Course Outcomes (COs)")
            if SAMPLE_COS_PATH.exists():
                st.download_button(
                    "📥 Download Sample COs (.txt)",
                    data=SAMPLE_COS_PATH.read_bytes(),
                    file_name="sample_cos.txt",
                    mime="text/plain"
                )
            co_file = st.file_uploader("Upload Course Outcomes (.txt / .csv)", type=["txt", "csv"])
            if st.button("Update Course Outcomes"):
                if co_file:
                    co_text = co_file.getvalue().decode("utf-8", errors="ignore")
                    cos = load_course_outcomes(co_text)
                    st.session_state["db_handler"].save_course_outcomes(cos)
                    st.session_state["course_outcomes"] = cos
                    st.success(f"Loaded {len(cos)} Course Outcomes!")

    with tab4:
        st.subheader("4. Instant Demo Setup")
        st.info(
            "Click below to immediately populate the application with a built-in 50-question database "
            "containing exact duplicates, near duplicates, ambiguous items, grammar errors, Bloom levels, and CO mappings."
        )
        if st.button("🚀 Load 50-Question Demo Dataset", type="primary"):
            with st.spinner("⚡ Loading 50-Question Demo Bank..."):
                load_demo_callback()
            st.success("Demo dataset loaded into EduGuard AI!")
            st.rerun()

