"""
utils.py

SHARED UTILITIES FOR RAG PIPELINE

This module provides shared functionality used across the RAG ingestion and analysis pipelines.

KEY FUNCTIONS:
  - auto_tag(snippet): Uses AI to assign Theme and Audience labels to document chunks
  - Loads environment variables from .env file (OpenAI API key)

USAGE:
  from utils import auto_tag

  theme, audience = auto_tag("Some healthcare policy text...")
  # Returns: ("Healthcare Productivity", "Healthcare executives")
"""

import re
from typing import Tuple

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env (OpenAI API key, etc.)

from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# ============================================================================
# AUTO-TAGGING FUNCTIONALITY
# ============================================================================
# Uses GPT-3.5-turbo to automatically categorize document chunks with:
# - Theme: What topic/domain the text covers (e.g., "Healthcare Productivity")
# - Audience: Who should read this (e.g., "Healthcare executives, policymakers")
#
# This enables semantic organization of documents for better retrieval.
# ============================================================================

# 1. Build your prompt template for tagging
TAG_PROMPT = PromptTemplate.from_template(
    "Assign a Theme and Audience for this excerpt:\n\n{content}\n\n"
    "Respond exactly:\n"
    "Theme: <theme>\n"
    "Audience: <audience>"
)

# 2. Initialize GPT-3.5-turbo client for auto-tagging
# Uses lower temperature (0.2) for consistent, deterministic responses
LLM_TAGGING = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)


def auto_tag(snippet: str) -> Tuple[str, str]:
    """
    Automatically assign Theme and Audience to a text snippet using AI.

    This function uses GPT-3.5-turbo to analyze a document excerpt and generate
    semantic labels (theme and target audience). These labels are stored as
    metadata and enable better document filtering and retrieval.

    Args:
        snippet (str): Text excerpt to categorize (typically 100-2000 characters)

    Returns:
        Tuple[str, str]: (theme, audience)
            - theme: Main topic/category (e.g., "Workforce Development")
            - audience: Target audience (e.g., "HR professionals, organizational leaders")

    Example:
        >>> theme, audience = auto_tag("NHS England is implementing a new workforce strategy...")
        >>> print(theme)
        "Workforce Development"
        >>> print(audience)
        "Healthcare administrators, HR professionals"

    Error Handling:
        If parsing fails, returns ("unknown", "unknown") instead of crashing
    """
    # Format the prompt with the snippet
    prompt_str = TAG_PROMPT.format(content=snippet)

    # Call GPT-3.5-turbo to generate theme and audience
    # Uses .invoke() method (modern LangChain API, not deprecated __call__)
    response_msg = LLM_TAGGING.invoke([HumanMessage(content=prompt_str)])

    # Extract response text
    raw = response_msg.content

    # Parse theme and audience using regex
    theme_match = re.search(r"Theme:\s*(.+)", raw)
    audience_match = re.search(r"Audience:\s*(.+)", raw)

    # Safely extract values, default to "unknown" if parsing fails
    theme = theme_match.group(1).strip() if theme_match else "unknown"
    audience = audience_match.group(1).strip() if audience_match else "unknown"

    return theme, audience