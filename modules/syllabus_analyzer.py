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


def generate_questions_from_syllabus(syllabus_text: str, num_questions: int = 15) -> list:
    """
    Dynamically generates a custom Question Bank directly from uploaded syllabus text.
    Extracts units/topics and creates diverse questions across 2M, 3M, 5M, 10M, and MCQs.
    """
    import re
    from models import Question

    if not syllabus_text or not syllabus_text.strip():
        return []

    lines = [line.strip() for line in syllabus_text.splitlines() if line.strip()]
    topic_units = []
    current_unit = "General Syllabus"
    current_topics = []

    unit_pattern = re.compile(r"^\s*(?:Unit|Module|Chapter)\s*\d*[\:\-]?\s*(.+)$", re.IGNORECASE)

    for line in lines:
        u_match = unit_pattern.match(line)
        if u_match:
            if current_topics:
                topic_units.append((current_unit, current_topics))
                current_topics = []
            current_unit = u_match.group(1).strip()
        else:
            parts = [
                p.strip() for p in re.split(r"[\,\;\.\n]", line) 
                if len(p.strip()) > 3 and not p.strip().lower().startswith(('unit', 'module', 'chapter'))
            ]
            current_topics.extend(parts)

    if current_topics:
        topic_units.append((current_unit, current_topics))

    if not topic_units:
        all_topics = [p.strip() for p in re.split(r"[\,\;\.\n]", syllabus_text) if len(p.strip()) > 3]
        topic_units = [("Syllabus Content", all_topics)]

    generated_qs = []
    q_counter = 1

    mark_patterns = [
        (2.0, "Descriptive", "Define {topic} in 2-3 sentences. State two key properties or applications in {unit}."),
        (3.0, "Descriptive", "Explain the working principle of {topic} with a suitable diagram or example. List 3 key characteristics."),
        (5.0, "Descriptive", "Explain the algorithm/mechanism for {topic} in detail. Trace its step-by-step execution on a sample input and analyze its best-case and worst-case time complexity."),
        (1.0, "MCQ", "Which of the following statements best describes {topic} in {unit}?\n  (A) Basic concept A\n  (B) Core working mechanism [Correct]\n  (C) Alternative concept misattribution\n  (D) Irrelevant system property"),
        (10.0, "Descriptive", "(a) Describe {topic} in {unit} with a neat block diagram and architecture. [4 Marks]\n(b) Solve a comprehensive problem using {topic} and evaluate performance trade-offs. [6 Marks]")
    ]

    p_idx = 0
    while len(generated_qs) < num_questions:
        initial_len = len(generated_qs)
        for unit_name, topics in topic_units:
            for top in topics:
                if len(generated_qs) >= num_questions:
                    break
                marks, q_type, tmpl = mark_patterns[p_idx % len(mark_patterns)]
                p_idx += 1
                q_id = f"SQ{q_counter:03d}"
                q_text = tmpl.format(topic=top, unit=unit_name)
                generated_qs.append(Question(
                    id=q_id,
                    text=q_text,
                    marks=marks,
                    topic=top[:35],
                    question_type=q_type
                ))
                q_counter += 1
        # Safety break if no topics were found
        if len(generated_qs) == initial_len:
            break

    return generated_qs


def analyze_and_suggest_questions_for_syllabus(syllabus_text: str) -> dict:
    """
    Performs comprehensive syllabus analysis and generates structured question suggestions
    grouped unit-by-unit with Bloom level, estimated difficulty, and pedagogical rationale.
    """
    import re

    if not syllabus_text or not syllabus_text.strip():
        return {"units_count": 0, "total_topics": 0, "unit_data": []}

    lines = [line.strip() for line in syllabus_text.splitlines() if line.strip()]
    topic_units = []
    current_unit = "Unit 1: Core Syllabus Concepts"
    current_topics = []

    unit_pattern = re.compile(r"^\s*(?:Unit|Module|Chapter)\s*\d*[\:\-]?\s*(.+)$", re.IGNORECASE)

    for line in lines:
        u_match = unit_pattern.match(line)
        if u_match:
            if current_topics:
                topic_units.append((current_unit, current_topics))
                current_topics = []
            current_unit = u_match.group(1).strip()
        else:
            parts = [
                p.strip() for p in re.split(r"[\,\;\.\n]", line) 
                if len(p.strip()) > 3 and not p.strip().lower().startswith(('unit', 'module', 'chapter'))
            ]
            current_topics.extend(parts)

    if current_topics:
        topic_units.append((current_unit, current_topics))

    if not topic_units:
        all_topics = [p.strip() for p in re.split(r"[\,\;\.\n]", syllabus_text) if len(p.strip()) > 3]
        topic_units = [("General Syllabus Topics", all_topics)]

    suggestions_by_unit = []
    q_counter = 1

    for unit_name, topics in topic_units:
        unit_suggestions = []
        for top in topics:
            # 2 Marks (Remember)
            unit_suggestions.append({
                "id": f"SQ{q_counter:03d}",
                "topic": top[:35],
                "marks": 2.0,
                "type": "Descriptive",
                "bloom": "Remember",
                "difficulty": "Easy",
                "text": f"Define {top} in 2-3 sentences. State two key properties or applications in {unit_name}.",
                "rationale": f"Evaluates foundational recall and basic definition of {top}."
            })
            q_counter += 1

            # 5 Marks (Analyze/Apply)
            unit_suggestions.append({
                "id": f"SQ{q_counter:03d}",
                "topic": top[:35],
                "marks": 5.0,
                "type": "Descriptive",
                "bloom": "Analyze",
                "difficulty": "Medium",
                "text": f"Explain the working principle of {top} in detail. Trace its step-by-step execution on a sample scenario and state its time/space complexity.",
                "rationale": f"Evaluates analytical understanding and execution tracing of {top}."
            })
            q_counter += 1

            # MCQ (1 Mark)
            unit_suggestions.append({
                "id": f"SQ{q_counter:03d}",
                "topic": top[:35],
                "marks": 1.0,
                "type": "MCQ",
                "bloom": "Understand",
                "difficulty": "Easy",
                "text": f"Which of the following statements best describes {top}?\n  (A) Basic concept A\n  (B) Core working mechanism [Correct]\n  (C) Alternative concept misattribution\n  (D) Irrelevant system property",
                "rationale": f"Quick 1-mark multiple choice question on {top}."
            })
            q_counter += 1

        suggestions_by_unit.append({
            "unit_name": unit_name,
            "topics_count": len(topics),
            "suggestions": unit_suggestions
        })

    return {
        "units_count": len(topic_units),
        "total_topics": sum(len(t) for _, t in topic_units),
        "unit_data": suggestions_by_unit
    }


