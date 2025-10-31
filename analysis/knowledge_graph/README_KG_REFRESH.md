# Knowledge Graph Refresh Guide

**Last Updated:** Oct 31, 2025
**KG Last Built:** Oct 25, 2025 (30 documents)

---

## Quick Start

```bash
# Rebuild the knowledge graph (15-20 minutes, ~$3-5)
python analysis/knowledge_graph/build_knowledge_graph_framework.py
```

Done! The graph is immediately available for next query.

---

## What is the Knowledge Graph?

The **Knowledge Graph** is a structured network of entities and relationships extracted from your documents. It powers:

- **Smart query expansion** - When you ask about "LCH", the system finds related organizations and services
- **Semantic search** - Discovers implicit relationships (services that work together)
- **Better search coverage** - Prevents missing relevant documents due to naming variations
- **Organization context** - Understands partnerships and service networks

### Current Graph Structure

```
Entities (200 total):
  • Organizations: 16 (LCH, LTHT, LYPFT, etc.)
  • Services: 115 (Community Nursing, Mental Health, etc.)
  • Care Pathways: 25 (Discharge, Step-up/down, etc.)
  • Roles: 9 (Clinicians, Medical Directors, etc.)
  • Conditions: 35 (Mental Health, Cancer, etc.)

Relationships (19,374 total):
  • Strong semantic links: 88 (0.5%)
    - provides: 81 relationships
    - uses: 6 relationships
    - manages: 1 relationship
  • Co-mention signals: 19,286 (99.5%)
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

### Relationship Types

**Strong Semantic Relationships** (Use for precise queries)
- `provides`: "Organization A provides Service B" (81 relationships)
- `uses`: "Service A uses Technology B" (6 relationships)
- `manages`: "Role A manages Service B" (1 relationship)

**Co-mention Relationships** (Use for discovery)
- `mentioned_together_in`: "Entity A and B appear in same document" (19,286 relationships)
- Quality varies; useful for finding adjacent topics
- Can include false positives (unrelated concepts in same document)

### Example Relationships

```json
{
  "source": "Leeds Community Healthcare NHS Trust",
  "target": "Community Nursing Service",
  "relationship": "provides"
  // Strong signal: LCH definitely provides this service
}

{
  "source": "Mental Health Service",
  "target": "Primary Care Integration",
  "relationship": "mentioned_together_in"
  // Weak signal: Both appear in documents about integration
  // Might be relevant, might be coincidence
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

**Last Updated:** Oct 31, 2025
**Maintained By:** Project Team
