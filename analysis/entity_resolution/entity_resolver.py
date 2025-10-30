"""
entity_resolver.py

ENTITY RESOLUTION SYSTEM

PURPOSE:
  Resolves entity synonyms and aliases to canonical names for consistent
  retrieval and synthesis across the NHS Strategic Analysis System.

FEATURES:
  - Multi-level entity mappings (organizations, services, conditions, etc.)
  - Query expansion with all aliases for better retrieval
  - Text normalization for consistent outputs
  - Fuzzy matching for typos and variations
  - Context-aware disambiguation

USAGE:
  from entity_resolver import EntityResolver

  resolver = EntityResolver()
  canonical = resolver.resolve("LCH")  # -> "Leeds Community Healthcare NHS Trust"
  expanded = resolver.expand_query("What are LCH's priorities?")
  normalized = resolver.normalize_text("LCH reported...")
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
from difflib import SequenceMatcher


class EntityResolver:
    """
    Central entity resolution system for mapping aliases to canonical names.
    """

    def __init__(self, mappings_path: Optional[str] = None):
        """
        Initialize Entity Resolver.

        Args:
            mappings_path: Path to entity_mappings.json (optional)
        """
        if mappings_path is None:
            # Default to same directory as this file
            current_dir = Path(__file__).parent
            mappings_path = current_dir / "entity_mappings.json"

        self.mappings_path = Path(mappings_path)
        self.mappings = self._load_mappings()

        # Build reverse lookup: alias -> (entity_type, canonical_name)
        self.alias_lookup = self._build_alias_lookup()

        # Build priority lookup for disambiguation
        self.priority_lookup = self._build_priority_lookup()

    def _load_mappings(self) -> Dict:
        """Load entity mappings from JSON file."""
        try:
            with open(self.mappings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load entity mappings: {e}")
            return {"metadata": {}, "organizations": {}, "services": {}, "conditions": {}, "roles": {}, "pathways": {}}

    def _build_alias_lookup(self) -> Dict[str, Tuple[str, str]]:
        """
        Build reverse lookup from alias -> (entity_type, canonical_name).

        Returns:
            Dict with lowercase aliases as keys
        """
        lookup = {}

        # Iterate through all entity types
        for entity_type in ["organizations", "services", "conditions", "roles", "pathways"]:
            entities = self.mappings.get(entity_type, {})

            for canonical_name, entity_data in entities.items():
                # Add canonical name itself
                lookup[canonical_name.lower()] = (entity_type, canonical_name)

                # Add all aliases
                for alias in entity_data.get("aliases", []):
                    lookup[alias.lower()] = (entity_type, canonical_name)

                # Add abbreviation if present
                if "abbreviation" in entity_data:
                    abbr = entity_data["abbreviation"]
                    lookup[abbr.lower()] = (entity_type, canonical_name)

        return lookup

    def _build_priority_lookup(self) -> Dict[str, str]:
        """Build lookup of entity -> priority level for disambiguation."""
        priority_lookup = {}

        for entity_type in ["organizations", "services", "conditions", "roles", "pathways"]:
            entities = self.mappings.get(entity_type, {})
            for canonical_name, entity_data in entities.items():
                priority_lookup[canonical_name] = entity_data.get("priority", "MEDIUM")

        return priority_lookup

    def resolve(self, text: str, entity_type: Optional[str] = None) -> Optional[str]:
        """
        Resolve an alias to its canonical name.

        Args:
            text: Alias or entity mention to resolve
            entity_type: Optional filter by entity type (organizations, services, etc.)

        Returns:
            Canonical name if found, None otherwise

        Example:
            >>> resolver.resolve("LCH")
            "Leeds Community Healthcare NHS Trust"
            >>> resolver.resolve("LTHT")
            "Leeds Teaching Hospitals NHS Trust"
        """
        text_lower = text.lower().strip()

        if text_lower in self.alias_lookup:
            found_entity_type, canonical_name = self.alias_lookup[text_lower]

            # Filter by entity type if specified
            if entity_type and found_entity_type != entity_type:
                return None

            return canonical_name

        return None

    def resolve_with_confidence(self, text: str, entity_type: Optional[str] = None, fuzzy_threshold: float = 0.85) -> Tuple[Optional[str], float]:
        """
        Resolve entity with confidence score, including fuzzy matching.

        Args:
            text: Text to resolve
            entity_type: Optional entity type filter
            fuzzy_threshold: Minimum similarity score for fuzzy matches (0-1)

        Returns:
            Tuple of (canonical_name, confidence_score)

        Example:
            >>> resolver.resolve_with_confidence("LCH")
            ("Leeds Community Healthcare NHS Trust", 1.0)
            >>> resolver.resolve_with_confidence("Leds Community")  # typo
            ("Leeds Community Healthcare NHS Trust", 0.87)
        """
        # Try exact match first
        exact_match = self.resolve(text, entity_type)
        if exact_match:
            return (exact_match, 1.0)

        # Try fuzzy matching
        text_lower = text.lower().strip()
        best_match = None
        best_score = 0.0

        for alias, (found_type, canonical) in self.alias_lookup.items():
            # Filter by entity type if specified
            if entity_type and found_type != entity_type:
                continue

            # Calculate similarity
            similarity = SequenceMatcher(None, text_lower, alias).ratio()

            if similarity > best_score and similarity >= fuzzy_threshold:
                best_score = similarity
                best_match = canonical

        return (best_match, best_score)

    def get_all_aliases(self, canonical_name: str) -> List[str]:
        """
        Get all aliases for a canonical entity name.

        Args:
            canonical_name: Canonical entity name

        Returns:
            List of aliases (including abbreviation and canonical name itself)

        Example:
            >>> resolver.get_all_aliases("Leeds Community Healthcare NHS Trust")
            ["Leeds Community Healthcare NHS Trust", "LCH", "LCH Trust", ...]
        """
        # Find entity in mappings
        for entity_type in ["organizations", "services", "conditions", "roles", "pathways"]:
            entities = self.mappings.get(entity_type, {})
            if canonical_name in entities:
                entity_data = entities[canonical_name]
                aliases = [canonical_name] + entity_data.get("aliases", [])

                # Add abbreviation if present
                if "abbreviation" in entity_data:
                    aliases.append(entity_data["abbreviation"])

                return list(set(aliases))  # Deduplicate

        return [canonical_name]  # Return input if not found

    def expand_query(self, query: str, max_aliases_per_entity: int = 3) -> str:
        """
        Expand query with entity aliases for better retrieval.

        Detects entities in query and adds their aliases to improve retrieval coverage.

        Args:
            query: Original query text
            max_aliases_per_entity: Max aliases to add per detected entity

        Returns:
            Expanded query string

        Example:
            >>> resolver.expand_query("What are LCH's workforce priorities?")
            "What are LCH's workforce priorities? Leeds Community Healthcare NHS Trust Leeds Community"
        """
        expanded_terms = []
        query_lower = query.lower()

        # Find all entity mentions in query
        detected_entities = []

        for alias, (entity_type, canonical) in self.alias_lookup.items():
            # Check if alias appears as whole word in query
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, query_lower):
                detected_entities.append((alias, canonical))

        # Deduplicate by canonical name
        seen_canonical = set()
        unique_entities = []
        for alias, canonical in detected_entities:
            if canonical not in seen_canonical:
                seen_canonical.add(canonical)
                unique_entities.append((alias, canonical))

        # Add aliases for detected entities
        for alias, canonical in unique_entities:
            all_aliases = self.get_all_aliases(canonical)

            # Remove the alias already in query
            all_aliases = [a for a in all_aliases if a.lower() != alias.lower()]

            # Sort by length (shorter aliases first) and take top N
            all_aliases.sort(key=len)
            selected_aliases = all_aliases[:max_aliases_per_entity]

            expanded_terms.extend(selected_aliases)

        if expanded_terms:
            # Add expanded terms to query
            expansion = " " + " ".join(expanded_terms)
            return query + expansion

        return query

    def normalize_text(self, text: str, entity_types: Optional[List[str]] = None) -> str:
        """
        Normalize text by replacing all aliases with canonical names.

        Useful for standardizing outputs and reports.

        Args:
            text: Text to normalize
            entity_types: Optional list of entity types to normalize (default: all)

        Returns:
            Normalized text with canonical names

        Example:
            >>> resolver.normalize_text("LCH reported strong collaboration with LTHT")
            "Leeds Community Healthcare NHS Trust reported strong collaboration with Leeds Teaching Hospitals NHS Trust"
        """
        normalized_text = text

        # Sort aliases by length (longest first) to avoid partial replacements
        sorted_aliases = sorted(self.alias_lookup.items(), key=lambda x: len(x[0]), reverse=True)

        for alias, (entity_type, canonical) in sorted_aliases:
            # Filter by entity types if specified
            if entity_types and entity_type not in entity_types:
                continue

            # Skip if alias is the canonical name (no need to replace)
            if alias == canonical.lower():
                continue

            # Replace whole word occurrences (case-insensitive)
            pattern = r'\b' + re.escape(alias) + r'\b'
            normalized_text = re.sub(pattern, canonical, normalized_text, flags=re.IGNORECASE)

        return normalized_text

    def extract_entities(self, text: str, entity_types: Optional[List[str]] = None) -> List[Dict]:
        """
        Extract all entities mentioned in text.

        Args:
            text: Text to analyze
            entity_types: Optional filter by entity types

        Returns:
            List of dicts with entity_type, canonical_name, matched_alias, position

        Example:
            >>> resolver.extract_entities("LCH and LTHT are collaborating on discharge planning")
            [
                {"entity_type": "organizations", "canonical_name": "Leeds Community Healthcare NHS Trust",
                 "matched_alias": "LCH", "position": 0},
                {"entity_type": "organizations", "canonical_name": "Leeds Teaching Hospitals NHS Trust",
                 "matched_alias": "LTHT", "position": 8},
                {"entity_type": "pathways", "canonical_name": "Discharge Pathway",
                 "matched_alias": "discharge planning", "position": 40}
            ]
        """
        text_lower = text.lower()
        found_entities = []

        for alias, (entity_type, canonical) in self.alias_lookup.items():
            # Filter by entity type if specified
            if entity_types and entity_type not in entity_types:
                continue

            # Find all occurrences
            pattern = r'\b' + re.escape(alias) + r'\b'
            for match in re.finditer(pattern, text_lower):
                found_entities.append({
                    "entity_type": entity_type,
                    "canonical_name": canonical,
                    "matched_alias": alias,
                    "position": match.start(),
                    "priority": self.priority_lookup.get(canonical, "MEDIUM")
                })

        # Sort by position
        found_entities.sort(key=lambda x: x["position"])

        return found_entities

    def get_entity_info(self, canonical_name: str) -> Optional[Dict]:
        """
        Get full information about an entity.

        Args:
            canonical_name: Canonical entity name

        Returns:
            Dict with all entity metadata or None if not found
        """
        for entity_type in ["organizations", "services", "conditions", "roles", "pathways"]:
            entities = self.mappings.get(entity_type, {})
            if canonical_name in entities:
                entity_data = entities[canonical_name].copy()
                entity_data["entity_type"] = entity_type
                return entity_data

        return None

    def get_entities_by_type(self, entity_type: str) -> List[str]:
        """
        Get all canonical names for a specific entity type.

        Args:
            entity_type: Type (organizations, services, conditions, roles, pathways)

        Returns:
            List of canonical entity names
        """
        entities = self.mappings.get(entity_type, {})
        return list(entities.keys())

    def suggest_corrections(self, text: str, threshold: float = 0.7, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Suggest possible entity corrections for unrecognized text.

        Useful for identifying potential typos or new aliases to add.

        Args:
            text: Text that didn't match any entity
            threshold: Minimum similarity threshold
            top_n: Number of suggestions to return

        Returns:
            List of (canonical_name, similarity_score) tuples

        Example:
            >>> resolver.suggest_corrections("Leds Teaching")
            [("Leeds Teaching Hospitals NHS Trust", 0.89), ...]
        """
        text_lower = text.lower().strip()
        suggestions = []

        for alias, (entity_type, canonical) in self.alias_lookup.items():
            similarity = SequenceMatcher(None, text_lower, alias).ratio()
            if similarity >= threshold:
                suggestions.append((canonical, similarity))

        # Deduplicate by canonical name (keep highest score)
        seen = {}
        for canonical, score in suggestions:
            if canonical not in seen or score > seen[canonical]:
                seen[canonical] = score

        # Sort by score and return top N
        suggestions = [(k, v) for k, v in seen.items()]
        suggestions.sort(key=lambda x: x[1], reverse=True)

        return suggestions[:top_n]

    def get_statistics(self) -> Dict:
        """Get statistics about loaded entity mappings."""
        stats = {
            "total_entities": 0,
            "total_aliases": 0,
            "by_type": {}
        }

        for entity_type in ["organizations", "services", "conditions", "roles", "pathways"]:
            entities = self.mappings.get(entity_type, {})
            entity_count = len(entities)
            alias_count = sum(len(e.get("aliases", [])) for e in entities.values())

            stats["total_entities"] += entity_count
            stats["total_aliases"] += alias_count
            stats["by_type"][entity_type] = {
                "entities": entity_count,
                "aliases": alias_count
            }

        return stats


# Singleton instance for easy import
_resolver_instance = None

def get_resolver() -> EntityResolver:
    """Get singleton EntityResolver instance."""
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = EntityResolver()
    return _resolver_instance
