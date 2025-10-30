"""
Components for tracking and displaying real-time analysis progress.
"""
import streamlit as st
from typing import Optional, Dict, Any


def create_iteration_status_container():
    """Create a status container for tracking iterations."""
    return st.status("🔄 Running Multi-Agent Analysis...", expanded=True)


def format_evidence_update(chunks_count: int, doc_count: int, documents: list = None) -> str:
    """
    Format evidence agent results.

    Args:
        chunks_count: Number of chunks retrieved
        doc_count: Number of unique documents
        documents: List of document names (optional)

    Returns:
        Formatted string
    """
    msg = f"🔍 Evidence Agent: Retrieved {chunks_count} chunks from {doc_count} document(s)"

    if documents and len(documents) > 0:
        doc_preview = ", ".join(documents[:3])
        if len(documents) > 3:
            doc_preview += f", +{len(documents) - 3} more"
        msg += f"\n   Sources: {doc_preview}"

    return msg


def format_critique_update(quality_rating: str, gaps_identified: list = None) -> str:
    """
    Format critique agent results.

    Args:
        quality_rating: Quality rating (WEAK/ADEQUATE/GOOD/EXCELLENT)
        gaps_identified: List of identified gaps

    Returns:
        Formatted string
    """
    # Color code quality rating
    quality_emoji = {
        "WEAK": "🔴",
        "ADEQUATE": "🟠",
        "GOOD": "🟡",
        "EXCELLENT": "🟢"
    }

    emoji = quality_emoji.get(quality_rating, "❓")
    msg = f"🧐 Critique Agent: Quality = {emoji} {quality_rating}"

    if gaps_identified:
        gap_text = ", ".join(gaps_identified[:2])
        if len(gaps_identified) > 2:
            gap_text += f", +{len(gaps_identified) - 2} more"
        msg += f"\n   Gaps: {gap_text}"
    else:
        msg += "\n   Gaps: None detected ✓"

    return msg


def format_decision(should_continue: bool, reason: str = "") -> str:
    """
    Format the decision to continue or stop iterations.

    Args:
        should_continue: Whether analysis should continue
        reason: Reason for the decision

    Returns:
        Formatted string
    """
    if should_continue:
        msg = "🔄 Decision: Continue with expanded search"
    else:
        msg = "✅ Decision: Analysis complete - sufficient quality achieved"

    if reason:
        msg += f"\n   Reason: {reason}"

    return msg


def display_iteration_log(iterations: list) -> None:
    """
    Display detailed iteration log in an expander.

    Args:
        iterations: List of iteration data dictionaries
    """
    if not iterations:
        return

    with st.expander("📋 Detailed Iteration Log", expanded=False):
        for i, iteration in enumerate(iterations, 1):
            with st.container():
                st.subheader(f"Iteration {i}")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Chunks Retrieved",
                        iteration.get('chunks_count', 0),
                        delta=f"{iteration.get('doc_count', 0)} docs"
                    )

                with col2:
                    quality = iteration.get('quality_rating', 'UNKNOWN')
                    st.metric("Quality", quality)

                with col3:
                    gap_count = len(iteration.get('gaps_identified', []))
                    st.metric("Gaps Found", gap_count)

                if iteration.get('gaps_identified'):
                    st.write("**Identified Gaps:**")
                    for gap in iteration['gaps_identified']:
                        st.write(f"• {gap}")


class ProgressTracker:
    """Context manager for tracking analysis progress."""

    def __init__(self):
        self.iterations = []
        self.status_container = None

    def __enter__(self):
        self.status_container = create_iteration_status_container()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.status_container:
            self.status_container.update(
                label="✅ Analysis Complete",
                state="complete"
            )

    def add_iteration(self, iteration_num: int, total_iterations: int, **details) -> None:
        """
        Add and display a new iteration.

        Args:
            iteration_num: Current iteration number
            total_iterations: Total iterations
            **details: Iteration details (chunks_count, doc_count, quality_rating, gaps_identified, etc.)
        """
        self.iterations.append(details)

        if self.status_container:
            # Format the update message
            progress_msg = f"⏳ Iteration {iteration_num}/{total_iterations}\n"
            progress_msg += format_evidence_update(
                details.get('chunks_count', 0),
                details.get('doc_count', 0),
                details.get('documents', [])
            ) + "\n"
            progress_msg += format_critique_update(
                details.get('quality_rating', 'UNKNOWN'),
                details.get('gaps_identified', [])
            )

            if 'decision_reason' in details:
                progress_msg += "\n" + format_decision(
                    details.get('should_continue', False),
                    details.get('decision_reason')
                )

            self.status_container.update(label=progress_msg)

    def get_iterations(self) -> list:
        """Get all recorded iterations."""
        return self.iterations
