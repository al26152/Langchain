"""
Check ChromaDB Metadata - Identify missing dates and metadata gaps
NO API KEY REQUIRED - Direct ChromaDB access
"""

import os
import json
import chromadb
from collections import defaultdict

STORE_DIR = "chroma_db_test"
DATES_CONFIG_FILE = "document_dates.json"

def load_document_dates():
    """Load document dates from JSON."""
    if not os.path.exists(DATES_CONFIG_FILE):
        return {}

    try:
        with open(DATES_CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def check_chromadb_metadata():
    """Check ChromaDB for missing metadata."""

    if not os.path.exists(STORE_DIR):
        print(f"[ERROR] ChromaDB directory '{STORE_DIR}' not found.")
        return

    # Connect directly to ChromaDB
    client = chromadb.PersistentClient(path=STORE_DIR)
    collection = client.get_or_create_collection(name="langchain")

    # Get all data
    all_data = collection.get(include=["metadatas", "documents"])
    metadatas = all_data.get("metadatas", [])
    documents = all_data.get("documents", [])

    print("=" * 100)
    print("CHROMADB METADATA CHECK")
    print("=" * 100)
    print(f"\nTotal chunks in ChromaDB: {len(documents)}\n")

    # Load expected dates from JSON
    expected_dates = load_document_dates()
    print(f"Expected documents (from document_dates.json): {len(expected_dates)}\n")

    # Analyze metadata
    chunks_by_source = defaultdict(list)
    missing_dates = []
    missing_theme = []
    missing_audience = []

    for i, metadata in enumerate(metadatas):
        source = metadata.get("source", "UNKNOWN")
        chunks_by_source[source].append({
            "index": i,
            "date": metadata.get("date"),
            "theme": metadata.get("theme"),
            "audience": metadata.get("audience"),
            "chunk_type": metadata.get("chunk_type"),
        })

        # Track missing metadata
        if not metadata.get("date") or metadata.get("date") == "None":
            missing_dates.append((source, i))

        if not metadata.get("theme") or metadata.get("theme") == "unknown":
            missing_theme.append((source, i))

        if not metadata.get("audience") or metadata.get("audience") == "unknown":
            missing_audience.append((source, i))

    # Report by source document
    print("CHUNKS PER DOCUMENT SOURCE:")
    print("-" * 100)
    for source in sorted(chunks_by_source.keys()):
        chunks = chunks_by_source[source]
        dates_present = sum(1 for c in chunks if c["date"])
        themes_present = sum(1 for c in chunks if c["theme"] != "unknown")
        audiences_present = sum(1 for c in chunks if c["audience"] != "unknown")

        in_json = "[OK]" if source in expected_dates else "[MISSING]"

        print(f"\n  {in_json} {source}")
        print(f"      Chunks: {len(chunks)}")
        print(f"      Dates: {dates_present}/{len(chunks)}", end="")
        if dates_present == len(chunks):
            print(" [OK]")
        else:
            print(f" [WARN] ({len(chunks) - dates_present} missing)")

        print(f"      Themes: {themes_present}/{len(chunks)}", end="")
        if themes_present == len(chunks):
            print(" [OK]")
        else:
            print(f" [WARN] ({len(chunks) - themes_present} missing)")

        print(f"      Audiences: {audiences_present}/{len(chunks)}", end="")
        if audiences_present == len(chunks):
            print(" [OK]")
        else:
            print(f" [WARN] ({len(chunks) - audiences_present} missing)")

    # Detailed missing metadata report
    print(f"\n\n" + "=" * 100)
    print("MISSING METADATA ISSUES")
    print("=" * 100)

    sources_missing_dates = defaultdict(int)
    for source, _ in missing_dates:
        sources_missing_dates[source] += 1

    if missing_dates:
        print(f"\n[WARN] MISSING DATES: {len(missing_dates)} chunks\n")
        for source in sorted(sources_missing_dates.keys()):
            count = sources_missing_dates[source]
            expected_date = expected_dates.get(source, {}).get("date", "NOT IN JSON")
            print(f"  - {source}: {count} chunks missing date")
            print(f"    Expected date: {expected_date}")
    else:
        print(f"\n[OK] All chunks have dates\n")

    # Check for sources in ChromaDB but not in JSON
    print(f"\n" + "=" * 100)
    print("DOCUMENT COVERAGE")
    print("=" * 100)

    chroma_sources = set(chunks_by_source.keys())
    json_sources = set(expected_dates.keys())

    missing_from_json = chroma_sources - json_sources
    missing_from_chroma = json_sources - chroma_sources

    print(f"\nDocuments in ChromaDB: {len(chroma_sources)}")
    print(f"Documents in JSON: {len(json_sources)}")
    print(f"Documents in BOTH: {len(chroma_sources & json_sources)}")

    if missing_from_json:
        print(f"\n[WARN] In ChromaDB but NOT in JSON ({len(missing_from_json)}):")
        for source in sorted(missing_from_json):
            print(f"  - {source}")

    if missing_from_chroma:
        print(f"\n[WARN] In JSON but NOT in ChromaDB ({len(missing_from_chroma)}):")
        for source in sorted(missing_from_chroma):
            print(f"  - {source}")

    # Sample chunks
    print(f"\n\n" + "=" * 100)
    print("SAMPLE CHUNKS (First 3)")
    print("=" * 100)

    for i in range(min(3, len(documents))):
        metadata = metadatas[i]
        doc_preview = documents[i][:80].replace("\n", " ")

        print(f"\n[Chunk {i+1}]")
        print(f"  Content: {doc_preview}...")
        print(f"  Metadata:")
        print(f"    - source: {metadata.get('source')}")
        print(f"    - date: {metadata.get('date')}")
        print(f"    - theme: {metadata.get('theme')}")
        print(f"    - audience: {metadata.get('audience')}")
        print(f"    - chunk_type: {metadata.get('chunk_type')}")
        print(f"    - element_type: {metadata.get('element_type')}")

    print(f"\n\n" + "=" * 100)
    print("RECOMMENDATION")
    print("=" * 100)

    if missing_dates or missing_from_json or missing_from_chroma:
        print("\n[WARN] Issues detected. Consider:")
        print("   1. Set FULL_REBUILD = True in ingest_pipeline.py")
        print("   2. Run: python ingest_pipeline.py")
        print("   3. This will re-ingest all documents with current metadata")
    else:
        print("\n[OK] All chunks have complete metadata")

    print("\n" + "=" * 100)

if __name__ == "__main__":
    check_chromadb_metadata()
