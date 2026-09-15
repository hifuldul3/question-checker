"""
EduGuard AI - File Export Wrapper Utilities
"""
import io
from typing import List, Dict, Any, Tuple
from models import Question, QuestionAnalysis
from modules.report_generator import generate_csv_export, generate_html_report, generate_pdf_report


def get_export_bytes(
    fmt: str,
    questions: List[Question],
    analyses: Dict[str, QuestionAnalysis],
    coverage_metrics: Dict[str, Any]
) -> Tuple[bytes, str, str]:
    """
    Returns (bytes_data, file_name, mime_type) for download.
    """
    if fmt == "csv":
        csv_str = generate_csv_export(questions, analyses)
        return csv_str.encode("utf-8"), "eduguard_question_analysis.csv", "text/csv"
    elif fmt == "html":
        html_str = generate_html_report(questions, analyses, coverage_metrics)
        return html_str.encode("utf-8"), "eduguard_audit_report.html", "text/html"
    else:  # pdf
        pdf_bytes = generate_pdf_report(questions, analyses, coverage_metrics)
        return pdf_bytes, "eduguard_audit_report.pdf", "application/pdf"
