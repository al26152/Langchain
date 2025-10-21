# Workforce Strategy Gap Analysis - Enhancements Summary

**Date:** October 21, 2025
**Status:** ✅ Complete - Ready for Testing

---

## Overview

Enhanced `analysis/workforce_strategy_gap_analysis.py` to incorporate broader macro-context analysis including PESTLE factors, strategic document anchoring, and cross-cutting theme analysis that spans all dimensions of external change.

---

## Key Enhancements

### 1. **Strategic Document Anchoring** (Lines 55-64)
Added reference dictionary to explicitly anchor analysis to:
- Assessment of priority skills to 2030 (GOV UK)
- Labour Market Outlook (CIPD 2025)
- CIPD Health and Wellbeing Report 2025
- Public Sector CIPD Report
- Leeds Health & Wellbeing Strategy
- NHS 10-Year Plan
- NHS Long-Term Workforce Plan

**Impact:** Analysis queries and prompts now reference these strategic documents as key evidence sources.

### 2. **PESTLE Framework Integration** (Lines 66-74)
Embedded six PESTLE factors with descriptions relevant to NHS workforce strategy:
- **Political**: Government priorities, policy direction, system integration, ICS leadership
- **Economic**: Labor market competitiveness, salary dynamics, funding constraints, efficiency
- **Social**: Demographic shifts, health disparities, workforce expectations, retention, wellbeing
- **Technological**: Digital transformation, legacy systems, emerging skills, AI/automation, interoperability
- **Legal**: Employment law, working time, professional standards, data protection, compliance
- **Environmental**: Net zero commitment, sustainability skills, pandemic preparedness, workplace environment

**Impact:** All analysis now explicitly considers external macro-factors.

### 3. **Enhanced Gap Analysis Prompt** (Lines 115-159)
**Additions:**
- Explicit section: `MACRO-CONTEXT CONSIDERATIONS`
- New analysis dimension: "Macro-Context Gaps" - identifying failures to account for PESTLE factors, skills trends, H&W trends, system transformation
- Enhanced evidence requirements: Multiple source types (NHS docs, labour market data, skills forecasts, H&W reports)
- Recommendations now address macro-context gaps and build resilience

**Impact:** Gap analysis moves beyond documents to address broader strategic context.

### 4. **Enhanced Missing Themes Prompt** (Lines 161-207)
**Additions:**
- Explicit PESTLE factor assessment
- Four cross-cutting macro-themes explicitly analyzed:
  - Digital Transformation (PESTLE Technological)
  - Health & Wellbeing Crisis (PESTLE Social)
  - Skills Development & Future Workforce (PESTLE Economic/Technological)
  - Sustainability & Environmental (PESTLE Environmental)
- PESTLE-specific assessment for emerging trends
- Evidence requirements: 2+ different source types

**Impact:** Missing themes analysis now contextual to macro-trends and cross-cutting challenges.

### 5. **Enhanced Evidence Synthesis Prompt** (Lines 209-257)
**Additions:**
- New section: "Strategic & Macro-Context Alignment" (including PESTLE factors, labour market trends, health/wellbeing agenda)
- Enhanced "Current State & Gap Analysis" to include macro-context amplification of gaps
- Best Practice Evidence now includes labour market insights and macro-context factor considerations
- Implementation Considerations expanded to include contingencies for policy/economic/technological changes
- New section: "Monitoring & Adaptation" - how to track emerging macro-context trends

**Impact:** Evidence synthesis now considers external trends and adaptation needs.

### 6. **New PESTLE Analysis Prompt** (Lines 259-293)
**Purpose:** Dedicated prompt for analyzing each PESTLE factor's influence on workforce strategy

**Content:**
- Factor definition & current landscape (UK healthcare context)
- Strategic implications for LCH (opportunities, threats, 2026-2031 evolution)
- Connection to 5 strategy themes (which are most affected, objective gaps)
- Recommendations for strategy robustness (adjustments, capabilities, contingencies)
- Monitoring & adaptation triggers

**Impact:** Comprehensive analysis of each external factor with strategic implications.

### 7. **New Cross-Cutting Themes Prompt** (Lines 295-337)
**Purpose:** Analyze themes that span multiple PESTLE dimensions and strategy themes

**Content:**
- Theme overview with multi-source evidence
- PESTLE dimensions analysis (6-factor assessment of each theme)
- Impact on all 5 strategy themes
- Strategy gaps relative to cross-theme
- Integrated recommendations across all themes

**Cross-Themes Identified:**
1. Digital Transformation
2. Health & Wellbeing Crisis (Retention, Burnout, Mental Health)
3. Skills Development & Future Workforce
4. System Integration & Partnership
5. Sustainability & Environmental Readiness

**Impact:** Identifies how macro-trends cut across organizational silos and require integrated responses.

### 8. **New Macro-Context Summary Prompt** (Lines 339-378)
**Purpose:** Executive-level synthesis of all macro-context findings

**Content:**
- 5-7 most significant external trends with evidence and urgency
- Strategic alignment assessment (gaps, risks)
- Capability & readiness gaps
- Prioritized recommendations (immediate 2026-2027, medium-term 2027-2030, long-term 2030-2031)
- Risk mitigation and contingency planning

**Impact:** Provides actionable strategic guidance for senior leadership.

### 9. **New Macro-Context Analysis Section in Main()** (Lines 476-551)
**Process:**
1. **Section 0A: PESTLE Factor Analysis**
   - Analyzes each of 6 PESTLE factors
   - Queries vector database for relevant context
   - Generates factor-specific analysis
   - Cites sources used

2. **Section 0B: Cross-Cutting Themes Analysis**
   - Analyzes 5 cross-cutting macro-themes
   - Retrieves broader evidence (20 docs per theme)
   - Generates theme-specific analysis
   - Identifies PESTLE interconnections

**Impact:** Analysis now includes 11-12 new in-depth analysis sections before theme-specific analysis.

### 10. **Macro-Context Passed to All Prompts** (Lines 468-474, 585, 622, 668)
- Created `format_macro_context()` helper function
- PESTLE factors formatted into readable context string
- Passed to GAP_ANALYSIS_PROMPT, MISSING_THEMES_PROMPT, and EVIDENCE_SYNTHESIS_PROMPT
- All analysis now contextually aware of 6 macro-factors

**Impact:** Every existing analysis section is enriched with macro-context awareness.

---

## Analysis Flow

### New Section Structure

```
## 0. Macro-Context Analysis: PESTLE & External Factors
  ### A. PESTLE Factor Analysis (6 factors)
    #### Political Factor
    #### Economic Factor
    #### Social Factor
    #### Technological Factor
    #### Legal Factor
    #### Environmental Factor
  ### B. Cross-Cutting Macro-Themes (5 themes)
    #### Digital Transformation
    #### Health & Wellbeing Crisis
    #### Skills Development & Future Workforce
    #### System Integration & Partnership
    #### Sustainability & Environmental Readiness

## 1. Theme Gap Analysis (ENHANCED with macro-context)
  ### Theme: People Services
  ### Theme: Inclusion
  ### Theme: Talent
  ### Theme: Staff Experience
  ### Theme: Organisation Design

## 2. Missing or Underemphasized Themes (ENHANCED with macro-context)

## 3. Evidence Synthesis by Theme (ENHANCED with macro-context)

## 4. Summary of Recommendations
```

---

## Data Sources Integrated

The enhanced analysis can now reference and synthesize from:

1. **Strategic NHS Documents** - 10-Year Plan, Long-Term Workforce Plan
2. **Labour Market Data** - CIPD Labour Market Outlook 2025
3. **Skills Forecasting** - GOV UK Priority Skills to 2030
4. **Health & Wellbeing** - CIPD H&W Report 2025
5. **Public Sector Context** - Public Sector CIPD Report
6. **Local Health Strategy** - Leeds Health & Wellbeing Strategy 2023-2030
7. **LCH Documents** - People strategy, staff surveys, operational data

---

## Expected Improvements

### Analysis Depth
- ✅ Now captures external macro-trends (PESTLE factors)
- ✅ Identifies cross-cutting themes spanning multiple dimensions
- ✅ Assesses strategy robustness against external changes
- ✅ Provides contingency and adaptation guidance
- ✅ Connects to labour market and skills forecasting

### Evidence Robustness
- ✅ Multi-source evidence synthesis (7+ source types)
- ✅ Strategic document anchoring
- ✅ Macro-trend contextualization
- ✅ Source type diversity (not just LCH docs)

### Actionability
- ✅ Clear gaps identified in macro-context coverage
- ✅ Prioritized recommendations with timelines
- ✅ Risk mitigation guidance
- ✅ Adaptation monitoring triggers

---

## Usage

### Standard Execution
```bash
python analysis/workforce_strategy_gap_analysis.py
```

### Prerequisites
1. ChromaDB populated with documents (run `ingest_pipeline.py` first)
2. OpenAI API key in `.env` file
3. All strategic documents ingested

### Output
- **workforce_strategy_gap_analysis_report.md** - Comprehensive analysis report
- Includes all 4 sections + new macro-context Section 0

---

## File Changes

**Modified:** `analysis/workforce_strategy_gap_analysis.py`

**Changes:**
- Lines 55-74: Added STRATEGIC_DOCUMENTS and PESTLE_FACTORS dictionaries
- Lines 115-378: Enhanced and new prompts (GAP_ANALYSIS, MISSING_THEMES, EVIDENCE_SYNTHESIS, PESTLE_ANALYSIS, CROSS_CUTTING_THEMES, MACRO_CONTEXT_SUMMARY)
- Lines 468-551: New macro-context analysis section in main()
- Lines 585, 622, 668: Macro-context passed to existing prompts

**Total Additions:** ~350 lines of enhanced/new code

---

## Next Steps

1. **Run the enhanced script** to generate new comprehensive analysis report
2. **Review PESTLE findings** to identify highest-risk/opportunity factors
3. **Review cross-cutting themes** to assess cross-organizational implications
4. **Review gap analysis** in context of macro-trends
5. **Use recommendations** to refine strategy 2026-2031

---

## Files Referenced

- `PESTLE_ANALYSIS_UK_HEALTHCARE_WORKFORCE.md` - High-level PESTLE template
- `ANALYSIS_ENHANCEMENTS_SUMMARY.md` - This document
- `analysis/workforce_strategy_gap_analysis.py` - Enhanced analysis script
- `workforce_strategy_gap_analysis_report.md` - Output report (generated)

