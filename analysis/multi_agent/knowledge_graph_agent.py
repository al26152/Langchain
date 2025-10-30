"""
knowledge_graph_agent.py

KNOWLEDGE GRAPH QUERY EXPANSION AGENT

PURPOSE:
  Uses the knowledge graph to expand queries with related entities,
  improving evidence retrieval through semantic relationships.

FEATURES:
  - Entity extraction from queries
  - Relationship traversal to find related entities
  - Query expansion with connected entities
  - Gap detection based on missing relationships
  - Entity-aware search suggestions

USAGE:
  from knowledge_graph_agent import KnowledgeGraphAgent

  kg_agent = KnowledgeGraphAgent("knowledge_graph_improved.json")
  expansion = kg_agent.expand_query("What are LTHT and LCH discharge challenges?")
"""

import json
import re
from typing import List, Dict, Set, Tuple
from pathlib import Path

# Import Entity Resolver
try:
    from analysis.entity_resolution import EntityResolver
except ImportError:
    EntityResolver = None  # Fallback if entity resolution not available


class KnowledgeGraphAgent:
    """Agent for knowledge graph-based query expansion."""

    def __init__(self, kg_path: str = "knowledge_graph_improved.json", use_entity_resolution: bool = True):
        """
        Initialize Knowledge Graph Agent.

        Args:
            kg_path: Path to knowledge graph JSON file
            use_entity_resolution: Whether to use EntityResolver for entity lookups (default True)
        """
        self.kg_path = Path(kg_path)
        self.kg = self._load_kg()

        # Initialize Entity Resolver if available
        self.entity_resolver = None
        if use_entity_resolution and EntityResolver is not None:
            try:
                self.entity_resolver = EntityResolver()
            except Exception as e:
                print(f"[WARNING] Could not initialize Entity Resolver in KG Agent: {e}")

        # Build reverse lookup for fast entity search
        self.entity_lookup = self._build_entity_lookup()

        # Build adjacency list for relationship traversal
        self.adjacency = self._build_adjacency_list()

    def _load_kg(self) -> Dict:
        """Load knowledge graph from JSON file."""
        try:
            with open(self.kg_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load knowledge graph: {e}")
            return {"entities": {}, "relationships": []}

    def _build_entity_lookup(self) -> Dict[str, Tuple[str, str]]:
        """
        Build lowercase entity lookup for fuzzy matching.

        If EntityResolver is available, it will be used for primary lookups.
        This method builds a fallback lookup from the knowledge graph.

        Returns:
            Dict mapping lowercase entity name to (entity_type, original_name)
        """
        lookup = {}

        # If EntityResolver is available, it handles aliases automatically
        # Just build basic lookup from KG entities
        for entity_type, entities in self.kg.get("entities", {}).items():
            for entity in entities:
                lookup[entity.lower()] = (entity_type, entity)

        return lookup

    def _build_adjacency_list(self) -> Dict[str, List[Dict]]:
        """
        Build adjacency list for fast relationship traversal.

        Returns:
            Dict mapping entity -> list of {target, relationship, direction}
        """
        adjacency = {}

        for rel in self.kg.get("relationships", []):
            source = rel["source"]
            target = rel["target"]
            rel_type = rel["relationship"]

            # Forward direction
            if source not in adjacency:
                adjacency[source] = []
            adjacency[source].append({
                "entity": target,
                "relationship": rel_type,
                "direction": "out"
            })

            # Backward direction (for bidirectional search)
            if target not in adjacency:
                adjacency[target] = []
            adjacency[target].append({
                "entity": source,
                "relationship": rel_type,
                "direction": "in"
            })

        return adjacency

    def extract_entities(self, query: str) -> List[Dict]:
        """
        Extract entities mentioned in the query.

        Uses EntityResolver if available for better alias recognition.

        Args:
            query: User query string

        Returns:
            List of dicts with entity_type, entity_name, matched_term
        """
        # Use EntityResolver if available (better alias handling)
        if self.entity_resolver:
            entities = self.entity_resolver.extract_entities(query)
            # Convert to KG format
            kg_entities = []
            for entity in entities:
                kg_entities.append({
                    "entity_type": entity["entity_type"],
                    "entity_name": entity["canonical_name"],
                    "matched_term": entity["matched_alias"],
                })
            return kg_entities

        # Fallback to original implementation
        query_lower = query.lower()
        found_entities = []

        # Check for entity mentions
        for entity_key, (entity_type, entity_name) in self.entity_lookup.items():
            if entity_key in query_lower:
                found_entities.append({
                    "entity_type": entity_type,
                    "entity_name": entity_name,
                    "matched_term": entity_key,
                })

        # Deduplicate (same entity matched multiple ways)
        seen = set()
        unique_entities = []
        for entity in found_entities:
            key = (entity["entity_type"], entity["entity_name"])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)

        return unique_entities

    def find_related_entities(self, entity_name: str, max_hops: int = 1) -> List[Dict]:
        """
        Find entities related to the given entity.

        Args:
            entity_name: Name of the entity
            max_hops: Maximum relationship hops (default 1)

        Returns:
            List of related entities with relationship info
        """
        if entity_name not in self.adjacency:
            return []

        related = []
        visited = {entity_name}
        queue = [(entity_name, 0)]  # (entity, hop_count)

        while queue:
            current, hops = queue.pop(0)

            if hops >= max_hops:
                continue

            for neighbor in self.adjacency.get(current, []):
                neighbor_entity = neighbor["entity"]

                if neighbor_entity not in visited:
                    visited.add(neighbor_entity)
                    related.append({
                        "entity": neighbor_entity,
                        "relationship": neighbor["relationship"],
                        "direction": neighbor["direction"],
                        "hops": hops + 1,
                        "from_entity": current,
                    })

                    # Add to queue for next hop
                    if hops + 1 < max_hops:
                        queue.append((neighbor_entity, hops + 1))

        return related

    def expand_query(self, query: str, max_expansion: int = 10) -> Dict:
        """
        Expand query with related entities from knowledge graph.

        Args:
            query: Original query
            max_expansion: Max number of expansion terms to add

        Returns:
            Dict with:
            - expanded_query: Query with added terms
            - entities_found: Entities identified in query
            - related_entities: Related entities added
            - expansion_terms: List of terms added to query
        """
        # Extract entities from query
        entities = self.extract_entities(query)

        if not entities:
            return {
                "expanded_query": query,
                "entities_found": [],
                "related_entities": [],
                "expansion_terms": [],
                "kg_used": False,
            }

        # Find related entities for each found entity
        all_related = []
        for entity in entities:
            related = self.find_related_entities(entity["entity_name"], max_hops=1)
            all_related.extend(related)

        # Prioritize related entities
        # Priority: Organizations > Services > Pathways > others
        priority_order = {
            "ORGANIZATIONS": 3,
            "SERVICES": 2,
            "PATHWAYS": 2,
            "CONDITIONS": 1,
            "ROLES": 1,
        }

        # Get entity types for related entities
        expansion_candidates = []
        for rel in all_related:
            entity_name = rel["entity"]
            entity_type = None

            # Find entity type
            for etype, entity_list in self.kg.get("entities", {}).items():
                if entity_name in entity_list:
                    entity_type = etype
                    break

            if entity_type:
                priority = priority_order.get(entity_type, 0)
                expansion_candidates.append({
                    "entity": entity_name,
                    "entity_type": entity_type,
                    "priority": priority,
                    "relationship": rel["relationship"],
                })

        # Sort by priority and take top N
        expansion_candidates.sort(key=lambda x: x["priority"], reverse=True)
        top_expansions = expansion_candidates[:max_expansion]

        # Build expansion terms
        expansion_terms = [e["entity"] for e in top_expansions]

        # Create expanded query
        expanded_query = query
        if expansion_terms:
            # Add terms in a natural way
            expansion_str = " ".join(expansion_terms)
            expanded_query = f"{query} {expansion_str}"

        return {
            "expanded_query": expanded_query,
            "entities_found": entities,
            "related_entities": top_expansions,
            "expansion_terms": expansion_terms,
            "kg_used": True,
        }

    def identify_missing_relationships(self,
                                      query: str,
                                      retrieved_sources: List[str]) -> List[Dict]:
        """
        Identify relationships mentioned in KG but missing from retrieved evidence.

        Args:
            query: Original query
            retrieved_sources: List of source documents retrieved

        Returns:
            List of missing relationship gaps
        """
        entities = self.extract_entities(query)

        if len(entities) < 2:
            return []

        gaps = []

        # For each pair of entities, check if they're related in KG
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Check if there's a relationship
                related = self.find_related_entities(entity1["entity_name"], max_hops=2)

                # Check if entity2 is in the related entities
                is_related = any(r["entity"] == entity2["entity_name"] for r in related)

                if is_related:
                    # Find the specific relationship
                    rel_info = next(
                        (r for r in related if r["entity"] == entity2["entity_name"]),
                        None
                    )

                    if rel_info:
                        gaps.append({
                            "type": "missing_relationship",
                            "severity": "MEDIUM",
                            "entity1": entity1["entity_name"],
                            "entity2": entity2["entity_name"],
                            "relationship": rel_info["relationship"],
                            "message": f"KG shows '{entity1['entity_name']}' {rel_info['relationship']} '{entity2['entity_name']}' but limited evidence retrieved",
                            "action": f"Search for evidence about {rel_info['relationship']} between these entities",
                        })

        return gaps

    def suggest_related_searches(self, query: str, top_n: int = 5) -> List[str]:
        """
        Suggest related search queries based on KG relationships.

        Args:
            query: Original query
            top_n: Number of suggestions to return

        Returns:
            List of suggested query strings
        """
        entities = self.extract_entities(query)

        if not entities:
            return []

        suggestions = []

        for entity in entities[:2]:  # Focus on first 2 entities
            related = self.find_related_entities(entity["entity_name"], max_hops=1)

            # Create suggestions based on relationships
            for rel in related[:top_n]:
                suggestion = f"{entity['entity_name']} {rel['relationship']} {rel['entity']}"
                suggestions.append(suggestion)

        return suggestions[:top_n]


# Test function
if __name__ == "__main__":
    kg_agent = KnowledgeGraphAgent()

    # Test query expansion
    test_query = "What are the discharge challenges between LTHT and LCH?"
    result = kg_agent.expand_query(test_query)

    print("=" * 80)
    print("KNOWLEDGE GRAPH AGENT TEST")
    print("=" * 80)
    print(f"\nOriginal Query: {test_query}")
    print(f"\nEntities Found: {len(result['entities_found'])}")
    for entity in result['entities_found']:
        print(f"  - {entity['entity_name']} ({entity['entity_type']})")

    print(f"\nRelated Entities Added: {len(result['related_entities'])}")
    for rel in result['related_entities'][:5]:
        print(f"  - {rel['entity']} ({rel['entity_type']}) via '{rel['relationship']}'")

    print(f"\nExpanded Query:\n{result['expanded_query']}")
    print("\n" + "=" * 80)
