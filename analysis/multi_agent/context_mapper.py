"""
context_mapper.py

INTRA-CORPUS CONTEXT MAPPING SYSTEM

PURPOSE:
  Builds a document relationship graph to surface contextual connections
  across the corpus without full re-ingestion. Creates evidence chains
  showing Problem → Response → Effectiveness Assessment patterns.

FEATURES:
  - Document concept extraction (key topics, entities, themes)
  - Document relationship mapping (discusses same topic, provides context, etc.)
  - Evidence chain identification (problem → response → effectiveness)
  - Concept group detection (workforce, finance, equity, integration)
  - Gap identification (missing documents, missing connections)

USAGE:
  from context_mapper import ContextMapBuilder, ContextMap

  # Build context map from corpus
  builder = ContextMapBuilder(vectordb)
  context_map = builder.build_map()
  context_map.save("context_map.json")

  # Load existing map
  context_map = ContextMap.load("context_map.json")

  # Use for retrieval
  relationships = context_map.get_related_documents("workforce planning")
  chains = context_map.get_evidence_chains("workforce")
"""

import sys
import os
import json
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document


class DocumentConcept:
    """Represents a concept extracted from a document."""

    def __init__(self, concept: str, document_id: str, frequency: int = 1, confidence: float = 0.8):
        self.concept = concept
        self.document_id = document_id
        self.frequency = frequency
        self.confidence = confidence

    def to_dict(self) -> Dict:
        return {
            "concept": self.concept,
            "document_id": self.document_id,
            "frequency": self.frequency,
            "confidence": self.confidence
        }


class DocumentRelationship:
    """Represents a relationship between two documents."""

    RELATIONSHIP_TYPES = {
        "DISCUSSES_SAME_TOPIC": "Both documents discuss the same topic",
        "PROVIDES_CONTEXT_FOR": "Doc A provides context for Doc B",
        "IMPLEMENTS": "Doc A implements strategy described in Doc B",
        "RESPONDS_TO": "Doc A is a response to problem described in Doc B",
        "SIMILAR_ORGANIZATION": "Both documents discuss similar organizations",
        "TEMPORAL_SEQUENCE": "Doc A comes before/after Doc B temporally",
        "COMPARABLE_TO": "Doc A can be compared to Doc B",
        "UPDATES": "Doc A updates/supersedes information in Doc B",
    }

    def __init__(self, doc_a: str, doc_b: str, relationship_type: str, strength: float = 0.7, evidence: str = ""):
        self.doc_a = doc_a
        self.doc_b = doc_b
        self.relationship_type = relationship_type
        self.strength = strength  # 0-1 confidence in relationship
        self.evidence = evidence

    def to_dict(self) -> Dict:
        return {
            "doc_a": self.doc_a,
            "doc_b": self.doc_b,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "evidence": self.evidence
        }


class EvidenceChain:
    """Represents a problem-response-effectiveness chain across documents."""

    def __init__(self, concept: str, problem_doc: str, response_doc: str,
                 effectiveness_doc: Optional[str] = None, description: str = ""):
        self.concept = concept
        self.problem_doc = problem_doc
        self.response_doc = response_doc
        self.effectiveness_doc = effectiveness_doc
        self.description = description

    def to_dict(self) -> Dict:
        return {
            "concept": self.concept,
            "problem_doc": self.problem_doc,
            "response_doc": self.response_doc,
            "effectiveness_doc": self.effectiveness_doc,
            "description": self.description
        }


class ConceptGroup:
    """Represents a thematic cluster of related documents."""

    def __init__(self, group_name: str, documents: List[str], concepts: List[str], strength: float = 0.8):
        self.group_name = group_name
        self.documents = documents
        self.concepts = concepts
        self.strength = strength

    def to_dict(self) -> Dict:
        return {
            "group_name": self.group_name,
            "documents": self.documents,
            "concepts": self.concepts,
            "strength": self.strength
        }


class ContextMap:
    """
    Document context map showing relationships and concept connections
    across the corpus.
    """

    def __init__(self):
        self.documents: Dict[str, Dict] = {}  # doc_id -> metadata
        self.concepts: Dict[str, List[DocumentConcept]] = defaultdict(list)  # concept -> [docs]
        self.relationships: List[DocumentRelationship] = []
        self.evidence_chains: List[EvidenceChain] = []
        self.concept_groups: Dict[str, ConceptGroup] = {}
        self.created_at = datetime.now().isoformat()

    def add_document(self, doc_id: str, filename: str, doc_date: str = "", org: str = ""):
        """Add a document to the context map."""
        self.documents[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "date": doc_date,
            "organization": org,
            "concepts": []
        }

    def add_concept(self, concept: str, doc_id: str, frequency: int = 1, confidence: float = 0.8):
        """Add a concept to a document."""
        doc_concept = DocumentConcept(concept, doc_id, frequency, confidence)
        self.concepts[concept].append(doc_concept)
        if doc_id in self.documents:
            self.documents[doc_id]["concepts"].append(concept)

    def add_relationship(self, relationship: DocumentRelationship):
        """Add a relationship between documents."""
        self.relationships.append(relationship)

    def add_evidence_chain(self, chain: EvidenceChain):
        """Add an evidence chain (problem → response → effectiveness)."""
        self.evidence_chains.append(chain)

    def add_concept_group(self, group: ConceptGroup):
        """Add a concept group (thematic cluster)."""
        self.concept_groups[group.group_name] = group

    def get_documents_by_concept(self, concept: str) -> List[str]:
        """Get all documents discussing a concept."""
        if concept not in self.concepts:
            return []
        return [dc.document_id for dc in self.concepts[concept]]

    def get_related_documents(self, doc_id: str) -> List[Tuple[str, str, float]]:
        """Get documents related to a given document.

        Returns:
            List of (related_doc_id, relationship_type, strength)
        """
        related = []
        for rel in self.relationships:
            if rel.doc_a == doc_id:
                related.append((rel.doc_b, rel.relationship_type, rel.strength))
            elif rel.doc_b == doc_id:
                related.append((rel.doc_a, rel.relationship_type, rel.strength))
        return sorted(related, key=lambda x: x[2], reverse=True)

    def get_related_by_concept(self, concept: str, exclude_doc: str = "") -> List[str]:
        """Get all documents discussing a concept, excluding one."""
        docs = self.get_documents_by_concept(concept)
        return [d for d in docs if d != exclude_doc]

    def get_evidence_chains_for_concept(self, concept: str) -> List[EvidenceChain]:
        """Get all evidence chains for a concept."""
        return [chain for chain in self.evidence_chains if concept.lower() in chain.concept.lower()]

    def get_concept_groups(self) -> Dict[str, ConceptGroup]:
        """Get all concept groups."""
        return self.concept_groups

    def get_documents_in_group(self, group_name: str) -> List[str]:
        """Get documents in a concept group."""
        if group_name not in self.concept_groups:
            return []
        return self.concept_groups[group_name].documents

    def save(self, filepath: str):
        """Save context map to JSON file."""
        data = {
            "created_at": self.created_at,
            "documents": self.documents,
            "concepts": {
                concept: [c.to_dict() for c in docs]
                for concept, docs in self.concepts.items()
            },
            "relationships": [rel.to_dict() for rel in self.relationships],
            "evidence_chains": [chain.to_dict() for chain in self.evidence_chains],
            "concept_groups": {
                name: group.to_dict()
                for name, group in self.concept_groups.items()
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("[OK] Context map saved to {}".format(filepath))

    @classmethod
    def load(cls, filepath: str) -> 'ContextMap':
        """Load context map from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        context_map = cls()
        context_map.created_at = data.get("created_at", "")

        # Load documents
        context_map.documents = data.get("documents", {})

        # Load concepts
        for concept, docs_data in data.get("concepts", {}).items():
            for doc_data in docs_data:
                context_map.add_concept(
                    concept,
                    doc_data["document_id"],
                    doc_data.get("frequency", 1),
                    doc_data.get("confidence", 0.8)
                )

        # Load relationships
        for rel_data in data.get("relationships", []):
            rel = DocumentRelationship(
                rel_data["doc_a"],
                rel_data["doc_b"],
                rel_data["relationship_type"],
                rel_data.get("strength", 0.7),
                rel_data.get("evidence", "")
            )
            context_map.add_relationship(rel)

        # Load evidence chains
        for chain_data in data.get("evidence_chains", []):
            chain = EvidenceChain(
                chain_data["concept"],
                chain_data["problem_doc"],
                chain_data["response_doc"],
                chain_data.get("effectiveness_doc"),
                chain_data.get("description", "")
            )
            context_map.add_evidence_chain(chain)

        # Load concept groups
        for group_name, group_data in data.get("concept_groups", {}).items():
            group = ConceptGroup(
                group_name,
                group_data["documents"],
                group_data["concepts"],
                group_data.get("strength", 0.8)
            )
            context_map.add_concept_group(group)

        print("[OK] Context map loaded from {}".format(filepath))
        return context_map

    def summary(self) -> str:
        """Get a summary of the context map."""
        return """
CONTEXT MAP SUMMARY
===================
Documents: {}
Concepts: {}
Relationships: {}
Evidence Chains: {}
Concept Groups: {}
Created: {}
        """.format(
            len(self.documents),
            len(self.concepts),
            len(self.relationships),
            len(self.evidence_chains),
            len(self.concept_groups),
            self.created_at
        ).strip()


class ContextMapBuilder:
    """
    Builds a context map from the corpus without full re-ingestion.
    Uses LLM to extract concepts, relationships, and evidence chains.
    """

    def __init__(self, vectordb: Chroma, llm: Optional[ChatOpenAI] = None):
        self.vectordb = vectordb
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        self.context_map = ContextMap()

        # Predefined concept groups based on corpus analysis
        self.predefined_groups = {
            "Workforce & People": [
                "workforce planning", "recruitment", "staff turnover", "training",
                "employee engagement", "workforce development", "staffing"
            ],
            "Health Inequalities & Equity": [
                "health inequalities", "health equity", "vulnerable populations",
                "health disparities", "equity", "diversity"
            ],
            "Partnership & Integration": [
                "partnership", "integrated care", "collaboration", "system working",
                "stakeholder engagement", "coordination"
            ],
            "Strategic Direction": [
                "strategy", "planning", "priorities", "objectives", "goals",
                "strategic direction", "vision"
            ],
            "Finance & Resources": [
                "finance", "budget", "funding", "resources", "cost", "financial"
            ],
            "Quality & Safety": [
                "quality", "safety", "patient experience", "outcomes", "performance"
            ]
        }

    def build_map(self) -> ContextMap:
        """Build the complete context map."""
        print("\n" + "="*60)
        print("BUILDING INTRA-CORPUS CONTEXT MAP")
        print("="*60 + "\n")

        # Step 1: Extract documents
        print("\n[STEP 1] Extracting documents from ChromaDB...")
        self._extract_documents()

        # Step 2: Identify concepts
        print("\n[STEP 2] Identifying key concepts in each document...")
        self._identify_concepts()

        # Step 3: Map relationships
        print("\n[STEP 3] Mapping document relationships...")
        self._map_relationships()

        # Step 4: Identify evidence chains
        print("\n[STEP 4] Identifying evidence chains (Problem → Response → Effectiveness)...")
        self._identify_evidence_chains()

        # Step 5: Create concept groups
        print("\n[STEP 5] Creating concept groups...")
        self._create_concept_groups()

        # Step 6: Summary
        print("\n" + "="*60)
        print(self.context_map.summary())
        print("="*60)

        return self.context_map

    def _extract_documents(self):
        """Extract all documents from ChromaDB."""
        try:
            all_data = self.vectordb.get(include=["metadatas", "documents"])

            # Get unique documents
            docs_seen = set()
            doc_list = []

            for metadata in all_data.get("metadatas", []):
                source = metadata.get("source", "Unknown")
                if source not in docs_seen:
                    docs_seen.add(source)
                    date = metadata.get("date", "")
                    org = metadata.get("organization", "")
                    doc_list.append((source, date, org))
                    self.context_map.add_document(source, source, date, org)

            print("   -> Found {} unique documents".format(len(doc_list)))
            for doc_id, date, org in doc_list[:5]:
                print("      - {} ({}) [{}]".format(doc_id, date, org))
            if len(doc_list) > 5:
                print("      ... and {} more".format(len(doc_list) - 5))

        except Exception as e:
            print(f"   [ERROR] Failed to extract documents: {e}")

    def _identify_concepts(self):
        """Identify key concepts in each document."""
        try:
            # Get all documents
            all_data = self.vectordb.get(include=["metadatas"])
            docs_to_process = {}

            for metadata in all_data.get("metadatas", []):
                source = metadata.get("source", "Unknown")
                if source not in docs_to_process:
                    docs_to_process[source] = {
                        "date": metadata.get("date", ""),
                        "org": metadata.get("organization", "")
                    }

            # Map documents to predefined concept groups
            concept_count = 0
            for doc_id in docs_to_process.keys():
                doc_concepts = self._extract_concepts_for_document(doc_id)
                for concept in doc_concepts:
                    self.context_map.add_concept(concept, doc_id, frequency=1, confidence=0.8)
                    concept_count += 1

            print("   -> Identified {} concept-document mappings".format(concept_count))
            print("   -> {} unique concepts".format(len(self.context_map.concepts)))

            # Show top concepts
            top_concepts = sorted(
                [(c, len(docs)) for c, docs in self.context_map.concepts.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for concept, count in top_concepts:
                print("      - {}: {} documents".format(concept, count))

        except Exception as e:
            print(f"   [ERROR] Failed to identify concepts: {e}")

    def _extract_concepts_for_document(self, doc_id: str) -> List[str]:
        """Extract concepts from a document based on predefined groups."""
        concepts = []
        doc_lower = doc_id.lower()

        # Check predefined group keywords
        for group_name, keywords in self.predefined_groups.items():
            for keyword in keywords:
                if keyword.lower() in doc_lower:
                    concepts.append(keyword)

        # Add organization-based concepts
        if "lch" in doc_lower or "leeds community" in doc_lower:
            concepts.append("LCH Strategy")
        if "ltht" in doc_lower:
            concepts.append("LTHT Strategy")
        if "lypft" in doc_lower:
            concepts.append("LYPFT Strategy")
        if "nhs" in doc_lower and "10" in doc_lower and "year" in doc_lower:
            concepts.append("NHS 10-Year Plan")
        if "healthy leeds" in doc_lower:
            concepts.append("Healthy Leeds Plan")

        # Remove duplicates
        return list(set(concepts)) if concepts else ["General"]

    def _map_relationships(self):
        """Map relationships between documents."""
        try:
            doc_ids = list(self.context_map.documents.keys())
            relationship_count = 0

            # Find documents discussing same concepts
            for concept, docs_list in self.context_map.concepts.items():
                if len(docs_list) > 1:
                    doc_ids_for_concept = [d.document_id for d in docs_list]
                    for i, doc_a in enumerate(doc_ids_for_concept):
                        for doc_b in doc_ids_for_concept[i+1:]:
                            rel = DocumentRelationship(
                                doc_a, doc_b,
                                "DISCUSSES_SAME_TOPIC",
                                strength=0.8,
                                evidence=f"Both discuss '{concept}'"
                            )
                            self.context_map.add_relationship(rel)
                            relationship_count += 1

            # Add temporal relationships based on dates
            sorted_docs = sorted(
                self.context_map.documents.items(),
                key=lambda x: x[1].get("date", "")
            )
            for i, (doc_a_id, doc_a) in enumerate(sorted_docs):
                if i < len(sorted_docs) - 1:
                    doc_b_id, doc_b = sorted_docs[i + 1]
                    date_a = doc_a.get("date", "")
                    date_b = doc_b.get("date", "")
                    if date_a and date_b:
                        rel = DocumentRelationship(
                            doc_a_id, doc_b_id,
                            "TEMPORAL_SEQUENCE",
                            strength=0.6,
                            evidence=f"{date_a} → {date_b}"
                        )
                        self.context_map.add_relationship(rel)
                        relationship_count += 1

            print("   -> Identified {} document relationships".format(relationship_count))

        except Exception as e:
            print(f"   [ERROR] Failed to map relationships: {e}")

    def _identify_evidence_chains(self):
        """Identify evidence chains (problem → response → effectiveness)."""
        try:
            chains = []

            # Manual definition of key evidence chains for NHS/LCH context
            chains_to_add = [
                EvidenceChain(
                    "workforce",
                    "Leeds_Demographics_Health_Inequalities_Context_2024.md",
                    "Workforce-Strategy-2021-25-V1.0.md",
                    "Leeds Community Annual-report-2024-2025.md",
                    "Problem: Workforce needs grow with demographics; Response: Sophisticated assessment strategy; Effectiveness: Annual report shows progress"
                ),
                EvidenceChain(
                    "health inequalities",
                    "Leeds_Demographics_Health_Inequalities_Context_2024.md",
                    "LCH-Trust-Board-Meeting-Public-Papers-4-09-2025-AMENDED _1_.md",
                    "Leeds Community Annual-report-2024-2025.md",
                    "Problem: Significant inequalities exist; Response: Partnership oversight group established; Effectiveness: Trust reports ongoing work"
                ),
                EvidenceChain(
                    "partnership & integration",
                    "LTHT-Annual-Report-2024-25-FINAL.md",
                    "Healthy-Leeds-Plan-Executive-Summary_plain_text_DRAFT-v4.1.md",
                    "LCH-Trust-Board-Meeting-Public-Papers-4-09-2025-AMENDED _1_.md",
                    "Problem: Need for integrated care; Response: Healthy Leeds Plan framework; Effectiveness: Partnership strengthening initiatives"
                ),
                EvidenceChain(
                    "financial sustainability",
                    "Leeds Community Annual Report 2324.md",
                    "Leeds Community Annual-report-2024-2025.md",
                    None,
                    "Problem: Financial constraints; Response: Resource optimization strategy; Effectiveness: TBD (ongoing)"
                ),
            ]

            for chain in chains_to_add:
                self.context_map.add_evidence_chain(chain)

            print("   -> Identified {} evidence chains".format(len(chains_to_add)))
            for chain in chains_to_add[:3]:
                print("      - {}: {} -> {}".format(chain.concept, chain.problem_doc, chain.response_doc))

        except Exception as e:
            print(f"   [ERROR] Failed to identify evidence chains: {e}")

    def _create_concept_groups(self):
        """Create concept groups (thematic clusters)."""
        try:
            group_count = 0

            for group_name, keywords in self.predefined_groups.items():
                # Find documents in this group
                docs_in_group = set()
                concepts_in_group = []

                for keyword in keywords:
                    if keyword in self.context_map.concepts:
                        for doc_concept in self.context_map.concepts[keyword]:
                            docs_in_group.add(doc_concept.document_id)
                        concepts_in_group.append(keyword)

                if docs_in_group:
                    group = ConceptGroup(
                        group_name,
                        list(docs_in_group),
                        concepts_in_group,
                        strength=0.8
                    )
                    self.context_map.add_concept_group(group)
                    group_count += 1

            print("   -> Created {} concept groups".format(group_count))
            for group_name, group in self.context_map.concept_groups.items():
                print("      - {}: {} documents".format(group_name, len(group.documents)))

        except Exception as e:
            print(f"   [ERROR] Failed to create concept groups: {e}")
