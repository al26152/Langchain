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
- **Complete temporal data** - All 30 documents indexed with full publication/strategy date metadata (100% coverage)
- **Quick context** - Find relevant strategic information across 30 documents with 16,983+ indexed chunks

---

## Current System Status ✓

**Pipeline is fully operational and tested. Metadata fully synchronized.**

| Metric | Value |
|--------|-------|
| **Documents** | 30 (27 MD + 3 TXT) |
| **Total Chunks** | 16,983 |
| **Documents with Dates** | 30/30 (100%) ✓ |
| **Chunks with Dates** | 16,983/16,983 (100%) ✓ |
| **Multi-Source Synthesis** | 4-7 sources per query ✓ |
| **Recency Flags** | Working perfectly ✓ |
| **Latest Rebuild** | Full rebuild completed with corrected document_dates.json |

**Documents Indexed:**
- ✓ 30 NHS & Leeds Healthcare strategic documents
- ✓ All documents have publication/strategy dates
- ✓ All 16,983 chunks enriched with date metadata

**Recency Flag Distribution:**
- `[RECENT]` - 24+ documents (2025 dates)
- `[RECENT - 1 YEAR]` - 5+ documents (2024 dates)
- `[STRATEGY EXPIRES 2025]` - Workforce strategy flagged ⚠️
- `[NO DATE]` - 0 documents (all dates populated) ✓

**Last Updated:** Oct 25, 2025 - Full database rebuild completed after document_dates.json sync. All 16,983 chunks now have complete metadata (dates, themes, audiences).

---

## Quick Start

### 1. Initial Setup (First Time Only)

```bash
# Install dependencies (if not already done)
pip install langchain langchain-openai langchain-chroma unstructured openai chromadb

# Set up your OpenAI API key in .env file
OPENAI_API_KEY=sk-...
```

---

## Command Reference

### Choose Your Path Based on Your Needs

#### 🚀 **RECOMMENDED: Full Automated Pipeline**

Use this 95% of the time - it handles everything in one command:

```bash
python run_full_pipeline.py
```

**What it does:**
1. Cleans filenames
2. Extracts document dates
3. Ingests documents into ChromaDB

**Time:** ~10-15 minutes (on first run)
**Cost:** ~$0.60-1.00 (first run); then incremental

---

#### ✓ **Pipeline with QA Validation**

Use this if you want to verify tagging quality before ingestion:

```bash
python run_full_pipeline.py --validate
```

**What it does:**
1. Cleans filenames
2. Extracts document dates
3. **Validates auto-tagging** on document samples (shows themes/audiences)
4. Ingests documents into ChromaDB

**When to use:** After updating tagging logic or for quality assurance

---

#### 📋 **Preview Mode (Dry-Run)**

See what would run without executing:

```bash
python run_full_pipeline.py --dry-run
```

**What it shows:** The exact commands that would execute

**When to use:** Testing or understanding the flow

---

#### 🔧 **Run Individual Steps**

Execute pipeline steps one at a time (advanced):

```bash
# Step 1: Clean filenames (removes special characters)
python pipeline/clean_doc.py

# Step 2: Extract and configure document dates
python pipeline/eval_dates.py

# Step 2.5 (Optional): Validate auto-tagging before full ingest
python pipeline/eval_tagging.py

# Step 3: Ingest documents into ChromaDB
python pipeline/ingest_pipeline.py
```

**When to use:** Debugging, testing individual components, or updating code

---

#### 🔄 **Reprocess Without Cleanup**

Skip filename cleanup if files are already clean:

```bash
python run_full_pipeline.py --skip-clean
```

**Available skip flags:**
- `--skip-clean` - Skip filename cleanup
- `--skip-dates` - Skip date extraction (use existing document_dates.json)
- `--skip-ingest` - Skip ingestion (just preview)

---

### After Ingestion Complete ✅

Once `run_full_pipeline.py` finishes, your documents are indexed. Now you can:

#### **Option 1: Ask Custom Questions (Interactive)**

```bash
python query/interactive_query_multi_source.py
```

**Features:**
- Ask your own questions
- Get multi-source answers with dates
- Recency flags for aging documents
- Real-time interaction

**Example:**
```
Enter your question: What are the priority workforce challenges?
[Searching...]
Answer with 3+ sources cited...
```

---

#### **Option 2: Run Strategic Analysis (Batch)**

```bash
python analysis/analyze_pipeline.py
```

**What it does:**
- Runs 5 pre-configured strategic queries
- Generates markdown report: `strategic_analysis_output_multi_source.md`
- Forces multi-source synthesis (3+ sources)
- Flags document recency

**Cost:** ~$0.10 (GPT calls for synthesis)
**Output:** Comprehensive analysis report

---

#### **Option 3: Run Workforce Strategy Analysis**

```bash
python analysis/run_strategy_analysis.py
```

**What it does:**
- Quick theme comparison (FREE - no API calls)
- Full RAG-based gap analysis (paid - ~$15-25)

**Flags:**
- `--quick-only` - Just fast analysis (no cost)
- `--full` - Both quick + full analysis (default)

---

### Typical Workflows

#### **Workflow 1: Just Ingest Documents (Most Common)**
```bash
python run_full_pipeline.py
# Wait ~10-15 minutes
# ✓ Done! Documents are indexed and searchable
```

#### **Workflow 2: Ingest + Analyze**
```bash
python run_full_pipeline.py
python analysis/analyze_pipeline.py
# Produces: strategic_analysis_output_multi_source.md
```

#### **Workflow 3: Ingest + Interactive**
```bash
python run_full_pipeline.py
python query/interactive_query_multi_source.py
# Ask questions in real-time
```

#### **Workflow 4: Quality Check Before Ingest**
```bash
python run_full_pipeline.py --validate
# Reviews tagging quality before full ingest
```

#### **Workflow 5: Just Update Dates**
```bash
# New documents added? Update dates first
python pipeline/eval_dates.py
python pipeline/ingest_pipeline.py
```

---

## Directory Structure

After reorganization, scripts are now organized by function:

```
Langchain/
├── run_full_pipeline.py              # ← Main entry point (use this!)
├── requirements.txt
├── README.md
├── document_dates.json
│
├── pipeline/                         # Core ingestion pipeline
│   ├── clean_doc.py
│   ├── eval_dates.py
│   ├── eval_tagging.py
│   └── ingest_pipeline.py
│
├── analysis/                         # Analysis systems (organized by type)
│   ├── rag/                          # RAG (Retrieval-Augmented Generation)
│   │   ├── analyze_pipeline.py       # Pre-configured strategic queries
│   │   └── interactive_query_multi_source.py  # Interactive query interface
│   │
│   ├── knowledge_graph/              # Knowledge Graph extraction
│   │   └── build_knowledge_graph_framework.py  # Entity & relationship extraction
│   │
│   └── theme_analysis/               # Theme-Based structured analysis
│       ├── theme_comparison_analysis.py  # Old vs new strategy comparison
│       ├── workforce_strategy_gap_analysis.py  # Gap analysis with evidence
│       └── run_strategy_analysis.py   # Orchestrator for both analyses
│
├── utils/                            # Utilities
│   └── utils.py
│
├── docs/                             # Source documents (30 files)
├── chroma_db_test/                  # Vector database (auto-generated)
├── prompts/                          # Prompt templates
└── archive_py/                       # Archived/old scripts
```

---

## Your 4 Analysis Systems

Your project includes **4 complementary analysis approaches**, each suited for different use cases:

### 1. Multi-Agent Iterative RAG ✓ ✨ **[RECOMMENDED - KG Enhanced]**
**Location**: `analysis/multi_agent/`

- **Purpose**: High-confidence strategic analysis with automatic evidence validation
- **How it works**: 4 AI agents (Evidence, Critique, Synthesis, Orchestrator) work together iteratively
  - **Iteration 1**: Knowledge Graph expands queries with related entities
  - **Iteration 2+**: Gap detection refines searches automatically
  - Stops when evidence quality is EXCELLENT or max iterations reached
- **Use for**: Critical decisions, systemic analysis, risk assessment, board-level insights
- **Command**: `python analysis/multi_agent/run_multi_agent.py --question "Your question"`

**Key Features**:
- 🔍 **Knowledge Graph Integration** - Expands searches using entity relationships
- 🎯 **Iterative Refinement** - Automatically improves until sufficient quality
- 📊 **Confidence Scoring** - 0-100% confidence with quality ratings
- 🏷️ **Epistemic Tags** - Every claim marked as FACT/ASSUMPTION/INFERENCE
- 🔄 **Convergence Detection** - Stops when diminishing returns detected

**Performance**: 85-90% confidence, 8-10 documents, 30-40 evidence chunks
**Cost**: $0.15-0.40 per question | **Time**: 2-4 minutes

**Example**: "What systemic risks exist between LTHT and LCH?" →
- Finds 10 documents across organizations
- Identifies 5 risk categories with evidence
- 85% confidence, EXCELLENT quality

---

### 2. RAG (Retrieval-Augmented Generation) ✓
**Location**: `analysis/rag/`

- **Purpose**: Quick questions and exploratory analysis
- **How it works**: Single-pass retrieval from ChromaDB → LLM synthesis
- **Use for**: Ad-hoc questions, quick insights, exploratory analysis
- **Commands**:
  - `python analysis/rag/analyze_pipeline.py` - Run 5 pre-configured strategic queries
  - `python analysis/rag/interactive_query_multi_source.py` - Ask your own questions

**Performance**: 70-75% confidence, 6-7 documents, ~20 evidence chunks
**Cost**: $0.02-0.10 per question | **Time**: 30-60 seconds

**Example**: "What are the key workforce challenges?" → Gets answer synthesizing 3-7 documents

**When to use**: Fast exploratory questions, budget-conscious queries

---

### 3. Knowledge Graph ✓
**Location**: `analysis/knowledge_graph/`

- **Purpose**: Extract and visualize relationships between entities
- **How it works**: Parse documents → Extract services, organizations, care pathways → Build graph structure
- **Use for**: Understanding relationships, exploring care pathways, system mapping
- **Command**: `python analysis/knowledge_graph/build_knowledge_graph_framework.py`

**Output**: JSON graph structure + HTML visualization
- 16 Organizations, 115 Services, 25 Pathways
- 19,374 Relationships mapped

**Example**: Visualize which services connect LTHT, LCH, and LYPFT

**Note**: The Knowledge Graph now **automatically enhances** Multi-Agent RAG queries!

---

### 4. Theme-Based Structured Analysis ✓
**Location**: `analysis/theme_analysis/`

- **Purpose**: Compare strategies, identify gaps against predefined themes
- **How it works**: Define themes → Compare across strategies → Identify what's missing/changed
- **Use for**: Strategic planning, gap analysis, strategy evolution tracking
- **Commands**:
  - `python analysis/theme_analysis/run_strategy_analysis.py` - Run both quick & full analysis
  - `python analysis/theme_analysis/theme_comparison_analysis.py` - Compare old vs new strategies
  - `python analysis/theme_analysis/workforce_strategy_gap_analysis.py` - Full gap analysis with evidence

**Phases**:
1. Quick theme comparison (FREE - no API calls)
2. Full RAG-based evidence synthesis (paid - ~$15-25)

**Example**: Compare 2021-25 strategy themes with 2026-31 proposed themes, identify gaps

---

## Which System Should You Use?

| Need | System | Why |
|------|--------|-----|
| **High-stakes strategic analysis** | ✨ **Multi-Agent** | Maximum confidence, iterative validation |
| **Quick exploratory questions** | RAG | Fast, low-cost, good enough for exploration |
| **Visualize entity relationships** | Knowledge Graph | See connections, pathways, system structure |
| **Strategy gap analysis** | Theme-Based | Structured comparison against themes |
| **Critical decisions** | ✨ **Multi-Agent** | Highest confidence, automatic refinement |
| **Complete picture** | All 4 | Use each for different perspectives |

**🌟 Recommendation**: Start with **Multi-Agent** for important questions - the KG integration makes it significantly more powerful (40-75% better evidence retrieval).

---

## Maintenance & Diagnostics

### Checking ChromaDB Metadata Integrity

After ingestion or metadata updates, verify that all chunks have proper date coverage:

```bash
python check_chromadb_metadata.py
```

**What it does:**
- Counts total chunks stored in ChromaDB
- Checks which documents have complete metadata (dates, themes, audiences)
- Identifies any chunks missing date information
- Compares ChromaDB contents with `document_dates.json`
- Lists documents in database vs. configuration file
- Provides recommendations for fixes

**Example output:**
```
====================================================================================================
CHROMADB METADATA CHECK
====================================================================================================

Total chunks in ChromaDB: 16983

Expected documents (from document_dates.json): 31

[OK] All chunks have dates
```

**Use this tool when:**
- After running a full rebuild to verify dates populated correctly
- Before running analysis to ensure metadata quality
- After updating `document_dates.json` to check sync
- Troubleshooting retrieval issues

**Note:** This script requires NO API key - it directly reads the ChromaDB database file.

---

## Individual Component Reference

### 2. Pipeline Scripts (in `pipeline/` folder)

#### **pipeline/clean_doc.py** - Filename Cleanup
- Removes special characters from filenames
- Automatically called by `run_full_pipeline.py`
- Usage: `python pipeline/clean_doc.py`

#### **pipeline/eval_dates.py** - Date Extraction

**Purpose**: Auto-extract publication/strategy dates from documents

**Usage:**
```bash
# Auto-extract and generate config
python pipeline/eval_dates.py

# Interactive mode - confirm each date
python pipeline/eval_dates.py --interactive
```

**Output**: `document_dates.json` (stores publication/strategy dates for all documents)

#### **pipeline/eval_tagging.py** - Tagging Validation

**Purpose**: Test and verify auto-tagging quality before ingestion

**Usage:**
```bash
python pipeline/eval_tagging.py
```

**Output**: Theme and audience assignments for document samples

#### **pipeline/ingest_pipeline.py** - Document Ingestion

**Purpose**: Ingest documents into ChromaDB with metadata

**What it does:**
1. Loads all `.md` and `.txt` files from `docs/`
2. Cleans filenames
3. Partitions documents into chunks
4. Auto-tags each chunk (Theme + Audience)
5. Loads dates from `document_dates.json`
6. Generates OpenAI embeddings
7. Stores in ChromaDB with metadata

**Usage:**
```bash
python pipeline/ingest_pipeline.py
```

**Ingestion Modes:**

The script automatically chooses based on what files exist:

| Scenario | What Happens | How to Trigger |
|----------|-------------|---|
| **Incremental** (Default) | Only processes NEW documents not yet in ChromaDB. Existing documents skipped. | Set `FULL_REBUILD = False` (line 77, default) |
| **Full Rebuild** | Deletes entire existing ChromaDB and re-ingests ALL documents | Set `FULL_REBUILD = True` (line 77) |

**When to Use Each:**

**Incremental Mode (Recommended for Most Cases)**
```python
# In pipeline/ingest_pipeline.py, line 77:
FULL_REBUILD = False  # Default
```
- ✓ You added 5 new documents to `docs/`
- ✓ Quick and efficient (only processes new files)
- ✓ Cheaper (no duplicate embedding costs)
- ✓ Results merge with existing database

**Full Rebuild Mode**
```python
# In pipeline/ingest_pipeline.py, line 77:
FULL_REBUILD = True
```
- ✓ You modified dates in `document_dates.json` and want them to apply to ALL documents
- ✓ You changed tagging logic in `utils.py` and want to re-tag everything
- ✓ You updated chunking parameters and need to repartition documents
- ✓ You want a completely fresh database from scratch

**Example: Adding 5 New Documents**
```bash
# 1. Add files to docs/
cp new_doc1.md new_doc2.md docs/

# 2. Update dates (optional)
python pipeline/eval_dates.py

# 3. Ingest - will only process the 5 new files (FULL_REBUILD=False)
python pipeline/ingest_pipeline.py
# Output: "Detected **5** new file(s) to process."
```

**Example: Full Rebuild After Tagging Changes**
```bash
# 1. Update tagging logic in utils/utils.py

# 2. Edit ingest_pipeline.py line 77:
# FULL_REBUILD = True

# 3. Run ingest
python pipeline/ingest_pipeline.py
# Output: "Detected FULL_REBUILD = True. Deleting existing ChromaDB..."
# Output: "Processing all 30 documents..."

# 4. After done, change back:
# FULL_REBUILD = False
```

**Output**: Updated `chroma_db_test/` vector database (16,983 chunks with complete metadata)

---

### 3. Analysis & Query Scripts

#### **analysis/analyze_pipeline.py** - Strategic Analysis

**Purpose**: Run pre-configured strategic queries with multi-source synthesis

**Usage:**
```bash
python analysis/analyze_pipeline.py
```

**Output**: `strategic_analysis_output_multi_source.md` report with:
- 5 strategic queries answered
- Multi-source citations (3+ sources per answer)
- Document recency flags
- Source tracking with dates

#### **query/interactive_query_multi_source.py** - Interactive Queries

**Purpose**: Ask your own questions about the documents

**Usage:**
```bash
python query/interactive_query_multi_source.py
```

**Example:**
```
Enter your question: What are key priorities?
[Searching...]
Answer: Based on [Source: doc1, doc2, doc3]...
```

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
        │ 16,983 chunks      │    │              │
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
python pipeline/eval_dates.py

# Interactive mode - confirm/override each date
python pipeline/eval_dates.py --interactive
```

**Output Example**:
```
[OK] Loaded 30 documents from docs/
[OK] Auto-extracted: 8 documents
[MANUAL ENTRY / FILE MTIME] 22 documents (user confirmed or auto-detected)
[OK] Generated document_dates.json with 30 entries
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
   python pipeline/eval_dates.py
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
python pipeline/ingest_pipeline.py
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
- Processed Files: **30**
- Total Chunks Ready: **16983**

### Updating ChromaDB...
  - Batch 1: Added 5000 chunks (Total: 5000)
  - Batch 2: Added 5000 chunks (Total: 10000)
  - Batch 3: Added 5000 chunks (Total: 15000)
  - Batch 4: Added 1983 chunks (Total: 16983)
[OK] ChromaDB updated successfully (16983 total chunks added).

[COMPLETE] Ingestion pipeline complete.
```

**Cost**: ~$0.70-1.20 per full run (tagging + embeddings); incremental updates cost significantly less

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
python analysis/analyze_pipeline.py
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
python query/interactive_query_multi_source.py
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

### Step 2-4: Use the Automated Pipeline

```bash
# This runs all steps automatically
python run_full_pipeline.py
```

**Alternatively, run steps individually:**

```bash
# Step 2: Update dates for new documents
python pipeline/eval_dates.py

# Step 3: Reingest (automatically detects new files)
python pipeline/ingest_pipeline.py
```

The ingestion pipeline automatically:
- Detects new files (files not already in ChromaDB) - **Incremental mode** (default)
- Cleans filenames if needed
- Processes only new documents (doesn't re-index existing ones)
- Updates ChromaDB with new chunks

**Note:** This is **incremental ingestion** (only new files). If you need to **full rebuild**:

```python
# Edit pipeline/ingest_pipeline.py line 77:
FULL_REBUILD = True    # Set to True for full rebuild
```

See "Ingestion Modes" section above for when to use full rebuild.

### Step 4: Re-run Analysis

```bash
# Optional: Generate updated analysis report
python analysis/analyze_pipeline.py
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
- ~16,983 chunks across 30 documents = ~$0.04 in embedding costs
- Initial run takes 10-15 minutes; subsequent runs are faster (incremental only)
- Cost is one-time for ingestion; queries are cheap

### Problem: Updated dates in document_dates.json but they're not reflected

**Cause**: Existing documents in ChromaDB weren't re-processed (incremental ingestion skips them)

**Solution**: Do a full rebuild:
1. Edit `pipeline/ingest_pipeline.py` line 77:
   ```python
   FULL_REBUILD = True
   ```
2. Run: `python pipeline/ingest_pipeline.py`
3. After done, change back:
   ```python
   FULL_REBUILD = False
   ```

### Problem: Changed tagging logic but old tags still in database

**Cause**: Existing documents retained old tags (incremental ingestion skips them)

**Solution**: Do a full rebuild:
1. Update `utils/utils.py` with new tagging logic
2. Edit `pipeline/ingest_pipeline.py` line 77: `FULL_REBUILD = True`
3. Run: `python pipeline/ingest_pipeline.py`
4. After done, change back: `FULL_REBUILD = False`

### Problem: Want completely fresh database

**Solution**: Full rebuild mode
```python
# Edit pipeline/ingest_pipeline.py line 77:
FULL_REBUILD = True

# Run ingestion
python pipeline/ingest_pipeline.py

# Change back after
FULL_REBUILD = False
```

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
- **Batch Processing**: Handles 16,983+ chunks without memory issues
- **Auto-Tagging**: Chunks categorized by Theme and Audience for better filtering
- **Interactive Queries**: Ask custom questions with date awareness

---

## Cost Analysis

### One-Time Costs (Initial Setup)

- **eval_dates.py**: $0 (Python regex, no API calls)
- **ingest_pipeline.py**: ~$0.70-1.30
  - Auto-tagging: ~$0.70 (GPT-3.5 for 16,983 tags)
  - Embeddings: ~$0.04 (OpenAI embedding API for all chunks)

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
├── run_full_pipeline.py                # Main entry point - run this!
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── document_dates.json                 # Config: publication/strategy dates (30 documents)
├── document_dates_schema.md            # Schema documentation
├── check_chromadb_metadata.py          # Metadata integrity checker (diagnostics)
│
├── pipeline/                           # Core ingestion pipeline
│   ├── clean_doc.py                    # Filename cleanup utility
│   ├── eval_dates.py                   # Date extraction evaluation tool
│   ├── eval_tagging.py                 # Tagging validation tool
│   └── ingest_pipeline.py              # Document ingestion pipeline
│
├── analysis/                           # Analysis systems (organized by type)
│   ├── rag/                            # RAG (Retrieval-Augmented Generation)
│   │   ├── analyze_pipeline.py         # Pre-configured strategic queries
│   │   └── interactive_query_multi_source.py  # Interactive query interface
│   │
│   ├── knowledge_graph/                # Knowledge Graph extraction
│   │   └── build_knowledge_graph_framework.py  # Entity & relationship extraction
│   │
│   └── theme_analysis/                 # Theme-Based structured analysis
│       ├── theme_comparison_analysis.py  # Old vs new strategy comparison
│       ├── workforce_strategy_gap_analysis.py  # Gap analysis with evidence
│       └── run_strategy_analysis.py     # Orchestrator for both analyses
│
├── utils/                              # Utilities
│   └── utils.py                        # Auto-tagging function (GPT-3.5)
│
├── docs/                               # Source documents (30 files: 27 MD + 3 TXT)
│   ├── 10-year-health-plan-for-england-executive-summary.md
│   ├── Assessment of priority skills to 2030 GOV UK.md
│   ├── CIPD Health and Wellbeing Report 2025.md
│   ├── Health Innovation North Turning Conversation into Collaboration.txt
│   ├── Healthy-Leeds-Plan-Executive-Summary_plain_text_DRAFT-v4.1.md
│   ├── LTHT-Annual-Report-2024-25-FINAL.md
│   ├── LYPFT Annual-Report-and-Accounts-2024-25.md
│   ├── Leeds Community Annual-report-2024-2025.md
│   ├── NHS England Board Meeting 23 September 2025.txt
│   ├── NHS England _ NHS Oversight Framework 2025_26 _ methodology manual.md
│   ├── Workforce-Strategy-2021-25-V1.0.md
│   ├── leeds health wellbeing strategy 2023-2030.md
│   └── ... (18 more strategic documents)
│
├── chroma_db_test/                     # ChromaDB vector store (auto-generated, 16,983 chunks)
├── prompts/                            # Prompt templates
├── archive_py/                         # Archived/old scripts
├── strategic_analysis_output_multi_source.md  # Analysis results (auto-generated)
└── .env                                # OpenAI API key (not in repo)
```

---

## Next Steps

### Quick Start Actions

1. **Run the complete pipeline** (if you haven't already):
   ```bash
   python run_full_pipeline.py
   ```
   This handles everything: cleaning → dates → ingestion

2. **Then choose what to do:**

   **Option A - Ask Questions Interactively**
   ```bash
   python query/interactive_query_multi_source.py
   ```

   **Option B - Generate Analysis Report**
   ```bash
   python analysis/analyze_pipeline.py
   ```

   **Option C - Workforce Strategy Analysis**
   ```bash
   python analysis/run_strategy_analysis.py
   ```

3. **Add new documents** and re-run:
   ```bash
   cp my_new_document.md docs/
   python run_full_pipeline.py
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

## Command Quick Reference

| What You Want | Command |
|---|---|
| **Ingest documents (new files only)** | `python run_full_pipeline.py` |
| **Ingest with QA check** | `python run_full_pipeline.py --validate` |
| **Full rebuild database** | Edit `pipeline/ingest_pipeline.py` line 77: `FULL_REBUILD = True` then run `python pipeline/ingest_pipeline.py` |
| **Check metadata integrity** | `python check_chromadb_metadata.py` |
| **Ask questions** | `python analysis/rag/interactive_query_multi_source.py` |
| **Generate analysis report** | `python analysis/rag/analyze_pipeline.py` |
| **Workforce strategy analysis** | `python analysis/theme_analysis/run_strategy_analysis.py` |
| **Build knowledge graph** | `python analysis/knowledge_graph/build_knowledge_graph_framework.py` |
| **Just update dates** | `python pipeline/eval_dates.py` |
| **Preview (dry-run)** | `python run_full_pipeline.py --dry-run` |

---

## Support & Questions

For questions about:
- **Date extraction**: See `pipeline/eval_dates.py` docstring
- **Tagging validation**: See `pipeline/eval_tagging.py` docstring
- **Ingestion process**: See `pipeline/ingest_pipeline.py` docstring
- **Analysis pipeline**: See `analysis/analyze_pipeline.py` docstring
- **Interactive queries**: See `query/interactive_query_multi_source.py` docstring
- **Multi-source synthesis**: See "Understanding the Multi-Source Enhancement" section above

All scripts include comprehensive docstrings and inline comments explaining functionality.

---

## Key Takeaways

✅ **For 95% of use cases, just run:**
```bash
python run_full_pipeline.py
```

✅ **After ingestion, choose your next action:**
- Ask questions: `python query/interactive_query_multi_source.py`
- Generate report: `python analysis/analyze_pipeline.py`
- Workforce analysis: `python analysis/run_strategy_analysis.py`

✅ **Adding documents?**
```bash
cp new_doc.md docs/
python run_full_pipeline.py
```

✅ **Scripts are organized by function:**
- `pipeline/` = ingestion (clean → dates → ingest)
- `analysis/` = analysis tools
- `query/` = interactive queries
- `utils/` = helper functions

✅ **Ingestion modes:**
- **Incremental (default)**: Only processes new documents - fast & cheap
- **Full Rebuild**: Deletes and re-ingests everything - set `FULL_REBUILD = True` in `pipeline/ingest_pipeline.py` line 77
