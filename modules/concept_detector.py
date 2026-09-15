"""
EduGuard AI - Concept Detection and Keyword Extraction Module
"""
import re
from typing import Tuple, List

# Common domain concept taxonomy dictionary
DOMAIN_CONCEPTS = [
    "Normalization", "Functional Dependency", "Primary Key", "Foreign Key",
    "Candidate Key", "Super Key", "Relational Model", "ER Diagram",
    "ACID Properties", "Transactions", "Concurrency Control", "Locking Protocol",
    "Two-Phase Locking", "Deadlock", "SQL Queries", "Joins", "Grouping & Aggregation",
    "Indexing", "B-Tree Index", "B+ Tree Index", "Relational Algebra",
    "Query Optimization", "Query Processing", "Recovery", "Write Ahead Logging",
    "Shadow Paging", "NoSQL", "Document Store", "CAP Theorem", "Database Security",
    "Views", "Data Independence", "Database Architecture"
]


def detect_concepts(question_text: str, topic_hint: str = "General") -> Tuple[str, str]:
    """
    Detects primary and secondary concepts from question text and topic hint.
    Returns:
      (primary_concept, secondary_concept)
    """
    text = question_text.strip()
    norm = text.lower()
    
    matches = []
    for concept in DOMAIN_CONCEPTS:
        c_norm = concept.lower()
        if c_norm in norm:
            matches.append(concept)

    if matches:
        primary = matches[0]
        secondary = matches[1] if len(matches) > 1 else ""
    else:
        # Fallback to topic hint or capitalized terms
        primary = topic_hint if topic_hint and topic_hint != "General" else "Database Core"
        secondary = ""

    return primary, secondary
