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


# ============================================================================
# DOCUMENT CLASSIFICATION FUNCTIONALITY
# ============================================================================
# Uses GPT-3.5-turbo to automatically classify documents by:
# - Document Type: STRATEGIC_PLAN, OPERATIONAL_GUIDANCE, ORG_SPECIFIC, PARTNERSHIP, GENERAL
# - Strategic Level: NATIONAL, SYSTEM, ORGANIZATION, LOCAL
# - Organization: LYPFT, LCH, LTHT, NHS England, Leeds City Council, etc.
#
# This enables dynamic metadata-based retrieval without hardcoded keywords.
# ============================================================================

CLASSIFICATION_PROMPT = PromptTemplate.from_template(
    "Classify this document excerpt:\n\n{content}\n\n"
    "Respond exactly in this format:\n"
    "DocumentType: <STRATEGIC_PLAN|OPERATIONAL_GUIDANCE|ORG_SPECIFIC|PARTNERSHIP|GENERAL>\n"
    "StrategicLevel: <NATIONAL|SYSTEM|ORGANIZATION|LOCAL>\n"
    "Organization: <organization name or 'Unknown'>\n\n"
    "Guidelines:\n"
    "- STRATEGIC_PLAN: NHS England 10-year plans, national health strategies\n"
    "- OPERATIONAL_GUIDANCE: Planning frameworks, operational guidance\n"
    "- ORG_SPECIFIC: Annual reports, board papers, strategy from specific trust/organization\n"
    "- PARTNERSHIP: Health and Care Partnership documents\n"
    "- GENERAL: Other health/NHS context\n"
    "- NATIONAL: NHS England, national policy\n"
    "- SYSTEM: Integrated Care System, partnerships\n"
    "- ORGANIZATION: Individual trust/council documents\n"
    "- LOCAL: Local authority documents"
)

# Initialize GPT-3.5-turbo for document classification
LLM_CLASSIFICATION = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)


def classify_document_type(filename: str, content_sample: str) -> Tuple[str, str, str]:
    """
    Automatically classify a document by type, strategic level, and organization.

    This function uses GPT-3.5-turbo to analyze a document and assign classification
    metadata. These labels enable dynamic retrieval based on document importance and
    organizational relevance, removing the need for hardcoded keywords.

    Args:
        filename (str): Document filename for context
        content_sample (str): Text excerpt for classification (typically 500-2000 characters)

    Returns:
        Tuple[str, str, str]: (document_type, strategic_level, organization)
            - document_type: One of STRATEGIC_PLAN, OPERATIONAL_GUIDANCE, ORG_SPECIFIC, PARTNERSHIP, GENERAL
            - strategic_level: One of NATIONAL, SYSTEM, ORGANIZATION, LOCAL
            - organization: The primary organization mentioned (e.g., "LYPFT", "NHS England")

    Example:
        >>> doc_type, level, org = classify_document_type(
        ...     "NHS 10-year plan.md",
        ...     "The NHS Long Term Plan sets out..."
        ... )
        >>> print(doc_type, level, org)
        "STRATEGIC_PLAN", "NATIONAL", "NHS England"

    Error Handling:
        If parsing fails, returns ("GENERAL", "LOCAL", "Unknown") as safe defaults
    """
    # Format the prompt with the content sample
    full_prompt = CLASSIFICATION_PROMPT.format(content=content_sample)

    try:
        # Call GPT-3.5-turbo to classify the document
        response_msg = LLM_CLASSIFICATION.invoke([HumanMessage(content=full_prompt)])
        raw = response_msg.content

        # Parse classification using regex
        doc_type_match = re.search(r"DocumentType:\s*(.+)", raw)
        strategic_level_match = re.search(r"StrategicLevel:\s*(.+)", raw)
        org_match = re.search(r"Organization:\s*(.+)", raw)

        # Safely extract values
        document_type = doc_type_match.group(1).strip() if doc_type_match else "GENERAL"
        strategic_level = strategic_level_match.group(1).strip() if strategic_level_match else "LOCAL"
        organization = org_match.group(1).strip() if org_match else "Unknown"

        # Validate document type
        valid_types = ["STRATEGIC_PLAN", "OPERATIONAL_GUIDANCE", "ORG_SPECIFIC", "PARTNERSHIP", "GENERAL"]
        if document_type not in valid_types:
            document_type = "GENERAL"

        # Validate strategic level
        valid_levels = ["NATIONAL", "SYSTEM", "ORGANIZATION", "LOCAL"]
        if strategic_level not in valid_levels:
            strategic_level = "LOCAL"

        return document_type, strategic_level, organization

    except Exception as e:
        # Log error but return safe defaults
        print(f"[WARN] Document classification error: {e}")
        return "GENERAL", "LOCAL", "Unknown"