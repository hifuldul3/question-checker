"""
EduGuard AI - Advisory Ambiguity Detection Module
"""
import re
from typing import Tuple


def analyze_ambiguity(question_text: str) -> Tuple[float, str, str, str]:
    """
    Analyzes question for ambiguity patterns.
    Returns:
      (ambiguity_score [0..100], issue, reason, suggestion)
    """
    text = question_text.strip()
    if not text:
        return 100.0, "Empty Question Text", "Question contains no readable text.", "Provide complete question text."

    norm = text.lower()
    score = 0.0
    issues = []
    reasons = []
    suggestions = []

    # 1. Missing context / extremely short questions
    if len(text.split()) < 4:
        score += 50.0
        issues.append("Missing Context")
        reasons.append("The question is extremely short and lacks explicit subject context.")
        suggestions.append("Expand the question prompt to specify the exact domain topic.")

    # 2. Vague demonstrative references ("this", "the above", "the following", "that method")
    vague_ref_match = re.search(r"\b(explain|discuss|describe|calculate|analyze)\s+(this|the above|the following|it|that)\b", norm)
    if vague_ref_match:
        score += 45.0
        issues.append("Undefined Reference")
        reasons.append(f"Question relies on relative reference '{vague_ref_match.group(0)}' without providing the referenced material.")
        suggestions.append("Replace vague pronoun references with explicit entity or scenario definitions.")

    # 3. Undefined broad terminology ("discuss the system", "explain the method")
    broad_terms = re.search(r"\b(the system|the method|the process|the result|the data)\b", norm)
    if broad_terms and len(text.split()) < 8:
        score += 30.0
        issues.append("Undefined Terminology")
        reasons.append(f"Generic phrase '{broad_terms.group(0)}' is used without clarifying which specific system or method is intended.")
        suggestions.append("Name the specific system, algorithm, or methodology being evaluated.")

    # 4. Calculation without parameters/numbers
    if re.search(r"\b(calculate|compute|find the result|solve)\b", norm) and not re.search(r"\d+|\b(where|given|if|relation|matrix|table)\b", norm):
        score += 40.0
        issues.append("Missing Information / Parameters")
        reasons.append("Question asks for calculation or computation but does not supply numerical input or given variables.")
        suggestions.append("Provide the required dataset, formula parameters, or scenario values.")

    final_score = min(100.0, score)

    if final_score == 0.0:
        return 0.0, "Clear Question", "Question provides clear context and explicit scope.", "No changes required."
    else:
        primary_issue = "; ".join(issues)
        primary_reason = " ".join(reasons)
        primary_suggestion = " ".join(suggestions)
        return round(final_score, 1), primary_issue, primary_reason, primary_suggestion
