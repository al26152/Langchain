# document_dates.json Schema & Guide

## Purpose

`document_dates.json` is a configuration file that stores publication/strategy dates for all documents. It serves as a fallback when date extraction isn't possible and enables date-aware analysis.

## Usage

- **Read by**: `ingest_pipeline.py` (stores dates in ChromaDB metadata)
- **Read by**: `analyze_pipeline.py` (flags old/expiring documents in reports)
- **Updated by**: `eval_dates.py` (auto-extraction tool)

## Structure

The file maps each document filename to its date information:

```json
{
  "filename.md": {
    "date": "YYYY-MM-DD",
    "source": "auto|manual|unknown",
    "year_range": ["YYYY", "YYYY"] or null,
    "notes": "Context about the date"
  }
}
```

## Field Definitions

### `date` (String, required)
- **Format**: `"YYYY-MM-DD"` (ISO 8601)
- **Examples**: `"2025-01-29"`, `"2024-06-30"`, `"2021-01-01"`
- **Purpose**: Primary date for the document (publication, updated, or fiscal year end)
- **For strategies**: Use the strategy start date (e.g., 2021 for "2021-2025" strategy)

### `source` (String, required)
- **Valid values**: `"auto"`, `"manual"`, `"unknown"`
- **`"auto"`**: Date was automatically extracted from document content by `eval_dates.py`
- **`"manual"`**: Date was manually entered or confirmed by user via `eval_dates.py --interactive`
- **`"unknown"`**: Date couldn't be determined; used as placeholder for now
- **Purpose**: Tracks how reliably the date was determined

### `year_range` (Array or null, optional)
- **Format**: `["YYYY", "YYYY"]` for multi-year documents, `null` for single-date documents
- **Examples**:
  - Multi-year strategy: `["2021", "2025"]`
  - Annual report: `null`
  - Fiscal year: `["2023", "2024"]`
- **Purpose**: For strategies or fiscal reports that span multiple years
- **Used for**: Expiry warnings (e.g., "STRATEGY EXPIRES 2025")

### `notes` (String, optional)
- **Purpose**: Context or explanation about the document and its date
- **Examples**:
  - `"Auto-extracted from 'Date published: 29 January, 2025'. RECENT - guidance for current year"`
  - `"Multi-year strategy 2021-2025. EXPIRING SOON (2025). Use with caution - will need replacement/update."`
  - `"Annual Report for fiscal year 2023-2024. Assuming June 30 year-end."`

## Date Priority (Extraction Order)

When `eval_dates.py` processes documents, it looks for dates in this order:

1. **Published date** - "Date published: 29 January, 2025"
2. **Updated date** - "Date updated: 15 March, 2025"
3. **Fiscal year** - "Fiscal year 2024-2025" or from filename
4. **Year range** - "2021-25 Strategy" or filename pattern
5. **Manual entry** - User provides via `eval_dates.py --interactive`

## How to Update

### Adding New Documents

1. Add your `.md` or `.txt` files to the `docs/` directory
2. Run date evaluation:
   ```bash
   python eval_dates.py
   ```
3. This will auto-detect new files and add them to `document_dates.json`
4. Then run ingestion:
   ```bash
   python ingest_pipeline.py
   ```

### Correcting Existing Dates

Edit `document_dates.json` directly:

1. Find the document filename (must match exactly, case-sensitive)
2. Update the `"date"` field
3. Change `"source"` to `"manual"` to indicate manual override
4. Add explanatory notes if helpful
5. Save the file
6. Re-run ingestion to update ChromaDB:
   ```bash
   python ingest_pipeline.py
   ```

**Example Before**:
```json
"Old Report 2020.md": {
  "date": "2020-06-15",
  "source": "auto",
  "year_range": null,
  "notes": "Auto-extracted but may be incorrect"
}
```

**Example After**:
```json
"Old Report 2020.md": {
  "date": "2020-09-15",
  "source": "manual",
  "year_range": null,
  "notes": "Corrected to September 2020 based on document review"
}
```

## Recency Flags (How Dates Are Used)

The `analyze_pipeline.py` uses these dates to generate flags:

| Flag | Meaning | Calculation |
|------|---------|-------------|
| `[RECENT]` | Less than 1 year old | `days_old < 365` |
| `[RECENT - 1 YEAR]` | 1-2 years old | `365 <= days_old < 730` |
| `[OLDER DOCUMENT - 2+ YEARS]` | 2-4 years old | `730 <= days_old < 1460` |
| `[ARCHIVAL - 4+ YEARS]` | Older than 4 years | `days_old >= 1460` |
| `[STRATEGY EXPIRES YYYY]` | Strategy expiring within 1 year | `year_range_end - current_year <= 1` |
| `[NO DATE]` | Date not found in config | Document not in `document_dates.json` |

## Common Issues & Solutions

### Issue: `[NO DATE]` flag but document has a date configured

**Cause**: Filename mismatch between `docs/` folder and `document_dates.json`

**Solution**: Check exact filename:
```bash
# See actual filenames in docs/
ls -la docs/

# Update document_dates.json to match exactly (case-sensitive)
# Example:
# WRONG: "Leeds Community Annual Report.md"
# RIGHT: "Leeds-Community-Annual-Report-2024-2025.md"
```

### Issue: Auto-extraction didn't find a date

**Cause**: Date format in document not recognized by `eval_dates.py` patterns

**Solution**: Manually add to `document_dates.json`:
```bash
# Run interactive mode to add manually
python eval_dates.py --interactive
```

Or edit `document_dates.json` directly:
```json
"Undated Report.md": {
  "date": "2024-03-15",
  "source": "manual",
  "year_range": null,
  "notes": "Date manually entered based on document review"
}
```

### Issue: Document has year range but single date in config

**Solution**: For multi-year documents (strategies, multi-year reports), add `year_range`:

```json
"NHS Strategy 2023-2027.md": {
  "date": "2023-01-01",          // Use start year
  "source": "manual",
  "year_range": ["2023", "2027"],  // Add the range
  "notes": "Strategy spans 2023-2027. Will expire 2027."
}
```

## Batch Import Example

If adding many documents, you can manually batch-add them to `document_dates.json`:

```json
{
  "existing-doc-1.md": { ... },

  "new-strategy-2025-2030.md": {
    "date": "2025-01-15",
    "source": "manual",
    "year_range": ["2025", "2030"],
    "notes": "New 5-year strategy. Recently approved."
  },

  "new-report-q4-2025.md": {
    "date": "2025-10-31",
    "source": "manual",
    "year_range": null,
    "notes": "Q4 2025 performance report"
  },

  "existing-doc-2.md": { ... }
}
```

After adding, run:
```bash
python ingest_pipeline.py
```

## Technical Notes

- **JSON Compliance**: `document_dates.json` is valid JSON (no comments) for tool compatibility
- **Date Format**: All dates must be ISO 8601 format (`YYYY-MM-DD`)
- **Filename Case**: Filenames are case-sensitive and must match exactly
- **Special Characters**: Filenames should use `_` instead of `»` (handled by `clean_doc.py`)
- **No Timezone**: Dates are assumed to be in local system timezone for recency calculation

## Schema Validation

To validate your `document_dates.json` file:

```bash
python -m json.tool document_dates.json > /dev/null && echo "Valid JSON"
```

Or in Python:
```python
import json
with open('document_dates.json', 'r') as f:
    config = json.load(f)
    print(f"Loaded {len(config)} documents")
```

## Related Files

- **`eval_dates.py`** - Tool to auto-extract dates
- **`ingest_pipeline.py`** - Reads this config during document ingestion
- **`analyze_pipeline.py`** - Uses dates for recency flagging
- **`README.md`** - Main pipeline documentation
