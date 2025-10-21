"""
workforce_strategy_gap_analysis.py

WORKFORCE STRATEGY 2026-2031 GAP ANALYSIS PIPELINE

PURPOSE:
  Performs comprehensive gap analysis for the new 5-year workforce strategy (2026-2031)
  by analyzing all available strategic documents against proposed themes and objectives.

  Identifies:
  1. Gaps in current themes against NHS/Leeds priorities
  2. Missing themes (e.g., Leadership, System Partner prominence)
  3. Evidence synthesis from multiple sources for each theme
  4. Alignment with NHS 10-year plan and local strategies

THEMES TO ANALYZE:
  1. People Services - Standardisation, efficiency, NHS systems alignment
  2. Inclusion - Data-driven interventions, inclusive practices
  3. Talent - 10YP objectives, pipelines, recruitment efficiency
  4. Staff Experience - Engagement, wellbeing, staff benefits
  5. Organisation Design - Neighbourhood health model, system partnership

DELIVERABLES:
  - workforce_strategy_gap_analysis_report.md: Comprehensive analysis
  - Recommendations for missing/emerging themes
  - Source coverage and evidence metrics

USAGE:
  python workforce_strategy_gap_analysis.py

PREREQUISITES:
  - Must run ingest_pipeline.py first to populate ChromaDB
  - Requires OpenAI API key in .env
"""

import os
import sys
from io import StringIO
from collections import defaultdict
from datetime import datetime, timedelta

# Add parent directory to path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate

from utils.utils import auto_tag  # Ensures .env is loaded

# --- CONFIGURATION ——————————————————————————————————————————————————

STORE_DIR = "chroma_db_test"

# Strategic documents to anchor analysis
STRATEGIC_DOCUMENTS = {
    "skills_trends": "Assessment of priority skills to 2030 GOV UK",
    "labor_market": "Labour Market Outlook CIPD 2025",
    "health_wellbeing": "CIPD Health and Wellbeing Report 2025",
    "public_sector": "Public Sector CIPD Report",
    "local_health": "leeds health wellbeing strategy 2023-2030",
    "nhs_plan": "NHS 10-Year Plan",
    "nhs_workforce": "NHS Long-Term Workforce Plan"
}

# PESTLE Analysis Factors
PESTLE_FACTORS = {
    "Political": "Government priorities, policy direction, system integration requirements, ICS leadership",
    "Economic": "Labor market competitiveness, salary dynamics, funding constraints, cost-benefit efficiency",
    "Social": "Demographic shifts, health disparities, workforce expectations, retention challenges, wellbeing trends",
    "Technological": "Digital transformation, legacy systems, emerging tech skills, AI/automation, system interoperability",
    "Legal": "Employment law, working time regulations, professional standards, data protection, compliance",
    "Environmental": "Net zero commitment, sustainability skills, pandemic preparedness, workplace environment"
}

# --- NEW STRATEGY THEMES AND OBJECTIVES ——————————————————————————

STRATEGY_THEMES = {
    "People Services": [
        "Increase standardisation and efficiency",
        "Embed new approaches to People Business Partnering and People Projects",
        "Adopt and embed new NHS models and systems",
        "Broaden opportunities for professional People skills development",
        "Use data reporting and insights to inform People and Trust decision-making",
        "Equip employee relations services to handle increased casework complexity and volume"
    ],
    "Inclusion": [
        "Design and target interventions based on data with insight from Staff Networks",
        "Embed inclusive practices as standard practices",
        "Target remedial support and interventions to areas falling below inclusive expectations",
        "Reduce disparity of experience"
    ],
    "Talent": [
        "Deliver 10YP objectives (apprenticeships, preceptorships etc)",
        "Support talent pipelines in local communities",
        "Codesign refreshed approach to Education, Training & Development at LCH",
        "Leverage benefits of ATS to deliver greater recruitment process efficiency"
    ],
    "Staff Experience": [
        "Enhance factors underpinning high Staff Engagement",
        "Assess and refresh local HWB and staff benefits offer against staff needs and expectations",
        "Improve Wellbeing at Work procedural delivery and outcomes",
        "Support staff and managers to apply 'Organisation of Adults' approach"
    ],
    "Organisation Design": [
        "Work in system partnership to implement Neighbourhood Health model",
        "Provide support and skills development to enhance service transformation",
        "Identify and develop inter-organisational opportunities to offer People Services at scale",
        "Provide support to delivery of workforce models and planning to deliver NHS 10YP"
    ]
}

# --- STRATEGIC QUERY PROMPTS ———————————————————————————————————————

GAP_ANALYSIS_PROMPT = """You are an AI specialist in NHS workforce strategy development for 2026-2031.

Your task is to analyze whether the proposed strategy theme and objectives are sufficiently ambitious and comprehensive
given current NHS priorities, Leeds health needs, emerging workforce challenges, AND the broader macro-context.

THEME: {theme}

PROPOSED OBJECTIVES:
{objectives}

MACRO-CONTEXT CONSIDERATIONS:
{macro_context}

CONTEXT FROM STRATEGIC DOCUMENTS:
{context}

AVAILABLE SOURCES: {available_sources}

Your analysis should:

1. **Current Coverage**: Assess how well the proposed objectives address:
   - NHS 10-Year Plan priorities and the broader PESTLE context
   - Local Leeds health and wellbeing needs
   - Emerging macro-trends in skills, labor market, and health/wellbeing

2. **Macro-Context Gaps**: Identify specific areas where objectives fail to account for:
   - PESTLE factors (Political, Economic, Social, Technological, Legal, Environmental)
   - Skills trends and future labor market demands
   - Health and wellbeing trends affecting workforce expectations and capability
   - System-wide transformation requirements

3. **Evidence Base**: Cite specific evidence from MULTIPLE SOURCE TYPES:
   - Strategic NHS documents
   - Labour market and skills forecasting (CIPD, GOV UK)
   - Health and wellbeing reports
   - Local Leeds health priorities
   - Show why macro-context gaps matter and impact on strategy effectiveness

4. **Recommendations**: Suggest specific additions or modifications that would:
   - Address identified macro-context gaps
   - Better align with PESTLE factors relevant to this theme
   - Anticipate 2-3 year emerging trends
   - Build resilience against identified risks

Format your response with clear sections for each area above."""

MISSING_THEMES_PROMPT = """You are an NHS workforce strategy analyst reviewing a 5-year strategy for 2026-2031.

The current strategy includes these 5 themes:
1. People Services
2. Inclusion
3. Talent
4. Staff Experience
5. Organisation Design

The PREVIOUS strategy (2021-25) included themes for:
- Leadership (inclusive leadership, capability development, succession planning)
- System Partner (integration, joint working, system leadership)

MACRO-CONTEXT (PESTLE FACTORS):
{macro_context}

CONTEXT FROM LATEST STRATEGIC DOCUMENTS:
{context}

AVAILABLE SOURCES: {available_sources}

Based on the latest NHS priorities, Leeds context, PESTLE factors, and emerging workforce trends:

1. **Leadership Theme**: Should this be a standalone theme given the PESTLE factors?
   - Cite evidence on leadership development needs (esp. from labour market and skills forecasts)
   - Assess against Political/Economic/Social factors requiring enhanced leadership
   - Identify any gaps if currently only embedded

2. **System Partnership**: Is system integration/partnership sufficiently prominent for macro-context challenges?
   - Cite evidence on collaborative working needs (PESTLE Political/Technological factors)
   - Identify gaps in current Organisation Design theme related to system transformation

3. **Cross-Cutting Macro-Context Themes**: Are these adequately integrated or need emphasis?
   - **Digital Transformation**: Skills gaps, legacy system modernization, interoperability (PESTLE Technological)
   - **Health & Wellbeing Crisis**: Post-pandemic retention, burnout, mental health (PESTLE Social)
   - **Skills Development & Future Workforce**: Addressing labour market gaps, emerging roles (PESTLE Economic/Technological)
   - **Sustainability & Environmental**: Net zero, green skills, climate-ready workforce (PESTLE Environmental)

4. **Emerging Trends by PESTLE**: Are there priority areas emerging that should be considered?
   - Political: System leadership capabilities, policy-responsive workforce planning
   - Economic: Salary competitiveness strategies, efficiency through technology
   - Social: Retention of mid-career staff, health disparities in service and workforce
   - Technological: Digital capability for all staff, AI/automation readiness
   - Legal: Compliance capability, working time management
   - Environmental: Sustainability skills and green practice adoption

For each, cite evidence from at least 2 different source types and explain strategic importance."""

EVIDENCE_SYNTHESIS_PROMPT = """You are an NHS workforce strategy analyst performing evidence synthesis for 2026-2031.

THEME: {theme}

OBJECTIVE: {objective}

MACRO-CONTEXT CONSIDERATIONS:
{macro_context}

CONTEXT FROM MULTIPLE SOURCES:
{context}

AVAILABLE SOURCES: {available_sources}

Synthesize evidence from AT LEAST 4 different source types (including strategic NHS docs, labour market data, skills forecasts, health/wellbeing reports):

1. **Strategic & Macro-Context Alignment**:
   - How this objective aligns with NHS 10-year plan AND emerging PESTLE factors
   - How it addresses local Leeds Health & Wellbeing Strategy priorities
   - How it responds to labour market trends (CIPD, GOV UK skills data)
   - How it supports health and wellbeing agenda
   - Connection to system-wide transformation requirements

2. **Current State & Gap Analysis** (from LCH and macro-context):
   - What is LCH's current position on this objective?
   - What evidence exists? (staff surveys, retention rates, skills audits, etc.)
   - What gaps exist between current state and macro-context demands?
   - How do external trends (skills gaps, labour market, wellbeing) amplify the gap?

3. **Best Practice Evidence from Multiple Contexts**:
   - What approaches are working in NHS trusts addressing similar challenges?
   - What does labour market and skills forecasting evidence suggest?
   - What best practices address the macro-context factors identified?
   - What evidence supports the proposed approach AND its feasibility?
   - What risks or challenges are documented from comparable implementations?

4. **Implementation Considerations in Macro-Context**:
   - Key enablers needed (including macro-context awareness)
   - Potential barriers (resource, cultural, market-based)
   - Resource requirements and funding strategies
   - Timeline alignment with macro-context trends
   - Contingencies for policy/economic/technological changes

5. **Monitoring & Adaptation**:
   - Metrics to track objective effectiveness
   - How to monitor emerging macro-context trends
   - Triggers for strategy adaptation

Format with clear citations [Source: filename] from the available sources, distinguishing between source types."""

PESTLE_ANALYSIS_PROMPT = """You are a strategic workforce analyst performing PESTLE analysis for NHS 2026-2031 strategy.

PESTLE FACTOR: {factor}
FACTOR DESCRIPTION: {factor_description}

STRATEGIC DOCUMENTS CONTEXT:
{context}

AVAILABLE SOURCES: {available_sources}

Analyze how the {factor} factor influences Leeds Community Healthcare workforce strategy:

1. **Factor Definition & Current Landscape**:
   - Define the factor and current state in UK healthcare
   - Cite evidence from documents on {factor} trends/challenges

2. **Strategic Implications for LCH**:
   - How does {factor} create opportunities or threats?
   - What workforce impacts are documented?
   - How might this factor evolve 2026-2031?

3. **Connection to Strategy Themes**:
   - Which of the 5 themes are most affected by {factor}?
   - Are there gaps in how objectives address {factor}?

4. **Recommendations for Strategy Robustness**:
   - What adjustments would make strategy resilient to {factor} changes?
   - What capabilities or investments are needed?
   - What contingencies should be built in?

5. **Monitoring & Adaptation Triggers**:
   - How should LCH monitor {factor} changes?
   - What indicators suggest need for strategy adjustment?

Format with citations [Source: filename]."""

CROSS_CUTTING_THEMES_PROMPT = """You are a strategic workforce analyst analyzing cross-cutting macro-themes for NHS 2026-2031.

CROSS-CUTTING THEME: {cross_theme}

STRATEGIC DOCUMENTS CONTEXT:
{context}

AVAILABLE SOURCES: {available_sources}

Analyze how {cross_theme} cuts across multiple PESTLE factors and strategy themes:

1. **Theme Overview & Evidence**:
   - Define {cross_theme} and its significance for NHS workforce
   - Cite evidence from multiple sources (labour market, skills, H&W, NHS docs)
   - Show why this is "cross-cutting" (spans multiple PESTLE factors)

2. **PESTLE Dimensions**:
   - How does {cross_theme} connect to Political priorities?
   - Economic implications and opportunities?
   - Social/workforce expectations?
   - Technological enablers and challenges?
   - Legal/compliance aspects?
   - Environmental/sustainability connections?

3. **Impact on All Strategy Themes**:
   - How does {cross_theme} impact People Services?
   - How does it impact Inclusion objectives?
   - How does it impact Talent development?
   - How does it impact Staff Experience?
   - How does it impact Organisation Design?

4. **Current Strategy Gaps**:
   - How well do current objectives address {cross_theme}?
   - What's missing or underemphasized?
   - Where are integration opportunities?

5. **Integrated Recommendations**:
   - How should {cross_theme} be woven into strategy across all themes?
   - What objectives need adjustment?
   - What new cross-theme initiatives are needed?
   - Resource and timeline implications?

Format with citations [Source: filename] from diverse source types."""

MACRO_CONTEXT_SUMMARY_PROMPT = """You are a strategic workforce analyst synthesizing macro-context findings.

MACRO-CONTEXT FINDINGS (PESTLE + CROSS-CUTTING THEMES):
{macro_findings}

STRATEGIC THEMES & OBJECTIVES:
{strategy_themes}

STRATEGIC DOCUMENTS:
{available_sources}

Provide an executive summary of macro-context implications:

1. **Key Macro-Trends**:
   - What are the 5-7 most significant external trends?
   - What's the evidence base?
   - What's the urgency/timeline?

2. **Strategic Alignment Assessment**:
   - How well does current strategy address macro-context?
   - What are the critical gaps?
   - What's at risk if gaps aren't addressed?

3. **Capability & Readiness Gaps**:
   - What new capabilities does LCH need?
   - What skills gaps must be closed?
   - What infrastructure/systems needed?

4. **Prioritized Recommendations**:
   - Top 3-5 strategic adjustments to make
   - High-impact, achievable actions for 2026-2027
   - Medium-term initiatives for 2027-2030
   - Long-term positioning for 2030-2031

5. **Risk Mitigation**:
   - Key risks if macro-context not addressed
   - Mitigation strategies
   - Contingency planning needs

Format as actionable strategic guidance."""


def get_recency_flag(doc_date: str, year_range_end: str = None) -> str:
    """Generate recency flag based on document date."""
    if not doc_date:
        return "[NO DATE]"

    try:
        doc_datetime = datetime.strptime(doc_date, "%Y-%m-%d")
        today = datetime.now()
        days_old = (today - doc_datetime).days
        years_old = days_old / 365.25

        if year_range_end:
            try:
                end_year = int(year_range_end)
                years_until_expiry = end_year - today.year
                if years_until_expiry <= 1 and years_until_expiry >= 0:
                    return f"[STRATEGY EXPIRES {year_range_end}]"
            except (ValueError, TypeError):
                pass

        if years_old < 1:
            return "[RECENT]"
        elif years_old < 2:
            return "[RECENT - 1 YEAR]"
        elif years_old < 4:
            return "[OLDER DOCUMENT - 2+ YEARS]"
        else:
            return "[ARCHIVAL - 4+ YEARS]"

    except (ValueError, TypeError):
        return "[DATE FORMAT ERROR]"


def analyze_source_coverage(source_documents):
    """Analyze how many unique sources were retrieved."""
    source_counts = defaultdict(int)
    for doc in source_documents:
        source = doc.metadata.get("source", "Unknown")
        source_counts[source] += 1
    return source_counts


def main():
    """Main gap analysis pipeline."""
    # Capture output for Markdown
    original_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    print("# Workforce Strategy 2026-2031: Gap Analysis Report\n")
    print(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print("---\n")

    # Check ChromaDB exists
    if not os.path.exists(STORE_DIR):
        sys.stdout = original_stdout
        print(f"[ERROR] ChromaDB not found at {STORE_DIR}")
        print("Please run ingest_pipeline.py first to ingest documents.")
        return

    # Initialize embeddings and load ChromaDB
    print("## Initialization\n")
    print("Loading strategic documents and performing gap analysis...\n")

    embeddings = OpenAIEmbeddings()
    print("[OK] Initialized OpenAI Embeddings client.\n")

    vectordb = Chroma(persist_directory=STORE_DIR, embedding_function=embeddings)
    print("[OK] ChromaDB loaded.\n")

    # Check if database has content
    try:
        all_db_data = vectordb._collection.get(include=["metadatas"])
        total_chunks = len(all_db_data.get("metadatas", []))
        if total_chunks == 0:
            sys.stdout = original_stdout
            print("[ERROR] ChromaDB is empty. No documents to analyze.")
            return
        print(f"Found **{total_chunks}** chunks in ChromaDB.\n")
    except Exception as e:
        sys.stdout = original_stdout
        print(f"[ERROR] Could not access ChromaDB: {e}")
        return

    # Initialize QA LLM
    qa_llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

    # Helper function to format macro-context for prompts
    def format_macro_context():
        """Format PESTLE factors into readable context."""
        pestle_text = "\n".join([f"- **{k}**: {v}" for k, v in PESTLE_FACTORS.items()])
        return f"Key PESTLE Factors:\n{pestle_text}"

    macro_context = format_macro_context()

    # --- SECTION 0: MACRO-CONTEXT OVERVIEW ———————————————————

    print("## 0. Macro-Context Analysis: PESTLE & External Factors\n")
    print("Analyzing the broader strategic context (Political, Economic, Social, Technological, Legal, Environmental factors)\n")
    print("and key cross-cutting themes that span multiple PESTLE dimensions.\n")

    # Analyze each PESTLE factor
    print("### A. PESTLE Factor Analysis\n")
    for factor_name, factor_description in PESTLE_FACTORS.items():
        print(f"#### {factor_name} Factor\n")

        query_text = f"What are the key {factor_name.lower()} factors affecting NHS workforce strategy? What trends should LCH consider for {factor_name.lower()} context?"
        retriever = vectordb.as_retriever(search_kwargs={"k": 15})
        retrieved_docs = retriever.invoke(query_text)

        unique_sources = []
        seen = set()
        for doc in retrieved_docs:
            src = doc.metadata.get("source", "Unknown")
            if src not in seen:
                unique_sources.append(src)
                seen.add(src)

        available_sources_str = ", ".join(unique_sources)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        prompt = PromptTemplate.from_template(PESTLE_ANALYSIS_PROMPT)
        formatted_prompt = prompt.format(
            factor=factor_name,
            factor_description=factor_description,
            context=context,
            available_sources=available_sources_str
        )

        analysis = qa_llm.predict(formatted_prompt)
        print(f"{analysis}\n")
        print("---\n")

    # Analyze cross-cutting themes
    print("### B. Cross-Cutting Macro-Themes\n")
    cross_themes = [
        "Digital Transformation",
        "Health & Wellbeing Crisis (Retention, Burnout, Mental Health)",
        "Skills Development & Future Workforce",
        "System Integration & Partnership",
        "Sustainability & Environmental Readiness"
    ]

    for cross_theme in cross_themes:
        print(f"#### {cross_theme}\n")

        query_text = f"How does {cross_theme.lower()} impact NHS workforce? What are the trends and evidence?"
        retriever = vectordb.as_retriever(search_kwargs={"k": 20})
        retrieved_docs = retriever.invoke(query_text)

        unique_sources = []
        seen = set()
        for doc in retrieved_docs:
            src = doc.metadata.get("source", "Unknown")
            if src not in seen:
                unique_sources.append(src)
                seen.add(src)

        available_sources_str = ", ".join(unique_sources)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        prompt = PromptTemplate.from_template(CROSS_CUTTING_THEMES_PROMPT)
        formatted_prompt = prompt.format(
            cross_theme=cross_theme,
            context=context,
            available_sources=available_sources_str
        )

        analysis = qa_llm.predict(formatted_prompt)
        print(f"{analysis}\n")
        print("---\n")

    # --- SECTION 1: ANALYZE EACH THEME FOR GAPS ———————————————

    print("## 1. Theme Gap Analysis\n")
    print("Analyzing each proposed theme against strategic documents to identify gaps and opportunities.\n")

    for theme_name, objectives in STRATEGY_THEMES.items():
        print(f"### Theme: {theme_name}\n")

        objectives_str = "\n".join([f"- {obj}" for obj in objectives])
        query_text = f"What are the NHS and Leeds priorities for {theme_name.lower()}? What should workforce strategy focus on for {theme_name.lower()}?"

        # Retrieve relevant documents
        retriever = vectordb.as_retriever(search_kwargs={"k": 25})
        retrieved_docs = retriever.invoke(query_text)

        # Extract unique source filenames
        unique_sources = []
        seen = set()
        for doc in retrieved_docs:
            src = doc.metadata.get("source", "Unknown")
            if src not in seen:
                unique_sources.append(src)
                seen.add(src)

        available_sources_str = ", ".join(unique_sources)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # Create gap analysis prompt with macro context
        prompt = PromptTemplate.from_template(GAP_ANALYSIS_PROMPT)
        formatted_prompt = prompt.format(
            theme=theme_name,
            objectives=objectives_str,
            macro_context=macro_context,
            context=context,
            available_sources=available_sources_str
        )

        # Get analysis from LLM
        analysis = qa_llm.predict(formatted_prompt)
        print(f"{analysis}\n")

        # Show sources
        sources_used = analyze_source_coverage(retrieved_docs)
        print(f"**Sources Referenced:** {len(sources_used)} documents\n")

        print("---\n")

    # --- SECTION 2: ANALYZE POTENTIALLY MISSING THEMES ———————

    print("## 2. Missing or Underemphasized Themes\n")
    print("Analyzing whether previous themes (Leadership, System Partner) should be reconsidered or if new themes are emerging.\n")

    query_text = "What are the top priorities for NHS workforce strategy in 2026-2031? What are the key themes organizations should focus on?"
    retriever = vectordb.as_retriever(search_kwargs={"k": 30})
    retrieved_docs = retriever.invoke(query_text)

    unique_sources = []
    seen = set()
    for doc in retrieved_docs:
        src = doc.metadata.get("source", "Unknown")
        if src not in seen:
            unique_sources.append(src)
            seen.add(src)

    available_sources_str = ", ".join(unique_sources)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    prompt = PromptTemplate.from_template(MISSING_THEMES_PROMPT)
    formatted_prompt = prompt.format(
        macro_context=macro_context,
        context=context,
        available_sources=available_sources_str
    )

    missing_themes_analysis = qa_llm.predict(formatted_prompt)
    print(f"{missing_themes_analysis}\n")
    print("---\n")

    # --- SECTION 3: EVIDENCE SYNTHESIS FOR KEY OBJECTIVES ———

    print("## 3. Evidence Synthesis by Theme\n")
    print("Synthesizing evidence from multiple sources for key objectives in each theme.\n")

    # Select 1-2 key objectives per theme for deep evidence synthesis
    key_objectives = {
        "People Services": "Adopt and embed new NHS models and systems",
        "Inclusion": "Design and target interventions based on data with insight from Staff Networks",
        "Talent": "Deliver 10YP objectives (apprenticeships, preceptorships etc)",
        "Staff Experience": "Assess and refresh local HWB and staff benefits offer against staff needs and expectations",
        "Organisation Design": "Work in system partnership to implement Neighbourhood Health model"
    }

    for theme_name, objective in key_objectives.items():
        print(f"### {theme_name}: {objective}\n")

        query_text = f"Evidence and best practices for: {objective}"

        retriever = vectordb.as_retriever(search_kwargs={"k": 20})
        retrieved_docs = retriever.invoke(query_text)

        unique_sources = []
        seen = set()
        for doc in retrieved_docs:
            src = doc.metadata.get("source", "Unknown")
            if src not in seen:
                unique_sources.append(src)
                seen.add(src)

        available_sources_str = ", ".join(unique_sources)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        prompt = PromptTemplate.from_template(EVIDENCE_SYNTHESIS_PROMPT)
        formatted_prompt = prompt.format(
            theme=theme_name,
            objective=objective,
            macro_context=macro_context,
            context=context,
            available_sources=available_sources_str
        )

        evidence_synthesis = qa_llm.predict(formatted_prompt)
        print(f"{evidence_synthesis}\n")
        print("---\n")

    # --- FINAL SUMMARY ———————————————————————————————————————

    print("## 4. Summary of Recommendations\n")
    print("### Immediate Actions\n")
    print("1. **Leadership Theme Review**: Consider whether Leadership should be reinstated as a standalone theme")
    print("2. **System Partnership Enhancement**: Strengthen Organisation Design objectives related to system integration")
    print("3. **10-Year Plan Alignment**: Ensure all objectives explicitly connect to NHS 10YP priorities")
    print("4. **Emerging Themes**: Evaluate digital transformation and new role development as potential focus areas")
    print("5. **Measurement Framework**: Develop clear metrics aligned with NHS and Leeds outcome frameworks\n")

    print("---\n")
    print("[COMPLETE] Gap analysis for 2026-2031 Workforce Strategy completed.\n")

    # Save Markdown output
    sys.stdout = original_stdout
    md_output_path = "workforce_strategy_gap_analysis_report.md"
    with open(md_output_path, "w", encoding="utf-8") as md_file:
        md_file.write(captured_output.getvalue())

    print(f"\n✓ ANALYSIS REPORT SAVED: {md_output_path}")
    print("\nNext steps:")
    print("1. Review the full analysis report in workforce_strategy_gap_analysis_report.md")
    print("2. Use identify_missing_themes.py for detailed analysis of potentially missing themes")
    print("3. Consider running interactive queries: python interactive_query_multi_source.py")


if __name__ == "__main__":
    main()
