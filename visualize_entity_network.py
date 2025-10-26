"""
visualize_entity_network.py

Create focused knowledge graph visualizations for specific entities.

Usage:
    python visualize_entity_network.py LTHT LCH
    python visualize_entity_network.py "Leeds Teaching Hospitals NHS Trust"
"""

import json
import sys
from pathlib import Path
from typing import List, Set, Dict


def load_knowledge_graph(path: str = "knowledge_graph_improved.json") -> Dict:
    """Load the knowledge graph from JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_entity(kg: Dict, search_term: str) -> str:
    """Find entity by name or abbreviation."""
    search_lower = search_term.lower()

    # Check for exact abbreviations
    abbrev_map = {
        "ltht": "Leeds Teaching Hospitals NHS Trust",
        "lch": "Leeds Community Healthcare NHS Trust",
        "lypft": "Leeds and York Partnership NHS Foundation Trust",
    }

    if search_lower in abbrev_map:
        return abbrev_map[search_lower]

    # Search all entities
    for entity_type, entities in kg["entities"].items():
        for entity in entities:
            if search_lower in entity.lower():
                return entity

    return search_term  # Return as-is if not found


def get_entity_relationships(kg: Dict, entity_name: str, max_hops: int = 1) -> Dict:
    """
    Get all relationships for an entity up to max_hops away.

    Returns:
        Dict with nodes and edges for visualization
    """
    nodes = set()
    edges = []
    nodes.add(entity_name)

    # Track which entities we've processed at each hop level
    current_level = {entity_name}
    visited = {entity_name}

    for hop in range(max_hops):
        next_level = set()

        for rel in kg["relationships"]:
            source = rel["source"]
            target = rel["target"]
            rel_type = rel["relationship"]

            # Forward relationships
            if source in current_level and target not in visited:
                nodes.add(source)
                nodes.add(target)
                edges.append({
                    "source": source,
                    "target": target,
                    "relationship": rel_type,
                    "direction": "forward",
                    "hop": hop + 1
                })
                next_level.add(target)
                visited.add(target)

            # Backward relationships
            elif target in current_level and source not in visited:
                nodes.add(source)
                nodes.add(target)
                edges.append({
                    "source": source,
                    "target": target,
                    "relationship": rel_type,
                    "direction": "backward",
                    "hop": hop + 1
                })
                next_level.add(source)
                visited.add(source)

        current_level = next_level
        if not current_level:
            break

    return {
        "nodes": list(nodes),
        "edges": edges,
        "center_node": entity_name
    }


def get_entity_type(kg: Dict, entity_name: str) -> str:
    """Get the type of an entity."""
    for entity_type, entities in kg["entities"].items():
        if entity_name in entities:
            return entity_type
    return "UNKNOWN"


def create_html_visualization(graph_data: Dict, kg: Dict, output_path: str = "entity_network.html"):
    """Create an interactive HTML visualization using vis.js."""

    # Get entity types for coloring
    node_data = []
    for node in graph_data["nodes"]:
        entity_type = get_entity_type(kg, node)
        is_center = (node == graph_data["center_node"])

        # Color scheme
        colors = {
            "ORGANIZATIONS": "#e74c3c",  # Red
            "SERVICES": "#3498db",       # Blue
            "PATHWAYS": "#2ecc71",       # Green
            "ROLES": "#f39c12",          # Orange
            "CONDITIONS": "#9b59b6",     # Purple
            "UNKNOWN": "#95a5a6",        # Gray
        }

        node_data.append({
            "id": node,
            "label": node,
            "title": f"{entity_type}: {node}",
            "color": colors.get(entity_type, "#95a5a6"),
            "size": 40 if is_center else 25,
            "font": {"size": 16 if is_center else 12, "bold": is_center}
        })

    # Prepare edges
    edge_data = []
    for edge in graph_data["edges"]:
        edge_data.append({
            "from": edge["source"],
            "to": edge["target"],
            "label": edge["relationship"],
            "title": f"{edge['source']} {edge['relationship']} {edge['target']}",
            "arrows": "to",
            "color": {"color": "#34495e", "opacity": 0.6},
            "font": {"size": 10, "align": "middle"}
        })

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Knowledge Graph: {graph_data['center_node']}</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        #header {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        #stats {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        #mynetwork {{
            width: 100%;
            height: 800px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        #legend {{
            background: white;
            padding: 15px;
            margin-top: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 10px;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 5px;
            vertical-align: middle;
        }}
        #controls {{
            background: white;
            padding: 15px;
            margin-top: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        button {{
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        button:hover {{
            background: #2980b9;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>Knowledge Graph Network: {graph_data['center_node']}</h1>
        <div id="stats">
            <strong>{len(graph_data['nodes'])}</strong> entities connected via <strong>{len(graph_data['edges'])}</strong> relationships
        </div>
    </div>

    <div id="mynetwork"></div>

    <div id="controls">
        <button onclick="network.fit()">Reset View</button>
        <button onclick="togglePhysics()">Toggle Physics</button>
        <button onclick="exportImage()">Export as Image</button>
    </div>

    <div id="legend">
        <h3 style="margin-top: 0;">Entity Types</h3>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #e74c3c;"></span>
            <span>Organizations</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #3498db;"></span>
            <span>Services</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #2ecc71;"></span>
            <span>Pathways</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #f39c12;"></span>
            <span>Roles</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #9b59b6;"></span>
            <span>Conditions</span>
        </div>
    </div>

    <script type="text/javascript">
        // Create network data
        var nodes = new vis.DataSet({json.dumps(node_data, indent=8)});

        var edges = new vis.DataSet({json.dumps(edge_data, indent=8)});

        // Create a network
        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};

        var options = {{
            nodes: {{
                shape: 'dot',
                scaling: {{
                    label: {{
                        min: 12,
                        max: 20
                    }}
                }},
                borderWidth: 2,
                borderWidthSelected: 4
            }},
            edges: {{
                width: 2,
                smooth: {{
                    type: 'continuous',
                    roundness: 0.5
                }}
            }},
            physics: {{
                stabilization: {{
                    iterations: 200
                }},
                barnesHut: {{
                    gravitationalConstant: -3000,
                    centralGravity: 0.3,
                    springLength: 150,
                    springConstant: 0.04,
                    damping: 0.09,
                    avoidOverlap: 0.5
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                navigationButtons: true,
                keyboard: true
            }}
        }};

        var network = new vis.Network(container, data, options);

        // Highlight connected nodes on click
        network.on("click", function(params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                var connectedNodes = network.getConnectedNodes(nodeId);
                var connectedEdges = network.getConnectedEdges(nodeId);

                // Highlight
                nodes.update(nodes.get().map(node => ({{
                    id: node.id,
                    color: connectedNodes.includes(node.id) || node.id === nodeId
                        ? undefined
                        : {{color: '#ecf0f1', border: '#bdc3c7'}}
                }})));

                edges.update(edges.get().map(edge => ({{
                    id: edge.id,
                    color: connectedEdges.includes(edge.id)
                        ? undefined
                        : {{color: '#ecf0f1', opacity: 0.2}}
                }})));
            }} else {{
                // Reset
                nodes.update(nodes.get().map(node => ({{
                    id: node.id,
                    color: undefined
                }})));
                edges.update(edges.get().map(edge => ({{
                    id: edge.id,
                    color: undefined
                }})));
            }}
        }});

        // Physics toggle
        var physicsEnabled = true;
        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            network.setOptions({{ physics: physicsEnabled }});
        }}

        // Export as image (basic)
        function exportImage() {{
            // This would require canvas-to-image library
            alert("To export: Right-click the graph and 'Save image as...'");
        }}

        // Initial stabilization message
        network.on("stabilizationProgress", function(params) {{
            var progress = Math.round((params.iterations / params.total) * 100);
            console.log("Stabilizing network: " + progress + "%");
        }});

        network.on("stabilizationIterationsDone", function() {{
            console.log("Network stabilized!");
        }});
    </script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n[OK] Visualization created: {output_path}")
    print(f"   Nodes: {len(graph_data['nodes'])}")
    print(f"   Edges: {len(graph_data['edges'])}")
    print(f"   Center: {graph_data['center_node']}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python visualize_entity_network.py <entity1> [entity2] [entity3] ...")
        print("\nExamples:")
        print("  python visualize_entity_network.py LTHT")
        print("  python visualize_entity_network.py LTHT LCH")
        print("  python visualize_entity_network.py 'Leeds Teaching Hospitals NHS Trust'")
        sys.exit(1)

    # Load knowledge graph
    print("Loading knowledge graph...")
    kg = load_knowledge_graph()

    # Find entities
    entities = []
    for search_term in sys.argv[1:]:
        entity = find_entity(kg, search_term)
        entities.append(entity)
        print(f"  Found: {entity}")

    # Get relationships for all entities
    print(f"\nExtracting relationships (1-hop from {len(entities)} entities)...")
    all_nodes = set()
    all_edges = []

    for entity in entities:
        graph_data = get_entity_relationships(kg, entity, max_hops=1)
        all_nodes.update(graph_data["nodes"])
        all_edges.extend(graph_data["edges"])

    # Remove duplicate edges
    unique_edges = []
    seen = set()
    for edge in all_edges:
        key = (edge["source"], edge["target"], edge["relationship"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(edge)

    combined_graph = {
        "nodes": list(all_nodes),
        "edges": unique_edges,
        "center_node": ", ".join(entities)
    }

    # Create visualization
    output_file = "entity_network.html"
    create_html_visualization(combined_graph, kg, output_file)

    # Print summary
    print("\n" + "="*80)
    print("ENTITY NETWORK SUMMARY")
    print("="*80)

    # Count entity types
    type_counts = {}
    for node in combined_graph["nodes"]:
        entity_type = get_entity_type(kg, node)
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1

    print(f"\nEntity Type Distribution:")
    for entity_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {entity_type}: {count}")

    # Count relationship types
    rel_counts = {}
    for edge in combined_graph["edges"]:
        rel_type = edge["relationship"]
        rel_counts[rel_type] = rel_counts.get(rel_type, 0) + 1

    print(f"\nTop Relationship Types:")
    for rel_type, count in sorted(rel_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {rel_type}: {count}")

    print(f"\n[OK] Open {output_file} in your browser to explore the network!")


if __name__ == "__main__":
    main()
