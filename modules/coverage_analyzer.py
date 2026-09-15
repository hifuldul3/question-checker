"""
EduGuard AI - Whole Question Bank Coverage & Diversity Analyzer
"""
from typing import List, Dict, Any
from models import Question, QuestionAnalysis
from eduguard_config import BLOOM_LEVELS


def analyze_question_bank_coverage(
    questions: List[Question],
    analyses: Dict[str, QuestionAnalysis]
) -> Dict[str, Any]:
    """
    Computes aggregate metrics across the question bank.
    """
    total_q = len(questions)
    if total_q == 0:
        return {
            "total_questions": 0,
            "average_quality": 0.0,
            "duplicate_pct": 0.0,
            "low_quality_pct": 0.0,
            "out_of_syllabus_pct": 0.0,
            "topic_coverage": {},
            "concept_coverage": {},
            "co_coverage": {},
            "bloom_distribution": {b: 0.0 for b in BLOOM_LEVELS},
            "difficulty_distribution": {"Easy": 0.0, "Medium": 0.0, "Hard": 0.0},
            "question_diversity_score": 0.0
        }

    # Initialize counters
    topic_counts = {}
    concept_counts = {}
    co_counts = {}
    bloom_counts = {b: 0 for b in BLOOM_LEVELS}
    difficulty_counts = {"Easy": 0, "Medium": 0, "Hard": 0}

    total_quality = 0.0
    duplicate_count = 0
    low_quality_count = 0
    out_syllabus_count = 0

    for q in questions:
        # Topic
        t = q.topic or "General"
        topic_counts[t] = topic_counts.get(t, 0) + 1

        a = analyses.get(q.id)
        if a:
            total_quality += a.quality_score

            if a.quality_score < 70.0:
                low_quality_count += 1

            if a.duplicate_status in ["Exact Duplicate", "Near Duplicate"]:
                duplicate_count += 1

            if a.relevance_status == "Potentially Out of Syllabus":
                out_syllabus_count += 1

            # Concept
            c = a.primary_concept or "General"
            concept_counts[c] = concept_counts.get(c, 0) + 1

            # CO
            co = a.mapped_co or "CO1"
            co_counts[co] = co_counts.get(co, 0) + 1

            # Bloom
            bl = a.bloom_level if a.bloom_level in BLOOM_LEVELS else "Understand"
            bloom_counts[bl] = bloom_counts.get(bl, 0) + 1

            # Difficulty
            diff = a.difficulty if a.difficulty in difficulty_counts else "Medium"
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

    # Percentages
    avg_quality = round(total_quality / total_q, 1)
    duplicate_pct = round((duplicate_count / total_q) * 100, 1)
    low_quality_pct = round((low_quality_count / total_q) * 100, 1)
    out_syllabus_pct = round((out_syllabus_count / total_q) * 100, 1)

    topic_pct = {k: round((v / total_q) * 100, 1) for k, v in topic_counts.items()}
    concept_pct = {k: round((v / total_q) * 100, 1) for k, v in concept_counts.items()}
    co_pct = {k: round((v / total_q) * 100, 1) for k, v in co_counts.items()}
    bloom_pct = {k: round((v / total_q) * 100, 1) for k, v in bloom_counts.items()}
    diff_pct = {k: round((v / total_q) * 100, 1) for k, v in difficulty_counts.items()}

    # Diversity score calculation (0..100)
    topic_div = min(100.0, len(topic_counts) * 20.0)
    bloom_div = min(100.0, (sum(1 for v in bloom_counts.values() if v > 0) / len(BLOOM_LEVELS)) * 100.0)
    diff_div = min(100.0, (sum(1 for v in difficulty_counts.values() if v > 0) / 3.0) * 100.0)
    dup_penalty = duplicate_pct * 0.5

    diversity_score = max(0.0, min(100.0, round((0.4 * topic_div + 0.3 * bloom_div + 0.3 * diff_div) - dup_penalty, 1)))

    return {
        "total_questions": total_q,
        "average_quality": avg_quality,
        "duplicate_pct": duplicate_pct,
        "low_quality_pct": low_quality_pct,
        "out_of_syllabus_pct": out_syllabus_pct,
        "topic_coverage": topic_pct,
        "concept_coverage": concept_pct,
        "co_coverage": co_pct,
        "bloom_distribution": bloom_pct,
        "difficulty_distribution": diff_pct,
        "question_diversity_score": diversity_score
    }
