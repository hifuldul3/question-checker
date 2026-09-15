"""
EduGuard AI - AI Question Improvement Generator
"""
import re


def generate_question_improvement(
    original_text: str,
    bloom_level: str,
    concept: str,
    duplicate_status: str,
    ambiguity_issue: str,
    grammar_issue: str
) -> str:
    """
    Generates an improved question suggestion preserving key educational intent.
    """
    text = original_text.strip()
    if not text:
        return "Please enter a valid question prompt."

    # 1. If duplicate issue: transform into scenario or application question
    if duplicate_status in ["Exact Duplicate", "Near Duplicate"]:
        return (
            f"Given a real-world scenario involving {concept}, apply the appropriate principles to solve "
            f"the problem. Describe each step in detail."
        )

    # 2. If ambiguous (e.g. short / vague)
    if "Missing Context" in ambiguity_issue or "Undefined Reference" in ambiguity_issue:
        return (
            f"In the context of {concept}, explain the core mechanism, key components, "
            f"and practical applications. Provide a concrete example to illustrate your explanation."
        )

    # 3. If grammar/punctuation issue
    if grammar_issue and grammar_issue != "Clean Syntax":
        fixed_text = text
        if fixed_text and not fixed_text[0].isupper():
            fixed_text = fixed_text[0].upper() + fixed_text[1:]
        if fixed_text and fixed_text[-1] not in ["?", ".", ":"]:
            fixed_text += "?"
        return fixed_text

    # 4. Enhance low-level Remember question to higher Bloom level if applicable
    if bloom_level == "Remember" and len(text.split()) < 6:
        return f"Define {concept}. Provide a detailed real-world example illustrating its importance in database system design."

    return text
