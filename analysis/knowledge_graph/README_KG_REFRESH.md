# Knowledge Graph Refresh Guide

**Last Updated:** Nov 4, 2025
**KG Last Built:** Nov 4, 2025 (30 documents)
**Status:** ✅ Phase 1 Complete - Confidence scoring, pattern extraction, test suite added

---

## Quick Start

```bash
# Rebuild the knowledge graph (15-20 minutes, ~$3-5)
python analysis/knowledge_graph/build_knowledge_graph_framework.py
```

Done! The graph is immediately available for next query.

---

## Recent Updates (November 4, 2025) - Phase 1 Complete

### Phase 1: Infrastructure & Confidence Scoring

**Testing & Quality Assessment:**
- ✅ `test_kg_quality.py` - Comprehensive KG quality metrics
  - Entity coverage analysis
  - Relationship distribution metrics
  - Connectivity analysis
  - Semantic quality scoring
  - Quality grade: 79.6/100 (Grade B)

**Confidence Scoring System:**
- ✅ All relationships now have confidence scores (0.0-1.0)
  - Explicit relationships: 0.65-0.8 (based on type)
    - `provides`: 0.75 (most reliable)
    - `partners_with`: 0.8 (partnership explicit)
    - `uses`: 0.7 (resource usage)
  - Implicit relationships: 0.0-0.5 (based on co-occurrence frequency)
    - Capped at 0.5 for fair weighting
    - Formula: min(co_mention_count/10, 0.5)

**Pattern-Based Extraction:**
- ✅ `pattern_extractor.py` - High-precision pattern matching
  - Partnerships: 85% confidence ("Board to Board", "partnership with")
  - Care pathways: 75-82% confidence ("discharge pathway", "referral")
  - Service provision: 80% confidence ("X provides Y")
  - Validation against known entities
  - Ready for integration into KG builder (Phase 2)

**Noise Filtering:**
- ✅ `filter_kg_noise.py` - Fixed Unicode encoding issues
- ✅ Removes 99.3% of weak co-mentions with threshold=5
- ✅ Preserves all 145 semantic relationships

**Available Graphs:**
- `knowledge_graph_improved.json` - Main graph with confidence scores
- `knowledge_graph_filtered.json` - Filtered version (99.3% noise reduction)

### How to Validate KG Quality

Use the quality assessment suite to check KG health:

```bash
# Run comprehensive quality assessment
python analysis/knowledge_graph/test_kg_quality.py

# This produces:
# - Entity coverage metrics
# - Relationship distribution
# - Connectivity analysis
# - Quality score (0-100)
# - Recommendations for improvement
```

Or test with actual queries:

```bash
# Run multi-agent analysis with test questions
python analysis/multi_agent/run_multi_agent.py \
  --question "What are LCH's key partnerships?"
```

---

## What is the Knowledge Graph?

The **Knowledge Graph** is a structured network of entities and relationships extracted from your documents. It powers:

- **Smart query expansion** - When you ask about "LCH", the system finds related organizations and services
- **Semantic search** - Discovers implicit relationships (services that work together)
- **Better search coverage** - Prevents missing relevant documents due to naming variations
- **Organization context** - Understands partnerships and service networks

### Current Graph Structure (Phase 1 - Nov 4, 2025)

```
Entities (224 total):
  • Organizations: 24 (LCH, LTHT, LYPFT, NHS England, West Yorkshire ICB, etc.)
  • Services: 118 (Community Nursing, Mental Health, Diabetes Management, etc.)
  • Care Pathways: 16 (Discharge, Referral, Integration, etc.)
  • Roles: 15 (Clinicians, Medical Directors, Managers, etc.)
  • Conditions: 48 (Mental Health, Cancer, Diabetes, Respiratory, etc.)

Relationships (21,510 total):
  • Explicit semantic links: 124 (0.58%)
    - provides: 114 relationships (avg confidence: 0.75)
    - partners_with: 2 relationships (confidence: 0.8)
    - uses: 8 relationships (confidence: 0.7)
  • Implicit co-mention signals: 21,386 (99.42%)
    - Avg confidence: 0.22 (capped at 0.5)
    - Frequency-based weighting applied

Confidence Scoring:
  • All relationships scored 0.0-1.0
  • Explicit avg: 0.74
  • Implicit avg: 0.22
  • Quality grade: B (79.6/100)
```

---

## When to Rebuild

### ✅ DO rebuild when:

| Scenario | Why | Frequency |
|----------|-----|-----------|
| New documents added | ~2-3+ new documents | As needed |
| 30+ days passed | Semantic drift in relationships | Every month |
| Major changes | Organization restructures, new partnerships | As announced |
| Before big analysis | Important strategic decision | Before critical work |

### ❌ DON'T rebuild for:

- Single document minor updates
- Typo fixes in documents
- Small metadata changes
- Weekly reviews (too frequent)

---

## How to Rebuild

### Step 1: Run the builder

```bash
python analysis/knowledge_graph/build_knowledge_graph_framework.py
```

### Step 2: Monitor progress

You'll see output like:

```
[09:45:12] [>>] KNOWLEDGE GRAPH BUILDER - Starting
[09:45:15] [i]  Phase 1: Extracting entities...
[09:45:45] [i]  Found: 200 entities across 30 documents
[09:46:00] [i]  Phase 2: Discovering relationships...
[10:04:32] [OK] Discovered: 19,374 relationships
[10:04:50] [OK] Knowledge graph built: knowledge_graph_improved.json (4.7 MB)
```

### Step 3: Verify success

Check that `knowledge_graph_improved.json` was updated:

```bash
# On Windows PowerShell
(Get-Item knowledge_graph_improved.json).LastWriteTime

# On Mac/Linux
ls -la analysis/knowledge_graph/knowledge_graph_improved.json
```

---

## Understanding Your Graph

### Relationship Types with Confidence Scoring

**Strong Semantic Relationships** (Use for precise queries)
- `provides`: "Organization A provides Service B"
  - Count: 114 relationships
  - Avg confidence: 0.75 (high reliability)
  - Best for: Service discovery, organizational capability search

- `partners_with`: "Organization A partners with Organization B"
  - Count: 2 relationships
  - Confidence: 0.8 (explicit when stated)
  - Best for: Partnership discovery, collaboration networks

- `uses`: "Service A uses Resource/Technology B"
  - Count: 8 relationships
  - Confidence: 0.7 (moderate reliability)
  - Best for: Integration discovery

**Co-mention Relationships** (Use for discovery with caution)
- `mentioned_together_in`: "Entity A and B appear in same document"
  - Count: 21,386 relationships
  - Avg confidence: 0.22 (low, based on frequency)
  - Quality: Varies by document context
  - Best for: Finding adjacent topics, potential connections
  - ⚠️ Note: Can include false positives (unrelated concepts in same document)

### Example Relationships

```json
{
  "source": "Leeds Community Healthcare NHS Trust",
  "target": "Community Nursing Service",
  "relationship": "provides",
  "confidence": 0.75,
  "co_occurrence_count": 12
  // Strong signal: LCH definitely provides this service
  // High confidence from explicit LLM extraction
}

{
  "source": "Mental Health Service",
  "target": "Primary Care Integration",
  "relationship": "mentioned_together_in",
  "confidence": 0.18,
  "co_occurrence_count": 2,
  "documents": ["West_Yorkshire_ICB_Strategy.md"]
  // Weak signal: Both appear together in 2 documents
  // Low confidence - might be relevant or coincidence
  // Use only for discovery, not as strong evidence
}

{
  "source": "Leeds Teaching Hospitals NHS Trust",
  "target": "Leeds Community Healthcare NHS Trust",
  "relationship": "partners_with",
  "confidence": 0.8
  // Very strong signal: Board-to-Board partnership explicitly stated
}
```

---

## Troubleshooting

### Build takes too long (>30 minutes)

**Cause:** Many documents, large chunk processing
**Solution:** It's normal for 30+ documents. Time is acceptable.

### "Out of memory" error

**Cause:** Too many relationships being processed simultaneously
**Solution:**
```bash
# Reduce verbosity to save memory
export DEBUG=0
python analysis/knowledge_graph/build_knowledge_graph_framework.py
```

### Graph file not updating

**Cause:** File permissions or disk full
**Solution:**
```bash
# Check disk space
df -h  # Mac/Linux
wmic logicaldisk get name,size,freespace  # Windows

# Verify write permissions
ls -l analysis/knowledge_graph/
```

### Relationships seem wrong/sparse

**Cause:** Document quality or extraction issues
**Solution:** Check document content:
- Are new documents well-formatted?
- Do they use consistent naming for organizations/services?
- Are sections clearly marked?

---

## Maintenance Schedule

Recommended refresh timeline:

| When | Action | Priority |
|------|--------|----------|
| Every 30 days | Routine refresh | Medium |
| New documents added | Immediate rebuild | High |
| Before major analysis | Verification rebuild | High |
| Quarterly review | Assess quality | Low |

---

## API Costs

Each rebuild costs approximately:

```
Document count: 30
Per-document cost: $0.10 (entity extraction + relationship discovery)
Total: ~$3.00

With 40 documents: ~$4.00
With 50 documents: ~$5.00
```

Budget ~$5 for safe margin.

---

## Next Steps

1. **Decided to rebuild?** → Run the build command above
2. **Want to improve quality?** → See docs about filtering noise
3. **Need architectural changes?** → Review `build_knowledge_graph_framework.py`
4. **Questions?** → Check main README.md Knowledge Graph section

---

## Reference

- **Main guide:** `README.md` (section: "Knowledge Graph Maintenance")
- **Technical docs:** `WIDE_THEN_DEEP_ARCHITECTURE.md`
- **Builder code:** `build_knowledge_graph_framework.py`
- **Graph agent:** `knowledge_graph_agent.py` (uses the graph)

---

## Coming Soon (Phases 2-7)

Following phases will enhance the KG further:

- **Phase 2**: Pattern-based extraction integration (partnerships, pathways, services)
- **Phase 3**: Metadata-driven service attribution from document ownership
- **Phase 4**: Enhanced LLM extraction with targeted two-pass approach
- **Phase 5**: Entity resolution and relationship deduplication
- **Phase 6**: KG Agent integration with confidence-weighted query expansion
- **Phase 7**: Automated refresh script and pipeline integration

Track progress on the `enhancement/KG` branch.

---

**Last Updated:** Nov 4, 2025
**Phase:** 1 of 7 (Infrastructure & Confidence Scoring)
**Maintained By:** Project Team
**Repository Branch:** `enhancement/KG`
