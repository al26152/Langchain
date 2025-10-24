#!/usr/bin/env python3
"""
deduplicate_organizations.py

Merge organizational aliases so that LCH and Leeds Community Healthcare NHS Trust
are treated as a single entity. Same for LTHT and Leeds Teaching Hospitals NHS Trust, etc.
"""

import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*80)
print("ORGANIZATIONAL ALIAS DEDUPLICATION")
print("="*80)

# Load the graph
with open("knowledge_graph_improved.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define mapping: alias -> primary name
ORGANIZATION_MAPPING = {
    # LCH variants
    "LCH": "Leeds Community Healthcare NHS Trust",

    # LTHT variants
    "LTHT": "Leeds Teaching Hospitals NHS Trust",

    # Add any other variants here as they're discovered
}

print("\nOrganization Alias Mapping:")
for alias, primary in ORGANIZATION_MAPPING.items():
    print(f"  {alias} -> {primary}")

# Process entities
print("\n[STEP 1] Merging organizational entities...")

original_org_count = len(data['entities']['ORGANIZATIONS'])

# Remove aliases, keep primary names
new_orgs = []
removed_aliases = []

for org in data['entities']['ORGANIZATIONS']:
    if org in ORGANIZATION_MAPPING:
        primary = ORGANIZATION_MAPPING[org]
        if primary not in new_orgs:
            new_orgs.append(primary)
        removed_aliases.append(org)
        print(f"  Merging: {org} -> {primary}")
    else:
        new_orgs.append(org)

data['entities']['ORGANIZATIONS'] = new_orgs

print(f"\nOrganizations: {original_org_count} -> {len(new_orgs)} (removed {len(removed_aliases)} aliases)")

# Process relationships
print("\n[STEP 2] Updating all relationships to use primary names...")

updated_count = 0
for rel in data['relationships']:
    source = rel.get('source', '')
    target = rel.get('target', '')

    # Map source
    if source in ORGANIZATION_MAPPING:
        rel['source'] = ORGANIZATION_MAPPING[source]
        updated_count += 1

    # Map target
    if target in ORGANIZATION_MAPPING:
        rel['target'] = ORGANIZATION_MAPPING[target]
        updated_count += 1

print(f"  Updated {updated_count} relationship references")

# Remove duplicate relationships (same source, target, relationship)
print("\n[STEP 3] Removing duplicate relationships...")

seen = set()
unique_rels = []

for rel in data['relationships']:
    key = (rel.get('source'), rel.get('target'), rel.get('relationship'))
    if key not in seen:
        unique_rels.append(rel)
        seen.add(key)

original_rel_count = len(data['relationships'])
data['relationships'] = unique_rels

print(f"  Relationships: {original_rel_count} -> {len(unique_rels)} (removed {original_rel_count - len(unique_rels)} duplicates)")

# Remove isolated entities
print("\n[STEP 4] Removing isolated entities...")

# Find connected entities
connected = set()
for rel in data['relationships']:
    connected.add(rel.get('source', ''))
    connected.add(rel.get('target', ''))

# Keep critical organizations even if isolated
critical_to_keep = {
    "Leeds Community Healthcare NHS Trust",
    "Leeds and York Partnership NHS Foundation Trust",
    "Leeds Teaching Hospitals NHS Trust",
    "Integrated Care Board",
    "NHS England"
}

for entity_type in ['SERVICES', 'PATHWAYS', 'ROLES', 'CONDITIONS']:
    original = len(data['entities'][entity_type])
    data['entities'][entity_type] = [e for e in data['entities'][entity_type] if e in connected]
    removed = original - len(data['entities'][entity_type])
    if removed > 0:
        print(f"  {entity_type}: removed {removed} isolated entities")

# For organizations, keep connected ones + critical ones
original_orgs = len(data['entities']['ORGANIZATIONS'])
data['entities']['ORGANIZATIONS'] = [
    e for e in data['entities']['ORGANIZATIONS']
    if e in connected or e in critical_to_keep
]
removed_orgs = original_orgs - len(data['entities']['ORGANIZATIONS'])
if removed_orgs > 0:
    print(f"  ORGANIZATIONS: removed {removed_orgs} isolated entities")

# Update statistics
print("\n[STEP 5] Updating statistics...")

total_entities = sum(len(v) for v in data['entities'].values())
data['statistics']['total_entities'] = total_entities
data['statistics']['total_relationships'] = len(data['relationships'])

print(f"  Total entities: {total_entities}")
print(f"  Total relationships: {len(data['relationships'])}")

# Save deduplicated graph
print("\n[STEP 6] Saving deduplicated knowledge graph...")

output_file = "knowledge_graph_improved.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"[OK] Saved to {output_file}")

# Summary
print("\n" + "="*80)
print("DEDUPLICATION COMPLETE")
print("="*80)

print("\nEntities by type:")
for entity_type, entities in data['entities'].items():
    print(f"  {entity_type:20} {len(entities):3}")

print("\nKey Organizations (should be single entries now):")
key_orgs = [
    "Leeds Community Healthcare NHS Trust",
    "Leeds and York Partnership NHS Foundation Trust",
    "Leeds Teaching Hospitals NHS Trust"
]

for org in key_orgs:
    if org in data['entities']['ORGANIZATIONS']:
        # Count relationships for this org
        rel_count = len([
            r for r in data['relationships']
            if r.get('source') == org or r.get('target') == org
        ])
        print(f"  ✓ {org} ({rel_count} relationships)")
    else:
        print(f"  ✗ {org} - MISSING")

print(f"\nRelationships: {len(data['relationships'])}")

print("\n" + "="*80 + "\n")
