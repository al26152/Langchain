"""
orchestrator.py

ORCHESTRATOR FOR MULTI-AGENT ITERATIVE RAG SYSTEM

PURPOSE:
  Controls the multi-agent workflow, manages iterations, tracks progress,
  and coordinates between Evidence, Critique, and Synthesis agents.

FEATURES:
  - Iteration loop management
  - Agent coordination (Evidence + Critique + Synthesis)
  - Progress tracking and logging
  - Stopping criteria enforcement
  - Result aggregation

USAGE:
  from orchestrator import Orchestrator

  orchestrator = Orchestrator(vectordb)
  result = orchestrator.run_analysis(query)
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

# Import configuration
try:
    from config import Config
except ImportError:
    print("[WARNING] Could not import config, using defaults")
    Config = None

# Import agents - handle both package and direct execution
import importlib
import importlib.util

def _import_agent_class(agent_name, class_name):
    """Import an agent class flexibly using importlib."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.join(current_dir, f"{agent_name}.py")

    # Load module directly from file path
    try:
        spec = importlib.util.spec_from_file_location(agent_name, module_path)
        if spec is None:
            raise ImportError(f"Could not create spec for {module_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[agent_name] = module
        spec.loader.exec_module(module)
        return getattr(module, class_name)
    except Exception as e:
        raise ImportError(f"Failed to import {class_name} from {agent_name}: {str(e)}")

# Import all agent classes
try:
    EvidenceAgent = _import_agent_class("evidence_agent", "EvidenceAgent")
    CritiqueAgent = _import_agent_class("critique_agent", "CritiqueAgent")
    SynthesisAgent = _import_agent_class("synthesis_agent", "SynthesisAgent")
    WebLookupAgent = _import_agent_class("web_lookup_agent", "WebLookupAgent")
    DocumentSelectorAgent = _import_agent_class("document_selector_agent", "DocumentSelectorAgent")
except ImportError as e:
    print(f"WARNING: Could not import agents: {str(e)}")
    raise


class Orchestrator:
    """
    Main orchestrator for multi-agent iterative RAG system.

    Coordinates Evidence Agent, Critique Agent, and Synthesis Agent
    through multiple iterations until convergence or stopping criteria met.
    """

    def __init__(
        self,
        vectordb: Chroma,
        llm: Optional[ChatOpenAI] = None,
        max_iterations: Optional[int] = None,
        verbose: bool = True,
    ):
        """
        Initialize Orchestrator.

        Args:
            vectordb: ChromaDB vector store
            llm: Language model (optional, defaults from config)
            max_iterations: Maximum iterations allowed (defaults from config)
            verbose: Enable detailed logging
        """
        self.vectordb = vectordb

        # Use config for defaults
        if Config:
            default_model = Config.DEFAULT_LLM_MODEL
            default_temp = Config.DEFAULT_TEMPERATURE
            self.max_iterations = max_iterations or Config.MAX_ITERATIONS
        else:
            default_model = "gpt-4o"
            default_temp = 0.5
            self.max_iterations = max_iterations or 5

        self.llm = llm or ChatOpenAI(model=default_model, temperature=default_temp)
        self.verbose = verbose

        # Initialize agents (they will use config defaults if not specified)
        self.web_lookup_agent = WebLookupAgent(self.llm)
        self.document_selector_agent = DocumentSelectorAgent(vectordb)
        self.evidence_agent = EvidenceAgent(vectordb, self.llm)
        self.critique_agent = CritiqueAgent(max_iterations=self.max_iterations)
        self.synthesis_agent = SynthesisAgent(self.llm)

    def run_wide_then_deep_analysis(self, query: str) -> Dict:
        """
        Run complete 4-phase wide-then-deep analysis.

        PHASES:
        1. Web Lookup: Get external context (themes, priorities)
        2. Document Selection: Filter documents using web context + metadata tags
        3. Evidence Search: RAG search limited to selected documents
        4. Analysis & Synthesis: Critique and generate long-form output

        Args:
            query: Strategic question to analyze

        Returns:
            Dict containing all phase results and final synthesis
        """
        print("="*80)
        print("WIDE-THEN-DEEP 4-PHASE ANALYSIS")
        print("="*80)
        print(f"\nQuestion: {query}")
        print(f"Start time: {datetime.now().strftime('%H:%M:%S')}\n")

        # PHASE 1: Web Lookup - Get external context
        print("\n" + "="*80)
        print("PHASE 1: WEB LOOKUP (External Context)")
        print("="*80)
        web_context = self.web_lookup_agent.get_context(query)
        print(f"[OK] Web context retrieved")
        print(f"    Themes: {', '.join(web_context.get('key_themes', []))}")
        print(f"    Priorities: {len(web_context.get('national_priorities', []))} identified")

        # PHASE 2: Document Selection - Intelligently filter documents
        print("\n" + "="*80)
        print("PHASE 2: DOCUMENT SELECTION (Smart Filtering)")
        print("="*80)
        selection_result = self.document_selector_agent.select_documents(query, web_context)
        selected_docs = selection_result["selected"]
        print(f"[OK] Document selection complete")
        print(f"    Selected: {selection_result['selected_count']} of {selection_result['total_documents']} documents")
        print(f"    Coverage: {(selection_result['selected_count']/selection_result['total_documents']*100):.1f}%")

        # Validate selection
        validation = self.critique_agent.validate_document_selection(
            selected_docs, query, selection_result["total_documents"], web_context
        )
        print(f"    Validation: {validation['recommendation']}")
        if validation['recommendation'] == "EXPAND":
            print(f"    [WARNING] Selection too narrow - expanding scope")
            # TODO: Could trigger automatic expansion here

        # PHASE 3: Evidence Search - RAG with document filter
        print("\n" + "="*80)
        print("PHASE 3: EVIDENCE RETRIEVAL (Limited to Selected Documents)")
        print("="*80)
        iteration_results = []
        critique_results = []
        iteration_num = 1

        # Iteration loop (limited search space)
        while iteration_num <= self.max_iterations:
            print(f"\n{'='*80}")
            print(f"ITERATION {iteration_num}")
            print(f"{'='*80}")

            # Get previous gaps
            previous_gaps = critique_results[-1]["gaps"] if critique_results else []

            # STEP 1: Evidence Agent - Search within selected documents
            k = Config.DEFAULT_RETRIEVAL_K if Config else 20
            evidence_result = self.evidence_agent.search(
                query=query,
                iteration_num=iteration_num,
                previous_gaps=previous_gaps,
                k=k,
                selected_documents=selected_docs,  # FILTERED SEARCH
            )

            iteration_results.append(evidence_result)

            # STEP 2: Critique Agent - Analyze quality
            critique_result = self.critique_agent.analyze(
                evidence_result=evidence_result,
                iteration_history=iteration_results[:-1],
                query=query,
            )

            critique_results.append(critique_result)

            # STEP 3: Check stopping criteria
            if not critique_result["continue_iteration"]:
                print(f"\n{'='*80}")
                print("STOPPING CRITERIA MET")
                print(f"{'='*80}")
                print(f"Reason: {self._get_stop_reason(critique_result, iteration_num)}")
                break

            iteration_num += 1

        # PHASE 4: Synthesis - Generate final long-form report
        print(f"\n{'='*80}")
        print("PHASE 4: SYNTHESIS (Long-Form Analysis)")
        print(f"{'='*80}")

        final_critique = critique_results[-1]

        synthesis_result = self.synthesis_agent.synthesize(
            query=query,
            iteration_results=iteration_results,
            final_critique=final_critique,
        )

        # Summary
        print(f"\n{'='*80}")
        print("WIDE-THEN-DEEP ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"\nIterations: {len(iteration_results)}")
        print(f"Sources consulted: {synthesis_result['unique_sources']}")
        print(f"Evidence chunks: {synthesis_result['total_evidence_chunks']}")
        print(f"Confidence: {synthesis_result['confidence_score']:.0f}%")
        print(f"Quality: {final_critique['overall_quality']}")
        print(f"\nEnd time: {datetime.now().strftime('%H:%M:%S')}")

        return {
            "query": query,
            "phase1_web_context": web_context,
            "phase2_document_selection": selection_result,
            "final_report": synthesis_result["report_markdown"],
            "answer": synthesis_result["answer"],
            "confidence_score": synthesis_result["confidence_score"],
            "quality_rating": final_critique["overall_quality"],
            "iterations": len(iteration_results),
            "unique_sources": synthesis_result["unique_sources"],
            "total_chunks": synthesis_result["total_evidence_chunks"],
            "epistemic_summary": synthesis_result["epistemic_summary"],
            "all_iteration_results": iteration_results,
            "all_critique_results": critique_results,
            "synthesis_result": synthesis_result,
        }

    def run_analysis(self, query: str) -> Dict:
        """
        Run complete multi-agent analysis (original method - backward compatible).

        This method is kept for backward compatibility. For new analysis, use run_wide_then_deep_analysis()

        Args:
            query: Strategic question to analyze

        Returns:
            Dict containing:
            - final_report: Complete markdown report
            - confidence_score: Overall confidence (0-100)
            - iterations: Number of iterations run
            - all_results: Raw results from all iterations
        """
        print("="*80)
        print("MULTI-AGENT ITERATIVE RAG ANALYSIS (Legacy Mode)")
        print("="*80)
        print(f"\nQuestion: {query}")
        print(f"Max iterations: {self.max_iterations}")
        print(f"Start time: {datetime.now().strftime('%H:%M:%S')}\n")
        print("[NOTE] Using legacy mode - consider run_wide_then_deep_analysis() for better results\n")

        iteration_results = []
        critique_results = []
        iteration_num = 1

        # Iteration loop
        while iteration_num <= self.max_iterations:
            print(f"\n{'='*80}")
            print(f"ITERATION {iteration_num}")
            print(f"{'='*80}")

            # Get previous gaps
            previous_gaps = critique_results[-1]["gaps"] if critique_results else []

            # STEP 1: Evidence Agent - Retrieve evidence
            # Use config for k value, default to 30 to include strategic documents
            k = Config.DEFAULT_RETRIEVAL_K if Config else 30
            evidence_result = self.evidence_agent.search(
                query=query,
                iteration_num=iteration_num,
                previous_gaps=previous_gaps,
                k=k,
            )

            iteration_results.append(evidence_result)

            # STEP 2: Critique Agent - Analyze quality and identify gaps
            critique_result = self.critique_agent.analyze(
                evidence_result=evidence_result,
                iteration_history=iteration_results[:-1],  # Exclude current
                query=query,
            )

            critique_results.append(critique_result)

            # STEP 3: Check stopping criteria
            if not critique_result["continue_iteration"]:
                print(f"\n{'='*80}")
                print("STOPPING CRITERIA MET")
                print(f"{'='*80}")
                print(f"Reason: {self._get_stop_reason(critique_result, iteration_num)}")
                break

            iteration_num += 1

        # STEP 4: Synthesis Agent - Generate final report
        print(f"\n{'='*80}")
        print("SYNTHESIS PHASE")
        print(f"{'='*80}")

        final_critique = critique_results[-1]

        synthesis_result = self.synthesis_agent.synthesize(
            query=query,
            iteration_results=iteration_results,
            final_critique=final_critique,
        )

        # Summary
        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"\nIterations: {len(iteration_results)}")
        print(f"Sources consulted: {synthesis_result['unique_sources']}")
        print(f"Evidence chunks: {synthesis_result['total_evidence_chunks']}")
        print(f"Confidence: {synthesis_result['confidence_score']:.0f}%")
        print(f"Quality: {final_critique['overall_quality']}")
        print(f"\nEnd time: {datetime.now().strftime('%H:%M:%S')}")

        return {
            "query": query,
            "final_report": synthesis_result["report_markdown"],
            "answer": synthesis_result["answer"],
            "confidence_score": synthesis_result["confidence_score"],
            "quality_rating": final_critique["overall_quality"],
            "iterations": len(iteration_results),
            "unique_sources": synthesis_result["unique_sources"],
            "total_chunks": synthesis_result["total_evidence_chunks"],
            "epistemic_summary": synthesis_result["epistemic_summary"],
            "all_iteration_results": iteration_results,
            "all_critique_results": critique_results,
            "synthesis_result": synthesis_result,
        }

    def _get_stop_reason(self, critique: Dict, iteration_num: int) -> str:
        """Get human-readable stopping reason."""
        if iteration_num >= self.max_iterations:
            return f"Maximum iterations ({self.max_iterations}) reached"

        if critique["overall_quality"] == "EXCELLENT":
            return "Excellent quality achieved"

        if critique["overall_quality"] == "GOOD" and critique["convergence_detected"]:
            return "Good quality + convergence detected"

        if critique["overall_quality"] == "ADEQUATE" and critique["convergence_detected"]:
            high_gaps = [g for g in critique["gaps"] if g.get("severity") == "HIGH"]
            if not high_gaps:
                return "Adequate quality + convergence + no high-priority gaps"

        return "Stopping criteria met"

    def save_report(self, result: Dict, output_path: str = None) -> str:
        """
        Save report to file.

        Args:
            result: Result from run_analysis()
            output_path: Output file path (optional)

        Returns:
            Path to saved report
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"multi_agent_report_{timestamp}.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["final_report"])

        print(f"\n[OK] Report saved: {output_path}")
        return output_path
