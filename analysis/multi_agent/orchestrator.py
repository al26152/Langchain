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

# Import AgentHub
try:
    from analysis.multi_agent.agent_hub import AgentHub
except ImportError:
    try:
        from agent_hub import AgentHub
    except ImportError:
        print("[ERROR] Could not import AgentHub")
        raise

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
    KnowledgeGraphAgent = _import_agent_class("knowledge_graph_agent", "KnowledgeGraphAgent")
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
        use_hub: bool = True,
    ):
        """
        Initialize Orchestrator.

        Args:
            vectordb: ChromaDB vector store
            llm: Language model (optional, defaults from config)
            max_iterations: Maximum iterations allowed (defaults from config)
            verbose: Enable detailed logging
            use_hub: Enable AgentHub for bidirectional communication (default True)
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
        self.use_hub = use_hub

        # Initialize agents (they will use config defaults if not specified)
        self.web_lookup_agent = WebLookupAgent(self.llm)
        self.document_selector_agent = DocumentSelectorAgent(vectordb)
        self.evidence_agent = EvidenceAgent(vectordb, self.llm)
        self.critique_agent = CritiqueAgent(max_iterations=self.max_iterations)
        self.synthesis_agent = SynthesisAgent(self.llm)
        self.knowledge_graph_agent = KnowledgeGraphAgent()

        # Initialize AgentHub for bidirectional communication
        if self.use_hub:
            self.hub = AgentHub(verbose=verbose)
            self.hub.register_agent("web_lookup", self.web_lookup_agent)
            self.hub.register_agent("document_selector", self.document_selector_agent)
            self.hub.register_agent("evidence", self.evidence_agent)
            self.hub.register_agent("critique", self.critique_agent)
            self.hub.register_agent("synthesis", self.synthesis_agent)
            self.hub.register_agent("knowledge_graph", self.knowledge_graph_agent)

            if self.verbose:
                print("[OK] AgentHub initialized with 6 agents registered")

    def run_analysis_with_hub(self, query: str) -> Dict:
        """
        Run analysis using AgentHub for bidirectional agent communication.

        This method enables true multi-agent collaboration where agents can
        request actions from each other, not just follow a sequential pipeline.

        WORKFLOW:
        - PRE-PHASE: Web Lookup - Get external context and evidence
        - PHASE 1-N: Hub-driven iteration with feedback loops
          * EvidenceAgent searches based on previous gaps
          * CritiqueAgent can request DocumentSelector expansion
          * CritiqueAgent can request targeted WebLookup
          * SynthesisAgent can request additional evidence
        - FINAL: SynthesisAgent generates comprehensive answer

        Args:
            query: Strategic question to analyze

        Returns:
            Dict containing all results and analysis metadata
        """
        print("="*80)
        print("MULTI-AGENT NETWORK ANALYSIS (HUB-BASED)")
        print("="*80)
        print(f"\nQuestion: {query}")
        print(f"Max iterations: {self.max_iterations}")
        print(f"Start time: {datetime.now().strftime('%H:%M:%S')}\n")

        # PRE-PHASE: Web Lookup
        print("="*80)
        print("PRE-PHASE: WEB LOOKUP (External Context & Evidence)")
        print("="*80)
        web_context = self.web_lookup_agent.get_context(query)
        web_evidence = web_context.get("web_evidence", [])
        print(f"[OK] Web context retrieved")
        print(f"    Themes: {', '.join(web_context.get('key_themes', []))}")
        print(f"    Priorities: {len(web_context.get('national_priorities', []))} identified")
        if web_evidence:
            print(f"    Web evidence: {len(web_evidence)} items extracted")
        else:
            print(f"    Web evidence: None found (will use local search only)")

        # Initialize hub state
        self.hub.update_shared_state({
            "web_context": web_context,
            "evidence_pool": web_evidence if web_evidence else [],
            "iteration_history": [],
            "critique_history": [],
            "web_search_invoked": True,
            "last_web_search_iteration": 0,
        })

        iteration_results = []
        critique_results = []
        iteration_num = 1
        web_evidence_used = False if not web_evidence else True

        # PHASE 1-N: Iteration loop with hub coordination
        while iteration_num <= self.max_iterations:
            print(f"\n{'='*80}")
            print(f"ITERATION {iteration_num}")
            print(f"{'='*80}")

            # Get previous gaps for Evidence Agent
            previous_gaps = critique_results[-1]["gaps"] if critique_results else []

            # STEP 1: Evidence Agent searches (may respond to requests from other agents)
            k = Config.DEFAULT_RETRIEVAL_K if Config else 30
            evidence_result = self.evidence_agent.search(
                query=query,
                iteration_num=iteration_num,
                previous_gaps=previous_gaps,
                k=k,
                web_evidence=web_evidence if iteration_num == 1 else None,
            )

            iteration_results.append(evidence_result)
            self.hub.append_to_state("iteration_history", evidence_result)

            if evidence_result.get("web_evidence_included"):
                web_evidence_used = True

            # STEP 2: Critique Agent analyzes and can request actions
            critique_result = self.critique_agent.analyze(
                evidence_result=evidence_result,
                iteration_history=iteration_results[:-1],
                query=query,
            )

            critique_results.append(critique_result)
            self.hub.append_to_state("critique_history", critique_result)

            # STEP 3: Process critique and send hub requests for bidirectional communication
            if self.use_hub:
                self._process_critique_for_hub_requests(
                    critique_result, iteration_num, query
                )

            # STEP 4: Check stopping criteria
            if not critique_result["continue_iteration"]:
                print(f"\n{'='*80}")
                print("STOPPING CRITERIA MET")
                print(f"{'='*80}")
                print(f"Reason: {self._get_stop_reason(critique_result, iteration_num)}")
                break

            iteration_num += 1

        # FINAL: Synthesis - Generate comprehensive answer
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
        print("ANALYSIS COMPLETE (HUB-BASED)")
        print(f"{'='*80}")
        print(f"\nIterations: {len(iteration_results)}")
        print(f"Sources consulted: {synthesis_result['unique_sources']}")
        print(f"Evidence chunks: {synthesis_result['total_evidence_chunks']}")
        print(f"Confidence: {synthesis_result['confidence_score']:.0f}%")
        print(f"Quality: {final_critique['overall_quality']}")
        print(f"\nEnd time: {datetime.now().strftime('%H:%M:%S')}")

        # Log communication summary
        comm_summary = self.hub.get_communication_summary()
        print(f"\nAgent Communications: {comm_summary['total_messages']} messages")

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
            "web_evidence_used": web_evidence_used,
            "web_context": web_context,
            "hub_communications": self.hub.get_communication_log(),
            "hub_summary": comm_summary,
        }

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
        Run complete multi-agent analysis with web lookup pre-phase.

        WORKFLOW:
        - PRE-PHASE: Web Lookup - Get external context and evidence
        - PHASE 1: Evidence Agent - Retrieve local + web evidence
        - PHASE 2: Critique Agent - Analyze quality and identify gaps
        - PHASE 3: Synthesis Agent - Generate comprehensive answer

        Args:
            query: Strategic question to analyze

        Returns:
            Dict containing:
            - final_report: Complete markdown report
            - confidence_score: Overall confidence (0-100)
            - iterations: Number of iterations run
            - all_results: Raw results from all iterations
            - web_evidence_used: Boolean indicating if web evidence was included
        """
        print("="*80)
        print("MULTI-AGENT ITERATIVE RAG ANALYSIS WITH WEB LOOKUP")
        print("="*80)
        print(f"\nQuestion: {query}")
        print(f"Max iterations: {self.max_iterations}")
        print(f"Start time: {datetime.now().strftime('%H:%M:%S')}\n")

        # PRE-PHASE: Web Lookup - Get external context and evidence
        print("="*80)
        print("PRE-PHASE: WEB LOOKUP (External Context & Evidence)")
        print("="*80)
        web_context = self.web_lookup_agent.get_context(query)
        web_evidence = web_context.get("web_evidence", [])
        print(f"[OK] Web context retrieved")
        print(f"    Themes: {', '.join(web_context.get('key_themes', []))}")
        print(f"    Priorities: {len(web_context.get('national_priorities', []))} identified")
        if web_evidence:
            print(f"    Web evidence: {len(web_evidence)} items extracted")
        else:
            print(f"    Web evidence: None found (will use local search only)")

        iteration_results = []
        critique_results = []
        iteration_num = 1
        web_evidence_used = False

        # Iteration loop
        while iteration_num <= self.max_iterations:
            print(f"\n{'='*80}")
            print(f"ITERATION {iteration_num}")
            print(f"{'='*80}")

            # Get previous gaps
            previous_gaps = critique_results[-1]["gaps"] if critique_results else []

            # STEP 1: Evidence Agent - Retrieve evidence (local + web)
            # Use config for k value, default to 30 to include strategic documents
            k = Config.DEFAULT_RETRIEVAL_K if Config else 30
            evidence_result = self.evidence_agent.search(
                query=query,
                iteration_num=iteration_num,
                previous_gaps=previous_gaps,
                k=k,
                web_evidence=web_evidence if iteration_num == 1 else None,  # Add web evidence in first iteration only
            )
            # Track if web evidence was used
            if evidence_result.get("web_evidence_included"):
                web_evidence_used = True

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
            "web_evidence_used": web_evidence_used,
            "web_context": web_context,
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

    def _process_critique_for_hub_requests(
        self, critique_result: Dict, iteration_num: int, query: str
    ) -> None:
        """
        Process critique results and send appropriate hub requests.

        Enables bidirectional agent communication:
        - High-priority gaps trigger document expansion requests
        - Weak quality triggers targeted web search requests
        - Contradictions trigger synthesis validation requests

        Args:
            critique_result: Result from CritiqueAgent.analyze()
            iteration_num: Current iteration number
            query: Original query
        """
        if not self.use_hub:
            return

        gaps = critique_result.get("gaps", [])
        quality = critique_result.get("overall_quality", "ADEQUATE")

        # INTERACTION 1: Request document expansion for high-priority gaps
        high_priority_gaps = [g for g in gaps if g.get("severity") == "HIGH"]
        if high_priority_gaps and self.hub.get_agent("document_selector"):
            print(f"\n[HUB] Critique detected {len(high_priority_gaps)} high-priority gaps")
            print(f"[HUB] Requesting document expansion via DocumentSelectorAgent")

            expansion_request = self.hub.send_message(
                from_agent="orchestrator",
                to_agent="document_selector",
                action="expand_selection",
                params={
                    "gaps": high_priority_gaps,
                    "query": query,
                    "iteration": iteration_num,
                },
                priority=8,
            )

            # Process request (simplified - in production would be async)
            results = self.hub.process_queue()
            if results.get("successful") > 0:
                print(f"[HUB] Document expansion processed")

        # INTERACTION 2: Request targeted web search for weak quality
        if quality == "WEAK" and iteration_num <= 3:
            if self.hub.get_agent("web_lookup"):
                print(f"\n[HUB] Quality is WEAK - requesting targeted web search")

                web_request = self.hub.send_message(
                    from_agent="orchestrator",
                    to_agent="web_lookup",
                    action="search_for_gaps",
                    params={
                        "gaps": gaps[:3],  # Top 3 gaps
                        "query": query,
                        "iteration": iteration_num,
                    },
                    priority=7,
                )

                results = self.hub.process_queue()
                if results.get("successful") > 0:
                    print(f"[HUB] Web search request processed")

        # INTERACTION 3: Request knowledge graph expansion
        if self.hub.get_agent("knowledge_graph"):
            kg_request = self.hub.send_message(
                from_agent="orchestrator",
                to_agent="knowledge_graph",
                action="find_gaps",
                params={
                    "query": query,
                    "iteration": iteration_num,
                },
                priority=5,
            )
            results = self.hub.process_queue()

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
