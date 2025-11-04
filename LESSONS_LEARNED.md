# Lessons Learned: Hub-Based vs Pipeline Architecture

**Date:** 2025-11-04
**Journey:** Testing whether a multi-agent hub architecture outperforms a simple sequential pipeline
**Conclusion:** The simple pipeline wins. Complexity introduced bugs that made the system worse.

---

## Executive Summary

We designed an elaborate hub-based multi-agent system to enable dynamic agent coordination and gap-driven document expansion. Testing revealed:

- **Pipeline (simple):** 12 sources, 39 chunks, 70% confidence, specific findings ✓
- **Hub (complex):** 14 sources, 38 chunks, 70% confidence, generic findings + corruption ✗

**The pipeline outperformed the hub despite being 10x simpler.**

This investigation exposed a fundamental truth: **Design systems against the specific problem you're solving, not hypothetical future problems.**

---

## The System We Built

### Hub-Based Architecture (What We Tried)

```
WebLookupAgent
     ↓
  AgentHub (central message bus + shared state)
     ↓
Evidence Agent → Critique Agent → Request for gaps
                     ↓
         DocumentSelectorAgent._expand_selection()
         KnowledgeGraphAgent._find_gaps_request()
         WebLookupAgent._search_for_gaps()
     ↓
Synthesis Agent → Answer
```

**Features:**
- Bidirectional agent communication via hub
- Real handlers that process inter-agent requests
- Dynamic document expansion based on identified gaps
- Shared state management across agents
- Communication logging and audit trail

**Code complexity:** ~2,000 lines of hub infrastructure

### Pipeline Architecture (What Actually Works)

```
WebLookupAgent (get context + web evidence)
     ↓
Evidence Agent (search documents)
     ↓
Critique Agent (analyze quality)
     ↓
Synthesis Agent (generate answer)
```

**Features:**
- Sequential flow
- Each agent processes output from previous
- No inter-agent communication
- No expansion logic
- Straightforward iteration loop

**Code complexity:** ~200 lines of orchestration

---

## What We Tested

### Test Question (Version 3 - Most Complex)

```
"Building on the national 10-year health plan, what are the specific
barriers and enablers for LCH, LTHT, and Leeds-based primary care
organisations to co-develop a neighbourhood workforce ecosystem?
How can we address health inequalities while managing financial
constraints, and what partnerships or training programs are needed?"
```

This was carefully designed to:
- Reference multiple organizations (LCH, LTHT, primary care)
- Include multiple dimensions (barriers, enablers, equity, finance, training)
- Span strategic levels (national, regional, organizational)
- Be complex enough to expose real differences

### Comparison Metrics

| Metric | Hub | Pipeline | Winner |
|--------|-----|----------|--------|
| **Sources Retrieved** | 14 | 12 | Pipeline |
| **Evidence Chunks** | 38 | 39 | Pipeline |
| **Confidence Score** | 70% | 70% | Tie |
| **Quality Rating** | GOOD | GOOD | Tie |
| **Web Evidence Extracted** | 0 items | 3 items | Pipeline +3 |
| **Iterations** | 2 | 2 | Tie |
| **Entity Name Corruption** | YES | NO | Pipeline |
| **Finding Specificity** | Generic | Specific | Pipeline |
| **Relevance to Question** | Off-topic | On-topic | Pipeline |

### Output Quality Comparison

**Hub Finding 5 (Generic, Off-Topic):**
```
**Population Health Management**

[SYNTHESIZED] Leeds Community Healthcare NHS Trust and its partners
are employing population health management approaches to design
interventions that address the diverse needs of Leeds residents...
```
→ Doesn't address barriers/enablers/partnerships question

**Pipeline Finding 5 (Specific, On-Topic):**
```
**Partnerships as Strategic Enablers**

Strategic partnerships are essential for overcoming barriers and
enhancing workforce capabilities. Leeds Community Healthcare NHS Trust's
involvement in the Leeds Health and Care Partnership...
```
→ Directly addresses the question

---

## Root Causes: Why Hub Failed

### Bug #1: Missing Handler Parameters

**Location:** orchestrator.py:621-631

What hub sends to handler:
```python
params={
    "gaps": high_priority_gaps,
    "query": query,
    "iteration": iteration_num,
}
```

What handler expects:
```python
params={
    "current_selection": [...],     # ← MISSING
    "gaps": [...],
    "expansion_size": 10,           # ← MISSING
    "query": ...,
}
```

**Impact:** Handler doesn't know which documents are already selected, so it scores all 53 documents and returns whatever ranks highest, which often overlaps with existing evidence.

### Bug #2: Web Evidence Lost

**Location:** orchestrator.py:182-190 (hub) vs orchestrator.py:475-483 (pipeline)

Hub code:
```python
web_context = self.web_lookup_agent.get_context(query)
# Gets web_context, stores in hub.shared_state
# But then doesn't pass it to evidence_agent.search()
```

Pipeline code:
```python
web_context = self.web_lookup_agent.get_context(query)
web_evidence = web_context.get("web_evidence", [])
evidence_result = self.evidence_agent.search(
    web_evidence=web_evidence if iteration_num == 1 else None,  # ← Properly passed
)
```

**Impact:** Hub extracted 3 web evidence items, never used them. Pipeline used all 3.

### Bug #3: Synthesis Confused by Extra Documents

This isn't a code bug, but an architectural one:
- Hub adds 2 extra documents (14 vs 12)
- Synthesis receives more context
- LLM generates lower-quality, more generic findings
- Entity names get corrupted as LLM struggles with larger context

**This suggests synthesis quality has a "Goldilocks zone"** - too few documents = incomplete, too many = confusing.

---

## Why Complexity Introduced These Bugs

### The Hub Added Layers of Indirection

```
Original problem: "Synthesize evidence into findings"

Hub solution path:
1. DetectGaps() in Critique
2. SendMessage() to hub
3. Hub routes to DocumentSelector
4. DocumentSelector.handle_request()
5. DocumentSelector._expand_selection()
6. Return results
7. ???
8. Use expanded docs in synthesis

Pipeline solution path:
1. Retrieve evidence
2. Synthesize
```

**Each layer is a place to:**
- Lose information (current_selection parameter)
- Lose configuration (expansion_size parameter)
- Lose coordination (web_evidence integration)
- Introduce bugs (parameter mismatches)

### More Components = More Failures

| Component | Potential Failure Modes |
|-----------|------------------------|
| AgentHub | Message routing, state management, communication logging |
| DocumentSelector handler | Parameter passing, selection logic, ranking bias |
| KnowledgeGraph handler | Gap detection, relationship inference |
| WebLookup handler | Search failures, result formatting |
| Orchestrator | State coordination, handler invocation |
| **Pipeline** | None (linear flow) |

---

## Key Insights

### 1. "Logic Suggests It Would Work, Yet It Doesn't"

The hub's logic is sound:
- ✓ Identify gaps
- ✓ Request document expansion
- ✓ Get additional evidence
- ✓ Use in synthesis

But in practice:
- ✗ Wrong parameters passed to handlers
- ✗ Expanded docs aren't better, are worse
- ✗ Synthesis quality degrades with more documents
- ✗ Result: overcomplicated system producing worse outputs

**Lesson:** Sound architecture + implementation bugs = worse than simple working system

### 2. Design Against Your Specific Problem

Hub was designed to solve:
> "How can autonomous agents dynamically coordinate to improve analysis?"

Your actual problem:
> "How do I synthesize evidence into workforce strategy findings for LCH?"

These are different problems. Hub is general-purpose infrastructure for a specific-purpose task.

### 3. Complexity Has a Cost

Hub cost:
- 2,000+ lines of infrastructure code
- Multiple layers of indirection
- Parameter passing complexity
- State management overhead
- Debugging difficulty (what breaks where?)

Pipeline benefit:
- 200 lines of orchestration
- Direct data flow
- Obvious parameter passing
- Simple state (just evidence list)
- Easy to debug (linear execution)

**The complexity tax outweighed any architectural benefits.**

### 4. YAGNI is Real

We built the hub anticipating:
- "What if we need more complex questions?" → We did, it broke
- "What if agents need to coordinate?" → They don't
- "What if we need dynamic expansion?" → It made things worse

None of these "what ifs" improved the system. They complicated it.

### 5. Measurements Beat Theory

Theoretical prediction (before testing):
> "Hub should win because it can dynamically expand evidence"

Actual results:
> "Pipeline wins because it avoids the complexity bugs"

We had to measure to know. Our intuitions were wrong.

---

## Recommendations

### For This Project

**Use the pipeline.** It works, it's simple, it's debuggable.

If you want to revisit hub architecture later:
1. Only after you prove you need inter-agent coordination
2. Only if simple approaches fail
3. Start minimal: one handler, one message type, prove the value

### For Future Projects

**Remember these principles:**

1. **Start simple, add complexity only when needed**
   - Pipeline now, hub only if you hit limits
   - Measure performance before and after changes

2. **Design for your actual problem, not hypothetical ones**
   - What documents do you have? (53, not thousands)
   - How complex are queries? (1 question at a time, not real-time systems)
   - What's your deployment model? (batch analysis, not interactive)

3. **Favor simplicity in system design**
   - Fewer moving parts = fewer bugs
   - Obvious code > clever code
   - Linear flow > distributed coordination

4. **Test against reality early**
   - Don't assume complex = better
   - Measure actual output quality, not just metrics
   - Compare solutions with same test cases

5. **Iteration beats prediction**
   - You can't know what will work until you test it
   - This investigation proved that
   - Build testable systems that let you validate assumptions

---

## What We Learned About Our Specific System

### Evidence Synthesis Has Optimal Document Count

- Too few (5-8): Incomplete findings
- Optimal (10-15): Specific, focused findings
- Too many (20+): Generic, unfocused findings

**Implication:** Document expansion should be selective, not automatic.

### Web Context Matters

Pipeline got 3 web evidence items and produced better findings. Hub never used them.

**Implication:** Integration of external context is valuable, but only if properly implemented.

### Entity Name Corruption Indicates Synthesis Stress

Hub's entity corruption wasn't a bug in normalize_text(), it was the LLM struggling with too much context.

**Implication:** If synthesis is corrupting output, the problem might be upstream (too much evidence).

### Gap Detection Works, Gap Expansion Doesn't

Hub successfully detected gaps (2 find_gaps messages). But expanding on those gaps (2 extra documents) made output worse.

**Implication:** Gap detection alone doesn't equal better analysis. Need smarter expansion logic.

---

## Files Changed / Created

- `ANALYSIS_HUB_BASED_FINDINGS_20251104_064828.md` - Hub output
- `ANALYSIS_PIPELINE_FINDINGS_20251104_064828.md` - Pipeline output
- `ANALYSIS_HUB_REPORT_20251104_064828.md` - Full hub report
- `test_strategic_question.py` - Modified to save both outputs
- `LESSONS_LEARNED.md` - This file

---

## Conclusion

We didn't fail to implement the hub correctly. We **correctly identified that the hub solves the wrong problem**.

The right lesson isn't "hub was a bad idea in general" (it could be useful for other problems). The right lesson is: **"Build what you need, measure it, don't build what you might need."**

This investigation cost us one evening and revealed that months of hub development might not be worth it for this use case. That's exactly when you want to catch it.

---

## Next Steps

1. ✓ Archive hub code (keep on feature branch, don't merge)
2. ✓ Use pipeline as primary approach
3. ✓ Focus on improving synthesis quality (not document quantity)
4. ✓ Revisit hub only if future requirements demand agent coordination

**Simple systems that work beat complex systems that theoretically should work.**

