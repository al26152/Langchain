#!/usr/bin/env python3
"""
visualize_improved_graph.py

Create interactive HTML visualization of the improved knowledge graph.
Shows all 98 entities and 4,265 relationships with color coding and clustering.
"""

import json
import sys
from typing import Dict, List

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

import networkx as nx
from pyvis.network import Network

print("\n[LOADING] Improved knowledge graph visualization...")

# Load improved graph
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

# Add edges (sample relationships to avoid clutter)
print("[EDGES] Adding relationships...")
relationships = data.get("relationships", [])

# Filter to show only explicit relationships (not all co-occurrences)
filtered_rels = [
    r for r in relationships
    if r.get("relationship") != "mentioned_together_in"
]

print(f"  Explicit relationships: {len(filtered_rels)}")
print(f"  Co-occurrence relationships: {len(relationships) - len(filtered_rels)} (hidden for clarity)")

for rel in filtered_rels:
    source = rel.get("source", "")
    target = rel.get("target", "")
    if source and target:
        G.add_edge(source, target, relationship=rel.get("relationship", "connected"))

print(f"  Total edges in visualization: {len(G.edges())}")

# Create visualization
print("\n[CREATING] Interactive visualization...")
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
    size = 15 + (degree * 2)

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
for source, target, attrs in G.edges(data=True):
    rel_type = attrs.get("relationship", "connected")

    # Color by relationship type
    rel_colors = {
        "provides": "#64B5F6",        # Light Blue
        "partners_with": "#81C784",   # Green
        "commissions": "#FFB74D",     # Orange
        "commissioned_to_carry_out": "#AB47BC",  # Purple
        "improves": "#EF5350",        # Red
    }

    color = rel_colors.get(rel_type, "#999999")

    net.add_edge(
        source,
        target,
        title=rel_type,
        label=rel_type,
        color=color,
        width=2,
        font={"size": 11, "color": "black"},
    )

# Save visualization
output_file = "knowledge_graph_improved_visualization.html"
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

print("\nMost Connected Entities (Hubs):")
top_10 = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
for entity, degree in top_10:
    entity_type = G.nodes[entity].get("entity_type", "?")
    print(f"  {entity:40} {degree:3} connections [{entity_type}]")

print("\nRelationship Types (Explicit Only):")
rel_types = {}
for rel in filtered_rels:
    rel_type = rel.get("relationship", "unknown")
    rel_types[rel_type] = rel_types.get(rel_type, 0) + 1

for rel_type, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {rel_type:30} {count:3} relationships")

print("\nGraph Metrics:")
print(f"  Nodes: {len(G.nodes())}")
print(f"  Edges (shown): {len(G.edges())}")
print(f"  Density: {nx.density(G):.4f}")
print(f"  Connected Components: {nx.number_connected_components(G)}")

if nx.is_connected(G):
    print(f"  Graph is fully connected (single component)")
    avg_path = nx.average_shortest_path_length(G)
    print(f"  Average shortest path: {avg_path:.2f}")
    diameter = nx.diameter(G)
    print(f"  Diameter: {diameter}")

print("\nVisualization Legend:")
print("  ● Red     = Organizations")
print("  ● Teal    = Services")
print("  ● Salmon  = Pathways")
print("  ● Blue    = Roles/Workforce")
print("  ● Mint    = Health Conditions")
print("")
print("  — Light Blue = 'provides' relationship")
print("  — Green      = 'partners_with' relationship")
print("  — Orange     = 'commissions' relationship")
print("")
print("Node Size = Connectivity (larger = more connected)")

print("\n" + "="*80)
print(f"✓ Open {output_file} in your browser to explore interactively!")
print("="*80 + "\n")

# Key insights
print("KEY INSIGHTS FROM VISUALIZATION:\n")

# Find most important orgs
org_entities = data.get("entities", {}).get("ORGANIZATIONS", [])
org_degrees = {e: degrees.get(e, 0) for e in org_entities if e in degrees}
top_orgs = sorted(org_degrees.items(), key=lambda x: x[1], reverse=True)[:5]

print("Top Organizations (by connectivity):")
for org, degree in top_orgs:
    print(f"  • {org} ({degree} connections)")

# Find most important services
service_entities = data.get("entities", {}).get("SERVICES", [])
service_degrees = {e: degrees.get(e, 0) for e in service_entities if e in degrees}
top_services = sorted(service_degrees.items(), key=lambda x: x[1], reverse=True)[:5]

print("\nTop Services (by connectivity):")
for service, degree in top_services:
    print(f"  • {service} ({degree} connections)")

# Show pathways
print("\nCare Pathways Identified:")
pathways = data.get("entities", {}).get("PATHWAYS", [])
for pathway in sorted(pathways)[:8]:
    print(f"  • {pathway}")

# Show key roles
print("\nKey Workforce Roles:")
roles = sorted(data.get("entities", {}).get("ROLES", []))[:8]
for role in roles:
    print(f"  • {role}")

print("\n" + "="*80 + "\n")
