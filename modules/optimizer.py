"""
EduGuard AI - What-If Assessment Optimizer Engine
"""
from typing import List, Dict, Tuple, Optional
from models import Question, QuestionAnalysis, AssessmentConstraint, OptimizationCandidate
from modules.assessment_health import calculate_assessment_health


def run_what_if_optimizer(
    current_assessment: List[Question],
    question_bank: List[Question],
    analyses: Dict[str, QuestionAnalysis],
    constraints: AssessmentConstraint,
    syllabus_text: str = ""
) -> List[OptimizationCandidate]:
    """
    Executes What-If optimization algorithm:
    1. Computes baseline health score.
    2. Identifies weak questions in current assessment (duplicates, low quality, or contribution to Bloom imbalance).
    3. Searches full question bank for candidate replacements not in current assessment.
    4. Temporarily substitutes candidates, recalculates health score, computes delta.
    5. Ranks and returns top optimization candidates.
    """
    if not current_assessment or not question_bank:
        return []

    baseline_health = calculate_assessment_health(
        current_assessment, analyses, constraints, syllabus_text
    ).total_health

    current_ids = {q.id for q in current_assessment}
    bank_candidates = [q for q in question_bank if q.id not in current_ids]

    if not bank_candidates:
        return []

    recommendations = []

    # Iterate through current assessment items to find candidates for replacement
    for i, orig_q in enumerate(current_assessment):
        a_orig = analyses.get(orig_q.id)
        
        # Determine why this question might be problematic
        reasons = []
        if a_orig:
            if a_orig.quality_score < 75.0:
                reasons.append(f"Low quality score ({a_orig.quality_score}/100)")
            if a_orig.duplicate_status in ["Exact Duplicate", "Near Duplicate"]:
                reasons.append(f"Duplicate status ({a_orig.duplicate_status})")
            if a_orig.ambiguity_score > 30.0:
                reasons.append(f"High ambiguity score ({a_orig.ambiguity_score}%)")

        # If question has a defect or bloom imbalance, search replacement candidate
        if not reasons:
            reasons.append(f"Cognitive level imbalance ({a_orig.bloom_level if a_orig else 'Remember'})")

        problem_desc = "; ".join(reasons)

        best_cand = None
        best_pred_health = baseline_health

        for cand_q in bank_candidates:
            a_cand = analyses.get(cand_q.id)
            # Skip low quality candidates
            if a_cand and a_cand.quality_score < 75.0:
                continue

            # Simulate temporary replacement
            temp_assessment = list(current_assessment)
            temp_assessment[i] = cand_q

            pred_health = calculate_assessment_health(
                temp_assessment, analyses, constraints, syllabus_text
            ).total_health

            if pred_health > best_pred_health:
                best_pred_health = pred_health
                best_cand = cand_q

        if best_cand and (best_pred_health - baseline_health) > 1.0:
            delta = round(best_pred_health - baseline_health, 1)
            recommendations.append(OptimizationCandidate(
                original_question_id=orig_q.id,
                candidate_question_id=best_cand.id,
                reason=problem_desc,
                current_health=baseline_health,
                predicted_health=best_pred_health,
                improvement_delta=delta
            ))

    # Sort recommendations by highest health improvement delta
    recommendations.sort(key=lambda x: x.improvement_delta, reverse=True)
    return recommendations
