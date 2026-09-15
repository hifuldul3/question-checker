"""
EduGuard AI - Multi-Format Report Generator (HTML, CSV, PDF)
"""
import io
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from models import Question, QuestionAnalysis, AssessmentHealthBreakdown, TeacherDecision


import html

def generate_html_report(
    questions: List[Question],
    analyses: Dict[str, QuestionAnalysis],
    coverage_metrics: Dict[str, Any],
    health_metrics: Optional[AssessmentHealthBreakdown] = None,
    decisions: List[TeacherDecision] = None
) -> str:
    """Generates an HTML report string."""
    decisions = decisions or []

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>EduGuard AI - Question Bank Quality & Assessment Audit Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 30px; background-color: #f8f9fa; color: #212529; }}
            .header {{ background-color: #1e3a8a; color: white; padding: 25px; border-radius: 8px; margin-bottom: 25px; }}
            .card-grid {{ display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }}
            .card {{ background: white; padding: 18px; border-radius: 8px; flex: 1; min-width: 150px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #3b82f6; }}
            .card h3 {{ margin: 0; font-size: 28px; color: #1e3a8a; }}
            .card p {{ margin: 5px 0 0 0; font-size: 13px; color: #6b7280; font-weight: bold; }}
            h2 {{ color: #1e3a8a; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #e5e7eb; font-size: 14px; }}
            th {{ background-color: #f3f4f6; color: #374151; font-weight: 600; }}
            .badge-unique {{ background: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
            .badge-duplicate {{ background: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
            .footer {{ margin-top: 40px; font-size: 12px; text-align: center; color: #9ca3af; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="margin:0;">EduGuard AI</h1>
            <p style="margin:5px 0 0 0; opacity:0.9;">Question Bank Quality Assurance & Assessment Optimization Report</p>
        </div>

        <div class="card-grid">
            <div class="card">
                <h3>{coverage_metrics.get('total_questions', 0)}</h3>
                <p>TOTAL QUESTIONS</p>
            </div>
            <div class="card">
                <h3>{coverage_metrics.get('average_quality', 0)} / 100</h3>
                <p>AVG QUALITY SCORE</p>
            </div>
            <div class="card">
                <h3>{coverage_metrics.get('duplicate_pct', 0)}%</h3>
                <p>DUPLICATE RATE</p>
            </div>
            <div class="card">
                <h3>{coverage_metrics.get('low_quality_pct', 0)}%</h3>
                <p>LOW QUALITY RATE</p>
            </div>
            <div class="card">
                <h3>{health_metrics.total_health if health_metrics else 'N/A'}</h3>
                <p>ASSESSMENT HEALTH</p>
            </div>
        </div>

        <h2>1. Executive Summary</h2>
        <p>This report presents the quality analysis of the evaluated question bank. Total questions processed: <strong>{len(questions)}</strong>.</p>

        <h2>2. Question Quality Findings</h2>
        <table>
            <thead>
                <tr>
                    <th>Q ID</th>
                    <th>Question Text</th>
                    <th>Topic</th>
                    <th>Bloom</th>
                    <th>Difficulty</th>
                    <th>Quality</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    """
    for q in questions:
        a = analyses.get(q.id)
        q_score = a.quality_score if a else 80.0
        status = a.duplicate_status if a else "Unique"
        badge_cls = "badge-duplicate" if status != "Unique" else "badge-unique"
        q_text_escaped = html.escape(q.text[:80] + ("..." if len(q.text) > 80 else ""))
        topic_escaped = html.escape(str(q.topic))
        html_code += f"""
                <tr>
                    <td><strong>{html.escape(str(q.id))}</strong></td>
                    <td>{q_text_escaped}</td>
                    <td>{topic_escaped}</td>
                    <td>{html.escape(str(a.bloom_level if a else 'Understand'))}</td>
                    <td>{html.escape(str(a.difficulty if a else 'Medium'))}</td>
                    <td><strong>{q_score}</strong></td>
                    <td><span class="{badge_cls}">{html.escape(str(status))}</span></td>
                </tr>
        """
    html_code += """
            </tbody>
        </table>

        <h2>3. Teacher Audit Trail & Decision Logs</h2>
        <table>
            <thead>
                <tr>
                    <th>Question ID</th>
                    <th>Type</th>
                    <th>Decision</th>
                    <th>Edited Content</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody>
    """
    if decisions:
        for d in decisions:
            html_code += f"""
                <tr>
                    <td><strong>{html.escape(str(d.question_id))}</strong></td>
                    <td>{html.escape(str(d.recommendation_type))}</td>
                    <td><strong>{html.escape(str(d.decision))}</strong></td>
                    <td>{html.escape(str(d.edited_content or 'N/A'))}</td>
                    <td>{html.escape(str(d.timestamp))}</td>
                </tr>
            """
    else:
        html_code += "<tr><td colspan='5'>No teacher decisions recorded yet.</td></tr>"

    html_code += """
            </tbody>
        </table>

        <div class="footer">
            <p>Generated by EduGuard AI - AI-Powered Question Bank Quality Assurance & Assessment Optimization System</p>
        </div>
    </body>
    </html>
    """
    return html_code


def generate_csv_export(
    questions: List[Question],
    analyses: Dict[str, QuestionAnalysis]
) -> str:
    """Generates a CSV string containing questions and all analysis metrics."""
    rows = []
    for q in questions:
        a = analyses.get(q.id)
        rows.append({
            "Question ID": q.id,
            "Question Text": q.text,
            "Marks": q.marks,
            "Topic": q.topic,
            "Question Type": q.question_type,
            "Duplicate Status": a.duplicate_status if a else "Unique",
            "Similar Question ID": a.similar_question_id if a else "",
            "Similarity Score": a.similarity_score if a else 0.0,
            "Ambiguity Score": a.ambiguity_score if a else 0.0,
            "Grammar Score": a.grammar_score if a else 100.0,
            "Relevance Status": a.relevance_status if a else "In Syllabus",
            "Primary Concept": a.primary_concept if a else "General",
            "Bloom Level": a.bloom_level if a else "Understand",
            "Difficulty": a.difficulty if a else "Medium",
            "Quality Score": a.quality_score if a else 80.0,
            "Mapped CO": a.mapped_co if a else "CO1",
            "AI Improvement Suggestion": a.suggested_improvement if a else ""
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


def generate_pdf_report(
    questions: List[Question],
    analyses: Dict[str, QuestionAnalysis],
    coverage_metrics: Dict[str, Any]
) -> bytes:
    """Generates a binary PDF document bytes using ReportLab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=12
        )
        h2_style = ParagraphStyle(
            'DocH2',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#1e3a8a'),
            spaceBefore=14,
            spaceAfter=8
        )
        header_cell_style = ParagraphStyle(
            'HeaderCell',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        )
        body_cell_style = ParagraphStyle(
            'BodyCell',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1f2937')
        )
        bold_cell_style = ParagraphStyle(
            'BoldCell',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1e3a8a'),
            fontName='Helvetica-Bold'
        )

        # Title & Banner
        story.append(Paragraph(html.escape("EduGuard AI Audit Report"), title_style))
        story.append(Paragraph(html.escape("Question Bank Quality Assurance & Assessment Optimization"), subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3b82f6'), spaceAfter=14))

        # Section 1: Executive Summary
        story.append(Paragraph(html.escape("1. Executive Summary & Key Metrics"), h2_style))

        summary_data = [
            [Paragraph("Metric Description", header_cell_style), Paragraph("Value", header_cell_style)],
            [Paragraph("Total Questions Processed", body_cell_style), Paragraph(str(coverage_metrics.get("total_questions", len(questions))), bold_cell_style)],
            [Paragraph("Average Quality Score", body_cell_style), Paragraph(f"{coverage_metrics.get('average_quality', 0)} / 100", bold_cell_style)],
            [Paragraph("Duplicate Rate", body_cell_style), Paragraph(f"{coverage_metrics.get('duplicate_pct', 0)}%", bold_cell_style)],
            [Paragraph("Low Quality Rate", body_cell_style), Paragraph(f"{coverage_metrics.get('low_quality_pct', 0)}%", bold_cell_style)],
            [Paragraph("Question Diversity Score", body_cell_style), Paragraph(f"{coverage_metrics.get('question_diversity_score', 0)} / 100", bold_cell_style)]
        ]
        sum_table = Table(summary_data, colWidths=[270, 270])
        sum_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        story.append(sum_table)
        story.append(Spacer(1, 14))

        # Section 2: Question Quality Breakdown
        story.append(Paragraph(html.escape("2. Question Quality Audit Details"), h2_style))
        
        q_data = [[
            Paragraph("Q ID", header_cell_style),
            Paragraph("Question Text", header_cell_style),
            Paragraph("Topic", header_cell_style),
            Paragraph("Bloom", header_cell_style),
            Paragraph("Quality", header_cell_style),
            Paragraph("Status", header_cell_style)
        ]]

        for q in questions[:35]:  # Include up to 35 questions cleanly in report
            a = analyses.get(q.id)
            q_text_escaped = html.escape(q.text[:90] + ("..." if len(q.text) > 90 else ""))
            topic_escaped = html.escape(str(q.topic[:20]))
            bloom_escaped = html.escape(str(a.bloom_level if a else "Understand"))
            status_escaped = html.escape(str(a.duplicate_status if a else "Unique"))
            score_str = str(a.quality_score if a else 80.0)

            q_data.append([
                Paragraph(html.escape(str(q.id)), bold_cell_style),
                Paragraph(q_text_escaped, body_cell_style),
                Paragraph(topic_escaped, body_cell_style),
                Paragraph(bloom_escaped, body_cell_style),
                Paragraph(score_str, body_cell_style),
                Paragraph(status_escaped, body_cell_style)
            ])

        q_table = Table(q_data, colWidths=[45, 235, 95, 65, 45, 55])
        q_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        story.append(q_table)

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    except Exception as e:
        # Fallback to generating a minimal valid PDF using ReportLab canvas
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 750, "EduGuard AI Audit Report")
            c.setFont("Helvetica", 10)
            c.drawString(50, 730, f"Total Questions: {len(questions)}")
            c.drawString(50, 710, f"Average Quality: {coverage_metrics.get('average_quality', 0)}")
            c.save()
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
        except Exception:
            return b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"

