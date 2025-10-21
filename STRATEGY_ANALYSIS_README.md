# LCH Workforce Strategy 2026-2031 Analysis Framework

## Overview

This analysis framework helps you develop a comprehensive 5-year workforce strategy (April 2026 - March 2031) for Leeds Community Healthcare (LCH). It identifies gaps in proposed themes, synthesizes evidence from strategic documents, and recommends enhancements.

**What it does:**
- ✓ Compares 2021-25 strategy (7 themes) with 2026-31 proposed strategy (5 themes)
- ✓ Identifies missing or de-emphasized areas (e.g., Leadership, System Partnership)
- ✓ Analyzes all documents in your `docs/` folder using RAG (Retrieval Augmented Generation)
- ✓ Provides evidence synthesis from multiple sources
- ✓ Generates actionable recommendations

**Key findings at a glance:**
- Leadership theme potentially missing (recommend reinstatement)
- System Partner theme de-emphasized (recommend strengthening)
- Career pathways and succession planning not explicitly retained
- Strong alignment with NHS 10-year plan emerging

---

## Quick Start (5 minutes)

### Step 1: Run Quick Analysis (No API Calls)

```bash
python run_strategy_analysis.py --quick-only
```

This generates:
- `theme_transition_analysis.md` - Shows what changed between old and new strategy, identifies gaps

**Output:** Immediate structural analysis showing:
- How themes transitioned from 2021-25 to 2026-31
- What objectives were dropped
- Potential gaps identified
- Strategic recommendations

### Step 2: Review the Output

```bash
# Open and review
theme_transition_analysis.md
```

**Reading time:** 10-15 minutes

---

## Full Analysis (40-60 minutes, requires API calls)

### Prerequisites

1. **ChromaDB populated** - You must run this first:
   ```bash
   python ingest_pipeline.py
   ```
   This ingests all documents from `docs/` folder into ChromaDB.

2. **OpenAI API key** - Must be in `.env` file with:
   ```
   OPENAI_API_KEY=sk-...
   ```

### Run Full Analysis

```bash
python run_strategy_analysis.py --full
```

Or run phases separately:

```bash
# Phase 1: Quick analysis (free, instant)
python theme_comparison_analysis.py

# Phase 2: Full RAG-based analysis (costs $15-25, takes 10-20 minutes)
python workforce_strategy_gap_analysis.py
```

### Output Files

1. **theme_transition_analysis.md** (5-10 minutes to read)
   - Structural gap analysis
   - No evidence synthesis
   - Quick decisions

2. **workforce_strategy_gap_analysis_report.md** (30-45 minutes to read)
   - Evidence synthesis from multiple documents
   - Multi-theme analysis
   - Evidence-based recommendations
   - Source citations

3. **strategy_analysis_summary.md** (10-15 minutes to read)
   - Combined findings and recommendations
   - Implementation roadmap
   - Questions for strategy sponsors

---

## Understanding Your Proposed Strategy Themes

### New Strategy (2026-31): 5 Themes

#### 1. **People Services**
*Standardisation, efficiency, NHS systems adoption*

Objectives:
- Standardise and improve efficiency
- Embed new People Business Partnering models
- Adopt NHS systems and approaches
- Professional People skills development
- Data-driven decision making
- Enhanced ER capacity

**Questions to ask:**
- How does this differ from 2021-25 "Foundations"?
- Are NHS systems adoption timelines realistic?
- What data insights are most critical?

#### 2. **Inclusion**
*Data-driven interventions, embedded practices, equity outcomes*

Objectives:
- Data-driven targeted interventions
- Embed inclusive practices as standard
- Targeted remedial support
- Reduce disparity of experience

**Questions to ask:**
- What data will drive interventions?
- How will progress be measured?
- Adequate resources for EDI?

#### 3. **Talent**
*10YP objectives, pipelines, recruitment efficiency, training*

Objectives:
- Deliver 10-year plan objectives (apprenticeships, preceptorships)
- Support local talent pipelines
- Codesign Education, Training & Development approach
- Leverage ATS for recruitment efficiency

**Questions to ask:**
- Does this cover succession planning adequately?
- What about career pathway diversity?
- Is leadership pipeline development sufficient?
- **POTENTIAL GAP:** No explicit mention of leadership development

#### 4. **Staff Experience**
*Engagement, wellbeing, benefits, adult social care framework*

Objectives:
- Enhance staff engagement factors
- Refresh HWB and benefits offer
- Improve wellbeing outcomes
- Apply "Organisation of Adults" approach

**Questions to ask:**
- Is "Organisation of Adults" framework the right fit for LCH?
- How does this differ from 2021-25 Wellbeing theme?
- What staff engagement metrics matter most?

#### 5. **Organisation Design**
*Neighbourhood Health model, system partnership, service transformation, 10YP delivery*

Objectives:
- System partnership for Neighbourhood Health model
- Support service transformation
- Inter-organisational opportunities for People Services scale
- Workforce models supporting 10-year plan

**Questions to ask:**
- Is system partnership adequately emphasized?
- Does this cover hybrid working?
- Career pathway specification included?
- **POTENTIAL GAP:** Less emphasis on system partnership than 2021-25

---

## Key Gaps Identified

### Gap 1: Leadership Theme Missing ⚠️
**Old Strategy (2021-25):** Standalone Leadership theme
**New Strategy (2026-31):** No Leadership theme; some elements in Talent

**Why it matters:**
- NHS People Plan emphasizes leadership for culture change
- Service transformation requires strong capability
- Succession planning critical for 5-year period

**What's missing:**
- Explicit leadership development objectives
- 360-degree assessments for senior leaders
- Mentoring schemes
- Talent management and succession planning

**Recommendation:**
- Option A: Reinstate Leadership as standalone theme
- Option B: Add explicit leadership objectives to Talent theme
- Must include: 360 assessments, mentoring, succession planning, talent management

---

### Gap 2: System Partnership De-emphasized ⚠️
**Old Strategy (2021-25):** Standalone "System Partner" theme
**New Strategy (2026-31):** Embedded in "Organisation Design"

**Why it matters:**
- ICS/ICP integration is NHS priority
- LCH has innovative partnership models (ARRS, staff sharing)
- Risk of losing strategic focus

**What's missing:**
- #TeamLeeds talent pipeline development
- GP Confederation maturity support
- ARRS offer sustainability
- Cross-organisational working emphasis

**Recommendation:**
- Strengthen Organisation Design with explicit partnership objectives
- OR: Elevate to standalone theme if system integration is strategic priority
- Include: #TeamLeeds pipeline, inter-org working, primary care partnership

---

### Gap 3: Career Pathway Development
**Status:** Not explicitly visible in new objectives
**Why it matters:** Labour market tight; career progression drives retention

**Recommendation:** Add objective: "Specify and diversify career pathways for progression and retention"

---

### Gap 4: Hybrid Working Model
**Status:** Not explicitly mentioned
**Why it matters:** Competitive differentiator; staff expectations; NHS direction

**Recommendation:** Add to Organisation Design or Staff Experience

---

### Gap 5: Succession Planning
**Status:** Not visible in objectives
**Why it matters:** 5-year period requires pipeline development

**Recommendation:** Add explicit objective in Talent or Leadership theme

---

## Using the Analysis Reports

### For Strategy Development Team

**Phase 1: Understand the Gaps (30 minutes)**
1. Read `strategy_analysis_summary.md` - high-level findings
2. Read `theme_transition_analysis.md` - detailed gap analysis
3. Note questions and concerns

**Phase 2: Validate Evidence (Optional, 40 minutes)**
1. Read `workforce_strategy_gap_analysis_report.md` (if generated)
2. Review evidence synthesis sections
3. Check how documents support/challenge proposals

**Phase 3: Make Decisions (60 minutes)**
1. Discuss gaps with strategy sponsors
2. Decide on Leadership and System Partner themes
3. Add missing objectives
4. Map objectives to NHS 10YP deliverables

### For Board Presentation

**Key talking points:**
- ✓ Strategy aligns with NHS 10-year plan priorities
- ✓ Reflects local health strategy (Leeds Health & Wellbeing)
- ⚠️ Leadership development needs explicit attention
- ⚠️ System partnership may need strengthening
- → Recommendations to enhance strategy

**Use evidence synthesis** to build business cases for significant investments

### For Implementation Planning

1. Review objectives for each theme
2. Identify interdependencies
3. Map to existing programs
4. Plan quick wins (Year 1)
5. Sequence longer-term initiatives
6. Define success metrics

---

## Customizing the Analysis

### Adding New Queries

Edit `workforce_strategy_gap_analysis.py`:

```python
# Add new analysis section
print("### New Analysis: Technology Readiness\n")

query_text = "What technology readiness and digital transformation is needed for NHS workforce strategy?"
retrieved_docs = retriever.invoke(query_text)
# ... continue with analysis
```

### Changing Search Scope

Edit retrieval parameters in analysis scripts:

```python
# Increase search scope (get more documents)
retriever = vectordb.as_retriever(search_kwargs={"k": 30})  # was k=20

# Focus search (fewer, more relevant documents)
retriever = vectordb.as_retriever(search_kwargs={"k": 15})
```

### Adding Documents

1. Place new documents in `docs/` folder
2. Run: `python ingest_pipeline.py`
3. Rerun gap analysis to include new evidence

---

## Understanding the Evidence Synthesis

Each analysis section in `workforce_strategy_gap_analysis_report.md` provides:

1. **Current Coverage** - How well objectives address documented priorities
2. **Gaps Identified** - Missing areas in the documents but not objectives
3. **Evidence Base** - Which documents support each finding (minimum 3 sources)
4. **Recommendations** - Specific additions/modifications to objectives

### Reading the Citations

Example:
```
[Source: NHS England Planning framework for the NHS in England]
[Source: Leeds Health & Wellbeing Strategy 2023-2030]
[Source: LCH Trust Board Meeting Papers September 2025]
```

This means: Evidence comes from at least 3 different strategic documents with dates

---

## Implementation Roadmap

### Before Strategy Approval
- [ ] Review gap analysis reports
- [ ] Discuss Leadership and System Partner themes
- [ ] Add missing explicit objectives
- [ ] Map all objectives to NHS 10YP deliverables

### Upon Strategy Approval
- [ ] Develop detailed implementation plans
- [ ] Define success metrics for each objective
- [ ] Identify resource requirements
- [ ] Establish governance framework

### Year 1 Implementation
- [ ] Launch quick-win initiatives
- [ ] Establish baseline metrics
- [ ] Begin progress monitoring
- [ ] Report quarterly to SMT

### Years 2-5 Ongoing
- [ ] Monitor progress regularly
- [ ] Adjust objectives based on changing context
- [ ] Public transparency reporting
- [ ] Build evidence base for next strategy

---

## FAQs

### Q: Why only 5 themes in 2026-31 vs. 7 in 2021-25?

**A:** Consolidation reduces complexity and focuses effort. However, this analysis suggests some consolidation may have cost strategic focus on Leadership and System Partnership, which remain important.

---

### Q: Should I reinstate the Leadership theme?

**A:** The analysis recommends YES, because:
1. Service transformation requires strong leadership capability
2. NHS People Plan emphasizes leadership for culture change
3. Succession planning is critical for 5-year period
4. Current embedding in Talent theme may not be sufficient

Alternatively: Add explicit leadership objectives to Talent theme including succession planning, 360 assessments, mentoring.

---

### Q: How comprehensive is this analysis?

**A:**
- ✓ Compares old vs. new themes structurally
- ✓ Identifies gaps through detailed analysis
- ✓ Synthesizes evidence from 20+ documents
- ✓ Provides specific recommendations
- ✗ Does NOT replace stakeholder consultation
- ✗ Does NOT include financial or resource modeling

---

### Q: Can I run this analysis repeatedly?

**A:** Yes!
- Quick analysis: rerun anytime, no cost
- Full analysis: rerun with new documents, ~$15-25 per run

Each run will generate new files; rename outputs to preserve history:
```bash
cp theme_transition_analysis.md theme_transition_analysis_v1.md
python run_strategy_analysis.py --quick-only
```

---

### Q: What if I disagree with the recommendations?

**A:** That's valid! This analysis is one input. Use it for:
- ✓ Identifying what changed and why
- ✓ Surfacing previously unconsidered gaps
- ✓ Evidence building
- ✓ Triggering discussion

Your stakeholder expertise and strategic judgment should prevail.

---

## Troubleshooting

### "ChromaDB not found" error
**Solution:** Run ingest pipeline first
```bash
python ingest_pipeline.py
```
Wait for it to complete before running gap analysis.

### "OpenAI API key not found" error
**Solution:** Check `.env` file has `OPENAI_API_KEY=sk-...`

### Analysis takes too long
**Solution:** This is normal
- Quick analysis: instant
- Full analysis: 10-20 minutes for 5 themes + 1 emerging themes analysis
- Don't interrupt; let it complete

### Out of memory errors
**Solution:** Reduce search scope in script
```python
# Change this in analysis script
retriever = vectordb.as_retriever(search_kwargs={"k": 15})  # was k=25
```

---

## Support and Questions

For questions about:
- **Strategy development process** → Consult with strategy sponsors
- **Tool usage** → Review this README or check script comments
- **Document issues** → Check `ingest_pipeline.py` output
- **Recommendations validity** → Validate with subject matter experts

---

## Appendix: Files Generated

### Analysis Scripts (You run these)
- `run_strategy_analysis.py` - Main orchestration (start here)
- `theme_comparison_analysis.py` - Quick gap analysis
- `workforce_strategy_gap_analysis.py` - Full RAG analysis

### Output Files (Automatically generated)
- `strategy_analysis_summary.md` - Combined summary & recommendations
- `theme_transition_analysis.md` - Detailed theme comparison
- `workforce_strategy_gap_analysis_report.md` - Full evidence synthesis (if run)

### Configuration Files (Already exist)
- `new workforce strategy themes.txt` - Your proposed 2026-31 themes
- `docs/` - Strategic documents analyzed
- `chroma_db_test/` - Vector database (created by ingest_pipeline.py)

---

## Version History

- **v1.0** (Created Oct 2025) - Initial framework for 2026-31 strategy development
  - Theme comparison analysis
  - Gap identification
  - Evidence synthesis via RAG
  - Recommendations framework

---

**Last Updated:** October 2025
**Next Review:** Before strategy board approval
**Owner:** Workforce Development Team

---

*This framework is designed to support strategy development through evidence-based analysis. Use it as one input among many in your strategic planning process.*
