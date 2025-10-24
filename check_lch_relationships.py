#!/usr/bin/env python3
"""
Check what explicit relationships LCH has in the graph
"""

import json

with open("knowledge_graph_improved.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

relationships = data.get("relationships", [])

print("=" * 80)
print("LCH RELATIONSHIPS ANALYSIS")
print("=" * 80)

print(f"\nTotal relationships: {len(relationships)}")

# Find LCH relationships
lch_rels = [r for r in relationships if 'LCH' in r.get('source', '') or 'LCH' in r.get('target', '')]
print(f"Total relationships involving LCH: {len(lch_rels)}")

# Separate explicit from implicit
explicit_lch_rels = [r for r in lch_rels if r.get('relationship') != 'mentioned_together_in']
implicit_lch_rels = [r for r in lch_rels if r.get('relationship') == 'mentioned_together_in']

print(f"\n[EXPLICIT RELATIONSHIPS] for LCH: {len(explicit_lch_rels)}")
if explicit_lch_rels:
    for rel in explicit_lch_rels:
        print(f"  {rel.get('source')} --[{rel.get('relationship')}]--> {rel.get('target')}")
else:
    print("  (None found)")

print(f"\n[IMPLICIT RELATIONSHIPS] for LCH: {len(implicit_lch_rels)}")
if implicit_lch_rels:
    print(f"  First 10:")
    for rel in implicit_lch_rels[:10]:
        print(f"    {rel.get('source')} --[mentioned_together_in]--> {rel.get('target')}")

# Check Leeds Community Healthcare NHS Trust too
print("\n" + "=" * 80)
print("Leeds Community Healthcare NHS Trust RELATIONSHIPS")
print("=" * 80)

lch_full_rels = [r for r in relationships if 'Leeds Community Healthcare NHS Trust' in r.get('source', '') or 'Leeds Community Healthcare NHS Trust' in r.get('target', '')]
print(f"Total relationships involving Leeds Community Healthcare NHS Trust: {len(lch_full_rels)}")

explicit_full = [r for r in lch_full_rels if r.get('relationship') != 'mentioned_together_in']
implicit_full = [r for r in lch_full_rels if r.get('relationship') == 'mentioned_together_in']

print(f"\n[EXPLICIT RELATIONSHIPS]: {len(explicit_full)}")
if explicit_full:
    for rel in explicit_full:
        print(f"  {rel.get('source')} --[{rel.get('relationship')}]--> {rel.get('target')}")
else:
    print("  (None found)")

print(f"\n[IMPLICIT RELATIONSHIPS]: {len(implicit_full)}")

# Show all explicit relationships to understand what was extracted
print("\n" + "=" * 80)
print("ALL EXPLICIT RELATIONSHIPS IN GRAPH")
print("=" * 80)

all_explicit = [r for r in relationships if r.get('relationship') != 'mentioned_together_in']
print(f"\nTotal: {len(all_explicit)}\n")

for rel in all_explicit:
    print(f"{rel.get('source')} --[{rel.get('relationship')}]--> {rel.get('target')}")
