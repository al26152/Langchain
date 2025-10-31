# Knowledge Graph Filtering Guide - Phase 1: Reduce Noise

**Date:** October 31, 2025
**Status:** Ready to Implement
**Tool:** `filter_kg_noise.py`

---

## Problem Statement

Current KG Quality (Before Filtering):
- **Total relationships:** 19,374
- **Strong semantic relationships:** 88 (0.5%) - provides, uses, manages
- **Weak co-mention relationships:** 19,286 (99.5%) - mentioned_together_in
- **Problem:** 99.5% noise makes query expansion unreliable

**Impact of Noise:**
- Entity expansion pulls in unrelated topics
- Query drift - search strays from original intent
- False positives in relationship discovery
- Lower confidence in expanded queries

---

## Phase 1 Solution: Frequency Threshold Filtering

**Strategy:** Keep only co-mention pairs that appear 5+ times in documents

**Rationale:**
- Single mentions are likely coincidental
- Multiple mentions indicate genuine relationship/context
- 5+ is a good balance: removes 85% noise, keeps strong signals

### Expected Results (With 5+ Threshold)

**Estimated Impact:**
```
Original relationships: 19,374
  ├── Semantic (keep all): 88
  └── Co-mentions: 19,286
      ├── 5+ mentions (keep): ~2,900
      └── <5 mentions (remove): ~16,386

Filtered relationships: ~2,988
  ├── Semantic: 88 (0.3%)
  ├── Strong co-mentions: 2,900 (97%)

Reduction: 85% of relationships removed
Result: Much cleaner graph, better query expansion
```

---

## How to Use

### Basic Usage

```bash
# Run with default threshold (5)
python analysis/knowledge_graph/filter_kg_noise.py
```

**What happens:**
1. Loads `knowledge_graph_improved.json` (from KG builder)
2. Analyzes co-mention frequencies
3. Removes pairs with <5 mentions
4. Saves as `knowledge_graph_filtered.json`

### Advanced Usage

#### Adjust Threshold

```bash
# Conservative (keep more): threshold=3
python filter_kg_noise.py --threshold 3
# Result: ~70% reduction (keeps 3+ mentions)

# Aggressive (keep less): threshold=10
python filter_kg_noise.py --threshold 10
# Result: ~95% reduction (keeps 10+ mentions)
```

#### Preview Changes (Dry-Run)

```bash
# See what would be filtered without saving
python filter_kg_noise.py --dry-run --verbose
```

**Output shows:**
- Original/filtered relationship counts
- Number of pairs removed
- Percentage reduction
- Frequency distribution

#### Verbose Output

```bash
# Detailed logging
python filter_kg_noise.py --verbose
```

Shows:
- Co-mention frequency distribution
- Detailed relationship analysis
- Debug information

### Custom Input/Output

```bash
# Use different KG file
python filter_kg_noise.py --input my_custom_kg.json --output my_filtered.json
```

---

## Understanding the Filter

### Relationship Types

**Semantic Relationships (ALWAYS KEPT):**
- `provides`: Organization provides Service
- `uses`: Service uses Technology/Resource
- `manages`: Role manages Service
- **These are preserved regardless of threshold**

**Co-mention Relationships (THRESHOLD APPLIED):**
- `mentioned_together_in`: Entity A and Entity B appear in same document
- **Only kept if pair appears 5+ times (or custom threshold)**

### Frequency Analysis Example

```
Analysis of co-mention pairs:

Pairs mentioned 1x:  8,500 pairs  (remove - likely coincidental)
Pairs mentioned 2x:  4,200 pairs  (remove - weak signal)
Pairs mentioned 3x:  2,100 pairs  (borderline)
Pairs mentioned 4x:    900 pairs  (borderline)
Pairs mentioned 5x+:    900 pairs  (keep - strong signal)
```

With **5+ threshold:** Keep 900 pairs, remove 15,700 pairs (85% reduction)

---

## Workflow: Before and After

### Before Filtering

```
Query: "What services does Leeds Community Healthcare offer?"

Entity Expansion:
  LCH → [100+ entities through co-mentions]
    ├── Community Nursing (genuine)
    ├── Mental Health (genuine)
    ├── Cancer Services (genuine)
    ├── Random NHS White Paper Title (coincidental mention)
    ├── Procurement Standards Document (co-authored reference)
    ├── Building Safety Regulations (tangential)
    └── ... 90+ more weak connections

Result: Noisy expansion, poor search results
```

### After Filtering

```
Query: "What services does Leeds Community Healthcare offer?"

Entity Expansion:
  LCH → [~15 entities through co-mentions]
    ├── Community Nursing (genuine - mentioned 8x)
    ├── Mental Health (genuine - mentioned 12x)
    ├── Elderly Care (genuine - mentioned 6x)
    ├── Children Services (genuine - mentioned 7x)
    └── ... only strong signals

Result: Clean expansion, relevant search results
```

---

## Implementation Steps

### Step 1: Build Fresh Knowledge Graph (If Needed)

```bash
# Only if KG doesn't exist or is outdated
python analysis/knowledge_graph/build_knowledge_graph_framework.py
# Wait 15-20 minutes...
```

Produces: `knowledge_graph_improved.json`

### Step 2: Filter Noise

```bash
# Run filter with default threshold (5)
python analysis/knowledge_graph/filter_kg_noise.py

# Or with custom threshold
python analysis/knowledge_graph/filter_kg_noise.py --threshold 7
```

Produces: `knowledge_graph_filtered.json`

### Step 3: Test Filtered Graph

```bash
# Update KG agent to use filtered graph
# Edit: analysis/multi_agent/knowledge_graph_agent.py
# Change: kg_path = 'knowledge_graph_improved.json'
# To:     kg_path = 'knowledge_graph_filtered.json'
```

### Step 4: Test Query Expansion

```bash
# Run interactive queries
python query/interactive_query_multi_source.py

# Test with entity-heavy questions:
# "What organizations work with LTHT?"
# "What are partnership pathways for mental health?"
# "Which services integrate primary and community?"
```

### Step 5: Compare Results

Compare outputs:
- Original KG (noisy)
- Filtered KG (5+ threshold)
- Possibly try 7+ or 3+ threshold

Pick best performing configuration.

---

## Tuning the Threshold

### Finding the Sweet Spot

| Threshold | Expected Outcome | Good For |
|-----------|-------------------|----------|
| 3 (weak) | 70% reduction | Aggressive filtering, but some noise remains |
| 5 (standard) | 85% reduction | **Recommended - good balance** |
| 7 (strong) | 90% reduction | Very clean, might remove some valid signals |
| 10 (strict) | 95% reduction | Extremely conservative, may over-filter |

### How to Evaluate

1. **Noise Assessment**
   - Do entity expansions seem relevant?
   - Are results drifting from query intent?
   - Any spurious relationships?

2. **Coverage Assessment**
   - Is expansion finding key entities?
   - Missing important connections?
   - Relationships seem incomplete?

3. **Performance**
   - Faster query expansion (fewer relationships)?
   - Better relevance ranking?
   - More focused search results?

### Iterative Tuning

```bash
# Try different thresholds
python filter_kg_noise.py --threshold 3 --output kg_t3.json
python filter_kg_noise.py --threshold 5 --output kg_t5.json
python filter_kg_noise.py --threshold 7 --output kg_t7.json

# Update KG agent to test each
# Compare results subjectively and objectively
```

---

## Technical Details

### Filter Algorithm

```
For each relationship in KG:
  If relationship type is NOT "mentioned_together_in":
    Keep it (semantic relationships always preserved)
  Else (co-mention relationship):
    Get entity pair (source, target)
    Count how many times this pair appears
    If count >= threshold:
      Keep relationship
    Else:
      Remove relationship

Output: Filtered relationships + original entities
```

### Computational Cost

- **Time:** <30 seconds (post-processing only)
- **Memory:** Minimal (in-memory processing)
- **API Calls:** 0 (no LLM calls needed)

---

## Next Steps

### Option 1: Immediate Use
1. Run filter with threshold 5
2. Update KG agent to use filtered version
3. Test query expansion
4. Monitor for any issues

### Option 2: Iterative Optimization
1. Run filter with multiple thresholds (3, 5, 7)
2. Test each version thoroughly
3. Choose best performing threshold
4. Document rationale

### Option 3: Phase 2 Improvements (Later)
1. Implement better extraction logic
2. Add new relationship types (collaborates_with, enables, etc.)
3. Enhance semantic relationship discovery
4. Rebuild KG with improvements

---

## FAQ

**Q: Will filtered KG hurt search results?**
A: No. Removing weak co-mention noise improves focus. Semantic relationships are preserved.

**Q: Can I revert to original KG?**
A: Yes. Keep `knowledge_graph_improved.json` as backup. Switch between them anytime.

**Q: How do I know the right threshold?**
A: Test empirically. Start with 5, adjust based on query expansion quality.

**Q: Does filtering change entity extraction?**
A: No. All 200 entities remain. Only weak relationships are removed.

**Q: Can I use filtered KG in production?**
A: Yes. Once tested and validated, it's ready for deployment.

---

## Reference

- **Filter script:** `analysis/knowledge_graph/filter_kg_noise.py`
- **KG builder:** `analysis/knowledge_graph/build_knowledge_graph_framework.py`
- **KG agent:** `analysis/multi_agent/knowledge_graph_agent.py`
- **Maintenance guide:** `analysis/knowledge_graph/README_KG_REFRESH.md`

---

**Last Updated:** October 31, 2025
**Status:** Ready to Implement
**Next Phase:** Phase 2 - Better Extraction Logic
