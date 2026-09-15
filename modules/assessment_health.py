"""
EduGuard AI - Assessment Health Score and Balance Diagnostic Engine
"""
from typing import List, Dict, Tuple
from models import Question, QuestionAnalysis, AssessmentConstraint, AssessmentHealthBreakdown
from eduguard_config import HEALTH_WEIGHTS, BLOOM_LEVELS
from modules.coverage_analyzer import analyze_question_bank_coverage


def calculate_assessment_health(
    assessment_questions: List[Question],
    analyses: Dict[str, QuestionAnalysis],
    constraints: AssessmentConstraint,
    syllabus_text: str = ""
) -> AssessmentHealthBreakdown:
    """
    Computes Assessment Health Score (0..100) and balance metrics.
    """
    total_q = len(assessment_questions)
    if total_q == 0:
        return AssessmentHealthBreakdown(
            total_health=0.0,
            quality_score=0.0,
            syllabus_coverage=0.0,
            concept_coverage=0.0,
            co_alignment=0.0,
            bloom_balance=0.0,
            difficulty_balance=0.0,
            diversity_score=0.0,
            warnings=["Assessment paper has no questions."]
        )

    # 1. Quality Score
    q_scores = [analyses[q.id].quality_score for q in assessment_questions if q.id in analyses]
    avg_quality = round(sum(q_scores) / len(q_scores), 1) if q_scores else 80.0

    # 2. Coverage analysis of assessment subset
    coverage = analyze_question_bank_coverage(assessment_questions, analyses)

    syllabus_cov = round(100.0 - coverage["out_of_syllabus_pct"], 1)
    concept_cov = min(100.0, round(len(coverage["concept_coverage"]) * 20.0, 1))

    # 3. CO Alignment (Check if all COs are represented)
    co_dist = coverage["co_coverage"]
    co_alignment = min(100.0, round(len(co_dist) * 20.0, 1))

    # 4. Bloom Balance calculation (Deviation from target distribution)
    actual_bloom = coverage["bloom_distribution"]
    target_bloom = constraints.bloom_distribution
    bloom_dev = sum(abs(actual_bloom.get(b, 0.0) - target_bloom.get(b, 0.0)) for b in BLOOM_LEVELS)
    bloom_balance = max(0.0, round(100.0 - (bloom_dev * 0.5), 1))

    # 5. Difficulty Balance calculation
    actual_diff = coverage["difficulty_distribution"]
    target_diff = constraints.difficulty_distribution
    diff_dev = sum(abs(actual_diff.get(d, 0.0) - target_diff.get(d, 0.0)) for d in ["Easy", "Medium", "Hard"])
    difficulty_balance = max(0.0, round(100.0 - (diff_dev * 0.6), 1))

    # 6. Diversity Score
    diversity_score = coverage["question_diversity_score"]

    # Calculate overall Health Score
    w = HEALTH_WEIGHTS
    total_health = (
        w["quality"] * avg_quality +
        w["syllabus"] * syllabus_cov +
        w["concept"] * concept_cov +
        w["co_alignment"] * co_alignment +
        w["bloom_balance"] * bloom_balance +
        w["difficulty_balance"] * difficulty_balance +
        w["diversity"] * diversity_score
    )

    final_health = max(0.0, min(100.0, round(total_health, 1)))

    # Generate Balance Warnings
    warnings = []
    if actual_bloom.get("Remember", 0) > 40.0:
        warnings.append("⚠ Too many 'Remember' level questions (>40% of assessment).")
    if actual_bloom.get("Apply", 0) < 15.0:
        warnings.append("⚠ Insufficient 'Apply' level problem-solving questions (<15%).")
    if actual_diff.get("Easy", 0) > 50.0:
        warnings.append("⚠ Assessment difficulty is too easy (>50% Easy questions).")
    if actual_diff.get("Hard", 0) == 0.0:
        warnings.append("⚠ No 'Hard' difficulty questions present to challenge top performers.")
    if coverage["duplicate_pct"] > 0:
        warnings.append("⚠ Assessment contains duplicate or near-identical questions.")

    return AssessmentHealthBreakdown(
        total_health=final_health,
        quality_score=avg_quality,
        syllabus_coverage=syllabus_cov,
        concept_coverage=concept_cov,
        co_alignment=co_alignment,
        bloom_balance=bloom_balance,
        difficulty_balance=difficulty_balance,
        diversity_score=diversity_score,
        warnings=warnings
    )
