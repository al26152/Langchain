# Scalability Analysis: Testing Three Approaches

## What We Tested

### 1. **Explicit-Only Approach** (build_knowledge_graph_explicit.py)
- Extract ONLY relationships explicitly stated in text
- NO document source inference
- NO organization-specific rules
- Result: **9 organizations, 1 relationship**
- **FAILED**: Too conservative, doesn't recognize service listings

### 2. **Context-Aware Approach** (build_knowledge_graph_context_aware.py)
- Extract organization names FROM TEXT (not from filename)
- Link services mentioned in context
- NO document source inference
- NO organization-specific rules
- Result: **2 organizations, 1 relationship**
- **FAILED**: Even worse - can't even find the main Leeds organizations

### 3. **Framework + Metadata Approach** (build_knowledge_graph_framework.py)
- Framework-based universal queries (works for any org)
- Use ChromaDB metadata (source field) as CONTEXT
- Metadata tells LLM "this chunk is from which document"
- No document-specific rules, no hardcoding
- Result: **16 organizations, 53 LCH services, 88 explicit relationships**
- **WORKS**: Found all 3 Leeds organizations and their services

---

## Why Explicit and Context-Aware Failed

Both approaches tried to extract relationships WITHOUT using document context.

**Problem**: The documents don't explicitly say "X provides Y"
- Instead they have: sections like "Our Services" with service listings
- Services are listed in context of the organization
- Without knowing which organization owns that section, the LLM can't create the link

**Example from actual document**:
```
Leeds Community Healthcare NHS Trust has a commitment to providing...
Our services are organised into three business units:
  - Adult Services
  - Children and Families Services
  - Specialist Services
```

For the LLM to extract "Leeds Community Healthcare NHS Trust provides Adult Services", it needs context that this section belongs to LCH. That context comes from:
1. Document source metadata, OR
2. Explicit "X provides Y" statements (rare in documents)

---

## The Real Scalability Issue

Your concern was: **"I don't want to add organization-specific exceptions"**

This is about **two different things**:

### ❌ HARDCODING (What you want to avoid)
```python
# Organization-specific rules in code
if "LCH" in doc.source:
    extraction_rule = "Apply LCH-specific prompt"
if "LTHT" in doc.source:
    extraction_rule = "Apply LTHT-specific prompt"
if "LYPFT" in doc.source:
    extraction_rule = "Apply LYPFT-specific prompt"
```
**This doesn't scale** - Need code change for each new org

### ✓ USING METADATA (What we're actually doing)
```python
# The source metadata is ALREADY in ChromaDB for EVERY document
source = doc.metadata.get('source', 'unknown')  # Automatic, no hardcoding

# Include it as context for the LLM
context = f"[From: {source}]\n{doc.page_content}"

# Single universal prompt - LLM uses the context
response = llm.invoke(UNIVERSAL_PROMPT.format(text=context))
```
**This scales** - Works the same way for any organization

**Key difference**:
- Hardcoding = changing code for each org
- Metadata = using information that's automatically available

---

## Why Framework + Metadata IS Scalable

### How It Works (Universal Process)
1. **RAG**: Framework queries - same for all organizations
   - `"community health services"`
   - `"mental health services"`
   - NOT org-specific like `"LCH adult services"`

2. **Metadata**: Use document source automatically
   - `source = doc.metadata.get('source')`  ← Automatic, no hardcoding
   - Works for ANY document

3. **LLM Extraction**: Universal prompt
   - Single prompt for all organizations
   - Tells LLM "use document context to attribute services"
   - No org-specific rules in the prompt

4. **Result**: Scalable
   - New organization? Just add its documents to ChromaDB
   - Same extraction code runs automatically
   - No code changes needed

### What DOESN'T Scale (What We Want to Avoid)
```python
# BAD: Organization-specific queries
"Leeds Community adult services children families"  ← LCH-specific
"LYPFT mental health services offerings"  ← LYPFT-specific
"Leeds Teaching Hospitals cancer diagnostics"  ← LTHT-specific
```
**Problem**: Need different queries for each org

### What DOES Scale (What We're Doing)
```python
# GOOD: Framework-based universal queries
"community health services"
"mental health services"
"hospital cancer services"
"primary care services"
```
**Benefit**: Same queries work for ANY organization

---

## Test Results Summary

| Approach | Organizations | Services | Relationships | Works? |
|----------|---|---|---|---|
| Explicit-Only | 9 | 29 | 1 | ❌ No |
| Context-Aware | 2 | 18 | 1 | ❌ No |
| Framework + Metadata | 16 | 115 | 88 explicit | ✓ Yes |

---

## The Misconception About Metadata

**Your concern**: "I don't want to enhance for each organization"

**What you might have thought we were doing**:
- Manually reading each org's documents
- Writing organization-specific rules
- Hardcoding org names and patterns
- Needing code changes for new organizations

**What we're actually doing**:
- Using METADATA that's automatically in ChromaDB
- Single universal extraction approach
- No manual work per organization
- No code changes for new organizations

---

## Recommendation

**Use the Framework + Metadata Approach** because:

1. ✓ **Universal Framework Queries** - Same for all organizations
2. ✓ **Automatic Metadata Usage** - No hardcoding, just using available information
3. ✓ **Scalable** - New organizations work without code changes
4. ✓ **Effective** - Actually finds the services and relationships
5. ✓ **No Organization-Specific Exceptions** - Single approach for all

---

## How to Extend to New Organizations

If you add documents for a new organization (e.g., Sheffield Teaching Hospitals):

1. Add their documents to the data folder
2. Run the ingestion pipeline (creates ChromaDB entries)
3. Run `build_knowledge_graph_framework.py`
4. **No code changes needed**
5. Extraction works automatically

The metadata approach scales because:
- Framework queries work for any healthcare org
- ChromaDB metadata is automatic (no manual tagging needed)
- LLM prompt is universal (no org-specific rules)

---

## Conclusion

The **Framework + Metadata approach IS truly scalable** because it:
- Uses RAG with universal queries (not org-specific queries)
- Uses automatic metadata context (not hardcoded rules)
- Requires no code changes for new organizations
- Works the same way for any healthcare system

This is the approach already implemented in `build_knowledge_graph_framework.py`.

The confusion was about what "scalable" means in this context:
- **Not**: Having one approach per organization
- **Actually**: Having ONE universal approach + automatic context = works for all organizations
