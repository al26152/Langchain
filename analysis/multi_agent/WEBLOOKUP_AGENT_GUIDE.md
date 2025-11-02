# WebLookupAgent - Dynamic Web Search + Evidence Extraction

**Date:** November 2, 2025
**Status:** Production Ready ✓
**File:** `analysis/multi_agent/web_lookup_agent.py`
**Enhancement:** ✨ Now extracts and returns structured web evidence items

---

## Overview

The **WebLookupAgent** is the **PRE-PHASE** of the multi-agent iterative RAG system. It provides **dynamic, current context AND evidence** about NHS and Leeds healthcare by searching the web in real-time.

### What It Does

1. **Analyzes the user's question** - Understands what they're asking about
2. **Formulates a smart search query** - Adds NHS/Leeds context intelligently (not forced)
3. **Searches the web** - Uses DuckDuckGo API to find current information
4. **Extracts structured context** - Uses Claude to pull out themes, priorities, and policies
5. **Extracts evidence items** ✨ **[NEW]** - Uses Claude to extract key evidence points from search results
6. **Returns combined output** - Provides context, priorities, and structured evidence items to downstream agents

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
    "web_evidence": [  # ✨ NEW - Structured evidence items
        {
            "content": "NHS England's 25K workforce target...",
            "detail": "Requires recruitment of 25,000 clinical staff nationally",
            "source": "NHS England",
            "relevance": "Provides national benchmark for workforce planning"
        },
        {
            "content": "Integration of community and mental health services...",
            "detail": "New guidance on partnership structures in 2025",
            "source": "NHSE Policy",
            "relevance": "Directly relevant to LCH partnership strategy"
        },
        ...
    ],
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

#### 3. `_extract_context_from_results(query, search_results, context_data)` - Context Extraction
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

#### 4. `_extract_evidence_from_results(query, search_results, context_data)` - Evidence Extraction ✨ **[NEW]**
Uses Claude to extract key evidence points from search results:

```python
# LLM Prompt:
"""
USER QUERY: What are workforce priorities for Leeds?

WEB SEARCH RESULTS:
[Search results text...]

Extract 3-5 key evidence points that directly address the query.
For each point, provide:
- The claim/finding
- Supporting detail or statistic
- Source indicator
- Relevance to query

Format as JSON:
[
  {
    "claim": "The key finding",
    "detail": "Supporting detail, statistics",
    "source_type": "Website name",
    "relevance": "How this addresses the query"
  },
  ...
]
"""

# Returns: Structured evidence items for Evidence Agent
```

**Why Separate Evidence Extraction?**
- Beyond context/themes, we need **actual evidence claims**
- Evidence items include specific findings, statistics, policies
- Each item is attributed to a source
- Can be merged with local evidence in Evidence Agent
- Provides external validation for local findings

#### 4. Graceful Degradation - No Fallback
If web search fails (rare), the system:
- Returns empty context (no misleading fallback themes)
- Proceeds with local evidence only
- No false signals or hardcoded defaults
- User sees clear warning: "[WARNING] Web search failed"

**Why no fallback?**
- Web is massive - unlikely to return zero results
- If search fails, local evidence still works fine
- No point injecting potentially irrelevant themes
- Keeps system simple and transparent

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

## Integration with Multi-Agent Pipeline

### PRE-PHASE Output → PHASE 1+ Input

```python
# PRE-PHASE: WebLookupAgent
context = web_lookup_agent.get_context(query)
# Returns: {
#   "key_themes": [...],
#   "national_priorities": [...],
#   "external_context": "...",
#   "web_evidence": [  # ✨ NEW - Structured evidence items
#     {"content": "...", "detail": "...", "source": "...", ...},
#     ...
#   ]
# }

# PHASE 1 (Iteration 1): EvidenceAgent
evidence = evidence_agent.search(
    query=query,
    iteration_num=1,
    web_evidence=context["web_evidence"]  # ✨ NEW - Pass web evidence to first iteration
)
# Evidence Agent:
# 1. Searches ChromaDB for local evidence
# 2. Merges web evidence into combined evidence list
# 3. Returns unified evidence with source attribution

# PHASE 2: CritiqueAgent
critique = critique_agent.critique(
    evidence=evidence,  # Contains both local + web evidence
    query=query
)

# PHASE 3: SynthesisAgent
report = synthesis_agent.synthesize(
    evidence=evidence,  # Includes web evidence with EXTERNAL_EVIDENCE type
    query=query,
    context=context  # Grounds synthesis in web context
)
# Synthesis Agent:
# 1. Generates answer using all evidence sources
# 2. Distinguishes local findings from external validation
# 3. Attributes claims to appropriate sources
```

**Flow Diagram:**
```
Query
  ↓
WebLookupAgent (PRE-PHASE)
  ├─ Web search
  ├─ Extract context (themes, priorities)
  ├─ Extract evidence (claims, details, sources)
  └─ Return: context + web_evidence
       ↓
   EvidenceAgent (PHASE 1, Iter 1)
     ├─ Search ChromaDB
     ├─ Merge web_evidence
     └─ Return: combined evidence
          ↓
      CritiqueAgent (PHASE 2)
        └─ Analyze combined evidence
             ↓
         SynthesisAgent (PHASE 3)
           └─ Generate answer with full attribution
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

### Web Search Fails (Rare)
```
→ Warning logged: "[WARNING] Web search failed: {error}"
→ System continues with local evidence only
→ No fallback themes injected
→ User sees warning in console
```

### Search Returns No Results (Extremely Rare)
```
→ Warning logged: "[WARNING] Web search returned no results"
→ web_evidence = [] (empty)
→ key_themes = [] (empty)
→ System proceeds with local evidence only
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
| **Graceful Degradation** | Yes - continues with local evidence only if web fails |
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
| "[WARNING] Web search failed" | Network/API issue (rare); system proceeds with local evidence |
| "No themes or evidence extracted" | Query too specific or niche; system continues with local search |
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
