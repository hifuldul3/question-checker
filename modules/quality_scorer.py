"""
EduGuard AI - Question Quality Scoring Module
"""
from typing import Dict, Tuple
from eduguard_config import QUALITY_WEIGHTS


def calculate_question_quality(
    clarity_score: float,
    grammar_score: float,
    structure_score: float,
    relevance_score: float,
    originality_score: float,
    completeness_score: float
) -> Tuple[float, Dict[str, float]]:
    """
    Computes weighted quality score (0..100) and component breakdown.
    Returns:
      (total_quality_score, breakdown_dict)
    """
    w = QUALITY_WEIGHTS

    breakdown = {
        "clarity": round(clarity_score, 1),
        "grammar": round(grammar_score, 1),
        "structure": round(structure_score, 1),
        "relevance": round(relevance_score, 1),
        "originality": round(originality_score, 1),
        "completeness": round(completeness_score, 1)
    }

    total_score = (
        w["clarity"] * breakdown["clarity"] +
        w["grammar"] * breakdown["grammar"] +
        w["structure"] * breakdown["structure"] +
        w["relevance"] * breakdown["relevance"] +
        w["originality"] * breakdown["originality"] +
        w["completeness"] * breakdown["completeness"]
    )

    final_quality = max(0.0, min(100.0, round(total_score, 1)))
    return final_quality, breakdown
