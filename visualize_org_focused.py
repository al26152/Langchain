"""
visualize_org_focused.py

Create a focused visualization showing only organizations and their key pathways/services.
This creates a cleaner, more strategic view compared to the full entity network.

Usage:
    python visualize_org_focused.py
"""

import json
from typing import Dict, List, Set


def load_knowledge_graph(path: str = "knowledge_graph_improved.json") -> Dict:
    """Load the knowledge graph from JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_org_focused_network(kg: Dict, include_types: List[str] = None) -> Dict:
    """
    Get a focused network showing organizations and selected entity types.

    Args:
        kg: Knowledge graph
        include_types: Entity types to include (default: ORGANIZATIONS, PATHWAYS)

    Returns:
        Dict with nodes and edges
    """
    if include_types is None:
        include_types = ["ORGANIZATIONS", "PATHWAYS"]

    # Get all entities of included types
    nodes = set()
    for entity_type in include_types:
        if entity_type in kg["entities"]:
            nodes.update(kg["entities"][entity_type])

    # Get edges connecting these nodes
    edges = []
    for rel in kg["relationships"]:
        source = rel["source"]
        target = rel["target"]

        if source in nodes and target in nodes:
            edges.append({
                "source": source,
                "target": target,
                "relationship": rel["relationship"]
            })

    return {
        "nodes": list(nodes),
        "edges": edges,
        "included_types": include_types
    }


def create_org_focused_html(graph_data: Dict, kg: Dict, output_path: str = "org_network.html"):
    """Create HTML visualization focused on organizations."""

    # Get entity types for each node
    node_data = []
    for node in graph_data["nodes"]:
        # Find entity type
        entity_type = "UNKNOWN"
        for etype, entities in kg["entities"].items():
            if node in entities:
                entity_type = etype
                break

        # Color scheme
        colors = {
            "ORGANIZATIONS": "#e74c3c",  # Red (large nodes)
            "PATHWAYS": "#2ecc71",       # Green (medium nodes)
            "SERVICES": "#3498db",       # Blue (small nodes)
        }

        # Size based on type
        sizes = {
            "ORGANIZATIONS": 50,
            "PATHWAYS": 30,
            "SERVICES": 20,
        }

        # Check if it's a Leeds organization
        is_leeds = any(x in node for x in ["Leeds", "LTHT", "LCH", "LYPFT"])

        node_data.append({
            "id": node,
            "label": node.replace("Leeds ", "").replace(" NHS Trust", "").replace(" NHS Foundation Trust", ""),
            "title": f"{entity_type}: {node}",
            "color": colors.get(entity_type, "#95a5a6"),
            "size": sizes.get(entity_type, 20) * (1.5 if is_leeds else 1.0),
            "font": {
                "size": 14 if is_leeds else 10,
                "bold": is_leeds
            },
            "borderWidth": 3 if is_leeds else 1
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
            "color": {"color": "#34495e", "opacity": 0.7},
            "font": {"size": 9, "align": "top"},
            "smooth": {"type": "curvedCW", "roundness": 0.2}
        })

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Organization Network - Leeds Healthcare System</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        #header {{
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 32px;
        }}
        .subtitle {{
            color: #7f8c8d;
            font-size: 16px;
            margin-bottom: 20px;
        }}
        #stats {{
            display: flex;
            gap: 30px;
            margin-top: 15px;
        }}
        .stat {{
            background: #f8f9fa;
            padding: 15px 25px;
            border-radius: 8px;
            flex: 1;
        }}
        .stat-number {{
            font-size: 28px;
            font-weight: bold;
            color: #3498db;
        }}
        .stat-label {{
            font-size: 13px;
            color: #7f8c8d;
            margin-top: 5px;
        }}
        #mynetwork {{
            width: 100%;
            height: 700px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        #legend {{
            background: white;
            padding: 25px;
            margin-top: 20px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .legend-section {{
            margin-bottom: 20px;
        }}
        .legend-section h3 {{
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 18px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 25px;
            margin-bottom: 12px;
            padding: 8px 16px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .legend-color {{
            display: inline-block;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
        }}
        #controls {{
            background: white;
            padding: 20px;
            margin-top: 20px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            margin: 5px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        .highlight {{
            background: #f39c12;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div id="header">
            <h1>Leeds Healthcare System Network</h1>
            <div class="subtitle">Organization-focused view showing key partnerships and pathways</div>
            <div id="stats">
                <div class="stat">
                    <div class="stat-number">{len([n for n in graph_data['nodes'] if any(x in n for x in kg['entities'].get('ORGANIZATIONS', []))])}</div>
                    <div class="stat-label">Organizations</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{len([n for n in graph_data['nodes'] if any(x in n for x in kg['entities'].get('PATHWAYS', []))])}</div>
                    <div class="stat-label">Pathways</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{len(graph_data['edges'])}</div>
                    <div class="stat-label">Connections</div>
                </div>
            </div>
        </div>

        <div id="mynetwork"></div>

        <div id="controls">
            <button onclick="network.fit()">🎯 Reset View</button>
            <button onclick="togglePhysics()">⚡ Toggle Physics</button>
            <button onclick="focusLeeds()">🔍 Focus Leeds Orgs</button>
            <button onclick="showAllConnections()">🌐 Show All</button>
        </div>

        <div id="legend">
            <div class="legend-section">
                <h3>Entity Types</h3>
                <div class="legend-item">
                    <span class="legend-color" style="background-color: #e74c3c;"></span>
                    <span><strong>Organizations</strong> (NHS Trusts, Councils)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background-color: #2ecc71;"></span>
                    <span><strong>Pathways</strong> (Care pathways, Collaboratives)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background-color: #3498db;"></span>
                    <span><strong>Services</strong> (Healthcare services)</span>
                </div>
            </div>
            <div class="legend-section">
                <h3>Key Leeds Organizations</h3>
                <div style="color: #7f8c8d; font-size: 14px;">
                    <span class="highlight">LTHT</span> Leeds Teaching Hospitals NHS Trust (Acute care) •
                    <span class="highlight">LCH</span> Leeds Community Healthcare NHS Trust (Community care) •
                    <span class="highlight">LYPFT</span> Leeds & York Partnership NHS Foundation Trust (Mental health)
                </div>
            </div>
        </div>
    </div>

    <script type="text/javascript">
        var nodes = new vis.DataSet({json.dumps(node_data, indent=8)});
        var edges = new vis.DataSet({json.dumps(edge_data, indent=8)});

        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};

        var options = {{
            nodes: {{
                shape: 'dot',
                borderWidth: 2,
                borderWidthSelected: 4,
                shadow: true
            }},
            edges: {{
                width: 2,
                shadow: true
            }},
            physics: {{
                barnesHut: {{
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 200,
                    springConstant: 0.04,
                    damping: 0.09,
                    avoidOverlap: 1
                }},
                stabilization: {{
                    iterations: 250
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 150,
                navigationButtons: true,
                keyboard: true,
                zoomView: true
            }}
        }};

        var network = new vis.Network(container, data, options);
        var physicsEnabled = true;
        var leedsNodes = {json.dumps([n['id'] for n in node_data if any(x in n['id'] for x in ['Leeds', 'LTHT', 'LCH', 'LYPFT'])])};

        network.on("click", function(params) {{
            if (params.nodes.length > 0) {{
                highlightConnected(params.nodes[0]);
            }} else {{
                resetHighlight();
            }}
        }});

        function highlightConnected(nodeId) {{
            var connectedNodes = network.getConnectedNodes(nodeId);
            var connectedEdges = network.getConnectedEdges(nodeId);

            nodes.get().forEach(function(node) {{
                if (connectedNodes.includes(node.id) || node.id === nodeId) {{
                    nodes.update({{id: node.id, color: undefined, hidden: false}});
                }} else {{
                    nodes.update({{id: node.id, color: '#ecf0f1', opacity: 0.3}});
                }}
            }});

            edges.get().forEach(function(edge) {{
                if (connectedEdges.includes(edge.id)) {{
                    edges.update({{id: edge.id, color: undefined, hidden: false}});
                }} else {{
                    edges.update({{id: edge.id, color: '#ecf0f1', opacity: 0.1}});
                }}
            }});
        }}

        function resetHighlight() {{
            nodes.get().forEach(function(node) {{
                nodes.update({{id: node.id, color: undefined, hidden: false, opacity: 1}});
            }});
            edges.get().forEach(function(edge) {{
                edges.update({{id: edge.id, color: undefined, hidden: false, opacity: 1}});
            }});
        }}

        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            network.setOptions({{ physics: physicsEnabled }});
        }}

        function focusLeeds() {{
            network.fit({{
                nodes: leedsNodes,
                animation: {{
                    duration: 1000,
                    easingFunction: 'easeInOutQuad'
                }}
            }});
        }}

        function showAllConnections() {{
            resetHighlight();
            network.fit();
        }}

        network.on("stabilizationIterationsDone", function() {{
            console.log("Network stabilized - ready for interaction!");
            network.fit();
        }});
    </script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n[OK] Organization-focused visualization created: {output_path}")
    print(f"   Organizations: {len([n for n in graph_data['nodes'] if any(x in n for x in kg['entities'].get('ORGANIZATIONS', []))])}")
    print(f"   Pathways: {len([n for n in graph_data['nodes'] if any(x in n for x in kg['entities'].get('PATHWAYS', []))])}")
    print(f"   Total Connections: {len(graph_data['edges'])}")


def main():
    """Main entry point."""
    print("="*80)
    print("ORGANIZATION-FOCUSED NETWORK VISUALIZATION")
    print("="*80)

    # Load knowledge graph
    print("\nLoading knowledge graph...")
    kg = load_knowledge_graph()

    # Get org-focused network
    print("Extracting organization and pathway network...")
    graph_data = get_org_focused_network(kg, include_types=["ORGANIZATIONS", "PATHWAYS"])

    # Create visualization
    create_org_focused_html(graph_data, kg, "org_network.html")

    print("\n[OK] Open org_network.html in your browser!")
    print("\nThis visualization shows:")
    print("  - All healthcare organizations in the system")
    print("  - Key care pathways and collaboratives")
    print("  - How organizations connect through shared pathways")
    print("\nClick any organization to see its connections!")


if __name__ == "__main__":
    main()
