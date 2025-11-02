"""
web_lookup_agent.py

WEB LOOKUP AGENT - Phase 1 of Wide-Then-Deep Analysis

PURPOSE:
  Get external context BEFORE local RAG search. Understands the question
  in national/strategic context (NHS policy, priorities, benchmarks).

FEATURES:
  - Web search for NHS England strategy documents
  - Identify national priorities and themes
  - Suggest document selection strategy based on context
  - Provide external validation framework for local findings

USAGE:
  from web_lookup_agent import WebLookupAgent

  agent = WebLookupAgent()
  context = agent.get_context("How should LCH respond to 10-year plan?")
  themes = agent.identify_key_themes(context)
  strategy = agent.suggest_search_strategy(context)
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun


class WebLookupAgent:
    """
    Provides external context for analysis questions using web search
    and LLM analysis. No local document access - purely external context.
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        Initialize Web Lookup Agent.

        Args:
            llm: Language model for context analysis
        """
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        self.search = DuckDuckGoSearchRun()

    def get_context(self, query: str) -> Dict:
        """
        Get external context AND evidence from web.

        Returns:
            Dict with:
            - external_context: Summary of relevant national/strategic context
            - key_themes: Major themes identified in policy/strategy
            - national_priorities: What NHS England is prioritizing
            - relevant_policies: Recent relevant policy documents
            - validation_framework: How to evaluate local approach vs national
            - web_evidence: List of evidence items from web search
            - sources: List of web sources used
        """
        print("\n[PRE-PHASE: WEB LOOKUP]")
        print("Getting external context and evidence for: {}".format(query[:70]))

        # Get both context and evidence from web
        context = self._analyze_query_context(query)

        return context

    def _analyze_query_context(self, query: str) -> Dict:
        """
        Dynamically search the web for NHS and Leeds healthcare context.
        Extracts themes, priorities, evidence snippets relevant to the query.
        """
        print("\n[WEB LOOKUP]")
        print("Searching for context and evidence: {}".format(query[:70]))

        context_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "external_context": "",
            "key_themes": [],
            "national_priorities": [],
            "relevant_policies": [],
            "validation_framework": {},
            "sources": [],
            "web_evidence": []  # NEW: Store web evidence items
        }

        # Step 1: Formulate smart search query
        search_query = self._formulate_search_query(query)
        print("Search query: {}".format(search_query))

        # Step 2: Perform web search
        try:
            search_results = self.search.run(search_query)
            print("Search completed - extracting context and evidence...")
        except Exception as e:
            print("[WARNING] Web search failed: {}".format(str(e)))
            print("[INFO] Proceeding with local evidence only")
            # Return minimal context - no fallback themes
            return context_data

        # Step 3: Extract context AND evidence from results
        if search_results and search_results.strip():
            context_data = self._extract_context_from_results(
                query=query,
                search_results=search_results,
                context_data=context_data
            )
            # Step 4: Extract evidence snippets
            context_data = self._extract_evidence_from_results(
                query=query,
                search_results=search_results,
                context_data=context_data
            )
        else:
            # This should be extremely rare on the public web
            print("[WARNING] Web search returned no results - proceeding with local evidence only")
            context_data["external_context"] = ""
            # Leave key_themes and web_evidence empty

        # Add validation framework
        context_data["validation_framework"] = {
            "alignment_with_national": "Is local approach aligned with current NHS strategic direction?",
            "workforce_competitiveness": "Is local strategy competitive in current market?",
            "partnership_effectiveness": "Are partnerships enabling or constraining?",
            "equity_impact": "Does approach address or worsen inequalities?",
            "sustainability": "Can current approach be sustained given financial constraints?"
        }

        print("\n[CONTEXT EXTRACTED]")
        print("Key themes: {}".format(", ".join(context_data["key_themes"])))
        print("Priorities identified: {}".format(len(context_data["national_priorities"])))

        return context_data

    def _formulate_search_query(self, user_query: str) -> str:
        """
        Intelligently formulate web search query.
        - Keeps user query intent (doesn't force geographic restrictions)
        - Adds NHS/healthcare context
        - Adds Leeds/West Yorkshire context if relevant
        """
        query_lower = user_query.lower()

        # Check if Leeds/LCH/LTHT/West Yorkshire already mentioned
        has_local_context = any(term in query_lower for term in [
            "leeds", "lch", "ltht", "west yorkshire", "yorkshire"
        ])

        # Check if clearly national policy question
        is_national_policy = any(term in query_lower for term in [
            "national policy", "nhs england", "government", "department of health"
        ])

        # Build search query
        search_parts = [user_query]

        # Add NHS context (always relevant)
        if "nhs" not in query_lower:
            search_parts.append("NHS")

        # Add Leeds context if not already mentioned and query seems healthcare-focused
        if not has_local_context and not is_national_policy and (
            any(term in query_lower for term in [
                "service", "healthcare", "care", "staff", "workforce",
                "partnership", "integration", "community"
            ])
        ):
            search_parts.append("Leeds")

        search_query = " ".join(search_parts)
        return search_query

    def _extract_context_from_results(self, query: str, search_results: str, context_data: Dict) -> Dict:
        """
        Use LLM to extract themes, priorities, and context from web search results.
        """
        extraction_prompt = """
You are analyzing NHS/healthcare web search results to extract strategic context.

USER QUERY: {}

WEB SEARCH RESULTS:
{}

Please extract:
1. Key NHS/healthcare themes mentioned (2-4 themes as bullet points)
2. Current priorities or initiatives (3-5 priorities mentioned)
3. Relevant policies or strategic direction (2-4 items)
4. Overall context summary (2-3 sentences)

Format your response as JSON with keys:
- themes: list of identified themes
- priorities: list of priorities mentioned
- policies: list of relevant policies
- summary: text summary of findings

If the search results are sparse or irrelevant, indicate that in the summary.
"""

        try:
            response = self.llm.invoke(
                extraction_prompt.format(query, search_results[:2000])  # Limit results to token budget
            )

            # Parse LLM response
            try:
                # Try to extract JSON from response
                response_text = response.content
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1

                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    extracted = json.loads(json_str)

                    context_data["key_themes"] = extracted.get("themes", [])
                    context_data["national_priorities"] = extracted.get("priorities", [])
                    context_data["relevant_policies"] = extracted.get("policies", [])
                    context_data["external_context"] = extracted.get("summary", "")

                    # Track that content came from web search
                    if extracted.get("summary", "").lower() != "sparse":
                        context_data["sources"].append("Web search - current results")

                else:
                    # Fall back to parsing response text
                    context_data["external_context"] = response_text[:500]
                    context_data["key_themes"].append("Query-relevant context from web")

            except json.JSONDecodeError:
                # If JSON parsing fails, use response as-is
                context_data["external_context"] = response.content[:500]
                context_data["key_themes"].append("Query-relevant context from web")

        except Exception as e:
            print("[WARNING] LLM extraction failed: {}".format(str(e)))
            context_data["external_context"] = "Could not extract structured context from search results."
            context_data["key_themes"].append("Query-relevant context")

        return context_data

    def _extract_evidence_from_results(self, query: str, search_results: str, context_data: Dict) -> Dict:
        """
        Extract evidence snippets from web search results.

        Parses search results to identify and structure evidence items that can
        be combined with local evidence in the Evidence Agent.
        """
        extraction_prompt = """
You are extracting key evidence points from healthcare web search results.

USER QUERY: {}

WEB SEARCH RESULTS:
{}

Please extract 3-5 key evidence points that directly address the query.
For each point, provide:
- The claim/finding
- Supporting detail or statistic (if mentioned)
- Source indicator (website name or document type)

Format as JSON with array of objects:
[
  {{
    "claim": "The key finding or statement",
    "detail": "Supporting detail, statistics, or context",
    "source_type": "Website name or document type",
    "relevance": "How this addresses the query"
  }},
  ...
]

Focus on factual claims that can validate or contextualize local findings.
If search results are sparse, return empty array.
"""

        try:
            response = self.llm.invoke(
                extraction_prompt.format(query, search_results[:2000])
            )

            response_text = response.content
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                evidence_items = json.loads(json_str)

                # Format evidence for Evidence Agent consumption
                web_evidence = []
                for item in evidence_items:
                    web_evidence.append({
                        "content": item.get("claim", ""),
                        "detail": item.get("detail", ""),
                        "source": item.get("source_type", "Web Search"),
                        "relevance": item.get("relevance", ""),
                        "type": "WEB_EVIDENCE"
                    })

                context_data["web_evidence"] = web_evidence
                if web_evidence:
                    print("[OK] Extracted {} evidence items from web".format(len(web_evidence)))
                    for item in web_evidence[:3]:
                        print("  - {}".format(item["content"][:80]))

        except Exception as e:
            print("[WARNING] Could not extract evidence from web results: {}".format(str(e)))
            context_data["web_evidence"] = []

        return context_data

    def identify_key_themes(self, context: Dict) -> List[str]:
        """
        Extract key themes from context.

        Returns:
            List of identified themes
        """
        return context.get("key_themes", [])

    def identify_priorities(self, context: Dict) -> List[str]:
        """
        Extract national priorities from context.

        Returns:
            List of national priorities
        """
        return context.get("national_priorities", [])

    def suggest_search_strategy(self, context: Dict) -> Dict:
        """
        Suggest which documents to search based on context.

        Returns:
            Dict with:
            - priority_tags: Document tags to prioritize
            - search_terms: Concepts to search for locally
            - related_areas: Related topics to explore
            - iteration_strategy: If first search too narrow, what to expand to
        """
        themes = context.get("key_themes", [])

        strategy = {
            "query_context": context.get("query", ""),
            "identified_themes": themes,
            "priority_tags": self._get_priority_tags(themes),
            "search_terms": self._get_search_terms(themes),
            "related_areas": self._get_related_areas(themes),
            "iteration_strategy": "If too narrow, expand to related areas"
        }

        print("\n[SEARCH STRATEGY]")
        print("Priority tags: {}".format(", ".join(strategy.get("priority_tags", []))))
        print("Search terms: {}".format(", ".join(strategy.get("search_terms", [])[:3])))

        return strategy

    def _get_priority_tags(self, themes: List[str]) -> List[str]:
        """
        Return document tags to prioritize based on themes.
        Uses your metadata: document_type, strategic_level, organization
        """
        tags = []

        for theme in themes:
            theme_lower = theme.lower()

            if "workforce" in theme_lower:
                tags.extend(["workforce", "strategy", "lch"])
            elif "10-year" in theme_lower:
                tags.extend(["strategic", "policy", "national"])
            elif "partnership" in theme_lower or "integration" in theme_lower:
                tags.extend(["partnership", "integration", "strategy"])
            elif "inequalities" in theme_lower or "equity" in theme_lower:
                tags.extend(["equity", "health_inequalities", "lch"])

        return list(set(tags))  # Remove duplicates

    def _get_search_terms(self, themes: List[str]) -> List[str]:
        """
        Return search terms to look for in documents.
        """
        terms = []

        for theme in themes:
            theme_lower = theme.lower()

            if "workforce" in theme_lower:
                terms.extend([
                    "workforce planning",
                    "recruitment",
                    "staff turnover",
                    "staffing strategy",
                    "employment"
                ])
            elif "10-year" in theme_lower:
                terms.extend([
                    "10-year plan",
                    "strategic priorities",
                    "five-year forward view",
                    "planning guidance"
                ])
            elif "partnership" in theme_lower:
                terms.extend([
                    "partnership",
                    "integrated care",
                    "collaboration",
                    "icb",
                    "place-based"
                ])
            elif "inequalities" in theme_lower:
                terms.extend([
                    "health inequalities",
                    "health equity",
                    "disparities",
                    "vulnerable populations"
                ])

        return list(set(terms))

    def _get_related_areas(self, themes: List[str]) -> List[str]:
        """
        Return related areas to explore if first search too narrow.
        """
        related = []

        for theme in themes:
            theme_lower = theme.lower()

            if "workforce" in theme_lower:
                related.extend(["training", "development", "retention", "recruitment"])
            elif "10-year" in theme_lower:
                related.extend(["partnership", "workforce", "finance", "innovation"])
            elif "partnership" in theme_lower:
                related.extend(["governance", "finance", "strategy", "outcomes"])
            elif "inequalities" in theme_lower:
                related.extend(["demographics", "social", "partnership", "targeted"])

        return list(set(related))

    def get_validation_questions(self, context: Dict) -> List[str]:
        """
        Get validation questions to check local findings against national context.
        """
        framework = context.get("validation_framework", {})
        return list(framework.values())


def demo_web_lookup():
    """Demo the web lookup agent."""
    agent = WebLookupAgent()

    queries = [
        "How should LCH respond to the 10-year plan?",
        "What are the workforce challenges for Leeds Community Healthcare?",
        "How should LCH structure partnerships for integrated care?"
    ]

    for query in queries:
        print("\n" + "="*70)
        print("Query: {}".format(query))
        print("="*70)

        context = agent.get_context(query)
        strategy = agent.suggest_search_strategy(context)

        print("\nExternal Context Summary:")
        print(context.get("external_context", "")[:300])

        print("\n")


if __name__ == "__main__":
    demo_web_lookup()
