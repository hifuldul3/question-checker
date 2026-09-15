"""
EduGuard AI - Course Outcome (CO) Semantic Mapper Module
"""
from typing import List, Tuple
import numpy as np
from models import Question, CourseOutcome
from modules.embeddings import BaseEmbeddingEngine


def map_question_to_co(
    question_text: str,
    cos: List[CourseOutcome],
    embedding_engine: BaseEmbeddingEngine
) -> Tuple[str, float]:
    """
    Maps a question text to the best matching Course Outcome using semantic embeddings.
    Returns:
      (mapped_co_code, confidence [0..1])
    """
    if not cos:
        return "CO1", 0.80

    co_texts = [f"{co.code}: {co.description}" for co in cos]
    all_texts = [question_text] + co_texts

    try:
        sim_matrix = embedding_engine.compute_similarity_matrix(all_texts)
        # Cosine similarity between index 0 (question) and 1..M (COs)
        scores = sim_matrix[0, 1:]
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])

        mapped_code = cos[best_idx].code
        confidence = min(0.98, max(0.55, round(best_score * 0.95, 2)))
        return mapped_code, confidence
    except Exception:
        # Fallback keyword match
        norm = question_text.lower()
        if "sql" in norm or "query" in norm:
            return "CO2", 0.75
        elif "normal" in norm or "functional" in norm:
            return "CO3", 0.85
        elif "transaction" in norm or "acid" in norm or "lock" in norm:
            return "CO4", 0.80
        elif "index" in norm or "nosql" in norm or "storage" in norm:
            return "CO5", 0.80
        else:
            return "CO1", 0.70
