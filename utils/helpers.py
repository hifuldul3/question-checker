"""
EduGuard AI - Helper & UI Visualization Utilities
"""
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any


def get_status_badge_html(status: str) -> str:
    """Returns styled HTML badge for duplicate and quality status."""
    if status == "Unique":
        return '<span style="background-color: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">Unique</span>'
    elif status == "Near Duplicate":
        return '<span style="background-color: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">Near Duplicate</span>'
    elif status == "Exact Duplicate":
        return '<span style="background-color: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">Exact Duplicate</span>'
    return f'<span style="background-color: #e5e7eb; color: #374151; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">{status}</span>'


def create_bloom_chart(bloom_dist: Dict[str, float]):
    """Creates a Plotly Bar Chart for Bloom's Taxonomy Distribution."""
    df = [{"Level": k, "Percentage": v} for k, v in bloom_dist.items()]
    fig = px.bar(
        df, x="Level", y="Percentage",
        text="Percentage",
        title="Bloom's Taxonomy Distribution (%)",
        color="Level",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(yaxis_range=[0, 100], showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    return fig


def create_difficulty_chart(diff_dist: Dict[str, float]):
    """Creates a Plotly Donut Chart for Difficulty Distribution."""
    labels = list(diff_dist.keys())
    values = list(diff_dist.values())
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=['#22c55e', '#f59e0b', '#ef4444']
    )])
    fig.update_layout(title="Difficulty Level Breakdown", margin=dict(l=20, r=20, t=40, b=20))
    return fig
