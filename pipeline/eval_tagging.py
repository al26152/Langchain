"""
eval_tagging.py

TAGGING EVALUATION TOOL

PURPOSE:
  Tests and validates the auto-tagging functionality to ensure themes and
  audiences are being assigned correctly to document chunks.

USAGE:
  python eval_tagging.py

  The script will:
  1. Load sample text from documents in docs/
  2. Run auto_tag() on each sample
  3. Display themes and audiences assigned
  4. Allow manual testing of custom snippets

This helps verify tagging quality before/after running the full pipeline.
"""

import os
import sys

# Add parent directory to path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unstructured.partition.auto import partition
from unstructured.documents.elements import Title, NarrativeText, Text

from utils.utils import auto_tag


def extract_sample_text(file_path: str, max_chars: int = 1500) -> str:
    """Extract sample text from a document for tagging evaluation."""
    try:
        elements = partition(filename=file_path)
        text = ""
        for element in elements:
            if hasattr(element, "text") and isinstance(element.text, str):
                if isinstance(element, (Title, NarrativeText, Text)):
                    text += element.text + " "
                    if len(text) >= max_chars:
                        break
        return text.strip()
    except Exception as e:
        print(f"[ERROR] Could not extract text from {file_path}: {e}")
        return ""


def eval_document_samples(docs_path: str = "docs"):
    """Evaluate tagging on sample text from each document."""
    if not os.path.exists(docs_path):
        print(f"[ERROR] Document path '{docs_path}' not found.")
        return

    files = sorted([f for f in os.listdir(docs_path) if f.endswith((".md", ".txt"))])

    if not files:
        print(f"[ERROR] No documents found in {docs_path}")
        return

    print("=" * 80)
    print("AUTO-TAGGING EVALUATION")
    print("=" * 80)
    print(f"\nTesting {len(files)} document(s)...\n")

    results = []

    for i, filename in enumerate(files, 1):
        file_path = os.path.join(docs_path, filename)
        print(f"[{i}/{len(files)}] {filename}")
        print("-" * 80)

        # Extract sample
        sample_text = extract_sample_text(file_path, max_chars=1500)

        if not sample_text:
            print("[SKIP] No valid text extracted")
            print()
            continue

        # Show sample
        print(f"Sample text (first 300 chars):\n{sample_text[:300]}...\n")

        # Run auto-tag
        try:
            theme, audience = auto_tag(sample_text)
            print(f"Theme:   {theme}")
            print(f"Audience: {audience}\n")

            results.append({
                "file": filename,
                "theme": theme,
                "audience": audience,
                "sample": sample_text[:200]
            })

        except Exception as e:
            print(f"[ERROR] Tagging failed: {e}\n")

    # Summary
    print("=" * 80)
    print("TAGGING SUMMARY")
    print("=" * 80)
    print(f"\nSuccessfully tagged {len(results)} document(s):\n")

    themes = {}
    audiences = {}

    for result in results:
        print(f"File: {result['file']}")
        print(f"  Theme:   {result['theme']}")
        print(f"  Audience: {result['audience']}\n")

        # Track unique themes and audiences
        theme = result['theme']
        audience = result['audience']
        themes[theme] = themes.get(theme, 0) + 1
        audiences[audience] = audiences.get(audience, 0) + 1

    # Show statistics
    print("=" * 80)
    print("TAGGING STATISTICS")
    print("=" * 80)
    print(f"\nUnique Themes ({len(themes)}):")
    for theme, count in sorted(themes.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {theme}: {count} document(s)")

    print(f"\nUnique Audiences ({len(audiences)}):")
    for audience, count in sorted(audiences.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {audience}: {count} document(s)")

    print()


def interactive_tagging_test():
    """Allow manual testing of custom text snippets."""
    print("\n" + "=" * 80)
    print("INTERACTIVE TAGGING TEST")
    print("=" * 80)
    print("\nEnter custom text snippets to test auto-tagging.")
    print("Type 'quit' to exit.\n")

    while True:
        print("-" * 80)
        snippet = input("\nEnter text snippet to tag (or 'quit' to exit):\n> ").strip()

        if snippet.lower() == "quit":
            break

        if len(snippet) < 20:
            print("[WARN] Snippet too short (minimum 20 characters). Try again.")
            continue

        print("\nProcessing...")
        try:
            theme, audience = auto_tag(snippet)
            print(f"\nTheme:   {theme}")
            print(f"Audience: {audience}")
        except Exception as e:
            print(f"[ERROR] Tagging failed: {e}")


def main():
    """Main evaluation flow."""
    print("\nRAG SYSTEM: AUTO-TAGGING EVALUATION\n")

    # Test on document samples
    eval_document_samples(docs_path="docs")

    # Ask if user wants interactive testing
    print("=" * 80)
    response = input("\nWould you like to test custom snippets? (y/n): ").strip().lower()
    if response == "y":
        interactive_tagging_test()

    print("\n[COMPLETE] Evaluation finished.\n")


if __name__ == "__main__":
    main()
