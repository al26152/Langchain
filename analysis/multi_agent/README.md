# Multi-Agent Iterative RAG System

## Overview

An advanced evidence-gathering system that uses multiple AI agents working together to iteratively search, validate, and synthesize evidence from your document corpus. The system automatically detects gaps in evidence coverage and refines its search until sufficient quality is achieved.

## Key Features

- **Knowledge Graph Integration** ✨ **[NEW]**: Uses entity relationships to expand searches intelligently
- **Iterative Evidence Gathering**: Automatically expands searches based on detected gaps
- **Real-Time Gap Detection**: Alerts you to missing evidence as analysis progresses
- **Epistemic Categorization**: Every claim tagged as FACT / ASSUMPTION / INFERENCE
- **Source Traceability**: All claims fully cited and traceable to source documents
- **Confidence Scoring**: 0-100% confidence based on evidence quality
- **Self-Refinement**: System critiques its own work and improves automatically

## The 4 Agents (+ Knowledge Graph Integration)

### 1. Evidence Agent ✨ **[Enhanced with KG + Metadata-Based Classification]**
- Retrieves relevant chunks from ChromaDB
- **Uses Knowledge Graph to expand queries with related entities**
- **Uses document metadata (type, strategic level, organization) for smart prioritization**
- **Identifies missing relationships between entities**
- Calculates coverage metrics (source count, date distribution)
- Identifies evidence gaps
- Classifies epistemic types (FACT/ASSUMPTION/INFERENCE)
- **Automatically boosts strategic documents (10-year plans, operational guidance) for strategy queries**

### 2. Critique Agent
- Analyzes evidence quality
- Detects gaps in coverage
- Checks epistemic quality (fact ratio, assumption validation)
- Decides whether to continue iterations
- Detects convergence (diminishing returns)

### 3. Synthesis Agent
- Generates LLM-based synthesized answer
- Creates comprehensive markdown report
- Calculates overall confidence score
- Provides epistemic breakdown

### 4. Orchestrator
- Coordinates workflow between agents
- Manages iteration loop
- Enforces stopping criteria
- Aggregates results

## Usage

### Interactive Mode (Recommended)

```bash
python analysis/multi_agent/run_multi_agent.py
```

Then enter your questions when prompted.

### Single Question Mode

```bash
python analysis/multi_agent/run_multi_agent.py --question "What are LCH's key workforce challenges for 2026-2031?"
```

### Custom Options

```bash
python analysis/multi_agent/run_multi_agent.py \
  --question "Your question" \
  --output custom_report.md \
  --max-iterations 7 \
  --model gpt-4o
```

## Example Workflow

```
User: "What are the key workforce challenges for LCH 2026-2031?"

[ITERATION 1] Evidence Agent: Searching for evidence...
[ITERATION 1] Retrieved 18 chunks from 3 documents
[ITERATION 1] Coverage: 10.0% of total documents
[ITERATION 1] Critique Agent: Analyzing evidence quality...
[ITERATION 1] Quality: WEAK
[ITERATION 1] Sources: 3 (10.0%)
[ITERATION 1] Gaps: 4 identified
[ITERATION 1] → Triggering Iteration 2

[ITERATION 2] Evidence Agent: Searching for evidence...
[QUERY EXPANSION] Added: NHS 10-year plan, partnerships
[ITERATION 2] Retrieved 22 chunks from 7 documents
[ITERATION 2] Coverage: 23.3% of total documents
[ITERATION 2] Critique Agent: Analyzing evidence quality...
[ITERATION 2] Quality: ADEQUATE
[ITERATION 2] Sources: 7 (23.3%)
[ITERATION 2] Gaps: 2 identified
[ITERATION 2] → Triggering Iteration 3

[ITERATION 3] Evidence Agent: Searching for evidence...
[ITERATION 3] Retrieved 24 chunks from 8 documents
[ITERATION 3] Coverage: 26.7% of total documents
[ITERATION 3] Critique Agent: Analyzing evidence quality...
[ITERATION 3] Quality: GOOD
[ITERATION 3] Sources: 8 (26.7%)
[ITERATION 3] Gaps: 1 identified
[ITERATION 3] ✓ CONVERGENCE DETECTED (diminishing returns)
[ITERATION 3] ✓ STOPPING (sufficient quality or max iterations)

[SYNTHESIS] Generating final report...
[SYNTHESIS] ✓ Complete - Confidence: 75%

ANALYSIS COMPLETE
Iterations: 3
Sources consulted: 8
Evidence chunks: 24
Confidence: 75%
Quality: GOOD

✓ Report saved: multi_agent_report_20251025_143022.md
```

## Output Report Structure

The generated markdown report includes:

1. **Confidence Assessment**
   - Overall confidence score (0-100%)
   - Sources consulted
   - Evidence chunk count
   - Date freshness metrics

2. **Executive Summary**
   - LLM-synthesized answer with multi-source citations

3. **Epistemic Analysis**
   - FACT count and examples (verified claims)
   - ASSUMPTION count and examples (extrapolations)
   - INFERENCE count and examples (logical conclusions)

4. **Sources Consulted**
   - All documents with dates and chunk counts
   - Freshness indicators (🟢 recent, 🟡 older)

5. **Gaps Identified**
   - High/Medium/Low priority gaps
   - Recommended actions

6. **Iteration Log**
   - What happened in each iteration
   - How evidence improved
   - Convergence detection

## Epistemic Categorization

### FACT
Direct statements from authoritative sources with high confidence.

**Example:**
```markdown
[FACT] LCH employs 5,024 staff as of March 2025
  Source: LCH Annual Report 2024-25, p.12
  Confidence: 95%
```

### ASSUMPTION
Reasonable extrapolations with stated basis and moderate confidence.

**Example:**
```markdown
[ASSUMPTION] Turnover will average 15% over 2026-2031
  Basis: 3-year trend average (14%, 15%, 16%)
  Sources: LCH Annual Reports 2022-2024
  Confidence: 70%
```

### INFERENCE
Logical conclusions derived from facts and assumptions.

**Example:**
```markdown
[INFERENCE] LCH must recruit ~750 staff annually
  Calculation: 5,024 × 0.15 = 754
  Based on: FACT (headcount) + ASSUMPTION (turnover rate)
  Confidence: 70%
```

## Configuration

Default thresholds in `critique_agent.py`:

```python
min_sources = 5              # Minimum sources for ADEQUATE
min_coverage_percent = 15.0  # Minimum % of docs for ADEQUATE
min_recent_percent = 30.0    # Minimum % recent evidence
max_iterations = 5           # Max iterations before stop
```

## Cost & Performance

**Per Strategic Question**:
- **Iterations**: 3-5 (automatic)
- **Time**: 2-4 minutes
- **Cost**: $0.15-0.40 (OpenAI API)
- **Sources**: 5-10 documents consulted
- **Evidence**: 20-40 chunks retrieved

**Cost Breakdown** (per iteration):
- Evidence retrieval: Free (local ChromaDB)
- Epistemic tagging: ~$0.02 (GPT-4o-mini)
- Answer synthesis: ~$0.05 (GPT-4o)
- **Total per iteration**: ~$0.07

## When to Use This vs Other Systems

| Need | Use This | Use Instead |
|------|----------|-------------|
| Strategic questions needing validation | ✓ Multi-Agent | - |
| Quick exploratory question | - | RAG (interactive_query) |
| Entity/relationship mapping | - | Knowledge Graph |
| Theme comparison | - | Theme Analysis |
| Maximum evidence rigor | ✓ Multi-Agent | - |
| Budget-conscious queries | - | RAG (single-pass) |

## Stopping Criteria

The system stops iterating when:

1. **Excellent quality** achieved (score ≥80%)
2. **Good quality** + **convergence detected** (diminishing returns)
3. **Adequate quality** + **convergence** + **no high-priority gaps**
4. **Max iterations** reached (default: 5)

## Troubleshooting

### Issue: "ChromaDB not found"
**Solution**: Run `python pipeline/ingest_pipeline.py` first

### Issue: System stops after 1 iteration
**Likely**: Quality already EXCELLENT (this is good!)
**Check**: Look at confidence score - if >80%, evidence is strong

### Issue: Too many iterations (hitting max)
**Likely**: Question too broad or specific documents missing
**Solution**: Rephrase question or check if relevant docs are in corpus

### Issue: Low confidence scores (<50%)
**Likely**: Insufficient documents on topic or documents too old
**Check**: Gaps section - which documents are missing?

## Architecture

```
User Question
     │
     ▼
Orchestrator (loop controller)
     │
     ├─→ Evidence Agent (retrieves chunks + metrics)
     │        │
     │        ▼
     ├─→ Critique Agent (analyzes + detects gaps)
     │        │
     │        ├─→ Continue? Yes → Loop back
     │        │
     │        └─→ Continue? No → Stop
     │
     ▼
Synthesis Agent (generates report)
     │
     ▼
Markdown Report (with epistemic tags)
```

## Advanced Usage

### Programmatic API

```python
from analysis.multi_agent import Orchestrator
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Initialize
embeddings = OpenAIEmbeddings()
vectordb = Chroma(persist_directory="chroma_db_test", embedding_function=embeddings)
llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

orchestrator = Orchestrator(vectordb, llm, max_iterations=5)

# Run analysis
result = orchestrator.run_analysis("Your strategic question")

# Access results
print(f"Confidence: {result['confidence_score']:.0f}%")
print(f"Quality: {result['quality_rating']}")
print(f"Sources: {result['unique_sources']}")

# Save report
orchestrator.save_report(result, "my_report.md")
```

## How Knowledge Graph Integration Works

The system now uses your pre-built knowledge graph to enhance evidence retrieval:

### Iteration 1: Knowledge Graph Expansion
When you ask a question like "How do LTHT and LCH collaborate on discharges?":

1. **Entity Extraction**: Identifies organizations mentioned (LTHT, LCH)
2. **Relationship Traversal**: Finds related entities in the knowledge graph
3. **Query Expansion**: Adds related services, pathways, and organizations
4. **Enhanced Retrieval**: Searches with expanded context

**Example:**
```
Original Query: "How do LTHT and LCH collaborate?"

KG Identifies:
- Leeds Teaching Hospitals NHS Trust (LTHT)
- Leeds Community Healthcare NHS Trust (LCH)

KG Adds Related Entities:
- Discharge to Assessment (D2A) pathways
- West Yorkshire Community Health Services Collaborative
- Integrated Care Boards
- Mental Health Collaborative

Result: Retrieves 33% more documents with richer context
```

### Iteration 2+: Gap-Based Expansion
Subsequent iterations use gap detection to refine searches:
- Missing themes → Add theme keywords
- Missing relationships → Search for specific connections
- Low coverage → Broaden search scope

### Performance Impact

**Before KG Integration:**
- 6-7 documents per query
- 20-23% document coverage
- ~20 evidence chunks

**After KG Integration:**
- 8-10 documents per query  (+40%)
- 27-33% document coverage (+45%)
- 30-40 evidence chunks (+75%)

## Future Enhancements

Potential improvements:

- [x] **Knowledge Graph integration** ✅ **[COMPLETED]**
- [ ] Contradiction detection (flag when sources disagree)
- [ ] Temporal analysis (track how priorities evolved over time)
- [ ] Interactive refinement (user can guide iterations)
- [ ] Batch question mode (run multiple questions sequentially)
- [ ] Custom stopping criteria (user-defined thresholds)

## Credits

Built on top of:
- LangChain (RAG framework)
- ChromaDB (vector database)
- OpenAI GPT-4o (synthesis)
- OpenAI GPT-4o-mini (classification)

---

**Version**: 2.1.0 (Knowledge Graph Integration + Metadata-Based Classification)
**Last Updated**: October 30, 2025
