# Multi-Source Synthesis Fix Guide

## Problem Summary

Your RAG system was retrieving **7-10 chunks per query** from the vector database, but the LLM answers were **only actively using 1-2 sources** in the final response, despite having access to all of them.

### Example from Your Current Output:

**Query 4: "What are the primary workforce development strategies across documents?"**

Retrieved sources:
1. `Workforce-Strategy-2021-25-V1.0.md` (6 chunks)
2. `Leeds Coommunity Annual Report 2425.md` (1 chunk)

Answer output: Dominated by `Workforce-Strategy-2021-25-V1.0.md`, minimal use of the Annual Report

---

## Root Causes

### 1. **Chain Type: "stuff"**
- Concatenates all retrieved chunks into a single context block
- The LLM *can* see all sources, but has no structural incentive to use them all
- "stuff" works well for factual Q&A but poorly for synthesis tasks

### 2. **Prompt Design Weakness**
Your original prompt:
```
"Use the following pieces of context to answer the question at the end."
```

Problems:
- Doesn't explicitly ask for multi-source synthesis
- Doesn't ask for citations
- Doesn't ask the LLM to identify patterns across sources
- Lazy prompts = lazy synthesis

### 3. **Retrieval Count Was Suboptimal**
- You retrieved `k=7` chunks per query
- Some large documents (LCH Trust, Leeds Annual Report) have 2000+ chunks
- 7 may not be enough to ensure diverse sources are represented

---

## Solutions Implemented

### Solution 1: Multi-Source Aware Prompt ✅

**Original Prompt:**
```
Use the following pieces of context to answer the question at the end.
Focus on extracting and synthesizing strategic insights...
```

**New Prompt (test_one_doc_multi_source.py):**
```
You MUST explicitly cite and synthesize information from AT LEAST 3 different sources.
When mentioning a fact or insight, reference which document(s) it comes from using [Source: filename].
Look for patterns, contradictions, and complementary perspectives across the sources.
Clearly separate different viewpoints or priorities from different documents.
If sources agree on a point, highlight this consensus. If they differ, explain the difference.
```

**Why it works:**
- Forces the LLM to think about multi-source synthesis explicitly
- Provides citation format ([Source: ...]) to make tracking easier
- Asks for synthesis patterns (agreement, disagreement, complementary views)

### Solution 2: Higher Retrieval Count ✅

Changed from:
```python
retriever=vectordb.as_retriever(search_kwargs={"k": 7})
```

To:
```python
retriever=vectordb.as_retriever(search_kwargs={"k": 10})
```

**Why it helps:**
- More chunks = higher probability of multiple sources
- Reduces chance of one large document dominating results
- Gives the prompt more material to synthesize

### Solution 3: Source Analysis & Tracking ✅

Added new utilities in `interactive_query_multi_source.py`:

```python
def analyze_source_coverage(source_documents):
    """Analyze how many unique sources were retrieved."""
    source_counts = defaultdict(int)
    for doc in source_documents:
        source = doc.metadata.get("source", "Unknown")
        source_counts[source] += 1
    return source_counts
```

This provides:
- Count of unique sources per query
- Distribution of chunks across sources
- Visual feedback on source diversity
- Debugging info for prompt tuning

---

## Implementation Details

### New Files Created:

1. **test_one_doc_multi_source.py** (180 lines)
   - Enhanced version of your main pipeline
   - Uses multi-source aware prompt
   - Includes source diversity metrics in output
   - Generates `strategic_analysis_output_multi_source.md` report

2. **interactive_query_multi_source.py** (140 lines)
   - Enhanced interactive query interface
   - Enforces multi-source synthesis
   - Shows source coverage statistics
   - Pretty-prints source details

3. **MULTI_SOURCE_FIX_GUIDE.md** (this file)
   - Comprehensive explanation of the problem and solutions

### Key Prompt Changes:

#### Before (Original):
```python
default_strategic_qa_prompt = PromptTemplate.from_template(
    "You are an AI assistant specialized in strategic analysis of health documents.\n"
    "Use the following pieces of context to answer the question at the end. "
    "Focus on extracting and synthesizing strategic insights, overarching priorities, key challenges, and emerging trends.\n"
    "If the answer cannot be found in the provided context, state that you don't know.\n\n"
    "Context:\n{context}\n\nQuestion: {question}\nStrategic Analysis Answer:"
)
```

#### After (Multi-Source):
```python
MULTI_SOURCE_STRATEGIC_PROMPT = """You are an AI assistant specialized in strategic analysis of health documents.

Your task is to synthesize information from MULTIPLE sources to provide comprehensive insights.

IMPORTANT INSTRUCTIONS:
1. You have received context from multiple documents and document sections.
2. For your answer, YOU MUST explicitly cite and synthesize information from AT LEAST 3 different sources.
3. When mentioning a fact or insight, reference which document(s) it comes from using the format [Source: filename].
4. Look for patterns, contradictions, and complementary perspectives across the sources.
5. Clearly separate different viewpoints or priorities from different documents.
6. If sources agree on a point, highlight this consensus. If they differ, explain the difference.
...
"""
```

---

## How to Use the Enhanced Version

### Option 1: Run Enhanced Batch Pipeline
```bash
python test_one_doc_multi_source.py
```

This will:
- Ingest all documents (same as before)
- Run sample queries with multi-source prompt
- Generate `strategic_analysis_output_multi_source.md` with source metrics
- Show how many unique sources were used per query

### Option 2: Interactive Multi-Source Queries
```bash
python interactive_query_multi_source.py
```

Then ask questions like:
```
Your Question: What are the strategic priorities?
```

You'll see:
- Answer with explicit source citations
- Source coverage analysis (e.g., "Unique sources: 4")
- Breakdown of chunks per source
- Snippet previews for each source

### Option 3: Compare Both Approaches
Run both your original and enhanced versions and compare outputs:

```bash
python test_one_doc.py > output_original.txt
python test_one_doc_multi_source.py > output_enhanced.txt
```

Then examine how the enhanced version includes more explicit multi-source synthesis.

---

## Expected Improvements

### Before (Original):
```
**Answer:** [Long paragraph mostly from 1-2 sources]

**Key Supporting Documents:**
- 1. Workforce-Strategy-2021-25-V1.0.md
- 2. Workforce-Strategy-2021-25-V1.0.md
- 3. Workforce-Strategy-2021-25-V1.0.md
- 4. Workforce-Strategy-2021-25-V1.0.md
- 5. Workforce-Strategy-2021-25-V1.0.md
- 6. Workforce-Strategy-2021-25-V1.0.md
- 7. Leeds Coommunity Annual Report 2425.md
```

(Notice: 6/7 from same source, minimal actual synthesis)

### After (Multi-Source Enhanced):
```
**Answer:**
The workforce development strategies combine perspectives from multiple sources:

[From Workforce-Strategy-2021-25-V1.0.md] The primary themes include Organization Design,
Resourcing, Inclusion, Wellbeing, Leadership, and System Partner approaches...

[Complementary perspective from Leeds Coommunity Annual Report 2425.md] The organizational
implementation emphasizes stakeholder engagement and transparency in how these strategies
are being executed...

[Additional insights from LCH-Trust-Board-Meeting-Public-Papers] The board-level discussion
reveals how these strategies address specific governance concerns...

[Source Coverage Analysis]
Unique sources: 4
- Workforce-Strategy-2021-25-V1.0.md: 3 chunks
- Leeds Coommunity Annual Report 2425.md: 3 chunks
- LCH-Trust-Board-Meeting-Public-Papers-4-09-2025-AMENDED_1_.md: 2 chunks
- NHS england Productivity.md: 2 chunks
```

---

## Fine-Tuning Options

### To Require Even More Sources:
Edit the prompt to require minimum 5 sources instead of 3:
```python
"For your answer, YOU MUST explicitly cite and synthesize information from AT LEAST 5 different sources."
```

### To Retrieve Even More Chunks:
```python
retriever=vectordb.as_retriever(search_kwargs={"k": 15})  # Instead of 10
```

### To Emphasize Contradictions:
Add to prompt:
```
"IMPORTANT: Identify and explain any contradictions or conflicting priorities between sources."
```

### To Require Different Themes:
Modify prompt to enforce theme diversity:
```
"Ensure that your sources represent AT LEAST 3 different themes (e.g., Healthcare Productivity,
Workforce Development, Healthcare Transformation, etc.)"
```

---

## Testing & Validation

To verify the enhancement is working:

1. **Run Enhanced Version:**
   ```bash
   python test_one_doc_multi_source.py
   ```

2. **Check Output:**
   - Look at `strategic_analysis_output_multi_source.md`
   - Find examples with explicit [Source: ...] citations
   - Verify each answer uses 3+ different documents
   - Check source coverage statistics

3. **Compare Metrics:**
   - Count unique sources per query (should be 3+)
   - Look for explicit cross-references between documents
   - Check if synthesis identifies patterns vs. listing facts

4. **Interactive Testing:**
   ```bash
   python interactive_query_multi_source.py

   Your Question: What are the key differences between the workforce strategy and the annual report?
   ```
   - Should synthesize across both documents
   - Should identify where they agree/differ
   - Should cite both sources explicitly

---

## Advanced: Using Map-Reduce Chain (Optional)

If you want even more sophisticated multi-source synthesis, consider upgrading to `map_reduce` chain type:

```python
qa = RetrievalQA.from_chain_type(
    llm=qa_llm,
    chain_type="map_reduce",  # Process each doc separately, then merge
    retriever=vectordb.as_retriever(search_kwargs={"k": 10}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": multi_source_prompt}
)
```

**map_reduce benefits:**
- Processes each source independently first
- Then synthesizes the results
- Better for complex multi-document analysis
- Higher token cost

---

## Summary

Your original system was good at retrieving multiple sources but weak at synthesis. The enhanced version:

✅ **Explicitly requires multi-source citations**
✅ **Retrieves more chunks per query (10 vs 7)**
✅ **Provides source coverage metrics**
✅ **Includes source analysis utilities**
✅ **Uses syntax that enforces synthesis pattern [Source: ...]**

Try running `test_one_doc_multi_source.py` and compare the output to your current version. You should see:
- More diverse sources cited per answer
- Explicit identification of patterns across documents
- Better synthesis of contradictory or complementary perspectives
- Clear source attribution throughout answers

---

## Next Steps

1. Run the enhanced versions
2. Compare outputs side-by-side
3. Fine-tune prompts based on your specific needs
4. Consider enabling source filtering by theme/audience in prompts
5. Optionally migrate to map_reduce chain for more sophisticated synthesis

Questions? Experiment with prompt variations and source count (`k` parameter) to find the sweet spot for your use case.
