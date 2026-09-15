"""
EduGuard AI - Question Difficulty Estimator
"""
import re
from typing import Tuple
from modules.preprocessing import normalize_text


def estimate_difficulty(
    question_text: str,
    marks: float,
    bloom_level: str,
    question_type: str = "Descriptive"
) -> Tuple[str, float]:
    """
    Estimates difficulty level (Easy, Medium, Hard) and returns confidence.
    Returns:
      (difficulty ["Easy" | "Medium" | "Hard"], confidence [0..1])
    """
    norm = normalize_text(question_text)
    word_count = len(norm.split())

    score = 0.0

    # 1. Marks factor
    if marks <= 2:
        score += 1.0
    elif marks <= 5:
        score += 2.5
    elif marks <= 10:
        score += 4.0
    else:
        score += 5.5

    # 2. Bloom level cognitive factor
    bloom_weights = {
        "Remember": 1.0,
        "Understand": 2.0,
        "Apply": 3.5,
        "Analyze": 4.5,
        "Evaluate": 5.0,
        "Create": 5.5
    }
    score += bloom_weights.get(bloom_level, 2.5)

    # 3. Text & Problem Solving complexity
    if word_count > 25:
        score += 1.5
    if re.search(r"\b(given|suppose|calculate|design|construct|proof|derive|justify|evaluate)\b", norm):
        score += 1.5

    # 4. Question type
    if question_type in ["Multiple Choice", "True/False"]:
        score -= 1.0
    elif question_type in ["Numerical", "Code/Design"]:
        score += 1.5

    # Final mapping
    if score <= 5.0:
        difficulty = "Easy"
        confidence = round(0.70 + (5.0 - score) * 0.04, 2)
    elif score <= 9.0:
        difficulty = "Medium"
        confidence = round(0.75 + (9.0 - abs(7.0 - score)) * 0.02, 2)
    else:
        difficulty = "Hard"
        confidence = round(0.72 + (score - 9.0) * 0.03, 2)

    confidence = min(0.95, max(0.65, confidence))
    return difficulty, confidence
