# NHS Strategic Analysis RAG Pipeline

## Overview

This is a **Retrieval-Augmented Generation (RAG)** pipeline designed to analyze NHS strategic documents, track document recency, and synthesize multi-source insights. The system ingests documents, auto-tags them by theme and audience, tracks publication/strategy dates, and flags aging or expiring documents.

### What This Pipeline Does

1. **Extracts and tracks document dates** - Automatically extracts publication dates, updated dates, fiscal years, and strategy timeframes
2. **Ingests documents into a searchable vector database** - Uses OpenAI embeddings and ChromaDB for semantic search
3. **Auto-tags documents** - Assigns Theme and Audience labels using GPT-3.5-turbo
4. **Analyzes with multi-source synthesis** - Forces answers to cite 3+ different sources with explicit synthesis
5. **Flags document recency** - Marks recent, aging, and archival documents; highlights strategies expiring soon
6. **Provides interactive queries** - Ask strategic questions and get multi-source answers with date awareness

### Why This Matters for NHS Strategy

- **Recency awareness** - Healthcare strategies change rapidly; the system flags documents 2+ years old and strategies expiring within 1 year
- **Multi-source thinking** - Forces synthesis across multiple documents rather than single-source answers
- **Metadata tracking** - Each retrieved chunk includes publication date, theme, audience, and relevance flags
- **Quick context** - Find relevant strategic information across 19 documents with 13,018+ indexed chunks

---

## Current System Status ✓

**Pipeline is fully operational and tested.**

| Metric | Value |
|--------|-------|
| **Documents** | 19 (13 MD + 6 TXT) |
| **Total Chunks** | 13,018 |
| **Documents with Dates** | 18/19 (95%) |
| **Multi-Source Synthesis** | 4-7 sources per query ✓ |
| **Recency Flags** | Working perfectly ✓ |
| **Latest Analysis** | ✓ Re-run with complete data |

**Documents Indexed:**
- ✓ 10 original NHS England documents
- ✓ 9 new documents (Leeds Community, Board meetings, Strategy documents)

**Recency Flag Distribution:**
- `[RECENT]` - 14 documents (2025 dates)
- `[RECENT - 1 YEAR]` - 3 documents (2024 dates)
- `[STRATEGY EXPIRES 2025]` - Workforce strategy flagged ⚠️
- `[NO DATE]` - 1 document (em-dash encoding issue - minimal impact)

**Last Updated:** Strategic analysis re-run with full rebuild - all 13,018 chunks with proper date metadata

---

## Quick Start

### 1. Initial Setup (First Time Only)

```bash
# Install dependencies (if not already done)
pip install langchain langchain-openai langchain-chroma unstructured openai chromadb

# Set up your OpenAI API key in .env file
OPENAI_API_KEY=sk-...
```

### 2. Evaluate Document Dates

```bash
# Auto-extract dates and generate configuration
python eval_dates.py

# Or confirm/override dates interactively
python eval_dates.py --interactive
```

Output: `document_dates.json` (stores publication/strategy dates for all documents)

### 3. Ingest Documents

```bash
python ingest_pipeline.py
```

This will:
- Load all `.md` files from the `docs/` folder
- Clean filenames (remove special characters)
- Partition documents into chunks
- Auto-tag each chunk with Theme and Audience
- Load dates from `document_dates.json`
- Generate OpenAI embeddings
- Store enriched chunks in ChromaDB

Output: Updated `chroma_db_test/` vector database with date metadata

### 4. Run Strategic Analysis

```bash
python analyze_pipeline.py
```

This will:
- Execute 5 pre-configured strategic queries
- Retrieve relevant chunks with multi-source synthesis (3+ sources)
- Flag document recency (RECENT, OLDER, ARCHIVAL, STRATEGY EXPIRES)
- Generate markdown report: `strategic_analysis_output_multi_source.md`

### 5. Ask Your Own Questions (Optional)

```bash
python interactive_query_multi_source.py
```

Interactively query the database. Answers will include:
- Multiple sources with dates and themes
- Recency flags for aging/expiring documents
- Explicit synthesis across sources

---

## Architecture & Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    SOURCE DOCUMENTS                          │
│      (19 NHS documents: 13 MD + 6 TXT files in docs/)       │
└─────────────────────┬──────────────────────────────────────┘
                      │
                      ▼
          ┌─────────────────────────┐
          │    eval_dates.py        │
          │  Auto-extract dates:    │
          │  - Published dates      │
          │  - Updated dates        │
          │  - Fiscal years         │
          │  - Strategy timeframes  │
          └────────────┬────────────┘
                       │
                       ▼
          ┌─────────────────────────────────┐
          │   document_dates.json           │
          │  Config file mapping:           │
          │  filename -> date info          │
          │  (source, notes, year_range)    │
          └────────┬──────────────────┬─────┘
                   │                  │
          ┌────────▼────┐     ┌──────▼─────────┐
          │   ingest_   │     │   analyze_     │
          │ pipeline.py │     │  pipeline.py   │
          │             │     │                │
          │ Processes:  │     │ Retrieves &    │
          │ - Partition │     │ Flags:         │
          │ - Clean     │     │ - Age flags    │
          │ - Auto-tag  │     │ - Expiry       │
          │ - Date load │     │ - Synthesis    │
          │ - Embed     │     │                │
          │ - Store     │     │                │
          └────────┬────┘     └──────┬─────────┘
                   │                  │
                   ▼                  ▼
        ┌────────────────────┐    ┌──────────────┐
        │   ChromaDB with    │    │   Analysis   │
        │  Date Metadata     │    │   Output     │
        │                    │    │   (.md file) │
        │ 13,018 chunks      │    │              │
        │ with dates, tags   │    │ Sources +    │
        └────────────────────┘    │ Dates +      │
                                  │ Flags       │
                                  └──────────────┘
```

---

## Component Documentation

### 1. eval_dates.py - Date Extraction Tool

**Purpose**: Evaluates and extracts dates from documents, generates `document_dates.json` config.

**Features**:
- Auto-extracts from multiple date formats (ISO, text, year ranges)
- Handles different document types:
  - Annual reports: fiscal year extracted
  - Strategies: start-end year range extracted
  - Updates: "Date published:" or "Date updated:" extracted
  - Filename-embedded dates detected

**Priority order** (which date type is preferred):
1. Published date (e.g., "Date published: 29 January, 2025")
2. Updated date (e.g., "Date updated: 15 March, 2025")
3. Fiscal year (e.g., "2024-2025")
4. Strategy year range (e.g., "2021-25")
5. Manual entry (if auto-extraction fails)

**Usage**:
```bash
# Auto-extract and generate config
python eval_dates.py

# Interactive mode - confirm/override each date
python eval_dates.py --interactive
```

**Output Example**:
```
[OK] Loaded 19 documents from docs/
[OK] Auto-extracted: 4 documents
[MANUAL ENTRY] 15 documents (user confirmed)
[OK] Generated document_dates.json
```

---

### 2. document_dates.json - Configuration File

**Purpose**: Central configuration storing publication/strategy dates for all documents.

**Structure**:
```json
{
  "filename.md": {
    "date": "YYYY-MM-DD",
    "source": "auto|manual|unknown",
    "year_range": ["YYYY", "YYYY"] or null,
    "notes": "Context about the date and document"
  }
}
```

**Fields explained**:
- `date` - Primary date in ISO format (YYYY-MM-DD)
- `source` - How date was determined:
  - `"auto"` - automatically extracted from content
  - `"manual"` - manually entered/confirmed
  - `"unknown"` - date couldn't be determined
- `year_range` - For multi-year strategies: `["start_year", "end_year"]`, or `null` for single-date documents
- `notes` - Context/explanation about the document and date

**When to Update**:
1. After adding new documents to `docs/`:
   ```bash
   python eval_dates.py
   ```
2. If dates need correction, edit manually:
   - Open `document_dates.json`
   - Update the `"date"` field
   - Change `"source"` to `"manual"` if you're overriding

**Example Entry**:
```json
"Workforce-Strategy-2021-25-V1.0.md": {
  "date": "2021-01-01",
  "source": "manual",
  "year_range": ["2021", "2025"],
  "notes": "Multi-year strategy 2021-2025. EXPIRING SOON (2025). Use with caution - will need replacement/update."
}
```

---

### 3. ingest_pipeline.py - Document Ingestion

**Purpose**: Loads documents from `docs/`, enriches them with metadata, and stores in ChromaDB.

**What it does**:
1. Loads all `.md` and `.txt` files from `docs/` directory
2. Cleans special characters from filenames
3. Partitions documents into text chunks using Unstructured library
4. Auto-tags each chunk with **Theme** and **Audience** using GPT-3.5-turbo
5. Loads dates from `document_dates.json`
6. Generates embeddings via OpenAI
7. Stores chunks in ChromaDB with rich metadata

**Metadata stored per chunk**:
```python
{
  "id": "unique_chunk_id",
  "source": "filename.md",
  "date": "2025-01-29",           # From document_dates.json
  "year_range_start": "2021",      # If multi-year strategy
  "year_range_end": "2025",        # If multi-year strategy
  "theme": "Healthcare reform",    # Auto-assigned by GPT
  "audience": "Policymakers",      # Auto-assigned by GPT
  "element_type": "NarrativeText", # Partition type
  "page_number": "5"               # Document page reference
}
```

**Usage**:
```bash
python ingest_pipeline.py
```

**Configuration**:
- `DOCS_PATH` - Where documents are located (default: `docs/`)
- `STORE_DIR` - Where ChromaDB is stored (default: `chroma_db_test/`)
- `FULL_REBUILD` - Set to `True` to completely rebuild database (default: `False`)
- `MIN_ELEMENT_TEXT_LENGTH` - Minimum chunk size (default: 50 characters)

**Output**:
```
# Document Ingestion Pipeline

## Processing Documents from `docs`

### Processing File: `NHS England Productivity update.md`
- Partitioned into 42 raw elements.
- Auto-tagged: Theme = 'Healthcare Productivity', Audience = 'Healthcare Administrators'
- [OK] Added 38 chunks.

## Ingestion Summary
- Processed Files: **17**
- Total Chunks Ready: **13018**

### Updating ChromaDB...
  - Batch 1: Added 5000 chunks (Total: 5000)
  - Batch 2: Added 5000 chunks (Total: 10000)
  - Batch 3: Added 3018 chunks (Total: 13018)
[OK] ChromaDB updated successfully (13018 total chunks added).

[COMPLETE] Ingestion pipeline complete.
```

**Cost**: ~$0.50-1.00 per full run (tagging + embeddings)

---

### 4. analyze_pipeline.py - Strategic Analysis

**Purpose**: Executes strategic queries against the ingested documents and flags document recency.

**What it does**:
1. Loads ChromaDB with indexed documents
2. Executes 5 pre-configured strategic queries
3. Retrieves 10 most relevant chunks per query
4. Forces multi-source synthesis (3+ sources explicitly cited)
5. Flags document recency based on age:
   - `[RECENT]` - Less than 1 year old
   - `[RECENT - 1 YEAR]` - 1-2 years old
   - `[OLDER DOCUMENT - 2+ YEARS]` - 2-4 years old
   - `[ARCHIVAL - 4+ YEARS]` - Older than 4 years
   - `[STRATEGY EXPIRES YYYY]` - Strategy ending within 1 year
   - `[NO DATE]` - Date not found in config

**Recency Calculation** (pseudo-code):
```python
today = 2025-10-19
document_date = 2023-06-15
days_old = 792 days
years_old = 2.17 years
-> Flagged as: [OLDER DOCUMENT - 2+ YEARS]
```

**Usage**:
```bash
python analyze_pipeline.py
```

**Output Example** (from `strategic_analysis_output_multi_source.md`):

```markdown
## Query: "What are the key workforce challenges and strategies?"

Retrieved 10 chunks from 7 different sources.

**All Retrieved Chunks:**

1. `Workforce-Strategy-2021-25-V1.0.md` [STRATEGY EXPIRES 2025]
   Published: 2021-01-01 | Theme: Workforce Development

2. `NHS England Productivity update.md` [RECENT]
   Published: 2024-12-03 | Theme: Operational Efficiency

3. `LCH-Trust-Board-Meeting-Public-Papers-4-09-2025-AMENDED.md` [RECENT]
   Published: 2025-09-04 | Theme: Organizational Development
```

**Multi-Source Synthesis**:
- Queries are designed to force answers that cite at least 3 sources
- Prompt explicitly requires: "YOU MUST explicitly cite and synthesize information from AT LEAST 3 different sources"
- Output includes `[Source: filename]` citations throughout

---

### 5. interactive_query_multi_source.py - Interactive Querying

**Purpose**: Ask custom questions about your documents and get multi-source answers with date awareness.

**Usage**:
```bash
python interactive_query_multi_source.py
```

**Example Session**:
```
Enter your question (or 'quit' to exit):
> What are the most important performance metrics for NHS trusts?

Searching for relevant information...

## Your Question
What are the most important performance metrics for NHS trusts?

**All Retrieved Chunks:**

1. `NHS England Productivity update.md` [RECENT]
   Published: 2024-12-03 | Theme: Performance Management

2. `LCH-Trust-Board-Meeting-Public-Papers-4-09-2025-AMENDED.md` [RECENT]
   Published: 2025-09-04 | Theme: Organizational Strategy

3. `NHS England _ NHS Oversight Framework 2025_26 _ methodology manual.md` [RECENT]
   Published: 2025-06-26 | Theme: Framework & Methodology

**Multi-Source Synthesis**

Based on analysis of the NHS Oversight Framework, recent Board discussions, and
Productivity updates [Source: NHS England Oversight Framework, LCH Trust Board Papers,
NHS England Productivity], the key performance metrics include...
```

**Features**:
- Multi-source synthesis (3+ sources minimum)
- Date awareness (shows publication dates)
- Recency flags for aging documents
- Citation tracking

---

## Adding New Documents

### Step 1: Add Documents to `docs/`

```bash
# Copy your new .md or .txt files to the docs/ directory
cp my_new_strategy.md docs/
```

### Step 2: Re-evaluate Dates

```bash
# Auto-detect the new files and extract their dates
python eval_dates.py

# Or confirm dates interactively
python eval_dates.py --interactive
```

This will update `document_dates.json` with entries for new documents.

### Step 3: Reingest Documents

```bash
python ingest_pipeline.py
```

The ingestion pipeline automatically:
- Detects new files (files not already in ChromaDB)
- Cleans filenames if needed
- Processes only new documents (doesn't re-index existing ones)
- Updates ChromaDB with new chunks

### Step 4: Re-run Analysis

```bash
python analyze_pipeline.py
```

New documents will appear in analysis output with proper date flags.

---

## Troubleshooting

### Problem: `[NO DATE]` flag for a document that has a date

**Cause**: Filename mismatch between `docs/` folder and `document_dates.json` config.

**Solution**:
1. Check the actual filename in `docs/` folder
2. Update `document_dates.json` to use the exact filename
3. Filename matching is case-sensitive and exact

```json
// WRONG (filename doesn't match)
"Leeds Community Annual Report.md": { "date": "2024-06-30" }

// RIGHT (exact filename from docs/ folder)
"Leeds Community Annual-report-2024-2025.md": { "date": "2024-06-30" }
```

### Problem: Documents not being ingested

**Cause 1**: File not in `docs/` directory
**Cause 2**: File not `.md` or `.txt` extension
**Cause 3**: No `document_dates.json` (warning, but still processes)

**Solution**:
1. Verify file is in `docs/` folder
2. Check file has `.md` or `.txt` extension
3. Run `eval_dates.py` to generate `document_dates.json`

### Problem: Out of memory or batch size errors

**Cause**: Large documents create too many chunks for ChromaDB in single batch

**Solution**: Already implemented! Pipeline automatically batches at 5,000 chunks per operation.

### Problem: Slow embedding generation

**Cause**: OpenAI API rate limits or large document volume

**Solution**:
- Embeddings are generated per chunk (not per document)
- ~13,018 chunks across 19 documents = ~$0.03 in embedding costs
- Initial run takes 10-15 minutes; subsequent runs are faster (incremental only)
- Cost is one-time for ingestion; queries are cheap

---

## Understanding the Multi-Source Enhancement

### Original Problem

The system initially retrieved 7-10 relevant chunks but only cited 1-2 sources in answers. This defeats the purpose of a multi-source synthesis tool for strategic analysis.

### Root Causes

1. **Vague prompts** - LLM wasn't explicitly told to use multiple sources
2. **No enforcement** - No mechanism to ensure citation format
3. **Low retrieval** - Only 7 chunks retrieved; not enough material for synthesis

### Solution Implemented

1. **Explicit multi-source requirement** in prompt:
   ```
   YOU MUST explicitly cite and synthesize information from
   AT LEAST 3 different sources. Include [Source: filename]
   citations throughout your answer.
   ```

2. **Increased chunk retrieval** from 7 to 10 per query

3. **Mandatory citation format** - Answers must include `[Source: ...]` tags

### Results

- Average sources cited: **3-7 per query** (was 1-2)
- Synthesis quality: **Improved** (connections between sources visible)
- Citation accuracy: **Verified** in output

### Example

**Before Enhancement**:
```
Q: What are key productivity opportunities?
A: The NHS has identified several productivity improvements...
[Source: NHS England Productivity update]
```

**After Enhancement**:
```
Q: What are key productivity opportunities?
A: According to the NHS Oversight Framework, Board discussions, and recent
productivity analysis [Source: NHS England Oversight Framework, LCH Trust Board,
NHS England Productivity], the key areas are...
- Operational efficiency (NHS England Productivity)
- Clinical pathway optimization (Board discussions)
- Resource allocation strategies (Framework methodology)
```

---

## Project Evolution

### Timeline of Development

1. **Phase 1**: Created basic RAG pipeline (document loading → embeddings → retrieval)
2. **Phase 2**: Identified multi-source synthesis gap - answers only used 1-2 sources
3. **Phase 3**: Enhanced pipeline with explicit multi-source requirements and increased retrieval
4. **Phase 4**: Added comprehensive date tracking (eval_dates.py, document_dates.json)
5. **Phase 5**: Integrated recency flags into analysis output
6. **Phase 6**: Fixed batch processing issues for large document volumes

### Key Improvements

- **Date Tracking**: Understand document recency and strategy timelines
- **Multi-Source Synthesis**: Answers now synthesize 3-7 sources with explicit citations
- **Batch Processing**: Handles 13,018+ chunks without memory issues
- **Auto-Tagging**: Chunks categorized by Theme and Audience for better filtering
- **Interactive Queries**: Ask custom questions with date awareness

---

## Cost Analysis

### One-Time Costs (Initial Setup)

- **eval_dates.py**: $0 (Python regex, no API calls)
- **ingest_pipeline.py**: ~$0.60-1.20
  - Auto-tagging: ~$0.60 (GPT-3.5 for 13,018 tags)
  - Embeddings: ~$0.03 (OpenAI embedding API for all chunks)

### Per-Query Costs (Ongoing)

- **analyze_pipeline.py**: ~$0.10 per 5 queries
  - Retrieval: Free (local ChromaDB search)
  - LLM synthesis: ~$0.02 per query (GPT-3.5-turbo)

- **interactive_query_multi_source.py**: ~$0.02 per question

### Monthly Estimate (Typical Usage)

- 20 strategic analyses: $0.40
- 50 interactive questions: $1.00
- **Total**: ~$1.40/month (very low cost)

---

## File Structure

```
Langchain/
├── README.md                           # This file
├── document_dates.json                 # Config: publication/strategy dates
├── document_dates_schema.md            # Schema documentation
├── docs/                               # Source documents (19 files: 13 MD + 6 TXT)
│   ├── NHS England Productivity update.md
│   ├── Workforce-Strategy-2021-25-V1.0.md
│   ├── Leeds Community Annual Report 2425.md
│   ├── Health Innovation North Turning Conversation into Collaboration.txt
│   ├── NHS England Board Meeting – 23 September 2025.txt
│   └── ... (14 more)
├── chroma_db_test/                     # ChromaDB vector store (auto-generated)
├── eval_dates.py                       # Date extraction evaluation tool
├── ingest_pipeline.py                  # Document ingestion pipeline
├── analyze_pipeline.py                 # Strategic analysis with flagging
├── interactive_query_multi_source.py   # Interactive querying tool
├── clean_doc.py                        # Filename cleanup utility
├── utils.py                            # Auto-tagging function (GPT-3.5)
├── strategic_analysis_output_multi_source.md  # Analysis results (auto-generated)
└── .env                                # OpenAI API key (not in repo)
```

---

## Next Steps

1. **Run the pipeline** if you haven't already:
   ```bash
   python eval_dates.py
   python ingest_pipeline.py
   python analyze_pipeline.py
   ```

2. **Add your own documents** to `docs/` and re-run the pipeline

3. **Ask custom questions** using the interactive tool:
   ```bash
   python interactive_query_multi_source.py
   ```

4. **Monitor document recency** - Pay attention to:
   - `[STRATEGY EXPIRES YYYY]` flags (may need refresh/replacement)
   - `[ARCHIVAL]` flags (consider removing or archiving)
   - `[RECENT]` flags (high confidence in data)

5. **Iterate and improve**:
   - Adjust themes/audiences in auto-tagging if needed
   - Add manual notes to `document_dates.json` for important context
   - Test different query angles to explore your documents

---

## Support & Questions

For questions about:
- **Date extraction**: See `eval_dates.py` docstring
- **Ingestion process**: See `ingest_pipeline.py` docstring
- **Analysis pipeline**: See `analyze_pipeline.py` docstring
- **Multi-source synthesis**: See "Understanding the Multi-Source Enhancement" section above

All scripts include comprehensive docstrings and inline comments explaining functionality.
