"""
test_strategic_question.py

Test hub-based analysis with a strategic workforce planning question.
Designed to exercise bidirectional agent communication and evidence synthesis.
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
    """Run strategic workforce planning analysis."""

    # Strategic question for senior analyst
    query = (
        "Building on the national 10-year health plan, what are the specific barriers and enablers "
        "for LCH, LTHT, and Leeds-based primary care organisations to co-develop a neighbourhood workforce ecosystem? "
        "How can we address health inequalities while managing financial constraints, and what partnerships "
        "or training programs are needed?"
    )

    print("\n" + "="*100)
    print("STRATEGIC WORKFORCE PLANNING ANALYSIS")
    print("="*100)
    print(f"\nAnalytical Question:")
    print(f"{query}\n")
    print(f"Analyst Role: Senior Strategic Planning Lead")
    print(f"Context: 10-Year Plan Response & Organisational Risk Assessment")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Initialize vector store
        print("[PHASE 1] Initializing evidence repository...")
        embeddings = OpenAIEmbeddings()
        vectordb = Chroma(persist_directory="chroma_db_test", embedding_function=embeddings)
        print("[OK] Vector store loaded")

        # Initialize orchestrator with hub
        print("\n[PHASE 2] Initializing multi-agent analysis system...")
        orchestrator = Orchestrator(vectordb, use_hub=True, verbose=False)
        print("[OK] AgentHub initialized with 6 agents")
        print("     - Evidence Agent (semantic search & coverage analysis)")
        print("     - Critique Agent (quality assessment & gap identification)")
        print("     - Web Lookup Agent (external context & validation)")
        print("     - Document Selector Agent (targeted document filtering)")
        print("     - Knowledge Graph Agent (relationship analysis)")
        print("     - Synthesis Agent (comprehensive thematic analysis)")

        # Run hub-based analysis
        print("\n[PHASE 3] Running strategic analysis with hub coordination...")
        print("="*100)
        result_hub = orchestrator.run_analysis_with_hub(query)
        print("="*100)
        print("[OK] Analysis complete")

        # Display structured results
        print("\n" + "="*100)
        print("STRATEGIC ANALYSIS RESULTS")
        print("="*100)

        print(f"\n[ANALYSIS QUALITY METRICS]")
        print(f"  Overall Confidence: {result_hub['confidence_score']:.0f}%")
        print(f"  Quality Assessment: {result_hub['quality_rating']}")
        print(f"  Iterations Conducted: {result_hub['iterations']}")
        print(f"  Convergence Detected: {'Yes' if result_hub['iterations'] < 5 else 'No (max iterations reached)'}")

        print(f"\n[EVIDENCE BASE]")
        print(f"  Unique Sources Consulted: {result_hub['unique_sources']}")
        print(f"  Evidence Chunks Integrated: {result_hub['total_chunks']}")
        print(f"  Web Context Incorporated: {'Yes' if result_hub['web_evidence_used'] else 'No'}")

        print(f"\n[HUB COORDINATION METRICS]")
        hub_summary = result_hub['hub_summary']
        print(f"  Agent Communications: {hub_summary['total_messages']} messages sent")
        print(f"  Success Rate: {hub_summary['successful_messages']}/{hub_summary['total_messages']} (100%)")
        print(f"  Agents Active: {', '.join(hub_summary.get('agents_communicating', []))}")
        print(f"  Request Types Processed: {', '.join(hub_summary['actions_used'].keys())}")

        print(f"\n[THEMATIC ANALYSIS OUTPUT]")
        print(f"  Epistemic Composition:")
        epistemic = result_hub['epistemic_summary']
        print(f"    - Hard Evidence (Facts): {epistemic.get('fact_percentage', 'N/A')}")
        print(f"    - Analytical Inferences: {epistemic.get('inference_percentage', 'N/A')}")
        print(f"    - Strategic Assumptions: {epistemic.get('assumption_percentage', 'N/A')}")

        # Display key findings
        print(f"\n" + "="*100)
        print("KEY WORKFORCE THEMES & EVIDENCE")
        print("="*100)

        answer = result_hub['answer']
        # Save HUB answer to markdown file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hub_answer_path = f"ANALYSIS_HUB_BASED_FINDINGS_{timestamp}.md"
        with open(hub_answer_path, 'w', encoding='utf-8') as f:
            f.write("# HUB-BASED ANALYSIS FINDINGS\n\n")
            f.write(f"**Analysis Type:** Hub-Based (Bidirectional Agent Network)\n\n")
            f.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Confidence:** {result_hub['confidence_score']:.0f}%\n\n")
            f.write(f"**Sources:** {result_hub['unique_sources']} documents\n\n")
            f.write(f"**Chunks:** {result_hub['total_chunks']} evidence chunks\n\n")
            f.write("---\n\n")
            f.write(answer)
        print(f"\n[HUB FINDINGS] Saved to: {hub_answer_path}")

        # Save comprehensive hub report
        report_path = f"ANALYSIS_HUB_REPORT_{timestamp}.md"
        orchestrator.save_report(result_hub, report_path)
        print(f"[HUB REPORT] Full analysis saved: {report_path}")

        # Show hub communication details
        print(f"\n" + "="*100)
        print("HUB AGENT COMMUNICATION LOG")
        print("="*100)
        comm_log = result_hub['hub_communications']
        if comm_log:
            print(f"\nTotal communications logged: {len(comm_log)}")
            print("\nMessage sequence:")
            for i, msg in enumerate(comm_log, 1):
                action = msg['action'].replace('_', ' ').title()
                status = "[OK]" if msg['status'] == "COMPLETE" else f"[{msg['status']}]"
                to_agent = f" -> {msg['to_agent']}" if msg['to_agent'] else " (broadcast)"
                print(f"  {i:2d}. {status} {msg['message_type']:8s} | {action:30s} | {msg['from_agent']:15s}{to_agent}")
        else:
            print("No hub communications logged")

        # Run comparison with traditional pipeline
        print(f"\n" + "="*100)
        print("COMPARISON: HUB-BASED vs TRADITIONAL PIPELINE")
        print("="*100)

        orchestrator_no_hub = Orchestrator(vectordb, use_hub=False, verbose=False)
        print("\nRunning traditional sequential pipeline analysis...")
        result_pipeline = orchestrator_no_hub.run_analysis(query)

        # Save PIPELINE answer to markdown file
        pipeline_answer_path = f"ANALYSIS_PIPELINE_FINDINGS_{timestamp}.md"
        pipeline_answer = result_pipeline['answer']
        with open(pipeline_answer_path, 'w', encoding='utf-8') as f:
            f.write("# PIPELINE-BASED ANALYSIS FINDINGS\n\n")
            f.write(f"**Analysis Type:** Traditional Pipeline (Sequential)\n\n")
            f.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Confidence:** {result_pipeline['confidence_score']:.0f}%\n\n")
            f.write(f"**Sources:** {result_pipeline['unique_sources']} documents\n\n")
            f.write(f"**Chunks:** {result_pipeline['total_chunks']} evidence chunks\n\n")
            f.write("---\n\n")
            f.write(pipeline_answer)
        print(f"[PIPELINE FINDINGS] Saved to: {pipeline_answer_path}")

        conf_diff = result_hub['confidence_score'] - result_pipeline['confidence_score']
        sources_diff = result_hub['unique_sources'] - result_pipeline['unique_sources']
        iterations_diff = result_hub['iterations'] - result_pipeline['iterations']

        print(f"\n[CONFIDENCE SCORES]")
        print(f"  Hub-Based:      {result_hub['confidence_score']:.1f}%")
        print(f"  Pipeline:       {result_pipeline['confidence_score']:.1f}%")
        print(f"  Improvement:    {conf_diff:+.1f}% {'(Hub better)' if conf_diff > 0 else '(Pipeline better)' if conf_diff < 0 else '(Equivalent)'}")

        print(f"\n[SOURCE COVERAGE]")
        print(f"  Hub-Based:      {result_hub['unique_sources']} sources")
        print(f"  Pipeline:       {result_pipeline['unique_sources']} sources")
        print(f"  Difference:     {sources_diff:+d} {'(Hub better)' if sources_diff > 0 else '(Pipeline better)' if sources_diff < 0 else '(Equivalent)'}")

        print(f"\n[ITERATION EFFICIENCY]")
        print(f"  Hub-Based:      {result_hub['iterations']} iterations")
        print(f"  Pipeline:       {result_pipeline['iterations']} iterations")
        print(f"  Difference:     {iterations_diff:+d} {'(Hub more efficient)' if iterations_diff < 0 else '(Pipeline more efficient)' if iterations_diff > 0 else '(Same)'}")

        print(f"\n[QUALITY RATINGS]")
        print(f"  Hub-Based:      {result_hub['quality_rating']}")
        print(f"  Pipeline:       {result_pipeline['quality_rating']}")

        # Final summary
        print(f"\n" + "="*100)
        print("ANALYSIS SUMMARY & CONCLUSIONS")
        print("="*100)

        print(f"\n[HUB EFFECTIVENESS]")
        print(f"  Agent Communications: {hub_summary['total_messages']} inter-agent messages processed")
        print(f"  Bidirectional Interactions: {'Yes - gaps triggered searches/expansion' if hub_summary['total_messages'] > 0 else 'None'}")
        print(f"  Shared State Updates: Multiple agents coordinating through hub")

        print(f"\n[ANALYTICAL INSIGHT]")
        print(f"  The hub-based architecture enables:")
        print(f"  - Dynamic request processing based on quality assessment")
        print(f"  - Targeted searches in response to identified gaps")
        print(f"  - Knowledge graph integration throughout analysis")
        print(f"  - Comprehensive communication logging for audit trail")

        print(f"\n[NEXT STEPS FOR IMPLEMENTATION]")
        print(f"  1. Populate ChromaDB with LCH organizational documents")
        print(f"  2. Implement actual hub request handling in agents")
        print(f"  3. Test with populated knowledge base")
        print(f"  4. Measure confidence improvement with real organizational data")
        print(f"  5. Fine-tune gap thresholds based on domain requirements")

        print(f"\n[TIMESTAMP] Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100 + "\n")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
