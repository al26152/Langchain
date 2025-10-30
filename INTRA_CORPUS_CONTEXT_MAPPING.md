# Intra-Corpus Context Mapping
## The Missing Context Problem: What Your Docs Contain

**Date:** October 30, 2025
**Problem:** RAG retrieves chunks but misses the **conceptual relationships** between documents
**Solution:** Build a "Document Context Map" to understand what information is scattered across your corpus

---

## The Intra-Corpus Context Loss Problem

### What's Happening Now

Your corpus has **26 documents** but the system treats each chunk atomically:

```
Query: "What are the workforce challenges facing LCH?"

Current Retrieval:
├─ Chunk from LCH Annual Report: "5,024 staff, turnover 15%"
├─ Chunk from Workforce Strategy: "Need sophisticated assessment"
├─ Chunk from Demographics: "Growing elderly population = demand"
└─ Chunk from Staff Survey: "31% of staff experience stress"

Problem: These chunks are retrieved INDEPENDENTLY
- No understanding that they're all describing the SAME problem
- No linking: "Turnover 15% + stress 31% = retention crisis"
- No connection to solutions elsewhere in corpus
- No indication of which other docs have related info
```

### Why This Matters

Your documents contain **multiple perspectives on the same issue**, but the system can't connect them:

**Example: "Workforce Challenges"**

| Document | Perspective | What's Missing |
|----------|-------------|-----------------|
| LCH Annual Report | Turnover data, headcount | Link to WHY turnover is high |
| Staff Survey | Stress, workload, burnout | Link to organizational context |
| Workforce Strategy 2021-25 | Strategic response plan | Link to actual effectiveness |
| Demographics | Population demand drivers | Link to how demand affects staff |
| LTHT Annual Report | Comparative context | Link showing LTHT faces same issues |
| Healthy Leeds Plan | System-wide coordination | Link to integrated solution |
| NHS Planning Guidance | National strategy | Link to policy requirements |

**Current system retrieves these as isolated facts.**
**It doesn't recognize: "These 7 documents are all talking about the same workforce crisis from different angles."**

---

## The Document Network Your Corpus Contains

### Conceptual Relationships (Currently Hidden)

Your 26 documents form multiple overlapping networks:

#### Network 1: WORKFORCE & PEOPLE
```
Documents connected by "workforce challenges":
├─ LCH Annual Reports (2024-25, 2023-24) → Current state
├─ Workforce Strategy 2021-25 → Strategic response
├─ Staff Survey Data (2 reports) → Staff perspective
├─ LTHT Annual Report → Comparative context
├─ LYPFT Annual Report → Comparative context
├─ CIPD Reports (3) → Sector trends
├─ NHS Planning Guidance → Policy requirements
└─ Demographics 2024 → Demand drivers

Missing Connections:
- How staff stress (Survey) relates to organizational demand (Demographics)
- How sector trends (CIPD) compare to local reality (Surveys)
- How strategy (Workforce 2021-25) is being implemented (Annual Reports)
```

#### Network 2: HEALTH INEQUALITIES & EQUITY
```
Documents connected by "reducing health inequalities":
├─ LCH Trust Board Papers (Sept 2025) → Current priority
├─ Demographics 2024 → Context on which inequalities
├─ Healthy Leeds Plan → Local strategy
├─ NHS 10-Year Plan → National mandate
├─ LTHT People Priorities → Comparative approach
├─ Leeds Health & Wellbeing Strategy → System coordination
└─ NHS Productivity Update → Resource context

Missing Connections:
- Which specific inequalities does LCH focus on? (fragmented across docs)
- How does LCH's approach compare to LTHT? (never connected)
- What's the resource gap? (scattered between Productivity + Board papers)
```

#### Network 3: PARTNERSHIP & INTEGRATION
```
Documents connected by "integrated care/partnership":
├─ LCH Board Papers → LCH partnership strategy
├─ LTHT Annual Report → LTHT partnerships
├─ LYPFT Annual Report → LYPFT partnerships
├─ Healthy Leeds Plan → System partnerships
├─ NHS Planning Guidance → National integration model
├─ Medium-term Planning Framework → System coordination
└─ NHS Oversight Framework → Governance structure

Missing Connections:
- What are the actual partnership mechanisms? (not clearly articulated across docs)
- Where are partnership gaps? (not compared)
- How effective are current partnerships? (no evaluation)
```

#### Network 4: STRATEGIC DIRECTION & PRIORITIES
```
Documents connected by "strategic priorities":
├─ NHS 10-Year Plan → National priorities
├─ NHS Planning Guidance (Jan 2025) → Current guidance
├─ Healthy Leeds Plan → Local interpretation
├─ LCH Board Papers → LCH translation
├─ LTHT People Priorities → LTHT translation
├─ Workforce Strategy → People strategy
└─ Medium-term Planning Framework → Implementation plan

Missing Connections:
- How does each organization interpret national guidance? (not cross-referenced)
- Where are organizational priorities misaligned with national? (not analyzed)
- What's being implemented vs. what's aspirational? (not distinguished)
```

---

## What Information Lives Where

### Problem: Context Fragmentation

**Example: Understanding "Workforce Turnover" requires cross-document reading**

To understand WHY turnover is 15% and WHAT TO DO, you need:

| Question | Answer Location | Current Retrieval |
|----------|-----------------|-------------------|
| What's the turnover rate? | LCH Annual Report | ✅ Found |
| Why is turnover 15%? | Staff Survey (burnout, stress) + Demographics (demand) | ⚠️ Fragments retrieved separately |
| Is 15% high? | CIPD Reports (benchmark data) | ❌ Rarely connected |
| What's the strategy? | Workforce Strategy 2021-25 | ⚠️ Retrieved without context |
| Is it working? | Annual Reports show 2-year trend | ❌ No temporal analysis |
| What's NHS policy? | Planning Guidance + 10-year plan | ❌ Never linked to local reality |
| What are other trusts doing? | LTHT + LYPFT Annual Reports | ❌ Never used for benchmarking |

**Current system finds 1-2 of these. Should connect all 7 to create insight.**

---

## Solution: Document Context Mapping

### What is a Context Map?

A **pre-computed document relationship graph** that understands:

```
Document A: "LCH has 15% turnover"
Document B: "Workforce stress is 31%"
Document C: "NHS expects 25K new staff"

Current System: Treats as 3 separate facts
With Context Map: "These 3 facts describe WORKFORCE RETENTION CRISIS"

Document A: "National strategy prioritizes equity"
Document B: "LCH focuses on partnership"
Document C: "LTHT focuses on people"

Current System: Treats as 3 separate priorities
With Context Map: "All 3 are implementing SAME national policy differently"
```

### Implementation: Multi-Level Context Index

#### Level 1: Document Classification (Already Have)
```python
Document: "LCH Annual Report 2024-25.md"
Classification:
  - document_type: ORG_SPECIFIC
  - strategic_level: ORGANIZATION
  - organization: Leeds Community Healthcare NHS Trust
  - themes: [workforce, finance, service delivery]
```

#### Level 2: Key Concepts (Document Topics)
```python
Document: "LCH Annual Report 2024-25.md"
Key Concepts:
  - workforce: [turnover 15%, recruitment challenges, staff stress]
  - finance: [financial challenge, ICB contracts, budget constraints]
  - equity: [health inequalities, targeted deployment]
  - service: [5000 daily patients, community care, integration]
```

#### Level 3: Document Relationships (Missing)
```python
Relationships:
  "LCH Annual Report 2024-25"
    --DISCUSSES_SAME_TOPIC--> "Staff Survey Benchmark 2024"
    --PROVIDES_CONTEXT_FOR--> "Workforce Strategy 2021-25"
    --IMPLEMENTS--> "NHS Planning Guidance Jan 2025"
    --COMPARABLE_TO--> "LTHT Annual Report 2024-25"
    --UPDATES--> "LCH Annual Report 2023-24"
```

#### Level 4: Evidence Chains (Missing)
```python
Evidence Chain: "Workforce Retention Crisis"
├─ Problem Statement
│  ├─ "LCH has 15% turnover" (LCH Annual Report)
│  ├─ "Staff experience 31% stress" (Staff Survey)
│  ├─ "15% turnover is above CIPD benchmark" (CIPD Report)
│  └─ "Population demand is growing" (Demographics)
│
├─ Organizational Response
│  ├─ "Workforce Strategy focuses on sophisticated assessment" (Workforce 2021-25)
│  ├─ "LCH Board priority: increase partnership" (Board Papers)
│  └─ "NHS guidance requires 25K new staff" (Planning Guidance)
│
└─ Effectiveness Assessment
   ├─ "Limited progress 2021-2024" (Annual Report trend)
   ├─ "Similar challenges at LTHT/LYPFT" (Comparative reports)
   └─ "National challenge - not unique to Leeds" (NHS reports)
```

---

## Building the Context Map: Technical Approach

### Phase 1: Extract Document Summaries & Topics

```python
class DocumentContextBuilder:
    """
    Pre-process corpus to build context relationships.
    Run ONCE per corpus update, not per query.
    """

    def extract_document_summaries(self, doc_path: str) -> Dict:
        """
        For each document, extract:
        - 1-2 sentence summary
        - Key topics/themes (e.g., workforce, equity, finance)
        - Key facts/numbers (e.g., "5,024 staff", "15% turnover")
        - Document purpose (e.g., "report", "strategy", "guidance")
        """
        return {
            "doc_name": "LCH Annual Report 2024-25",
            "summary": "LCH served 5000+ patients daily with 5,024 staff, facing 15% turnover and health equity challenges",
            "topics": ["workforce", "finance", "equity", "service-delivery"],
            "key_facts": [
                ("turnover_rate", "15%"),
                ("staff_count", "5024"),
                ("daily_patients", "5000"),
                ("stress_level", "31%")
            ],
            "doc_type": "organizational_report",
            "org": "Leeds Community Healthcare NHS Trust",
            "year": 2024-2025
        }

    def identify_concept_groups(self) -> Dict:
        """
        Group documents by shared concepts.
        E.g., all documents discussing "workforce challenges"
        """
        return {
            "workforce_challenges": [
                "LCH Annual Report 2024-25",
                "LCH Staff Survey 2024",
                "Workforce Strategy 2021-25",
                "CIPD Health & Wellbeing 2025",
                "Demographics 2024",
                "LTHT Annual Report 2024-25",
                "LYPFT Annual Report 2024-25",
                "NHS Planning Guidance Jan 2025"
            ],
            "health_inequalities": [
                "LCH Board Papers Sept 2025",
                "Demographics 2024",
                "Healthy Leeds Plan",
                "NHS 10-Year Plan",
                "LTHT People Priorities"
            ],
            # ... more concept groups
        }

    def find_relationships(self, doc_a: str, doc_b: str) -> Optional[str]:
        """
        Determine if/how two documents are related.
        Returns relationship type or None.
        """
        relationships = {
            "SAME_TOPIC": ("LCH Annual 2024", "Staff Survey 2024"),
            "PROVIDES_CONTEXT": ("Demographics 2024", "Workforce Crisis"),
            "RESPONDS_TO": ("Workforce Strategy", "Staffing Crisis"),
            "IMPLEMENTS": ("LCH Board Papers", "NHS Planning Guidance"),
            "COMPARES": ("LCH Annual", "LTHT Annual"),
            "UPDATES": ("LCH Annual 2024-25", "LCH Annual 2023-24"),
            "BENCHMARKS": ("Staff Survey", "CIPD Benchmark")
        }
```

### Phase 2: Build Context Map (Pre-Query)

```python
def build_context_map(corpus_path: str) -> ContextMap:
    """
    Run ONCE per corpus update (not per query).
    Creates a graph of document relationships and concept linkages.
    """

    context_map = {
        "documents": {
            "LCH Annual Report 2024-25": {
                "summary": "...",
                "topics": ["workforce", "finance", "equity"],
                "key_facts": [...],
            },
            # ... 25 more documents
        },
        "concept_groups": {
            "workforce_challenges": [list of docs],
            "health_inequalities": [list of docs],
            # ... more concept groups
        },
        "relationships": [
            {
                "doc_a": "LCH Annual Report 2024-25",
                "doc_b": "Staff Survey 2024",
                "type": "SAME_TOPIC",
                "strength": 0.95  # 0-1 confidence
            },
            # ... hundreds of relationships
        ],
        "evidence_chains": {
            "workforce_retention_crisis": {
                "problem": [...],
                "response": [...],
                "effectiveness": [...]
            },
            # ... more evidence chains
        }
    }

    return context_map
```

### Phase 3: Use Context Map During Analysis

```python
class EnhancedEvidenceAgent:
    """
    Enhanced agent that uses context map to retrieve
    not just chunks, but conceptual relationships.
    """

    def retrieve_with_context(self, query: str, context_map: ContextMap):
        """
        When retrieving evidence:
        1. Find matching chunks (normal semantic search)
        2. Identify which concept group(s) apply
        3. Retrieve ALL documents in that concept group
        4. Include relationship information
        5. Surface evidence chains
        """

        # Step 1: Normal retrieval
        relevant_chunks = self.vectordb.search(query, k=30)

        # Step 2: Identify concept groups
        concepts = context_map.identify_concepts(query)
        # → ["workforce_challenges", "organizational_response"]

        # Step 3: Get all docs in those concepts
        all_related_docs = context_map.get_documents_by_concept(concepts)
        # → [LCH Annual, Staff Survey, Workforce Strategy, CIPD, ...]

        # Step 4: Include relationships
        relationships = context_map.get_relationships(relevant_chunks, all_related_docs)
        # → Shows how docs connect

        # Step 5: Surface evidence chains
        evidence_chain = context_map.get_evidence_chain("workforce_challenges")
        # → Problem + Response + Effectiveness assessment

        return {
            "direct_chunks": relevant_chunks,
            "concept_groups": concepts,
            "all_related_docs": all_related_docs,
            "relationships": relationships,
            "evidence_chain": evidence_chain
        }
```

### Phase 4: Synthesis with Context

```python
class ContextAwareSynthesisAgent:
    """
    Synthesize findings using full document context.
    """

    def synthesize_with_context(self,
                               query: str,
                               evidence: Dict,
                               context_map: ContextMap) -> str:
        """
        Generate answer that:
        - Draws from multiple concept groups
        - Shows document relationships
        - References evidence chains
        - Indicates where information is fragmented
        - Suggests missing connections
        """

        prompt = f"""
        User Question: {query}

        Direct Evidence (semantic search):
        {format_chunks(evidence['direct_chunks'])}

        Related Concept Groups:
        {format_concepts(evidence['concept_groups'])}

        All Related Documents (context map):
        {format_doc_list(evidence['all_related_docs'])}

        Document Relationships:
        {format_relationships(evidence['relationships'])}

        Evidence Chain:
        {format_evidence_chain(evidence['evidence_chain'])}

        Synthesis Instructions:
        1. Answer using direct evidence
        2. Use concept groups to add depth (e.g., "Multiple documents
           discuss this workforce challenge from different angles...")
        3. Reference document relationships (e.g., "The Annual Report
           documents the problem; the Workforce Strategy outlines the
           response; the Staff Survey assesses effectiveness")
        4. Highlight evidence chains (e.g., "This forms part of a larger
           workforce retention crisis: problem stated in X, strategy
           in Y, effectiveness measured in Z")
        5. Flag fragmentation (e.g., "This information is scattered
           across 7 documents; more integrated approach would be: ...")

        Generate comprehensive answer that shows deep corpus knowledge.
        """
```

---

## Example: How Context Map Would Work

### Query: "What is LCH's workforce strategy and how is it working?"

#### Without Context Map (Current):
```
Evidence Agent retrieves:
- "LCH workforce strategy emphasizes sophisticated assessment"
  → from Workforce Strategy 2021-25
- "LCH has 15% turnover"
  → from LCH Annual Report 2024-25

Synthesis: "LCH has a workforce strategy focused on assessment.
They have 15% turnover."

Quality: SURFACE-LEVEL (isolated facts, no coherence)
```

#### With Context Map (Enhanced):
```
Evidence Agent retrieves:
- Direct chunks: as above

Context Map provides:
- Concept Group: "workforce_challenges" includes:
  ✓ Workforce Strategy 2021-25 (strategy)
  ✓ LCH Annual Reports (implementation)
  ✓ Staff Survey (staff perspective)
  ✓ Demographics (demand drivers)
  ✓ CIPD Reports (sector benchmarks)
  ✓ NHS Planning Guidance (policy context)

Relationships:
- Workforce Strategy RESPONDS_TO Workforce Challenge
- LCH Annual IMPLEMENTS Workforce Strategy
- Staff Survey MEASURES effectiveness
- CIPD Report BENCHMARKS against sector
- NHS Guidance MANDATES national changes

Evidence Chain "Workforce Strategy Effectiveness":
├─ Problem: High turnover (15%), staff stress (31%), demand growing
├─ Response: Sophisticated assessment strategy (2021-25)
├─ Implementation: Board priority 2025, partnership focus
├─ Effectiveness: Limited progress 2021-2024, LTHT/LYPFT similar struggles
└─ Context: National shortage (25K) makes local success harder

Synthesis: "LCH's workforce strategy, outlined in 2021-25 framework,
emphasizes sophisticated assessment to address critical challenges:
15% turnover, 31% staff stress, and growing population demand.
However, implementation progress has been limited (2021-2024 period),
and the strategy now faces headwinds:
1. National shortage of 25K staff (NHS planning guidance)
2. Sector-wide turnover at 15% (CIPD benchmark - LCH is at sector avg)
3. Similar struggles at LTHT/LYPFT show systemic challenge

The board's 2025 pivot to partnership (Board Papers) suggests
recognition that individual trust strategies insufficient.
LCH is not behind - it's implementing a sound strategy in a
constrained national environment."

Quality: STRATEGIC-LEVEL (multi-dimensional, contextualized)
```

---

## Implementation Roadmap

### Phase 1: Build Context Map (1 week)
- [ ] Extract summaries for all 26 documents
- [ ] Identify key concepts in each document
- [ ] Extract key facts/numbers
- [ ] Identify document relationships
- [ ] Build evidence chains

### Phase 2: Integrate with Evidence Agent (1 week)
- [ ] Modify Evidence Agent to use context map
- [ ] Return not just chunks, but concept context
- [ ] Include relationship information
- [ ] Surface evidence chains

### Phase 3: Update Synthesis (1 week)
- [ ] Update Synthesis Agent to leverage context
- [ ] Generate multi-level answers
- [ ] Highlight document relationships
- [ ] Reference evidence chains

### Phase 4: Optimize & Iterate (1 week)
- [ ] Test on various queries
- [ ] Refine concept groupings
- [ ] Improve relationship detection
- [ ] Validate evidence chains

**Total: 4 weeks to solve intra-corpus context loss**

---

## What This Solves

| Problem | Current | With Context Map |
|---------|---------|------------------|
| "Missing related docs" | ❌ Isolated chunks | ✅ Related docs from concept groups |
| "No interconnection" | ❌ Separate facts | ✅ Relationships shown |
| "Flat answers" | ❌ Surface-level | ✅ Multi-dimensional |
| "No benchmarking" | ❌ Facts in vacuum | ✅ Compared across docs |
| "Shallow inference" | ❌ Obvious | ✅ Considers full context |
| "Missing context" | ❌ Chunks only | ✅ Evidence chains |

---

## Your 26 Documents: Hidden Value

Your corpus actually contains **far more insight** than currently retrieved.

**Example Strategic Networks Waiting to Be Connected:**

1. **Workforce Crisis Evidence Chain** (7 documents)
   - Problem: turnover + stress data
   - Response: strategy documents
   - Effectiveness: annual reports + survey trends

2. **Health Equity Story** (5 documents)
   - Challenge: demographics
   - Policy: NHS 10-year plan + planning guidance
   - Response: LCH/LTHT/LYPFT priorities
   - Implementation: board papers

3. **Partnership Evolution** (6 documents)
   - Current: individual trust strategies
   - Direction: Healthy Leeds Plan + Planning Framework
   - Coordination: Medium-term framework
   - Governance: Oversight framework

**With Context Map, these stories become visible.**

---

## Comparison: Web Lookup vs. Context Mapping

Both solve the "flat answer" problem but differently:

| Approach | Solves | Requires | Best For |
|----------|--------|----------|----------|
| **Web Lookup** | External context missing | Web access | National strategy alignment, policy context, benchmarking data |
| **Context Mapping** | Internal context missing | Document preprocessing | Connecting related docs, evidence chains, integrated understanding |
| **Both Together** | All context missing | Web + preprocessing | Strategic analysis with full internal + external context |

**Recommendation: Implement Context Mapping FIRST** (4 weeks, high value)
**Then Web Lookup** (4-5 weeks, adds external dimension)

---

## Conclusion

Your corpus is **rich with interconnected information**, but the RAG system treats each chunk as atomic.

A Context Map would:
- ✅ Connect related documents automatically
- ✅ Surface evidence chains across documents
- ✅ Enable multi-dimensional analysis
- ✅ Make inferences deeper and more strategic
- ✅ Show comparative analysis (org vs. org, local vs. national)

**This solves the "missing context" and "flat answers" problems for local knowledge.**

Combined with Web Lookup, you'd have:
- ✅ Local context (Context Map)
- ✅ External context (Web Lookup)
- ✅ Strategic depth (both together)

