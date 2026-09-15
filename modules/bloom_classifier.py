"""
EduGuard AI - Bloom's Taxonomy Advisory Classifier
"""
import re
from typing import Tuple
from eduguard_config import BLOOM_VERBS, BLOOM_LEVELS
from modules.preprocessing import normalize_text


def classify_bloom_level(question_text: str, question_type: str = "Descriptive") -> Tuple[str, float]:
    """
    Classifies question text into one of Bloom's Taxonomy cognitive levels.
    Returns:
      (bloom_level, confidence [0..1])
    """
    if not question_text:
        return "Understand", 0.50

    norm = normalize_text(question_text)
    words = norm.split()
    first_two_words = words[:3] if len(words) >= 3 else words

    scores = {level: 0.0 for level in BLOOM_LEVELS}

    # Match verbs in taxonomy
    for level, verbs in BLOOM_VERBS.items():
        for verb in verbs:
            verb_norm = normalize_text(verb)
            # Higher weight if verb appears in beginning of question
            if any(w == verb_norm for w in first_two_words):
                scores[level] += 3.0
            elif verb_norm in norm:
                scores[level] += 1.5

    # Contextual modifiers
    if re.search(r"\b(code|design|construct|develop|build|formulate)\b", norm):
        scores["Create"] += 2.0
    if re.search(r"\b(compare|contrast|differentiate|distinguish|why|examine)\b", norm):
        scores["Analyze"] += 2.0
    if re.search(r"\b(evaluate|justify|critique|rate|judge)\b", norm):
        scores["Evaluate"] += 2.0
    if re.search(r"\b(calculate|compute|solve|given|find)\b", norm):
        scores["Apply"] += 2.5
    if re.search(r"\b(what is|define|list|state|name)\b", norm):
        scores["Remember"] += 2.5

    # Question Type hints
    if question_type in ["Multiple Choice", "True/False"]:
        scores["Remember"] += 0.5
    elif question_type == "Code/Design":
        scores["Create"] += 1.5
    elif question_type == "Numerical":
        scores["Apply"] += 1.5

    best_level = max(scores, key=scores.get)
    max_score = scores[best_level]

    if max_score == 0:
        return "Understand", 0.65

    total_score = sum(scores.values())
    confidence = min(0.95, max(0.60, round(max_score / (total_score + 0.001) + 0.35, 2)))

    return best_level, confidence
