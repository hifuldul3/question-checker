"""
EduGuard AI - SQLite Database Handler and Persistence Layer
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from eduguard_config import DB_PATH, DEFAULT_TEACHER_USER, DEFAULT_TEACHER_PASS
from models import Question, QuestionAnalysis, CourseOutcome, TeacherDecision, AssessmentConstraint


class DatabaseHandler:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Creates tables if they do not exist and populates initial default teacher."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Teachers table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 2. Question Banks table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_banks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                file_name TEXT,
                total_questions INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 3. Questions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                bank_id TEXT NOT NULL,
                text TEXT NOT NULL,
                marks REAL NOT NULL,
                topic TEXT NOT NULL,
                question_type TEXT DEFAULT 'Descriptive',
                FOREIGN KEY (bank_id) REFERENCES question_banks(id) ON DELETE CASCADE
            )
            """)

            # 4. Question Analysis table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_analysis (
                question_id TEXT PRIMARY KEY,
                original_text TEXT,
                normalized_text TEXT,
                duplicate_status TEXT,
                similar_question_id TEXT,
                similarity_score REAL,
                ambiguity_score REAL,
                ambiguity_issue TEXT,
                ambiguity_reason TEXT,
                grammar_score REAL,
                grammar_issue TEXT,
                grammar_suggestion TEXT,
                relevance_score REAL,
                relevance_status TEXT,
                primary_concept TEXT,
                secondary_concept TEXT,
                bloom_level TEXT,
                bloom_confidence REAL,
                difficulty TEXT,
                difficulty_confidence REAL,
                quality_score REAL,
                quality_breakdown TEXT,
                explanation TEXT,
                suggested_improvement TEXT,
                mapped_co TEXT,
                co_confidence REAL,
                co_is_manual INTEGER DEFAULT 0,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
            """)

            # 5. Course Outcomes table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_outcomes (
                code TEXT PRIMARY KEY,
                description TEXT NOT NULL
            )
            """)

            # 6. Teacher Decisions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS teacher_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT NOT NULL,
                recommendation_type TEXT NOT NULL,
                decision TEXT NOT NULL,
                edited_content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 7. Assessments table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                total_marks REAL NOT NULL,
                health_score REAL DEFAULT 0.0,
                constraints_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 8. Assessment Questions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessment_questions (
                assessment_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                PRIMARY KEY (assessment_id, question_id),
                FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
            """)

            # Insert default teacher prototype account if not exists
            cursor.execute("SELECT username FROM teachers WHERE username = ?", (DEFAULT_TEACHER_USER,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO teachers (username, password, name) VALUES (?, ?, ?)",
                    (DEFAULT_TEACHER_USER, DEFAULT_TEACHER_PASS, "Prof. Alex Reed")
                )

            conn.commit()

    # --- Teacher Auth Methods ---
    def verify_teacher(self, username: str, password: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password FROM teachers WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if row and row["password"] == password:
                return True
            return False

    # --- Questions & Analysis Storage ---
    def save_question_bank(self, bank_id: str, name: str, file_name: str, questions: List[Question]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO question_banks (id, name, file_name, total_questions) VALUES (?, ?, ?, ?)",
                (bank_id, name, file_name, len(questions))
            )
            for q in questions:
                cursor.execute(
                    "INSERT OR REPLACE INTO questions (id, bank_id, text, marks, topic, question_type) VALUES (?, ?, ?, ?, ?, ?)",
                    (q.id, bank_id, q.text, q.marks, q.topic, q.question_type)
                )
            conn.commit()

    def save_analysis(self, analyses: List[QuestionAnalysis]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for a in analyses:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO question_analysis (
                        question_id, original_text, normalized_text, duplicate_status,
                        similar_question_id, similarity_score, ambiguity_score, ambiguity_issue,
                        ambiguity_reason, grammar_score, grammar_issue, grammar_suggestion,
                        relevance_score, relevance_status, primary_concept, secondary_concept,
                        bloom_level, bloom_confidence, difficulty, difficulty_confidence,
                        quality_score, quality_breakdown, explanation, suggested_improvement,
                        mapped_co, co_confidence, co_is_manual
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        a.question_id, a.original_text, a.normalized_text, a.duplicate_status,
                        a.similar_question_id, a.similarity_score, a.ambiguity_score, a.ambiguity_issue,
                        a.ambiguity_reason, a.grammar_score, a.grammar_issue, a.grammar_suggestion,
                        a.relevance_score, a.relevance_status, a.primary_concept, a.secondary_concept,
                        a.bloom_level, a.bloom_confidence, a.difficulty, a.difficulty_confidence,
                        a.quality_score, json.dumps(a.quality_breakdown), a.explanation, a.suggested_improvement,
                        a.mapped_co, a.co_confidence, 1 if a.co_is_manual else 0
                    )
                )
            conn.commit()

    def get_all_questions(self, bank_id: str = "default_bank") -> List[Question]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions WHERE bank_id = ?", (bank_id,))
            rows = cursor.fetchall()
            return [
                Question(
                    id=r["id"],
                    text=r["text"],
                    marks=r["marks"],
                    topic=r["topic"],
                    question_type=r["question_type"],
                    bank_id=r["bank_id"]
                )
                for r in rows
            ]

    def get_all_analyses(self) -> Dict[str, QuestionAnalysis]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM question_analysis")
            rows = cursor.fetchall()
            results = {}
            for r in rows:
                breakdown = json.loads(r["quality_breakdown"]) if r["quality_breakdown"] else {}
                results[r["question_id"]] = QuestionAnalysis(
                    question_id=r["question_id"],
                    original_text=r["original_text"] or "",
                    normalized_text=r["normalized_text"] or "",
                    duplicate_status=r["duplicate_status"] or "Unique",
                    similar_question_id=r["similar_question_id"],
                    similarity_score=r["similarity_score"] or 0.0,
                    ambiguity_score=r["ambiguity_score"] or 0.0,
                    ambiguity_issue=r["ambiguity_issue"] or "",
                    ambiguity_reason=r["ambiguity_reason"] or "",
                    grammar_score=r["grammar_score"] or 100.0,
                    grammar_issue=r["grammar_issue"] or "",
                    grammar_suggestion=r["grammar_suggestion"] or "",
                    relevance_score=r["relevance_score"] or 100.0,
                    relevance_status=r["relevance_status"] or "In Syllabus",
                    primary_concept=r["primary_concept"] or "General",
                    secondary_concept=r["secondary_concept"] or "",
                    bloom_level=r["bloom_level"] or "Understand",
                    bloom_confidence=r["bloom_confidence"] or 0.80,
                    difficulty=r["difficulty"] or "Medium",
                    difficulty_confidence=r["difficulty_confidence"] or 0.75,
                    quality_score=r["quality_score"] or 85.0,
                    quality_breakdown=breakdown,
                    explanation=r["explanation"] or "",
                    suggested_improvement=r["suggested_improvement"] or "",
                    mapped_co=r["mapped_co"] or "CO1",
                    co_confidence=r["co_confidence"] or 0.80,
                    co_is_manual=bool(r["co_is_manual"])
                )
            return results

    # --- Decisions & Audit ---
    def record_decision(self, decision: TeacherDecision):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO teacher_decisions (question_id, recommendation_type, decision, edited_content, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (decision.question_id, decision.recommendation_type, decision.decision, decision.edited_content, decision.timestamp)
            )
            conn.commit()

    def get_decisions(self) -> List[TeacherDecision]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teacher_decisions ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            return [
                TeacherDecision(
                    question_id=r["question_id"],
                    recommendation_type=r["recommendation_type"],
                    decision=r["decision"],
                    edited_content=r["edited_content"],
                    timestamp=r["timestamp"]
                )
                for r in rows
            ]

    # --- Course Outcomes ---
    def save_course_outcomes(self, cos: List[CourseOutcome]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for co in cos:
                cursor.execute(
                    "INSERT OR REPLACE INTO course_outcomes (code, description) VALUES (?, ?)",
                    (co.code, co.description)
                )
            conn.commit()

    def get_course_outcomes(self) -> List[CourseOutcome]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM course_outcomes ORDER BY code ASC")
            rows = cursor.fetchall()
            return [CourseOutcome(code=r["code"], description=r["description"]) for r in rows]
