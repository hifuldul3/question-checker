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
            pdf_path = DATA_DIR / "sample_question_bank.pdf"
            if pdf_path.exists():
                st.download_button(
                    "📕 Download Sample PDF Bank",
                    data=pdf_path.read_bytes(),
                    file_name="sample_question_bank.pdf",
                    mime="application/pdf",
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
        st.subheader("3. Syllabus & Course Outcomes (CO) Management")
        st.caption("Upload files or paste text for your course syllabus and outcomes. Updating here automatically re-analyzes all questions.")

        # --- Active Status Summary Cards ---
        curr_syl = st.session_state.get("syllabus_text", "")
        curr_cos = st.session_state.get("course_outcomes", [])
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.info(f"📘 **Active Syllabus Status**: {'Configured (' + str(len(curr_syl.split())) + ' words)' if curr_syl.strip() else 'No Syllabus Loaded'}")
        with col_stat2:
            st.info(f"🎯 **Active Course Outcomes**: {len(curr_cos)} COs Loaded ({', '.join([c.code for c in curr_cos[:5]]) if curr_cos else 'None'})")

        st.markdown("---")

        col_s, col_co = st.columns(2)

        # --- SECTION 1: COURSE SYLLABUS ---
        with col_s:
            st.markdown("### 📚 1. Course Syllabus")
            
            if SAMPLE_SYLLABUS_PATH.exists():
                st.download_button(
                    "📥 Download Sample Syllabus File",
                    data=SAMPLE_SYLLABUS_PATH.read_bytes(),
                    file_name="sample_syllabus.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            syl_file = st.file_uploader(
                "Upload Syllabus File (.txt, .pdf, .docx, .csv)", 
                type=["txt", "pdf", "docx", "csv"],
                key="syl_uploader"
            )
            
            # Pre-fill text area with uploaded file content OR active session state
            default_syl_text = curr_syl
            if syl_file is not None:
                from modules.file_loader import extract_text_from_file
                extracted_syl = extract_text_from_file(syl_file.name, syl_file.getvalue())
                if extracted_syl.strip():
                    default_syl_text = extracted_syl
                    st.success(f"Loaded text from {syl_file.name}!")

            syl_text_input = st.text_area(
                "View / Edit / Paste Syllabus Text",
                value=default_syl_text,
                height=180,
                key="syl_text_area",
                help="Type or paste unit topics, concepts, and course content."
            )

            if st.button("💾 Save & Re-Analyze Syllabus", type="primary", use_container_width=True):
                if not syl_text_input.strip():
                    st.error("Syllabus text cannot be empty.")
                else:
                    st.session_state["syllabus_text"] = syl_text_input.strip()
                    # Re-analyze questions if available
                    existing_qs = st.session_state.get("questions", [])
                    if existing_qs:
                        with st.spinner("⚡ Re-analyzing syllabus relevance for all questions..."):
                            on_new_data_loaded_callback(existing_qs, "Updated Syllabus Analysis")
                        st.success(f"Syllabus updated & re-analyzed across {len(existing_qs)} questions!")
                    else:
                        st.success("Syllabus updated successfully!")
                    st.rerun()

        # --- SECTION 2: COURSE OUTCOMES (COs) ---
        with col_co:
            st.markdown("### 🎯 2. Course Outcomes (COs)")
            
            if SAMPLE_COS_PATH.exists():
                st.download_button(
                    "📥 Download Sample COs File",
                    data=SAMPLE_COS_PATH.read_bytes(),
                    file_name="sample_cos.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            co_file = st.file_uploader(
                "Upload Course Outcomes File (.txt, .csv, .pdf, .docx)", 
                type=["txt", "csv", "pdf", "docx"],
                key="co_uploader"
            )

            # Pre-fill CO text area
            default_co_text = "\n".join([f"{c.code}: {c.description}" for c in curr_cos])
            if co_file is not None:
                from modules.file_loader import extract_text_from_file
                extracted_co = extract_text_from_file(co_file.name, co_file.getvalue())
                if extracted_co.strip():
                    default_co_text = extracted_co
                    st.success(f"Loaded outcomes from {co_file.name}!")

            if not default_co_text.strip():
                default_co_text = (
                    "CO1: Understand fundamental concepts of data structures and algorithms.\n"
                    "CO2: Analyze time and space complexity of sorting and searching techniques.\n"
                    "CO3: Apply tree and graph data structures to solve complex engineering problems.\n"
                    "CO4: Evaluate algorithmic performance under constraints.\n"
                    "CO5: Design efficient dynamic programming solutions."
                )

            co_text_input = st.text_area(
                "View / Edit / Paste Course Outcomes (Format: CODE: Description)",
                value=default_co_text,
                height=180,
                key="co_text_area",
                help="Enter one CO per line, e.g. CO1: Description"
            )

            if st.button("💾 Save & Re-Analyze Course Outcomes", type="primary", use_container_width=True):
                if not co_text_input.strip():
                    st.error("Course Outcomes text cannot be empty.")
                else:
                    from modules.file_loader import load_course_outcomes
                    new_cos = load_course_outcomes(co_text_input.strip())
                    if not new_cos:
                        st.error("No valid Course Outcomes found in text.")
                    else:
                        st.session_state["db_handler"].save_course_outcomes(new_cos)
                        st.session_state["course_outcomes"] = new_cos
                        
                        existing_qs = st.session_state.get("questions", [])
                        if existing_qs:
                            with st.spinner("⚡ Re-mapping Course Outcomes (COs) for all questions..."):
                                on_new_data_loaded_callback(existing_qs, "Updated CO Analysis")
                            st.success(f"Loaded {len(new_cos)} COs & re-mapped across {len(existing_qs)} questions!")
                        else:
                            st.success(f"Loaded {len(new_cos)} Course Outcomes successfully!")
                        st.rerun()


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

