"""
test_hub_analysis.py

Test script for hub-based multi-agent analysis.
Compares hub-enabled vs traditional pipeline approach.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from analysis.multi_agent.orchestrator import Orchestrator


def main():
    """Run hub-based analysis test."""

    # Test question
    query = (
        "What are the key workforce integration challenges between LTHT and LCH, "
        "and how should they be addressed within the integrated care agenda?"
    )

    print("\n" + "="*80)
    print("MULTI-AGENT HUB-BASED ANALYSIS TEST")
    print("="*80)
    print(f"\nTest Query:\n{query}\n")

    try:
        # Initialize vector store
        print("[1/4] Initializing vector store...")
        embeddings = OpenAIEmbeddings()
        vectordb = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
        print("[OK] Vector store loaded")

        # Initialize orchestrator with hub
        print("\n[2/4] Initializing orchestrator with AgentHub...")
        orchestrator = Orchestrator(vectordb, use_hub=True, verbose=True)
        print("[OK] Orchestrator initialized")

        # Run hub-based analysis
        print("\n[3/4] Running hub-based analysis...")
        print("="*80)
        result_hub = orchestrator.run_analysis_with_hub(query)
        print("="*80)
        print("[OK] Analysis complete")

        # Display results
        print("\n" + "="*80)
        print("HUB-BASED ANALYSIS RESULTS")
        print("="*80)

        print(f"\n[CONFIDENCE & QUALITY]")
        print(f"  Confidence Score: {result_hub['confidence_score']:.1f}%")
        print(f"  Quality Rating: {result_hub['quality_rating']}")
        print(f"  Iterations: {result_hub['iterations']}")

        print(f"\n[EVIDENCE]")
        print(f"  Unique Sources: {result_hub['unique_sources']}")
        print(f"  Total Chunks: {result_hub['total_chunks']}")

        print(f"\n[HUB COMMUNICATIONS]")
        hub_summary = result_hub['hub_summary']
        print(f"  Total Messages: {hub_summary['total_messages']}")
        print(f"  Successful Messages: {hub_summary['successful_messages']}")
        print(f"  Agents Communicating: {hub_summary['unique_agents']}")
        print(f"  Message Types: {hub_summary['message_types']}")
        print(f"  Actions Used: {hub_summary['actions_used']}")

        print(f"\n[EPISTEMIC SUMMARY]")
        epistemic = result_hub['epistemic_summary']
        print(f"  Facts: {epistemic.get('fact_percentage', 'N/A')}")
        print(f"  Inferences: {epistemic.get('inference_percentage', 'N/A')}")
        print(f"  Assumptions: {epistemic.get('assumption_percentage', 'N/A')}")

        print(f"\n[ANSWER PREVIEW]")
        answer = result_hub['answer']
        preview = answer[:300] + "..." if len(answer) > 300 else answer
        print(f"{preview}")

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"analysis_report_hub_{timestamp}.md"
        orchestrator.save_report(result_hub, report_path)
        print(f"\n[REPORT] Full report saved: {report_path}")

        # Show hub communication details
        print(f"\n" + "="*80)
        print("HUB COMMUNICATION LOG")
        print("="*80)
        comm_log = result_hub['hub_communications']
        if comm_log:
            print(f"\nTotal communications logged: {len(comm_log)}")
            print("\nDetailed log (first 5):")
            for i, msg in enumerate(comm_log[:5], 1):
                print(f"\n[{i}] {msg['message_type']} - {msg['action']}")
                print(f"    From: {msg['from_agent']} -> To: {msg['to_agent']}")
                print(f"    Status: {msg['status']}")
        else:
            print("No communications logged (hub may not have been used)")

        # Run comparison test (traditional pipeline)
        print(f"\n" + "="*80)
        print("COMPARISON: TRADITIONAL PIPELINE (NO HUB)")
        print("="*80)

        orchestrator_no_hub = Orchestrator(vectordb, use_hub=False, verbose=False)
        print("\nRunning traditional pipeline analysis...")
        result_pipeline = orchestrator_no_hub.run_analysis(query)

        print(f"\n[TRADITIONAL PIPELINE RESULTS]")
        print(f"  Confidence Score: {result_pipeline['confidence_score']:.1f}%")
        print(f"  Quality Rating: {result_pipeline['quality_rating']}")
        print(f"  Iterations: {result_pipeline['iterations']}")
        print(f"  Unique Sources: {result_pipeline['unique_sources']}")

        # Comparison
        print(f"\n" + "="*80)
        print("COMPARISON: HUB vs PIPELINE")
        print("="*80)

        conf_diff = result_hub['confidence_score'] - result_pipeline['confidence_score']
        sources_diff = result_hub['unique_sources'] - result_pipeline['unique_sources']
        iterations_diff = result_hub['iterations'] - result_pipeline['iterations']

        print(f"\nConfidence Score:")
        print(f"  Hub:      {result_hub['confidence_score']:.1f}%")
        print(f"  Pipeline: {result_pipeline['confidence_score']:.1f}%")
        status = "[IMPROVED]" if conf_diff > 0 else "[DECREASED]" if conf_diff < 0 else "[SAME]"
        print(f"  Diff:     {conf_diff:+.1f}% {status}")

        print(f"\nUnique Sources:")
        print(f"  Hub:      {result_hub['unique_sources']}")
        print(f"  Pipeline: {result_pipeline['unique_sources']}")
        status = "[MORE]" if sources_diff > 0 else "[FEWER]" if sources_diff < 0 else "[SAME]"
        print(f"  Diff:     {sources_diff:+d} {status}")

        print(f"\nIterations:")
        print(f"  Hub:      {result_hub['iterations']}")
        print(f"  Pipeline: {result_pipeline['iterations']}")
        print(f"  Diff:     {iterations_diff:+d}")

        print(f"\nQuality Ratings:")
        print(f"  Hub:      {result_hub['quality_rating']}")
        print(f"  Pipeline: {result_pipeline['quality_rating']}")

        # Summary
        print(f"\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"\n[SUCCESS] Hub-based analysis executed successfully")
        print(f"[HUB] {hub_summary['total_messages']} agent communications processed")
        print(f"[IMPACT] Confidence {'improved' if conf_diff > 0 else 'changed'} by {abs(conf_diff):.1f}%")
        print(f"[SOURCES] {sources_diff:+d} additional sources {'accessed' if sources_diff > 0 else 'used'}")
        print(f"\n[DONE] Test completed at {datetime.now().strftime('%H:%M:%S')}")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
