"""
EduGuard AI - Exact and Semantic Duplicate Detection Module
"""
import numpy as np
from typing import List, Dict, Tuple
from models import Question, DuplicateGroup
from eduguard_config import SIMILARITY_NEAR_IDENTICAL, SIMILARITY_NEAR_DUPLICATE
from modules.preprocessing import normalize_text


def detect_duplicates(
    questions: List[Question],
    similarity_matrix: np.ndarray
) -> Tuple[Dict[str, Dict[str, any]], List[DuplicateGroup]]:
    """
    Analyzes questions using precomputed cosine similarity matrix.
    Returns:
      1. Map of question_id -> {
             'duplicate_status': "Exact Duplicate" | "Near Duplicate" | "Unique",
             'similar_q_id': str | None,
             'similarity_score': float
         }
      2. List of DuplicateGroup dataclasses.
    """
    N = len(questions)
    normalized_texts = [normalize_text(q.text) for q in questions]

    analysis_results = {}
    duplicate_groups = []
    visited = set()

    for i in range(N):
        q1 = questions[i]
        q1_norm = normalized_texts[i]

        best_sim = 0.0
        best_match_id = None
        exact_match_id = None

        for j in range(N):
            if i == j:
                continue
            q2 = questions[j]
            q2_norm = normalized_texts[j]

            # 1. Check exact match
            if q1_norm and q1_norm == q2_norm:
                exact_match_id = q2.id
                best_sim = 1.0
                best_match_id = q2.id
                break

            # 2. Check semantic similarity
            sim = float(similarity_matrix[i, j])
            if sim > best_sim:
                best_sim = sim
                best_match_id = q2.id

        # Determine classification
        if exact_match_id:
            status = "Exact Duplicate"
        elif best_sim >= SIMILARITY_NEAR_IDENTICAL:
            status = "Near Duplicate"
        elif best_sim >= SIMILARITY_NEAR_DUPLICATE:
            status = "Near Duplicate"
        else:
            status = "Unique"

        analysis_results[q1.id] = {
            "duplicate_status": status,
            "similar_q_id": best_match_id if status != "Unique" else None,
            "similarity_score": round(best_sim * 100, 1) if status != "Unique" else 0.0
        }

    # Group duplicate clusters
    group_counter = 1
    for i in range(N):
        if i in visited:
            continue
        q1 = questions[i]
        q1_norm = normalized_texts[i]
        cluster_indices = [i]

        for j in range(i + 1, N):
            if j in visited:
                continue
            q2_norm = normalized_texts[j]
            sim = float(similarity_matrix[i, j])

            if (q1_norm and q1_norm == q2_norm) or sim >= SIMILARITY_NEAR_DUPLICATE:
                cluster_indices.append(j)
                visited.add(j)

        if len(cluster_indices) > 1:
            visited.add(i)
            cluster_q_ids = [questions[idx].id for idx in cluster_indices]
            # Check if all in cluster have identical normalized text
            is_exact = all(normalized_texts[idx] == q1_norm for idx in cluster_indices)
            status = "Exact Duplicate" if is_exact else "Near Duplicate"

            duplicate_groups.append(DuplicateGroup(
                group_id=group_counter,
                primary_question_id=cluster_q_ids[0],
                duplicate_question_ids=cluster_q_ids[1:],
                similarity_score=round(float(similarity_matrix[i, cluster_indices[1]]) * 100, 1),
                status=status
            ))
            group_counter += 1

    return analysis_results, duplicate_groups
