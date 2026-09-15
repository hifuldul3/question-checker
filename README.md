# EduGuard AI

### AI-Powered Question Bank Quality Assurance and Assessment Optimization System

EduGuard AI is a complete, modular, locally runnable web application built for educators to evaluate, score, improve, build, and optimize academic question banks and examination papers.

---

## Key Features

1. **Teacher Decision Guarantee**: AI strictly assists the teacher and never auto-modifies, auto-deletes, or auto-replaces questions without explicit teacher review (`Accept`, `Edit`, `Reject`, `Ignore`).
2. **Modular AI Engine with Automatic Fallback**: Uses `SentenceTransformers` (`all-MiniLM-L6-v2`) for semantic embeddings with automatic fallback to Scikit-learn TF-IDF cosine similarity.
3. **Exact & Semantic Duplicate Detection**: Single-pass vector matrix comparison for exact matches and near-duplicates ($\ge 90\%$ near-identical, $82–89\%$ near duplicate).
4. **Advisory Ambiguity & Grammar Checking**: Detects missing context ("Explain this."), undefined references ("Explain the above method"), vague terms, and sentence structure issues.
5. **Bloom's Taxonomy & Difficulty Estimator**: Classifies questions into Remember, Understand, Apply, Analyze, Evaluate, Create with confidence metrics.
6. **Transparent Quality Formula**:
   $$\text{Quality} = 0.20 \times \text{Clarity} + 0.15 \times \text{Grammar} + 0.15 \times \text{Structure} + 0.20 \times \text{Relevance} + 0.15 \times \text{Originality} + 0.15 \times \text{Completeness}$$
7. **Course Outcome (CO) Semantic Mapping**: Automatically maps questions to Course Outcomes using cosine similarity, with manual override support.
8. **Interactive Assessment Builder**: Construct examination papers based on target marks, question count, Bloom distribution, and difficulty constraints.
9. **Assessment Health Score & What-If Optimizer**:
   $$\text{Health} = 0.20 \times \text{Quality} + 0.15 \times \text{Syllabus} + 0.15 \times \text{Concept} + 0.15 \times \text{CO} + 0.15 \times \text{Bloom} + 0.10 \times \text{Difficulty} + 0.10 \times \text{Diversity}$$
   Runs What-If simulations, tests candidate replacements from the bank, predicts score improvements (+15 points), and provides interactive teacher decision controls.
10. **Multi-Format Export & Audit Trail**: Export HTML, CSV, and PDF audit reports along with persistent SQLite teacher decision logs.

---

## Project Structure

```
EduGuard_AI/
│
├── app.py                      # Main Streamlit application entry point
├── eduguard_config.py          # App constants & weight formulas
├── database.py                 # SQLite ORM & query handler
├── models.py                   # Dataclasses & schema mappings
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation
│
├── data/                       # Built-in sample datasets
│   ├── sample_question_bank.csv# 50-question sample dataset
│   ├── sample_syllabus.txt     # Course syllabus text
│   └── sample_cos.txt          # Course Outcomes (CO1-CO5)
│
├── modules/                    # Modular Engine Pipeline
│   ├── file_loader.py          # CSV, XLSX, PDF parser
│   ├── preprocessing.py       # Text normalization
│   ├── embeddings.py           # SentenceTransformer / TF-IDF adapter engine
│   ├── duplicate_detector.py   # Exact & semantic duplicate detector
│   ├── ambiguity_detector.py   # Advisory ambiguity detector
│   ├── grammar_checker.py      # Grammar & syntax analyzer
│   ├── syllabus_analyzer.py    # Syllabus relevance matching
│   ├── concept_detector.py     # Primary/secondary concept detector
│   ├── bloom_classifier.py     # Bloom's taxonomy classifier
│   ├── difficulty_estimator.py # Difficulty estimator
│   ├── quality_scorer.py       # Quality score calculator
│   ├── improvement_generator.py# AI question suggestion generator
│   ├── coverage_analyzer.py   # Topic, Concept, Bloom, & Diversity analyzer
│   ├── co_mapper.py            # CO semantic mapper
│   ├── assessment_builder.py   # Exam paper builder
│   ├── assessment_health.py    # Assessment Health formula & balance engine
│   ├── optimizer.py            # What-If replacement simulator
│   └── report_generator.py     # HTML, CSV, PDF report generator
│
├── pages/                      # Streamlit UI Navigation Views
│   ├── dashboard.py
│   ├── upload.py
│   ├── question_analysis.py
│   ├── question_details.py
│   ├── coverage.py
│   ├── assessment_builder.py
│   ├── assessment_health.py
│   ├── optimizer.py
│   └── reports.py
│
└── utils/                      # Utilities & Helpers
    ├── validators.py
    ├── helpers.py
    └── export.py
```

---

## Quick Start & Installation

### 1. Prerequisites
- Python 3.10+

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
streamlit run app.py
```

---

## Sample Credentials

- **Username**: `teacher`
- **Password**: `eduguard123`

---

## How to Replace AI Embedding Model

In `modules/embeddings.py`, the `BaseEmbeddingEngine` abstract class allows replacing `SentenceTransformerEngine` with custom models (such as OpenAI Embeddings or HuggingFace transformers) by creating a subclass and implementing `.encode(texts)` and `.compute_similarity_matrix(texts)`.
