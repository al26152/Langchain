"""
eval_dates.py

DATE EXTRACTION EVALUATION TOOL

PURPOSE:
  Evaluates date extraction logic across all documents to identify:
  - What dates can be automatically extracted
  - Which documents need manual date entry
  - Patterns for different document types (strategies, reports, plans)

  Generates document_dates.json with all date decisions for fallback
  during ingestion.

USAGE:
  python eval_dates.py

OUTPUT:
  - Console report showing extracted/manual dates
  - document_dates.json: Config file for ingest_pipeline.py to use

DATE TYPES SUPPORTED:
  - Published dates: "Date published: 2024-12-03"
  - Updated dates: "last updated: 2025-03-01"
  - Start-End dates: "2021-25" (from filename or content)
  - Fiscal year: "2425" = 2024-2025
  - Reporting year: "2023-2024"
"""

import os
import re
import json
from datetime import datetime
from typing import Tuple, Optional, Dict, List
from unstructured.partition.auto import partition
from unstructured.documents.elements import Text, NarrativeText


class DateExtractor:
    """Extract various date formats from documents."""

    # Regex patterns for different date formats
    PATTERNS = {
        "iso_date": r"(\d{4}-\d{1,2}-\d{1,2})",  # YYYY-MM-DD
        "published": r"[Dd]ate\s+(?:published|Published):\s*(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4})",
        "published_iso": r"[Dd]ate\s+(?:published|Published):\s*(\d{4}-\d{1,2}-\d{1,2})",
        "updated": r"[Dd]ate\s+(?:last\s+)?(?:updated|Updated):\s*(\d{4}-\d{1,2}-\d{1,2})",
        "fiscal_year": r"(?:Fiscal\s+)?[Yy]ear\s+(?:20)?(\d{2})[/-](?:20)?(\d{2})",  # YY/YY or YYYY/YYYY
        "year_range": r"(\d{4})[/-](\d{2})",  # 2024-25 or 2024/25
        "single_year": r"(?:^|[^\d])(\d{4})(?:[^\d]|$)",  # Standalone year
    }

    @staticmethod
    def extract_published_date(text: str) -> Optional[str]:
        """Extract published date in ISO format."""
        # Try ISO format first
        match = re.search(DateExtractor.PATTERNS["published_iso"], text)
        if match:
            return match.group(1)

        # Try text format (e.g., "3 December, 2024")
        match = re.search(DateExtractor.PATTERNS["published"], text)
        if match:
            try:
                date_str = match.group(1)
                parsed = datetime.strptime(date_str, "%d %B, %Y")
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                pass

        return None

    @staticmethod
    def extract_updated_date(text: str) -> Optional[str]:
        """Extract last updated date."""
        match = re.search(DateExtractor.PATTERNS["updated"], text)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def extract_year_range(text: str, filename: str) -> Optional[Tuple[str, str]]:
        """
        Extract start and end years (e.g., 2021-25 or 2024/25).
        Returns (start_year, end_year) or None.
        """
        # Check filename first (e.g., "Workforce-Strategy-2021-25-V1.0.md")
        match = re.search(DateExtractor.PATTERNS["year_range"], filename)
        if match:
            start = match.group(1)
            end = match.group(2)
            # Handle 2-digit years
            if len(end) == 2:
                end = "20" + end
            return (start, end)

        # Check content
        match = re.search(DateExtractor.PATTERNS["fiscal_year"], text)
        if match:
            start_yy = match.group(1)
            end_yy = match.group(2)
            # Convert YY to YYYY
            start = "20" + start_yy if len(start_yy) == 2 else start_yy
            end = "20" + end_yy if len(end_yy) == 2 else end_yy
            return (start, end)

        return None

    @staticmethod
    def extract_all_years(text: str) -> List[str]:
        """Extract all 4-digit years found in text."""
        matches = re.findall(r"\d{4}", text)
        # Filter to reasonable years (1990-2030)
        years = [m for m in matches if 1990 <= int(m) <= 2030]
        return sorted(set(years), reverse=True)


def extract_sample_text(file_path: str, max_chars: int = 2000) -> str:
    """Extract sample text from document."""
    try:
        elements = partition(filename=file_path)
        text = ""
        for element in elements:
            if hasattr(element, "text") and isinstance(element.text, str):
                if isinstance(element, (Text, NarrativeText)):
                    text += element.text + " "
                    if len(text) >= max_chars:
                        break
        return text.strip()
    except Exception as e:
        print(f"  [ERROR] Could not extract text: {e}")
        return ""


def evaluate_document_dates(docs_path: str = "docs", interactive: bool = False) -> Dict:
    """Evaluate date extraction for all documents."""
    if not os.path.exists(docs_path):
        print(f"[ERROR] Document path '{docs_path}' not found.")
        return {}

    files = sorted([f for f in os.listdir(docs_path) if f.endswith((".md", ".txt"))])

    if not files:
        print(f"[ERROR] No documents found in {docs_path}")
        return {}

    print("=" * 90)
    print("DATE EXTRACTION EVALUATION")
    print("=" * 90)
    print(f"\nTesting {len(files)} document(s) for date extraction...\n")

    results = {}

    for i, filename in enumerate(files, 1):
        file_path = os.path.join(docs_path, filename)
        print(f"[{i}/{len(files)}] {filename}")
        print("-" * 90)

        # Extract sample text
        sample_text = extract_sample_text(file_path, max_chars=2000)

        if not sample_text:
            print("  [SKIP] No valid text extracted")
            print()
            continue

        # Try date extraction
        extractor = DateExtractor()
        published = extractor.extract_published_date(sample_text)
        updated = extractor.extract_updated_date(sample_text)
        year_range = extractor.extract_year_range(sample_text, filename)
        all_years = extractor.extract_all_years(sample_text + " " + filename)

        # Display findings
        print("  Extraction Results:")
        if published:
            print(f"    Published:  {published} [AUTO]")
        if updated:
            print(f"    Updated:    {updated} [AUTO]")
        if year_range:
            print(f"    Year Range: {year_range[0]}-{year_range[1]} [AUTO]")
        if all_years and not published and not updated and not year_range:
            print(f"    Years found in text: {', '.join(all_years[:3])}")
        if not published and not updated and not year_range and not all_years:
            print("    No dates found automatically")

        # Determine primary date
        primary_date = published or updated

        # Store result
        doc_result = {
            "published": published,
            "updated": updated,
            "year_range": year_range,
            "all_years_found": all_years,
            "primary_date": primary_date,
        }

        results[filename] = doc_result

        # Ask for manual override/confirmation (only in interactive mode)
        print()
        if interactive:
            if primary_date:
                response = input(f"  Use {primary_date}? (y/n/other): ").strip()
                if response.lower() == "n":
                    manual = input(f"  Enter date (YYYY-MM-DD) or skip: ").strip()
                    if manual:
                        results[filename]["primary_date"] = manual
                        print(f"  Set to: {manual}")
                elif response.lower() not in ("y", ""):
                    results[filename]["primary_date"] = response
                    print(f"  Set to: {response}")
            else:
                manual = input(f"  Enter date manually (YYYY-MM-DD) or skip: ").strip()
                if manual:
                    results[filename]["primary_date"] = manual
                    print(f"  Set to: {manual}")

        print()

    return results


def generate_config(results: Dict, output_file: str = "document_dates.json"):
    """Generate document_dates.json config file."""
    print("=" * 90)
    print("GENERATING CONFIG FILE")
    print("=" * 90)

    # Create clean config with only primary dates
    config = {}
    for filename, data in results.items():
        if data.get("primary_date"):
            config[filename] = {
                "date": data["primary_date"],
                "source": "auto" if data.get("published") or data.get("updated") else "manual",
                "year_range": data.get("year_range")
            }

    # Write to JSON
    with open(output_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\nConfig saved to: {output_file}")
    print(f"Total documents with dates: {len(config)}/{len(results)}")

    # Display summary
    print("\n" + "=" * 90)
    print("DATE SUMMARY")
    print("=" * 90)
    print("\nDocuments with dates:\n")
    for filename in sorted(config.keys()):
        data = config[filename]
        source = data["source"]
        date_val = data["date"]
        year_range = f" (Strategy {data['year_range'][0]}-{data['year_range'][1]})" if data.get("year_range") else ""
        print(f"  {filename}")
        print(f"    Date: {date_val} ({source}){year_range}")

    print()

    return config


def main():
    """Main evaluation flow."""
    print("\n" + "=" * 90)
    print("RAG SYSTEM: DATE EXTRACTION EVALUATION")
    print("=" * 90)
    print("\nThis tool evaluates date extraction across all documents.")
    print("Run with --interactive flag for manual confirmation mode.\n")

    # Check for interactive mode
    import sys
    interactive = "--interactive" in sys.argv

    # Evaluate documents
    results = evaluate_document_dates(docs_path="docs", interactive=interactive)

    if not results:
        print("[ERROR] No documents evaluated.")
        return

    # Generate config
    config = generate_config(results)

    print("\n" + "=" * 90)
    print("NEXT STEPS")
    print("=" * 90)
    print("\n1. Review document_dates.json")
    print("2. Update ingest_pipeline.py to use dates")
    print("3. Update analyze_pipeline.py to flag old/expiring docs")
    print("4. Run: python ingest_pipeline.py\n")


if __name__ == "__main__":
    main()
