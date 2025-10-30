"""
synthesis_agent.py

SYNTHESIS AGENT FOR FINAL REPORT GENERATION

PURPOSE:
  Generates comprehensive final report with epistemic categorization
  (FACT/ASSUMPTION/INFERENCE), confidence scores, and gap analysis.

FEATURES:
  - Multi-iteration evidence aggregation
  - Epistemic categorization and tracking
  - Confidence score calculation
  - Structured markdown report generation
  - Source traceability
  - Gap and iteration logging

USAGE:
  from synthesis_agent import SynthesisAgent

  agent = SynthesisAgent(llm)
  report = agent.synthesize(all_evidence, all_critiques, query)
"""

import sys
import os
from typing import List, Dict, Optional
from collections import defaultdict, Counter
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_openai import ChatOpenAI

# Import configuration
try:
    from config import Config
except ImportError:
    print("[WARNING] Could not import config, using defaults")
    Config = None

# Import Entity Resolver
try:
    from analysis.entity_resolution import EntityResolver
except ImportError:
    EntityResolver = None  # Fallback if entity resolution not available


class SynthesisAgent:
    """Agent responsible for synthesizing evidence into final report."""

    def __init__(self, llm: Optional[ChatOpenAI] = None, use_entity_resolution: bool = True, max_context_chunks: Optional[int] = None):
        """
        Initialize Synthesis Agent.

        Args:
            llm: Language model for answer generation
            use_entity_resolution: Whether to normalize entity names in output (default True)
            max_context_chunks: Maximum evidence chunks to use in synthesis (from config if not provided)
        """
        # Use config for defaults
        if Config:
            default_model = Config.DEFAULT_LLM_MODEL
            default_temp = Config.DEFAULT_TEMPERATURE
            self.max_context_chunks = max_context_chunks or Config.MAX_SYNTHESIS_CHUNKS
        else:
            default_model = "gpt-4o"
            default_temp = 0.5
            self.max_context_chunks = max_context_chunks or 30  # Increased from 20

        self.llm = llm or ChatOpenAI(model=default_model, temperature=default_temp)

        # Initialize Entity Resolver if available
        self.entity_resolver = None
        if use_entity_resolution and EntityResolver is not None:
            try:
                self.entity_resolver = EntityResolver()
                print("[OK] Entity Resolver initialized for answer normalization")
            except Exception as e:
                print(f"[WARNING] Could not initialize Entity Resolver: {e}")
                self.entity_resolver = None

    def synthesize(
        self,
        query: str,
        iteration_results: List[Dict],
        final_critique: Dict,
    ) -> Dict:
        """
        Generate comprehensive synthesis from all iterations.

        Args:
            query: Original strategic question
            iteration_results: List of results from all iterations
            final_critique: Final critique from Critique Agent

        Returns:
            Dict containing:
            - answer: Synthesized answer
            - report_markdown: Full markdown report
            - confidence_score: Overall confidence (0-100)
            - epistemic_summary: Breakdown of FACT/ASSUMPTION/INFERENCE
        """
        print("\n[SYNTHESIS] Generating final report...")

        # Aggregate all evidence across iterations
        all_evidence = []
        for result in iteration_results:
            all_evidence.extend(result["evidence"])

        # Remove duplicates (same content from same source)
        unique_evidence = self._deduplicate_evidence(all_evidence)

        # Tag evidence with epistemic types
        import importlib.util
        current_dir = os.path.dirname(os.path.abspath(__file__))
        evidence_agent_path = os.path.join(current_dir, "evidence_agent.py")
        spec = importlib.util.spec_from_file_location("evidence_agent", evidence_agent_path)
        evidence_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(evidence_module)
        EvidenceAgent = evidence_module.EvidenceAgent

        temp_agent = EvidenceAgent(None, self.llm)
        tagged_evidence = temp_agent.tag_evidence_batch(unique_evidence)

        # Generate synthesized answer using LLM
        answer = self._generate_answer(query, tagged_evidence)

        # Normalize entity names in answer
        if self.entity_resolver:
            original_length = len(answer)
            answer = self.entity_resolver.normalize_text(answer, entity_types=["organizations", "services"])
            if len(answer) != original_length:
                print("[NORMALIZATION] Standardized entity names in answer")

        # Calculate confidence score
        confidence_score = self._calculate_confidence(tagged_evidence, final_critique)

        # Generate epistemic summary
        epistemic_summary = self._epistemic_summary(tagged_evidence)

        # Generate full markdown report
        report_markdown = self._generate_markdown_report(
            query,
            answer,
            tagged_evidence,
            iteration_results,
            final_critique,
            confidence_score,
            epistemic_summary,
        )

        print(f"[SYNTHESIS] [OK] Complete - Confidence: {confidence_score:.0f}%")

        return {
            "answer": answer,
            "report_markdown": report_markdown,
            "confidence_score": confidence_score,
            "epistemic_summary": epistemic_summary,
            "total_evidence_chunks": len(tagged_evidence),
            "unique_sources": len(set(e["source"] for e in tagged_evidence)),
        }

    def _deduplicate_evidence(self, evidence_list: List[Dict]) -> List[Dict]:
        """Remove duplicate evidence chunks."""
        seen = set()
        unique = []

        for evidence in evidence_list:
            # Create unique key from source + content snippet
            key = (evidence["source"], evidence["content"][:100])
            if key not in seen:
                seen.add(key)
                unique.append(evidence)

        return unique

    def generate_longform_findings(self, query: str, evidence: List[Dict], topic: str = "") -> str:
        """
        Generate 600-word long-form structured findings.

        Structure: Context (200w) -> Analysis (200w) -> Implications (200w)

        Args:
            query: Original question
            evidence: Tagged evidence chunks
            topic: Optional specific topic within the query

        Returns:
            600-word long-form markdown response
        """
        context_parts = []
        for i, e in enumerate(evidence[:self.max_context_chunks], 1):
            relevance = e.get('org_relevance', 'general').upper()
            relevance_note = e.get('relevance_note', '')
            relevance_marker = f"[{relevance}]"
            if relevance_note:
                relevance_marker += f" {relevance_note}"

            context_parts.append(
                f"[{i}] {relevance_marker}\n"
                f"    Source: {e['source']}\n"
                f"    Date: {e.get('date', 'Unknown')}\n"
                f"    Content: {e['content'][:500]}"
            )

        context = "\n\n".join(context_parts)

        prompt = f"""You are a strategic healthcare analyst synthesizing evidence into long-form findings.

TASK: Generate a 600-word long-form response structured into three sections.

STRUCTURE (EXACTLY as specified):
1. CONTEXT (200 words): Describe the background, policy landscape, and strategic context
2. ANALYSIS (200 words): Analyze the evidence, patterns, and findings
3. IMPLICATIONS (200 words): Strategic implications and what this means going forward

CRITICAL REQUIREMENTS:
- Total: EXACTLY 600 words (200 + 200 + 200)
- Each section is clearly labeled with ## headers
- Each section must be substantive and use evidence from provided sources
- Use [Source1, Source2] citations inline
- For PATTERN evidence, acknowledge: "Like other trusts..."
- For COLLABORATIVE evidence: "In collaborative initiatives..."
- For PRIMARY evidence: Direct attribution

EPISTEMIC CLARITY:
- Distinguish [FACT] from [INFERENCE]
- State assumptions explicitly
- Include caveats where appropriate

EVIDENCE:
{context}

QUESTION: {query}
{f'TOPIC FOCUS: {topic}' if topic else ''}

Generate the long-form response (exactly 600 words):"""

        response = self.llm.invoke(prompt)
        return response.content

    def _generate_answer(self, query: str, evidence: List[Dict]) -> str:
        """Generate synthesized answer with traceable findings using LLM."""
        # Build context from evidence
        context_parts = []
        # Use configurable limit (default 30, increased from 20)
        for i, e in enumerate(evidence[:self.max_context_chunks], 1):
            # Include relevance information to guide synthesis
            relevance = e.get('org_relevance', 'general').upper()
            relevance_note = e.get('relevance_note', '')
            relevance_marker = f"[{relevance}]"
            if relevance_note:
                relevance_marker += f" {relevance_note}"

            context_parts.append(
                f"[{i}] {relevance_marker}\n"
                f"    Source: {e['source']}\n"
                f"    Date: {e.get('date', 'Unknown')}\n"
                f"    Content: {e['content'][:500]}"
            )

        context = "\n\n".join(context_parts)

        prompt = f"""You are a strategic healthcare analyst synthesizing evidence from NHS documents.

TASK: Generate strategic findings with full traceability to answer the user's question.

CRITICAL INSTRUCTIONS:

1. UNDERSTAND DOCUMENT RELEVANCE:
   Each evidence item is marked with its relevance type:
   - [PRIMARY] = Directly about the target organization
   - [PATTERN] = From other organizations (indicates broader patterns)
   - [COLLABORATIVE] = Cross-organizational initiatives

   Use this to frame findings appropriately:
   - For PRIMARY evidence: Direct attribution ("LYPFT is...")
   - For PATTERN evidence: Acknowledge broader context ("Like other trusts, LYPFT...")
   - For COLLABORATIVE evidence: Joint initiative framing ("In collaborative efforts, LYPFT...")

2. IDENTIFY KEY FINDINGS (3-5 major insights)
   - Look for patterns across multiple sources
   - Identify consensus vs. contradictions
   - Focus on insights that directly answer the question
   - Use relevance markers to add nuance to your findings

3. FOR EACH FINDING, STRUCTURE AS:

   **Finding Title**

   [SYNTHESIZED] Your synthesis combining multiple sources, with inline citations [Source1, Source2].

   NOTE: If using PATTERN or COLLABORATIVE evidence, acknowledge the source type:
   - "Like other trusts, LYPFT..." (for PATTERN evidence)
   - "In collaborative initiatives, LYPFT..." (for COLLABORATIVE evidence)
   - Direct statements for PRIMARY evidence

   Supporting Evidence:
   - [FACT] "Direct quote from document"
     → Source name, specific location if available

   Strategic Implication:
   [INFERENCE] What this means in the context of the question asked.

   Basis for inference:
   - FACT: List the facts this is based on
   - ASSUMPTION: State any assumptions made (if any)
   - LOGIC: Explain the reasoning

   Caution: Any risks of over-interpretation or conditions that might invalidate this.

4. EVIDENCE TYPE DEFINITIONS:
   - [FACT] = Direct quote or specific data from authoritative source
   - [SYNTHESIZED] = Your combination of multiple facts into coherent insight
   - [INFERENCE] = Your strategic interpretation/implication

5. CRITICAL: For inferences, clearly separate what the documents STATE vs what YOU INFER.

6. Guard against over-interpretation:
   - If documents don't explicitly state something, note it as an inference
   - Include "Caution" notes when making strategic leaps
   - Acknowledge uncertainties and conditions
   - Be explicit about when using PATTERN evidence (infer from other orgs)

EVIDENCE:
{context}

QUESTION: {query}

STRATEGIC FINDINGS (structure each as shown above):"""

        response = self.llm.invoke(prompt)
        return response.content

    def _calculate_confidence(
        self,
        evidence: List[Dict],
        critique: Dict,
    ) -> float:
        """
        Calculate overall confidence score (0-100).

        Based on:
        - Quality rating from critique
        - Source count
        - Epistemic quality (FACT ratio)
        - Date freshness
        """
        score = 0

        # Quality rating (40 points)
        quality_scores = {
            "EXCELLENT": 40,
            "GOOD": 30,
            "ADEQUATE": 20,
            "WEAK": 10,
        }
        score += quality_scores.get(critique["overall_quality"], 10)

        # Source count (20 points)
        source_count = len(set(e["source"] for e in evidence))
        if source_count >= 10:
            score += 20
        elif source_count >= 7:
            score += 15
        elif source_count >= 5:
            score += 10
        else:
            score += 5

        # Epistemic quality (20 points)
        epistemic_counts = Counter(e.get("epistemic_type") for e in evidence)
        total = len(evidence)
        fact_ratio = epistemic_counts.get("FACT", 0) / total if total > 0 else 0

        if fact_ratio >= 0.4:
            score += 20
        elif fact_ratio >= 0.3:
            score += 15
        elif fact_ratio >= 0.2:
            score += 10
        else:
            score += 5

        # Date freshness (20 points)
        recent_count = sum(1 for e in evidence if self._is_recent(e.get("date")))
        recent_ratio = recent_count / total if total > 0 else 0

        if recent_ratio >= 0.5:
            score += 20
        elif recent_ratio >= 0.3:
            score += 15
        else:
            score += 10

        return min(score, 100)

    def _is_recent(self, date_str: Optional[str]) -> bool:
        """Check if date is within last 2 years."""
        if not date_str:
            return False

        try:
            doc_date = datetime.strptime(date_str, "%Y-%m-%d")
            years_old = (datetime.now() - doc_date).days / 365.25
            return years_old < 2
        except:
            return False

    def _epistemic_summary(self, evidence: List[Dict]) -> Dict:
        """Generate epistemic breakdown summary."""
        epistemic_counts = Counter(e.get("epistemic_type") for e in evidence)
        total = len(evidence)

        facts = [e for e in evidence if e.get("epistemic_type") == "FACT"]
        assumptions = [e for e in evidence if e.get("epistemic_type") == "ASSUMPTION"]
        inferences = [e for e in evidence if e.get("epistemic_type") == "INFERENCE"]

        return {
            "total_chunks": total,
            "fact_count": len(facts),
            "assumption_count": len(assumptions),
            "inference_count": len(inferences),
            "fact_ratio": len(facts) / total if total > 0 else 0,
            "facts": facts[:5],  # Top 5 facts
            "assumptions": assumptions[:5],  # Top 5 assumptions
            "inferences": inferences[:5],  # Top 5 inferences
        }

    def _generate_markdown_report(
        self,
        query: str,
        answer: str,
        evidence: List[Dict],
        iteration_results: List[Dict],
        final_critique: Dict,
        confidence_score: float,
        epistemic_summary: Dict,
    ) -> str:
        """Generate comprehensive markdown report."""

        # Confidence rating
        if confidence_score >= 80:
            confidence_rating = "EXCELLENT"
        elif confidence_score >= 65:
            confidence_rating = "GOOD"
        elif confidence_score >= 50:
            confidence_rating = "ADEQUATE"
        else:
            confidence_rating = "WEAK"

        # Unique sources
        unique_sources = sorted(set(e["source"] for e in evidence))
        total_docs = 30  # Known from system

        # Date distribution
        recent = sum(1 for e in evidence if self._is_recent(e.get("date")))
        total = len(evidence)
        recent_percent = (recent / total * 100) if total > 0 else 0

        # Build report
        report = f"""# Multi-Agent Strategic Analysis Report

## Question
**{query}**

---

## Confidence Assessment

| Metric | Value | Rating |
|--------|-------|--------|
| **Overall Confidence** | {confidence_score:.0f}% | **{confidence_rating}** |
| **Sources Consulted** | {len(unique_sources)}/{total_docs} documents | {(len(unique_sources)/total_docs*100):.0f}% coverage |
| **Evidence Chunks** | {len(evidence)} unique chunks | - |
| **Recent Evidence** | {recent_percent:.0f}% from 2023-2025 | {'[FRESH]' if recent_percent > 50 else '[AGING]'} |
| **Iterations** | {len(iteration_results)} iterations | {'[CONVERGED]' if final_critique.get('convergence_detected') else '[IN PROGRESS]'} |

---

## Strategic Findings

**Traceability Legend**:
- **[FACT]** = Direct quote/data from source document
- **[SYNTHESIZED]** = Multiple facts combined into coherent insight
- **[INFERENCE]** = Strategic interpretation/implication

{answer}

---

## Epistemic Analysis

Understanding what we **know** vs what we **assume** vs what we **infer**:

### Definitions
- **FACT**: Direct statement from authoritative source (verified data, published statistics, official statements)
- **ASSUMPTION**: Reasonable extrapolation based on trends or patterns (e.g., "turnover will remain at 15%")
- **INFERENCE**: Logical conclusion drawn from combining facts and/or assumptions (e.g., "therefore we need 750 recruits")

| Type | Count | Ratio |
|------|-------|-------|
| **FACT** | {epistemic_summary['fact_count']} | {epistemic_summary['fact_ratio']:.1%} |
| **ASSUMPTION** | {epistemic_summary['assumption_count']} | {(epistemic_summary['assumption_count']/total*100):.0f}% |
| **INFERENCE** | {epistemic_summary['inference_count']} | {(epistemic_summary['inference_count']/total*100):.0f}% |

**Quality Assessment**: {"Strong evidence base (fact-heavy)" if epistemic_summary['fact_ratio'] > 0.3 else "[WARNING] Inference-heavy - findings based on interpretations rather than hard data. Recommend searching for official reports with verified statistics." if epistemic_summary['fact_ratio'] < 0.2 else "Balanced mix of facts and reasoning"}

### Key Facts (Verified Data)

{f"Found {epistemic_summary['fact_count']} verified facts from authoritative sources:" if epistemic_summary['fact_count'] > 0 else "[ALERT] No verified facts found - all evidence is inference-based. Recommend searching for official reports with hard data."}
"""

        # Add top facts
        if epistemic_summary.get("facts"):
            for i, fact in enumerate(epistemic_summary.get("facts", [])[:5], 1):
                report += f"\n{i}. **{fact['content'][:300]}**\n"
                report += f"   - Source: `{fact['source']}` ({fact.get('date', 'Unknown date')})\n"
                report += f"   - Type: Direct statement from document\n"
                report += f"   - Confidence: {fact.get('confidence', 0.5):.0%}\n"
        else:
            report += "\nNo direct facts identified. All evidence consists of inferences or assumptions.\n"

        report += "\n### Key Assumptions (Extrapolations)\n\n"

        if epistemic_summary.get("assumptions"):
            report += "Assumptions are reasonable extrapolations based on trends or patterns:\n"
            for i, assumption in enumerate(epistemic_summary.get("assumptions", [])[:5], 1):
                report += f"\n{i}. **{assumption['content'][:300]}**\n"
                report += f"   - Source: `{assumption['source']}`\n"
                report += f"   - Basis: Trend/pattern identified in source document\n"
                report += f"   - Confidence: {assumption.get('confidence', 0.5):.0%}\n"
                report += f"   - Risk: Assumption may not hold if conditions change\n"
        else:
            report += "No explicit assumptions identified.\n"

        report += "\n### Key Inferences (Logical Conclusions)\n\n"

        if epistemic_summary.get("inferences"):
            report += """Inferences are conclusions or interpretations found in the source documents.
These are NOT direct facts but rather reasoning/analysis presented by the source authors.

**Note**: Current system identifies text that contains inferential language (e.g., "therefore", "implies", "suggests").
For explicit reasoning chains (e.g., "Given X and Y, we conclude Z"), future enhancement needed.

"""
            for i, inference in enumerate(epistemic_summary.get("inferences", [])[:5], 1):
                report += f"\n{i}. **{inference['content'][:300]}**\n"
                report += f"   - Source document: `{inference['source']}`\n"
                report += f"   - Type: Conclusion/interpretation from source\n"
                report += f"   - Confidence: {inference.get('confidence', 0.5):.0%}\n"
                report += f"   - Reliability: Depends on source's methodology and evidence base\n"
        else:
            report += "No inferences identified.\n"

        report += "\n---\n\n## Sources Consulted\n\n"

        # List all unique sources with metadata
        source_details = defaultdict(lambda: {"chunks": 0, "date": None})
        for e in evidence:
            source = e["source"]
            source_details[source]["chunks"] += 1
            if not source_details[source]["date"] and e.get("date"):
                source_details[source]["date"] = e["date"]

        for i, source in enumerate(unique_sources, 1):
            details = source_details[source]
            date_str = details["date"] or "Unknown date"
            recent_flag = "[RECENT]" if self._is_recent(details["date"]) else "[OLDER]"
            report += f"{i}. {recent_flag} `{source}` - {date_str} ({details['chunks']} chunks)\n"

        report += "\n---\n\n## Gaps Identified\n\n"
        report += """**Gap Severity Levels**:
- **HIGH**: Critical missing evidence - findings may be unreliable without this
- **MEDIUM**: Evidence exists but coverage could be improved for confidence
- **LOW**: Minor gaps - current evidence is adequate but could be enhanced

"""

        # List gaps from final critique
        gaps = final_critique.get("gaps", [])
        if gaps:
            high_gaps = [g for g in gaps if g.get("severity") == "HIGH"]
            medium_gaps = [g for g in gaps if g.get("severity") == "MEDIUM"]
            low_gaps = [g for g in gaps if g.get("severity") == "LOW"]

            if high_gaps:
                report += "### High Priority Gaps\n\n"
                for gap in high_gaps:
                    report += f"- [HIGH] **{gap.get('message')}**\n"
                    report += f"  - Action: {gap.get('action')}\n\n"

            if medium_gaps:
                report += "### Medium Priority Gaps\n\n"
                for gap in medium_gaps:
                    report += f"- [MEDIUM] {gap.get('message')}\n"
                    report += f"  - Action: {gap.get('action')}\n\n"

            if low_gaps:
                report += "### Low Priority Gaps\n\n"
                for gap in low_gaps:
                    report += f"- [LOW] {gap.get('message')}\n\n"
        else:
            report += "[OK] No significant gaps identified.\n\n"

        report += "---\n\n## Iteration Log\n\n"

        # Log each iteration
        for i, result in enumerate(iteration_results, 1):
            metrics = result.get("metrics", {})
            report += f"### Iteration {i}\n"
            report += f"- Sources: {metrics.get('source_count', 0)} documents\n"
            report += f"- Chunks: {metrics.get('total_chunks', 0)}\n"
            report += f"- Coverage: {metrics.get('coverage_percent', 0):.1f}%\n"

            iteration_gaps = result.get("gaps", [])
            if iteration_gaps:
                report += f"- Gaps detected: {len(iteration_gaps)}\n"
                for gap in iteration_gaps[:2]:  # Show top 2 gaps
                    report += f"  - {gap.get('message')}\n"

            report += "\n"

        report += f"**Final Quality:** {final_critique['overall_quality']} "
        report += f"({'[CONVERGED]' if final_critique.get('convergence_detected') else '[CONTINUED]'})\n\n"

        report += "---\n\n## Recommendations\n\n"

        recommendations = final_critique.get("recommendations", [])
        if recommendations:
            for rec in recommendations:
                report += f"- {rec}\n"
        else:
            report += "[OK] Evidence quality is sufficient for strategic decision-making.\n"

        report += f"\n---\n\n*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return report
