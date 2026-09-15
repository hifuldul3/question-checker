"""
EduGuard AI - Question Bank & Resource File Loader
"""
import io
import re
import pandas as pd
from typing import List, Tuple, Optional
from models import Question, CourseOutcome


def load_question_bank_csv(file_content: io.BytesIO | str) -> List[Question]:
    """Loads a question bank from CSV file or buffer."""
    df = pd.read_csv(file_content)
    return parse_question_dataframe(df)


def load_question_bank_xlsx(file_content: io.BytesIO | str) -> List[Question]:
    """Loads a question bank from Excel (XLSX) file or buffer."""
    df = pd.read_excel(file_content)
    return parse_question_dataframe(df)


def parse_question_dataframe(df: pd.DataFrame) -> List[Question]:
    """Normalizes column names and parses DataFrame into Question objects."""
    # Column mapping normalization
    col_map = {}
    for col in df.columns:
        c_clean = str(col).strip().lower()
        if "id" in c_clean:
            col_map[col] = "id"
        elif "text" in c_clean or "question" in c_clean and "type" not in c_clean and "id" not in c_clean:
            col_map[col] = "text"
        elif "mark" in c_clean:
            col_map[col] = "marks"
        elif "topic" in c_clean or "subject" in c_clean or "unit" in c_clean:
            col_map[col] = "topic"
        elif "type" in c_clean:
            col_map[col] = "question_type"

    df = df.rename(columns=col_map)

    questions = []
    for idx, row in df.iterrows():
        q_id = str(row.get("id", f"Q{idx+1}")).strip()
        text = str(row.get("text", "")).strip() if pd.notna(row.get("text")) else ""
        
        raw_marks = row.get("marks", 5.0)
        try:
            marks = float(raw_marks) if pd.notna(raw_marks) else 5.0
        except (ValueError, TypeError):
            marks = 5.0

        topic = str(row.get("topic", "General")).strip() if pd.notna(row.get("topic")) else "General"
        q_type = str(row.get("question_type", "Descriptive")).strip() if pd.notna(row.get("question_type")) else "Descriptive"

        questions.append(Question(
            id=q_id,
            text=text,
            marks=marks,
            topic=topic,
            question_type=q_type
        ))
    return questions


def load_question_bank_pdf(file_bytes: bytes) -> List[Question]:
    """Extracts questions from text-based PDF using PyMuPDF / pdfplumber fallback."""
    text_content = ""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text_content += page.get_text() + "\n"
    except Exception:
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    text_content += (page.extract_text() or "") + "\n"
        except Exception:
            text_content = file_bytes.decode("utf-8", errors="ignore")

    return parse_pdf_text_to_questions(text_content)


def parse_pdf_text_to_questions(raw_text: str) -> List[Question]:
    """Parses raw extracted PDF text using common pattern matching."""
    lines = raw_text.splitlines()
    questions = []
    q_counter = 1
    current_q_id = None
    current_text = []

    pattern = re.compile(r"^\s*(?:Q(?:uestion)?\s*(\d+)|(\d+))\s*[\.\:\)]\s*(.+)$", re.IGNORECASE)

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        match = pattern.match(line_str)
        if match:
            if current_q_id and current_text:
                questions.append(Question(
                    id=current_q_id,
                    text=" ".join(current_text).strip(),
                    marks=5.0,
                    topic="General",
                    question_type="Descriptive"
                ))
                current_text = []

            num = match.group(1) or match.group(2)
            current_q_id = f"Q{num}" if num else f"Q{q_counter}"
            q_text_start = match.group(3)
            current_text.append(q_text_start)
            q_counter += 1
        else:
            if current_q_id:
                current_text.append(line_str)

    if current_q_id and current_text:
        questions.append(Question(
            id=current_q_id,
            text=" ".join(current_text).strip(),
            marks=5.0,
            topic="General",
            question_type="Descriptive"
        ))

    return questions


def load_course_outcomes(file_content: str) -> List[CourseOutcome]:
    """Loads Course Outcomes from text/CSV lines."""
    cos = []
    lines = file_content.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            parts = line.split(":", 1)
            code = parts[0].strip()
            desc = parts[1].strip()
        elif "," in line:
            parts = line.split(",", 1)
            code = parts[0].strip()
            desc = parts[1].strip()
        else:
            code = f"CO{len(cos)+1}"
            desc = line
        cos.append(CourseOutcome(code=code, description=desc))
    return cos
