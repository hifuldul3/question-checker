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
    """
    Parses raw extracted PDF text into Question objects.
    Extracts Question IDs, question text, embedded marks, topic headers, and question types.
    """
    lines = raw_text.splitlines()
    questions = []
    current_topic = "General"
    current_q_id = None
    current_text = []
    current_marks = 5.0
    q_counter = 1

    q_pattern = re.compile(r"^\s*(?:Q(?:uestion)?[\.\s]*(\d+)|(\d+))\s*[\.\:\)\-]\s*(.+)$", re.IGNORECASE)
    marks_pattern = re.compile(r"(?:\[|\()(\d+(?:\.\d+)?)\s*(?:marks?|m)?(?:\]|\))", re.IGNORECASE)
    topic_pattern = re.compile(r"^\s*(?:Unit|Module|Topic|Chapter)\s*\d*[\:\-]\s*(.+)$", re.IGNORECASE)

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        # Check for Topic / Unit header line
        t_match = topic_pattern.match(line_str)
        if t_match:
            current_topic = t_match.group(1).strip()
            continue

        # Check for new Question start line
        q_match = q_pattern.match(line_str)
        if q_match:
            if current_q_id and current_text:
                full_text = " ".join(current_text).strip()
                q_type = "MCQ" if any(opt in full_text for opt in ["(A)", "(a)", "A)", "B)"]) else "Descriptive"
                questions.append(Question(
                    id=current_q_id,
                    text=full_text,
                    marks=current_marks,
                    topic=current_topic,
                    question_type=q_type
                ))
                current_text = []
                current_marks = 5.0

            num = q_match.group(1) or q_match.group(2)
            current_q_id = f"Q{num}" if num else f"Q{q_counter}"
            rest = q_match.group(3)

            # Check if marks specified in title line
            m_match = marks_pattern.search(rest)
            if m_match:
                try:
                    current_marks = float(m_match.group(1))
                except ValueError:
                    current_marks = 5.0

            current_text.append(rest)
            q_counter += 1
        else:
            if current_q_id:
                m_match = marks_pattern.search(line_str)
                if m_match:
                    try:
                        current_marks = float(m_match.group(1))
                    except ValueError:
                        pass
                current_text.append(line_str)

    # Append last question
    if current_q_id and current_text:
        full_text = " ".join(current_text).strip()
        q_type = "MCQ" if any(opt in full_text for opt in ["(A)", "(a)", "A)", "B)"]) else "Descriptive"
        questions.append(Question(
            id=current_q_id,
            text=full_text,
            marks=current_marks,
            topic=current_topic,
            question_type=q_type
        ))

    # Fallback if no numbered questions detected: split by non-empty blocks
    if not questions and raw_text.strip():
        paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
        for idx, p in enumerate(paragraphs, 1):
            if len(p) >= 10:
                questions.append(Question(
                    id=f"Q{idx}",
                    text=p,
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


def extract_text_from_file(file_name: str, file_bytes: bytes) -> str:
    """Extracts plain text content from uploaded TXT, CSV, PDF, or DOCX files."""
    ext = file_name.split(".")[-1].lower() if "." in file_name else ""
    if ext == "pdf":
        try:
            import pymupdf
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            return "\n".join([page.get_text() for page in doc])
        except Exception:
            try:
                import fitz
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                return "\n".join([page.get_text() for page in doc])
            except Exception:
                return file_bytes.decode("utf-8", errors="ignore")
    elif ext == "docx":
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            return file_bytes.decode("utf-8", errors="ignore")
    else:
        return file_bytes.decode("utf-8", errors="ignore")

