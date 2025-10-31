# Web Lookup in Multi-Agent System - Analysis & Assessment

**Date:** October 31, 2025
**Status:** Functional but Limited

---

## Overview

Yes, your multi-agent system **does include web lookup**, but it's currently operating in **rule-based mode** rather than real web search. Let me break down what it is and whether it's adding value.

---

## Current Implementation

### How It Works

**Phase 1 of Wide-Then-Deep Analysis:**

```
Query Input
    ↓
WebLookupAgent.get_context(query)
    ├─ Analyzes query for keywords
    ├─ Identifies key themes (10-year plan, workforce, partnership, etc.)
    ├─ Returns hardcoded context based on theme matching
    ├─ Suggests national priorities
    ├─ Provides validation framework
    ↓
DocumentSelectorAgent (uses this context to filter documents)
```

### What WebLookupAgent Does

**File:** `analysis/multi_agent/web_lookup_agent.py`

**Methods:**
1. `get_context(query)` - Main method that returns external context
2. `_analyze_query_context(query)` - Rule-based keyword matching
3. `identify_key_themes(context)` - Extract major themes
4. `identify_priorities(context)` - Extract national priorities
5. `suggest_search_strategy(context)` - Recommend document tags

**Example Output for "10-year plan" query:**
```python
{
    "external_context": "The NHS 10-Year Plan (2024-2034) sets out strategic direction...",
    "key_themes": ["NHS 10-Year Plan for Neighbourhood Health"],
    "national_priorities": [
        "Prevention - shift to prevention and early intervention",
        "Integration - full integration of primary and community care",
        "Workforce - 25,000 additional clinical staff needed nationally",
        "Inequity - address health disparities across regions",
        "Innovation - adopt new models and technologies"
    ],
    "relevant_policies": [...],
    "validation_framework": {...}
}
```

---

## Value Added - Is It Working Well?

### ✅ What's Working Well

**1. Conceptual Framework**
- Correctly implements the "Wide-Then-Deep" principle
- Gets external context BEFORE local search
- Prevents narrow initial retrieval
- Good architectural decision

**2. Integration**
- Properly integrated into orchestrator
- Used to inform Document Selector (Phase 2)
- Output feeds downstream agents
- Clean separation of concerns

**3. Theme Detection**
- Recognizes major NHS strategic themes:
  - 10-year plan
  - Workforce challenges
  - Integration/partnerships
  - Health inequalities
  - Innovation
- Provides relevant context for each

**4. Strategic Grounding**
- Prevents purely local/document-driven analysis
- Anchors findings to national context
- Provides validation framework
- Good for healthcare strategic analysis

### ❌ Limitations

**1. Rule-Based, Not Real Web Search**
```python
# Current implementation (lines 71-76 of web_lookup_agent.py)
if "10-year" in query_lower or "10 year" in query_lower:
    context_data["key_themes"].append("NHS 10-Year Plan for Neighbourhood Health")
    # ... returns hardcoded context
```

**Issues:**
- Can't find NEW policy documents released after hardcoded date
- Can't search for unexpected themes
- Can't access real-time NHS England updates
- Brittle keyword matching (misses "ten year plan", "10yr", variants)

**2. Limited Scope**
- Only recognizes ~5 major themes
- Doesn't handle queries outside those themes
- Would fail on unexpected NHS policy areas

**3. Static Context**
- Hardcoded priorities from Oct 2024
- Won't reflect policy changes
- No ability to cite sources (where did this info come from?)

**4. No Real API Integration**
- No actual web search happening
- No connection to NHS England website
- No ability to cite sources
- Can't validate freshness of information

---

## Current vs. Potential

### Current State (Rule-Based)
```
Query: "How should LCH respond to 10-year plan?"
  ↓
WebLookupAgent matches "10-year" keyword
  ↓
Returns hardcoded context about NHS 10-Year Plan
  ↓
Document Selector uses this to filter documents
  ↓
Result: Better document selection for this query
```

### Potential State (Real Web Search)
```
Query: "How should LCH respond to the new NHS digital transformation initiative?"
  ↓
WebLookupAgent performs actual web search
  ↓
Finds official NHS England policy documents
  ↓
Extracts key priorities and themes
  ↓
Provides current, sourced context
  ↓
Document Selector uses real-time context
  ↓
Result: Relevant analysis even for new/unexpected topics
```

---

## Value Assessment

### For Covered Topics (10-year plan, workforce, partnerships)
**Rating: 7/10**

✅ **Pros:**
- Ensures analysis is grounded in national context
- Prevents pure document-driven narrowness
- Good document filtering based on themes
- Better synthesis quality

❌ **Cons:**
- Hardcoded context (could be outdated)
- No sources to cite
- Limited to 5 pre-defined themes

### For Uncovered Topics
**Rating: 2/10**

- Query about new NHS policy → Returns generic fallback
- Query about unexpected topic → Falls back to basic theme detection
- Results in mediocre analysis

---

## How It's Integrated Into Wide-Then-Deep

### Phase 1: Web Lookup
```
WebLookupAgent.get_context(query)
→ Returns: themes, priorities, context, validation framework
```

### Phase 2: Document Selection
```
DocumentSelectorAgent.select_documents(query, web_context)
→ Uses web_context to score documents
→ Prioritizes documents matching identified themes
→ Can filter more intelligently than query alone
```

### Phase 3: Evidence Retrieval
```
EvidenceAgent.search(query, selected_documents)
→ Searches within pre-filtered document set
→ Gets better results because set is curated
```

### Phase 4: Synthesis
```
SynthesisAgent.synthesize(query, evidence)
→ Creates long-form output
→ Grounded in national context (from Phase 1)
→ Better synthesis quality
```

---

## Recommendations

### Short Term (No Cost)
Keep web lookup as-is. It adds value for known topics (10-year plan, workforce) and doesn't break for unknown topics.

**ROI:** Good for current use cases
**Cost:** Free (already implemented)

### Medium Term (Moderate Cost)
Expand hardcoded themes to cover more NHS strategic areas:
- Long-term workforce plan
- Health inequalities initiatives
- Mental health strategy
- Elective care targets
- Social care integration

**Effort:** 1-2 hours to add 5-10 more themes
**ROI:** Better coverage without real API calls
**Cost:** Free

### Long Term (Higher Cost)
Integrate real web search API:

**Option A: Manual Search (Free)**
- Instead of WebLookupAgent, run manual web search
- Copy-paste findings into system
- Synthesize results
- **Cost:** 5-10 min per query
- **ROI:** Perfect freshness, cited sources

**Option B: Programmatic Search ($)**
- Use `WebSearch` tool in Claude SDK
- Or integrate Bing/Google Search API
- Automatic theme extraction with LLM
- **Cost:** $0.01-0.05 per query
- **ROI:** Automatic, always fresh, high quality
- **Implementation:** 2-3 hours of coding

---

## Current Stance in Architecture

**From WIDE_THEN_DEEP_ARCHITECTURE.md:**

> **PHASE 1: WebLookupAgent (External Context)**
> - Analyze query for NHS themes and priorities
> - Get national strategic context
> - Identify validation framework
> - **Current Implementation:** Rule-based (detects query keywords) → **Ready for API integration**

The architecture explicitly acknowledges this is a placeholder ready for real API integration.

---

## Quick Assessment Table

| Aspect | Status | Quality | Future |
|--------|--------|---------|--------|
| **Exists?** | ✅ Yes | - | - |
| **Integrated?** | ✅ Yes | - | - |
| **Adds Value?** | ✅ Partially | 7/10 for known topics | Can improve |
| **Real Web Search?** | ❌ No | Rule-based | Ready for upgrade |
| **Source Cited?** | ❌ No | Hardcoded | Needs upgrade |
| **Handles New Topics?** | ⚠️ Poorly | 2/10 | Needs expansion |
| **Working Well?** | ✅ For Current Use | Good enough | Room to improve |

---

## Summary

Your web lookup is:
- ✅ **Conceptually correct** - Good architectural decision to include it
- ✅ **Well integrated** - Feeds into document selection effectively
- ⚠️ **Rule-based** - Not real web search, just keyword matching
- ✅ **Adds value** - For topics it knows about (10-year plan, workforce)
- ❌ **Limited scope** - Only ~5 hardcoded themes
- 🚀 **Ready for upgrade** - Architecture designed for easy API integration

**Overall Assessment:** Working well for current use cases (NHS 10-year plan analysis), but would benefit from real web search integration for broader applicability and to handle novel policy areas.

---

**Recommendation:** Keep as-is for now (it's working), but consider real web search integration if you need to analyze novel NHS policy areas or want to ensure analysis is always grounded in current (not Oct 2024) policy context.
