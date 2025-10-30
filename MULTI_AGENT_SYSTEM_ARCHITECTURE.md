# Multi-Agent Strategic Analysis System: Architecture Documentation

**Document Purpose**: Detailed technical explanation of how the multi-agent RAG system works, including manual hardcoding patterns, knowledge graph usage, and context stuffing mechanisms.

**Date**: 2025-10-30
**System Version**: Current implementation with ranking-based retrieval

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Multi-Agent Architecture](#2-multi-agent-architecture)
3. [RAG (Retrieval-Augmented Generation) Implementation](#3-rag-retrieval-augmented-generation-implementation)
4. [Query Expansion Pipeline](#4-query-expansion-pipeline)
5. [Knowledge Graph Integration](#5-knowledge-graph-integration)
6. [Context Stuffing Mechanisms](#6-context-stuffing-mechanisms)
7. [Manual Hardcoding Patterns](#7-manual-hardcoding-patterns)
8. [Document Ranking and Affinity System](#8-document-ranking-and-affinity-system)
9. [Iterative Refinement Loop](#9-iterative-refinement-loop)
10. [Limitations and Current Issues](#10-limitations-and-current-issues)

---

## 1. System Overview

### High-Level Architecture

The system implements an **iterative multi-agent RAG architecture** designed to answer strategic questions about healthcare organizations by retrieving evidence from a ChromaDB vector store and synthesizing insights through multiple LLM agents.

**Core Components**:
- **ChromaDB Vector Store**: Contains ~1600+ document chunks with embeddings
- **Entity Resolution System**: Maps organization aliases to canonical names
- **Knowledge Graph**: JSON-based entity relationship network
- **Three LLM Agents**: Evidence Agent, Critique Agent, Synthesis Agent
- **Orchestrator**: Controls iteration loop and agent coordination

**Data Flow**:
```
User Query
    ↓
Query Expansion (4 steps)
    ↓
Vector Semantic Search (ChromaDB)
    ↓
Document Ranking (3-tier affinity system)
    ↓
Evidence Agent → Critique Agent → [Continue?] → Synthesis Agent
    ↑_______________|
    (Iteration Loop)
```

---

## 2. Multi-Agent Architecture

### Agent Roles

#### 2.1 Evidence Agent (`evidence_agent.py`)

**Purpose**: Retrieve relevant evidence from ChromaDB with comprehensive coverage

**Key Responsibilities**:
- Expand queries using entity resolution and knowledge graph
- Perform semantic vector search against ChromaDB
- Rank retrieved documents by organization affinity
- Tag documents by relevance (PRIMARY/STRATEGIC/GENERAL)
- Track source diversity and coverage metrics

**Input**:
- `query`: User's strategic question
- `iteration_num`: Current iteration number
- `previous_gaps`: List of gaps from previous critique
- `k`: Number of chunks to retrieve (default: 30)

**Output**:
```python
{
    "query": str,
    "expanded_query": str,
    "results": List[Dict],  # Retrieved chunks
    "metadata_summary": Dict,  # Coverage stats
    "unique_sources": int,
    "unique_organizations": int,
    "date_range": str,
    "iteration_num": int
}
```

**Critical Method**: `search(query, iteration_num, previous_gaps, k)`

---

#### 2.2 Critique Agent (`critique_agent.py`)

**Purpose**: Analyze evidence quality and identify gaps requiring additional retrieval

**Key Responsibilities**:
- Calculate confidence scores based on source diversity
- Detect convergence (repeated evidence across iterations)
- Identify gaps: coverage, source diversity, recency, data quality
- Determine overall quality rating (EXCELLENT/GOOD/ADEQUATE/POOR)
- Decide whether to continue iterating

**Input**:
- `evidence_result`: Output from Evidence Agent
- `iteration_history`: Previous iteration results
- `query`: Original question

**Output**:
```python
{
    "confidence_score": float,  # 0-100
    "overall_quality": str,  # EXCELLENT/GOOD/ADEQUATE/POOR
    "continue_iteration": bool,
    "convergence_detected": bool,
    "gaps": List[Dict],  # Identified evidence gaps
    "reasoning": str
}
```

**Stopping Criteria Logic**:
```python
if quality == "EXCELLENT":
    stop = True
elif quality == "GOOD" and convergence_detected:
    stop = True
elif quality == "ADEQUATE" and convergence_detected and no_high_priority_gaps:
    stop = True
elif iteration_num >= max_iterations:
    stop = True
```

---

#### 2.3 Synthesis Agent (`synthesis_agent.py`)

**Purpose**: Generate final strategic analysis report with full traceability

**Key Responsibilities**:
- Consolidate evidence from all iterations
- Perform epistemic analysis (FACT vs INFERENCE vs ASSUMPTION)
- Generate strategic findings with source citations
- Create confidence assessment
- Document gaps and recommendations

**Input**:
- `query`: Original question
- `iteration_results`: All evidence from all iterations
- `final_critique`: Final quality assessment

**Output**:
```python
{
    "report_markdown": str,  # Full formatted report
    "answer": str,  # Direct answer to question
    "confidence_score": float,
    "unique_sources": int,
    "total_evidence_chunks": int,
    "epistemic_summary": Dict  # Facts/Assumptions/Inferences breakdown
}
```

**Report Structure**:
1. Question
2. Confidence Assessment
3. Strategic Findings (with [FACT]/[SYNTHESIZED]/[INFERENCE] tags)
4. Epistemic Analysis
5. Sources Consulted
6. Gaps Identified
7. Iteration Log
8. Recommendations

---

#### 2.4 Orchestrator (`orchestrator.py`)

**Purpose**: Coordinate agent workflow through iteration loop

**Core Loop**:
```python
while iteration_num <= max_iterations:
    # STEP 1: Evidence Agent - Retrieve evidence
    evidence_result = evidence_agent.search(query, iteration_num, previous_gaps, k)

    # STEP 2: Critique Agent - Analyze quality
    critique_result = critique_agent.analyze(evidence_result, iteration_history, query)

    # STEP 3: Check stopping criteria
    if not critique_result["continue_iteration"]:
        break

    iteration_num += 1

# STEP 4: Synthesis Agent - Generate report
synthesis_result = synthesis_agent.synthesize(query, iteration_results, final_critique)
```

**Configuration Sources**:
- `config.py`: `DEFAULT_RETRIEVAL_K`, `MAX_SYNTHESIS_CHUNKS`, quality thresholds
- **HARDCODED**: `max_iterations` parameter (default: 5)

---

## 3. RAG (Retrieval-Augmented Generation) Implementation

### RAG Pattern Overview

The system implements **Multi-Iteration RAG** with quality-based stopping criteria.

**Classic RAG Pattern**:
```
Query → Retrieve Documents → Stuff Context → LLM Generate → Answer
```

**Our Enhanced Pattern**:
```
Query → [Expand Query] → Retrieve → [Rank by Affinity] → LLM Critique → [Continue?]
  ↑_____________________________________________________________________________|

  → [All Evidence] → LLM Synthesize → Report
```

### RAG Implementation Points

#### 3.1 Vector Semantic Search

**Location**: `evidence_agent.py`, lines 435-444

```python
def _semantic_search(self, query: str, k: int) -> List[Dict]:
    """Perform semantic search using ChromaDB."""
    results = self.vectordb.similarity_search_with_score(
        query=query,
        k=k,
    )

    formatted_results = []
    for doc, score in results:
        formatted_results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "similarity_score": score,
        })

    return formatted_results
```

**How it works**:
1. Query is embedded using OpenAI embeddings (text-embedding-3-small)
2. ChromaDB performs cosine similarity search against stored embeddings
3. Returns top `k` chunks with similarity scores
4. **CRITICAL**: Semantic search alone may miss strategically important documents if query embeddings don't align well

**Current Limitation**: NHS 10-year plan wasn't appearing in top 30 results for "LYPFT priorities" until we added hardcoded strategic keywords.

---

#### 3.2 Context Retrieval Configuration

**Location**: `orchestrator.py`, lines 153-159

```python
# HARDCODED FALLBACK: If Config not available, defaults to 30
k = Config.DEFAULT_RETRIEVAL_K if Config else 30

evidence_result = self.evidence_agent.search(
    query=query,
    iteration_num=iteration_num,
    previous_gaps=previous_gaps,
    k=k,
)
```

**Configuration Source**: `config.py`, line 24
```python
DEFAULT_RETRIEVAL_K = 30  # Increased from 20 to capture more strategic documents
```

**Why k=30?**:
- Database contains ~1600 chunks from 30 documents
- k=20 captured only ~6 documents (20% coverage)
- k=30 captures ~9-10 documents (30% coverage)
- **HARDCODED ASSUMPTION**: 30 chunks is sufficient for strategic context

---

#### 3.3 Context Stuffing (Evidence to LLM)

**Location**: `synthesis_agent.py`, lines 95-140

**Selection Strategy**:
```python
def _select_top_evidence(self, all_evidence: List[Dict]) -> List[Dict]:
    """Select top evidence chunks for synthesis."""

    # STEP 1: Deduplicate by content
    unique_chunks = self._deduplicate_chunks(all_evidence)

    # STEP 2: Rank by organization affinity
    ranked_chunks = self._rank_by_organization_affinity(unique_chunks)

    # STEP 3: Take top MAX_SYNTHESIS_CHUNKS (default: 30)
    top_chunks = ranked_chunks[:Config.MAX_SYNTHESIS_CHUNKS]

    return top_chunks
```

**Context Stuffing Limits** (`config.py`):
```python
MAX_SYNTHESIS_CHUNKS = 30  # HARDCODED: Maximum evidence chunks in final synthesis
```

**Why limit context?**:
- LLM context windows have token limits (GPT-4: 128k tokens)
- Average chunk size: ~500 tokens
- 30 chunks ≈ 15,000 tokens for evidence
- Leaves room for system prompt, reasoning, and output

**Context Window Usage Breakdown**:
```
System Prompt:           ~2,000 tokens
Evidence (30 chunks):   ~15,000 tokens
Query + Instructions:    ~1,000 tokens
LLM Response:           ~5,000 tokens
-------------------------------------------
Total:                  ~23,000 tokens (18% of GPT-4 capacity)
```

---

#### 3.4 Prompt Construction for Synthesis

**Location**: `synthesis_agent.py`, lines 185-235

**Prompt Structure**:
```python
prompt = f"""
# STRATEGIC ANALYSIS SYNTHESIS

## Your Role
You are a strategic analyst synthesizing evidence from multiple healthcare documents.

## Question
{query}

## Evidence from {len(iteration_results)} Iterations
{formatted_evidence}

## Quality Assessment
Confidence: {final_critique["confidence_score"]}%
Quality: {final_critique["overall_quality"]}
Gaps: {final_critique["gaps"]}

## Your Task
Generate a comprehensive strategic analysis report with:
1. Direct answer to the question
2. Strategic findings (mark as [FACT], [SYNTHESIZED], or [INFERENCE])
3. Epistemic analysis (what is fact vs assumption vs inference)
4. Source citations for all claims
5. Gap identification

## Output Format
Return JSON with:
- answer: Direct answer string
- strategic_findings: List of findings with evidence
- epistemic_breakdown: {{"facts": [], "assumptions": [], "inferences": []}}
- confidence_explanation: Reasoning for confidence level
"""
```

**Context Stuffing Pattern**:
1. System instructions (static)
2. Question (user input)
3. Evidence chunks (retrieved from RAG)
4. Quality metadata (from Critique Agent)
5. Output format instructions (static)

**HARDCODED ELEMENTS**:
- Prompt template structure
- Output format requirements
- Epistemic categories (FACT/ASSUMPTION/INFERENCE)
- Report section structure

---

## 4. Query Expansion Pipeline

The system uses a **4-step query expansion pipeline** before vector search. This is critical for comprehensive retrieval.

**Location**: `evidence_agent.py`, `search()` method, lines 310-375

### Step 1: Entity Resolution Expansion

**Purpose**: Replace aliases with canonical names and add related aliases

**Implementation**: `analysis/entity_resolution/entity_resolver.py`

**How it works**:
```python
# Input query
"What are LCH priorities?"

# Entity Resolution looks up "LCH" in entity_mappings.json
entity_mappings.json:
{
    "Leeds Community Healthcare NHS Trust": {
        "canonical_name": "Leeds Community Healthcare NHS Trust",
        "aliases": ["LCH", "LCH Trust", "Leeds Community Healthcare", ...],
        "abbreviation": "LCH"
    }
}

# Expanded query
"What are LCH Leeds Community Healthcare NHS Trust Leeds Community Healthcare priorities?"
```

**HARDCODED DATA**:
- **File**: `analysis/entity_resolution/entity_mappings.json`
- **27 entities** with **112 total aliases**
- **Manually curated** list of organization names and abbreviations
- **Static** - requires manual updates for new organizations

**Example Entry**:
```json
"Leeds and York Partnership NHS Foundation Trust": {
    "canonical_name": "Leeds and York Partnership NHS Foundation Trust",
    "aliases": [
        "LYPFT",
        "Leeds and York Partnership",
        "Leeds York Partnership",
        "L&Y Partnership",
        "Leeds and York Partnership Trust"
    ],
    "abbreviation": "LYPFT",
    "entity_type": "ORGANIZATION",
    "priority": "HIGH"
}
```

**Code Location**: `evidence_agent.py`, lines 318-327
```python
# STEP 1: Entity Resolution
if hasattr(self, 'entity_resolver') and self.entity_resolver:
    expanded_query = self.entity_resolver.expand_query(query)
    print(f"[ENTITY RESOLUTION] Expanded: {query} → {expanded_query}")
else:
    expanded_query = query
```

**Limitation**: New organizations not in `entity_mappings.json` won't be recognized or expanded.

---

### Step 2: Knowledge Graph Expansion

**Purpose**: Add related entities and services from knowledge graph relationships

**Implementation**: `analysis/multi_agent/knowledge_graph_agent.py`

**How it works**:
```python
# Input query (after entity resolution)
"What are LYPFT Leeds and York Partnership NHS Foundation Trust priorities?"

# Knowledge Graph Agent searches knowledge_graph_improved.json
knowledge_graph_improved.json:
{
    "Leeds and York Partnership NHS Foundation Trust": {
        "type": "ORGANIZATION",
        "relationships": {
            "PROVIDES": ["Mental Health Services", "Learning Disability Services"],
            "COLLABORATES_WITH": ["Leeds Teaching Hospitals NHS Trust", "Leeds Community Healthcare NHS Trust"],
            "PART_OF": ["Leeds Health and Care Partnership"]
        }
    }
}

# Expanded query
"What are LYPFT Leeds and York Partnership NHS Foundation Trust Mental Health Services Learning Disability Services Leeds Health and Care Partnership priorities?"
```

**HARDCODED DATA**:
- **File**: `knowledge_graph_improved.json`
- **146 entities** (organizations and services)
- **Manually created** relationship mappings
- **Static graph structure** - requires manual updates

**Example Knowledge Graph Entry**:
```json
{
    "id": "LYPFT",
    "name": "Leeds and York Partnership NHS Foundation Trust",
    "type": "ORGANIZATION",
    "attributes": {
        "abbreviation": "LYPFT",
        "domain": "Mental Health and Learning Disabilities"
    },
    "relationships": [
        {
            "type": "PROVIDES",
            "target": "Mental Health Services",
            "strength": "PRIMARY"
        },
        {
            "type": "COLLABORATES_WITH",
            "target": "Leeds Community Healthcare NHS Trust",
            "context": "Integrated Care System"
        },
        {
            "type": "PART_OF",
            "target": "Leeds Health and Care Partnership",
            "role": "Partner Organization"
        }
    ]
}
```

**Code Location**: `evidence_agent.py`, lines 329-338
```python
# STEP 2: Knowledge Graph Expansion
if hasattr(self, 'kg_agent') and self.kg_agent:
    kg_expanded = self.kg_agent.expand_query(expanded_query)
    if kg_expanded != expanded_query:
        expanded_query = kg_expanded
        print(f"[KNOWLEDGE GRAPH] Added related entities")
    else:
        print(f"[KNOWLEDGE GRAPH] No additional entities found")
else:
    print(f"[KNOWLEDGE GRAPH] Agent not available")
```

**Knowledge Graph Agent Implementation** (`knowledge_graph_agent.py`, lines 70-140):
```python
def expand_query(self, query: str) -> str:
    """Expand query using knowledge graph relationships."""

    # Find mentioned entities in query
    mentioned_entities = self._find_entities_in_query(query)

    # For each entity, get related entities (1-hop traversal)
    related_terms = []
    for entity in mentioned_entities:
        relationships = self.graph.get(entity, {}).get("relationships", {})
        for rel_type, targets in relationships.items():
            related_terms.extend(targets)

    # Add related terms to query
    expanded = f"{query} {' '.join(related_terms)}"
    return expanded
```

**Limitation**: Only performs **1-hop traversal** - doesn't follow relationships recursively. Strategic connections may be missed.

---

### Step 3: Strategic Keywords Expansion (HARDCODED - IDENTIFIED ISSUE)

**Purpose**: Add national strategic terms for priority/strategy questions

**THIS IS THE HARDCODING THE USER IDENTIFIED AS PROBLEMATIC**

**Code Location**: `evidence_agent.py`, lines 340-361

```python
# STEP 3: Strategic Keywords - Add for priority/strategy questions
strategy_keywords = ["priority", "priorities", "strategy", "plan", "goal", "objective"]
query_lower = query.lower()

if any(kw in query_lower for kw in strategy_keywords):
    # HARDCODED LIST OF STRATEGIC TERMS
    strategic_terms = [
        "10-year plan",
        "health plan England",
        "national health strategy",
        "NHS England planning framework",
        "long-term planning"
    ]

    # Only add if not already present
    if not any(term.lower() in expanded_query.lower() for term in strategic_terms):
        expanded_query = f"{expanded_query} {' '.join(strategic_terms)}"
        print(f"[STRATEGY EXPANSION] Added national strategic context")
else:
    print(f"[STRATEGY EXPANSION] Not a strategy question, skipping")
```

**Why this exists**:
- NHS 10-year plan document (170 chunks) wasn't appearing in semantic search results
- Semantic search alone couldn't connect "LYPFT priorities" to "NHS England 10-year plan"
- Adding these hardcoded terms forces ChromaDB to retrieve strategic context documents

**HARDCODED ELEMENTS**:
1. **Trigger keywords**: `["priority", "priorities", "strategy", "plan", "goal", "objective"]`
2. **Strategic terms**: `["10-year plan", "health plan England", "national health strategy", "NHS England planning framework", "long-term planning"]`

**User's Concern (Quote)**: *"This isnt very dynamic is it, if i have to hard code these words."*

**Why it's not dynamic**:
- New strategic documents (e.g., "5-year workforce plan") won't be retrieved unless manually added to list
- Different policy domains (education, housing, etc.) would need separate hardcoded lists
- No mechanism to discover important strategic context automatically

**Potential Dynamic Alternatives** (not yet implemented):
- Document metadata tagging (document_type: "STRATEGIC_PLAN")
- Hybrid search (semantic + keyword + metadata filters)
- Document importance scoring based on citation frequency
- Hierarchical document relationships (organization docs → system docs → national docs)

---

### Step 4: Gap-Based Expansion (Iterative)

**Purpose**: Add search terms based on gaps identified in previous iteration

**Code Location**: `evidence_agent.py`, lines 363-375

```python
# STEP 4: Gap-based expansion (if iteration > 1)
if iteration_num > 1 and previous_gaps:
    gap_keywords = []
    for gap in previous_gaps:
        if gap.get("severity") in ["HIGH", "MEDIUM"]:
            # Extract suggested search terms from gap description
            gap_action = gap.get("action", "")
            if "search for" in gap_action.lower():
                # Parse out search terms (simple extraction)
                terms = gap_action.split("search for")[-1].strip()
                gap_keywords.append(terms)

    if gap_keywords:
        expanded_query = f"{expanded_query} {' '.join(gap_keywords)}"
        print(f"[GAP REFINEMENT] Added terms from {len(gap_keywords)} gaps")
```

**How Critique Agent generates gaps**:

**Location**: `critique_agent.py`, lines 180-250

```python
def _identify_gaps(self, evidence_result: Dict) -> List[Dict]:
    """Identify evidence gaps."""
    gaps = []

    # Gap 1: Low source coverage
    if evidence_result["unique_sources"] < 10:
        gaps.append({
            "severity": "MEDIUM",
            "category": "coverage",
            "description": "Limited source diversity",
            "action": "Search for more sources on [TOPIC]"  # ← Parsed in Step 4
        })

    # Gap 2: Over-reliance on single source
    source_distribution = self._analyze_source_distribution(evidence_result)
    dominant_source = max(source_distribution.items(), key=lambda x: x[1])
    if dominant_source[1] > 0.5:  # HARDCODED: 50% threshold
        gaps.append({
            "severity": "MEDIUM",
            "category": "source_diversity",
            "description": f"Over 50% of evidence from {dominant_source[0]}",
            "action": "Diversify sources to avoid bias"
        })

    # Gap 3: Insufficient factual data
    if evidence_result.get("fact_count", 0) < 5:  # HARDCODED: 5 fact minimum
        gaps.append({
            "severity": "MEDIUM",
            "category": "data_quality",
            "description": "Insufficient facts - need more hard data",
            "action": "Search for more factual sources (reports, statistics)"
        })

    return gaps
```

**HARDCODED THRESHOLDS**:
- Source diversity threshold: 50% from single source
- Minimum fact count: 5 facts
- Coverage threshold: 10 sources minimum

**Limitation**: Gap-based expansion is simple keyword extraction, not semantic understanding of what's actually missing.

---

### Query Expansion Summary

**Complete Flow Example**:
```
Original Query:
"What are the largest priorities for LYPFT over the next 12 months?"

↓ Step 1: Entity Resolution
"What are the largest priorities for LYPFT Leeds and York Partnership NHS Foundation Trust Leeds and York Partnership over the next 12 months?"

↓ Step 2: Knowledge Graph
"What are the largest priorities for LYPFT Leeds and York Partnership NHS Foundation Trust Leeds and York Partnership Mental Health Services Learning Disability Services Leeds Health and Care Partnership over the next 12 months?"

↓ Step 3: Strategic Keywords (HARDCODED)
"What are the largest priorities for LYPFT Leeds and York Partnership NHS Foundation Trust Leeds and York Partnership Mental Health Services Learning Disability Services Leeds Health and Care Partnership over the next 12 months? 10-year plan health plan England national health strategy NHS England planning framework long-term planning"

↓ Step 4: Gap-based (Iteration 2+)
[If gaps identified: add specific search terms]
"... workforce development service transformation digital health"

↓ Final Expanded Query → ChromaDB Semantic Search
```

**Total Expansion Ratio**: Original query (~15 words) → Expanded query (~60-80 words) = **4-5x expansion**

**Hardcoded Dependencies**:
- Entity mappings JSON (27 entities, 112 aliases)
- Knowledge graph JSON (146 entities, relationships)
- Strategic keywords list (5 terms)
- Gap threshold values (50%, 5 facts, 10 sources)

---

## 5. Knowledge Graph Integration

### Knowledge Graph Structure

**File**: `knowledge_graph_improved.json`
**Format**: JSON with entity nodes and relationship edges

**Schema**:
```json
{
    "entities": [
        {
            "id": "unique_identifier",
            "name": "Full Entity Name",
            "type": "ORGANIZATION | SERVICE | STRATEGY | INITIATIVE",
            "attributes": {
                "abbreviation": "ABBR",
                "domain": "Clinical Area",
                "description": "..."
            },
            "relationships": [
                {
                    "type": "PROVIDES | COLLABORATES_WITH | PART_OF | LEADS | ...",
                    "target": "target_entity_id",
                    "strength": "PRIMARY | SECONDARY",
                    "context": "Description of relationship"
                }
            ]
        }
    ]
}
```

**Example Entries**:

```json
{
    "id": "LYPFT",
    "name": "Leeds and York Partnership NHS Foundation Trust",
    "type": "ORGANIZATION",
    "attributes": {
        "abbreviation": "LYPFT",
        "domain": "Mental Health and Learning Disabilities",
        "location": "Leeds and York"
    },
    "relationships": [
        {
            "type": "PROVIDES",
            "target": "Mental_Health_Services",
            "strength": "PRIMARY"
        },
        {
            "type": "PROVIDES",
            "target": "Learning_Disability_Services",
            "strength": "PRIMARY"
        },
        {
            "type": "LEADS",
            "target": "Tier4_CYPMHS",
            "context": "Lead provider for West Yorkshire"
        },
        {
            "type": "PART_OF",
            "target": "Leeds_Health_Care_Partnership",
            "context": "Partner organization"
        },
        {
            "type": "COLLABORATES_WITH",
            "target": "LCH",
            "context": "Integrated care delivery"
        }
    ]
}
```

**Statistics**:
- **146 total entities**
- **Organizations**: 12 (NHS trusts, councils, partnerships)
- **Services**: 78 (clinical services, programs)
- **Strategies**: 23 (plans, frameworks)
- **Initiatives**: 33 (projects, programs)
- **Relationship types**: 15 (PROVIDES, COLLABORATES_WITH, PART_OF, LEADS, SUPPORTS, etc.)

**HARDCODED ELEMENTS**:
1. All entity names and IDs
2. All relationship mappings
3. Relationship types (15 predefined types)
4. Entity categorization (4 types: ORG/SERVICE/STRATEGY/INITIATIVE)

---

### Knowledge Graph Agent Implementation

**File**: `analysis/multi_agent/knowledge_graph_agent.py`

**Core Methods**:

#### 5.1 Loading the Graph

```python
def __init__(self, kg_path: str = "knowledge_graph_improved.json"):
    """Load knowledge graph from JSON."""
    with open(kg_path, 'r', encoding='utf-8') as f:
        self.raw_graph = json.load(f)

    # Build adjacency list for fast lookup
    self.graph = self._build_adjacency_list()
```

**Adjacency List Structure**:
```python
{
    "LYPFT": {
        "name": "Leeds and York Partnership NHS Foundation Trust",
        "type": "ORGANIZATION",
        "relationships": {
            "PROVIDES": ["Mental_Health_Services", "Learning_Disability_Services"],
            "PART_OF": ["Leeds_Health_Care_Partnership"],
            "COLLABORATES_WITH": ["LCH", "LTHT"]
        }
    }
}
```

---

#### 5.2 Query Expansion

**Method**: `expand_query(query: str) -> str`

**Algorithm**:
```python
def expand_query(self, query: str) -> str:
    """Expand query using 1-hop knowledge graph traversal."""

    # Step 1: Find entities mentioned in query (exact match or alias)
    mentioned_entities = self._find_entities_in_query(query)

    # Step 2: For each entity, get related entities (1-hop)
    related_terms = []
    for entity_id in mentioned_entities:
        entity = self.graph.get(entity_id)
        if entity:
            # Get all outgoing relationships
            for rel_type, targets in entity["relationships"].items():
                related_terms.extend(targets)

    # Step 3: Resolve entity IDs to full names
    resolved_terms = [self._get_entity_name(term) for term in related_terms]

    # Step 4: Add to query
    if resolved_terms:
        expanded = f"{query} {' '.join(resolved_terms)}"
        return expanded

    return query
```

**Example**:
```python
query = "What are LYPFT priorities?"

# Step 1: Find entities
mentioned_entities = ["LYPFT"]

# Step 2: Get relationships
relationships = {
    "PROVIDES": ["Mental_Health_Services", "Learning_Disability_Services"],
    "PART_OF": ["Leeds_Health_Care_Partnership"],
    "COLLABORATES_WITH": ["LCH", "LTHT"]
}

# Step 3: Resolve IDs to names
related_terms = [
    "Mental Health Services",
    "Learning Disability Services",
    "Leeds Health and Care Partnership",
    "Leeds Community Healthcare NHS Trust",
    "Leeds Teaching Hospitals NHS Trust"
]

# Step 4: Expand query
expanded = "What are LYPFT priorities? Mental Health Services Learning Disability Services Leeds Health and Care Partnership Leeds Community Healthcare NHS Trust Leeds Teaching Hospitals NHS Trust"
```

**HARDCODED LIMITATIONS**:
1. **Only 1-hop traversal**: Doesn't follow relationship chains (A→B→C)
2. **No relationship filtering**: All relationship types treated equally
3. **No relevance scoring**: All related entities added with equal weight
4. **No cycle detection**: Could theoretically create infinite loops (not observed in practice)

---

#### 5.3 Entity Recognition in Query

**Method**: `_find_entities_in_query(query: str) -> List[str]`

**Algorithm**:
```python
def _find_entities_in_query(self, query: str) -> List[str]:
    """Find entities mentioned in query using alias matching."""
    query_lower = query.lower()
    mentioned = []

    for entity_id, entity in self.graph.items():
        # Check entity name
        if entity["name"].lower() in query_lower:
            mentioned.append(entity_id)
            continue

        # Check abbreviation
        if entity.get("attributes", {}).get("abbreviation", "").lower() in query_lower:
            mentioned.append(entity_id)
            continue

        # Check aliases (if entity resolver provides them)
        # NOTE: This depends on entity_mappings.json alignment

    return mentioned
```

**HARDCODED DEPENDENCY**: Relies on exact string matching of entity names and abbreviations. Doesn't handle:
- Fuzzy matching ("LYPFT" vs "L&YPFT")
- Partial matches ("Leeds Partnership" for "Leeds and York Partnership")
- Typos or variations

---

### Knowledge Graph Usage in System

**Integration Point**: `evidence_agent.py`, lines 329-338

```python
# STEP 2: Knowledge Graph Expansion
if hasattr(self, 'kg_agent') and self.kg_agent:
    kg_expanded = self.kg_agent.expand_query(expanded_query)
    if kg_expanded != expanded_query:
        expanded_query = kg_expanded
        print(f"[KNOWLEDGE GRAPH] Added related entities")
```

**Effect on Retrieval**:
- Adds 5-15 related terms per mentioned organization
- Increases query length by ~30-50 words
- Improves recall for collaborative initiatives and related services
- **Side effect**: May dilute semantic search if too many unrelated terms added

---

### Knowledge Graph Limitations

**Current Issues**:

1. **Manual Maintenance**:
   - Relationships must be manually added to JSON
   - New organizations/services require manual updates
   - Relationship accuracy depends on manual curation

2. **Static Structure**:
   - No automatic relationship discovery from documents
   - Can't adapt to changing organizational relationships
   - Outdated relationships (e.g., partnerships that ended) remain unless manually removed

3. **Shallow Traversal**:
   - Only 1-hop expansion (immediate neighbors)
   - Doesn't explore deeper strategic connections
   - Example: "LYPFT" → "Leeds Health and Care Partnership" (found)
   - Example: "LYPFT" → "Leeds Health and Care Partnership" → "Healthy Leeds Plan" (NOT found)

4. **No Relationship Weighting**:
   - All relationships treated equally
   - "PRIMARY" vs "SECONDARY" strength markers not used in expansion
   - Can't prioritize more important relationships

5. **No Contextual Filtering**:
   - Adds all related entities regardless of question context
   - Question about "workforce" still adds "clinical services" relationships
   - No semantic filtering of which relationships are relevant

**Example Limitation**:
```python
query = "What are LYPFT workforce priorities?"

# Current behavior: Adds ALL relationships
expanded = "What are LYPFT workforce priorities? Mental Health Services Learning Disability Services Forensic Services Eating Disorders Adult Services Child Services Leeds Health and Care Partnership..."

# Desired behavior: Filter to workforce-relevant relationships
expanded = "What are LYPFT workforce priorities? workforce development recruitment retention training career pathways staffing..."
```

**This limitation connects to the user's concern about hardcoding** - the knowledge graph doesn't adapt to query intent, just blindly adds all relationships.

---

## 6. Context Stuffing Mechanisms

"Context stuffing" refers to how we select and pack evidence chunks into LLM prompts. This is critical because LLMs have token limits and too much context degrades performance.

### 6.1 Evidence Selection Strategy

**Location**: `synthesis_agent.py`, `_select_top_evidence()`, lines 95-140

**3-Step Selection Process**:

```python
def _select_top_evidence(self, all_evidence: List[Dict]) -> List[Dict]:
    """
    Select top evidence chunks for synthesis.

    Strategy:
    1. Deduplicate identical/near-identical chunks
    2. Rank by organization affinity (PRIMARY > STRATEGIC > GENERAL)
    3. Take top MAX_SYNTHESIS_CHUNKS
    """

    # STEP 1: Deduplicate
    unique_chunks = self._deduplicate_chunks(all_evidence)

    # STEP 2: Rank by affinity
    ranked_chunks = self._rank_by_organization_affinity(unique_chunks)

    # STEP 3: Limit to max chunks
    max_chunks = Config.MAX_SYNTHESIS_CHUNKS if Config else 30  # HARDCODED: 30
    top_chunks = ranked_chunks[:max_chunks]

    return top_chunks
```

---

#### Step 1: Deduplication

**Purpose**: Remove duplicate content retrieved across iterations

**Algorithm**:
```python
def _deduplicate_chunks(self, chunks: List[Dict]) -> List[Dict]:
    """Remove duplicate chunks based on content similarity."""
    seen_content = {}
    unique_chunks = []

    for chunk in chunks:
        content = chunk["content"]
        # Normalize: lowercase, strip whitespace
        normalized = ' '.join(content.lower().split())

        # Check for exact or near-duplicate
        content_hash = hash(normalized)

        if content_hash not in seen_content:
            seen_content[content_hash] = True
            unique_chunks.append(chunk)

    return unique_chunks
```

**HARDCODED LOGIC**: Uses exact hash matching - doesn't detect semantic duplicates (same meaning, different wording)

**Example**:
```python
chunks = [
    {"content": "LYPFT provides mental health services."},
    {"content": "LYPFT provides mental health services."},  # ← Duplicate (removed)
    {"content": "Leeds and York Partnership NHS Foundation Trust delivers mental health care."}  # ← Semantic duplicate (NOT removed)
]
```

---

#### Step 2: Ranking by Organization Affinity

**Purpose**: Prioritize chunks most relevant to the question's target organization

**Algorithm** (see Section 8 for full details):
```python
def _rank_by_organization_affinity(self, chunks: List[Dict]) -> List[Dict]:
    """Rank chunks by 3-tier affinity system."""

    # Tier 3 (PRIMARY): Organization-specific docs
    tier3_chunks = [c for c in chunks if self._is_primary_org_doc(c)]

    # Tier 2 (STRATEGIC): National plans, frameworks
    tier2_chunks = [c for c in chunks if self._is_strategic_doc(c) and c not in tier3_chunks]

    # Tier 1 (GENERAL): Other NHS/health context
    tier1_chunks = [c for c in chunks if c not in tier3_chunks and c not in tier2_chunks]

    # Sort within each tier by similarity score
    tier3_sorted = sorted(tier3_chunks, key=lambda x: x["similarity_score"], reverse=True)
    tier2_sorted = sorted(tier2_chunks, key=lambda x: x["similarity_score"], reverse=True)
    tier1_sorted = sorted(tier1_chunks, key=lambda x: x["similarity_score"], reverse=True)

    # Concatenate: PRIMARY → STRATEGIC → GENERAL
    return tier3_sorted + tier2_sorted + tier1_sorted
```

**HARDCODED KEYWORD LISTS** (see Section 8.2):
- PRIMARY keywords: ["LYPFT", "Leeds and York Partnership", ...]
- STRATEGIC keywords: ["NHS England", "national strategy", "10-year plan", ...]

---

#### Step 3: Limiting to MAX_SYNTHESIS_CHUNKS

**Configuration**: `config.py`, line 27
```python
MAX_SYNTHESIS_CHUNKS = 30  # HARDCODED
```

**Why 30?**:
- Empirically tested balance between coverage and prompt length
- Average chunk: ~500 tokens
- 30 chunks = ~15,000 tokens (leaves room for instructions and output)
- Too few (10-15): Misses important context
- Too many (50+): Dilutes focus, increases cost, slows generation

**Trade-offs**:
```
Fewer Chunks (10-15):
✓ Faster generation
✓ Lower cost
✓ More focused answers
✗ Might miss key evidence
✗ Lower coverage

More Chunks (50+):
✓ Higher coverage
✓ More comprehensive evidence
✗ Slower generation
✗ Higher cost ($$$)
✗ Risk of "lost in the middle" effect (LLM ignores middle chunks)
```

**Research Basis**: ["Lost in the Middle" paper (Liu et al. 2023)](https://arxiv.org/abs/2307.03172) showed LLMs perform worse when relevant information is in the middle of long contexts.

---

### 6.2 Context Packing Format

**Location**: `synthesis_agent.py`, `synthesize()`, lines 45-90

**Prompt Template**:
```python
def _format_evidence_for_prompt(self, chunks: List[Dict]) -> str:
    """Format evidence chunks for LLM prompt."""

    formatted_sections = []

    for i, chunk in enumerate(chunks, 1):
        source = chunk["metadata"].get("source", "Unknown")
        org = chunk["metadata"].get("organization", "Unknown")
        date = chunk["metadata"].get("date", "Unknown")
        relevance = chunk.get("relevance_tag", "GENERAL")
        content = chunk["content"]

        # Format with metadata header
        section = f"""
        ### Evidence Chunk {i}
        **Source**: {source}
        **Organization**: {org}
        **Date**: {date}
        **Relevance**: {relevance}

        {content}

        ---
        """

        formatted_sections.append(section)

    return '\n'.join(formatted_sections)
```

**Example Formatted Context**:
```
### Evidence Chunk 1
**Source**: LYPFT Annual-Report-and-Accounts-2024-25.md
**Organization**: Leeds and York Partnership NHS Foundation Trust
**Date**: 2025-06-30
**Relevance**: PRIMARY

Improving the Health and Lives of the Communities we Serve: from 2025 to 2030 is the new five-year strategy of Leeds and York Partnership NHS Foundation Trust. It was developed during 2024, ratified by the Trust Board in November that year and has been socialised internally and externally during quarter four of 2024.

---

### Evidence Chunk 2
**Source**: NHS England _ Planning framework for the NHS in England.md
**Organization**: NHS England
**Date**: 2025-09-08
**Relevance**: STRATEGIC

This framework has been developed as a guide for local leaders across England responsible for the development of the strategic and operational plans for the next 5 years.

---

[... 28 more chunks ...]
```

**HARDCODED ELEMENTS**:
1. Metadata fields (source, organization, date, relevance)
2. Section divider (`---`)
3. Numbering format (`Evidence Chunk {i}`)
4. Field labels (Source, Organization, etc.)

---

### 6.3 Token Budget Management

**Estimated Token Distribution** for typical query:

| Component | Tokens | % of Total |
|-----------|--------|------------|
| System prompt (role, instructions) | ~2,000 | 9% |
| Query + context | ~500 | 2% |
| Evidence chunks (30 × 500 tokens) | ~15,000 | 65% |
| Quality metadata (critique) | ~1,000 | 4% |
| Output instructions | ~500 | 2% |
| LLM response | ~4,000 | 17% |
| **Total** | **~23,000** | **100%** |

**Model Context Limits**:
- GPT-4: 128,000 tokens (we use ~18%)
- GPT-4o: 128,000 tokens (we use ~18%)
- GPT-3.5-Turbo: 16,385 tokens (would exceed limit!)

**HARDCODED ASSUMPTIONS**:
- Average chunk size: 500 tokens (not measured, assumed)
- System prompt size: 2,000 tokens (not measured, assumed)
- Output size: 4,000 tokens (not measured, assumed)

**No Dynamic Token Counting**: System doesn't actually measure token usage, just assumes these values. Could lead to issues with:
- Very long chunks (some may be 1000+ tokens)
- Complex queries requiring longer system prompts
- Detailed reports requiring longer outputs

---

### 6.4 Context Stuffing Across Multiple Agents

**Evidence Agent** → Retrieves 30 chunks (k=30)
- Input: Query
- Output: 30 chunks with metadata

**Critique Agent** → Analyzes all retrieved chunks
- Input: All 30 chunks from Evidence Agent
- Output: Quality scores and gaps
- **Does NOT reduce context size**

**Synthesis Agent** → Selects top 30 chunks from ALL iterations
- Input: ALL chunks from ALL iterations (could be 60-90 chunks if 2-3 iterations)
- Selection: Deduplicates → Ranks → Takes top 30
- Output: Final report using selected 30 chunks

**Context Flow**:
```
Iteration 1: Retrieve 30 chunks → Critique → Continue
Iteration 2: Retrieve 30 chunks → Critique → Continue
Iteration 3: Retrieve 30 chunks → Critique → Stop
---------------------------------------------------------
Total retrieved: 90 chunks
After deduplication: ~60 unique chunks
After ranking + limiting: 30 chunks (sent to Synthesis Agent)
```

**HARDCODED BEHAVIOR**: Always limits to exactly 30 chunks in final synthesis, regardless of:
- Number of iterations (could be 1 or 5)
- Total chunks retrieved (could be 30 or 150)
- Quality of evidence (even if all 60 chunks are high quality, only 30 used)

---

## 7. Manual Hardcoding Patterns

This section catalogs ALL hardcoded values, thresholds, and logic throughout the system.

### 7.1 Configuration Hardcoding (`config.py`)

**All Configuration Values**:
```python
# Retrieval settings
DEFAULT_RETRIEVAL_K = 30  # Number of chunks to retrieve per search
MAX_SYNTHESIS_CHUNKS = 30  # Maximum chunks for final synthesis
SIMILARITY_THRESHOLD = 0.7  # Minimum similarity score (NOT CURRENTLY USED)

# Quality thresholds
CONFIDENCE_EXCELLENT = 90  # Confidence score for EXCELLENT quality
CONFIDENCE_GOOD = 75       # Confidence score for GOOD quality
CONFIDENCE_ADEQUATE = 50   # Confidence score for ADEQUATE quality

# Iteration settings
MAX_ITERATIONS = 5  # Maximum iterations before forced stop

# LLM settings
DEFAULT_LLM_MODEL = "gpt-4o"  # OpenAI model
DEFAULT_TEMPERATURE = 0.5     # Lower = more deterministic
```

**Why these values?**
- **k=30**: Empirically tested - provides ~30% coverage of 30-document database
- **MAX_SYNTHESIS_CHUNKS=30**: Token budget constraint (~15k tokens for evidence)
- **Confidence thresholds (90/75/50)**: Arbitrary - not validated against ground truth
- **MAX_ITERATIONS=5**: Practical limit to prevent infinite loops and costs
- **Temperature=0.5**: Balance between determinism and creativity

**NOT DYNAMICALLY TUNED**: These values are not learned or adapted based on:
- Query complexity
- Database size
- Evidence quality
- User preferences
- Historical performance

---

### 7.2 Strategic Keywords Hardcoding (`evidence_agent.py`)

**Location**: Lines 340-361

**Trigger Keywords**:
```python
strategy_keywords = ["priority", "priorities", "strategy", "plan", "goal", "objective"]
```

**Strategic Terms Added**:
```python
strategic_terms = [
    "10-year plan",
    "health plan England",
    "national health strategy",
    "NHS England planning framework",
    "long-term planning"
]
```

**Why this exists**: NHS 10-year plan document wasn't being retrieved by semantic search alone.

**Limitations**:
1. Only works for queries containing trigger keywords
2. Always adds ALL strategic terms (no selective addition)
3. Only covers NHS strategic documents (not education, housing, etc.)
4. Requires manual updates for new strategic documents
5. Can't adapt to different policy domains

**USER'S IDENTIFIED PROBLEM**: *"This isnt very dynamic is it, if i have to hard code these words."*

---

### 7.3 Organization Affinity Keywords (`evidence_agent.py`)

**Location**: Lines 460-520, `_rank_by_organization_affinity()` method

**PRIMARY Organization Keywords** (Tier 3):
```python
primary_keywords = [
    "LYPFT",
    "Leeds and York Partnership NHS Foundation Trust",
    "Leeds and York Partnership",
    "Leeds York Partnership",
    # ... organization-specific variations
]
```

**STRATEGIC Keywords** (Tier 2):
```python
strategic_keywords = [
    "NHS England",
    "national strategy",
    "10-year plan",
    "health plan England",
    "long-term plan",
    "planning framework",
    "operational planning guidance",
    "NHS Long Term Plan",
    "workforce plan",
    "digital health strategy"
]
```

**GENERAL Keywords** (Tier 1):
- Everything else (default category)

**Why this exists**: To prioritize organization-specific documents while keeping strategic context.

**Limitations**:
1. Keywords must be manually maintained for each organization
2. Can't detect organization-specific docs without keyword match
3. Strategic keywords may miss new policy documents
4. No semantic understanding (e.g., "decade-long plan" wouldn't match "10-year plan")

---

### 7.4 Gap Detection Thresholds (`critique_agent.py`)

**Location**: Lines 180-250, `_identify_gaps()` method

**Coverage Gap**:
```python
if evidence_result["unique_sources"] < 10:  # HARDCODED: 10 sources minimum
    gaps.append({
        "severity": "MEDIUM",
        "category": "coverage",
        "description": "Limited source diversity",
        "action": "Search for more sources"
    })
```

**Source Diversity Gap**:
```python
dominant_source_ratio = max(source_distribution.values())
if dominant_source_ratio > 0.5:  # HARDCODED: 50% threshold
    gaps.append({
        "severity": "MEDIUM",
        "category": "source_diversity",
        "description": f"Over 50% of evidence from one source",
        "action": "Diversify sources to avoid bias"
    })
```

**Fact Count Gap**:
```python
if evidence_result.get("fact_count", 0) < 5:  # HARDCODED: 5 facts minimum
    gaps.append({
        "severity": "MEDIUM",
        "category": "data_quality",
        "description": "Insufficient facts - need more hard data",
        "action": "Search for more factual sources"
    })
```

**Recency Gap**:
```python
old_evidence_count = sum(1 for chunk in evidence_result["results"]
                         if chunk.get("date", "2025") < "2023")  # HARDCODED: 2023 cutoff

if old_evidence_count > 0.3 * len(evidence_result["results"]):  # HARDCODED: 30% threshold
    gaps.append({
        "severity": "LOW",
        "category": "recency",
        "description": "Some evidence is outdated",
        "action": "Prioritize recent sources"
    })
```

**ALL HARDCODED THRESHOLDS**:
- Minimum sources: 10
- Source dominance: 50%
- Minimum facts: 5
- Recency cutoff: 2023
- Old evidence threshold: 30%

**Why these values?** Arbitrary - not validated through testing or research.

---

### 7.5 Quality Rating Thresholds (`critique_agent.py`)

**Location**: Lines 120-150, `analyze()` method

**Quality Calculation**:
```python
def _calculate_quality(self, confidence_score: float, gaps: List[Dict]) -> str:
    """Determine overall quality rating."""

    high_gaps = sum(1 for gap in gaps if gap["severity"] == "HIGH")
    medium_gaps = sum(1 for gap in gaps if gap["severity"] == "MEDIUM")

    # HARDCODED LOGIC:
    if confidence_score >= 90 and high_gaps == 0:  # HARDCODED: 90% threshold
        return "EXCELLENT"

    elif confidence_score >= 75 and high_gaps == 0:  # HARDCODED: 75% threshold
        return "GOOD"

    elif confidence_score >= 50 and high_gaps <= 1:  # HARDCODED: 50% threshold, 1 high gap
        return "ADEQUATE"

    else:
        return "POOR"
```

**Stopping Criteria Logic** (`orchestrator.py`, lines 221-237):
```python
def _get_stop_reason(self, critique: Dict, iteration_num: int) -> str:
    # HARDCODED: Stop on EXCELLENT
    if critique["overall_quality"] == "EXCELLENT":
        return "Excellent quality achieved"

    # HARDCODED: Stop on GOOD + convergence
    if critique["overall_quality"] == "GOOD" and critique["convergence_detected"]:
        return "Good quality + convergence detected"

    # HARDCODED: Stop on ADEQUATE + convergence + no high gaps
    if critique["overall_quality"] == "ADEQUATE" and critique["convergence_detected"]:
        high_gaps = [g for g in critique["gaps"] if g.get("severity") == "HIGH"]
        if not high_gaps:
            return "Adequate quality + convergence + no high-priority gaps"

    return "Stopping criteria met"
```

**HARDCODED LOGIC TREE**:
```
EXCELLENT (90%+ confidence, 0 high gaps) → STOP
GOOD (75%+ confidence, 0 high gaps) + convergence → STOP
ADEQUATE (50%+ confidence, ≤1 high gap) + convergence + no high gaps → STOP
Iteration ≥ MAX_ITERATIONS (5) → STOP
Otherwise → CONTINUE
```

---

### 7.6 Convergence Detection (`critique_agent.py`)

**Location**: Lines 260-290, `_detect_convergence()` method

**Algorithm**:
```python
def _detect_convergence(self, current_result: Dict, iteration_history: List[Dict]) -> bool:
    """Detect if we're seeing repeated evidence."""

    if not iteration_history:
        return False

    # Get source lists from current and previous iteration
    current_sources = set(chunk["metadata"]["source"] for chunk in current_result["results"])
    previous_sources = set(chunk["metadata"]["source"] for chunk in iteration_history[-1]["results"])

    # Calculate overlap
    overlap = len(current_sources & previous_sources)
    overlap_ratio = overlap / len(current_sources) if current_sources else 0

    # HARDCODED: 80% overlap indicates convergence
    if overlap_ratio > 0.8:
        return True

    return False
```

**HARDCODED THRESHOLD**: 80% source overlap = convergence

**Why 80%?** Arbitrary choice - not validated.

**Potential Issues**:
- May declare convergence too early (new sources still exist but not retrieved)
- May never converge if retrieval is noisy (different results each time due to query expansion variations)
- Doesn't account for content overlap (could retrieve different chunks from same source)

---

### 7.7 Entity Resolution Hardcoding

**File**: `analysis/entity_resolution/entity_mappings.json`

**All 27 entities manually defined** with canonical names, aliases, abbreviations.

**Example Entry**:
```json
{
    "Leeds and York Partnership NHS Foundation Trust": {
        "canonical_name": "Leeds and York Partnership NHS Foundation Trust",
        "aliases": [
            "LYPFT",
            "Leeds and York Partnership",
            "Leeds York Partnership",
            "L&Y Partnership",
            "Leeds and York Partnership Trust",
            "Leeds & York Partnership NHS Foundation Trust"
        ],
        "abbreviation": "LYPFT",
        "entity_type": "ORGANIZATION",
        "priority": "HIGH"
    }
}
```

**HARDCODED DATA**:
- 27 entities
- 112 total aliases
- Entity types: ORGANIZATION, SERVICE, PARTNERSHIP
- Priority levels: HIGH, MEDIUM

**Manual Maintenance Required**:
- New organizations must be manually added
- Aliases must be manually curated
- No automatic alias discovery from documents
- No validation that aliases actually appear in corpus

---

### 7.8 Knowledge Graph Hardcoding

**File**: `knowledge_graph_improved.json`

**146 entities manually defined** with relationships.

**Example Entry**:
```json
{
    "id": "LYPFT",
    "name": "Leeds and York Partnership NHS Foundation Trust",
    "type": "ORGANIZATION",
    "attributes": {
        "abbreviation": "LYPFT",
        "domain": "Mental Health and Learning Disabilities"
    },
    "relationships": [
        {
            "type": "PROVIDES",
            "target": "Mental_Health_Services",
            "strength": "PRIMARY"
        },
        {
            "type": "PART_OF",
            "target": "Leeds_Health_Care_Partnership",
            "context": "Partner organization"
        }
    ]
}
```

**HARDCODED DATA**:
- 146 entities (12 organizations, 78 services, 23 strategies, 33 initiatives)
- All relationships manually mapped
- 15 relationship types (PROVIDES, COLLABORATES_WITH, PART_OF, LEADS, etc.)
- Relationship strengths (PRIMARY, SECONDARY)

**Manual Maintenance Required**:
- New entities must be manually added
- Relationships must be manually discovered and encoded
- No automatic relationship extraction from documents
- No validation that relationships are accurate or current

---

### 7.9 Epistemic Categorization (`synthesis_agent.py`)

**Location**: Lines 300-400, `_categorize_epistemic_type()` method

**HARDCODED KEYWORD LISTS**:

**FACT indicators**:
```python
fact_indicators = [
    "published",
    "reported",
    "announced",
    "stated",
    "according to",
    "data shows",
    "survey found",
    "statistics indicate",
    "% of",
    "total of",
    "number of"
]
```

**INFERENCE indicators**:
```python
inference_indicators = [
    "therefore",
    "thus",
    "suggests",
    "indicates",
    "implies",
    "likely",
    "probably",
    "may",
    "could",
    "appears to"
]
```

**ASSUMPTION indicators**:
```python
assumption_indicators = [
    "assuming",
    "expected to",
    "projected",
    "anticipated",
    "based on trends",
    "estimated",
    "forecasted"
]
```

**Classification Algorithm**:
```python
def _categorize_epistemic_type(self, text: str) -> str:
    """Categorize text as FACT, INFERENCE, or ASSUMPTION."""
    text_lower = text.lower()

    # Check for fact indicators
    if any(indicator in text_lower for indicator in fact_indicators):
        return "FACT"

    # Check for inference indicators
    if any(indicator in text_lower for indicator in inference_indicators):
        return "INFERENCE"

    # Check for assumption indicators
    if any(indicator in text_lower for indicator in assumption_indicators):
        return "ASSUMPTION"

    # Default: INFERENCE (if uncertain)
    return "INFERENCE"
```

**HARDCODED LOGIC**:
- Keyword-based classification (no semantic understanding)
- Default to INFERENCE if no keywords match
- No confidence scoring
- No validation against ground truth

**Limitations**:
- False positives: "This appears to be a fact" → classified as INFERENCE
- False negatives: "The report showed improvements" → might miss "FACT" classification
- No handling of complex statements (mixed types)
- No temporal reasoning (past facts vs future assumptions)

---

### 7.10 Summary of All Hardcoded Elements

| Component | What's Hardcoded | Location | Impact |
|-----------|-----------------|----------|--------|
| **Retrieval** | k=30 chunks | `config.py:24` | Limits coverage to 30% of database |
| **Synthesis** | MAX_SYNTHESIS_CHUNKS=30 | `config.py:27` | Always uses exactly 30 chunks |
| **Strategic Keywords** | 5 strategic terms | `evidence_agent.py:355-361` | **USER'S CONCERN** - not dynamic |
| **Organization Keywords** | PRIMARY/STRATEGIC lists | `evidence_agent.py:460-520` | Requires manual updates per org |
| **Quality Thresholds** | 90/75/50% for EXCELLENT/GOOD/ADEQUATE | `config.py:30-32` | Arbitrary, not validated |
| **Max Iterations** | 5 iterations | `config.py:35` | Prevents exhaustive search |
| **Gap Thresholds** | 10 sources, 50% dominance, 5 facts | `critique_agent.py:180-250` | Arbitrary values |
| **Convergence** | 80% overlap | `critique_agent.py:280` | May stop too early/late |
| **Entity Mappings** | 27 entities, 112 aliases | `entity_mappings.json` | Manual maintenance |
| **Knowledge Graph** | 146 entities, relationships | `knowledge_graph_improved.json` | Manual maintenance |
| **Epistemic Keywords** | FACT/INFERENCE/ASSUMPTION indicators | `synthesis_agent.py:300-400` | Keyword-based only |
| **LLM Model** | gpt-4o | `config.py:38` | Fixed model choice |
| **Temperature** | 0.5 | `config.py:39` | Fixed creativity level |

**Total Hardcoded Values**: 50+ distinct values, thresholds, and keyword lists

**None of these are learned, tuned, or validated** - all are manual choices based on intuition and limited testing.

---

## 8. Document Ranking and Affinity System

### 8.1 Overview

After semantic search retrieves chunks, the system **ranks** (not filters) them using a **3-tier organization affinity system**.

**Previous Approach (REMOVED)**: STRICT mode that **filtered out** non-organization docs
**Current Approach**: Ranks all docs but **reorders** them by relevance

**3 Tiers**:
1. **Tier 3 (PRIMARY)**: Organization-specific documents
2. **Tier 2 (STRATEGIC)**: National strategic plans, NHS England frameworks
3. **Tier 1 (GENERAL)**: Other NHS/health context documents

**Location**: `evidence_agent.py`, lines 460-560

---

### 8.2 Tier Classification Logic

**Method**: `_rank_by_organization_affinity(results, query)`

**Algorithm**:
```python
def _rank_by_organization_affinity(self, results: List[Dict], query: str) -> List[Dict]:
    """Rank documents by organization affinity (3-tier system)."""

    # Extract target organization from query
    target_org = self._extract_target_organization(query)

    # Classify each document into tiers
    tier3_primary = []
    tier2_strategic = []
    tier1_general = []

    for doc in results:
        source = doc["metadata"].get("source", "").lower()
        content = doc["content"].lower()
        org = doc["metadata"].get("organization", "").lower()

        # Tier 3: PRIMARY (organization-specific)
        if self._is_primary_org_doc(doc, target_org):
            tier3_primary.append(doc)

        # Tier 2: STRATEGIC (national/system-level)
        elif self._is_strategic_doc(doc):
            tier2_strategic.append(doc)

        # Tier 1: GENERAL (other)
        else:
            tier1_general.append(doc)

    # Sort within each tier by similarity score
    tier3_sorted = sorted(tier3_primary, key=lambda x: x["similarity_score"], reverse=True)
    tier2_sorted = sorted(tier2_strategic, key=lambda x: x["similarity_score"], reverse=True)
    tier1_sorted = sorted(tier1_general, key=lambda x: x["similarity_score"], reverse=True)

    # Concatenate: PRIMARY → STRATEGIC → GENERAL
    return tier3_sorted + tier2_sorted + tier1_sorted
```

---

### 8.3 Tier 3: PRIMARY Classification

**Method**: `_is_primary_org_doc(doc, target_org)`

**HARDCODED KEYWORD LISTS** (must be maintained per organization):

```python
def _is_primary_org_doc(self, doc: Dict, target_org: str) -> bool:
    """Check if document is PRIMARY (organization-specific)."""

    source = doc["metadata"].get("source", "").lower()
    content = doc["content"].lower()
    org_metadata = doc["metadata"].get("organization", "").lower()

    # HARDCODED: LYPFT-specific keywords
    lypft_keywords = [
        "lypft",
        "leeds and york partnership nhs foundation trust",
        "leeds and york partnership",
        "leeds york partnership",
    ]

    # HARDCODED: LCH-specific keywords
    lch_keywords = [
        "leeds community healthcare",
        "lch trust",
        "lch nhs",
    ]

    # HARDCODED: LTHT-specific keywords
    ltht_keywords = [
        "leeds teaching hospitals",
        "ltht",
        "leeds teaching hospitals nhs trust",
    ]

    # Select keywords based on target organization
    if "lypft" in target_org or "leeds and york partnership" in target_org:
        keywords = lypft_keywords
    elif "lch" in target_org or "leeds community" in target_org:
        keywords = lch_keywords
    elif "ltht" in target_org or "leeds teaching" in target_org:
        keywords = ltht_keywords
    else:
        keywords = []

    # Check if any keyword appears in source, content, or metadata
    for keyword in keywords:
        if keyword in source or keyword in content or keyword in org_metadata:
            return True

    return False
```

**HARDCODED ELEMENTS**:
- Keyword lists for each organization (LYPFT, LCH, LTHT)
- Organization detection logic (if "lypft" in target_org...)
- Matching strategy (simple substring search)

**Limitations**:
- New organizations require code changes
- Keyword lists must be manually maintained
- No fuzzy matching (e.g., "Leeds & York" vs "Leeds and York")
- No semantic matching (e.g., "mental health trust in Leeds" wouldn't match LYPFT)

---

### 8.4 Tier 2: STRATEGIC Classification

**Method**: `_is_strategic_doc(doc)`

**HARDCODED STRATEGIC KEYWORDS**:
```python
def _is_strategic_doc(self, doc: Dict) -> bool:
    """Check if document is STRATEGIC (national/system-level)."""

    source = doc["metadata"].get("source", "").lower()
    content = doc["content"].lower()

    # HARDCODED: Strategic document keywords
    strategic_keywords = [
        "nhs england",
        "national strategy",
        "10-year plan",
        "health plan england",
        "long-term plan",
        "planning framework",
        "operational planning guidance",
        "nhs long term plan",
        "workforce plan",
        "digital health strategy",
        "integrated care system",
        "system planning",
        "medium-term planning framework",
        "priorities and operational planning",
        "delivering change together"
    ]

    # Check if any strategic keyword appears
    for keyword in strategic_keywords:
        if keyword in source or keyword in content:
            return True

    return False
```

**Why these keywords?**
- Designed to capture NHS England policy documents
- Includes key document titles (e.g., "10-year plan", "long-term plan")
- Includes strategic themes (e.g., "integrated care system", "workforce plan")

**Limitations**:
- Only works for explicitly mentioned terms
- New strategic documents require manual keyword additions
- Can't detect strategic importance through semantic understanding
- May miss documents with different naming conventions (e.g., "decade-long health strategy")

---

### 8.5 Tier 1: GENERAL Classification

**Default Category**: Any document not classified as PRIMARY or STRATEGIC.

**No Keyword Matching** - just a catch-all for:
- Other NHS trust documents
- Local authority documents
- Partnership documents not explicitly marked strategic
- Generic health policy documents

---

### 8.6 Document Tagging for Transparency

**Purpose**: Tag each document with relevance level for reporting

**Method**: `_tag_documents_by_relevance(results, query)`

**Algorithm**:
```python
def _tag_documents_by_relevance(self, results: List[Dict], query: str) -> List[Dict]:
    """Add relevance tags to documents (PRIMARY/STRATEGIC/GENERAL)."""

    target_org = self._extract_target_organization(query)

    for doc in results:
        if self._is_primary_org_doc(doc, target_org):
            doc["relevance_tag"] = "PRIMARY"
        elif self._is_strategic_doc(doc):
            doc["relevance_tag"] = "STRATEGIC"
        else:
            doc["relevance_tag"] = "GENERAL"

    return results
```

**Used in Reporting**: Tags appear in final report source lists

**Example Output**:
```markdown
## Sources Consulted

1. [PRIMARY] `LYPFT Annual-Report-and-Accounts-2024-25.md` - 2025-06-30 (15 chunks)
2. [STRATEGIC] `NHS England _ Planning framework for the NHS in England.md` - 2025-09-08 (2 chunks)
3. [GENERAL] `Leeds Community Annual-report-2024-2025.md` - 2024-06-30 (3 chunks)
```

---

### 8.7 Example: Full Ranking Flow

**Scenario**: Query = "What are LYPFT priorities for the next 12 months?"

**Step 1: Semantic Search Retrieves 30 Chunks**
```
Chunk 1: LYPFT Annual Report 2024-25 (similarity: 0.92)
Chunk 2: NHS England 10-year plan (similarity: 0.89)
Chunk 3: LCH Trust Board Papers (similarity: 0.88)
Chunk 4: LYPFT Strategy 2025-2030 (similarity: 0.87)
Chunk 5: Leeds Health Wellbeing Strategy (similarity: 0.85)
... (25 more chunks)
```

**Step 2: Classify into Tiers**
```
Tier 3 (PRIMARY):
- Chunk 1: LYPFT Annual Report (0.92)
- Chunk 4: LYPFT Strategy (0.87)
[Total: 2 chunks]

Tier 2 (STRATEGIC):
- Chunk 2: NHS England 10-year plan (0.89)
- Chunk 5: Leeds Health Wellbeing Strategy (0.85)
[Total: 2 chunks]

Tier 1 (GENERAL):
- Chunk 3: LCH Trust Board Papers (0.88)
- ... (24 more chunks)
[Total: 26 chunks]
```

**Step 3: Sort Within Tiers by Similarity**
```
Tier 3 sorted: [Chunk 1 (0.92), Chunk 4 (0.87)]
Tier 2 sorted: [Chunk 2 (0.89), Chunk 5 (0.85)]
Tier 1 sorted: [Chunk 3 (0.88), ...]
```

**Step 4: Concatenate Tiers**
```
Final Ranked Order:
1. Chunk 1: LYPFT Annual Report (0.92) [PRIMARY]
2. Chunk 4: LYPFT Strategy (0.87) [PRIMARY]
3. Chunk 2: NHS England 10-year plan (0.89) [STRATEGIC]
4. Chunk 5: Leeds Health Wellbeing Strategy (0.85) [STRATEGIC]
5. Chunk 3: LCH Trust Board Papers (0.88) [GENERAL]
... (25 more)
```

**Key Observation**: LCH chunk (0.88 similarity) is ranked BELOW NHS England chunk (0.89) and Leeds Health Strategy (0.85) because STRATEGIC tier is prioritized over GENERAL tier, even when similarity scores are close.

---

## 9. Iterative Refinement Loop

### 9.1 Loop Architecture

**Purpose**: Improve evidence quality through multiple retrieval rounds

**Orchestrator Loop** (`orchestrator.py`, lines 142-181):
```python
iteration_results = []
critique_results = []
iteration_num = 1

while iteration_num <= self.max_iterations:  # HARDCODED: max_iterations=5
    print(f"\n{'='*80}")
    print(f"ITERATION {iteration_num}")
    print(f"{'='*80}")

    # Get previous gaps (empty on first iteration)
    previous_gaps = critique_results[-1]["gaps"] if critique_results else []

    # STEP 1: Evidence Agent - Retrieve evidence
    evidence_result = self.evidence_agent.search(
        query=query,
        iteration_num=iteration_num,
        previous_gaps=previous_gaps,
        k=Config.DEFAULT_RETRIEVAL_K,  # k=30
    )
    iteration_results.append(evidence_result)

    # STEP 2: Critique Agent - Analyze quality and identify gaps
    critique_result = self.critique_agent.analyze(
        evidence_result=evidence_result,
        iteration_history=iteration_results[:-1],  # Exclude current
        query=query,
    )
    critique_results.append(critique_result)

    # STEP 3: Check stopping criteria
    if not critique_result["continue_iteration"]:
        print("STOPPING CRITERIA MET")
        break

    iteration_num += 1

# STEP 4: Synthesis Agent - Generate final report
synthesis_result = self.synthesis_agent.synthesize(
    query=query,
    iteration_results=iteration_results,
    final_critique=critique_results[-1],
)
```

---

### 9.2 Stopping Criteria Decision Tree

**Evaluated After Each Iteration** (`critique_agent.py`, lines 120-150):

```python
def analyze(self, evidence_result: Dict, iteration_history: List[Dict], query: str) -> Dict:
    """Analyze evidence quality and decide whether to continue."""

    # Calculate metrics
    confidence_score = self._calculate_confidence(evidence_result)
    convergence_detected = self._detect_convergence(evidence_result, iteration_history)
    gaps = self._identify_gaps(evidence_result)

    # Determine quality
    overall_quality = self._calculate_quality(confidence_score, gaps)

    # STOPPING CRITERIA LOGIC
    continue_iteration = True

    # Stop if EXCELLENT
    if overall_quality == "EXCELLENT":
        continue_iteration = False

    # Stop if GOOD + convergence
    elif overall_quality == "GOOD" and convergence_detected:
        continue_iteration = False

    # Stop if ADEQUATE + convergence + no high-priority gaps
    elif overall_quality == "ADEQUATE" and convergence_detected:
        high_gaps = [g for g in gaps if g.get("severity") == "HIGH"]
        if not high_gaps:
            continue_iteration = False

    # Always stop at max iterations (handled by orchestrator)

    return {
        "confidence_score": confidence_score,
        "overall_quality": overall_quality,
        "continue_iteration": continue_iteration,
        "convergence_detected": convergence_detected,
        "gaps": gaps,
    }
```

**Decision Tree**:
```
Is quality EXCELLENT (90%+ confidence, 0 high gaps)?
├─ YES → STOP
└─ NO → Continue

Is quality GOOD (75%+ confidence, 0 high gaps) AND convergence detected?
├─ YES → STOP
└─ NO → Continue

Is quality ADEQUATE (50%+ confidence, ≤1 high gap) AND convergence detected AND no high-priority gaps?
├─ YES → STOP
└─ NO → Continue

Is iteration_num ≥ MAX_ITERATIONS (5)?
├─ YES → STOP (forced)
└─ NO → Continue
```

---

### 9.3 Convergence Detection

**Purpose**: Detect when additional iterations aren't finding new evidence

**Algorithm** (`critique_agent.py`, lines 260-290):
```python
def _detect_convergence(self, current_result: Dict, iteration_history: List[Dict]) -> bool:
    """Detect if we're seeing repeated evidence."""

    if not iteration_history:
        return False  # Can't converge on first iteration

    # Get source lists from current and previous iteration
    current_sources = set(
        chunk["metadata"]["source"] for chunk in current_result["results"]
    )
    previous_sources = set(
        chunk["metadata"]["source"] for chunk in iteration_history[-1]["results"]
    )

    # Calculate overlap
    overlap = len(current_sources & previous_sources)
    total = len(current_sources)
    overlap_ratio = overlap / total if total > 0 else 0

    # HARDCODED: 80% overlap = convergence
    if overlap_ratio > 0.8:
        print(f"[CONVERGENCE] {overlap_ratio:.0%} source overlap detected")
        return True

    return False
```

**Example**:
```
Iteration 1 Sources: [LYPFT Annual Report, NHS 10-year plan, LCH Strategy, LTHT Board Papers, Healthy Leeds Plan]
Iteration 2 Sources: [LYPFT Annual Report, NHS 10-year plan, LCH Strategy, LTHT Board Papers, Leeds Health Strategy]

Overlap: 4 out of 5 sources (80%) → CONVERGENCE DETECTED
```

**HARDCODED THRESHOLD**: 80% overlap

**Why 80%?** Arbitrary - not validated through experimentation.

**Potential Issues**:
- May declare convergence too early (more diverse sources exist but weren't retrieved)
- Doesn't account for content overlap (could retrieve different chunks from same sources)
- Noisy retrieval (query expansion variations) could prevent convergence

---

### 9.4 Gap-Based Query Refinement

**Purpose**: Use identified gaps to refine search in next iteration

**Gap Structure**:
```python
{
    "severity": "HIGH | MEDIUM | LOW",
    "category": "coverage | source_diversity | recency | data_quality",
    "description": "Human-readable gap description",
    "action": "Suggested action to address gap"
}
```

**How Gaps Influence Next Iteration** (`evidence_agent.py`, lines 363-375):
```python
# STEP 4: Gap-based expansion (if iteration > 1)
if iteration_num > 1 and previous_gaps:
    gap_keywords = []
    for gap in previous_gaps:
        if gap.get("severity") in ["HIGH", "MEDIUM"]:
            # Extract suggested search terms from gap description
            gap_action = gap.get("action", "")
            if "search for" in gap_action.lower():
                # Simple keyword extraction
                terms = gap_action.split("search for")[-1].strip()
                gap_keywords.append(terms)

    if gap_keywords:
        expanded_query = f"{expanded_query} {' '.join(gap_keywords)}"
        print(f"[GAP REFINEMENT] Added terms from {len(gap_keywords)} gaps")
```

**Example**:
```
Iteration 1 Result:
- Gap identified: "Limited workforce planning evidence"
- Action: "Search for workforce development and retention"

Iteration 2 Query Expansion:
- Original: "What are LYPFT priorities?"
- With gap terms: "What are LYPFT priorities? workforce development and retention"
```

**Limitation**: Very simplistic keyword extraction - doesn't understand semantic intent of gaps.

---

### 9.5 Iteration Example: Full Flow

**Query**: "What are LYPFT priorities over the next 12 months?"

**Iteration 1**:
```
Evidence Agent:
- Retrieves 30 chunks (k=30)
- Sources: 6 documents
- Chunks from LYPFT Annual Report: 15
- Chunks from other sources: 15

Critique Agent:
- Confidence: 55% (ADEQUATE)
- Quality: ADEQUATE
- Gaps detected:
  - [MEDIUM] Limited source diversity (6/30 documents)
  - [MEDIUM] Over 50% chunks from LYPFT Annual Report
- Convergence: No (first iteration)
- Continue: YES
```

**Iteration 2**:
```
Evidence Agent:
- Query expanded with gap terms: "workforce development", "service transformation"
- Retrieves 30 chunks (k=30)
- Sources: 9 documents (improved!)
- Chunks from LYPFT Annual Report: 16
- Chunks from NHS 10-year plan: 3
- Chunks from other sources: 11

Critique Agent:
- Confidence: 80% (GOOD)
- Quality: GOOD
- Gaps detected:
  - [MEDIUM] Over 50% chunks from LYPFT Annual Report (still dominant)
  - [LOW] Insufficient factual data (4 facts found)
- Convergence: YES (80% source overlap with Iteration 1)
- Continue: NO (GOOD quality + convergence)
```

**Synthesis**:
```
- Aggregates 60 chunks from both iterations
- Deduplicates: 41 unique chunks
- Ranks: PRIMARY → STRATEGIC → GENERAL
- Selects top 30 chunks
- Generates final report
```

**Final Output**:
```
Report:
- Confidence: 80%
- Quality: GOOD
- Iterations: 2
- Sources: 9 documents
- Chunks: 41 unique (30 used in synthesis)
```

---

### 9.6 Why Iteration Helps

**Benefits**:
1. **Coverage Improvement**: More diverse sources across iterations
2. **Gap Filling**: Targeted retrieval based on identified gaps
3. **Quality Assurance**: Continue until acceptable quality reached
4. **Transparency**: Track improvement across iterations in report

**Example Improvement**:
```
Iteration 1:
- 6 documents
- 20% coverage
- Confidence: 55%
- Missing NHS 10-year plan

Iteration 2:
- 9 documents
- 30% coverage
- Confidence: 80%
- Includes NHS 10-year plan (retrieved via strategic keywords)
```

**Cost Trade-off**:
- More iterations = higher LLM API costs
- Iteration 1: ~30k tokens
- Iteration 2: ~30k tokens
- Synthesis: ~50k tokens
- **Total**: ~110k tokens per 2-iteration analysis (vs ~80k for single iteration)

---

## 10. Limitations and Current Issues

### 10.1 User-Identified Issues

**Quote**: *"This isnt very dynamic is it, if i have to hard code these words."*

**Context**: User observed that strategic keywords are hardcoded in `evidence_agent.py`:
```python
strategic_terms = [
    "10-year plan",
    "health plan England",
    "national health strategy",
    "NHS England planning framework",
    "long-term planning"
]
```

**Problem**: New strategic documents or different policy domains require manual code changes.

**Example Scenario**:
- New document published: "NHS 5-Year Workforce Transformation Plan"
- Current system: Won't retrieve it unless "5-Year Workforce Transformation Plan" is added to hardcoded list
- Dynamic system would: Automatically recognize document importance and retrieve it

---

### 10.2 Semantic Search Limitations

**Issue**: Embedding-based semantic search doesn't always capture strategic importance

**Example**:
```
Query: "What are LYPFT priorities over the next 12 months?"
Query Embedding: [0.23, -0.45, 0.67, ...]  # Vector representation

NHS 10-year plan content: "The NHS Long Term Plan sets out a vision for the NHS over the next 10 years..."
Content Embedding: [0.15, -0.52, 0.71, ...]

Cosine Similarity: 0.65 (not in top 30 results)
```

**Why this happens**:
- Query asks about "LYPFT" but document discusses "NHS England"
- Semantic similarity is based on word co-occurrence patterns
- Strategic connection ("NHS national plans influence LYPFT priorities") is not captured in embeddings

**Current Workaround**: Hardcode strategic keywords to force retrieval

**Better Solutions** (not implemented):
1. **Hybrid Search**: Combine semantic + keyword + metadata filters
2. **Document Hierarchy**: Model relationships (national → system → organization)
3. **Citation Network**: Use document citations to infer importance
4. **Metadata-Based Boosting**: Tag documents with `document_type: STRATEGIC_PLAN` and boost in ranking

---

### 10.3 Knowledge Graph Limitations

**Issue 1: Shallow Traversal**
- Only 1-hop relationships explored
- Strategic connections may require 2-3 hops
- Example: "LYPFT" → "Leeds Health and Care Partnership" (found)
- Example: "LYPFT" → "Leeds Health and Care Partnership" → "Healthy Leeds Plan" → "NHS 10-year plan" (NOT found)

**Issue 2: Manual Maintenance**
- All 146 entities manually created
- All relationships manually encoded
- No automatic relationship discovery from documents
- Relationships can become outdated (e.g., partnerships that ended)

**Issue 3: No Semantic Understanding**
- Relationships are symbolic (PROVIDES, COLLABORATES_WITH)
- No understanding of what relationship means for query relevance
- Can't filter relationships by query context (e.g., "workforce" query should prioritize workforce-related relationships)

**Example**:
```json
{
    "id": "LYPFT",
    "relationships": [
        {"type": "PROVIDES", "target": "Mental_Health_Services"},
        {"type": "PROVIDES", "target": "Learning_Disability_Services"},
        {"type": "COLLABORATES_WITH", "target": "LCH"},
        {"type": "PART_OF", "target": "Leeds_Health_Care_Partnership"}
    ]
}
```

**Query**: "What are LYPFT workforce priorities?"

**Current Behavior**: Adds ALL relationships (Mental Health Services, Learning Disability Services, LCH, Leeds Health Care Partnership)

**Desired Behavior**: Only add workforce-relevant relationships (e.g., HR partnerships, training collaborations)

---

### 10.4 Entity Resolution Limitations

**Issue 1: Manual Alias Curation**
- 27 entities with 112 aliases manually defined
- New organizations require manual additions
- Aliases must be manually discovered and added

**Issue 2: No Fuzzy Matching**
- "LYPFT" vs "L&YPFT" vs "LYPFT Trust" - requires all variations in alias list
- Typos not handled (e.g., "LYPFY" wouldn't match "LYPFT")

**Issue 3: No Validation**
- No check that aliases actually appear in corpus
- Can't detect new aliases that emerge in documents (e.g., "Leeds Partnership" as informal abbreviation)

**Example**:
```json
{
    "Leeds and York Partnership NHS Foundation Trust": {
        "aliases": ["LYPFT", "Leeds and York Partnership", ...]
    }
}
```

**Query**: "What are L&YP priorities?"

**Current Behavior**: "L&YP" not in alias list → no expansion → poor retrieval

**Better Solution**: Fuzzy matching, TF-IDF-based alias discovery, or LLM-based entity linking

---

### 10.5 Gap Detection Limitations

**Issue: Arbitrary Thresholds**

All gap detection thresholds are **hardcoded and not validated**:
- Minimum sources: 10 (why not 8 or 12?)
- Source dominance: 50% (why not 40% or 60%?)
- Minimum facts: 5 (why not 3 or 7?)
- Recency cutoff: 2023 (why not 2022 or 2024?)
- Old evidence threshold: 30% (why not 25% or 35%?)

**No Ground Truth Validation**: These thresholds weren't validated against:
- Human expert assessments
- Historical query performance
- User satisfaction scores

**Example**:
```python
if evidence_result["unique_sources"] < 10:  # Why 10?
    gaps.append({"severity": "MEDIUM", "description": "Limited source diversity"})
```

**Better Approach**: Learn thresholds from data:
- Collect user feedback on report quality
- Correlate quality with metrics (source diversity, fact count, etc.)
- Optimize thresholds to maximize user satisfaction

---

### 10.6 Epistemic Categorization Limitations

**Issue: Keyword-Based Classification**

Current approach uses **hardcoded keyword lists**:
```python
fact_indicators = ["published", "reported", "announced", ...]
inference_indicators = ["therefore", "suggests", "implies", ...]
assumption_indicators = ["assuming", "expected to", "projected", ...]
```

**Problems**:
1. **False Positives**: "This appears to be a fact" → classified as INFERENCE (keyword "appears")
2. **False Negatives**: "The report showed improvements" → might miss FACT classification (no explicit keyword)
3. **No Context Understanding**: "The study suggests X" (FACT - reporting a finding) vs "This suggests X" (INFERENCE - making a claim)
4. **No Confidence Scoring**: Binary classification (FACT or INFERENCE), no "80% confident this is a FACT"

**Example**:
```
Text: "NHS England announced the 10-year plan in January 2025."
Classification: FACT (correct - keyword "announced")

Text: "The plan aims to improve workforce capacity."
Classification: INFERENCE (incorrect - should be FACT from plan document)

Text: "This announcement suggests a shift in policy."
Classification: INFERENCE (correct - keyword "suggests")

Text: "The report states that 80% of trusts are understaffed."
Classification: FACT (correct - keyword "report" + statistic)
```

**Better Approach**: LLM-based classification with confidence scores:
```python
{
    "text": "The plan aims to improve workforce capacity.",
    "epistemic_type": "FACT",
    "confidence": 0.85,
    "reasoning": "Direct statement from official plan document"
}
```

---

### 10.7 Context Stuffing Limitations

**Issue 1: Fixed Chunk Limit**
- Always selects exactly 30 chunks (MAX_SYNTHESIS_CHUNKS=30)
- Doesn't adapt based on:
  - Query complexity (simple vs complex questions)
  - Evidence quality (high-quality evidence might need fewer chunks)
  - Model context window (GPT-4 has 128k tokens, we use ~18%)

**Issue 2: No Dynamic Token Counting**
- System assumes average chunk size (~500 tokens)
- Doesn't actually measure token usage
- Could exceed limits with very long chunks or complex queries

**Issue 3: "Lost in the Middle" Effect**
- Research shows LLMs perform worse when relevant info is in middle of long contexts
- Current approach: Simply concatenates 30 chunks in order
- No optimization for chunk positioning

**Better Approach**:
1. **Dynamic Chunk Selection**: Use more chunks for complex queries, fewer for simple ones
2. **Token Budget Management**: Actually count tokens and optimize selection
3. **Strategic Positioning**: Place most important chunks at beginning and end of context

---

### 10.8 Ranking System Limitations

**Issue 1: Organization-Specific Hardcoding**
- Each organization needs manual keyword list
- LYPFT keywords: ["LYPFT", "Leeds and York Partnership", ...]
- LCH keywords: ["LCH", "Leeds Community Healthcare", ...]
- LTHT keywords: ["LTHT", "Leeds Teaching Hospitals", ...]

**Scaling Problem**: Adding new organization requires code changes

**Issue 2: Strategic Keywords Maintenance**
- Strategic keywords manually maintained:
  ```python
  strategic_keywords = ["NHS England", "10-year plan", "national strategy", ...]
  ```
- New strategic documents require manual additions
- Different policy domains (education, housing) would need separate lists

**Issue 3: No Semantic Ranking**
- Rankings based on keyword matching, not semantic relevance
- Can't detect strategic importance without explicit keywords
- Example: "decade-long health initiative" wouldn't match "10-year plan"

**Better Approach**:
1. **Metadata-Based Ranking**: Tag documents with `org`, `doc_type`, `strategic_level` in database
2. **Learned Ranking**: Train model to predict document relevance
3. **Hybrid Ranking**: Combine semantic similarity + metadata + learned weights

---

### 10.9 System-Wide Issues

**Issue 1: No Feedback Loop**
- System doesn't learn from:
  - User corrections
  - Quality assessments
  - Usage patterns
- Same queries will produce same results (given same database)

**Issue 2: No A/B Testing**
- Can't compare different configurations
- No systematic way to validate improvements
- Changes made based on intuition, not data

**Issue 3: No Observability**
- Limited logging of:
  - Why specific documents were retrieved
  - How rankings were calculated
  - Why stopping criteria were met
- Hard to debug poor results

**Issue 4: No Personalization**
- Same results for all users
- Can't adapt to:
  - User expertise level
  - Previous queries
  - User preferences

**Better Approach**: Build feedback and evaluation infrastructure:
1. **User Feedback Collection**: Thumbs up/down, relevance ratings
2. **A/B Testing Framework**: Compare configurations systematically
3. **Observability**: Log all decisions with reasoning
4. **Personalization**: User profiles and query history

---

### 10.10 Cost and Performance

**Current Costs** (estimated per query):
```
Iteration 1 Evidence Retrieval:
- Embedding API call: ~30 tokens (query)
- ChromaDB search: ~10ms
- Cost: ~$0.0001

Iteration 1 Critique:
- LLM call: ~5k tokens input, ~500 tokens output
- Cost: ~$0.03

Iteration 2 Evidence Retrieval:
- Same as Iteration 1
- Cost: ~$0.0001

Iteration 2 Critique:
- Same as Iteration 1
- Cost: ~$0.03

Final Synthesis:
- LLM call: ~25k tokens input, ~4k tokens output
- Cost: ~$0.20

Total per query: ~$0.26
```

**Scaling Issues**:
- 100 queries/day = $26/day = $780/month
- 1000 queries/day = $260/day = $7,800/month
- Max iterations (5) would increase costs by ~2x

**Performance Bottlenecks**:
- LLM API calls: ~2-5 seconds per iteration
- Total time per query: ~10-20 seconds (for 2-3 iterations)
- ChromaDB search: ~10-50ms (not a bottleneck)

**Better Approach**:
1. **Caching**: Cache results for identical queries
2. **Early Stopping**: More aggressive stopping criteria to reduce iterations
3. **Batch Processing**: Batch multiple queries for efficiency
4. **Model Selection**: Use cheaper models (GPT-3.5) for critique, GPT-4 only for synthesis

---

## Conclusion

This document has detailed how the multi-agent RAG system works, with particular focus on:

1. **Multi-Agent Architecture**: Evidence, Critique, and Synthesis agents with orchestrated iteration loop
2. **RAG Implementation**: Semantic search → rank → stuff context → LLM generate
3. **Query Expansion**: 4-step pipeline (Entity Resolution → Knowledge Graph → Strategic Keywords → Gap-based)
4. **Knowledge Graph**: JSON-based entity relationships with 1-hop traversal
5. **Context Stuffing**: 3-step selection (deduplicate → rank → limit to 30 chunks)
6. **Hardcoding Patterns**: 50+ hardcoded values, thresholds, and keyword lists documented
7. **Document Ranking**: 3-tier affinity system (PRIMARY → STRATEGIC → GENERAL)
8. **Iterative Refinement**: Quality-based stopping criteria with convergence detection
9. **Limitations**: User-identified hardcoding issue and many other architectural limitations

**Key Takeaway for User's Concern**:

The system currently requires **extensive manual hardcoding** at multiple levels:
- Strategic keywords (5 terms)
- Organization keywords (3 lists)
- Entity mappings (27 entities, 112 aliases)
- Knowledge graph (146 entities, relationships)
- Gap thresholds (50%, 10 sources, 5 facts, etc.)
- Epistemic keywords (FACT/INFERENCE/ASSUMPTION indicators)

**This makes the system brittle and non-adaptive** - exactly the concern the user raised:

> *"This isnt very dynamic is it, if i have to hard code these words."*

**Potential Solutions** (for future discussion):
1. **Metadata-Based Retrieval**: Tag documents with type/importance in database
2. **Learned Document Importance**: Train model to predict strategic relevance
3. **Hierarchical Document Modeling**: Represent org → system → national relationships
4. **Dynamic Threshold Learning**: Learn optimal thresholds from user feedback
5. **LLM-Based Classification**: Replace keyword-based categorization with LLM reasoning
6. **Feedback Loops**: Collect user feedback to continuously improve retrieval

---

**Next Steps**:
1. User reviews this documentation
2. Discuss which hardcoding patterns are most problematic
3. Prioritize solutions (metadata tagging? learned ranking? hybrid search?)
4. Plan implementation approach for making system more dynamic

---

*Document generated: 2025-10-30*
*Author: Multi-Agent RAG System Analysis*
