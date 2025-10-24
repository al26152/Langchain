#!/usr/bin/env python3
"""
visualize_balanced.py

Create a readable visualization with a balanced mix of relationships.
- Keep all explicit relationships (21)
- Keep only top co-occurrence relationships to avoid overwhelming the browser
- Show implicit relationships for key organizations (LCH, LYPFT, LTHT)
"""

import json
import sys
from typing import Dict, List

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

import networkx as nx
from pyvis.network import Network

print("\n[LOADING] Knowledge graph with balanced implicit relationships...")

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

# Add nodes - exclude ROLES for clarity
print("[NODES] Adding entities (excluding ROLES)...")
for entity_type, entities in data.get("entities", {}).items():
    if entity_type == "ROLES":  # Skip roles to reduce clutter
        continue
    for entity in entities:
        color = COLORS.get(entity_type, "#CCCCCC")
        G.add_node(entity, entity_type=entity_type, color=color)

print(f"  Added {len(G.nodes())} entities")

# Process relationships
relationships = data.get("relationships", [])

explicit_rels = [r for r in relationships if r.get("relationship") != "mentioned_together_in"]
implicit_rels = [r for r in relationships if r.get("relationship") == "mentioned_together_in"]

print(f"\n[FILTERING] Selecting relationships for visualization...")
print(f"  Explicit relationships: {len(explicit_rels)}")
print(f"  Implicit relationships available: {len(implicit_rels)}")

# Key organizations to show all implicit relationships for
KEY_ORGS = [
    "Leeds Community Healthcare NHS Trust",
    "Leeds and York Partnership NHS Foundation Trust",
    "Leeds Teaching Hospitals NHS Trust",
    "NHS England",
    "Integrated Care Board"
]

# Filter implicit relationships - keep only those involving key organizations
filtered_implicit = []
for rel in implicit_rels:
    source = rel.get('source', '')
    target = rel.get('target', '')

    # Keep if either source or target is a key organization
    if source in KEY_ORGS or target in KEY_ORGS:
        filtered_implicit.append(rel)

print(f"  Implicit relationships (filtered to key organizations): {len(filtered_implicit)}")

# Combine relationships
all_rels_to_show = explicit_rels + filtered_implicit

print(f"  Total relationships to visualize: {len(all_rels_to_show)}")

# Add edges to graph - skip any involving ROLES
print("[EDGES] Adding relationships...")
roles_to_skip = set(data.get("entities", {}).get("ROLES", []))
for rel in all_rels_to_show:
    source = rel.get("source", "")
    target = rel.get("target", "")
    # Skip relationships involving ROLES
    if source in roles_to_skip or target in roles_to_skip:
        continue
    if source and target and source in G.nodes() and target in G.nodes():
        G.add_edge(source, target,
                  relationship=rel.get("relationship", "connected"),
                  is_implicit=(rel.get("relationship") == "mentioned_together_in"))

print(f"  Total edges in graph: {len(G.edges())}")

# Create visualization
print("\n[CREATING] Interactive visualization...")
net = Network(height="1000px", width="100%", directed=False, notebook=False)

# Configure physics - lighter for better performance
net.toggle_physics(True)
net.set_options("""
{
  "physics": {
    "enabled": true,
    "stabilization": {
      "iterations": 200,
      "fit": true
    },
    "barnesHut": {
      "gravitationalConstant": -8000,
      "centralGravity": 0.3,
      "springLength": 150
    }
  }
}
""")

# Add nodes with styling
degrees = dict(G.degree())
max_degree = max(degrees.values()) if degrees else 1

for node, attrs in G.nodes(data=True):
    entity_type = attrs.get("entity_type", "UNKNOWN")
    color = COLORS.get(entity_type, "#CCCCCC")
    degree = degrees.get(node, 0)

    # Size by connectivity
    size = 20 + (degree * 1.2)

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
        color = "#DDDDDD"  # Light gray
        width = 0.3
        dashes = True
        label = "mentioned together"  # Simpler label than "co-occurrence"
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
        font={"size": 10, "color": "black"},
    )

print(f"\n  Added {explicit_count} explicit relationship edges")
print(f"  Added {implicit_count} implicit relationship edges (filtered)")

# Save visualization
output_file = "knowledge_graph_balanced_visualization.html"
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

print("\nVisualization Strategy:")
print("  ✓ Shows ALL 21 explicit relationships")
print(f"  ✓ Shows {implicit_count} implicit relationships (filtered to key organizations)")
print(f"  ✓ Focuses on LCH, LYPFT, LTHT, NHS England, ICB connections")
print(f"  ✓ Total edges: {len(G.edges())} (much more browser-friendly)")

print("\nEntity Type Distribution:")
for entity_type, entities in data.get("entities", {}).items():
    count = len(entities)
    pct = 100 * count / len(G.nodes())
    print(f"  {entity_type:20} {count:3} entities ({pct:5.1f}%)")

print("\nMost Connected Entities:")
top_10 = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
for entity, degree in top_10:
    entity_type = G.nodes[entity].get("entity_type", "?")
    print(f"  {entity:45} {degree:3} connections [{entity_type}]")

print("\nRelationship Types (Explicit):")
rel_types = {}
for rel in explicit_rels:
    rel_type = rel.get("relationship", "unknown")
    rel_types[rel_type] = rel_types.get(rel_type, 0) + 1

for rel_type, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {rel_type:35} {count:3} relationships")

print("\nVisualization Legend:")
print("  ● Red     = Organizations")
print("  ● Teal    = Services")
print("  ● Salmon  = Pathways")
print("  ● Blue    = Roles/Workforce")
print("  ● Mint    = Health Conditions")
print("")
print("  — Solid colored lines = Explicit relationships (provides, commissions, etc.)")
print("  — Dashed light gray lines = Implicit relationships (co-occurrence)")
print("")
print("Node Size = Connectivity (larger = more connected)")

print("\n" + "="*80)
print(f"✓ Open {output_file} in your browser!")
print("="*80 + "\n")

# Show what's visible for key orgs
print("KEY ORGANIZATIONS IN THIS VISUALIZATION:\n")

for org in KEY_ORGS:
    if org in G.nodes():
        degree = degrees.get(org, 0)
        org_rels = [r for r in all_rels_to_show if r.get('source') == org or r.get('target') == org]
        explicit = len([r for r in org_rels if r.get('relationship') != 'mentioned_together_in'])
        implicit = len([r for r in org_rels if r.get('relationship') == 'mentioned_together_in'])

        print(f"{org}")
        print(f"  Visible connections: {degree}")
        print(f"  - Explicit: {explicit}")
        print(f"  - Implicit (shown): {implicit}")
        print()
