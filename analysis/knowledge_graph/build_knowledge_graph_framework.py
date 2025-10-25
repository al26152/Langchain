#!/usr/bin/env python3
"""
build_knowledge_graph_framework.py

FRAMEWORK-BASED Knowledge Graph Extraction

Instead of hardcoding queries for each organization, we use NHS service frameworks
to define what constitutes a "service" and extract universally.

Framework approach:
1. Services are defined by characteristics: Type, Setting, Population, Condition areas
2. Services are provided by Organizations to specific populations
3. Services are connected via Care Pathways
4. Relationships emerge from document context (which org, which population)

This works for ANY organization without special-case handling.
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
# FRAMEWORK DEFINITIONS - Based on NHS Service Standards
# ============================================================================

# NHS service types and characteristics
SERVICE_FRAMEWORK = {
    "service_types": [
        "Primary Care",
        "Secondary Care",
        "Community Health",
        "Mental Health",
        "Dental",
        "Pharmacy",
        "Optical",
        "Diagnostic",
        "Emergency",
        "Planned Care",
        "Rehabilitation",
    ],

    "care_settings": [
        "Hospital",
        "Community",
        "Primary Care",
        "Home",
        "Outpatient",
        "Inpatient",
        "Virtual",
    ],

    "populations": [
        "Adults",
        "Children",
        "Elderly",
        "Pregnant women",
        "Young people",
        "Babies",
        "Learning disabilities",
        "Physical disabilities",
    ],

    "condition_areas": [
        "Mental Health",
        "Cancer",
        "Cardiovascular",
        "Respiratory",
        "Diabetes",
        "Chronic conditions",
        "Acute conditions",
        "Maternity",
        "Neonatal",
        "Pediatric",
        "Dental",
        "Orthopedic",
        "Neurology",
        "Trauma",
    ],

    "service_characteristics": [
        "Diagnosis",
        "Treatment",
        "Prevention",
        "Screening",
        "Management",
        "Rehabilitation",
        "Palliative care",
        "Therapy",
        "Education",
        "Support",
    ]
}

# ============================================================================
# FRAMEWORK-BASED ENTITY QUERIES - Universally applicable
# ============================================================================

FRAMEWORK_QUERIES = {
    "ORGANIZATIONS": [
        # General organization queries - works for any org
        "NHS Trust hospital provider",
        "healthcare organization services",
        "health service provider",
        "care provider commission services",
        "NHS foundation trust",
        "integrated care board",
        "GP practice primary care",
    ],

    "SERVICES": [
        # Framework-based queries - define services by their characteristics
        # Service types + settings
        "primary care secondary care services",
        "community health services",
        "hospital services departments",
        "outpatient inpatient services",
        "emergency department urgent care",
        "planned elective care surgery",
        "diagnostic imaging laboratory",
        "mental health services",
        "dental services",
        "rehabilitation therapy",

        # Service types + populations
        "children's services pediatric",
        "adult services elderly care",
        "maternity neonatal services",
        "young people services adolescent",

        # Service types + conditions
        "cancer services oncology",
        "cardiovascular heart services",
        "respiratory lung disease",
        "diabetes endocrine services",
        "mental health psychiatry",
        "orthopedic surgery",
        "neurology neurological",
        "trauma injury",

        # Service characteristics
        "diagnostic screening assessment",
        "treatment surgery therapy",
        "rehabilitation recovery",
        "palliative end of life care",
        "prevention health promotion",
    ],

    "PATHWAYS": [
        "care pathway patient journey",
        "referral pathway urgent community hospital",
        "discharge pathway step-down",
        "integrated care pathway",
        "clinical pathway protocol",
        "service pathway commissioning",
    ],

    "ROLES": [
        "clinical staff positions doctors nurses",
        "allied health professionals therapists",
        "management leadership roles",
        "administrative support roles",
    ],

    "CONDITIONS": [
        "health conditions diseases",
        "chronic long-term conditions",
        "acute conditions urgent",
        "mental health conditions",
        "physical health conditions",
        "vulnerable populations",
    ],
}

EXTRACTION_PROMPT = """You are a healthcare knowledge extraction system using NHS service frameworks.

Extract entities and relationships based on NHS service standards and frameworks.

FRAMEWORK-BASED EXTRACTION RULES:

1. SERVICES are identified by their characteristics:
   - Type: Primary Care, Secondary Care, Community Health, Mental Health, Dental, etc.
   - Setting: Hospital, Community, Home, Outpatient, Virtual, etc.
   - Population: Adults, Children, Elderly, Pregnant women, etc.
   - Condition areas: Cancer, Cardiovascular, Mental Health, Diabetes, etc.
   - Characteristics: Diagnosis, Treatment, Therapy, Rehabilitation, Screening, etc.

   Extract service names, and include type/population if mentioned.

2. ORGANIZATIONS are healthcare providers:
   - NHS Trusts, Foundation Trusts, GP Practices, Integrated Care Boards, etc.
   - Include full official names

3. PATHWAYS connect organizations and services:
   - Care pathways (patient journeys through services)
   - Referral pathways (between organizations)
   - Discharge pathways
   - Service integration pathways

4. RELATIONSHIPS - Create "provides" relationships when:
   - Text states organization provides service (explicit)
   - Service is listed in organization's service sections/catalogs
   - Service appears in organization's documents with organization context

5. USE DOCUMENT CONTEXT:
   - Document source tells you which organization owns/provides services
   - Services listed in that org's document = that org provides them
   - Look for pathways that connect multiple organizations

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
    {{"source": "Org1", "target": "Pathway1", "relationship": "uses"}},
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
print("KNOWLEDGE GRAPH EXTRACTION - FRAMEWORK-BASED APPROACH")
print("="*80)

print(f"""
This approach uses NHS service frameworks instead of organization-specific queries.

FRAMEWORK ELEMENTS:
  Service Types: {len(SERVICE_FRAMEWORK['service_types'])}
  Care Settings: {len(SERVICE_FRAMEWORK['care_settings'])}
  Populations: {len(SERVICE_FRAMEWORK['populations'])}
  Condition Areas: {len(SERVICE_FRAMEWORK['condition_areas'])}
  Service Characteristics: {len(SERVICE_FRAMEWORK['service_characteristics'])}

EXTRACTION STRATEGY:
  1. Use framework-based queries to find services by characteristics
  2. Extract organizations and their relationships to services
  3. Identify pathways that connect organizations
  4. Use document context (metadata) to attribute services to organizations
  5. Works for ANY organization without special-case handling

ADVANTAGES:
  ✓ Scalable - works for new organizations automatically
  ✓ Standards-based - follows NHS frameworks
  ✓ Comprehensive - captures all service types
  ✓ Maintainable - no hardcoding per organization
""")

# Load ChromaDB
print("\n[STEP 1] Loading ChromaDB...")
try:
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory="chroma_db_test", embedding_function=embeddings)
    print(f"[OK] ChromaDB loaded")
except Exception as e:
    print(f"[ERROR] Could not load ChromaDB: {e}")
    sys.exit(1)

# Extract using framework-based queries
print("\n[STEP 2] Semantic search using framework-based queries...")

all_extractions = {
    "ORGANIZATIONS": [],
    "SERVICES": [],
    "PATHWAYS": [],
    "ROLES": [],
    "CONDITIONS": [],
}

all_relationships = []
doc_mentions = {}

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

for entity_type, queries in FRAMEWORK_QUERIES.items():
    print(f"\n  {entity_type}:")

    for query in queries:
        try:
            # Search ChromaDB semantically
            results = vectordb.similarity_search(query, k=10)

            if not results:
                continue

            # Combine relevant chunks with metadata context
            chunks_with_context = []
            document_sources = set()
            for doc in results[:5]:
                source = doc.metadata.get('source', 'unknown')
                document_sources.add(source)
                chunks_with_context.append(f"[From: {source}]\n{doc.page_content}")

            context = "\n\n".join(chunks_with_context)
            document_hint = f"\nDocument sources in this context: {', '.join(document_sources)}"
            contextual_prompt = EXTRACTION_PROMPT.format(text=context + document_hint)

            # Extract entities and relationships
            response = llm.invoke(contextual_prompt)

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

# Deduplicate
print("\n[STEP 3] Deduplicating entities...")

def deduplicate_list_smart(items: List[str], threshold: float = 0.85) -> List[str]:
    """Remove duplicate strings with fuzzy matching."""
    if not items:
        return []

    unique = []
    for item in sorted(set(items)):
        found_dup = False
        for i, existing in enumerate(unique):
            similarity = SequenceMatcher(None, item.lower(), existing.lower()).ratio()
            if similarity >= threshold:
                if len(item) > len(existing):
                    unique[i] = item
                found_dup = True
                break

        if not found_dup:
            unique.append(item)

    return unique

cleaned_entities = {}
for entity_type, entities in all_extractions.items():
    cleaned_entities[entity_type] = deduplicate_list_smart(entities)
    removed = len(entities) - len(cleaned_entities[entity_type])
    if removed > 0:
        print(f"  {entity_type}: {len(cleaned_entities[entity_type])} unique (removed {removed} duplicates)")

# Find implicit relationships from co-occurrence
print("\n[STEP 4] Finding implicit relationships from co-occurrence...")

implicit_rels = []
all_entities_list = []
for entities in cleaned_entities.values():
    all_entities_list.extend(entities)

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
all_relationships.extend(implicit_rels)

# Remove isolated entities
print("\n[STEP 5] Removing isolated entities...")

connected = set()
for rel in all_relationships:
    connected.add(rel.get("source", ""))
    connected.add(rel.get("target", ""))

final_entities = {}
for entity_type, entities in cleaned_entities.items():
    final_entities[entity_type] = [e for e in entities if e in connected]
    removed = len(cleaned_entities[entity_type]) - len(final_entities[entity_type])
    if removed > 0:
        print(f"  {entity_type}: Removed {removed} isolated entities")

# Save
print("\n[STEP 6] Saving knowledge graph...")

output_data = {
    "entities": final_entities,
    "relationships": all_relationships,
    "statistics": {
        "total_entities": sum(len(v) for v in final_entities.values()),
        "total_relationships": len(all_relationships),
        "extraction_method": "Framework-Based (NHS Service Standards)",
        "implicit_relationships": len(implicit_rels),
    },
    "framework": {
        "service_types": SERVICE_FRAMEWORK["service_types"],
        "care_settings": SERVICE_FRAMEWORK["care_settings"],
        "populations": SERVICE_FRAMEWORK["populations"],
    }
}

with open("knowledge_graph_improved.json", 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("[OK] Saved to knowledge_graph_improved.json")

# Summary
print("\n" + "="*80)
print("EXTRACTION COMPLETE")
print("="*80)

print(f"\nEntities by type:")
for entity_type, entities in final_entities.items():
    print(f"  {entity_type:20} {len(entities):3}")

print(f"\nRelationships: {len(all_relationships)}")
print(f"  Explicit: {len(all_relationships) - len(implicit_rels)}")
print(f"  Implicit (co-occurrence): {len(implicit_rels)}")

print("\n" + "="*80)
print("✓ Framework-based extraction ready for all organizations!")
print("="*80 + "\n")
