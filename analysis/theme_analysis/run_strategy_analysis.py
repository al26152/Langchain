"""
run_strategy_analysis.py

WORKFORCE STRATEGY 2026-2031 ANALYSIS RUNNER

Orchestrates the complete gap analysis process:
1. Quick theme comparison analysis (no LLM calls)
2. RAG-based gap analysis with evidence synthesis (requires API calls)
3. Combines outputs into comprehensive report

USAGE:
  python run_strategy_analysis.py [--quick-only] [--full]

OPTIONS:
  --quick-only  : Run only fast analysis (no LLM calls, useful for planning)
  --full        : Run both quick and full RAG analysis (default)
  --help        : Show this help message

COST:
  - Quick analysis: FREE
  - Full RAG analysis: ~$15-25 (GPT-4o API calls)

OUTPUT FILES:
  1. theme_transition_analysis.md        (quick analysis)
  2. workforce_strategy_gap_analysis_report.md  (full analysis)
  3. strategy_analysis_summary.md        (combined summary)
"""

import sys
import subprocess
import os
from datetime import datetime

def run_quick_analysis():
    """Run fast theme comparison analysis."""
    print("\n" + "="*70)
    print("PHASE 1: Quick Theme Comparison Analysis (No API calls)")
    print("="*70 + "\n")

    try:
        from . import theme_comparison_analysis
        theme_comparison_analysis.main()
        print("\n✓ Quick analysis complete!")
        return True
    except Exception as e:
        print(f"\n✗ Error running quick analysis: {e}")
        return False


def run_full_analysis():
    """Run full RAG-based gap analysis."""
    print("\n" + "="*70)
    print("PHASE 2: Full RAG-Based Gap Analysis (API calls required)")
    print("="*70 + "\n")

    print("This phase will:")
    print("  - Connect to ChromaDB (requires ingest_pipeline.py to have run)")
    print("  - Query all 20+ documents in your docs/ folder")
    print("  - Use GPT-4o to synthesize evidence (moderate cost)")
    print("  - Generate comprehensive gap analysis report\n")

    user_input = input("Continue with full analysis? (yes/no): ").strip().lower()
    if user_input != "yes":
        print("Skipping full analysis.")
        return False

    try:
        # Check ChromaDB exists
        if not os.path.exists("chroma_db_test"):
            print("\n✗ ChromaDB not found. Please run ingest_pipeline.py first:")
            print("   python pipeline/ingest_pipeline.py\n")
            return False

        print("Starting full analysis...\n")
        subprocess.run([sys.executable, "analysis/theme_analysis/workforce_strategy_gap_analysis.py"], check=True)
        print("\n✓ Full analysis complete!")
        return True
    except Exception as e:
        print(f"\n✗ Error running full analysis: {e}")
        return False


def create_summary_report(quick_only=False):
    """Create combined summary report."""
    print("\n" + "="*70)
    print("Creating Summary Report")
    print("="*70 + "\n")

    summary_content = f"""# Workforce Strategy 2026-2031: Analysis Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Overview

This analysis supports the development of LCH's Workforce Strategy 2026-2031 by:

1. **Comparing themes** from the previous 2021-25 strategy with proposed 2026-31 themes
2. **Identifying gaps** between proposed objectives and current NHS/Leeds strategic priorities
3. **Synthesizing evidence** from 20+ strategic documents
4. **Recommending** improvements and missing areas

---

## Files Generated

### 1. theme_transition_analysis.md
**Type:** Quick structural analysis (no API calls)

Contains:
- Mapping of how 2021-25 themes transition to 2026-31 themes
- Identification of dropped or under-emphasized objectives
- New strategic emphases in the 2026-31 strategy
- Gap analysis with recommendations

**Key Findings:**
- **2 themes potentially missing**: Leadership (standalone), System Partner (prominence)
- **3 objectives consolidations**: Resourcing→Talent, Wellbeing→Staff Experience, Foundations→People Services
- **5 new emphases**: Neighbourhood Health, 10YP alignment, ATS, Organisation of Adults, data-driven decisions

**Recommendations:**
1. Reinstate Leadership theme or explicitly embed succession planning and 360 assessments
2. Strengthen system partnership strategy given ICS/ICP priorities
3. Retain explicit objectives: hybrid working, career pathways, ARRS models
4. Ensure all themes map to NHS 10-year plan objectives

---
"""

    if not quick_only:
        summary_content += """### 2. workforce_strategy_gap_analysis_report.md
**Type:** Full RAG-based analysis with evidence synthesis (API calls)

Contains:
- Gap analysis for each of 5 proposed themes against strategic documents
- Analysis of potentially missing/underemphasized themes
- Evidence synthesis for key objectives across multiple sources
- Source citations and coverage metrics
- Strategic recommendations

**Key Features:**
- Multi-source evidence synthesis (minimum 3 sources per analysis)
- Document recency flags (RECENT, OLDER, ARCHIVAL)
- Source coverage metrics
- Alignment analysis with NHS 10-year plan and Leeds Health & Wellbeing Strategy

**Suggested Review Focus:**
1. Theme 1 (People Services) - How well do objectives align with NHS systems modernization?
2. Theme 2 (Inclusion) - Are data-driven approaches feasible and sufficient?
3. Theme 3 (Talent) - Does this adequately cover succession planning and leadership pipeline?
4. Theme 4 (Staff Experience) - Is "Organisation of Adults" the right framework for LCH?
5. Theme 5 (Organisation Design) - Does Neighbourhood Health implementation need dedicated resources?

---

### 3. strategy_analysis_summary.md
This file - a synthesis of both analyses with recommended next steps.

---

## Critical Gaps to Address

Based on theme comparison analysis:

### 1. Leadership Theme Gap
**Current State:** No standalone Leadership theme; elements in Talent theme
**Why It Matters:**
- Service transformation requires strong leadership capability
- NHS People Plan emphasizes leadership for culture change
- Succession planning critical for 5-year period

**Recommendation:**
- Reinstate as standalone theme, OR
- Add explicit objectives for leadership development, 360 assessments, mentoring

### 2. System Partner De-emphasis
**Current State:** System partnership moved from standalone theme to Organisation Design
**Why It Matters:**
- ICS/ICP integration is NHS priority
- LCH has innovative partnership models (ARRS, staff sharing)
- Risk of losing strategic focus on collaboration

**Recommendation:**
- Strengthen Organisation Design theme with explicit partnership objectives, OR
- Consider standalone theme if system integration is strategic priority

### 3. Career Pathway Development
**Current State:** Not explicitly visible in 2026-31 objectives
**Why It Matters:**
- Labour market is tight; career progression drives retention
- NHS 10-year plan requires new roles and career paths
- Previous strategy had career pathway diversity as explicit objective

**Recommendation:**
- Add explicit objective in Talent theme: "Specify and diversify career pathways for progression and retention"

### 4. Hybrid Working Model
**Current State:** Not explicitly mentioned in 2026-31 objectives
**Why It Matters:**
- Competitive differentiator for attraction and retention
- NHS moving toward hybrid as standard
- Staff expectations have changed post-pandemic

**Recommendation:**
- Add to Organisation Design or Staff Experience theme

### 5. Succession Planning and Talent Management
**Current State:** Not visible in 2026-31 objectives
**Why It Matters:**
- 5-year strategy period requires pipeline development
- Underrepresented groups require targeted development
- Risk of talent loss without clear plans

**Recommendation:**
- Add explicit objective in Talent or Leadership theme

---

## Implementation Roadmap

### Immediate (Before Strategy Approval)
1. Review this analysis with strategy sponsors
2. Decide on Leadership and System Partner themes
3. Add missing explicit objectives identified above
4. Map all objectives to NHS 10-year plan deliverables

### Phase 1 (Upon Strategy Approval)
1. Develop implementation plans for each theme
2. Define success metrics aligned with objectives
3. Identify resource requirements
4. Establish governance and monitoring framework

### Phase 2 (Year 1)
1. Launch quick-win initiatives in each theme
2. Establish baseline metrics
3. Begin evidence collection for evaluation
4. Regular progress reporting (suggested quarterly to SMT)

### Phase 3 (Years 2-5)
1. Monitor progress against metrics
2. Adjust objectives based on changing context
3. Report progress transparently (public reporting)
4. Build evidence base for next strategy cycle

---

## Recommended Questions for Strategy Sponsors

1. **On Leadership:** Should this be a standalone theme? What's the rationale for embedding in Talent?

2. **On System Partnership:** Given ICS/ICP importance, is current prominence sufficient?

3. **On 10-year Plan:** Should strategy have explicit mapping of objectives to 10YP deliverables?

4. **On Measurement:** What outcomes are most important? (Engagement, retention, diversity, service capacity?)

5. **On Emerging Areas:**
   - Digital transformation readiness?
   - Retention and career progression?
   - Equity and health disparities focus?
   - New role development and deployment?

6. **On Scope:** Are there other strategic priorities (regulatory, financial, clinical) that should influence workforce strategy?

---

## Using This Analysis

### For Strategy Development Team
- Use theme_transition_analysis.md to understand what's changed
- Use workforce_strategy_gap_analysis_report.md (if available) for evidence synthesis
- Use recommendations above to enhance objectives

### For Stakeholder Engagement
- Share theme_transition_analysis.md with service leaders for feedback
- Highlight gaps and ask for input on missing areas
- Use evidence synthesis to build business cases

### For Board Presentation
- Highlight alignment with NHS 10-year plan
- Show evidence base for proposed themes
- Present risk/gap analysis with mitigations
- Outline measurement and accountability framework

---

## Next Steps

1. **Review this summary** with strategy development team
2. **Discuss gaps** identified (especially Leadership and System Partner)
3. **Validate priorities** against stakeholder feedback
4. **Enhance objectives** based on recommendations
5. **Create detailed plans** for each theme
6. **Develop success metrics** aligned with objectives
7. **Establish governance** for delivery and monitoring

---

## Appendix: File Locations

Generated analysis files:
- `theme_transition_analysis.md` - Quick analysis of theme changes
- `workforce_strategy_gap_analysis_report.md` - Full RAG-based analysis (if run)
- `strategy_analysis_summary.md` - This summary document

Source documents analyzed:
- All files in `docs/` folder (20+ strategic documents)
- ChromaDB vectorstore in `chroma_db_test/`

Analysis scripts:
- `theme_comparison_analysis.py` - Quick theme analysis
- `workforce_strategy_gap_analysis.py` - Full RAG analysis
- `run_strategy_analysis.py` - This orchestration script

---

**Analysis complete. Ready for strategy development team review.**
"""

    if not quick_only:
        summary_content += "\n\n*Full RAG-based gap analysis report included above.*\n"
    else:
        summary_content += "\n\n*Note: Full RAG-based gap analysis was not run. Run `python workforce_strategy_gap_analysis.py` to add detailed evidence synthesis.*\n"

    output_path = "strategy_analysis_summary.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_content)

    print(f"✓ Summary report created: {output_path}")
    return True


def print_usage():
    """Print help message."""
    print(__doc__)


def main():
    """Main orchestration."""
    print("\n" + "="*70)
    print("LCH WORKFORCE STRATEGY 2026-2031 ANALYSIS ORCHESTRATOR")
    print("="*70)

    # Parse arguments
    quick_only = "--quick-only" in sys.argv
    full = "--full" in sys.argv or (not quick_only)
    help_flag = "--help" in sys.argv or "-h" in sys.argv

    if help_flag:
        print_usage()
        return

    # Run quick analysis
    quick_success = run_quick_analysis()

    # Run full analysis if requested
    full_success = True
    if full and not quick_only:
        full_success = run_full_analysis()

    # Create summary
    summary_success = create_summary_report(quick_only=quick_only and not full_success)

    # Final summary
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

    if quick_success:
        print("\n✓ Theme comparison analysis: COMPLETE")
        print("  → Review: theme_transition_analysis.md")

    if full and full_success:
        print("✓ Full RAG-based analysis: COMPLETE")
        print("  → Review: workforce_strategy_gap_analysis_report.md")

    if summary_success:
        print("✓ Summary report: CREATED")
        print("  → Review: strategy_analysis_summary.md")

    print("\n" + "="*70)
    print("Next Steps:")
    print("="*70)
    print("\n1. Review strategy_analysis_summary.md")
    print("2. Review theme_transition_analysis.md for detailed gap analysis")
    if not full_success and not quick_only:
        print("3. Run full RAG analysis when ready:")
        print("   python workforce_strategy_gap_analysis.py")
    print("\n4. Share findings with strategy development team")
    print("5. Incorporate recommendations into final strategy")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
