#!/usr/bin/env python3
"""
query_graph.py

Query the improved knowledge graph.
Simple analysis and visualization of the graph data.
"""

import json
import sys
from typing import List, Dict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

import networkx as nx

# Load improved graph
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
print("KNOWLEDGE GRAPH ANALYSIS - Improved Version")
print("="*80)

# Summary
print("\n[SUMMARY]")
stats = data.get("statistics", {})
for key, value in stats.items():
    print(f"  {key}: {value}")

# Entities
print("\n[ENTITIES] By Type:")
for entity_type, entities in data.get("entities", {}).items():
    print(f"  {entity_type:20} {len(entities):3}")
    if entities:
        print(f"    Examples: {', '.join(entities[:3])}")

# Key entities
print("\n[KEY ENTITIES] Most Connected:")
degrees = dict(G.degree())
top_10 = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
for entity, degree in top_10:
    entity_type = G.nodes[entity].get("entity_type", "?")
    print(f"  {entity:35} {degree:3} connections [{entity_type}]")

# By entity type
print("\n[SERVICES PROVIDED]:")
for rel in data.get("relationships", []):
    if rel.get("relationship") == "provides":
        print(f"  {rel.get('source')} → {rel.get('target')}")

print("\n[PATHWAYS]:")
for entity in data.get("entities", {}).get("PATHWAYS", []):
    print(f"  • {entity}")

print("\n[ROLES/WORKFORCE]:")
for entity in sorted(data.get("entities", {}).get("ROLES", []))[:10]:
    print(f"  • {entity}")

print("\n[HEALTH CONDITIONS]:")
for entity in data.get("entities", {}).get("CONDITIONS", []):
    print(f"  • {entity}")

# Relationship summary
print("\n[RELATIONSHIP TYPES]:")
rel_types = {}
for rel in data.get("relationships", []):
    rel_type = rel.get("relationship", "unknown")
    rel_types[rel_type] = rel_types.get(rel_type, 0) + 1

for rel_type, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {rel_type:30} {count:5}")

print("\n" + "="*80 + "\n")
