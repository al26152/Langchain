"""
Multi-Agent Iterative RAG System

A sophisticated evidence-gathering system that iteratively searches,
critiques, and refines evidence until sufficient coverage is achieved.

Components:
- EvidenceAgent: Retrieves evidence with coverage metrics
- CritiqueAgent: Identifies gaps and assesses quality
- SynthesisAgent: Generates reports with epistemic categorization
- Orchestrator: Coordinates the multi-agent workflow
"""

from .evidence_agent import EvidenceAgent
from .critique_agent import CritiqueAgent
from .synthesis_agent import SynthesisAgent
from .orchestrator import Orchestrator

__all__ = [
    "EvidenceAgent",
    "CritiqueAgent",
    "SynthesisAgent",
    "Orchestrator",
]

__version__ = "1.0.0"
