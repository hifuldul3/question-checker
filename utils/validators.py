"""
EduGuard AI - Data Validation and Error Reporting Utility
"""
from typing import List, Tuple
from models import Question


def validate_question_bank(questions: List[Question]) -> Tuple[List[Question], List[str]]:
    """
    Validates question bank entries.
    Returns:
      (valid_questions, error_warnings_list)
    """
    errors = []
    seen_ids = set()
    cleaned_questions = []

    for idx, q in enumerate(questions):
        q_id = q.id or f"Q{idx+1}"

        # 1. Missing question text check
        if not q.text or not q.text.strip():
            errors.append(f"⚠ {q_id} has empty or invalid question text.")
            continue

        # 2. Duplicate question ID check
        if q_id in seen_ids:
            new_id = f"{q_id}_dup_{idx+1}"
            errors.append(f"⚠ Question ID {q_id} appears multiple times. Auto-assigned ID: {new_id}")
            q.id = new_id
        seen_ids.add(q.id)

        # 3. Invalid marks check
        if q.marks <= 0:
            errors.append(f"⚠ {q.id} has invalid marks ({q.marks}). Resetting to default 5.0 marks.")
            q.marks = 5.0

        # 4. Empty topic check
        if not q.topic or not q.topic.strip():
            q.topic = "General"

        cleaned_questions.append(q)

    return cleaned_questions, errors
