"""
data_quality_agent.py

PURPOSE:
  Assesses data completeness and reliability across evidence sources,
  identifies critical gaps, and prioritizes future data collection.
  Creates Data Quality Assessment section with transparency.

FEATURES:
  - High/Medium/Low confidence data source classification
  - Explicit gap identification and handling approaches
  - Priority ranking for future data collection
  - Data collection enhancement strategy

USAGE:
  from data_quality_agent import DataQualityAgent

  agent = DataQualityAgent()
  assessment = agent.assess(evidence_result, iteration_results)
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from config import Config
except ImportError:
    Config = None


class DataQualityAgent:
    """
    Assesses data quality and completeness across evidence sources.

    Classifies data sources by confidence, identifies gaps, and creates
    Data Quality Assessment section with transparency about limitations.
    """

    def assess(
        self,
        evidence_chunks: List[Dict],
        iteration_results: List[Dict],
        query: str,
        web_context: Optional[Dict] = None,
    ) -> Dict:
        """
        Assess data quality and completeness.

        Args:
            evidence_chunks: List of evidence dictionaries with metadata
            iteration_results: Raw results from all iterations
            query: Original query analyzed
            web_context: Web lookup context (optional)

        Returns:
            Dict with:
            - high_quality_sources: 85-90% confidence sources
            - medium_quality_sources: 70-80% confidence sources
            - lower_quality_sources: 50-60% confidence sources
            - critical_gaps: High severity gaps
            - medium_gaps: Medium severity gaps
            - collection_priority: Ranked list for future collection
            - enhancement_strategy: Recommendations for improvement
        """

        # Classify sources by quality
        high, medium, lower = self._classify_sources(evidence_chunks)

        # Identify gaps
        critical_gaps, medium_gaps, low_gaps = self._identify_gaps(
            evidence_chunks, query, high, medium, lower
        )

        # Create collection priority ranking
        collection_priority = self._rank_collection_priorities(
            critical_gaps, medium_gaps, evidence_chunks
        )

        # Enhancement strategy
        enhancement = self._create_enhancement_strategy(
            critical_gaps, medium_gaps, collection_priority
        )

        return {
            "high_quality_sources": high,
            "medium_quality_sources": medium,
            "lower_quality_sources": lower,
            "critical_gaps": critical_gaps,
            "medium_gaps": medium_gaps,
            "low_gaps": low_gaps,
            "collection_priority": collection_priority,
            "enhancement_strategy": enhancement,
            "assessment_timestamp": datetime.now().isoformat(),
        }

    def _classify_sources(
        self,
        chunks: List[Dict],
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Classify evidence sources by quality and confidence.

        Returns:
            Tuple of (high_quality, medium_quality, lower_quality)
        """

        high_quality = []
        medium_quality = []
        lower_quality = []

        # Group chunks by source for analysis
        sources_by_type = defaultdict(list)
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            source = metadata.get("source", "Unknown")
            doc_type = metadata.get("document_type", "general")
            sources_by_type[(source, doc_type)].append(chunk)

        # Classify each source
        for (source, doc_type), source_chunks in sources_by_type.items():
            quality_score, confidence, reasoning = self._score_source_quality(
                source, doc_type, len(source_chunks)
            )

            source_info = {
                "source": source,
                "type": doc_type,
                "confidence": confidence,
                "quality_score": quality_score,
                "chunk_count": len(source_chunks),
                "reasoning": reasoning,
            }

            if confidence == "85-90%":
                high_quality.append(source_info)
            elif confidence == "70-80%":
                medium_quality.append(source_info)
            else:
                lower_quality.append(source_info)

        return high_quality, medium_quality, lower_quality

    def _score_source_quality(
        self,
        source: str,
        doc_type: str,
        chunk_count: int,
    ) -> Tuple[int, str, str]:
        """
        Score a source's quality and confidence level.
        """

        score = 50  # Base score

        # Document type factors
        type_scores = {
            "strategic": 15,
            "operational": 10,
            "report": 20,
            "survey": 15,
            "framework": 12,
            "general": 5,
        }
        score += type_scores.get(doc_type, 5)

        # Source name patterns (high quality indicators)
        high_quality_patterns = ["annual report", "staff survey", "audit", "report", "framework",
                                "plan", "strategy", "statistics"]
        if any(pattern in source.lower() for pattern in high_quality_patterns):
            score += 15

        # Data completeness (more chunks = more comprehensive)
        if chunk_count >= 10:
            score += 15
        elif chunk_count >= 5:
            score += 10
        elif chunk_count >= 2:
            score += 5

        # Determine confidence level and reasoning
        if score >= 85:
            confidence = "85-90%"
            reasoning = "Robust quantitative data, audited reports, or validated survey methodology"
        elif score >= 70:
            confidence = "70-80%"
            reasoning = "Good evidence base with documented sources and clear data"
        elif score >= 50:
            confidence = "50-60%"
            reasoning = "Limited data requiring inference or extrapolation from available sources"
        else:
            confidence = "Below 50%"
            reasoning = "Insufficient data for high confidence analysis"

        return score, confidence, reasoning

    def _identify_gaps(
        self,
        chunks: List[Dict],
        query: str,
        high: List[Dict],
        medium: List[Dict],
        lower: List[Dict],
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Identify critical gaps in evidence coverage.

        Returns:
            Tuple of (critical_gaps, medium_gaps, low_gaps)
        """

        critical_gaps = []
        medium_gaps = []
        low_gaps = []

        # Check for coverage balance
        total_sources = len(high) + len(medium) + len(lower)
        if len(high) == 0:
            critical_gaps.append({
                "gap": "No high-confidence sources identified",
                "severity": "CRITICAL",
                "description": "Analysis relies entirely on medium/lower confidence sources",
                "handling": "Accept lower confidence threshold; recommend validation from high-confidence sources",
                "impact": "Confidence in analysis reduced",
            })

        if len(high) + len(medium) < 3:
            critical_gaps.append({
                "gap": "Insufficient medium-high confidence sources",
                "severity": "CRITICAL",
                "description": f"Only {len(high) + len(medium)} medium-high confidence sources available",
                "handling": "Expand source pool or wait for additional data collection",
                "impact": "Analysis may miss important context",
            })

        # Workforce-specific gaps
        workforce_terms = ["workforce", "staff", "fte", "turnover", "retention", "employment"]
        has_workforce_data = any(
            any(term in chunk.get("metadata", {}).get("source", "").lower() for term in workforce_terms)
            for chunk in chunks
        )
        if "workforce" in query.lower() and not has_workforce_data:
            critical_gaps.append({
                "gap": "Workforce-specific data gaps",
                "severity": "HIGH",
                "description": "Query focuses on workforce but limited dedicated workforce data in corpus",
                "handling": "Inferring from general organizational and engagement data",
                "impact": "Workforce analysis may lack role/group specificity",
            })

        # Strategic context gaps
        if "10-year" in query.lower() or "plan" in query.lower():
            strategic_sources = [s for s in high + medium if "plan" in s["source"].lower()]
            if len(strategic_sources) == 0:
                medium_gaps.append({
                    "gap": "Limited strategic framework sources",
                    "severity": "MEDIUM",
                    "description": "Query about strategic planning but limited dedicated strategy documents",
                    "handling": "Using organizational reports and context to infer strategic alignment",
                    "impact": "Strategic analysis less detailed than ideal",
                })

        # Quantitative/qualitative balance
        quantitative_sources = [s for s in high + medium if "survey" in s["source"].lower() or
                               "report" in s["source"].lower()]
        if len(quantitative_sources) < 2:
            medium_gaps.append({
                "gap": "Limited quantitative baseline data",
                "severity": "MEDIUM",
                "description": "Few quantitative sources for metrics and benchmarking",
                "handling": "Using qualitative evidence and inferences for trends",
                "impact": "Cannot provide detailed metrics or statistical comparison",
            })

        # Age/demographic data
        age_sources = [s for s in chunks if "age" in s.get("metadata", {}).get("source", "").lower() or
                      "demographic" in s.get("metadata", {}).get("source", "").lower()]
        if len(age_sources) == 0:
            low_gaps.append({
                "gap": "Age profile and demographic data missing",
                "severity": "LOW",
                "description": "No detailed workforce age distribution or demographic analysis",
                "handling": "Applying national NHS patterns with local adjustment factor",
                "impact": "Retirement projections less accurate than ideal",
            })

        return critical_gaps, medium_gaps, low_gaps

    def _rank_collection_priorities(
        self,
        critical_gaps: List[Dict],
        medium_gaps: List[Dict],
        chunks: List[Dict],
    ) -> List[Dict]:
        """
        Rank priority order for future data collection.
        """

        priorities = []

        # High priority: Fill critical gaps
        for gap in critical_gaps:
            priorities.append({
                "priority": "HIGH",
                "gap": gap["gap"],
                "data_needed": gap["description"],
                "impact": "Critical for decision-making confidence",
                "timeline": "Immediate (0-3 months)",
            })

        # High priority: Workforce establishment analysis
        priorities.append({
            "priority": "HIGH",
            "gap": "Service-level establishment vs. actual staffing analysis",
            "data_needed": "Detailed capacity audit by business unit and service area",
            "impact": "Essential for targeted recruitment and capacity planning",
            "timeline": "Near-term (1-3 months)",
        })

        # High priority: Demographic/succession planning
        priorities.append({
            "priority": "HIGH",
            "gap": "Detailed workforce demographic and succession planning data",
            "data_needed": "Age profile, length of service, retirement eligibility by professional group",
            "impact": "Critical for strategic workforce forecasting",
            "timeline": "Near-term (1-3 months)",
        })

        # Medium priority: Skills assessment
        priorities.append({
            "priority": "MEDIUM",
            "gap": "Skills gap assessment by professional group",
            "data_needed": "Systematic assessment of current capabilities vs. required future skills",
            "impact": "Target development interventions effectively",
            "timeline": "Medium-term (3-6 months)",
        })

        # Medium priority: Digital readiness
        priorities.append({
            "priority": "MEDIUM",
            "gap": "Digital capability baseline assessment",
            "data_needed": "Role-level digital skills and readiness mapping",
            "impact": "Inform digital transformation timeline planning",
            "timeline": "Medium-term (3-6 months)",
        })

        # Medium priority: Career progression tracking
        priorities.append({
            "priority": "MEDIUM",
            "gap": "Career progression and internal promotion analysis",
            "data_needed": "Promotion rates, career pathway tracking, development programme effectiveness",
            "impact": "Support retention strategy development",
            "timeline": "Medium-term (3-6 months)",
        })

        return priorities

    def _create_enhancement_strategy(
        self,
        critical_gaps: List[Dict],
        medium_gaps: List[Dict],
        collection_priority: List[Dict],
    ) -> Dict:
        """
        Create data collection enhancement strategy.
        """

        return {
            "phase_1_immediate": {
                "timeline": "0-3 months",
                "focus": "Address critical gaps preventing confident analysis",
                "actions": [
                    "Conduct service-level workforce establishment audit",
                    "Collect detailed age/demographic workforce data",
                    "Validate key assumptions with subject matter experts",
                ],
            },
            "phase_2_near_term": {
                "timeline": "3-6 months",
                "focus": "Build comprehensive workforce analytics capability",
                "actions": [
                    "Implement recruitment pipeline tracking system",
                    "Conduct skills gap assessment across roles",
                    "Evaluate digital capability baseline",
                    "Analyze career progression and promotion patterns",
                ],
            },
            "phase_3_medium_term": {
                "timeline": "6-12 months",
                "focus": "Establish continuous improvement data systems",
                "actions": [
                    "Implement exit interview systematic collection",
                    "Develop role-level capability assessment framework",
                    "Create workforce analytics dashboard",
                    "Establish quarterly data quality reporting",
                ],
            },
            "key_metrics_to_track": [
                "Data completeness percentage by source",
                "Confidence level distribution (% high/medium/low confidence)",
                "Gap closure rate (reduction in identified gaps over time)",
                "Time-to-insight (speed of data availability)",
                "Data accuracy validation rate",
            ],
        }

    def generate_assessment_markdown(self, assessment: Dict) -> str:
        """
        Generate markdown-formatted Data Quality Assessment section.
        """

        markdown = "# DATA QUALITY ASSESSMENT\n\n"

        # High quality sources
        markdown += "## 5.1 Current Data Completeness and Reliability\n\n"
        markdown += "### High Quality Data Sources (Confidence Level: 85-90%)\n\n"
        for source in assessment["high_quality_sources"]:
            markdown += f"**{source['source']}** - {source['type']}\n"
            markdown += f"  - Confidence: {source['confidence']}\n"
            markdown += f"  - Chunks: {source['chunk_count']}\n"
            markdown += f"  - Reasoning: {source['reasoning']}\n\n"

        # Medium quality sources
        markdown += "### Medium Quality Data Sources (Confidence Level: 70-80%)\n\n"
        for source in assessment["medium_quality_sources"]:
            markdown += f"**{source['source']}** - {source['type']}\n"
            markdown += f"  - Confidence: {source['confidence']}\n"
            markdown += f"  - Chunks: {source['chunk_count']}\n"
            markdown += f"  - Reasoning: {source['reasoning']}\n\n"

        # Lower quality sources
        markdown += "### Lower Quality Data Sources (Confidence Level: 50-60%)\n\n"
        for source in assessment["lower_quality_sources"]:
            markdown += f"**{source['source']}** - {source['type']}\n"
            markdown += f"  - Confidence: {source['confidence']}\n"
            markdown += f"  - Chunks: {source['chunk_count']}\n"
            markdown += f"  - Reasoning: {source['reasoning']}\n\n"

        # Critical gaps
        markdown += "## 5.2 Data Gaps Requiring Strategic Attention\n\n"
        markdown += "### Critical Gaps\n\n"
        for gap in assessment["critical_gaps"]:
            markdown += f"- **{gap['gap']}** [{gap['severity']}]\n"
            markdown += f"  - Description: {gap['description']}\n"
            markdown += f"  - Handling: {gap['handling']}\n"
            markdown += f"  - Impact: {gap['impact']}\n\n"

        markdown += "### Medium Priority Gaps\n\n"
        for gap in assessment["medium_gaps"]:
            markdown += f"- **{gap['gap']}** [{gap['severity']}]\n"
            markdown += f"  - Description: {gap['description']}\n"
            markdown += f"  - Handling: {gap['handling']}\n\n"

        # Collection priorities
        markdown += "## 5.3 Data Collection Enhancement Strategy\n\n"
        markdown += "### Priority Order for Future Data Collection\n\n"
        for i, priority in enumerate(assessment["collection_priority"], 1):
            markdown += f"{i}. [{priority['priority']}] {priority['gap']}\n"
            markdown += f"   - Data needed: {priority['data_needed']}\n"
            markdown += f"   - Impact: {priority['impact']}\n"
            markdown += f"   - Timeline: {priority['timeline']}\n\n"

        # Enhancement strategy
        enhancement = assessment["enhancement_strategy"]
        markdown += "### Enhancement Timeline\n\n"
        for phase in ["phase_1_immediate", "phase_2_near_term", "phase_3_medium_term"]:
            phase_data = enhancement[phase]
            markdown += f"**Phase {phase[-1]}: {phase_data['timeline']}**\n\n"
            markdown += f"Focus: {phase_data['focus']}\n\n"
            markdown += "Actions:\n"
            for action in phase_data["actions"]:
                markdown += f"- {action}\n"
            markdown += "\n"

        # Key metrics
        markdown += "## 5.4 Confidence Framework and Validation Requirements\n\n"
        markdown += "### Key Metrics to Track\n\n"
        for metric in enhancement["key_metrics_to_track"]:
            markdown += f"- {metric}\n"

        return markdown
