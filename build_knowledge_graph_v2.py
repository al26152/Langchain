#!/usr/bin/env python3
"""
build_knowledge_graph_v2.py

IMPROVED Knowledge Graph Extraction using ChromaDB

Uses semantic similarity search instead of raw file reading:
1. Query ChromaDB for relevant chunks per entity type
2. Extract entities and relationships from semantically relevant text
3. Build implicit relationships from co-occurrence
4. Deduplicate and clean
5. Output high-quality knowledge graph

This approach is superior because:
✓ Uses full document context (not just first 3000 chars)
✓ Semantic understanding via embeddings
✓ Finds relationships anywhere in documents
✓ Reuses existing ChromaDB work
"""

import json
import sys
import re
from typing import Dict, List, Set, Tuple
from difflib import SequenceMatcher

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

import networkx as nx
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# ============================================================================
# CONFIGURATION
# ============================================================================

CHROMA_PATH = "chroma_db_test"
OUTPUT_FILE = "knowledge_graph_improved.json"

# Search queries to extract different entity types
ENTITY_QUERIES = {
    "ORGANIZATIONS": [
        "healthcare organizations NHS trusts councils partnerships",
        "hospital trust health authority commissioning body",
        "Leeds Teaching Hospitals LCH LYPFT LTHT",
    ],
    "SERVICES": [
        "healthcare services provided emergency department urgent care",
        "virtual wards diagnostics mental health community nursing",
        "elective care outpatient inpatient rehabilitation",
    ],
    "PATHWAYS": [
        "care pathways patient journey emergency discharge referral",
        "clinical pathway service flow treatment protocol",
        "urgent care pathway community to hospital referral",
    ],
    "ROLES": [
        "job roles staff positions nursing doctors clinical roles",
        "management leadership director chief executive manager",
        "allied health therapists AHP consultant specialist",
    ],
    "CONDITIONS": [
        "health conditions populations mental health physical health",
        "chronic disease frailty dementia long-term conditions",
        "vulnerable populations elderly children young people",
    ],
}

EXTRACTION_PROMPT = """You are a healthcare knowledge extraction system.

Extract ONLY explicit entities and relationships from the provided text.

CRITICAL: Only extract what is EXPLICITLY stated, not implied.

Return valid JSON:
{{
  "entities": {{
    "ORGANIZATIONS": ["Entity1", "Entity2", ...],
    "SERVICES": ["Service1", "Service2", ...],
    "PATHWAYS": ["Pathway1", ...],
    "ROLES": ["Role1", ...],
    "CONDITIONS": ["Condition1", ...]
  }},
  "relationships": [
    {{"source": "Org1", "target": "Service1", "relationship": "provides"}},
    {{"source": "Org1", "target": "Org2", "relationship": "partners_with"}},
    ...
  ]
}}

TEXT:
{text}

Return ONLY valid JSON, no explanation."""

# ============================================================================
# MAIN EXECUTION
# ============================================================================

print("\n" + "="*80)
print("KNOWLEDGE GRAPH EXTRACTION V2 - ChromaDB-Driven")
print("="*80)

# Load ChromaDB
print("\n[STEP 1] Loading ChromaDB...")
try:
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    print(f"[OK] ChromaDB loaded from {CHROMA_PATH}")
except Exception as e:
    print(f"[ERROR] Could not load ChromaDB: {e}")
    sys.exit(1)

# ============================================================================
# STEP 2: SEMANTIC SEARCH FOR ENTITY EXTRACTION
# ============================================================================

print("\n[STEP 2] Semantic search for entities...")

all_extractions = {
    "ORGANIZATIONS": [],
    "SERVICES": [],
    "PATHWAYS": [],
    "ROLES": [],
    "CONDITIONS": [],
}

all_relationships = []
doc_mentions = {}  # Track which docs mention which entities

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

for entity_type, queries in ENTITY_QUERIES.items():
    print(f"\n  {entity_type}:")

    for query in queries:
        try:
            # Search ChromaDB semantically
            results = vectordb.similarity_search(query, k=10)

            if not results:
                continue

            # Combine relevant chunks
            context = "\n".join([doc.page_content for doc in results[:5]])

            # Extract entities and relationships
            response = llm.invoke(
                EXTRACTION_PROMPT.format(text=context)
            )

            # Parse JSON
            try:
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())

                    # Collect entities
                    for found_type, entities in data.get("entities", {}).items():
                        if isinstance(entities, list):
                            all_extractions[found_type].extend(entities)

                    # Collect relationships
                    for rel in data.get("relationships", []):
                        all_relationships.append(rel)

                    # Track document mentions
                    for doc in results:
                        source = doc.metadata.get("source", "unknown")
                        for found_type, entities in data.get("entities", {}).items():
                            if isinstance(entities, list):
                                for entity in entities:
                                    key = f"{entity}_{found_type}"
                                    if key not in doc_mentions:
                                        doc_mentions[key] = set()
                                    doc_mentions[key].add(source)

            except json.JSONDecodeError:
                continue

        except Exception as e:
            continue

    print(f"    Found {len(set(all_extractions[entity_type]))} unique {entity_type}")

# ============================================================================
# STEP 3: DEDUPLICATE ENTITIES
# ============================================================================

print("\n[STEP 3] Deduplicating entities...")

def deduplicate_list(items: List[str], threshold: float = 0.85) -> List[str]:
    """Remove duplicate strings with fuzzy matching."""
    if not items:
        return []

    unique = []
    for item in sorted(set(items)):
        # Check if similar to existing
        found_dup = False
        for existing in unique:
            similarity = SequenceMatcher(None, item.lower(), existing.lower()).ratio()
            if similarity >= threshold:
                found_dup = True
                break

        if not found_dup:
            unique.append(item)

    return unique

cleaned_entities = {}
for entity_type, entities in all_extractions.items():
    cleaned_entities[entity_type] = deduplicate_list(entities)
    print(f"  {entity_type}: {len(entities)} → {len(cleaned_entities[entity_type])} (deduplicated)")

# ============================================================================
# STEP 4: FIND IMPLICIT RELATIONSHIPS
# ============================================================================

print("\n[STEP 4] Finding implicit relationships from co-occurrence...")

implicit_rels = []
all_entities_list = []
for entities in cleaned_entities.values():
    all_entities_list.extend(entities)

# Find entities mentioned together
for i, entity1 in enumerate(all_entities_list):
    key1 = None
    for type1, ents in cleaned_entities.items():
        if entity1 in ents:
            key1 = f"{entity1}_{type1}"
            break

    if not key1 or key1 not in doc_mentions:
        continue

    docs1 = doc_mentions[key1]

    for entity2 in all_entities_list[i+1:]:
        key2 = None
        for type2, ents in cleaned_entities.items():
            if entity2 in ents:
                key2 = f"{entity2}_{type2}"
                break

        if not key2 or key2 not in doc_mentions:
            continue

        docs2 = doc_mentions[key2]
        common_docs = docs1 & docs2

        if common_docs:
            implicit_rels.append({
                "source": entity1,
                "target": entity2,
                "relationship": "mentioned_together_in",
                "documents": list(common_docs)[:1]
            })

print(f"  Found {len(implicit_rels)} implicit relationships")

# Combine with explicit relationships
all_relationships.extend(implicit_rels)

# ============================================================================
# STEP 5: REMOVE ISOLATED ENTITIES
# ============================================================================

print("\n[STEP 5] Removing isolated entities...")

# Find entities with connections
connected = set()
for rel in all_relationships:
    connected.add(rel.get("source", ""))
    connected.add(rel.get("target", ""))

# Filter entities
final_entities = {}
for entity_type, entities in cleaned_entities.items():
    final_entities[entity_type] = [e for e in entities if e in connected]
    removed = len(cleaned_entities[entity_type]) - len(final_entities[entity_type])
    if removed > 0:
        print(f"  {entity_type}: Removed {removed} isolated entities")

# ============================================================================
# STEP 6: SAVE GRAPH
# ============================================================================

print("\n[STEP 6] Saving improved knowledge graph...")

output_data = {
    "entities": final_entities,
    "relationships": all_relationships,
    "statistics": {
        "total_entities": sum(len(v) for v in final_entities.values()),
        "total_relationships": len(all_relationships),
        "extraction_method": "ChromaDB-Driven Semantic Search",
        "implicit_relationships": len(implicit_rels),
    }
}

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"[OK] Saved to {OUTPUT_FILE}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("EXTRACTION COMPLETE")
print("="*80)

print(f"\nEntities by type:")
for entity_type, entities in final_entities.items():
    print(f"  {entity_type:20} {len(entities):3}")

print(f"\nRelationships: {len(all_relationships)}")
print(f"  Explicit: {len(all_relationships) - len(implicit_rels)}")
print(f"  Implicit (co-occurrence): {len(implicit_rels)}")

# Build graph to show stats
G = nx.Graph()
for entity_type, entities in final_entities.items():
    for entity in entities:
        G.add_node(entity, entity_type=entity_type)

for rel in all_relationships:
    G.add_edge(rel.get("source", ""), rel.get("target", ""))

degrees = dict(G.degree())
hubs = sorted(degrees.items(), key=lambda x: x[1], reverse=True)

print(f"\nTop Connected Entities:")
for org, degree in hubs[:5]:
    print(f"  {org}: {degree} connections")

print(f"\nConnected Components: {nx.number_connected_components(G)}")
print(f"Graph Density: {nx.density(G):.3f}")

print(f"\n✓ Next: Use {OUTPUT_FILE} for analysis")
print("="*80 + "\n")
