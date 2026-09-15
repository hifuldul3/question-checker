"""
EduGuard AI - Grammar, Spelling, and Sentence Structure Analyzer
"""
import re
from typing import Tuple


def check_grammar_and_structure(text: str) -> Tuple[float, str, str]:
    """
    Analyzes question grammar, capitalization, punctuation, and question formulation.
    Returns:
      (grammar_score [0..100], issue, suggestion)
    """
    if not text or not text.strip():
        return 0.0, "Empty Question Text", "Provide valid question text."

    clean_text = text.strip()
    score = 100.0
    issues = []
    suggestions = []

    # 1. Capitalization check (first letter capitalized)
    if not clean_text[0].isupper() and not clean_text[0].isdigit():
        score -= 15.0
        issues.append("Capitalization")
        suggestions.append("Capitalize the first letter of the question.")

    # 2. Terminal punctuation check (Ends with ?, ., or :)
    if clean_text[-1] not in ["?", ".", ":"]:
        score -= 15.0
        issues.append("Missing Terminal Punctuation")
        suggestions.append("Add a closing question mark '?' or period '.'.")

    # 3. Question starter phrasing checks ("what is", "explain", "how", "define", "given")
    first_word = clean_text.split()[0].lower()
    common_starters = ["what", "explain", "describe", "discuss", "define", "calculate", "compute", "design", "differentiate", "compare", "given", "write", "list", "state", "which", "how", "why", "construct", "evaluate", "justfy", "is", "are", "critique"]
    
    # Simple typo check on common question words
    typo_map = {
        "expln": "explain", "waht": "what", "whichh": "which", "defne": "define",
        "calulate": "calculate", "descibe": "describe", "justfy": "justify"
    }
    for word in clean_text.split():
        w_norm = word.lower().strip(".,?:")
        if w_norm in typo_map:
            score -= 20.0
            issues.append(f"Spelling Typo ('{word}')")
            suggestions.append(f"Correct '{word}' to '{typo_map[w_norm]}'.")

    # 4. Spacing anomalies (e.g. double spaces, spaces before punctuation)
    if re.search(r"\s{2,}", clean_text) or re.search(r"\s+[\?\.\,]", clean_text):
        score -= 10.0
        issues.append("Formatting & Spacing")
        suggestions.append("Remove redundant spaces before punctuation marks.")

    # 5. Incomplete sentence structure (Single isolated word)
    if len(clean_text.split()) == 1 and clean_text.isalnum():
        score -= 40.0
        issues.append("Incomplete Question Structure")
        suggestions.append(f"Rephrase as a complete question, e.g., 'What is {clean_text}?'")

    final_score = max(0.0, min(100.0, score))

    if final_score == 100.0:
        return 100.0, "Clean Syntax", "Question has proper capitalization, grammar, and punctuation."
    else:
        issue_str = "; ".join(issues)
        sug_str = " ".join(suggestions)
        return round(final_score, 1), issue_str, sug_str
