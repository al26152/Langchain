"""
enhanced_evidence_agent.py

EVIDENCE RETRIEVAL AGENT WITH INTRA-CORPUS CONTEXT MAPPING

PURPOSE:
  Extends the Evidence Agent to use intra-corpus context mapping,
  surfacing relationships between documents and evidence chains.

FEATURES:
  - Standard semantic search (from original Evidence Agent)
  - Context mapping integration (relationships, concept groups, chains)
  - Evidence chain discovery
  - Related document suggestions
  - Concept group expansion

USAGE:
  from enhanced_evidence_agent import EnhancedEvidenceAgent

  agent = EnhancedEvidenceAgent(vectordb, context_map_path="context_map.json")
  result = agent.search(query, iteration_num=1, previous_gaps=[])

  # Results include:
  # - Original chunks
  # - Related documents (from context map)
  # - Evidence chains (from context map)
  # - Concept groups
"""

import sys
import os
from typing import List, Dict, Optional, Set
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

# Import original Evidence Agent
import importlib.util
import importlib

# Load evidence_agent
spec = importlib.util.spec_from_file_location(
    "evidence_agent",
    os.path.join(os.path.dirname(__file__), "evidence_agent.py")
)
evidence_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence_agent_module)
EvidenceAgent = evidence_agent_module.EvidenceAgent

# Load context_mapper
spec = importlib.util.spec_from_file_location(
    "context_mapper",
    os.path.join(os.path.dirname(__file__), "context_mapper.py")
)
context_mapper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_mapper_module)
ContextMap = context_mapper_module.ContextMap


class EnhancedEvidenceAgent(EvidenceAgent):
    """
    Extended Evidence Agent that incorporates intra-corpus context mapping
    to surface relationships and evidence chains.
    """

    def __init__(
        self,
        vectordb: Chroma,
        llm: Optional[ChatOpenAI] = None,
        context_map_path: str = "context_map.json",
        use_kg: bool = True,
        use_entity_resolution: bool = True
    ):
        """
        Initialize Enhanced Evidence Agent.

        Args:
            vectordb: ChromaDB vector store instance
            llm: Language model for epistemic classification (optional)
            context_map_path: Path to context map JSON file
            use_kg: Whether to use Knowledge Graph
            use_entity_resolution: Whether to use Entity Resolver
        """
        # Initialize parent class
        super().__init__(vectordb, llm, use_kg, use_entity_resolution)

        # Load context map
        self.context_map = None
        self.context_map_path = context_map_path
        if os.path.exists(context_map_path):
            try:
                self.context_map = ContextMap.load(context_map_path)
                print("[OK] Context Map loaded for enhanced retrieval")
            except Exception as e:
                print("[WARNING] Could not load context map: {}".format(e))
                self.context_map = None
        else:
            print("[WARNING] Context map not found at {}".format(context_map_path))

    def search_with_context(self, query: str, iteration_num: int = 1, previous_gaps: List[str] = None):
        """
        Enhanced search incorporating context mapping.

        Returns:
            Dict with:
            - chunks: Retrieved evidence chunks (from parent)
            - sources: Source documents (from parent)
            - related_documents: Documents related by context mapping
            - evidence_chains: Problem-response-effectiveness chains
            - concept_groups: Thematic document clusters
            - context_insights: Notes about relationships discovered
        """
        # First, do standard search
        base_result = self.search(query, iteration_num, previous_gaps or [])

        if not self.context_map:
            return base_result

        # Enhance with context mapping
        enhanced_result = base_result.copy()

        # Get source documents from base result
        source_docs = set()
        if "sources" in base_result:
            for source_info in base_result["sources"]:
                if isinstance(source_info, dict):
                    source_docs.add(source_info.get("source", ""))
                else:
                    source_docs.add(str(source_info))

        # Find related documents using context map
        related_by_concept = self._find_related_documents(source_docs, query)
        enhanced_result["related_documents_by_concept"] = related_by_concept

        # Find relevant evidence chains
        evidence_chains = self._find_evidence_chains(query)
        enhanced_result["evidence_chains"] = evidence_chains

        # Find concept groups
        concept_groups = self._find_relevant_concept_groups(source_docs, query)
        enhanced_result["concept_groups"] = concept_groups

        # Add context insights
        context_insights = self._generate_context_insights(
            source_docs, related_by_concept, evidence_chains
        )
        enhanced_result["context_insights"] = context_insights

        return enhanced_result

    def _find_related_documents(self, source_docs: Set[str], query: str) -> Dict[str, List[str]]:
        """Find documents related to the retrieved sources through context mapping."""
        related = {}

        for doc_id in source_docs:
            relationships = self.context_map.get_related_documents(doc_id)
            if relationships:
                related[doc_id] = []
                for related_doc, rel_type, strength in relationships:
                    if strength > 0.5:  # Only strong relationships
                        related[doc_id].append({
                            "document": related_doc,
                            "relationship": rel_type,
                            "strength": strength
                        })

        return related

    def _find_evidence_chains(self, query: str) -> List[Dict]:
        """Find evidence chains relevant to the query."""
        if not self.context_map:
            return []

        chains = []
        query_lower = query.lower()

        # Search for chains matching query keywords
        for chain in self.context_map.evidence_chains:
            # Check if chain concept matches query
            if chain.concept.lower() in query_lower or \
               any(word in query_lower for word in chain.concept.lower().split()):

                chain_data = {
                    "concept": chain.concept,
                    "problem_document": chain.problem_doc,
                    "response_document": chain.response_doc,
                    "effectiveness_document": chain.effectiveness_doc,
                    "description": chain.description
                }
                chains.append(chain_data)

        return chains

    def _find_relevant_concept_groups(self, source_docs: Set[str], query: str) -> List[Dict]:
        """Find concept groups relevant to the query or source docs."""
        if not self.context_map:
            return []

        relevant_groups = []
        query_lower = query.lower()

        for group_name, group in self.context_map.concept_groups.items():
            # Check if group is relevant to query or source docs
            group_relevant = any(
                word.lower() in query_lower
                for word in group.group_name.lower().split()
            )

            if group_relevant or any(doc in source_docs for doc in group.documents):
                group_data = {
                    "name": group.group_name,
                    "documents": group.documents,
                    "concepts": group.concepts,
                    "documents_in_retrieval": [
                        doc for doc in group.documents if doc in source_docs
                    ]
                }
                relevant_groups.append(group_data)

        return relevant_groups

    def _generate_context_insights(self, source_docs: Set[str], related_docs: Dict,
                                   evidence_chains: List[Dict]) -> List[str]:
        """Generate insights about document relationships discovered."""
        insights = []

        # Insight 1: Related documents
        if related_docs:
            total_related = sum(len(rels) for rels in related_docs.values())
            insights.append(
                "Found {} additional documents related to retrieved sources "
                "through concept mapping".format(total_related)
            )

        # Insight 2: Evidence chains
        if evidence_chains:
            insights.append(
                "Identified {} evidence chains showing Problem -> Response -> "
                "Effectiveness patterns for key concepts".format(len(evidence_chains))
            )

            for chain in evidence_chains:
                if chain.get("concept"):
                    insights.append(
                        "For '{}': {} shows problem, {} shows response{}".format(
                            chain["concept"],
                            chain.get("problem_document", "").split("/")[-1][:30],
                            chain.get("response_document", "").split("/")[-1][:30],
                            ", {} shows effectiveness".format(
                                chain.get("effectiveness_document", "").split("/")[-1][:20]
                            ) if chain.get("effectiveness_document") else ""
                        )
                    )

        if not insights:
            insights.append(
                "Context map loaded but no additional relationships found for this query"
            )

        return insights

    def search(self, query: str, iteration_num: int = 1, previous_gaps: List[str] = None):
        """
        Search with context mapping integration.
        Overrides parent search to include context enhancements.
        """
        # Don't recurse - call parent directly first
        base_result = super().search(query, iteration_num, previous_gaps or [])

        if not self.context_map:
            return base_result

        # Enhance with context mapping
        return self._enhance_result_with_context(base_result)

    def _enhance_result_with_context(self, base_result: Dict) -> Dict:
        """Add context mapping enhancements to base result."""
        enhanced_result = base_result.copy()

        # Get source documents from base result
        source_docs = set()
        if "sources" in base_result:
            for source_info in base_result["sources"]:
                if isinstance(source_info, dict):
                    source_docs.add(source_info.get("source", ""))
                else:
                    source_docs.add(str(source_info))

        # Add context enhancements only if we found sources
        if source_docs and len(base_result.get("chunks", [])) > 0:
            enhanced_result["context_map_available"] = True

            # Find related documents
            related = self._find_related_documents(source_docs, "")
            if related:
                enhanced_result["related_documents_by_concept"] = related

            # Find evidence chains
            chains = self.context_map.evidence_chains
            if chains:
                enhanced_result["evidence_chains"] = [c.to_dict() for c in chains[:3]]

            # Generate insights
            insights = self._generate_context_insights(source_docs, related, chains)
            enhanced_result["context_insights"] = insights
        else:
            enhanced_result["context_map_available"] = False

        return enhanced_result


def demonstrate_enhanced_retrieval():
    """Demo function showing enhanced retrieval in action."""
    from dotenv import load_dotenv

    load_dotenv()

    # Initialize
    embeddings = __import__('langchain_openai', fromlist=['OpenAIEmbeddings']).OpenAIEmbeddings()
    db = Chroma(persist_directory="chroma_db_test", embedding_function=embeddings)

    agent = EnhancedEvidenceAgent(db, context_map_path="context_map.json")

    # Example query
    query = "What are the key workforce challenges for Leeds Community Healthcare?"

    print("\n" + "="*70)
    print("ENHANCED EVIDENCE RETRIEVAL DEMO")
    print("="*70)
    print("\nQuery: {}".format(query))

    # Standard search
    result = agent.search(query, iteration_num=1)

    print("\n[BASIC RETRIEVAL]")
    print("  Retrieved chunks: {}".format(len(result.get("chunks", []))))
    print("  Sources: {}".format(len(result.get("sources", []))))

    # Check for enhanced results
    if "related_documents_by_concept" in result:
        print("\n[CONTEXT MAPPING - RELATED DOCUMENTS]")
        for doc, rels in result.get("related_documents_by_concept", {}).items():
            print("  {}:".format(doc))
            for rel in rels:
                print("    -> {} ({})".format(rel["document"], rel["relationship"]))

    if "evidence_chains" in result:
        print("\n[EVIDENCE CHAINS]")
        for chain in result.get("evidence_chains", []):
            print("  {}:".format(chain["concept"]))
            print("    Problem: {}".format(chain["problem_document"]))
            print("    Response: {}".format(chain["response_document"]))

    if "context_insights" in result:
        print("\n[CONTEXT INSIGHTS]")
        for insight in result.get("context_insights", []):
            print("  - {}".format(insight))

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    demonstrate_enhanced_retrieval()
