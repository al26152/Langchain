"""
Reusable components for displaying analysis results in Streamlit.
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Any


def display_confidence_badge(confidence_score: int) -> None:
    """Display a color-coded confidence badge."""
    if confidence_score >= 85:
        color = "🟢"
        label = "EXCELLENT"
    elif confidence_score >= 70:
        color = "🟡"
        label = "GOOD"
    elif confidence_score >= 50:
        color = "🟠"
        label = "ADEQUATE"
    else:
        color = "🔴"
        label = "WEAK"

    st.metric("Confidence Score", f"{confidence_score}%", delta=label, label_visibility="visible")


def display_epistemic_chart(epistemic_breakdown: Dict[str, int]) -> None:
    """Display epistemic breakdown as an interactive pie chart."""
    if not epistemic_breakdown:
        return

    labels = list(epistemic_breakdown.keys())
    values = list(epistemic_breakdown.values())

    # Color mapping
    colors_map = {
        "FACT": "#2ecc71",      # Green
        "ASSUMPTION": "#f39c12", # Orange
        "INFERENCE": "#3498db"   # Blue
    }
    colors = [colors_map.get(label, "#95a5a6") for label in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
    )])

    fig.update_layout(
        title="Epistemic Breakdown",
        height=400,
        showlegend=True,
        font=dict(size=12)
    )

    st.plotly_chart(fig, use_container_width=True)


def get_recency_flag(doc_date: str, current_year: int = 2025) -> str:
    """
    Determine recency flag based on document date.

    Args:
        doc_date: Date string (YYYY-MM-DD format)
        current_year: Current year for comparison

    Returns:
        Recency flag string with emoji
    """
    try:
        year = int(doc_date.split("-")[0])
        age = current_year - year

        if age == 0:
            return "[🟢 RECENT]"
        elif age <= 2:
            return "[🟡 AGING]"
        elif age <= 4:
            return "[🟠 ARCHIVAL]"
        else:
            return "[🔴 OUTDATED]"
    except:
        return "[❓ UNKNOWN]"


def display_source_metadata_table(sources: List[Dict[str, Any]]) -> None:
    """
    Display source metadata as a formatted table.

    Args:
        sources: List of source dictionaries with metadata
    """
    import pandas as pd

    if not sources:
        st.info("No sources found.")
        return

    # Prepare data for table
    table_data = []
    for source in sources:
        table_data.append({
            "Document": source.get("name", "Unknown")[:40],  # Truncate long names
            "Date": source.get("date", "N/A"),
            "Recency": get_recency_flag(source.get("date", "")),
            "Theme": source.get("theme", "N/A")[:25],
            "Chunks": source.get("chunks", 0)
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def display_answer_with_sections(answer_text: str, max_preview_lines: int = 5) -> None:
    """
    Display answer with collapsible sections for readability.

    Args:
        answer_text: Full answer text
        max_preview_lines: Lines to show before "Show more"
    """
    lines = answer_text.split("\n")

    if len(lines) > max_preview_lines:
        preview = "\n".join(lines[:max_preview_lines])
        with st.expander("📄 Full Answer", expanded=True):
            st.markdown(answer_text)
    else:
        st.markdown(answer_text)


def export_to_markdown(result: Dict[str, Any]) -> str:
    """
    Convert analysis result to Markdown format.

    Args:
        result: Result dictionary from analysis

    Returns:
        Markdown formatted string
    """
    markdown = f"""# Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Question
{result.get('question', 'N/A')}

## Summary
**Confidence Score:** {result.get('confidence_score', 'N/A')}%
**Quality Rating:** {result.get('quality_rating', 'N/A')}
**Documents Consulted:** {result.get('unique_sources', 0)}
**Evidence Chunks:** {result.get('total_chunks', 0)}

## Answer
{result.get('answer', 'No answer generated')}

## Epistemic Breakdown
"""

    epistemic = result.get('epistemic_breakdown', {})
    for key, value in epistemic.items():
        markdown += f"- **{key}:** {value}\n"

    markdown += "\n## Sources\n"
    sources = result.get('sources', [])
    for source in sources:
        markdown += f"- **{source.get('name', 'Unknown')}** ({source.get('date', 'N/A')}) - {source.get('chunks', 0)} chunks\n"

    if result.get('gaps_identified'):
        markdown += "\n## Identified Gaps\n"
        for gap in result.get('gaps_identified', []):
            markdown += f"- {gap}\n"

    return markdown


def create_download_button(content: str, filename: str, file_format: str) -> None:
    """
    Create a download button for exporting results.

    Args:
        content: Content to download
        filename: Filename for download
        file_format: Format type ('markdown' or 'json')
    """
    if file_format == "markdown":
        mime_type = "text/markdown"
        button_label = "📥 Download as Markdown"
    elif file_format == "json":
        mime_type = "application/json"
        button_label = "📥 Download as JSON"
    else:
        mime_type = "text/plain"
        button_label = "📥 Download"

    st.download_button(
        label=button_label,
        data=content,
        file_name=filename,
        mime=mime_type
    )
