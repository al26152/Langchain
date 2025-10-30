"""
config.py

CENTRALIZED CONFIGURATION FOR NHS STRATEGIC ANALYSIS SYSTEM

All hardcoded values are now in this single file for easy management.
To change any setting, simply edit this file - no code changes needed!

Usage:
    from config import Config

    # Access settings
    db_path = Config.CHROMA_DB_PATH
    model = Config.DEFAULT_LLM_MODEL
"""

import os
from pathlib import Path


class Config:
    """Central configuration for the NHS Strategic Analysis RAG Pipeline."""

    # =========================================================================
    # DATABASE SETTINGS
    # =========================================================================

    # ChromaDB vector database path
    CHROMA_DB_PATH = "chroma_db_test"

    # Knowledge graph JSON file path
    KNOWLEDGE_GRAPH_PATH = "knowledge_graph_improved.json"

    # Entity resolution mappings
    ENTITY_MAPPINGS_PATH = "analysis/entity_resolution/entity_mappings.json"

    # =========================================================================
    # MODEL SETTINGS
    # =========================================================================

    # Main LLM model for synthesis and orchestration
    DEFAULT_LLM_MODEL = "gpt-4o"

    # Faster/cheaper model for epistemic classification
    EPISTEMIC_LLM_MODEL = "gpt-4o-mini"

    # Model for metadata tagging during ingestion
    TAGGING_LLM_MODEL = "gpt-3.5-turbo"

    # Available models for web interface dropdown
    AVAILABLE_MODELS = ["gpt-4o", "gpt-4o-mini"]

    # =========================================================================
    # TEMPERATURE SETTINGS (Creativity vs Consistency)
    # =========================================================================

    # Default temperature for main synthesis (0.0 = deterministic, 1.0 = creative)
    DEFAULT_TEMPERATURE = 0.5

    # Temperature for epistemic classification (lower = more consistent)
    EPISTEMIC_TEMPERATURE = 0.3

    # Temperature for metadata tagging (very low for consistency)
    TAGGING_TEMPERATURE = 0.2

    # =========================================================================
    # RETRIEVAL SETTINGS
    # =========================================================================

    # Default number of chunks to retrieve from ChromaDB
    # Increased to 30 to ensure strategic documents like 10-year plan are included
    DEFAULT_RETRIEVAL_K = 30

    # Maximum k value allowed (for advanced users)
    MAX_RETRIEVAL_K = 50

    # Minimum k value allowed
    MIN_RETRIEVAL_K = 5

    # Maximum evidence chunks to use in synthesis (increased from 20!)
    MAX_SYNTHESIS_CHUNKS = 30

    # =========================================================================
    # QUALITY THRESHOLDS (Critique Agent)
    # =========================================================================
    # IMPORTANT: These control when the system stops iterating!
    # Higher thresholds = more iterations = better quality but slower/costlier

    # Score threshold for EXCELLENT quality (stops immediately)
    # Increased from 80 to 90 to prevent premature stopping
    EXCELLENT_THRESHOLD = 90

    # Score threshold for GOOD quality (stops if convergence detected)
    # Increased from 60 to 75
    GOOD_THRESHOLD = 75

    # Score threshold for ADEQUATE quality
    # Increased from 40 to 50
    ADEQUATE_THRESHOLD = 50

    # Minimum unique sources required for ADEQUATE rating
    MIN_SOURCES = 5

    # Minimum coverage percentage (% of total documents)
    MIN_COVERAGE_PERCENT = 15.0

    # Minimum percentage of recent evidence (< 1 year old)
    MIN_RECENT_PERCENT = 30.0

    # Maximum iterations allowed
    MAX_ITERATIONS = 5

    # Default iterations for web interface
    DEFAULT_ITERATIONS = 5

    # =========================================================================
    # ENTITY RESOLUTION SETTINGS
    # =========================================================================

    # Maximum aliases to add per entity during query expansion
    MAX_ALIASES_PER_ENTITY = 2

    # Fuzzy matching threshold for typo correction (0.0-1.0)
    FUZZY_MATCH_THRESHOLD = 0.85

    # Enable entity resolution by default
    ENTITY_RESOLUTION_ENABLED = True

    # =========================================================================
    # KNOWLEDGE GRAPH SETTINGS
    # =========================================================================

    # Maximum terms to add from knowledge graph expansion
    MAX_KG_EXPANSION_TERMS = 5

    # Enable knowledge graph by default
    KNOWLEDGE_GRAPH_ENABLED = True

    # =========================================================================
    # DOCUMENT CLASSIFICATION SETTINGS (Metadata-Based Retrieval)
    # =========================================================================

    # Valid document types (auto-assigned during ingestion)
    DOCUMENT_TYPES = [
        "STRATEGIC_PLAN",        # NHS England 10-year plans, national health strategies
        "OPERATIONAL_GUIDANCE",  # Planning frameworks, operational guidance
        "ORG_SPECIFIC",         # Annual reports, board papers, organizational strategies
        "PARTNERSHIP",          # Health and Care Partnership documents
        "GENERAL"               # Other NHS/health context
    ]

    # Valid strategic levels (auto-assigned during ingestion)
    STRATEGIC_LEVELS = [
        "NATIONAL",     # NHS England, national policy level
        "SYSTEM",       # Integrated Care System, partnerships
        "ORGANIZATION", # Individual trust/council documents
        "LOCAL"         # Local authority documents
    ]

    # Enable metadata-based strategic document boosting
    STRATEGIC_BOOST_ENABLED = True

    # =========================================================================
    # WEB INTERFACE SETTINGS
    # =========================================================================

    # Default page title
    APP_TITLE = "NHS Strategic Analysis System"

    # Default page icon
    APP_ICON = "🏥"

    # Layout mode
    LAYOUT = "wide"

    # Web interface sliders - iterations
    WEB_MIN_ITERATIONS = 1
    WEB_MAX_ITERATIONS = 10
    WEB_DEFAULT_ITERATIONS = 5

    # Web interface sliders - temperature
    WEB_MIN_TEMPERATURE = 0.0
    WEB_MAX_TEMPERATURE = 1.0
    WEB_DEFAULT_TEMPERATURE = 0.5

    # Web interface sliders - k value
    WEB_MIN_K = 5
    WEB_MAX_K = 20
    WEB_DEFAULT_K = 10

    # =========================================================================
    # DATE CLASSIFICATION THRESHOLDS
    # =========================================================================

    # Years threshold for "recent" documents
    RECENT_YEARS_THRESHOLD = 1.0

    # Years threshold for "moderate" age documents
    MODERATE_YEARS_THRESHOLD = 3.0

    # Documents older than this are considered "old"
    # (anything > MODERATE_YEARS_THRESHOLD)

    # =========================================================================
    # FALLBACK VALUES
    # =========================================================================

    # Assumed document count if ChromaDB count fails
    FALLBACK_DOCUMENT_COUNT = 30

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    @classmethod
    def get_db_path(cls) -> Path:
        """Get ChromaDB path as Path object."""
        return Path(cls.CHROMA_DB_PATH)

    @classmethod
    def get_kg_path(cls) -> Path:
        """Get Knowledge Graph path as Path object."""
        return Path(cls.KNOWLEDGE_GRAPH_PATH)

    @classmethod
    def get_entity_mappings_path(cls) -> Path:
        """Get Entity Mappings path as Path object."""
        return Path(cls.ENTITY_MAPPINGS_PATH)

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that critical paths exist.

        Returns:
            True if all critical files exist, False otherwise
        """
        critical_paths = [
            cls.get_db_path(),
            cls.get_kg_path(),
            cls.get_entity_mappings_path(),
        ]

        all_exist = True
        for path in critical_paths:
            if not path.exists():
                print(f"[WARNING] Missing: {path}")
                all_exist = False

        return all_exist

    @classmethod
    def print_config(cls):
        """Print current configuration (for debugging)."""
        print("="*80)
        print("NHS STRATEGIC ANALYSIS SYSTEM - CONFIGURATION")
        print("="*80)
        print("\n[DATABASE]")
        print(f"  ChromaDB Path: {cls.CHROMA_DB_PATH}")
        print(f"  Knowledge Graph: {cls.KNOWLEDGE_GRAPH_PATH}")
        print(f"  Entity Mappings: {cls.ENTITY_MAPPINGS_PATH}")

        print("\n[MODELS]")
        print(f"  Default LLM: {cls.DEFAULT_LLM_MODEL}")
        print(f"  Epistemic LLM: {cls.EPISTEMIC_LLM_MODEL}")
        print(f"  Tagging LLM: {cls.TAGGING_LLM_MODEL}")

        print("\n[RETRIEVAL]")
        print(f"  Default K: {cls.DEFAULT_RETRIEVAL_K}")
        print(f"  Max Synthesis Chunks: {cls.MAX_SYNTHESIS_CHUNKS}")

        print("\n[QUALITY THRESHOLDS]")
        print(f"  EXCELLENT: {cls.EXCELLENT_THRESHOLD}+ points")
        print(f"  GOOD: {cls.GOOD_THRESHOLD}+ points")
        print(f"  ADEQUATE: {cls.ADEQUATE_THRESHOLD}+ points")
        print(f"  Max Iterations: {cls.MAX_ITERATIONS}")

        print("\n[ENTITY RESOLUTION]")
        print(f"  Enabled: {cls.ENTITY_RESOLUTION_ENABLED}")
        print(f"  Max Aliases: {cls.MAX_ALIASES_PER_ENTITY}")
        print(f"  Fuzzy Threshold: {cls.FUZZY_MATCH_THRESHOLD}")

        print("="*80)


# Create default instance for easy import
config = Config()


# For backwards compatibility - can import individual settings
CHROMA_DB_PATH = Config.CHROMA_DB_PATH
KNOWLEDGE_GRAPH_PATH = Config.KNOWLEDGE_GRAPH_PATH
DEFAULT_LLM_MODEL = Config.DEFAULT_LLM_MODEL
EPISTEMIC_LLM_MODEL = Config.EPISTEMIC_LLM_MODEL
MAX_SYNTHESIS_CHUNKS = Config.MAX_SYNTHESIS_CHUNKS
EXCELLENT_THRESHOLD = Config.EXCELLENT_THRESHOLD
GOOD_THRESHOLD = Config.GOOD_THRESHOLD
ADEQUATE_THRESHOLD = Config.ADEQUATE_THRESHOLD


if __name__ == "__main__":
    # Test/debug mode - print config and validate
    Config.print_config()
    print("\n[VALIDATION]")
    if Config.validate():
        print("[OK] All critical paths exist")
    else:
        print("[WARNING] Some paths are missing (see above)")
