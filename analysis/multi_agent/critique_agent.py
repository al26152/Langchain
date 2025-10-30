"""
critique_agent.py

CRITIQUE AGENT FOR GAP DETECTION AND QUALITY ASSESSMENT

PURPOSE:
  Analyzes evidence from Evidence Agent and identifies gaps, weaknesses,
  and areas needing refinement. Decides whether to continue iterations.

FEATURES:
  - Evidence coverage analysis
  - Epistemic quality assessment (FACT/ASSUMPTION/INFERENCE ratios)
  - Gap detection across multiple dimensions
  - Convergence detection (diminishing returns)
  - Stopping criteria recommendations

USAGE:
  from critique_agent import CritiqueAgent

  agent = CritiqueAgent()
  critique = agent.analyze(evidence_result, iteration_history)
"""

import sys
import os
from typing import List, Dict, Optional
from collections import Counter

# Add project root to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import configuration
try:
    from config import Config
except ImportError:
    # Fallback if config not available
    print("[WARNING] Could not import config, using defaults")
    Config = None


class CritiqueAgent:
    """Agent responsible for critiquing evidence and identifying gaps."""

    def __init__(
        self,
        min_sources: Optional[int] = None,
        min_coverage_percent: Optional[float] = None,
        min_recent_percent: Optional[float] = None,
        max_iterations: Optional[int] = None,
        excellent_threshold: Optional[int] = None,
        good_threshold: Optional[int] = None,
        adequate_threshold: Optional[int] = None,
    ):
        """
        Initialize Critique Agent.

        All parameters are optional and will use config.py defaults if not provided.
        This allows easy customization while maintaining centralized configuration.

        Args:
            min_sources: Minimum unique sources for ADEQUATE coverage
            min_coverage_percent: Minimum % of total documents for ADEQUATE
            min_recent_percent: Minimum % of recent evidence (<1 year)
            max_iterations: Maximum iterations before forcing stop
            excellent_threshold: Score threshold for EXCELLENT rating
            good_threshold: Score threshold for GOOD rating
            adequate_threshold: Score threshold for ADEQUATE rating
        """
        # Use config defaults if values not provided
        if Config:
            self.min_sources = min_sources or Config.MIN_SOURCES
            self.min_coverage_percent = min_coverage_percent or Config.MIN_COVERAGE_PERCENT
            self.min_recent_percent = min_recent_percent or Config.MIN_RECENT_PERCENT
            self.max_iterations = max_iterations or Config.MAX_ITERATIONS
            self.excellent_threshold = excellent_threshold or Config.EXCELLENT_THRESHOLD
            self.good_threshold = good_threshold or Config.GOOD_THRESHOLD
            self.adequate_threshold = adequate_threshold or Config.ADEQUATE_THRESHOLD
        else:
            # Fallback to old defaults if config not available
            self.min_sources = min_sources or 5
            self.min_coverage_percent = min_coverage_percent or 15.0
            self.min_recent_percent = min_recent_percent or 30.0
            self.max_iterations = max_iterations or 5
            self.excellent_threshold = excellent_threshold or 90  # Updated from 80
            self.good_threshold = good_threshold or 75  # Updated from 60
            self.adequate_threshold = adequate_threshold or 50  # Updated from 40

    def validate_document_selection(
        self,
        selected_documents: List[str],
        query: str,
        total_documents: int,
        web_context: Optional[Dict] = None,
    ) -> Dict:
        """
        Validate document selection from DocumentSelectorAgent.

        Args:
            selected_documents: List of selected document IDs
            query: Original query
            total_documents: Total documents in corpus
            web_context: Context from WebLookupAgent (themes, priorities)

        Returns:
            Dict containing:
            - selection_adequate: Boolean (is selection sufficient?)
            - coverage_percent: What % of corpus was selected
            - recommendation: Action to take (PROCEED / EXPAND / REVIEW)
            - rationale: Why this recommendation
        """
        selection_size = len(selected_documents)
        coverage_percent = (selection_size / total_documents) * 100

        # Assess selection adequacy
        recommendation = "PROCEED"
        rationale = f"Selected {selection_size} of {total_documents} documents ({coverage_percent:.1f}%)"

        # Check if selection might be too narrow
        if coverage_percent < 30:  # Less than 30% of corpus
            recommendation = "CAUTION"
            rationale += " - Selection is narrow; may miss important context"

        if coverage_percent < 15:  # Less than 15% of corpus
            recommendation = "EXPAND"
            rationale += " - Selection is too narrow; recommend expanding before RAG search"

        # If web context provided, validate thematic alignment
        if web_context and web_context.get("key_themes"):
            themes = web_context["key_themes"]
            # Note: This is simplified - could be enhanced with semantic matching
            rationale += f"; Themes: {', '.join(themes[:2])}"

        return {
            "selection_adequate": recommendation in ["PROCEED", "CAUTION"],
            "coverage_percent": coverage_percent,
            "selection_size": selection_size,
            "total_documents": total_documents,
            "recommendation": recommendation,
            "rationale": rationale,
        }

    def analyze(
        self,
        evidence_result: Dict,
        iteration_history: List[Dict],
        query: str,
    ) -> Dict:
        """
        Analyze evidence and provide critique.

        Args:
            evidence_result: Result from Evidence Agent
            iteration_history: List of previous iteration results
            query: Original query

        Returns:
            Dict containing:
            - overall_quality: WEAK/ADEQUATE/GOOD/EXCELLENT
            - gaps: List of identified gaps
            - continue_iteration: Boolean (should we continue?)
            - convergence_detected: Boolean
            - recommendations: List of improvement actions
        """
        iteration_num = evidence_result["iteration"]
        metrics = evidence_result["metrics"]
        evidence = evidence_result["evidence"]
        existing_gaps = evidence_result["gaps"]

        print(f"\n[ITERATION {iteration_num}] Critique Agent: Analyzing evidence quality...")

        # 1. Assess overall coverage quality
        quality_assessment = self._assess_coverage_quality(metrics)

        # 2. Analyze epistemic quality
        epistemic_analysis = self._analyze_epistemic_quality(evidence)

        # 3. Detect convergence (are we still improving?)
        convergence_detected = self._detect_convergence(iteration_history, metrics)

        # 4. Aggregate all gaps
        all_gaps = existing_gaps + self._additional_gaps(
            metrics, epistemic_analysis, quality_assessment
        )

        # 5. Decide whether to continue
        continue_iteration = self._should_continue(
            iteration_num,
            quality_assessment,
            convergence_detected,
            all_gaps,
        )

        # 6. Generate recommendations
        recommendations = self._generate_recommendations(
            all_gaps, quality_assessment, convergence_detected
        )

        # Log critique
        print(f"[ITERATION {iteration_num}] Quality: {quality_assessment['rating']}")
        print(f"[ITERATION {iteration_num}] Sources: {metrics['source_count']} ({metrics['coverage_percent']:.1f}%)")
        print(f"[ITERATION {iteration_num}] Gaps: {len(all_gaps)} identified")

        if convergence_detected:
            print(f"[ITERATION {iteration_num}] [OK] CONVERGENCE DETECTED (diminishing returns)")

        if continue_iteration:
            print(f"[ITERATION {iteration_num}] -> Triggering Iteration {iteration_num + 1}")
        else:
            print(f"[ITERATION {iteration_num}] [OK] STOPPING (sufficient quality or max iterations)")

        return {
            "overall_quality": quality_assessment["rating"],
            "quality_details": quality_assessment,
            "epistemic_analysis": epistemic_analysis,
            "gaps": all_gaps,
            "convergence_detected": convergence_detected,
            "continue_iteration": continue_iteration,
            "recommendations": recommendations,
            "iteration": iteration_num,
        }

    def _assess_coverage_quality(self, metrics: Dict) -> Dict:
        """
        Assess overall coverage quality.

        Returns rating: WEAK/ADEQUATE/GOOD/EXCELLENT
        """
        source_count = metrics["source_count"]
        coverage_percent = metrics["coverage_percent"]
        theme_count = metrics["theme_count"]

        # Calculate score
        score = 0

        # Source count scoring
        if source_count >= 10:
            score += 40
        elif source_count >= 7:
            score += 30
        elif source_count >= 5:
            score += 20
        else:
            score += 10

        # Coverage percent scoring
        if coverage_percent >= 30:
            score += 30
        elif coverage_percent >= 20:
            score += 20
        elif coverage_percent >= 10:
            score += 10

        # Theme diversity scoring
        if theme_count >= 4:
            score += 20
        elif theme_count >= 3:
            score += 15
        elif theme_count >= 2:
            score += 10

        # Date distribution scoring
        date_dist = metrics["date_distribution"]
        total_dated = sum(date_dist.values()) - date_dist.get("unknown", 0)
        if total_dated > 0:
            recent_percent = (date_dist.get("recent", 0) / total_dated) * 100
            if recent_percent >= 50:
                score += 10
            elif recent_percent >= 30:
                score += 5

        # Rating based on score (using config thresholds)
        if score >= self.excellent_threshold:
            rating = "EXCELLENT"
        elif score >= self.good_threshold:
            rating = "GOOD"
        elif score >= self.adequate_threshold:
            rating = "ADEQUATE"
        else:
            rating = "WEAK"

        return {
            "rating": rating,
            "score": score,
            "source_count": source_count,
            "coverage_percent": coverage_percent,
            "theme_count": theme_count,
        }

    def _analyze_epistemic_quality(self, evidence: List[Dict]) -> Dict:
        """Analyze distribution of FACT/ASSUMPTION/INFERENCE."""
        if not evidence:
            return {
                "fact_count": 0,
                "assumption_count": 0,
                "inference_count": 0,
                "fact_ratio": 0.0,
                "warning": "No evidence classified yet",
            }

        # Count epistemic types
        epistemic_counts = Counter(e.get("epistemic_type") for e in evidence)

        fact_count = epistemic_counts.get("FACT", 0)
        assumption_count = epistemic_counts.get("ASSUMPTION", 0)
        inference_count = epistemic_counts.get("INFERENCE", 0)
        total = len(evidence)

        fact_ratio = fact_count / total if total > 0 else 0

        # Assess quality
        warnings = []
        if fact_count < 3:
            warnings.append("Insufficient facts - need more hard data")
        if inference_count > fact_count * 2:
            warnings.append("Too many inferences relative to facts")
        if assumption_count > fact_count:
            warnings.append("Assumptions outnumber facts - validate assumptions")

        return {
            "fact_count": fact_count,
            "assumption_count": assumption_count,
            "inference_count": inference_count,
            "fact_ratio": fact_ratio,
            "warnings": warnings,
        }

    def _detect_convergence(
        self,
        iteration_history: List[Dict],
        current_metrics: Dict,
    ) -> bool:
        """
        Detect if we're experiencing diminishing returns.

        Convergence detected if:
        - Source count increased by less than 20% from previous iteration
        - Less than 2 new sources added
        """
        if len(iteration_history) < 1:
            return False  # Can't detect convergence on first iteration

        previous = iteration_history[-1]
        prev_metrics = previous.get("metrics", {})
        prev_source_count = prev_metrics.get("source_count", 0)
        current_source_count = current_metrics.get("source_count", 0)

        # Calculate improvement
        new_sources = current_source_count - prev_source_count
        if prev_source_count > 0:
            improvement_percent = (new_sources / prev_source_count) * 100
        else:
            improvement_percent = 100

        # Convergence criteria
        if new_sources < 2 and improvement_percent < 20:
            return True

        return False

    def _additional_gaps(
        self,
        metrics: Dict,
        epistemic_analysis: Dict,
        quality_assessment: Dict,
    ) -> List[Dict]:
        """Identify additional gaps beyond what Evidence Agent found."""
        gaps = []

        # Epistemic quality gaps
        if epistemic_analysis.get("warnings"):
            for warning in epistemic_analysis["warnings"]:
                gaps.append({
                    "type": "epistemic_quality",
                    "severity": "MEDIUM",
                    "message": warning,
                    "action": "Search for more factual sources (reports, statistics)",
                })

        # Overall quality gaps
        if quality_assessment["rating"] == "WEAK":
            gaps.append({
                "type": "overall_weak_coverage",
                "severity": "HIGH",
                "message": f"Overall coverage quality is WEAK (score: {quality_assessment['score']}/100)",
                "action": "Significantly expand search scope",
            })

        return gaps

    def _should_continue(
        self,
        iteration_num: int,
        quality_assessment: Dict,
        convergence_detected: bool,
        gaps: List[Dict],
    ) -> bool:
        """
        Decide whether to continue iterations.

        Stop if:
        - Max iterations reached
        - Quality is GOOD or EXCELLENT AND convergence detected
        - Quality is EXCELLENT regardless of convergence
        """
        # Hard stop at max iterations
        if iteration_num >= self.max_iterations:
            return False

        # Stop if excellent quality
        if quality_assessment["rating"] == "EXCELLENT":
            return False

        # Stop if good quality AND converged
        if quality_assessment["rating"] == "GOOD" and convergence_detected:
            return False

        # Stop if adequate quality, converged, AND no HIGH severity gaps
        high_severity_gaps = [g for g in gaps if g.get("severity") == "HIGH"]
        if (quality_assessment["rating"] == "ADEQUATE" and
            convergence_detected and
            len(high_severity_gaps) == 0):
            return False

        # Continue otherwise
        return True

    def generate_document_expansion_gaps(
        self,
        gaps: List[Dict],
    ) -> List[Dict]:
        """
        Generate gaps specifically for document expansion.

        These gaps can be passed to DocumentSelectorAgent.expand_selection()
        to request additional documents based on identified gaps.

        Args:
            gaps: Gaps from the analysis

        Returns:
            List of expansion gaps for DocumentSelectorAgent
        """
        expansion_gaps = []

        # Extract gap types that DocumentSelectorAgent can address
        for gap in gaps:
            gap_type = gap.get("type", "")

            # LOW_SOURCE_COVERAGE -> request more documents
            if gap_type in ["low_source_coverage", "moderate_source_coverage"]:
                expansion_gaps.append({
                    "type": "low_document_coverage",
                    "severity": gap.get("severity", "MEDIUM"),
                    "reason": gap.get("message", "Need more documents"),
                    "action": "Expand document selection to improve coverage",
                })

            # MISSING_THEME -> request documents about missing themes
            elif gap_type == "low_theme_diversity":
                expansion_gaps.append({
                    "type": "missing_themes",
                    "severity": "MEDIUM",
                    "reason": f"Evidence spans only {gap.get('metric', 1)} theme(s)",
                    "missing_themes": ["partnership", "finance", "innovation"],  # Default expansion themes
                })

            # INSUFFICIENT_RECENT_EVIDENCE -> request recent documents
            elif gap_type == "insufficient_recent_evidence":
                expansion_gaps.append({
                    "type": "missing_time_period",
                    "severity": "MEDIUM",
                    "reason": "Need more recent evidence (2024-2025)",
                    "missing_time_period": "2024",
                })

        return expansion_gaps

    def _generate_recommendations(
        self,
        gaps: List[Dict],
        quality_assessment: Dict,
        convergence_detected: bool,
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # High-priority gaps
        high_gaps = [g for g in gaps if g.get("severity") == "HIGH"]
        for gap in high_gaps:
            recommendations.append(f"[HIGH] {gap.get('action', gap.get('message'))}")

        # Medium-priority gaps
        medium_gaps = [g for g in gaps if g.get("severity") == "MEDIUM"]
        for gap in medium_gaps[:3]:  # Limit to top 3
            recommendations.append(f"[MEDIUM] {gap.get('action', gap.get('message'))}")

        # Quality-based recommendations
        if quality_assessment["rating"] == "WEAK":
            recommendations.append("[QUALITY] Expand search to broader topics and more documents")

        if convergence_detected and quality_assessment["rating"] != "GOOD":
            recommendations.append("[CONVERGENCE] Search strategy may be exhausted - consider different query angles")

        return recommendations
