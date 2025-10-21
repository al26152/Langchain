"""
analyze_pipeline.py

STRATEGIC ANALYSIS PIPELINE

PURPOSE:
  Loads pre-ingested documents from ChromaDB and performs multi-source
  strategic analysis. Generates comprehensive reports that synthesize
  insights across multiple documents while tracking document recency.

FEATURES:
  - Multi-source synthesis (forces answers to cite 3+ sources)
  - Document recency tracking (flags old/expiring/archival documents)
  - Source diversity metrics (shows unique documents per query)
  - Explicit source citations (with dates for context)
  - Strategic filtering (highlights aging strategies)

WORKFLOW:
  1. Loads existing ChromaDB (no ingestion needed)
  2. Builds multi-source aware QA chain
  3. Executes strategic sample queries
  4. Flags old/expiring documents in results
  5. Generates Markdown report with source citations and dates
  6. Reports source diversity metrics

RECENCY FLAGS (added to source citations):
  - RECENT: Document <1 year old
  - OLDER DOCUMENT: 1-2 years old
  - AGING: 2-4 years old
  - ARCHIVAL: >4 years old
  - STRATEGY EXPIRING: Multi-year strategy ending in <1 year
  - NO DATE: Unable to determine publication date

USAGE:
  python analyze_pipeline.py

PREREQUISITES:
  - Must run ingest_pipeline.py first to populate ChromaDB
  - Requires OpenAI API key in .env

OUTPUT:
  - strategic_analysis_output_multi_source.md: Full analysis report
  - Console display of progress

COST:
  - OpenAI GPT-4o API calls (~$5 per 1M input tokens, $15 per 1M output tokens)
"""

import sys
import os
from io import StringIO
from collections import defaultdict
from datetime import datetime, timedelta

# Add parent directory to path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate

from utils.utils import auto_tag  # Just to ensure .env is loaded

# --- CONFIGURATION ——————————————————————————————————————————————————

STORE_DIR = "chroma_db_test"

# --- MULTI-SOURCE SYNTHESIS PROMPT ———————————————————————————————————

def get_recency_flag(doc_date: str, year_range_end: str = None) -> str:
    """
    Generate recency flag based on document date.

    Args:
        doc_date: Publication date (YYYY-MM-DD format) or None
        year_range_end: End year for strategy documents or None

    Returns:
        Recency flag string (e.g., "[RECENT]", "[OLDER DOCUMENT - 2+ YEARS]")
    """
    if not doc_date:
        return "[NO DATE]"

    try:
        doc_datetime = datetime.strptime(doc_date, "%Y-%m-%d")
        today = datetime.now()
        days_old = (today - doc_datetime).days
        years_old = days_old / 365.25

        # Check if strategy is expiring soon
        if year_range_end:
            try:
                end_year = int(year_range_end)
                years_until_expiry = end_year - today.year
                if years_until_expiry <= 1 and years_until_expiry >= 0:
                    return f"[STRATEGY EXPIRES {year_range_end}]"
            except (ValueError, TypeError):
                pass

        # Recency flags
        if years_old < 1:
            return "[RECENT]"
        elif years_old < 2:
            return "[RECENT - 1 YEAR]"
        elif years_old < 4:
            return "[OLDER DOCUMENT - 2+ YEARS]"
        else:
            return "[ARCHIVAL - 4+ YEARS]"

    except (ValueError, TypeError):
        return "[DATE FORMAT ERROR]"


MULTI_SOURCE_STRATEGIC_PROMPT = """You are an AI assistant specialized in strategic analysis of health documents.

Your task is to synthesize information from MULTIPLE sources to provide comprehensive insights.

IMPORTANT INSTRUCTIONS:
1. You have received context from multiple documents and document sections below.
2. For your answer, YOU MUST explicitly cite and synthesize information from AT LEAST 3 different sources.
3. When mentioning a fact or insight, cite the EXACT filename it comes from using the format [Source: exact_filename].
4. AVAILABLE SOURCES: {available_sources}
5. Look for patterns, contradictions, and complementary perspectives across the sources.
6. Clearly separate different viewpoints or priorities from different documents.
7. If sources agree on a point, highlight this consensus. If they differ, explain the difference.

CONTEXT FROM MULTIPLE SOURCES:
{context}

QUESTION: {question}

ANSWER (Must cite at least 3 different sources by their exact filenames and synthesize across them):"""


def analyze_source_coverage(source_documents):
    """Analyze how many unique sources were retrieved."""
    source_counts = defaultdict(int)
    for doc in source_documents:
        source = doc.metadata.get("source", "Unknown")
        source_counts[source] += 1
    return source_counts


def main():
    """Main analysis pipeline."""
    # Capture output for Markdown
    original_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    print("# Strategic Analysis Pipeline - Multi-Source Enhanced\n")
    print("## Initialization\n")
    print("Starting analysis of ingested documents...\n")

    # Check ChromaDB exists
    if not os.path.exists(STORE_DIR):
        sys.stdout = original_stdout
        print(f"[ERROR] ChromaDB not found at {STORE_DIR}")
        print("Please run ingest_pipeline.py first to ingest documents.")
        return

    # Initialize embeddings and load ChromaDB
    print("## Loading Vector Store\n")
    embeddings = OpenAIEmbeddings()
    print("[OK] Initialized OpenAI Embeddings client.\n")

    vectordb = Chroma(persist_directory=STORE_DIR, embedding_function=embeddings)
    print("[OK] ChromaDB loaded.\n")

    # Check if database has content
    try:
        all_db_data = vectordb._collection.get(include=["metadatas"])
        total_chunks = len(all_db_data.get("metadatas", []))
        if total_chunks == 0:
            sys.stdout = original_stdout
            print("[ERROR] ChromaDB is empty. No documents to analyze.")
            print("Please run ingest_pipeline.py first.")
            return
        print(f"Found **{total_chunks}** chunks in ChromaDB.\n")
    except Exception as e:
        sys.stdout = original_stdout
        print(f"[ERROR] Could not access ChromaDB: {e}")
        return

    # Initialize QA LLM
    print("## Building Multi-Source Strategic QA Chain\n")
    print("Using MULTI-SOURCE aware prompt to force synthesis across documents.\n")
    print("Each query will list available sources and enforce explicit citation.\n")

    print("## Executing Sample Strategic Queries\n")
    sample_queries = [
        "Q01 - Summarise the 10 year plan",
        "Q02 - Pick out the key focus areas for Leeds Community Healthcare based on the 10 year plan, Leeds Health and Wellbeing Strategy 2023, and Neighbourhood health guides",
        "Q03 - With the 10 year plan in mind, what are the top 10 documents needed to write a Leeds Community Healthcare workforce strategy for 5 years?",
        "Q04 - The strategy may cover Leadership, People Services, Inclusion, Talent, Staff Experience and Organisational Design - are there any missing focus areas?",
        "Q05 - What are the current staffing turnover rates, joiner/leaver patterns and headcount trends for Leeds Community Healthcare?"
    ]

    for i, query in enumerate(sample_queries):
        query_num = query.split(" - ")[0]
        query_text = query.split(" - ", 1)[1]
        print(f"\n### {query_num}: {query_text}\n")

        # Retrieve documents manually to get source list (increased from k=13 to k=20 for better coverage)
        retriever = vectordb.as_retriever(search_kwargs={"k": 20})
        retrieved_docs = retriever.invoke(query_text)  # Use query_text without the Q01 prefix

        # Extract unique source filenames
        unique_sources = []
        seen = set()
        for doc in retrieved_docs:
            src = doc.metadata.get("source", "Unknown")
            if src not in seen:
                unique_sources.append(src)
                seen.add(src)

        # Format source list for prompt
        available_sources_str = ", ".join(unique_sources)

        # Create context from retrieved docs
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # Use the LLM directly with formatted prompt
        prompt = PromptTemplate.from_template(MULTI_SOURCE_STRATEGIC_PROMPT)
        formatted_prompt = prompt.format(
            context=context,
            question=query,
            available_sources=available_sources_str
        )

        # Get answer from LLM
        qa_llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
        answer = qa_llm.predict(formatted_prompt)

        print(f"**Answer:**\n{answer}\n")

        # Analyze source diversity
        sources_used = analyze_source_coverage(retrieved_docs)
        unique_sources_count = len(sources_used)
        print(f"**Source Summary:** {unique_sources_count} unique document(s) referenced\n")

        # Show all retrieved chunks with date flags and chunk type
        print("**All Retrieved Chunks:**")
        for j, doc in enumerate(retrieved_docs):
            src = doc.metadata.get("source", "N/A")
            theme = doc.metadata.get("theme", "N/A")
            elem = doc.metadata.get("element_type", "N/A")
            chunk_type = doc.metadata.get("chunk_type", "unknown")
            content_category = doc.metadata.get("content_category", "")
            doc_date = doc.metadata.get("date")
            year_range_end = doc.metadata.get("year_range_end")

            # Get recency flag
            flag = get_recency_flag(doc_date, year_range_end)

            # Display source with date and flag
            print(f"- {j+1}. `{src}` {flag}")
            if doc_date:
                print(f"    Published: {doc_date} | Theme: {theme}")
            else:
                print(f"    Theme: {theme}")

            # Show chunk type and content category
            chunk_info = f"Chunk Type: {chunk_type}"
            if content_category:
                chunk_info += f" | Category: {content_category}"
            print(f"    {chunk_info}")
            print(f"    Snippet: {doc.page_content[:200].replace(chr(10), ' ')}...\n")

    print("---\n[COMPLETE] Multi-source strategic analysis complete.\n")

    # Save Markdown output
    sys.stdout = original_stdout
    md_output_path = "strategic_analysis_output_multi_source.md"
    with open(md_output_path, "w", encoding="utf-8") as md_file:
        md_file.write(captured_output.getvalue())

    print(f"\nANALYSIS REPORT SAVED: {md_output_path}")
    print("\nYou can now:")
    print("- Review the full analysis report in strategic_analysis_output_multi_source.md")
    print("- Run interactive_query_multi_source.py for ad-hoc queries")
    print("- Re-run this pipeline with different sample queries as needed")


if __name__ == "__main__":
    main()
