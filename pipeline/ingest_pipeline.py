"""
ingest_pipeline.py

DOCUMENT INGESTION PIPELINE

PURPOSE:
  Automates the complete document ingestion process:
  1. Loads documents from docs/ directory
  2. Cleans filenames (removes special characters)
  3. Partitions documents into text elements
  4. Auto-tags each chunk with Theme and Audience using AI
  5. Loads document dates from document_dates.json (publication/strategy dates)
  6. Generates embeddings via OpenAI
  7. Stores enriched chunks in ChromaDB for retrieval

WORKFLOW:
  documents (docs/)
    ↓
  Filename cleanup (clean_doc.py)
    ↓
  Text partitioning (unstructured)
    ↓
  Auto-tagging (GPT-3.5-turbo)
    ↓
  Date lookup (document_dates.json)
    ↓
  Embedding generation (OpenAI)
    ↓
  ChromaDB storage (chroma_db_test/)

METADATA STORED PER CHUNK:
  - source: filename
  - date: publication/strategy date
  - year_range: [start, end] for multi-year strategies
  - theme: auto-assigned category (Theme tagging)
  - audience: target audience (Theme tagging)
  - document_type: classification (STRATEGIC_PLAN, OPERATIONAL_GUIDANCE, ORG_SPECIFIC, PARTNERSHIP, GENERAL)
  - strategic_level: classification (NATIONAL, SYSTEM, ORGANIZATION, LOCAL)
  - organization: primary organization mentioned
  - element_type: Partition type (Title, NarrativeText, etc)
  - page_number: document page reference
  - chunk_type: narrative, table_data, or table_context
  - content_category: optional content type (staff_wellbeing_metrics, performance_benchmark)

USAGE:
  python ingest_pipeline.py

DEPENDENCIES:
  - document_dates.json: Run eval_dates.py first to generate
  - .env: OpenAI API key

OUTPUT:
  - Updated ChromaDB in chroma_db_test/ directory
  - Console report of ingestion progress with date tracking

COST:
  - OpenAI embedding API calls (~$0.02 per 1M tokens)
  - OpenAI tagging API calls (~$0.50 per 1K tags)
"""

import os
import shutil
import sys
import json
from io import StringIO
from typing import Set, List, Dict, Optional
from datetime import datetime

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

import sys
import os

# Add parent directory to path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.utils import auto_tag, classify_document_type

# Import clean_docs - handle both direct execution and package import
try:
    from .clean_doc import clean_docs
except ImportError:
    from pipeline.clean_doc import clean_docs
from unstructured.partition.auto import partition
from unstructured.documents.elements import Title, NarrativeText, ListItem, Table, Text

# --- CONFIGURATION ——————————————————————————————————————————————————

DOCS_PATH = "docs"
STORE_DIR = "chroma_db_test"
FULL_REBUILD = False  # Rebuild complete - reset to False for incremental ingestion
MIN_ELEMENT_TEXT_LENGTH = 50
DATES_CONFIG_FILE = "document_dates.json"


def load_document_dates() -> Dict[str, Dict]:
    """
    Load document dates from document_dates.json.

    Returns dict mapping filename to date info:
      {
        "filename.md": {
          "date": "YYYY-MM-DD",
          "source": "auto|manual|unknown",
          "year_range": ["YYYY", "YYYY"] or null,
          "notes": "..."
        }
      }
    """
    if not os.path.exists(DATES_CONFIG_FILE):
        print(f"[WARN] document_dates.json not found. Skipping date metadata.")
        print(f"       Run: python eval_dates.py\n")
        return {}

    try:
        with open(DATES_CONFIG_FILE, "r") as f:
            dates_config = json.load(f)
        print(f"[OK] Loaded dates for {len(dates_config)} document(s) from document_dates.json\n")
        return dates_config
    except Exception as e:
        print(f"[WARN] Error loading document_dates.json: {e}")
        print(f"       Run: python eval_dates.py\n")
        return {}


def get_document_date(filename: str, dates_config: Dict) -> Optional[str]:
    """Get publication date for a document, or None if not available."""
    if not dates_config:
        return None

    doc_info = dates_config.get(filename, {})
    return doc_info.get("date")


def get_document_year_range(filename: str, dates_config: Dict) -> Optional[List[str]]:
    """Get year range for a strategy document, or None if not applicable."""
    if not dates_config:
        return None

    doc_info = dates_config.get(filename, {})
    return doc_info.get("year_range")


def get_existing_sources(vectordb: Chroma) -> Set[str]:
    """Get set of document filenames already in ChromaDB."""
    existing_sources = set()
    try:
        all_db_data = vectordb._collection.get(include=["metadatas"])
        for metadata_entry in all_db_data.get("metadatas", []):
            if "source" in metadata_entry:
                existing_sources.add(metadata_entry["source"])
        print(f"Found **{len(existing_sources)}** existing document sources in ChromaDB.\n")
    except Exception as e:
        print(f"Could not retrieve existing document sources (possibly empty DB): {e}\n")
    return existing_sources


def get_new_files(docs_path: str, existing_sources: Set[str]) -> Set[str]:
    """Detect new files not yet in database."""
    if not os.path.exists(docs_path):
        print(f"[ERROR] Document path `{docs_path}` does not exist.")
        return set()

    docs_files = set([f for f in os.listdir(docs_path) if f.endswith((".md", ".txt"))])
    new_files = docs_files - existing_sources
    return new_files


def clean_and_ingest(docs_path: str, vectordb: Chroma, existing_sources: Set[str],
                     dates_config: Dict, full_rebuild: bool = False) -> int:
    """
    Main ingestion logic: clean, partition, tag, add dates, and store documents.

    Args:
        docs_path: Path to documents directory
        vectordb: ChromaDB instance
        existing_sources: Set of filenames already in database
        dates_config: Document dates loaded from document_dates.json
        full_rebuild: Whether to rebuild entire database

    Returns: Number of documents processed
    """
    processed_files_count = 0
    all_chunks_to_add = []

    for filename in sorted(os.listdir(docs_path)):
        if not filename.endswith((".md", ".txt")):
            continue

        file_path = os.path.join(docs_path, filename)
        print(f"### Processing File: `{filename}`")

        # Skip if file already exists and not doing full rebuild
        if not full_rebuild and filename in existing_sources:
            print(f"- Skipping `{filename}` (already in database).")
            continue

        # Partition document into elements
        try:
            elements = partition(filename=file_path)
            print(f"- Partitioned into {len(elements)} raw elements.")
        except Exception as e:
            print(f"[WARN] Error partitioning `{filename}`: {e}")
            continue

        # Extract sample text for auto-tagging (include title, narrative, and contextual headers)
        doc_content_for_tagging = ""
        for element in elements:
            if hasattr(element, "text") and isinstance(element.text, str) and element.text.strip():
                # Include titles, narrative text, and text elements (which include added context)
                if isinstance(element, (Title, NarrativeText, Text)):
                    doc_content_for_tagging += element.text + " "
                if len(doc_content_for_tagging) >= 1000:
                    break

        # If document title suggests table data, ensure it's included in tagging sample
        if "staff survey" in filename.lower() or "benchmark" in filename.lower():
            doc_content_for_tagging = f"Staff survey and wellbeing metrics report: {doc_content_for_tagging}"

        # Auto-tag document with theme and audience
        theme, audience = "unknown", "unknown"
        if doc_content_for_tagging.strip():
            try:
                theme, audience = auto_tag(doc_content_for_tagging.strip())
                print(f"- Auto-tagged: **Theme = '{theme}'**, **Audience = '{audience}'**")
            except Exception as e:
                print(f"[WARN] Auto-tagging error: {e}")
        else:
            print("- No sufficient text for auto-tagging. Using defaults.")

        # Classify document by type, strategic level, and organization
        doc_type, strategic_level, organization = "GENERAL", "LOCAL", "Unknown"
        if doc_content_for_tagging.strip():
            try:
                doc_type, strategic_level, organization = classify_document_type(filename, doc_content_for_tagging.strip())
                print(f"- Classified: **Type = '{doc_type}'**, **Level = '{strategic_level}'**, **Organization = '{organization}'**")
            except Exception as e:
                print(f"[WARN] Document classification error: {e}")
        else:
            print("- No sufficient text for classification. Using defaults.")

        # Create document chunks with metadata
        current_document_chunks = []
        for i, element in enumerate(elements):
            if not hasattr(element, "text") or not isinstance(element.text, str):
                continue
            text_content = element.text.strip()
            if not text_content or len(text_content) < MIN_ELEMENT_TEXT_LENGTH:
                continue

            chunk_id = f"{filename}_element_{i}_{hash(text_content[:min(len(text_content), 500)])}"

            # Get document date and year range from config
            doc_date = get_document_date(filename, dates_config)
            doc_year_range = get_document_year_range(filename, dates_config)

            # Detect if this chunk is table data or contextual header
            is_table_chunk = False
            chunk_type = "narrative"
            if "**Table Data:**" in text_content or "|" in text_content:
                is_table_chunk = True
                chunk_type = "table_data" if "|" in text_content else "table_context"

            metadata = {
                "id": chunk_id,
                "source": filename,
                "date": doc_date,  # Publication/strategy date (YYYY-MM-DD or null)
                "theme": theme,
                "audience": audience,
                "document_type": doc_type,  # NEW: classification (STRATEGIC_PLAN, OPERATIONAL_GUIDANCE, etc.)
                "strategic_level": strategic_level,  # NEW: classification (NATIONAL, SYSTEM, ORGANIZATION, LOCAL)
                "organization": organization,  # NEW: primary organization mentioned
                "element_type": type(element).__name__,
                "page_number": getattr(element.metadata, "page_number", "N/A"),
                "chunk_type": chunk_type,  # narrative, table_data, or table_context
            }

            # Year_range for multi-year strategies
            if doc_year_range:
                metadata["year_range_start"] = doc_year_range[0]
                metadata["year_range_end"] = doc_year_range[1]

            # Add table content flag for better filtering
            if is_table_chunk and "staff survey" in filename.lower():
                metadata["content_category"] = "staff_wellbeing_metrics"
            elif is_table_chunk and "benchmark" in filename.lower():
                metadata["content_category"] = "performance_benchmark"

            # Add optional metadata fields
            for key in [
                "filename", "file_directory", "filetype", "languages", "category", "url",
                "last_modified", "sent_from", "sent_to", "subject"
            ]:
                value = getattr(element.metadata, key, None)
                if value is not None and key not in metadata:
                    if isinstance(value, (str, int, float, bool)):
                        metadata[key] = value
                    elif key == "languages" and isinstance(value, list) and value:
                        metadata[key] = ", ".join(value)

            current_document_chunks.append(Document(page_content=text_content, metadata=metadata))

        if current_document_chunks:
            all_chunks_to_add.extend(current_document_chunks)
            processed_files_count += 1
            print(f"- [OK] Added {len(current_document_chunks)} chunks.\n")
        else:
            print(f"- [WARN] No valid chunks extracted.\n")

    # Update ChromaDB
    print(f"## Ingestion Summary\n")
    print(f"- Processed Files: **{processed_files_count}**")
    print(f"- Total Chunks Ready: **{len(all_chunks_to_add)}**\n")

    if all_chunks_to_add:
        print("### Updating ChromaDB...")
        # Add documents in batches to avoid ChromaDB batch size limits (~5461 max)
        batch_size = 5000
        total_added = 0

        for i in range(0, len(all_chunks_to_add), batch_size):
            batch = all_chunks_to_add[i:i+batch_size]
            vectordb.add_documents(batch)
            total_added += len(batch)
            print(f"  - Batch {i//batch_size + 1}: Added {len(batch)} chunks (Total: {total_added})")

        print(f"[OK] ChromaDB updated successfully ({total_added} total chunks added).\n")
    else:
        print("[INFO] No updates made to ChromaDB.\n")

    return processed_files_count


def main():
    """Main ingestion pipeline."""
    print("# Document Ingestion Pipeline\n")
    print("## Initialization\n")
    print("Starting document ingestion...\n")

    # Handle full rebuild
    if FULL_REBUILD:
        print(f"Detected FULL_REBUILD = True. Deleting existing ChromaDB at `{STORE_DIR}`...")
        shutil.rmtree(STORE_DIR, ignore_errors=True)
        print("[DONE] ChromaDB wiped clean.\n")

    # Create storage directory if needed
    if not os.path.exists(STORE_DIR):
        print(f"Creating ChromaDB persistence directory: `{STORE_DIR}`\n")
        os.makedirs(STORE_DIR)

    # Initialize embeddings and vector store
    print("## Embedding & Vector Store Setup\n")
    embeddings = OpenAIEmbeddings()
    print("[OK] Initialized OpenAI Embeddings client.\n")
    vectordb = Chroma(persist_directory=STORE_DIR, embedding_function=embeddings)
    print("[OK] ChromaDB vector store initialized.\n")

    # Get existing sources
    existing_sources = get_existing_sources(vectordb)

    # Check docs directory exists
    if not os.path.exists(DOCS_PATH):
        print(f"[ERROR] Document path `{DOCS_PATH}` does not exist. Please add your documents.")
        return

    # Detect and clean new files
    print("## Checking for New Files\n")
    new_files = get_new_files(DOCS_PATH, existing_sources)

    if new_files:
        print(f"Detected **{len(new_files)}** new file(s) to process.")
        print(f"Running filename cleanup on new files...\n")
        clean_docs(docs_path=DOCS_PATH, verbose=True)
        print()
    else:
        print(f"No new files detected. Skipping cleanup.\n")

    # Load document dates
    print("## Loading Document Dates\n")
    dates_config = load_document_dates()

    # Ingest documents with date metadata
    print(f"## Processing Documents from `{DOCS_PATH}`\n")
    clean_and_ingest(DOCS_PATH, vectordb, existing_sources, dates_config, full_rebuild=FULL_REBUILD)

    print("---\n[COMPLETE] Ingestion pipeline complete.\n")
    print(f"ChromaDB ready at: {STORE_DIR}\n")
    print("Next step: Run analyze_pipeline.py to perform analysis on ingested documents")


if __name__ == "__main__":
    main()
