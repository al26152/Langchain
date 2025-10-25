"""
Inspect ChromaDB - Check metadata and chunking across all stored documents
"""

import os
import json
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

STORE_DIR = "chroma_db_test"

def inspect_chromadb():
    """Inspect ChromaDB contents and metadata."""

    if not os.path.exists(STORE_DIR):
        print(f"[ERROR] ChromaDB directory '{STORE_DIR}' not found.")
        return

    # Initialize embeddings and vector store
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=STORE_DIR, embedding_function=embeddings)

    # Get all data with metadata
    all_data = vectordb._collection.get(include=["metadatas", "documents", "distances"])

    documents = all_data.get("documents", [])
    metadatas = all_data.get("metadatas", [])

    print("=" * 100)
    print("CHROMADB INSPECTION REPORT")
    print("=" * 100)
    print(f"\nTotal chunks stored: {len(documents)}\n")

    # Analyze metadata
    metadata_fields = set()
    documents_with_dates = 0
    documents_with_year_range = 0
    sources_with_chunks = {}

    for i, metadata in enumerate(metadatas):
        # Track which fields are present
        metadata_fields.update(metadata.keys())

        # Count documents with dates
        if metadata.get("date"):
            documents_with_dates += 1

        # Count documents with year range
        if metadata.get("year_range_start") or metadata.get("year_range_end"):
            documents_with_year_range += 1

        # Count chunks per source
        source = metadata.get("source", "UNKNOWN")
        if source not in sources_with_chunks:
            sources_with_chunks[source] = 0
        sources_with_chunks[source] += 1

    # Report metadata fields
    print("METADATA FIELDS STORED WITH EACH CHUNK:")
    print("-" * 100)
    for field in sorted(metadata_fields):
        print(f"  ✓ {field}")

    print(f"\n\nMETADATA COVERAGE:")
    print("-" * 100)
    print(f"  Total chunks: {len(documents)}")
    print(f"  Chunks with 'date' field: {documents_with_dates} ({documents_with_dates/len(documents)*100:.1f}%)")
    print(f"  Chunks with 'year_range': {documents_with_year_range} ({documents_with_year_range/len(documents)*100:.1f}%)")

    print(f"\n\nCHUNKS PER DOCUMENT:")
    print("-" * 100)
    for source in sorted(sources_with_chunks.keys()):
        chunk_count = sources_with_chunks[source]
        print(f"  {source}: {chunk_count} chunks")

    print(f"\n\nSAMPLE CHUNKS (First 3):")
    print("-" * 100)
    for i in range(min(3, len(documents))):
        print(f"\n[Chunk {i+1}]")
        print(f"  Content preview: {documents[i][:150]}...")
        print(f"  Metadata:")
        for key, value in sorted(metadatas[i].items()):
            # Truncate long values
            if isinstance(value, str) and len(value) > 80:
                value = value[:80] + "..."
            print(f"    - {key}: {value}")

    # Check for missing metadata
    print(f"\n\nMISSING METADATA ISSUES:")
    print("-" * 100)

    missing_date_chunks = []
    for i, metadata in enumerate(metadatas):
        if not metadata.get("date") or metadata.get("date") == "None":
            source = metadata.get("source", "UNKNOWN")
            missing_date_chunks.append((source, i))

    if missing_date_chunks:
        print(f"⚠️  {len(missing_date_chunks)} chunks missing 'date' metadata")
        print("   Sources affected:")
        sources_missing = {}
        for source, _ in missing_date_chunks:
            if source not in sources_missing:
                sources_missing[source] = 0
            sources_missing[source] += 1
        for source in sorted(sources_missing.keys()):
            print(f"     - {source}: {sources_missing[source]} chunks")
    else:
        print("✓ All chunks have 'date' metadata")

    print("\n" + "=" * 100)
    print("END OF REPORT")
    print("=" * 100)

if __name__ == "__main__":
    inspect_chromadb()
