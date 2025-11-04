"""
Pattern-Based Relationship Extractor

Extracts high-confidence relationships using regex patterns for:
- Partnerships and collaborations
- Care pathways and referrals
- Service provision

These patterns target explicit mentions in documents for maximum precision.
"""

import re
import json
import sys
from typing import List, Dict, Set, Tuple
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class PatternExtractor:
    """Extract relationships using regex patterns."""

    # Partnership pattern definitions
    PARTNERSHIP_PATTERNS = [
        # Board to Board relationships
        r"Board\s+to\s+Board\s+(?:meetings?|relationships?|working)(?:\s+with)?\s+(\w+(?:\s+\w+){0,4})",
        r"Board\s+to\s+Board\s+(?:with|to)\s+([A-Z][^,.\n]+(?:NHS|Trust|Board|Council))",

        # Partnership mentions
        r"partnership\s+(?:with|between)\s+([A-Z][^,.\n]+?)(?:\s+(?:and|or)\s+)?(?:to|for|in)?",
        r"partnerships?\s+(?:with|involving|including)\s+([A-Z][^,.\n]{5,40}?)\s+(?:to|for|include)",

        # Collaboration patterns
        r"(?:collaborat(?:e|ing|es|ed)\s+with|work(?:ing)?\s+(?:alongside|in\s+partnership\s+with))\s+([A-Z][^,.\n]{5,40}?)\s+(?:to|on|for|in)",

        # Alliance patterns
        r"Alliance\s+(?:with|between)\s+([A-Z][^,.\n]{5,40}?)\s+(?:to|on|for|in)",
        r"strategic\s+(?:partnership|alliance|collaboration)\s+with\s+([A-Z][^,.\n]{5,40}?)",
    ]

    # Pathway pattern definitions
    PATHWAY_PATTERNS = [
        # Discharge patterns
        r"discharge\s+(?:pathway|process|route)\s+(?:to|from)\s+([A-Z][^,.\n]{5,40}?)",
        r"discharge\s+to\s+([A-Z][^,.\n]{5,40}?)\s+(?:pathway|process|route)",
        r"(?:transfer|discharge)\s+(?:from|to)\s+([A-Z][^,.\n]{5,40}?)\s+to\s+([A-Z][^,.\n]{5,40}?)",

        # Referral patterns
        r"referral\s+(?:pathway|process|route)\s+(?:from|to)\s+([A-Z][^,.\n]{5,40}?)",
        r"refer\s+(?:from|to)\s+([A-Z][^,.\n]{5,40}?)\s+to\s+([A-Z][^,.\n]{5,40}?)",

        # Care pathway patterns
        r"care\s+pathway\s+(?:from|between|involves?)\s+([A-Z][^,.\n]{5,40}?)",
        r"patient\s+(?:pathway|journey)\s+(?:through|involving|from)\s+([A-Z][^,.\n]{5,40}?)",

        # Integration patterns
        r"integrated\s+pathway\s+(?:between|with)\s+([A-Z][^,.\n]{5,40}?)",
        r"integrated\s+care\s+between\s+([A-Z][^,.\n]{5,40}?)\s+and\s+([A-Z][^,.\n]{5,40}?)",
    ]

    # Service provision pattern definitions
    SERVICE_PATTERNS = [
        # Direct provision
        r"([A-Z][^,.\n]{5,40}?)\s+(?:provides?|delivers?|offers?)\s+([a-z][^,.\n]{3,40}?)\s+(?:service|services|care)",
        r"([A-Z][^,.\n]{5,40}?)\s+provides?\s+([A-Z][^,.\n]{5,40}?)\s+(?:service|services|care)",

        # Service delivered by
        r"([a-z][^,.\n]{3,40}?)\s+(?:service|services|care)\s+(?:is\s+)?delivered?\s+(?:by|from)\s+([A-Z][^,.\n]{5,40}?)",
        r"([A-Z][^,.\n]{5,40}?)\s+(?:service|services)\s+(?:at|delivered\s+by|from)\s+([A-Z][^,.\n]{5,40}?)",
    ]

    def __init__(self, kg_path: str = "knowledge_graph_improved.json"):
        """Initialize extractor with existing KG for entity validation."""
        self.kg_path = kg_path
        self.kg = self._load_kg()
        self.entities = self._build_entity_set()

    def _load_kg(self) -> Dict:
        """Load knowledge graph for entity validation."""
        try:
            with open(self.kg_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load KG: {e}")
            return {"entities": {}, "relationships": []}

    def _build_entity_set(self) -> Dict[str, Set[str]]:
        """Build sets of entities for validation."""
        entities = {}
        for entity_type, entity_list in self.kg.get("entities", {}).items():
            entities[entity_type] = set(e.lower() for e in entity_list)
        return entities

    def extract_partnerships(self, text: str, document_source: str = "") -> List[Dict]:
        """Extract partnership relationships using patterns."""
        relationships = []

        for pattern in self.PARTNERSHIP_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                try:
                    # Extract matched text
                    matched_org = match.group(1).strip()

                    # Validate against known organizations
                    if not self._is_valid_organization(matched_org):
                        continue

                    # For now, without knowing the source org, mark as potential partnership
                    rel = {
                        "relationship": "partners_with",
                        "target": matched_org,
                        "confidence": 0.85,
                        "pattern_type": "partnership",
                        "source": document_source,
                    }
                    relationships.append(rel)

                except (IndexError, AttributeError):
                    continue

        return relationships

    def extract_pathways(self, text: str, document_source: str = "") -> List[Dict]:
        """Extract pathway relationships using patterns."""
        relationships = []

        for pattern in self.PATHWAY_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                try:
                    # Extract matched text
                    if match.lastindex == 2:
                        # Two-entity patterns (e.g., referral from X to Y)
                        source_entity = match.group(1).strip()
                        target_entity = match.group(2).strip()

                        if (self._is_valid_entity(source_entity) and
                            self._is_valid_entity(target_entity)):
                            rel = {
                                "source": source_entity,
                                "target": target_entity,
                                "relationship": "connected_via_pathway",
                                "confidence": 0.82,
                                "pattern_type": "pathway",
                                "source": document_source,
                            }
                            relationships.append(rel)
                    else:
                        # Single-entity patterns
                        entity = match.group(1).strip()
                        if self._is_valid_entity(entity):
                            rel = {
                                "target": entity,
                                "relationship": "uses_pathway",
                                "confidence": 0.75,
                                "pattern_type": "pathway",
                                "source": document_source,
                            }
                            relationships.append(rel)

                except (IndexError, AttributeError):
                    continue

        return relationships

    def extract_services(self, text: str, document_source: str = "") -> List[Dict]:
        """Extract service provision relationships using patterns."""
        relationships = []

        for pattern in self.SERVICE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                try:
                    if match.lastindex == 2:
                        # Two-entity patterns (org provides service or vice versa)
                        entity1 = match.group(1).strip()
                        entity2 = match.group(2).strip()

                        # Determine which is org, which is service
                        entity1_lower = entity1.lower()
                        entity2_lower = entity2.lower()

                        is_entity1_org = self._is_organization(entity1_lower)
                        is_entity2_org = self._is_organization(entity2_lower)

                        if is_entity1_org and not is_entity2_org:
                            rel = {
                                "source": entity1,
                                "target": entity2,
                                "relationship": "provides",
                                "confidence": 0.80,
                                "pattern_type": "service",
                                "source": document_source,
                            }
                            relationships.append(rel)
                        elif is_entity2_org and not is_entity1_org:
                            rel = {
                                "source": entity2,
                                "target": entity1,
                                "relationship": "provides",
                                "confidence": 0.80,
                                "pattern_type": "service",
                                "source": document_source,
                            }
                            relationships.append(rel)

                except (IndexError, AttributeError):
                    continue

        return relationships

    def _is_valid_organization(self, text: str) -> bool:
        """Check if text looks like an organization name."""
        text_lower = text.lower()

        # Check if it matches known organization
        if self._is_organization(text_lower):
            return True

        # Check for organizational keywords
        org_keywords = [
            'nhs', 'trust', 'board', 'council', 'service', 'hospital',
            'foundation', 'partnership', 'integrated', 'provider', 'icb'
        ]

        # Must have at least 3 characters and contain org keyword or proper case
        if len(text) < 3:
            return False

        has_org_keyword = any(kw in text_lower for kw in org_keywords)
        has_proper_case = any(c.isupper() for c in text)

        return has_org_keyword or (has_proper_case and len(text) > 5)

    def _is_valid_entity(self, text: str) -> bool:
        """Check if text looks like a valid entity."""
        text_lower = text.lower()
        return (len(text) >= 3 and
                (any(c.isupper() for c in text) or
                 any(text_lower in entities for entities in self.entities.values())))

    def _is_organization(self, text_lower: str) -> bool:
        """Check if text is a known organization."""
        orgs = self.entities.get("ORGANIZATIONS", set())
        return any(org.startswith(text_lower[:10]) or text_lower.startswith(org[:10])
                  for org in orgs if len(text_lower) > 5)

    def extract_from_text(self, text: str, document_source: str = "") -> Dict:
        """Extract all relationships from text."""
        return {
            "partnerships": self.extract_partnerships(text, document_source),
            "pathways": self.extract_pathways(text, document_source),
            "services": self.extract_services(text, document_source),
        }

    def extract_from_documents(self, texts: List[Tuple[str, str]]) -> Dict:
        """Extract relationships from list of (text, source) tuples."""
        all_relationships = defaultdict(list)

        for text, source in texts:
            extracted = self.extract_from_text(text, source)
            for rel_type, rels in extracted.items():
                all_relationships[rel_type].extend(rels)

        return dict(all_relationships)


def validate_patterns():
    """Test pattern matching on sample text."""
    print("\n" + "="*80)
    print("PATTERN VALIDATION TEST")
    print("="*80 + "\n")

    sample_texts = [
        ("Board to Board meeting with Leeds Teaching Hospitals NHS Trust confirmed", "test.md"),
        ("We partner with NHS England to deliver services", "test.md"),
        ("Discharge pathway from acute hospital to community care", "test.md"),
        ("LCH provides Community Nursing services for adults", "test.md"),
    ]

    extractor = PatternExtractor()

    for text, source in sample_texts:
        print(f"Text: {text[:60]}...")
        results = extractor.extract_from_text(text, source)

        for rel_type, rels in results.items():
            if rels:
                print(f"  {rel_type}: {len(rels)} matches")
                for rel in rels[:2]:
                    print(f"    - {rel}")
        print()


if __name__ == "__main__":
    validate_patterns()
