"""
enhance_table_context.py

TABLE CONTEXT ENHANCEMENT SCRIPT

PURPOSE:
  Pre-processes markdown documents to add semantic context to tables.
  Detects table patterns and injects descriptive headers that help
  semantic search understand what the tables contain.

FEATURES:
  - Detects markdown tables and extracts column headers
  - Generates context descriptions based on table content
  - Adds synthetic context above tables for better semantic matching
  - Preserves original table data structure
  - Works on files before ingestion pipeline

LOGIC:
  1. Scans markdown for table patterns (| ... |)
  2. Extracts table headers and first few rows
  3. Generates contextual description based on content
  4. Inserts context above table
  5. Overwrites file with enhanced version

TABLE TYPE DETECTION:
  - Staff Survey tables → "Staff survey results by [breakdown type]"
  - Benchmark tables → "Benchmark comparison for [metric]"
  - Score tables → "Performance scores (0-10 scale) for [subject]"
  - Historical tables → "Historical comparison [year range]"

USAGE:
  python enhance_table_context.py

OUTPUT:
  - Enhanced markdown files in docs/ (overwrites originals)
  - Console report of enhancements made
"""

import os
import re
from typing import List, Tuple

# Configuration
DOCS_PATH = "docs"
TABLE_DETECTION_THRESHOLD = 3  # Min pipes per line to be considered a table


def detect_tables(content: str) -> List[Tuple[int, int, List[str]]]:
    """
    Detect tables in markdown content.

    Returns:
        List of (start_line, end_line, headers) tuples
    """
    lines = content.split('\n')
    tables = []
    in_table = False
    table_start = 0
    headers = []

    for i, line in enumerate(lines):
        pipe_count = line.count('|')

        if pipe_count >= TABLE_DETECTION_THRESHOLD and '|' in line:
            if not in_table:
                # Start of new table
                in_table = True
                table_start = i
                # Extract headers from first row
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                headers = cells

            else:
                # Continue table
                pass
        else:
            if in_table:
                # End of table
                tables.append((table_start, i - 1, headers))
                in_table = False
                headers = []

    # Handle table at end of file
    if in_table:
        tables.append((table_start, len(lines) - 1, headers))

    return tables


def generate_table_context(headers: List[str], first_row_cells: List[str], section_above: str) -> str:
    """
    Generate a contextual description for a table.

    Args:
        headers: Column headers from table
        first_row_cells: First data row (for pattern recognition)
        section_above: Previous section heading or text

    Returns:
        Contextual description string
    """
    # Identify table type based on headers and context
    headers_lower = [h.lower() for h in headers]
    section_lower = section_above.lower()

    context = "**Table Data:** "

    # Detect staff survey tables
    if any(keyword in section_lower for keyword in ["business unit", "staff group", "breakdown"]):
        if any(keyword in headers_lower for keyword in ["morale", "engagement", "compassionate", "rewarded", "voice"]):
            context += "Staff survey results showing People Promise element and theme scores (0-10 scale) "
            if "business" in section_lower:
                context += "by business unit. "
            elif "staff group" in section_lower:
                context += "by staff group. "
            else:
                context += "across breakdown areas. "
            context += f"Metrics include: {', '.join(headers[1:5])} and others. "

    # Detect benchmark comparison tables
    elif any(keyword in section_lower for keyword in ["benchmark", "comparison", "best result"]):
        if "2024" in section_lower or "2023" in section_lower:
            context += "Benchmark comparison showing organizational performance versus peer group performance (best, average, worst) on 0-10 scale. "
        else:
            context += "Benchmark comparison metrics comparing organizational results to benchmarked peer group. "

    # Detect score/performance tables
    elif any(keyword in headers_lower for keyword in ["score", "results", "compassionate", "engagement", "morale"]):
        context += "Performance scores (0-10 scale) for staff engagement and wellbeing metrics. "
        if "responses" in headers_lower:
            context += "Includes response counts for statistical confidence. "

    # Detect historical tables
    elif "2023" in str(first_row_cells) and "2024" in str(first_row_cells):
        context += "Historical comparison showing changes in scores between 2023 and 2024 survey cycles. "
        if "significant" in section_lower:
            context += "Includes statistical significance testing of score changes. "

    # Default context
    else:
        col_summary = ", ".join(headers[1:min(6, len(headers))])
        context += f"Data table with columns: {col_summary}. "

    context += "This table provides detailed metrics for analysis and benchmarking."

    return context


def enhance_file_tables(filepath: str) -> int:
    """
    Enhance a markdown file by adding context to tables.

    Returns:
        Number of tables enhanced
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()

        lines = original_content.split('\n')
        tables = detect_tables(original_content)

        if not tables:
            return 0

        # Process tables in reverse order to maintain line numbers
        enhanced_lines = lines.copy()
        enhancements_made = 0

        for table_start, table_end, headers in reversed(tables):
            # Skip if context already exists (check previous 2 lines)
            if table_start > 0:
                prev_text = '\n'.join(lines[max(0, table_start-2):table_start]).lower()
                if "table data:" in prev_text or "staff survey" in prev_text:
                    continue

            # Get section context from previous heading
            section_above = ""
            for i in range(table_start - 1, max(0, table_start - 20), -1):
                if lines[i].startswith("#"):
                    section_above = lines[i]
                    break

            # Get first data row for pattern recognition
            first_row_cells = []
            for i in range(table_start + 1, min(table_end + 1, table_start + 3)):
                if '|' in lines[i] and not lines[i].startswith('|'):
                    continue
                if '---' not in lines[i]:
                    cells = [cell.strip() for cell in lines[i].split('|')[1:-1]]
                    if cells and len(cells) > 1:
                        first_row_cells = cells
                        break

            # Generate context
            context = generate_table_context(headers, first_row_cells, section_above)

            # Insert context before table with blank line
            enhanced_lines.insert(table_start, "")
            enhanced_lines.insert(table_start, context)
            enhancements_made += 1

        # Write back to file
        enhanced_content = '\n'.join(enhanced_lines)

        # Only write if changed
        if enhanced_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)

        return enhancements_made

    except Exception as e:
        print(f"[ERROR] Error processing {filepath}: {e}")
        return 0


def main():
    """Main enhancement pipeline."""
    print("# Table Context Enhancement Script\n")
    print("## Scanning Documents\n")

    if not os.path.exists(DOCS_PATH):
        print(f"[ERROR] Docs path '{DOCS_PATH}' not found.")
        return

    markdown_files = [f for f in os.listdir(DOCS_PATH) if f.endswith('.md')]
    print(f"Found {len(markdown_files)} markdown file(s).\n")

    total_enhancements = 0

    print("## Processing Files\n")
    for filename in sorted(markdown_files):
        filepath = os.path.join(DOCS_PATH, filename)
        enhancements = enhance_file_tables(filepath)

        if enhancements > 0:
            print(f"[OK] {filename}")
            print(f"  Enhanced {enhancements} table(s) with context headers\n")
            total_enhancements += enhancements
        else:
            print(f"[--] {filename}")
            print(f"  No tables requiring enhancement\n")

    print("---\n")
    print(f"[COMPLETE] Enhancement complete.\n")
    print(f"Total table enhancements: {total_enhancements}\n")
    print("Next step: Run ingest_pipeline.py to re-ingest enhanced documents")


if __name__ == "__main__":
    main()
