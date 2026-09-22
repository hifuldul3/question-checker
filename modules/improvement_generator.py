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

def extract_concept_from_text(sample_text: str) -> str:
    """Extracts a clean, representative concept phrase from sample question text."""
    clean = re.sub(r'[^\w\s]', '', sample_text).strip()
    words = clean.split()
    stop_words = {
        'what', 'is', 'are', 'explain', 'describe', 'how', 'does', 'why', 'define', 
        'the', 'a', 'an', 'in', 'of', 'to', 'for', 'with', 'and', 'or', 'state', 'give', 'list'
    }
    meaningful = [w for w in words if w.lower() not in stop_words]
    if meaningful:
        return ' '.join(meaningful[:4]).title()
    return clean[:30].title() if clean else 'Target Concept'


def recommend_question_by_sample_and_marks(
    sample_text: str,
    target_marks: float,
    target_type: str,
    topic: str = "General"
) -> list:
    """
    Analyzes sample reference question and generates recommended structural variations 
    tailored to specific target marks (2M, 3M, 5M, 10M) and question type (MCQ, Descriptive, Numerical, Code).
    """
    sample = sample_text.strip()
    concept = extract_concept_from_text(sample)
    topic_str = topic.strip() if topic else "General"
    marks_int = int(target_marks)

    recs = []

    if target_type == "MCQ":
        recs.append({
            "title": f"Structured 4-Option MCQ ({marks_int} Mark)",
            "structure": (
                f"Which of the following statements best describes {concept} in {topic_str}?\n"
                f"  (A) Incorrect definition or secondary characteristic.\n"
                f"  (B) Core definition and primary working mechanism. [Correct]\n"
                f"  (C) Alternative concept misattribution.\n"
                f"  (D) Irrelevant system property."
            ),
            "rationale": "Formatted as a standard 4-option MCQ with clear distractors and identified correct key."
        })
        recs.append({
            "title": f"Application Scenario MCQ ({marks_int} Mark)",
            "structure": (
                f"In a real-world scenario involving {topic_str}, when using {concept}, what is the expected outcome?\n"
                f"  (A) High computational latency.\n"
                f"  (B) Optimal execution and reduced space complexity. [Correct]\n"
                f"  (C) Unhandled runtime exception.\n"
                f"  (D) Memory overflow error."
            ),
            "rationale": "Evaluates practical application and outcome prediction."
        })
    elif target_type == "Numerical":
        recs.append({
            "title": f"{marks_int}-Mark Numerical Problem Structure",
            "structure": (
                f"Given a system operating on {concept} in {topic_str} with input parameters [X = 10 units, Y = 5 units]:\n"
                f"  (a) State the relevant governing formula. [1 Mark]\n"
                f"  (b) Calculate the final output parameter step-by-step. [{max(1, marks_int - 1)} Marks]"
            ),
            "rationale": "Clear numerical problem template with step-by-step marks distribution."
        })
    elif target_type == "Code":
        recs.append({
            "title": f"{marks_int}-Mark Coding / Algorithm Question",
            "structure": (
                f"Write a clean, efficient program/function to implement {concept} in {topic_str}.\n"
                f"  - Include appropriate input/output validation.\n"
                f"  - State time complexity (O-notation) and space complexity.\n"
                f"  - Demonstrate execution on a sample test case. ({marks_int} Marks)"
            ),
            "rationale": "Structured for programming evaluation with complexity and test case requirements."
        })
    else:  # Descriptive
        if target_marks <= 2:
            recs.append({
                "title": "2-Mark Concise Definition & Feature",
                "structure": f"Define {concept} in 2-3 sentences. State two key properties or applications in {topic_str}. (2 Marks)",
                "rationale": "Structured for rapid 2-mark assessment (1 Mark Definition + 1 Mark Key Points)."
            })
            recs.append({
                "title": "2-Mark Direct Comparison Question",
                "structure": f"State two fundamental differences between {concept} and standard alternative methods. (2 Marks)",
                "rationale": "Direct 2-point comparison template for simple grading."
            })
        elif target_marks == 3:
            recs.append({
                "title": "3-Mark Explanation with Example / Diagram",
                "structure": f"Explain the core working principle of {concept} with a suitable diagram or example. List 3 key characteristics. (3 Marks)",
                "rationale": "Balanced 3-mark breakdown (1.5 Marks Explanation + 1.5 Marks Example/Diagram)."
            })
            recs.append({
                "title": "3-Point Analytical Comparison",
                "structure": f"Compare {concept} against an alternative approach across 3 parameters: (i) Working mechanism, (ii) Efficiency, (iii) Use-case. (3 Marks)",
                "rationale": "Structured 3-parameter matrix comparison."
            })
        elif target_marks == 5:
            recs.append({
                "title": "5-Mark Detailed Analytical Question",
                "structure": (
                    f"Explain the working principle of {concept} in detail. "
                    f"Trace its step-by-step execution using a sample input and analyze its best-case and worst-case time complexity. (5 Marks)"
                ),
                "rationale": "Comprehensive 5-mark analytical structure testing higher Bloom taxonomy level (Analyze/Apply)."
            })
            recs.append({
                "title": "5-Mark Multi-Part Question Breakdown",
                "structure": (
                    f"(a) Define {concept} and explain its core components. [2 Marks]\n"
                    f"(b) Illustrate its application with a concrete step-by-step scenario. [3 Marks]"
                ),
                "rationale": "Clear sub-part demarcation ensuring objective marking scheme."
            })
        else:  # 10 Marks or higher
            recs.append({
                "title": f"{marks_int}-Mark Comprehensive Examination Question",
                "structure": (
                    f"(a) Describe {concept} in {topic_str} with a neat block diagram and architecture overview. [4 Marks]\n"
                    f"(b) Develop a step-by-step solution for a complex problem using {concept}. [4 Marks]\n"
                    f"(c) Evaluate trade-offs and performance constraints. [2 Marks]"
                ),
                "rationale": f"End-to-end multi-part question suited for high-weightage ({marks_int} marks) university examinations."
            })

    return recs

