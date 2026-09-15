"""
EduGuard AI - Configuration and Application Constants
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "eduguard.db"
EXPORTS_DIR = BASE_DIR / "exports"

# Ensure required directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Authentication Credentials (Prototype)
DEFAULT_TEACHER_USER = "teacher"
DEFAULT_TEACHER_PASS = "eduguard123"

# AI Model Configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Duplicate Detection Thresholds
SIMILARITY_NEAR_IDENTICAL = 0.90
SIMILARITY_NEAR_DUPLICATE = 0.82

# Quality Scoring Formula Weights (Must sum to 1.0)
QUALITY_WEIGHTS = {
    "clarity": 0.20,
    "grammar": 0.15,
    "structure": 0.15,
    "relevance": 0.20,
    "originality": 0.15,
    "completeness": 0.15,
}

# Assessment Health Formula Weights (Must sum to 1.0)
HEALTH_WEIGHTS = {
    "quality": 0.20,
    "syllabus": 0.15,
    "concept": 0.15,
    "co_alignment": 0.15,
    "bloom_balance": 0.15,
    "difficulty_balance": 0.10,
    "diversity": 0.10,
}

# Bloom's Taxonomy Cognitive Levels & Action Verbs
BLOOM_LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

BLOOM_VERBS = {
    "Remember": ["define", "list", "state", "name", "recall", "identify", "label", "match", "mention", "quote", "select", "what is"],
    "Understand": ["explain", "describe", "discuss", "summarize", "interpret", "classify", "outline", "illustrate", "express", "locate"],
    "Apply": ["apply", "calculate", "compute", "solve", "demonstrate", "construct", "execute", "implement", "use", "determine", "derive"],
    "Analyze": ["analyze", "compare", "contrast", "differentiate", "distinguish", "examine", "investigate", "categorize", "deconstruct", "breakdown"],
    "Evaluate": ["evaluate", "assess", "justify", "critique", "validate", "rate", "appraise", "judge", "defend", "recommend"],
    "Create": ["design", "develop", "formulate", "propose", "synthesize", "build", "invent", "devise", "compose", "plan", "generate"]
}

# Question Types Supported
QUESTION_TYPES = [
    "Descriptive",
    "Short Answer",
    "Multiple Choice",
    "Numerical",
    "True/False",
    "Code/Design"
]

# Sample Dataset Paths
SAMPLE_CSV_PATH = DATA_DIR / "sample_question_bank.csv"
SAMPLE_SYLLABUS_PATH = DATA_DIR / "sample_syllabus.txt"
SAMPLE_COS_PATH = DATA_DIR / "sample_cos.txt"
