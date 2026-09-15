"""
EduGuard AI - Assessment Builder Engine
"""
from typing import List, Dict
from models import Question, QuestionAnalysis, AssessmentConstraint


def build_assessment_paper(
    questions: List[Question],
    analyses: Dict[str, QuestionAnalysis],
    constraints: AssessmentConstraint
) -> List[Question]:
    """
    Selects optimal candidate questions from bank matching constraints.
    """
    if not questions:
        return []

    target_count = min(constraints.num_questions, len(questions))
    selected = []

    # Sort questions prioritizing higher quality score and non-duplicates
    scored_questions = []
    for q in questions:
        a = analyses.get(q.id)
        q_score = a.quality_score if a else 80.0
        # Penalty for duplicates
        if a and a.duplicate_status in ["Exact Duplicate", "Near Duplicate"]:
            q_score -= 25.0
        scored_questions.append((q_score, q))

    scored_questions.sort(key=lambda x: x[0], reverse=True)

    # Simple greedy selection filling target count
    for _, q in scored_questions:
        if len(selected) >= target_count:
            break
        selected.append(q)

    return selected
