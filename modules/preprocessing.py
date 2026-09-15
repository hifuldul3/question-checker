"""
EduGuard AI - Text Preprocessing and Normalization Module
"""
import re
import string
from typing import List, Tuple

# Default minimal stop words list for fallback token filtering
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what", "which",
    "this", "that", "these", "those", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "to", "from", "in", "out",
    "on", "off", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don",
    "should", "now"
}


def normalize_text(text: str) -> str:
    """
    Normalizes raw question text:
    1. Lowercase conversion
    2. Remove extra spaces
    3. Normalize punctuation
    """
    if not text:
        return ""
    text_lower = text.lower()
    # Normalize punctuation and extra spaces
    text_clean = re.sub(r"[^\w\s]", " ", text_lower)
    text_clean = re.sub(r"\s+", " ", text_clean).strip()
    return text_clean


def tokenize(text: str, remove_stopwords: bool = False) -> List[str]:
    """Tokenizes text into words."""
    norm = normalize_text(text)
    tokens = norm.split()
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOP_WORDS]
    return tokens


def preprocess_question(original_text: str) -> Tuple[str, str, List[str]]:
    """
    Returns:
    (original_text, normalized_text, tokens)
    """
    orig = original_text.strip() if original_text else ""
    norm = normalize_text(orig)
    tokens = tokenize(orig, remove_stopwords=True)
    return orig, norm, tokens
