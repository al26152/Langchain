# Organization-Aware Filtering - Fix for LTHT vs LCH Results

**Date:** 2025-10-30
**Status:** ✅ IMPLEMENTED

## Problem Identified

When querying about a specific organization (e.g., "What are the main challenges for LTHT?"), the system was returning results from multiple organizations (LTHT, LCH, LYPFT) because:

1. **Query Expansion:** Entity resolution expands "LTHT" to include related terms
2. **Knowledge Graph Expansion:** Adds related organizations that are part of "Leeds health ecosystem"
3. **No Document Filtering:** The semantic similarity search returns all relevant chunks regardless of which organization's document they come from
4. **Attribution Confusion:** Results from collaborative frameworks (like "Leeds One Workforce") get attributed to the queried organization

**Example:**
- Query: "What are the main challenges for LTHT over the next 4 years?"
- Expected: LTHT Annual Report 2024-25, LTHT strategic documents
- Actual: LCH documents, Leeds One Workforce (collaborative), mixed sources

---

## Solution Implemented

Added **organization-aware document filtering** to the Evidence Agent that:

1. **Extracts the Primary Organization** from the query
2. **Filters and Re-ranks Results** to prioritize organization-specific documents
3. **Maintains Cross-Org References** for context (doesn't exclude other organizations completely)

### New Methods Added to `evidence_agent.py`:

#### `_extract_primary_organization(query: str) -> Optional[str]`
```python
Extracts the primary organization mentioned in the query using entity resolution.

Args:
    query: The original search query

Returns:
    Canonical organization name (e.g., "Leeds Teaching Hospitals NHS Trust") or None
```

**How it works:**
- Uses entity resolver to find all organizations mentioned in query
- Returns the first (most relevant) one as the primary organization
- Falls back to None if no organization found

#### `_filter_by_organization_affinity(results, primary_org) -> List`
```python
Re-ranks retrieved documents to prioritize the primary organization.

Args:
    results: List of documents from similarity search
    primary_org: The primary organization to filter by

Returns:
    Re-ranked results with organization-specific docs first
```

**How it works:**
- Checks each document's metadata and content for organization keywords
- Separates results into:
  - **Primary org docs**: Documents specifically about the queried organization
  - **Other docs**: Supporting context from other sources
- Returns primary org docs first, followed by others
- **Does not exclude** other organizations - just reorders them

### Organization Keywords Mapping:

```python
"Leeds Teaching Hospitals NHS Trust": ["LTHT", "Teaching", "Acute", "Hospital"]
"Leeds Community Healthcare NHS Trust": ["LCH", "Community"]
"Leeds and York Partnership NHS Foundation Trust": ["LYPFT", "Mental Health", "Partnership"]
```

---

## Implementation in Search Flow

The `search()` method now follows this flow:

```
1. Extract primary organization from query
   └─> "What are the main challenges for LTHT?" → "Leeds Teaching Hospitals NHS Trust"

2. Expand query (entity resolution + knowledge graph)
   └─> Adds aliases and related terms

3. Retrieve results from ChromaDB (semantic similarity)
   └─> Gets top k chunks regardless of source

4. Filter and re-rank by organization affinity
   └─> LTHT-specific docs move to top of results

5. Extract evidence with metadata
   └─> Process filtered results
```

**Console Output Example:**
```
[ITERATION 1] Evidence Agent: Searching for evidence...
[ORG FILTER] Primary organization: Leeds Teaching Hospitals NHS Trust
[ENTITY EXPANSION] Detected: Leeds Teaching Hospitals NHS Trust
[ENTITY EXPANSION] Added aliases for better retrieval
[ITERATION 1] Retrieved 20 chunks from 6 documents
```

---

## Expected Behavior Changes

### Before Fix:
```
Query: "What are the main challenges for LTHT?"

Retrieved Sources (top 5):
1. LCH Annual Report 2024-25
2. Leeds One Workforce Strategy
3. LTHT Annual Report 2024-25  (4th place!)
4. LCH Strategic Plan
5. Trust Board Minutes (LCH)

Result: Lots of LCH and collaborative content, not LTHT-focused
```

### After Fix:
```
Query: "What are the main challenges for LTHT?"

Retrieved Sources (top 5):
1. LTHT Annual Report 2024-25
2. LTHT Strategic Plan
3. LTHT Workforce Strategy
4. Leeds One Workforce (collaborative context)
5. LCH Annual Report (comparative context)

Result: LTHT-specific content prioritized, with collaborative/comparative context
```

---

## Benefits

✅ **Organization-Specific Answers:** Queries about LTHT now prioritize LTHT documents

✅ **Maintains Context:** Still includes collaborative and comparative information

✅ **Better Attribution:** Results are properly attributed to the right organization

✅ **Transparent Filtering:** Console logs show which organization was detected and filtered

✅ **Backward Compatible:** Non-organization queries work as before (no filtering applied)

---

## Testing the Fix

To verify the fix works in the web interface:

1. **Ask an organization-specific question:**
   ```
   "What are the main challenges for LTHT over the next 4 years?"
   ```

2. **Look for organization filter in logs:**
   ```
   [ORG FILTER] Primary organization: Leeds Teaching Hospitals NHS Trust
   ```

3. **Verify sources are LTHT-focused:**
   - First sources should be LTHT Annual Report, LTHT Strategy documents
   - LCH and other organization docs appear lower in the list
   - Collaborative documents (Leeds One Workforce) used as supporting context

4. **Compare with similar question for another org:**
   ```
   "What are the main challenges for LCH?"
   ```
   Should return LCH-specific documents in priority order.

---

## Edge Cases Handled

| Scenario | Handling |
|----------|----------|
| Query mentions multiple orgs | Uses first (most relevant) org as primary |
| Query mentions no org | No filtering applied, normal retrieval |
| Org has no specific documents | Falls back to general/collaborative docs |
| Collaborative documents only | Returns in original relevance order |

---

## Code Location

**Modified File:** `analysis/multi_agent/evidence_agent.py`

**Changes:**
- Lines 176-239: Added two new filtering methods
- Lines 139-152: Modified `search()` to apply filtering

**No changes needed to:**
- Config system
- Knowledge graph
- Entity resolution mappings
- Synthesis agent
- Web interface

---

## Future Improvements

1. **Metadata-based filtering:** Add "organization" field to document metadata for more reliable filtering

2. **Relationship-aware filtering:** Use knowledge graph relationships to identify organization-specific documents

3. **Confidence scoring:** Add confidence scores indicating how directly relevant a document is to the primary organization

4. **User controls:** Allow users to toggle organization filtering in web interface

5. **Weighted re-ranking:** Use similarity scores as secondary sort after organization affinity

---

## Summary

Organization-aware filtering has been successfully added to the Evidence Agent. When users ask about a specific organization, the system now intelligently prioritizes documents from that organization while maintaining access to cross-organizational context and collaborative frameworks.

This ensures that answers are **focused, accurate, and properly attributed** to the correct organization.
