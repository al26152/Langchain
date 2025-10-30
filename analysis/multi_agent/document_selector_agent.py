"""
document_selector_agent.py

DOCUMENT SELECTOR AGENT - Phase 2 of Wide-Then-Deep Analysis

PURPOSE:
  Intelligently filter the 30-document corpus using:
  1. Web context from Phase 1 (what themes matter?)
  2. Your metadata tags (document_type, strategic_level, organization)

  Result: Prioritized subset of documents for RAG search (not all 30)

FEATURES:
  - Filters documents by metadata tags
  - Ranks documents by relevance to query + web context
  - Can expand selection if Critique Agent finds gaps
  - Provides rationale for document selection

USAGE:
  from document_selector_agent import DocumentSelectorAgent

  selector = DocumentSelectorAgent(vectordb)
  selected = selector.select_documents(query, web_context)
  # Returns: {"selected": [...], "ranking": [...], "rationale": ...}
"""

import sys
import os
from typing import Dict, List, Optional, Set
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_chroma import Chroma


class DocumentSelectorAgent:
    """
    Intelligently selects documents from corpus based on web context
    and metadata tags. Enables iterative expansion if gaps identified.
    """

    def __init__(self, vectordb: Chroma):
        """
        Initialize Document Selector Agent.

        Args:
            vectordb: ChromaDB instance with all documents and metadata
        """
        self.vectordb = vectordb
        self.all_documents = self._extract_all_documents()

    def _extract_all_documents(self) -> Dict:
        """
        Extract all documents from ChromaDB with their metadata.

        Returns:
            Dict of document_id -> metadata
        """
        try:
            all_data = self.vectordb.get(include=["metadatas"])
            documents = {}

            for metadata in all_data.get("metadatas", []):
                source = metadata.get("source", "Unknown")
                if source not in documents:
                    documents[source] = {
                        "source": source,
                        "date": metadata.get("date", ""),
                        "organization": metadata.get("organization", ""),
                        "document_type": metadata.get("document_type", ""),
                        "strategic_level": metadata.get("strategic_level", "")
                    }

            print("[OK] Extracted {} documents from ChromaDB".format(len(documents)))
            return documents

        except Exception as e:
            print("[ERROR] Failed to extract documents: {}".format(e))
            return {}

    def select_documents(self, query: str, web_context: Dict) -> Dict:
        """
        Select relevant documents based on query + web context.

        Args:
            query: User's question
            web_context: Output from WebLookupAgent (themes, priorities, etc.)

        Returns:
            Dict with:
            - selected: List of selected document IDs
            - ranking: Documents sorted by relevance (highest first)
            - rationale: Why these documents were selected
            - metadata: Metadata for selected documents
        """
        print("\n[PHASE 2: DOCUMENT SELECTION]")
        print("Filtering {} documents based on web context...".format(len(self.all_documents)))

        # Get selection strategy from web context
        themes = web_context.get("key_themes", [])
        priorities = web_context.get("national_priorities", [])

        # Filter documents by relevance
        ranked = self._rank_documents(query, themes, priorities)

        # Select top documents (dynamic based on corpus size)
        # Start with ~50% of corpus, can expand if needed
        target_count = max(5, len(self.all_documents) // 2)
        selected_ids = [doc_id for doc_id, _ in ranked[:target_count]]

        result = {
            "query": query,
            "themes_used": themes,
            "total_documents": len(self.all_documents),
            "selected_count": len(selected_ids),
            "selected": selected_ids,
            "ranking": ranked,
            "rationale": self._generate_rationale(selected_ids, themes),
            "metadata": {doc_id: self.all_documents[doc_id] for doc_id in selected_ids}
        }

        print("\n[SELECTION COMPLETE]")
        print("Selected: {} of {} documents".format(len(selected_ids), len(self.all_documents)))
        print("Themes: {}".format(", ".join(themes[:2])))

        return result

    def _rank_documents(self, query: str, themes: List[str], priorities: List[str]) -> List[tuple]:
        """
        Rank all documents by relevance to query + themes + priorities.

        Returns:
            List of (document_id, relevance_score) tuples, sorted by relevance descending
        """
        ranked = []
        query_lower = query.lower()
        themes_lower = [t.lower() for t in themes]

        for doc_id, metadata in self.all_documents.items():
            score = 0
            doc_source_lower = doc_id.lower()

            # 1. Query keyword match in document name (high priority)
            if any(keyword in doc_source_lower for keyword in query_lower.split()):
                score += 30

            # 2. Theme match in document name
            for theme in themes_lower:
                if theme in doc_source_lower or any(word in doc_source_lower for word in theme.split()):
                    score += 20

            # 3. Organization-specific boost
            if "lch" in doc_source_lower or "leeds community" in doc_source_lower:
                score += 15  # Local org gets boost

            # 4. Document type relevance
            doc_type = metadata.get("document_type", "").lower()
            if doc_type in ["strategic_plan", "operational_guidance", "org_specific"]:
                score += 10
            elif doc_type in ["partnership", "general"]:
                score += 5

            # 5. Strategic level (higher = more relevant)
            strategic_level = metadata.get("strategic_level", "").lower()
            if strategic_level == "organization":
                score += 8
            elif strategic_level == "system":
                score += 6
            elif strategic_level == "national":
                score += 4  # National context helpful but not primary

            # 6. Recency boost (recent documents higher)
            date = metadata.get("date", "")
            if "2025" in date or "2024" in date:
                score += 5
            elif "2023" in date:
                score += 2

            ranked.append((doc_id, score))

        # Sort by score descending
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    def _generate_rationale(self, selected_ids: List[str], themes: List[str]) -> str:
        """
        Generate explanation for why these documents were selected.
        """
        org_count = sum(1 for doc_id in selected_ids if "lch" in doc_id.lower())
        recent_count = sum(
            1 for doc_id in selected_ids
            if "2024" in self.all_documents[doc_id].get("date", "")
            or "2025" in self.all_documents[doc_id].get("date", "")
        )

        rationale = """
Selected {} documents based on:
- Primary relevance: Documents directly addressing {} (themes identified by web context)
- Organization focus: {} LCH-specific documents (local priorities)
- Recency: {} recent documents (2024-2025)
- Strategic level: Mix of organization, system, and national context

First search will use these {} documents. If gaps identified, will expand to:
- Additional organization-specific documents
- Related thematic areas
- Broader strategic context
        """.format(
            len(selected_ids),
            ", ".join(themes[:2]) if themes else "key themes",
            org_count,
            recent_count,
            len(selected_ids)
        )

        return rationale.strip()

    def expand_selection(self, gaps: Dict) -> Dict:
        """
        Expand document selection if Critique Agent identifies gaps.

        Args:
            gaps: Gap analysis from Critique Agent
                  Expected keys: "missing_themes", "missing_orgs", "missing_time_period"

        Returns:
            Dict with expanded document selection
        """
        print("\n[EXPANDING SELECTION]")
        print("Gaps identified: {}".format(list(gaps.keys())))

        # Get additional documents based on gaps
        additional = []

        if "missing_themes" in gaps:
            for theme in gaps["missing_themes"]:
                theme_docs = [
                    (doc_id, doc_meta)
                    for doc_id, doc_meta in self.all_documents.items()
                    if theme.lower() in doc_id.lower()
                ]
                additional.extend(theme_docs)

        if "missing_time_period" in gaps:
            period = gaps["missing_time_period"]
            period_docs = [
                (doc_id, doc_meta)
                for doc_id, doc_meta in self.all_documents.items()
                if period in doc_meta.get("date", "")
            ]
            additional.extend(period_docs)

        result = {
            "expansion_reason": gaps.get("reason", ""),
            "additional_documents": [doc_id for doc_id, _ in additional],
            "count": len(additional)
        }

        print("Adding {} additional documents".format(len(additional)))
        return result

    def get_document_summary(self, doc_id: str) -> str:
        """
        Get summary information about a document.
        """
        if doc_id not in self.all_documents:
            return "Document not found"

        meta = self.all_documents[doc_id]
        return "{} [{}] ({})".format(
            doc_id,
            meta.get("document_type", "unknown"),
            meta.get("date", "unknown date")
        )

    def compare_selections(self, selection1: List[str], selection2: List[str]) -> Dict:
        """
        Compare two document selections.
        """
        set1 = set(selection1)
        set2 = set(selection2)

        return {
            "added": list(set2 - set1),
            "removed": list(set1 - set2),
            "overlap": list(set1 & set2),
            "original_count": len(set1),
            "new_count": len(set2),
            "change": len(set2) - len(set1)
        }


def demo_selector():
    """Demo the document selector."""
    from dotenv import load_dotenv
    from langchain_openai import OpenAIEmbeddings

    load_dotenv()

    # Initialize
    embeddings = OpenAIEmbeddings()
    db = Chroma(persist_directory="chroma_db_test", embedding_function=embeddings)
    selector = DocumentSelectorAgent(db)

    # Simulate web context
    web_context = {
        "key_themes": ["Workforce Planning", "Health Inequalities"],
        "national_priorities": ["Staff recruitment", "Equity focus"]
    }

    # Test selection
    query = "How should LCH respond to workforce challenges?"
    result = selector.select_documents(query, web_context)

    print("\n" + "="*70)
    print("DOCUMENT SELECTION RESULT")
    print("="*70)
    print("\nQuery: {}".format(query))
    print("Web themes: {}".format(", ".join(web_context["key_themes"])))
    print("\nSelected Documents ({}/{}):".format(result["selected_count"], result["total_documents"]))
    for doc_id in result["selected"][:5]:
        print("  - {}".format(selector.get_document_summary(doc_id)))
    if result["selected_count"] > 5:
        print("  ... and {} more".format(result["selected_count"] - 5))

    print("\nRationale:")
    print(result["rationale"])

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    demo_selector()
