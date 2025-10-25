#!/usr/bin/env python3
"""
Clean up duplicate organizations and filter out governance bodies.

This script:
1. Identifies and removes governance bodies (not provider organizations)
2. Merges organization variants (LCH TRUST, Leeds Community -> Leeds Community Healthcare NHS Trust)
3. Updates all relationships to use canonical organization names
"""

import json
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*80)
print("CLEANING DUPLICATE ORGANIZATIONS AND GOVERNANCE BODIES")
print("="*80)

# Load data
with open('knowledge_graph_improved.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define canonical organization names and their variants
ORGANIZATION_MERGES = {
    # Leeds-based organizations
    "Leeds Community Healthcare NHS Trust": [
        "LCH Trust",
        "Leeds Community",
        "Community Health Leeds",
        "Community healthcare",
        "LCH",
    ],
    "Leeds Teaching Hospitals NHS Trust": [
        "LTHT",
        "Teaching Hospitals",
        "Leeds Teaching Hospital",
    ],
    "Leeds and York Partnership NHS Foundation Trust": [
        "LYPFT",
        "Leeds York Partnership",
    ],
}

# Governance bodies - should not be listed as provider organizations
GOVERNANCE_BODIES = {
    "NHS England",
    "NHS West Yorkshire Integrated Care Board",
    "Integrated Care Board",
    "NHS",
    "Health Innovation North",
    "Wellbeing Board",
    "Long-term Conditions and Frailty Population Boards",
    "Children and Young People's Population Board",
    "End-of-life Population Board",
}

# Other non-provider entities that should not be in ORGANIZATIONS
NON_PROVIDERS = {
    "Services NHS Foundation Trust",  # Generic fragment
    "NHS Foundation Trust",  # Generic fragment
    "Foundation Trust",  # Generic fragment
    "Health services",  # Too generic
    "Royal College of Psychiatry",  # Professional body, not provider
    "Tees, Esk and Wear Valleys NHS Foundation Trust",  # Not Leeds-based
    "Tower Hamlets NHS Trust",  # Not Leeds-based
}

print("\n[STEP 1] Analyzing organizations...")

current_orgs = data['entities']['ORGANIZATIONS']
print(f"Current organizations: {len(current_orgs)}")

# Build reverse mapping: variant -> canonical
variant_to_canonical = {}
for canonical, variants in ORGANIZATION_MERGES.items():
    for variant in variants:
        variant_to_canonical[variant] = canonical

print(f"\nOrganization variants to merge: {sum(len(v) for v in ORGANIZATION_MERGES.values())}")

# Track replacements
replacements = {}
removals = set()

for org in current_orgs:
    # Check if it's a governance body
    if org in GOVERNANCE_BODIES:
        removals.add(org)
        print(f"  REMOVE (governance body): {org}")
    # Check if it's a non-provider entity
    elif org in NON_PROVIDERS:
        removals.add(org)
        print(f"  REMOVE (non-provider): {org}")
    # Check if it's a variant
    elif org in variant_to_canonical:
        canonical = variant_to_canonical[org]
        replacements[org] = canonical
        print(f"  MERGE: {org} -> {canonical}")

print(f"\nSummary:")
print(f"  Governance bodies to remove: {len([o for o in removals if o in GOVERNANCE_BODIES])}")
print(f"  Non-provider entities to remove: {len([o for o in removals if o in NON_PROVIDERS])}")
print(f"  Variants to merge: {len(replacements)}")

print("\n[STEP 2] Updating organization entities...")

# Remove governance bodies and non-providers
cleaned_orgs = [org for org in current_orgs if org not in removals]

# Ensure canonical organizations exist
for canonical in ORGANIZATION_MERGES.keys():
    if canonical not in cleaned_orgs:
        cleaned_orgs.append(canonical)
        print(f"  Added canonical: {canonical}")

data['entities']['ORGANIZATIONS'] = sorted(list(set(cleaned_orgs)))
print(f"New organization count: {len(data['entities']['ORGANIZATIONS'])}")

print("\n[STEP 3] Updating relationships...")

old_rel_count = len(data['relationships'])

# Update relationships to use canonical names
updated_relationships = []
for rel in data['relationships']:
    source = rel.get('source', '')
    target = rel.get('target', '')

    # Replace variants with canonical names
    if source in replacements:
        source = replacements[source]
    if target in replacements:
        target = replacements[target]

    # Remove relationships that reference removed organizations
    if source in removals or target in removals:
        continue

    # Keep the relationship with updated names
    rel['source'] = source
    rel['target'] = target
    updated_relationships.append(rel)

data['relationships'] = updated_relationships
print(f"Relationships before cleanup: {old_rel_count}")
print(f"Relationships after cleanup: {len(data['relationships'])}")
print(f"Relationships removed: {old_rel_count - len(data['relationships'])}")

print("\n[STEP 4] Recalculating statistics...")

# Update statistics
explicit_rels = len([r for r in data['relationships'] if r.get('relationship') != 'mentioned_together_in'])
implicit_rels = len([r for r in data['relationships'] if r.get('relationship') == 'mentioned_together_in'])

data['statistics'] = {
    'total_entities': sum(len(v) for v in data['entities'].values()),
    'total_relationships': len(data['relationships']),
    'extraction_method': 'Framework-Based (NHS Service Standards)',
    'explicit_relationships': explicit_rels,
    'implicit_relationships': implicit_rels,
}

print(f"Total entities: {data['statistics']['total_entities']}")
print(f"Total relationships: {data['statistics']['total_relationships']}")
print(f"  Explicit: {explicit_rels}")
print(f"  Implicit: {implicit_rels}")

print("\n[STEP 5] Saving cleaned knowledge graph...")

with open('knowledge_graph_improved.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("[OK] Saved to knowledge_graph_improved.json")

print("\n[STEP 6] Organizations summary...")

print("\nKey Leeds Provider Organizations:")
key_orgs = [
    "Leeds Community Healthcare NHS Trust",
    "Leeds Teaching Hospitals NHS Trust",
    "Leeds and York Partnership NHS Foundation Trust",
]

for org in key_orgs:
    if org in data['entities']['ORGANIZATIONS']:
        provides = len([r for r in data['relationships'] if r.get('source') == org and r.get('relationship') == 'provides'])
        total_conn = len([r for r in data['relationships'] if r.get('source') == org or r.get('target') == org])
        print(f"  {org}")
        print(f"    Services provided: {provides}")
        print(f"    Total connections: {total_conn}")

print("\nAll remaining organizations:")
for org in sorted(data['entities']['ORGANIZATIONS']):
    provides = len([r for r in data['relationships'] if r.get('source') == org and r.get('relationship') == 'provides'])
    if provides > 0:
        print(f"  {org}: {provides} services")

print("\n" + "="*80)
print("CLEANED AND READY FOR VISUALIZATION")
print("="*80 + "\n")
