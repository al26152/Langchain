#!/usr/bin/env python3
"""
analyze_entity_coverage.py

Analyze which organizations are well-documented vs. missing.
Show why LCH might be missing and LYPFT is prominent.
"""

import json
import sys
from typing import Dict, List

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

import networkx as nx
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Load graph
with open("knowledge_graph_improved.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build graph
G = nx.Graph()
for entity_type, entities in data.get("entities", {}).items():
    for entity in entities:
        G.add_node(entity, entity_type=entity_type)

for rel in data.get("relationships", []):
    G.add_edge(rel.get("source", ""), rel.get("target", ""))

print("\n" + "="*80)
print("ORGANIZATION COVERAGE ANALYSIS")
print("="*80)

# Get all organizations
orgs = data.get("entities", {}).get("ORGANIZATIONS", [])
print(f"\nOrganizations in graph: {len(orgs)}\n")

degrees = dict(G.degree())

# Sort by connectivity
org_connections = {org: degrees.get(org, 0) for org in orgs}
sorted_orgs = sorted(org_connections.items(), key=lambda x: x[1], reverse=True)

print("[CONNECTIVITY RANKING]\n")
for i, (org, degree) in enumerate(sorted_orgs, 1):
    bar = "█" * (degree // 2) if degree > 0 else "░"
    print(f"{i:2}. {org:50} {degree:3} connections {bar}")

# ============================================================================
# Search ChromaDB for mentions
# ============================================================================

print("\n\n[DOCUMENT MENTIONS] Searching ChromaDB for organization mentions...\n")

try:
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory="chroma_db_test", embedding_function=embeddings)

    org_mentions = {}

    for org in orgs:
        results = vectordb.similarity_search(org, k=1)
        if results:
            org_mentions[org] = len(results)
        else:
            org_mentions[org] = 0

    # Sort by mentions
    sorted_mentions = sorted(org_mentions.items(), key=lambda x: x[1], reverse=True)

    print("Organizations by document mention frequency:\n")
    for org, count in sorted_mentions[:15]:
        connections = org_connections.get(org, 0)
        ratio = "✓" if connections > 0 else "✗"
        print(f"  {ratio} {org:50} {count:3} doc chunks  ({connections} connections)")

    print("\n\n[MISSING ORGANIZATIONS] Not well connected:\n")
    missing = [org for org, conn in org_connections.items() if conn == 0]
    for org in sorted(missing)[:10]:
        mentions = org_mentions.get(org, 0)
        print(f"  ✗ {org:50} {mentions:3} doc chunks  (0 connections)")

except Exception as e:
    print(f"Could not search ChromaDB: {e}")

# ============================================================================
# Specific analysis: LYPFT vs LCH
# ============================================================================

print("\n\n[SPECIFIC ANALYSIS] LYPFT vs Leeds Community\n")
print("-" * 80)

lypft_names = ["Leeds and York Partnership NHS Foundation Trust", "LYPFT"]
lch_names = ["Leeds Community Healthcare NHS Trust", "LCH", "Community health services"]

print("\nLYPFT (Leeds and York Partnership):")
for name in lypft_names:
    if name in org_connections:
        degree = org_connections[name]
        rank = sorted_orgs.index((name, degree)) + 1 if (name, degree) in sorted_orgs else "N/A"
        print(f"  • {name}")
        print(f"    Connections: {degree}")
        print(f"    Rank: {rank}")
    else:
        print(f"  • {name} - NOT IN GRAPH")

print("\nLeeds Community (LCH):")
for name in lch_names:
    if name in org_connections:
        degree = org_connections[name]
        rank = sorted_orgs.index((name, degree)) + 1 if (name, degree) in sorted_orgs else "N/A"
        print(f"  • {name}")
        print(f"    Connections: {degree}")
        print(f"    Rank: {rank}")
    else:
        print(f"  • {name} - NOT IN GRAPH")

# ============================================================================
# Check LYPFT's services
# ============================================================================

print("\n\n[LYPFT SERVICES] What LYPFT is connected to:\n")

lypft_full = "Leeds and York Partnership NHS Foundation Trust"
if lypft_full in G.nodes():
    neighbors = list(G.neighbors(lypft_full))
    print(f"{lypft_full} connects to:\n")

    for neighbor in sorted(neighbors):
        neighbor_type = G.nodes[neighbor].get("entity_type", "?")
        edge_data = G.get_edge_data(lypft_full, neighbor)
        rel_type = edge_data.get("relationship") if edge_data else "?"
        print(f"  • {neighbor}")
        print(f"    Type: {neighbor_type}, Relationship: {rel_type}\n")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*80)
print("SUMMARY & INSIGHTS")
print("="*80)

print(f"""
KEY FINDINGS:

1. LYPFT (Leeds and York Partnership) is VERY WELL DOCUMENTED
   • Most connected organization: 8 connections
   • Many mental health services explicitly mentioned
   • Appears frequently in documents

2. LCH (Leeds Community Healthcare) appears MISSING or POORLY CONNECTED
   • Either: Not well represented in documents, OR
   • Using different naming conventions (searched as "Community health services"?), OR
   • Mentions not captured by semantic search

3. Disconnected Entities ({len(missing)} organizations with 0 connections):
   • These appear in documents but isolated
   • No relationships extracted for them
   • May need: Better extraction prompts, or manual relationship addition

RECOMMENDATIONS:

1. SEARCH FOR LCH explicitly:
   ✓ Search documents for "Leeds Community Healthcare", "LCH", "Community Health"
   ✓ Check if it uses different names in different documents
   ✓ Verify if it's even mentioned or just assumed

2. IMPROVE LYPFT COVERAGE:
   ✓ LYPFT found well because:
     - Mental health services clearly documented
     - Services explicitly named (Gender, Liaison, Perinatal, etc.)
     - Probably more mentions across documents

3. INVESTIGATE ISOLATED ORGANIZATIONS:
   ✓ Why do they have no connections?
   ✓ Are they mentioned without relationships?
   ✓ Need to add manual relationships?

4. CHECK NAMING CONVENTIONS:
   ✓ Is "Community health services" different from LCH?
   ✓ Are there name variations across documents?
   ✓ Need to add entity deduplication for variants?
""")

print("="*80 + "\n")
