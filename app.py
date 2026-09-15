"""
EduGuard AI - Main Streamlit Application Entry Point
"""
import streamlit as st
import numpy as np
from pathlib import Path

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="EduGuard AI - Question Bank Quality Assurance",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Separate Box per Navigation Row
st.markdown(
    """
    <style>
    /* Hide default Streamlit sidebar navigation list */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Sidebar Navigation Container: Flex column with spacing */
    [data-testid="stSidebar"] .stRadio > div {
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
    }

    /* Individual Separate Box Card for Every Row */
    [data-testid="stSidebar"] .stRadio label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        margin-bottom: 2px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Hover State for Rows */
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.12) !important;
        border-color: #3b82f6 !important;
    }

    /* Active Selected Row Box */
    [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
        background-color: #1d4ed8 !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 4px 12px rgba(29, 78, 216, 0.4) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Imports after page config
from eduguard_config import DEFAULT_TEACHER_USER, DEFAULT_TEACHER_PASS, SAMPLE_CSV_PATH, SAMPLE_SYLLABUS_PATH, SAMPLE_COS_PATH
from database import DatabaseHandler
from models import Question, QuestionAnalysis, CourseOutcome, TeacherDecision
from modules.file_loader import load_question_bank_csv, load_course_outcomes
from modules.preprocessing import normalize_text, preprocess_question
from modules.embeddings import get_embedding_engine
from modules.duplicate_detector import detect_duplicates
from modules.ambiguity_detector import analyze_ambiguity
from modules.grammar_checker import check_grammar_and_structure
from modules.syllabus_analyzer import analyze_syllabus_relevance
from modules.concept_detector import detect_concepts
from modules.bloom_classifier import classify_bloom_level
from modules.difficulty_estimator import estimate_difficulty
from modules.quality_scorer import calculate_question_quality
from modules.improvement_generator import generate_question_improvement
from modules.co_mapper import map_question_to_co
from modules.coverage_analyzer import analyze_question_bank_coverage

# View Render Imports
from views.dashboard import render_dashboard
from views.upload import render_upload_page
from views.question_analysis import render_question_analysis_page
from views.question_details import render_question_details_page
from views.coverage import render_coverage_page
from views.assessment_builder import render_assessment_builder_page
from views.assessment_health import render_assessment_health_page
from views.optimizer import render_optimizer_page
from views.reports import render_reports_page


# Cached AI Embedding Engine Resource
@st.cache_resource
def get_cached_embedding_engine():
    return get_embedding_engine()


# Initialize Session State
def init_session_state():
    if "db_handler" not in st.session_state:
        st.session_state["db_handler"] = DatabaseHandler()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "questions" not in st.session_state:
        st.session_state["questions"] = []

    if "analyses" not in st.session_state:
        st.session_state["analyses"] = {}

    if "coverage_metrics" not in st.session_state:
        st.session_state["coverage_metrics"] = {}

    if "syllabus_text" not in st.session_state:
        if SAMPLE_SYLLABUS_PATH.exists():
            st.session_state["syllabus_text"] = SAMPLE_SYLLABUS_PATH.read_text(encoding="utf-8")
        else:
            st.session_state["syllabus_text"] = ""

    if "course_outcomes" not in st.session_state:
        if SAMPLE_COS_PATH.exists():
            co_text = SAMPLE_COS_PATH.read_text(encoding="utf-8")
            st.session_state["course_outcomes"] = load_course_outcomes(co_text)
        else:
            st.session_state["course_outcomes"] = []


def run_pipeline(questions: list[Question], bank_name: str = "Demo Question Bank"):
    """
    Executes end-to-end EduGuard AI analysis pipeline on a list of questions.
    """
    if not questions:
        return

    db_handler = st.session_state["db_handler"]
    engine = get_cached_embedding_engine()
    cos = st.session_state.get("course_outcomes", [])
    syllabus_text = st.session_state.get("syllabus_text", "")

    # Save Bank to DB
    db_handler.save_question_bank("default_bank", bank_name, bank_name, questions)

    # 1. Single-pass Embeddings & Cosine Similarity Matrix Generation
    texts = [q.text for q in questions]
    sim_matrix = engine.compute_similarity_matrix(texts)

    # 2. Duplicate Detection
    dup_results, dup_groups = detect_duplicates(questions, sim_matrix)

    # 3. Item-level Analysis Loop
    analyses = {}
    for q in questions:
        orig, norm, tokens = preprocess_question(q.text)

        # Ambiguity
        amb_score, amb_issue, amb_reason, amb_sug = analyze_ambiguity(q.text)

        # Grammar & Structure
        gram_score, gram_issue, gram_sug = check_grammar_and_structure(q.text)

        # Syllabus Relevance
        rel_score, rel_status, rel_conf = analyze_syllabus_relevance(q.text, syllabus_text)

        # Concepts
        p_concept, s_concept = detect_concepts(q.text, q.topic)

        # Bloom's Taxonomy
        b_level, b_conf = classify_bloom_level(q.text, q.question_type)

        # Difficulty Estimation
        diff_level, diff_conf = estimate_difficulty(q.text, q.marks, b_level, q.question_type)

        # CO Mapping
        co_code, co_conf = map_question_to_co(q.text, cos, engine)

        # Duplicate Status
        dup_info = dup_results.get(q.id, {"duplicate_status": "Unique", "similar_q_id": None, "similarity_score": 0.0})

        # Quality Score Calculation
        clarity_score = max(0.0, 100.0 - amb_score)
        struct_score = gram_score
        originality_score = 100.0 if dup_info["duplicate_status"] == "Unique" else (100.0 - dup_info["similarity_score"])
        completeness_score = 100.0 if len(tokens) >= 5 else 60.0

        q_quality, quality_breakdown = calculate_question_quality(
            clarity_score, gram_score, struct_score, rel_score, originality_score, completeness_score
        )

        # AI Improvement Suggestion
        improvement_text = generate_question_improvement(
            q.text, b_level, p_concept, dup_info["duplicate_status"], amb_issue, gram_issue
        )

        explanation = f"Question quality score is {q_quality}/100. "
        if dup_info["duplicate_status"] != "Unique":
            explanation += f"Flagged as {dup_info['duplicate_status']} with {dup_info['similar_q_id']}. "
        if amb_score > 0:
            explanation += f"Ambiguity detected: {amb_issue}. "
        if gram_score < 100:
            explanation += f"Grammar issue: {gram_issue}. "

        analyses[q.id] = QuestionAnalysis(
            question_id=q.id,
            original_text=orig,
            normalized_text=norm,
            duplicate_status=dup_info["duplicate_status"],
            similar_question_id=dup_info["similar_q_id"],
            similarity_score=dup_info["similarity_score"],
            ambiguity_score=amb_score,
            ambiguity_issue=amb_issue,
            ambiguity_reason=amb_reason,
            grammar_score=gram_score,
            grammar_issue=gram_issue,
            grammar_suggestion=gram_sug,
            relevance_score=rel_score,
            relevance_status=rel_status,
            primary_concept=p_concept,
            secondary_concept=s_concept,
            bloom_level=b_level,
            bloom_confidence=b_conf,
            difficulty=diff_level,
            difficulty_confidence=diff_conf,
            quality_score=q_quality,
            quality_breakdown=quality_breakdown,
            explanation=explanation,
            suggested_improvement=improvement_text,
            mapped_co=co_code,
            co_confidence=co_conf
        )

    # Save to SQLite Database
    db_handler.save_analysis(list(analyses.values()))

    # Compute Whole Bank Coverage Metrics
    coverage = analyze_question_bank_coverage(questions, analyses)

    st.session_state["questions"] = questions
    st.session_state["analyses"] = analyses
    st.session_state["coverage_metrics"] = coverage


def load_demo_data():
    """Loads 50-question sample CSV dataset."""
    if SAMPLE_CSV_PATH.exists():
        questions = load_question_bank_csv(str(SAMPLE_CSV_PATH))
        run_pipeline(questions, "Built-in 50-Question Demo Dataset")


def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown(
            """
            <div style='text-align: center; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
                <h1 style='color: #1e3a8a; margin-bottom: 0;'>EduGuard AI</h1>
                <p style='color: #6b7280; font-weight: bold;'>Teacher Portal Authentication</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)

        user = st.text_input("Username", value=DEFAULT_TEACHER_USER)
        password = st.text_input("Password", type="password", value=DEFAULT_TEACHER_PASS)

        if st.button("🔐 Login to EduGuard AI", type="primary", use_container_width=True):
            db = st.session_state["db_handler"]
            if db.verify_teacher(user, password):
                st.session_state["logged_in"] = True
                st.session_state["teacher_user"] = user
                load_demo_data()
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")


def main():
    init_session_state()

    if not st.session_state["logged_in"]:
        render_login()
        return

    # Sidebar Navigation
    with st.sidebar:
        st.markdown(
            """
            <h2 style='color:#1e3a8a;'>🎓 EduGuard AI</h2>
            <p style='font-size:12px; color:#6b7280;'>Assessment Quality Assurance</p>
            """,
            unsafe_allow_html=True
        )
        st.markdown("---")

        page = st.radio(
            "Navigation Menu",
            [
                "Dashboard",
                "Upload & Config",
                "Question Analysis",
                "Question Details & Review",
                "Coverage & CO Mapping",
                "Assessment Builder",
                "Assessment Health",
                "What-If Optimizer",
                "Reports & Export"
            ]
        )

        st.markdown("---")
        st.caption(f"Logged in as: **{st.session_state.get('teacher_user', 'teacher')}**")
        if st.button("Logout", use_container_width=True):
            st.session_state["logged_in"] = False
            st.rerun()

    questions = st.session_state["questions"]
    analyses = st.session_state["analyses"]
    coverage_metrics = st.session_state["coverage_metrics"]
    health_metrics = st.session_state.get("assessment_health")
    db_handler = st.session_state["db_handler"]

    # Router
    if page == "Dashboard":
        render_dashboard(questions, analyses, coverage_metrics, health_metrics)
    elif page == "Upload & Config":
        render_upload_page(
            on_new_data_loaded_callback=lambda qs, name: run_pipeline(qs, name),
            load_demo_callback=load_demo_data
        )
    elif page == "Question Analysis":
        render_question_analysis_page(questions, analyses)
    elif page == "Question Details & Review":
        render_question_details_page(questions, analyses, db_handler)
    elif page == "Coverage & CO Mapping":
        render_coverage_page(questions, analyses, coverage_metrics, db_handler)
    elif page == "Assessment Builder":
        render_assessment_builder_page(questions, analyses, db_handler)
    elif page == "Assessment Health":
        render_assessment_health_page(analyses)
    elif page == "What-If Optimizer":
        render_optimizer_page(questions, analyses, db_handler)
    elif page == "Reports & Export":
        render_reports_page(questions, analyses, coverage_metrics, db_handler)


if __name__ == "__main__":
    main()
