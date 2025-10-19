# Date Tracking Integration Summary

## What Was Done

Integrated comprehensive date tracking into the RAG ingestion and analysis pipelines to track document recency and flag aging/expiring strategic documents.

## Files Created/Modified

### 1. **eval_dates.py** (Created - Evaluation Tool)
Evaluates date extraction across documents

**Features:**
- Auto-extracts dates from documents (published, updated, fiscal year, strategy year-range)
- Generates `document_dates.json` config file
- Interactive mode (`--interactive` flag) for confirming/overriding dates
- Handles multiple date patterns (ISO, text format, year ranges)

**Usage:**
```bash
python eval_dates.py                  # Auto-extract and generate config
python eval_dates.py --interactive    # Confirm/override dates interactively
```

---

### 2. **document_dates.json** (Created - Configuration File)

Stores publication/strategy dates for all documents

**Structure:**
```json
{
  "filename.md": {
    "date": "YYYY-MM-DD",                    // Primary date
    "source": "auto|manual|unknown",         // How date was obtained
    "year_range": ["YYYY", "YYYY"] or null,  // Strategy dates
    "notes": "Context about the date"
  }
}
```

**Key features:**
- Comprehensive header documentation explaining usage
- Auto-extracted dates (marked with `"source": "auto"`)
- Manual dates (marked with `"source": "manual"`)
- Unknown dates (marked with `"source": "unknown"`)
- Notes field with context about each document
- Flags for RECENT, RECENT-1YEAR, OLDER, ARCHIVAL, EXPIRING

**When to update:**
- Run `eval_dates.py` after adding new documents
- Edit manually if dates need correction

---

### 3. **ingest_pipeline.py** (Modified - Ingestion Pipeline)

Updated to load and integrate document dates into ChromaDB metadata

**New functionality:**
- `load_document_dates()` - Loads `document_dates.json` config
- `get_document_date()` - Retrieves date for a specific document
- `get_document_year_range()` - Retrieves strategy year range
- Stores in chunk metadata:
  - `date`: Publication date (YYYY-MM-DD)
  - `year_range_start`: Strategy start year
  - `year_range_end`: Strategy end year

**Metadata now stored per chunk:**
```python
metadata = {
  "source": filename,
  "date": "2025-01-29",              # From document_dates.json
  "year_range_start": "2021",        # If applicable
  "year_range_end": "2025",          # If applicable
  "theme": "Healthcare reform",
  "audience": "Policymakers",
  "element_type": "NarrativeText",
  ...
}
```

**Updated workflow:**
```
1. Load documents
2. Clean filenames
3. Partition documents
4. Auto-tag (Theme/Audience)
5. LOAD DATES from document_dates.json ← NEW
6. Generate embeddings
7. Store in ChromaDB with date metadata
```

---

### 4. **analyze_pipeline.py** (Modified - Analysis Pipeline)

Updated to read dates and flag old/expiring documents in reports

**New functionality:**
- `get_recency_flag()` - Generates age flags based on document date
  - `[RECENT]` - Less than 1 year old
  - `[RECENT - 1 YEAR]` - 1-2 years old
  - `[OLDER DOCUMENT - 2+ YEARS]` - 2-4 years old
  - `[ARCHIVAL - 4+ YEARS]` - Older than 4 years
  - `[STRATEGY EXPIRES YYYY]` - Strategy ending soon
  - `[NO DATE]` - Date not found

**Updated output format:**
```
**All Retrieved Chunks:**
- 1. `filename.md` [RECENT]
    Published: 2025-01-29 | Theme: Healthcare reform
    Snippet: ...

- 2. `strategy.md` [STRATEGY EXPIRES 2025]
    Published: 2021-01-01 | Theme: Workforce Development
    Snippet: ...

- 3. `old_report.md` [OLDER DOCUMENT - 2+ YEARS]
    Published: 2020-06-15 | Theme: Health Equity
    Snippet: ...
```

---

## Data Flow

```
                eval_dates.py
                     |
                     v
           document_dates.json
                     |
          ___________|___________
         |                       |
         v                       v
  ingest_pipeline.py     analyze_pipeline.py
         |                       |
         v                       v
   ChromaDB + dates          Flagged output
  (Date metadata)          (RECENT, ARCHIVAL, etc.)
```

---

## How to Use (Complete Workflow)

### Step 1: Evaluate and Generate Date Config
```bash
python eval_dates.py
# or with interactive confirmation:
python eval_dates.py --interactive
```
Output: `document_dates.json`

### Step 2: Ingest Documents with Dates
```bash
python ingest_pipeline.py
```
- Loads `document_dates.json`
- Stores dates in ChromaDB metadata
- Output: Updated ChromaDB with date metadata

### Step 3: Analyze with Recency Flags
```bash
python analyze_pipeline.py
```
- Reads dates from ChromaDB
- Flags old/expiring documents
- Output: `strategic_analysis_output_multi_source.md` with date flags

### Step 4: Interactive Queries (Optional)
```bash
python interactive_query_multi_source.py
```
- Ask questions interactively
- Receive multi-source answers with dates and recency flags

---

## Adding New Documents

When you add new documents to `docs/`:

1. **Run date evaluation:**
   ```bash
   python eval_dates.py
   ```
   It will detect new files and update `document_dates.json`

2. **Run ingestion:**
   ```bash
   python ingest_pipeline.py
   ```
   It will pick up new document_dates.json entries

3. **Run analysis:**
   ```bash
   python analyze_pipeline.py
   ```
   New documents appear in reports with proper date flags

---

## Key Features

✅ **Automatic date extraction** - Finds published dates, updated dates, fiscal years
✅ **Fallback configuration** - Manual entries in document_dates.json
✅ **Recency tracking** - Flags documents by age (Recent, Older, Archival)
✅ **Strategy expiry warnings** - Highlights strategies ending soon
✅ **Date-aware analysis** - Shows publication dates in analysis output
✅ **Easy maintenance** - Update document_dates.json with new documents

---

## Important Notes

- **document_dates.json is version-controlled** - Commit it to git
- **Dates are optional** - System works without dates (just won't flag recency)
- **Auto-extraction handles:**
  - "Date published: 2025-01-29"
  - "Date updated: 2025-01-29"
  - "Fiscal year 2024-2025"
  - "Strategy 2021-25" (from filename or content)
- **No date strategy** - Set manually in JSON if extraction fails
- **Timezone-aware** - Uses system's current date/time for recency calculation

---

## Testing

All three files were created/modified with comprehensive documentation:

1. **eval_dates.py** - Full docstring + inline comments
2. **document_dates.json** - 50-line header documentation
3. **ingest_pipeline.py** - Updated docstring + function docs
4. **analyze_pipeline.py** - Updated docstring + recency function docs
