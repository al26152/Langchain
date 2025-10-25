# RAG and Metadata Usage in Framework-Based Extraction

## Quick Answer
**YES - We ARE using both RAG and Metadata**, but we can strengthen the metadata usage.

---

## 1. How RAG is Being Used

### What is RAG?
RAG = **Retrieval-Augmented Generation**
- NOT context-stuffing all documents
- Semantic search to retrieve ONLY relevant chunks
- Pass relevant chunks + context to LLM

### Evidence in Code (build_knowledge_graph_framework.py, line 308)
```python
# Framework query (universal, not org-specific)
query = "community health services"

# RAG: Semantic search on ChromaDB
results = vectordb.similarity_search(query, k=10)

# This retrieves only the most relevant chunks, not all documents
```

### Framework Queries Used for RAG
Instead of hardcoded organization names, we use framework dimensions:
```python
FRAMEWORK_QUERIES = {
    "SERVICES": [
        "primary care secondary care services",
        "community health services",
        "mental health services",
        "cancer services oncology",
        "diagnostic imaging laboratory",
        ...
    ]
}
```

### Why This is RAG, Not Context-Stuffing
- Query: `"community health services"` searches ChromaDB semantically
- Returns chunks from documents that match this concept
- OpenAI embeddings find semantic similarity
- Pass only top 5-10 relevant chunks to LLM
- NOT passing all 29 documents

**Result**: Efficient, focused retrieval

---

## 2. How Metadata is Being Used

### Metadata Available in ChromaDB
Each chunk has metadata:
```json
{
  "source": "Leeds_Community_Annual-report_2024.md",
  "date": "2024-2025",
  "theme": "Annual Report",
  "other_metadata": "..."
}
```

### Evidence in Code (build_knowledge_graph_framework.py, lines 316-323)
```python
# Extract metadata from retrieved chunks
chunks_with_context = []
document_sources = set()

for doc in results[:5]:
    source = doc.metadata.get('source', 'unknown')  # <-- Get source
    document_sources.add(source)
    # Include source in context
    chunks_with_context.append(f"[From: {source}]\n{doc.page_content}")

# Build final context with metadata hints
context = "\n\n".join(chunks_with_context)
document_hint = f"\nDocument sources in this context: {', '.join(document_sources)}"
contextual_prompt = EXTRACTION_PROMPT.format(text=context + document_hint)
```

### What Gets Passed to LLM
```
[From: Leeds_Community_Annual-report_2024.md]
Community nursing services providing care in the home setting...

[From: Leeds_Teaching_Hospitals_Annual-Report_2024.md]
Cancer services offering diagnostic and treatment...

Document sources in this context: Leeds_Community_Annual-report_2024.md, Leeds_Teaching_Hospitals_Annual-Report_2024.md
```

### Extraction Prompt Metadata Guidance (lines 217-220)
```
5. USE DOCUMENT CONTEXT:
   - Document source tells you which organization owns/provides services
   - Services listed in that org's document = that org provides them
   - Look for pathways that connect multiple organizations
```

**Result**: LLM knows which document each chunk comes from

---

## 3. Current Strengths

✓ **RAG Implementation**
- Using semantic search with framework queries
- Retrieving relevant chunks, not all documents
- Efficient and focused

✓ **Metadata Extraction**
- Pulling source from ChromaDB metadata
- Including source in LLM context
- Telling LLM to use document context

✓ **Framework-Based Queries**
- Universal queries work for any organization
- No hardcoding of org names
- Scalable approach

---

## 4. How to Improve Metadata Usage (Optional Enhancement)

### Current Generic Guidance
```
"Document source tells you which organization owns/provides services"
```

### Proposed Explicit Mapping (Like v3)
Add specific mappings to the prompt:
```
4. CRITICAL - USE DOCUMENT CONTEXT:
   - If from "Leeds_Community_Annual-report" or "LCH" documents:
     → Services listed are provided by "Leeds Community Healthcare NHS Trust"

   - If from "LTHT" or "Teaching_Hospitals" documents:
     → Services listed are provided by "Leeds Teaching Hospitals NHS Trust"

   - If from "LYPFT" or "Partnership" documents:
     → Services listed are provided by "Leeds and York Partnership NHS Foundation Trust"

   - If from "Healthy_Leeds_Plan" or "integrated care" documents:
     → These are system-wide services, may be provided by multiple orgs
```

### Why Improve?
- More explicit = higher accuracy
- LLM doesn't have to infer organization from vague hints
- Matches how we know documents are structured

### Impact
- Could improve service attribution accuracy
- Would help with LYPFT's low explicit service count
- Makes extraction more deterministic

---

## 5. Flow Diagram: RAG + Metadata

```
1. Framework Query
   "community health services"
        |
        v
2. RAG Search on ChromaDB
   vectordb.similarity_search(query, k=10)
        |
        v
3. Retrieve Chunks with Metadata
   [chunk1, source: "Leeds_Community_*.md"]
   [chunk2, source: "LTHT_*.md"]
   [chunk3, source: "LYPFT_*.md"]
        |
        v
4. Build Context with Metadata
   "[From: Leeds_Community_*.md]\nContent...\n"
   "Document sources: Leeds_Community_*.md, LTHT_*.md"
        |
        v
5. LLM Extraction (With Context)
   "Extract entities knowing this is from LCH, LTHT, LYPFT docs"
        |
        v
6. Output
   Entities + Relationships properly attributed
```

---

## 6. Summary

| Aspect | Status | How |
|--------|--------|-----|
| **RAG Used?** | ✓ YES | ChromaDB semantic search with framework queries |
| **Metadata Extracted?** | ✓ YES | `doc.metadata.get('source')` from ChromaDB |
| **Metadata in Context?** | ✓ YES | `[From: source]` prefix on chunks |
| **Metadata Hints in Prompt?** | PARTIAL | Generic guidance, could be more explicit |
| **Framework Queries?** | ✓ YES | Universal queries, no org-specific code |
| **Scalable?** | ✓ YES | Same approach works for any organization |

---

## 7. Recommendation

### Current State
✓ Working well - RAG + metadata are being used effectively
✓ Framework-based approach is scalable
✓ Results show LCH: 53 services, LTHT: 9 services, LYPFT: 3 services

### Optional Enhancement
Could add explicit document-to-organization mappings in the extraction prompt for higher accuracy, especially for LYPFT which may have different documentation structure.

### Decision
- **Keep current approach** - It's working, RAG + metadata are in place
- **Only enhance if needed** - If LYPFT services need to be higher, add explicit mappings
