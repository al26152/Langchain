#!/usr/bin/env python3
"""
visualize_with_implicit_rels.py

Create interactive HTML visualization including IMPLICIT relationships.
Shows both explicit relationships (solid lines) and co-occurrence relationships (lighter lines).
This reveals LCH's 65 co-occurrence connections that are hidden in the standard visualization.
"""

import json
import sys
from typing import Dict, List

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

import networkx as nx
from pyvis.network import Network

print("\n[LOADING] Knowledge graph with implicit relationships...")

# Load graph
with open("knowledge_graph_improved.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build NetworkX graph
G = nx.Graph()

# Color scheme by entity type
COLORS = {
    "ORGANIZATIONS": "#FF6B6B",      # Red
    "SERVICES": "#4ECDC4",            # Teal
    "PATHWAYS": "#FFA07A",            # Salmon
    "ROLES": "#45B7D1",               # Blue
    "CONDITIONS": "#98D8C8",          # Mint
}

# Add nodes
print("[NODES] Adding entities...")
for entity_type, entities in data.get("entities", {}).items():
    for entity in entities:
        color = COLORS.get(entity_type, "#CCCCCC")
        G.add_node(entity, entity_type=entity_type, color=color)

print(f"  Added {len(G.nodes())} entities")

# Add edges - INCLUDING implicit relationships
print("[EDGES] Adding relationships (explicit + implicit)...")
relationships = data.get("relationships", [])

explicit_rels = [r for r in relationships if r.get("relationship") != "mentioned_together_in"]
implicit_rels = [r for r in relationships if r.get("relationship") == "mentioned_together_in"]

print(f"  Explicit relationships: {len(explicit_rels)}")
print(f"  Implicit relationships (co-occurrence): {len(implicit_rels)}")

# Add all relationships to graph
for rel in relationships:
    source = rel.get("source", "")
    target = rel.get("target", "")
    if source and target:
        G.add_edge(source, target,
                  relationship=rel.get("relationship", "connected"),
                  is_implicit=(rel.get("relationship") == "mentioned_together_in"))

print(f"  Total edges in graph: {len(G.edges())}")

# Create visualization
print("\n[CREATING] Interactive visualization with implicit relationships...")
net = Network(height="1000px", width="100%", directed=False, notebook=False)

# Configure physics
net.toggle_physics(True)

# Add nodes with styling
degrees = dict(G.degree())
max_degree = max(degrees.values()) if degrees else 1

for node, attrs in G.nodes(data=True):
    entity_type = attrs.get("entity_type", "UNKNOWN")
    color = COLORS.get(entity_type, "#CCCCCC")
    degree = degrees.get(node, 0)

    # Size by connectivity
    size = 15 + (degree * 1.5)

    # Title with info
    title_text = f"{node}\n({entity_type})\n{degree} connections"

    net.add_node(
        node,
        label=node,
        title=title_text,
        color=color,
        size=size,
        font={"size": 13, "color": "black"},
        borderWidth=2,
    )

# Add edges with styling
explicit_count = 0
implicit_count = 0

for source, target, attrs in G.edges(data=True):
    rel_type = attrs.get("relationship", "connected")
    is_implicit = attrs.get("is_implicit", False)

    if is_implicit:
        implicit_count += 1
        # Implicit relationships: lighter, thinner, dashed
        color = "#CCCCCC"  # Light gray
        width = 0.5
        dashes = True
        label = "co-occurrence"
    else:
        explicit_count += 1
        # Explicit relationships: colored by type
        rel_colors = {
            "provides": "#64B5F6",        # Light Blue
            "partners_with": "#81C784",   # Green
            "commissions": "#FFB74D",     # Orange
            "commissioned to carry out a review of": "#AB47BC",  # Purple
            "improves": "#EF5350",        # Red
            "overseen by": "#FFA726",     # Orange-red
            "earns income from": "#29B6F6",  # Bright blue
            "integrates_with": "#66BB6A",    # Green
            "benchmarking_with": "#AB47BC",  # Purple
            "expands": "#EC407A",         # Pink
        }

        color = rel_colors.get(rel_type, "#999999")
        width = 2
        dashes = False
        label = rel_type

    net.add_edge(
        source,
        target,
        title=label,
        label=label,
        color=color,
        width=width,
        dashes=dashes,
        font={"size": 11, "color": "black"},
    )

print(f"\n  Added {explicit_count} explicit relationship edges")
print(f"  Added {implicit_count} implicit relationship edges")

# Save visualization
output_file = "knowledge_graph_with_implicit_visualization.html"
try:
    net.write_html(output_file)
    print(f"\n[OK] Visualization saved to {output_file}")
except Exception as e:
    print(f"[WARN] Visualization save issue: {e}")
    print(f"       File may still be created: {output_file}")

# ============================================================================
# ANALYSIS SUMMARY
# ============================================================================

print("\n" + "="*80)
print("VISUALIZATION SUMMARY")
print("="*80)

print("\nEntity Type Distribution:")
for entity_type, entities in data.get("entities", {}).items():
    count = len(entities)
    pct = 100 * count / len(G.nodes())
    print(f"  {entity_type:20} {count:3} entities ({pct:5.1f}%)")

print("\nMost Connected Entities (including implicit co-occurrence):")
top_15 = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:15]
for entity, degree in top_15:
    entity_type = G.nodes[entity].get("entity_type", "?")
    print(f"  {entity:45} {degree:3} connections [{entity_type}]")

print("\nRelationship Types (Explicit Only):")
rel_types = {}
for rel in explicit_rels:
    rel_type = rel.get("relationship", "unknown")
    rel_types[rel_type] = rel_types.get(rel_type, 0) + 1

for rel_type, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {rel_type:35} {count:3} relationships")

print("\nGraph Metrics:")
print(f"  Nodes: {len(G.nodes())}")
print(f"  Edges (total): {len(G.edges())}")
print(f"    - Explicit: {explicit_count}")
print(f"    - Implicit (co-occurrence): {implicit_count}")
print(f"  Density: {nx.density(G):.4f}")
print(f"  Connected Components: {nx.number_connected_components(G)}")

if nx.is_connected(G):
    print(f"  Graph is fully connected (single component)")
    try:
        avg_path = nx.average_shortest_path_length(G)
        print(f"  Average shortest path: {avg_path:.2f}")
        diameter = nx.diameter(G)
        print(f"  Diameter: {diameter}")
    except:
        pass

print("\nVisualization Legend:")
print("  ● Red     = Organizations")
print("  ● Teal    = Services")
print("  ● Salmon  = Pathways")
print("  ● Blue    = Roles/Workforce")
print("  ● Mint    = Health Conditions")
print("")
print("  — Solid lines = Explicit relationships (provides, commissions, etc.)")
print("  — Dashed light lines = Implicit relationships (co-occurrence in documents)")
print("")
print("Node Size = Connectivity (larger = more connected)")

print("\n" + "="*80)
print(f"✓ Open {output_file} in your browser to explore interactively!")
print("="*80 + "\n")

# Key insights - check LCH
print("KEY INSIGHTS:\n")

print("Leeds Community Healthcare NHS Trust (LCH):")
if "Leeds Community Healthcare NHS Trust" in G.nodes():
    lch_degree = degrees.get("Leeds Community Healthcare NHS Trust", 0)
    lch_rels = [r for r in relationships if r.get('source') == "Leeds Community Healthcare NHS Trust" or r.get('target') == "Leeds Community Healthcare NHS Trust"]
    explicit_lch = [r for r in lch_rels if r.get('relationship') != 'mentioned_together_in']
    implicit_lch = [r for r in lch_rels if r.get('relationship') == 'mentioned_together_in']

    print(f"  Total connections: {lch_degree}")
    print(f"  - Explicit relationships: {len(explicit_lch)}")
    print(f"  - Implicit relationships: {len(implicit_lch)}")
    print(f"\n  Connected to (sample of 10 implicit co-occurrences):")
    for rel in implicit_lch[:10]:
        other = rel.get('target') if rel.get('source') == "Leeds Community Healthcare NHS Trust" else rel.get('source')
        print(f"    • {other}")

print("\n")
