"""
run_multi_agent.py

MULTI-AGENT ITERATIVE RAG - INTERACTIVE INTERFACE

PURPOSE:
  Interactive interface for running multi-agent iterative RAG analysis.
  Allows users to ask strategic questions and receive comprehensive
  reports with evidence coverage validation and epistemic categorization.

USAGE:
  python analysis/multi_agent/run_multi_agent.py

  Or for single question:
  python analysis/multi_agent/run_multi_agent.py --question "Your question here"

FEATURES:
  - Interactive query mode
  - Automatic report generation
  - Real-time progress logging
  - Epistemic categorization (FACT/ASSUMPTION/INFERENCE)
  - Confidence scoring
  - Gap detection and iteration

REQUIREMENTS:
  - ChromaDB must be populated (run ingest_pipeline.py first)
  - OpenAI API key in .env
"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from utils.utils import auto_tag  # Load .env

# Import orchestrator - handle both package and direct execution
try:
    from analysis.multi_agent.orchestrator import Orchestrator
except ImportError:
    from orchestrator import Orchestrator


def main():
    """Main entry point."""

    # Parse arguments
    parser = argparse.ArgumentParser(description="Multi-Agent Iterative RAG Analysis")
    parser.add_argument(
        "--question",
        type=str,
        help="Question to analyze (skip interactive mode)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: auto-generated)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum iterations (default: 5)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="LLM model to use (default: gpt-4o)",
    )

    args = parser.parse_args()

    # Initialize ChromaDB
    print("="*80)
    print("MULTI-AGENT ITERATIVE RAG SYSTEM")
    print("="*80)
    print("\nInitializing system...\n")

    STORE_DIR = "chroma_db_test"

    if not os.path.exists(STORE_DIR):
        print(f"❌ Error: ChromaDB not found at {STORE_DIR}")
        print("   Please run ingest_pipeline.py first to populate the database.")
        print("\n   Command: python pipeline/ingest_pipeline.py\n")
        sys.exit(1)

    print("Loading ChromaDB...")
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=STORE_DIR, embedding_function=embeddings)
    print("[OK] ChromaDB loaded\n")

    # Initialize LLM
    llm = ChatOpenAI(model=args.model, temperature=0.5)

    # Initialize orchestrator
    orchestrator = Orchestrator(
        vectordb=vectordb,
        llm=llm,
        max_iterations=args.max_iterations,
        verbose=True,
    )

    print("[OK] Multi-agent system ready\n")
    print("="*80)
    print("SYSTEM FEATURES")
    print("="*80)
    print("""
This system provides:
  [OK] Iterative evidence gathering (auto-expands search based on gaps)
  [OK] Real-time gap detection and reporting
  [OK] Epistemic categorization (FACT / ASSUMPTION / INFERENCE)
  [OK] Source traceability (every claim cited)
  [OK] Confidence scoring (0-100%)
  [OK] Convergence detection (stops when evidence is sufficient)

Average analysis time: 2-4 minutes (3-5 iterations)
Average cost: $0.15-0.40 per question
    """)

    # Single question mode
    if args.question:
        print("="*80)
        print("SINGLE QUESTION MODE")
        print("="*80)
        print(f"\nQuestion: {args.question}\n")

        result = orchestrator.run_analysis(args.question)
        output_path = orchestrator.save_report(result, args.output)

        print(f"\n[OK] Analysis complete!")
        print(f"   Report: {output_path}")
        print(f"   Confidence: {result['confidence_score']:.0f}%")
        print(f"   Quality: {result['quality_rating']}")

        return

    # Interactive mode
    print("="*80)
    print("INTERACTIVE MODE")
    print("="*80)
    print("\nEnter your strategic questions below.")
    print("Type 'exit' or 'quit' to end session.\n")

    while True:
        try:
            user_query = input("\n🔍 Your Question: ").strip()

            if user_query.lower() in ["exit", "quit", "q"]:
                print("\nExiting. Goodbye!")
                break

            if not user_query:
                print("[WARN] Please enter a question.")
                continue

            # Run analysis
            result = orchestrator.run_analysis(user_query)

            # Save report
            output_path = orchestrator.save_report(result)

            # Display summary
            print("\n" + "="*80)
            print("QUICK SUMMARY")
            print("="*80)
            print(f"\nConfidence: {result['confidence_score']:.0f}% ({result['quality_rating']})")
            print(f"Sources: {result['unique_sources']} documents")
            print(f"Evidence: {result['total_chunks']} chunks")
            print(f"Iterations: {result['iterations']}")
            print(f"\nFull report saved: {output_path}")

            # Show answer preview
            print("\n" + "-"*80)
            print("ANSWER PREVIEW (first 500 chars):")
            print("-"*80)
            print(result['answer'][:500] + "...")
            print("\n(See full report in markdown file)")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different question.\n")
            continue


if __name__ == "__main__":
    main()
