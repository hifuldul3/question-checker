"""
EduGuard AI - Syllabus Relevance Analyzer
"""
from typing import Tuple, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from modules.preprocessing import normalize_text


def analyze_syllabus_relevance(
    question_text: str,
    syllabus_text: str
) -> Tuple[float, str, float]:
    """
    Compares a question against syllabus text.
    Returns:
      (relevance_score [0..100], relevance_status ["In Syllabus" | "Potentially Out of Syllabus"], confidence [0..1])
    """
    if not syllabus_text or not syllabus_text.strip():
        # Default if no syllabus provided
        return 100.0, "In Syllabus", 1.0

    q_norm = normalize_text(question_text)
    s_norm = normalize_text(syllabus_text)

    if not q_norm:
        return 0.0, "Potentially Out of Syllabus", 0.90

    # Extract syllabus units / bullet points
    syllabus_lines = [normalize_text(line) for line in syllabus_text.splitlines() if len(line.strip()) > 5]
    if not syllabus_lines:
        syllabus_lines = [s_norm]

    # Compute similarity against syllabus sections using TF-IDF / keyword overlap
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([q_norm] + syllabus_lines)
        sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        max_sim = float(np.max(sim_scores)) if len(sim_scores) > 0 else 0.0
    except Exception:
        # Keyword fallback
        q_tokens = set(q_norm.split())
        s_tokens = set(s_norm.split())
        overlap = q_tokens.intersection(s_tokens)
        max_sim = len(overlap) / max(1, len(q_tokens))

    # Convert similarity [0..1] to relevance percentage
    relevance_pct = min(100.0, round(max_sim * 130.0, 1))  # Boost factor for TF-IDF

    if max_sim >= 0.15 or relevance_pct >= 45.0:
        status = "In Syllabus"
        confidence = round(0.70 + (max_sim * 0.30), 2)
    else:
        status = "Potentially Out of Syllabus"
        confidence = round(0.75 + ((0.15 - max_sim) * 1.5), 2)
        confidence = min(0.95, max(0.60, confidence))

    return max(15.0, relevance_pct), status, confidence
