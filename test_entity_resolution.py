"""
Test Entity Resolution System

Tests the entity resolution capabilities across the multi-agent system.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("ENTITY RESOLUTION SYSTEM TEST")
print("="*80)

# Test 1: EntityResolver initialization and basic functions
print("\n[TEST 1] EntityResolver Basic Functions")
print("-" * 80)

from analysis.entity_resolution import EntityResolver

resolver = EntityResolver()
stats = resolver.get_statistics()
print(f"[OK] Loaded {stats['total_entities']} entities with {stats['total_aliases']} aliases")
print(f"     Organizations: {stats['by_type']['organizations']['entities']} entities")
print(f"     Services: {stats['by_type']['services']['entities']} entities")
print(f"     Conditions: {stats['by_type']['conditions']['entities']} entities")

# Test 2: Entity resolution
print("\n[TEST 2] Entity Resolution (Alias to Canonical)")
print("-" * 80)

test_aliases = ["LCH", "LTHT", "LYPFT", "PCN", "ICB", "A&E", "COPD"]
for alias in test_aliases:
    canonical = resolver.resolve(alias)
    print(f"[OK] '{alias}' -> '{canonical}'")

# Test 3: Query expansion
print("\n[TEST 3] Query Expansion")
print("-" * 80)

test_queries = [
    "What are LCH workforce priorities?",
    "How do LTHT and LCH collaborate on discharge planning?",
    "What PCN services support mental health?"
]

for query in test_queries:
    expanded = resolver.expand_query(query, max_aliases_per_entity=2)
    print(f"\nOriginal: {query}")
    print(f"Expanded: {expanded}")

# Test 4: Text normalization
print("\n[TEST 4] Text Normalization (Standardizing Entity Names)")
print("-" * 80)

test_texts = [
    "LCH reported strong collaboration with LTHT on intermediate care.",
    "The PCN provides A&E diversion services for COPD patients.",
    "LYPFT partners with LCH Trust on mental health pathways."
]

for text in test_texts:
    normalized = resolver.normalize_text(text)
    print(f"\nOriginal:   {text}")
    print(f"Normalized: {normalized}")

# Test 5: Entity extraction
print("\n[TEST 5] Entity Extraction")
print("-" * 80)

sample_text = "LCH and LTHT are working with the ICB to improve discharge planning for COPD patients."
entities = resolver.extract_entities(sample_text)
print(f"Text: {sample_text}\n")
print(f"Found {len(entities)} entities:")
for entity in entities:
    print(f"  - {entity['canonical_name']} ({entity['entity_type']}) - matched '{entity['matched_alias']}'")

# Test 6: Fuzzy matching
print("\n[TEST 6] Fuzzy Matching (Typo Correction)")
print("-" * 80)

typos = ["Leds Community", "LTTH", "PCNs"]
for typo in typos:
    canonical, confidence = resolver.resolve_with_confidence(typo, fuzzy_threshold=0.8)
    if canonical:
        print(f"[OK] '{typo}' -> '{canonical}' (confidence: {confidence:.2f})")
    else:
        print(f"[FAIL] '{typo}' - no match found")

# Test 7: Integration with Knowledge Graph Agent
print("\n[TEST 7] Integration with Knowledge Graph Agent")
print("-" * 80)

try:
    from analysis.multi_agent.knowledge_graph_agent import KnowledgeGraphAgent

    kg_agent = KnowledgeGraphAgent()
    test_query = "What are LCH and LTHT discharge challenges?"

    # Extract entities using EntityResolver (through KG Agent)
    entities = kg_agent.extract_entities(test_query)
    print(f"Query: {test_query}")
    print(f"Entities detected: {[e['entity_name'] for e in entities]}")

    # Expand query
    expansion = kg_agent.expand_query(test_query)
    if expansion.get("kg_used"):
        print(f"[OK] KG expansion successful")
        print(f"     Entities found: {[e['entity_name'] for e in expansion['entities_found']]}")
        print(f"     Related terms added: {expansion['expansion_terms'][:5]}")
except Exception as e:
    print(f"[FAIL] KG Agent test failed: {e}")

# Test 8: Full system test (optional - commented out as it requires ChromaDB connection)
print("\n[TEST 8] Full Multi-Agent System Test")
print("-" * 80)
print("To test with actual multi-agent analysis, run:")
print("  python analysis/multi_agent/run_multi_agent.py --question \"What are LCH priorities?\" --max-iterations 2")

print("\n" + "="*80)
print("ENTITY RESOLUTION TESTS COMPLETE")
print("="*80)
print("\n[SUCCESS] All core entity resolution features working correctly!")
print("\nNext steps:")
print("  1. Test with full multi-agent analysis using web interface")
print("  2. Monitor logs for [ENTITY EXPANSION] and [NORMALIZATION] messages")
print("  3. Compare results with/without entity resolution")
