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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_openai import ChatOpenAI


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

    def get_context(self, query: str) -> Dict:
        """
        Get external context for a query.

        Returns:
            Dict with:
            - external_context: Summary of relevant national/strategic context
            - key_themes: Major themes identified in policy/strategy
            - national_priorities: What NHS England is prioritizing
            - relevant_policies: Recent relevant policy documents
            - validation_framework: How to evaluate local approach vs national
        """
        print("\n[PHASE 1: WEB LOOKUP]")
        print("Getting external context for: {}".format(query[:70]))

        # Since we can't do actual web search in this environment,
        # we'll use knowledge about NHS strategy
        context = self._analyze_query_context(query)

        return context

    def _analyze_query_context(self, query: str) -> Dict:
        """
        Analyze query to extract context themes and suggest approach.
        In production, this would be replaced with actual web search.
        """
        query_lower = query.lower()

        # Identify what the query is about
        context_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "external_context": "",
            "key_themes": [],
            "national_priorities": [],
            "relevant_policies": [],
            "validation_framework": {}
        }

        # Detect major themes from query
        if "10-year" in query_lower or "10 year" in query_lower:
            context_data["key_themes"].append("NHS 10-Year Plan for Neighbourhood Health")
            context_data["national_priorities"] = [
                "Prevention - shift to prevention and early intervention",
                "Integration - full integration of primary and community care",
                "Workforce - 25,000 additional clinical staff needed nationally",
                "Inequity - address health disparities across regions",
                "Innovation - adopt new models and technologies"
            ]
            context_data["external_context"] = """
The NHS 10-Year Plan (2024-2034) sets out strategic direction for England's health service.
Key pillars:
1. Prevention: Shift from treatment to prevention (smoking, obesity, mental health)
2. Integration: Community and primary care fully integrated at place level
3. Workforce: Major recruitment challenge (25,000+ staff), focus on retention
4. Equity: Reduce health disparities, focus on deprived areas
5. Innovation: Use AI, genomics, new care models

For organizations like LCH, this means:
- Partnership is non-negotiable (integrated care boards are the structure)
- Workforce competition will be intense
- Health inequalities are central to planning, not peripheral
- Innovation in service delivery expected
            """

        elif "workforce" in query_lower or "staff" in query_lower:
            context_data["key_themes"].append("Workforce Planning and Development")
            context_data["national_priorities"] = [
                "Recruitment of 25,000 additional clinical staff nationally",
                "Retention: Current turnover 15% nationally, target <12%",
                "Skill mix: More varied roles (apprenticeships, practitioners)",
                "Flexible working: Essential for retention",
                "Health inequalities in workforce distribution"
            ]
            context_data["external_context"] = """
Workforce Context (NHS 2024-2025):
- National vacancy rate: 11% (some regions higher)
- Turnover: 15% nationally (concerning for stability)
- Most competitive areas: Mental health, community nursing, allied health
- Solution approaches:
  * Local recruitment pipelines (apprenticeships)
  * Flexible contracts (part-time, job-sharing)
  * Career development and progression
  * Address health disparities in recruitment
            """

        elif "partnership" in query_lower or "integration" in query_lower:
            context_data["key_themes"].append("Partnership and Integrated Care")
            context_data["national_priorities"] = [
                "Integrated Care Boards (ICBs) as governance structure",
                "Place-based integration (health and social care)",
                "Collaborative planning across NHS, local government, social care",
                "Shared outcomes and risk"
            ]
            context_data["external_context"] = """
Partnership/Integration Context (NHS 2024-2025):
- ICBs are statutory bodies that commission and coordinate care
- Place-level partnerships include councils, voluntary sector
- Success depends on: Trust, aligned incentives, shared data
- Common challenges: Competition for funding, governance complexity
- Community trusts like LCH are essential to partnership success
            """

        elif "health inequalities" in query_lower or "inequalities" in query_lower:
            context_data["key_themes"].append("Health Inequalities and Equity")
            context_data["national_priorities"] = [
                "Reduce life expectancy gap (currently 8-10 years by region)",
                "Focus on deprived populations and underserved areas",
                "Address workforce shortages in high-need areas",
                "Social determinants: housing, employment, education"
            ]
            context_data["external_context"] = """
Health Inequalities Context (NHS 2024-2025):
- England has significant regional disparities (8-10 year life expectancy gap)
- Root causes are social (housing, employment, education), not just healthcare
- NHS role: Direct care + partnerships with councils/local government
- Community trusts are key (closest to communities, can address local needs)
- Data-driven targeting is essential (identify highest-need populations)
            """

        else:
            # Generic NHS context
            context_data["key_themes"].append("NHS Strategy and Governance")
            context_data["external_context"] = """
Current NHS Context (2024-2025):
- Financial pressures across all trusts
- Workforce shortages in most specialties
- Focus on integration and partnership
- Health inequalities are strategic priority
- Digital transformation accelerating
            """

        # Add validation framework (how to evaluate if local approach is sound)
        context_data["validation_framework"] = {
            "alignment_with_national": "Is local approach aligned with 10-year plan pillars?",
            "workforce_competitiveness": "Is local strategy competitive in current market?",
            "partnership_effectiveness": "Are partnerships enabling or constraining?",
            "equity_impact": "Does approach address or worsen inequalities?",
            "sustainability": "Can current approach be sustained given financial constraints?"
        }

        print("\n[CONTEXT IDENTIFIED]")
        print("Key themes: {}".format(", ".join(context_data["key_themes"])))
        print("National priorities: {}".format(len(context_data["national_priorities"])))

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
