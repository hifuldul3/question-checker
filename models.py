"""
EduGuard AI - Data Models and Dataclasses
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class Question:
    id: str
    text: str
    marks: float
    topic: str
    question_type: str = "Descriptive"
    bank_id: str = "default_bank"


@dataclass
class QuestionAnalysis:
    question_id: str
    original_text: str
    normalized_text: str
    duplicate_status: str  # "Unique", "Near Duplicate", "Exact Duplicate"
    similar_question_id: Optional[str] = None
    similarity_score: float = 0.0
    ambiguity_score: float = 0.0  # 0 to 100
    ambiguity_issue: str = ""
    ambiguity_reason: str = ""
    grammar_score: float = 100.0  # 0 to 100
    grammar_issue: str = ""
    grammar_suggestion: str = ""
    relevance_score: float = 100.0  # 0 to 100
    relevance_status: str = "In Syllabus"  # "In Syllabus", "Potentially Out of Syllabus"
    primary_concept: str = "General"
    secondary_concept: str = ""
    bloom_level: str = "Understand"
    bloom_confidence: float = 0.80
    difficulty: str = "Medium"
    difficulty_confidence: float = 0.75
    quality_score: float = 85.0
    quality_breakdown: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""
    suggested_improvement: str = ""
    mapped_co: str = "CO1"
    co_confidence: float = 0.80
    co_is_manual: bool = False


@dataclass
class CourseOutcome:
    code: str  # e.g., "CO1"
    description: str


@dataclass
class DuplicateGroup:
    group_id: int
    primary_question_id: str
    duplicate_question_ids: List[str]
    similarity_score: float
    status: str  # "Exact Duplicate" or "Near Duplicate"


@dataclass
class TeacherDecision:
    question_id: str
    recommendation_type: str  # e.g., "Duplicate", "Grammar", "Ambiguity", "Improvement", "Optimization"
    decision: str  # "Accept", "Edit", "Reject", "Ignore"
    edited_content: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AssessmentConstraint:
    title: str = "End Semester Examination"
    num_questions: int = 10
    total_marks: float = 50.0
    bloom_distribution: Dict[str, float] = field(default_factory=lambda: {
        "Remember": 20.0,
        "Understand": 25.0,
        "Apply": 25.0,
        "Analyze": 15.0,
        "Evaluate": 10.0,
        "Create": 5.0
    })
    difficulty_distribution: Dict[str, float] = field(default_factory=lambda: {
        "Easy": 30.0,
        "Medium": 50.0,
        "Hard": 20.0
    })
    co_requirements: Dict[str, float] = field(default_factory=dict)
    topic_requirements: Dict[str, float] = field(default_factory=dict)


@dataclass
class AssessmentHealthBreakdown:
    total_health: float
    quality_score: float
    syllabus_coverage: float
    concept_coverage: float
    co_alignment: float
    bloom_balance: float
    difficulty_balance: float
    diversity_score: float
    warnings: List[str] = field(default_factory=list)


@dataclass
class OptimizationCandidate:
    original_question_id: str
    candidate_question_id: str
    reason: str
    current_health: float
    predicted_health: float
    improvement_delta: float
