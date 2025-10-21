"""
clean_doc.py

PURPOSE:
  This utility module cleans up filenames in the docs/ directory by replacing
  special characters with underscores. Specifically, it replaces the "»" character
  (right-pointing guillemet/arrow) with an underscore "_".

WHY THIS MATTERS:
  - Some markdown files are downloaded with special characters in their filenames
  - These special characters can cause issues with file path handling and
    document ingestion in the RAG pipeline
  - This module normalizes filenames to be filesystem and tool-friendly

USAGE:
  As a function (called from other scripts):
    from clean_doc import clean_docs
    renamed_files = clean_docs(docs_path="docs", verbose=True)

  As a standalone script:
    python clean_doc.py

SAFE TO RUN:
  - Only renames files, doesn't delete anything
  - Reports all changes made
  - Safe to run multiple times (only renames files that still have »)
"""

import os


def clean_docs(docs_path="docs", verbose=True):
    """
    Clean filenames in docs directory by replacing special characters.

    Args:
        docs_path (str): Path to the docs directory. Default: "docs"
        verbose (bool): Print results to console. Default: True

    Returns:
        list: List of tuples (old_name, new_name) for renamed files

    Example:
        renamed = clean_docs()
        if renamed:
            print(f"Renamed {len(renamed)} files")
    """
    if not os.path.exists(docs_path):
        if verbose:
            print(f"[INFO] Docs directory '{docs_path}' does not exist. Skipping cleanup.")
        return []

    files = os.listdir(docs_path)
    renamed = []

    # Scan through all files in docs/ directory
    for filename in files:
        # Check if filename contains the problematic "»" character
        if "»" in filename:
            # Create new filename with "»" replaced by "_"
            new_name = filename.replace("»", "_")
            # Rename the file on disk
            old_path = os.path.join(docs_path, filename)
            new_path = os.path.join(docs_path, new_name)
            os.rename(old_path, new_path)
            # Track this rename for reporting
            renamed.append((filename, new_name))

    # Print results if verbose
    if verbose:
        if renamed:
            print(f"\n[CLEANUP] Renamed {len(renamed)} file(s):")
            for old, new in renamed:
                print(f"  {old} -> {new}")
        else:
            print(f"[CLEANUP] No files needed renaming in '{docs_path}'")

    return renamed


# Allow running as standalone script
if __name__ == "__main__":
    clean_docs(docs_path="docs", verbose=True)