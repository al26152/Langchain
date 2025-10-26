"""
evidence_agent.py

EVIDENCE RETRIEVAL AGENT WITH COVERAGE METRICS

PURPOSE:
  Retrieves evidence from ChromaDB with comprehensive coverage analysis.
  Tracks source diversity, date distribution, and identifies gaps.

FEATURES:
  - Semantic search with ChromaDB
  - Source coverage metrics (unique documents consulted)
  - Date distribution analysis (recent vs archival)
  - Theme coverage tracking
  - Gap identification (missing documents, date gaps)
  - Epistemic type classification (FACT/ASSUMPTION/INFERENCE)

USAGE:
  from evidence_agent import EvidenceAgent

  agent = EvidenceAgent(vectordb)
  result = agent.search(query, iteration_num=1, previous_gaps=[])
"""

import sys
import os
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

# Import Knowledge Graph Agent
try:
    from analysis.multi_agent.knowledge_graph_agent import KnowledgeGraphAgent
except ImportError:
    KnowledgeGraphAgent = None  # Fallback if KG not available


class EvidenceAgent:
    """Agent responsible for evidence retrieval and coverage analysis."""

    def __init__(self, vectordb: Chroma, llm: Optional[ChatOpenAI] = None, use_kg: bool = True):
        """
        Initialize Evidence Agent.

        Args:
            vectordb: ChromaDB vector store instance
            llm: Language model for epistemic classification (optional)
            use_kg: Whether to use Knowledge Graph for query expansion (default True)
        """
        self.vectordb = vectordb
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        self.total_documents = self._count_total_documents()

        # Initialize Knowledge Graph Agent if available
        self.kg_agent = None
        if use_kg and KnowledgeGraphAgent is not None:
            try:
                self.kg_agent = KnowledgeGraphAgent()
                print("[OK] Knowledge Graph Agent initialized")
            except Exception as e:
                print(f"[WARNING] Could not initialize Knowledge Graph Agent: {e}")
                self.kg_agent = None

    def _count_total_documents(self) -> int:
        """Count total unique documents in ChromaDB."""
        try:
            all_data = self.vectordb._collection.get(include=["metadatas"])
            sources = set(m.get("source", "") for m in all_data.get("metadatas", []))
            return len(sources)
        except:
            return 30  # Fallback to known count

    def search(
        self,
        query: str,
        iteration_num: int = 1,
        previous_gaps: Optional[List[Dict]] = None,
        k: int = 20
    ) -> Dict:
        """
        Execute evidence search with coverage analysis.

        Args:
            query: Search query
            iteration_num: Current iteration number
            previous_gaps: Gaps identified in previous iterations
            k: Number of chunks to retrieve

        Returns:
            Dict containing:
            - evidence: List of evidence chunks with metadata
            - metrics: Coverage metrics
            - gaps: Identified gaps
        """
        print(f"\n[ITERATION {iteration_num}] Evidence Agent: Searching for evidence...")

        # Expand query based on previous gaps
        expanded_query = self._expand_query(query, previous_gaps)

        # Retrieve chunks from ChromaDB
        results = self.vectordb.similarity_search(expanded_query, k=k)

        # Extract evidence with metadata
        evidence = []
        for i, doc in enumerate(results):
            evidence.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "date": doc.metadata.get("date"),
                "theme": doc.metadata.get("theme", "N/A"),
                "audience": doc.metadata.get("audience", "N/A"),
                "chunk_type": doc.metadata.get("chunk_type", "narrative"),
                "epistemic_type": None,  # Will be classified later
                "confidence": None,  # Will be calculated later
            })

        # Calculate coverage metrics
        metrics = self._calculate_metrics(evidence)

        # Identify gaps
        gaps = self._identify_gaps(evidence, metrics, query)

        # Log progress
        print(f"[ITERATION {iteration_num}] Retrieved {len(evidence)} chunks from {metrics['source_count']} documents")
        print(f"[ITERATION {iteration_num}] Coverage: {metrics['coverage_percent']:.1f}% of total documents")

        return {
            "evidence": evidence,
            "metrics": metrics,
            "gaps": gaps,
            "iteration": iteration_num,
        }

    def _expand_query(self, query: str, previous_gaps: Optional[List[Dict]]) -> str:
        """
        Expand query using Knowledge Graph (iteration 1) or gaps (subsequent iterations).

        Args:
            query: Original query
            previous_gaps: Gaps from previous iterations

        Returns:
            Expanded query string
        """
        # Iteration 1: Use Knowledge Graph for entity-based expansion
        if not previous_gaps and self.kg_agent:
            try:
                kg_result = self.kg_agent.expand_query(query, max_expansion=5)

                if kg_result.get("kg_used") and kg_result.get("expansion_terms"):
                    print(f"[KG EXPANSION] Found entities: {', '.join([e['entity_name'] for e in kg_result['entities_found']])}")
                    print(f"[KG EXPANSION] Added related: {', '.join(kg_result['expansion_terms'][:3])}...")
                    return kg_result["expanded_query"]
            except Exception as e:
                print(f"[WARNING] KG expansion failed: {e}")

        # Subsequent iterations: Use gap-based expansion
        if previous_gaps:
            gap_terms = []
            for gap in previous_gaps:
                if gap.get("type") == "missing_document" and "document" in gap:
                    # Extract key terms from missing document name
                    doc_name = gap["document"].replace(".md", "").replace("-", " ")
                    gap_terms.append(doc_name)
                elif gap.get("type") == "missing_theme" and "theme" in gap:
                    gap_terms.append(gap["theme"])
                elif gap.get("type") == "missing_relationship" and "action" in gap:
                    # Add relationship-specific terms from KG gaps
                    gap_terms.append(gap.get("relationship", ""))

            if gap_terms:
                expanded = f"{query} {' '.join(gap_terms)}"
                print(f"[GAP EXPANSION] Added: {', '.join(gap_terms)}")
                return expanded

        return query

    def _calculate_metrics(self, evidence: List[Dict]) -> Dict:
        """Calculate coverage metrics from evidence."""
        # Source diversity
        unique_sources = set(e["source"] for e in evidence)
        source_count = len(unique_sources)
        coverage_percent = (source_count / self.total_documents) * 100

        # Date distribution
        date_counts = {"recent": 0, "moderate": 0, "old": 0, "unknown": 0}
        today = datetime.now()

        for e in evidence:
            date_str = e.get("date")
            if not date_str:
                date_counts["unknown"] += 1
                continue

            try:
                doc_date = datetime.strptime(date_str, "%Y-%m-%d")
                years_old = (today - doc_date).days / 365.25

                if years_old < 1:
                    date_counts["recent"] += 1
                elif years_old < 3:
                    date_counts["moderate"] += 1
                else:
                    date_counts["old"] += 1
            except:
                date_counts["unknown"] += 1

        # Theme diversity
        unique_themes = set(e["theme"] for e in evidence if e["theme"] != "N/A")

        # Source distribution (which sources are heavily used)
        source_distribution = defaultdict(int)
        for e in evidence:
            source_distribution[e["source"]] += 1

        return {
            "source_count": source_count,
            "coverage_percent": coverage_percent,
            "unique_sources": list(unique_sources),
            "date_distribution": date_counts,
            "theme_count": len(unique_themes),
            "unique_themes": list(unique_themes),
            "source_distribution": dict(source_distribution),
            "total_chunks": len(evidence),
        }

    def _identify_gaps(self, evidence: List[Dict], metrics: Dict, query: str) -> List[Dict]:
        """Identify gaps in evidence coverage."""
        gaps = []

        # Gap 0: Knowledge Graph relationship gaps (if KG available)
        if self.kg_agent:
            try:
                retrieved_sources = list(set(e["source"] for e in evidence))
                kg_gaps = self.kg_agent.identify_missing_relationships(query, retrieved_sources)
                gaps.extend(kg_gaps)
            except Exception as e:
                pass  # Silently continue if KG gap detection fails

        # Gap 1: Low source coverage
        if metrics["source_count"] < 5:
            gaps.append({
                "type": "low_source_coverage",
                "severity": "HIGH",
                "message": f"Only {metrics['source_count']}/{self.total_documents} documents consulted",
                "action": "Expand search to more documents",
                "metric": metrics["coverage_percent"],
            })
        elif metrics["source_count"] < 8:
            gaps.append({
                "type": "moderate_source_coverage",
                "severity": "MEDIUM",
                "message": f"{metrics['source_count']}/{self.total_documents} documents consulted (adequate but could be better)",
                "action": "Consider searching related topics",
                "metric": metrics["coverage_percent"],
            })

        # Gap 2: Date distribution issues
        total_dated = sum(metrics["date_distribution"].values()) - metrics["date_distribution"]["unknown"]
        if total_dated > 0:
            recent_percent = (metrics["date_distribution"]["recent"] / total_dated) * 100
            old_percent = (metrics["date_distribution"]["old"] / total_dated) * 100

            if recent_percent < 30:
                gaps.append({
                    "type": "insufficient_recent_evidence",
                    "severity": "MEDIUM",
                    "message": f"Only {recent_percent:.0f}% of evidence is from recent documents (<1 year)",
                    "action": "Search for more recent documents (2024-2025)",
                    "metric": recent_percent,
                })

            if old_percent > 60:
                gaps.append({
                    "type": "overreliance_on_old_evidence",
                    "severity": "MEDIUM",
                    "message": f"{old_percent:.0f}% of evidence is from documents >3 years old",
                    "action": "Validate with more recent sources",
                    "metric": old_percent,
                })

        # Gap 3: Single-source dominance
        max_chunks_per_source = max(metrics["source_distribution"].values())
        if max_chunks_per_source > len(evidence) * 0.5:
            dominant_source = [s for s, c in metrics["source_distribution"].items() if c == max_chunks_per_source][0]
            gaps.append({
                "type": "single_source_dominance",
                "severity": "MEDIUM",
                "message": f"Over 50% of evidence from one source: {dominant_source}",
                "action": "Diversify sources to avoid bias",
                "document": dominant_source,
            })

        # Gap 4: Theme diversity
        if metrics["theme_count"] < 2:
            gaps.append({
                "type": "low_theme_diversity",
                "severity": "LOW",
                "message": f"Evidence spans only {metrics['theme_count']} theme(s)",
                "action": "Search related themes for broader perspective",
                "metric": metrics["theme_count"],
            })

        return gaps

    def classify_epistemic_type(self, evidence_chunk: Dict) -> Tuple[str, float]:
        """
        Classify evidence as FACT, ASSUMPTION, or INFERENCE.

        Args:
            evidence_chunk: Evidence chunk with content and metadata

        Returns:
            Tuple of (epistemic_type, confidence)
        """
        content = evidence_chunk["content"]
        source = evidence_chunk["source"]
        chunk_type = evidence_chunk.get("chunk_type", "narrative")

        # Simple heuristic-based classification (fast)
        # Can be enhanced with LLM if needed

        # FACT indicators
        fact_indicators = [
            "according to",
            "reported",
            "stated",
            "data shows",
            "statistics",
            "figures show",
            "recorded",
            "measured",
            "observed",
            chunk_type == "table_data",
            "annual report" in source.lower(),
            "survey" in source.lower(),
        ]

        # ASSUMPTION indicators
        assumption_indicators = [
            "projected",
            "estimated",
            "expected",
            "anticipated",
            "assuming",
            "likely",
            "predicted",
            "forecasted",
            "trend suggests",
        ]

        # INFERENCE indicators
        inference_indicators = [
            "therefore",
            "thus",
            "consequently",
            "implies",
            "suggests that",
            "indicates that",
            "can be concluded",
            "this means",
            "as a result",
        ]

        content_lower = content.lower()

        fact_score = sum(1 for indicator in fact_indicators if
                        (isinstance(indicator, str) and indicator in content_lower) or
                        (isinstance(indicator, bool) and indicator))

        assumption_score = sum(1 for indicator in assumption_indicators if indicator in content_lower)
        inference_score = sum(1 for indicator in inference_indicators if indicator in content_lower)

        # Classify based on highest score
        scores = {
            "FACT": fact_score,
            "ASSUMPTION": assumption_score,
            "INFERENCE": inference_score,
        }

        epistemic_type = max(scores, key=scores.get)

        # If all scores are 0, default to FACT for hard data, INFERENCE for narrative
        if max(scores.values()) == 0:
            if chunk_type == "table_data" or "annual report" in source.lower():
                epistemic_type = "FACT"
                confidence = 0.7
            else:
                epistemic_type = "INFERENCE"
                confidence = 0.5
        else:
            # Confidence based on score margin
            max_score = max(scores.values())
            second_max = sorted(scores.values())[-2]
            confidence = 0.5 + (0.3 * (max_score - second_max))

        return epistemic_type, min(confidence, 0.95)

    def tag_evidence_batch(self, evidence_list: List[Dict]) -> List[Dict]:
        """
        Tag entire batch of evidence with epistemic types.

        Args:
            evidence_list: List of evidence chunks

        Returns:
            Same list with epistemic_type and confidence added
        """
        for evidence in evidence_list:
            epistemic_type, confidence = self.classify_epistemic_type(evidence)
            evidence["epistemic_type"] = epistemic_type
            evidence["confidence"] = confidence

        return evidence_list
