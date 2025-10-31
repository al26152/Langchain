# WebLookupAgent - Dynamic Web Search Implementation

**Date:** November 1, 2025
**Status:** Production Ready ✓
**File:** `analysis/multi_agent/web_lookup_agent.py`

---

## Overview

The **WebLookupAgent** is Phase 1 of the Wide-Then-Deep 4-phase analysis architecture. It provides **dynamic, current context** about NHS and Leeds healthcare by searching the web in real-time, rather than relying on hardcoded rules.

### What It Does

1. **Analyzes the user's question** - Understands what they're asking about
2. **Formulates a smart search query** - Adds NHS/Leeds context intelligently (not forced)
3. **Searches the web** - Uses DuckDuckGo API to find current information
4. **Extracts structured context** - Uses Claude to pull out themes, priorities, and policies
5. **Returns framed context** - Provides structured output for document selection phase

### Why This Matters

**Before (Hardcoded):**
- Limited to 5 pre-defined themes
- Context frozen at October 2024
- Couldn't handle novel policy questions
- Brittle keyword matching

**After (Dynamic Web Search):**
- Handles ANY NHS/Leeds healthcare topic
- Always current information
- Gracefully handles unknowns
- Intelligent query formulation

---

## How It Works

### Architecture

```
User Query
    ↓
_formulate_search_query()
├─ Check if Leeds/NHS already mentioned
├─ Detect national vs local scope
└─ Build intelligent search query
    ↓
Web Search (DuckDuckGo)
    ├─ Query: "What are workforce priorities for Leeds? NHS"
    └─ Returns: Current articles, policies, news
    ↓
_extract_context_from_results()
├─ Send results + query to Claude
├─ Request: Extract themes, priorities, policies
└─ Parse: Return structured JSON
    ↓
Return to Orchestrator
└─ Input to Phase 2 (Document Selection)
```

### Key Methods

#### 1. `get_context(query)` - Main Entry Point
```python
agent = WebLookupAgent()
context = agent.get_context("What are workforce priorities for Leeds Community Healthcare?")

# Returns:
{
    "query": "What are workforce priorities for Leeds Community Healthcare?",
    "key_themes": ["Workforce wellbeing", "Collaboration", "Community engagement"],
    "national_priorities": ["Priority 1", "Priority 2", ...],
    "relevant_policies": ["Policy A", "Policy B"],
    "external_context": "Summary of web findings...",
    "validation_framework": {...},
    "sources": ["Web search - current results"]
}
```

#### 2. `_formulate_search_query(query)` - Smart Query Building
Intelligently adds context without forcing restrictions:

```python
# Examples:
"What are workforce priorities?"
  → "What are workforce priorities? NHS Leeds"
  (Adds Leeds because healthcare-focused and not already mentioned)

"What is national NHS policy on X?"
  → "What is national NHS policy on X? NHS"
  (No Leeds added - clearly national scope)

"How does LCH respond to 10-year plan?"
  → "How does LCH respond to 10-year plan? NHS"
  (Leeds already implied by LCH mention)
```

**Detection Logic:**
- Checks if Leeds/LCH/LTHT/West Yorkshire mentioned
- Checks if question is clearly national policy
- Only adds Leeds if healthcare-focused AND location not mentioned
- Always adds NHS (healthcare domain marker)

#### 3. `_extract_context_from_results(query, search_results, context_data)` - LLM Extraction
Uses Claude to extract themes and priorities from search results:

```python
# LLM Prompt:
"""
USER QUERY: What are workforce priorities for Leeds?

WEB SEARCH RESULTS:
[Search results text...]

Extract:
1. Key NHS/healthcare themes (2-4)
2. Current priorities/initiatives (3-5)
3. Relevant policies (2-4)
4. Summary (2-3 sentences)
"""

# Returns: JSON with themes, priorities, policies, summary
```

**Why LLM Extraction?**
- Search results are unstructured
- Need to extract only relevant information
- Themes emerge from context, not keywords
- Synthesis required for clarity

#### 4. `_get_fallback_context(query)` - Graceful Degradation
If web search fails, returns basic NHS/Leeds context:

```python
{
    "external_context": "Web search unavailable. Providing baseline NHS/Leeds healthcare context...",
    "key_themes": ["NHS Strategy", "Community Partnership", "Health Equity"],
    "national_priorities": [
        "Workforce recruitment and retention",
        "Health and social care integration",
        "Health inequalities reduction"
    ]
}
```

---

## Usage Examples

### Example 1: Workforce Planning Query

**Query:** "What are the current workforce priorities for Leeds Community Healthcare?"

**Process:**
1. `_formulate_search_query()` detects healthcare-focused + Leeds not mentioned
   - Creates: "What are the current workforce priorities for Leeds Community Healthcare? NHS"
2. Web search finds:
   - NHS England workforce strategy documents
   - West Yorkshire ICS workforce plans
   - LCH recent announcements
3. LLM extracts:
   - Themes: Workforce wellbeing, Retention, Community nursing
   - Priorities: Recruitment targets, Flexible working, Career development
   - Policies: NHS 10-Year Plan, Long-term workforce plan
4. Returns structured context to Document Selector

**Output Used By:**
- Document Selector prioritizes workforce/partnership/strategy documents
- Evidence Agent searches within those documents
- Synthesis produces workforce-focused analysis

### Example 2: National Policy Query

**Query:** "How does NHS national discharge policy affect care pathways?"

**Process:**
1. `_formulate_search_query()` detects national scope
   - Creates: "How does NHS national discharge policy affect care pathways? NHS"
   - Does NOT add Leeds (question is about national policy)
2. Web search finds:
   - NHS England discharge guidance
   - NHSE policy documents
   - Healthcare system reports
3. LLM extracts:
   - Themes: Discharge planning, Care coordination, Policy compliance
   - Priorities: Same-day decisions, Partnership working, Patient choice
   - Policies: Current discharge standards, System guidance
4. Returns national context for analysis

**Output Used By:**
- Document Selector balances national + local documents
- Ensures analysis grounds in official policy
- Connects local implementation to national directives

### Example 3: Unknown/Novel Topic

**Query:** "What is the latest on NHS digital twin technology?"

**Process:**
1. `_formulate_search_query()` identifies unusual query
   - Creates: "What is the latest on NHS digital twin technology? NHS"
2. Web search finds:
   - Limited results (emerging topic)
   - Few NHS-specific results
3. LLM extracts:
   - Themes: Innovation, Digital transformation, Technology
   - Priorities: Sparse (few results)
   - Summary: "Web search found limited NHS-specific context on this emerging topic"
4. Returns minimal context gracefully

**Output Used By:**
- Document Selector works with generic innovation themes
- Evidence Agent expands search scope if needed
- Analysis acknowledges limited national context

---

## Integration with Wide-Then-Deep Pipeline

### Phase 1 Output → Phase 2 Input

```python
# Phase 1: WebLookupAgent
context = web_lookup_agent.get_context(query)
# Returns: themes, priorities, policies, validation_framework

# Phase 2: DocumentSelectorAgent
selected_docs = doc_selector.select_documents(
    query=query,
    web_context=context  # ← Uses web context to score documents
)
# Scores documents using identified themes + metadata tags

# Phase 3: EvidenceAgent
evidence = evidence_agent.search(
    query=query,
    selected_documents=selected_docs  # ← Searches within curated set
)

# Phase 4: SynthesisAgent
report = synthesis_agent.synthesize(
    query=query,
    evidence=evidence,
    context=context  # ← Grounds synthesis in web context
)
```

---

## Configuration & Tuning

### Default Behavior

```python
agent = WebLookupAgent()
# Uses gpt-4o-mini (faster, cheaper)
# Temperature: 0.3 (consistent extraction)
# Extraction prompt focuses on themes/priorities/policies
```

### Custom Configuration

```python
from langchain_openai import ChatOpenAI

custom_llm = ChatOpenAI(
    model="gpt-4-turbo",
    temperature=0.2
)

agent = WebLookupAgent(llm=custom_llm)
```

### Adjusting Query Formulation

Edit `_formulate_search_query()` to:
- Change geographic scope logic
- Add domain keywords
- Adjust NHS/healthcare detection

```python
# Example: Always add NHS region
def _formulate_search_query(self, user_query):
    query_lower = user_query.lower()
    search_parts = [user_query, "NHS", "West Yorkshire healthcare"]
    # ... rest of logic
    return " ".join(search_parts)
```

---

## Error Handling

### Web Search Fails
```
→ `_get_fallback_context()` returns baseline NHS context
→ System continues with generic context
→ User sees notice: "Web search unavailable..."
```

### Search Returns No Results
```
→ Minimal context returned: "No specific results found"
→ System continues with sparse context
→ Document selection uses query + generic themes
```

### LLM Extraction Fails
```
→ Falls back to parsing raw search results
→ Returns context_data with best-effort extraction
→ System continues (graceful degradation)
```

---

## Testing

### Basic Test

```python
from analysis.multi_agent.web_lookup_agent import WebLookupAgent
from dotenv import load_dotenv
load_dotenv('.env')

agent = WebLookupAgent()

query = "What are workforce priorities for Leeds Community Healthcare?"
context = agent.get_context(query)

print(f"Themes: {context['key_themes']}")
print(f"Priorities: {context['national_priorities']}")
print(f"Context: {context['external_context'][:200]}...")
```

### Test with Multiple Queries

```python
test_queries = [
    "What are workforce priorities for Leeds?",
    "How does NHS national discharge policy affect care?",
    "What partnerships should LCH develop?",
    "Unknown emerging technology X"
]

for q in test_queries:
    print(f"\nQuery: {q}")
    context = agent.get_context(q)
    print(f"Themes found: {len(context['key_themes'])}")
    print(f"Priorities: {len(context['national_priorities'])}")
```

---

## Performance Characteristics

| Aspect | Value |
|--------|-------|
| **Web Search Time** | 1-3 seconds |
| **LLM Extraction Time** | 2-5 seconds |
| **Total Phase 1 Time** | 3-8 seconds |
| **API Cost Per Query** | ~$0.02-0.05 |
| **Graceful Degradation** | Yes - fallback to baseline context |
| **Internet Required** | Yes - for web search |
| **Cache Friendly** | Yes - could be cached across similar queries |

---

## Advantages of Dynamic Implementation

✓ **Always Current** - Not limited to hardcoded Oct 2024 data
✓ **Flexible** - Handles any NHS/Leeds healthcare topic
✓ **Intelligent** - Doesn't force geographic scope
✓ **Transparent** - Shows sources of information
✓ **Graceful** - Continues working if web unavailable
✓ **Maintainable** - No manual updates when NHS policy changes

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Web search unavailable" | Check internet connection; may be DuckDuckGo rate limit |
| "No themes extracted" | Query too specific or niche; fallback context used |
| "Wrong context returned" | Check `_formulate_search_query()` logic; may not match query intent |
| "Slow performance" | DuckDuckGo search slow; consider caching common queries |
| "Missing Leeds context" | Query may not trigger Leeds detection; check query keywords |

---

## Future Improvements

### Phase 1.1: Caching
- Cache web search results for similar queries
- Reduce API cost and latency

### Phase 1.2: Query Optimization
- Use query expansion before search
- Search for related terms if primary search sparse

### Phase 1.3: Multi-Source Search
- Search NHS England official docs directly
- Integrate with news APIs for recent developments
- Add trust scoring (weight official sources higher)

### Phase 1.4: Semantic Parsing
- Extract more sophisticated relationships from search results
- Identify contradictions or evolving policy
- Track policy change timeline

---

## References

- **Wide-Then-Deep Architecture:** `WIDE_THEN_DEEP_ARCHITECTURE.md`
- **Orchestrator:** `analysis/multi_agent/orchestrator.py`
- **Document Selector:** `analysis/multi_agent/document_selector_agent.py`
- **DuckDuckGo API:** Uses LangChain's `DuckDuckGoSearchRun()`

---

**Last Updated:** November 1, 2025
**Status:** Production Ready ✓
**Next Review:** When new NHS policy released or query patterns indicate need for adjustment
