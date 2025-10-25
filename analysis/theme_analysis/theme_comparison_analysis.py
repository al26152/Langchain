"""
theme_comparison_analysis.py

THEME COMPARISON AND TRANSITION ANALYSIS

PURPOSE:
  Provides structured comparison between:
  1. LCH Workforce Strategy 2021-25 themes (7 themes)
  2. LCH Workforce Strategy 2026-2031 themes (5 themes)

  Identifies:
  - Which objectives from old strategy are retained/modified
  - Which objectives are dropped
  - Potential gaps in new strategy
  - Opportunities for rebalancing

USAGE:
  python theme_comparison_analysis.py

OUTPUT:
  - theme_transition_analysis.md: Detailed transition analysis
  - Gap identification report
  - Cross-theme dependency mapping
"""

import sys
from io import StringIO
from datetime import datetime

# --- OLD STRATEGY THEMES (2021-25) ———————————————————————————

OLD_THEMES_2021_25 = {
    "Resourcing": {
        "ambition": "We maximise our workforce capacity for delivery of the best possible care, by fully exploring all options available to us",
        "objectives": [
            "Increase breadth and quality of attraction and marketing techniques",
            "Specify and mobilise a new temporary staffing model",
            "Enhance internal Bank capacity and increase fill rates",
            "Adapt approach to internal mutual aid",
            "Attract and retain more staff by enabling flexible working options",
            "Meet regularly with LCH new starters to understand needs"
        ],
        "focus": "External and internal recruitment, staffing flexibility, retention"
    },
    "Organisation Design": {
        "ambition": "We know what workforce and what skills LCH needs to deliver the best possible care, now and in the future; and take action to enable its delivery",
        "objectives": [
            "Embed tactical, operational and strategic workforce planning",
            "Specify and diversify career pathways",
            "Support improved organisational productivity through technology",
            "Develop and implement new Hybrid Working approach",
            "Lead on protocols enabling working across organisational boundaries",
            "Engage with external partners to address skills shortages"
        ],
        "focus": "Workforce planning, career development, hybrid working, system integration"
    },
    "Leadership": {
        "ambition": "LCH leaders are consistently inclusive, capable, put people before process and are aligned with LCH values",
        "objectives": [
            "Deliver leadership development provision adapted to organisational needs",
            "Require all new leaders to attend Leadership Essentials course",
            "Identify areas with leadership capability issues and create action plans",
            "Commission 360 degree assessments for senior leaders",
            "Focus talent management on underrepresented groups",
            "Explore opportunities with system partners for leadership programmes",
            "Implement new mentoring scheme for new and struggling leaders"
        ],
        "focus": "Leadership capability, succession planning, diversity in leadership, mentoring"
    },
    "Inclusion": {
        "ambition": "We are much more representative of our communities. Disparities in employee experience have substantially reduced",
        "objectives": [
            "Identify underrepresented communities and reduce barriers",
            "Use appraisal processes to emphasise personal responsibility for anti-racism",
            "Identify and tackle areas with disparity in employee experience",
            "Work with Staff Groups, Forums and Networks on lived experience",
            "Build on Allyship and Reverse Mentoring Programmes",
            "Seek sustainable funding for ED&I programme"
        ],
        "focus": "Diversity, equity, inclusion, anti-racism, staff networks, lived experience"
    },
    "Wellbeing": {
        "ambition": "We look after our people through improved psychological, physical and financial wellbeing",
        "objectives": [
            "Board-level scrutiny of wellbeing with Wellbeing Guardian",
            "Expand HWB offer to include financial and lifestyle support",
            "Psychological support offer demonstrably enables people to remain well",
            "Fewer people report feeling pressure to attend work when unwell",
            "Leaders and staff feel safe to engage in wellbeing conversations",
            "Employees with long-term conditions coproduce new HWB approaches"
        ],
        "focus": "Health & wellbeing, psychological support, financial wellbeing, sick leave culture"
    },
    "System Partner": {
        "ambition": "We enable further successful integration and joint working for services and clinical pathways",
        "objectives": [
            "Develop and share #TeamLeeds talent pipeline with city partners",
            "Lead on protocols enabling working across organisational boundaries",
            "Deliver Leeds One Workforce objectives",
            "Work in partnership with Anchor Institutions",
            "Enable GP Confederation to become mature employer",
            "Develop LCH ARRS offer into self-sustaining model",
            "Support LCH staff to develop collaborative working skills"
        ],
        "focus": "System integration, partnership working, cross-organisational teams, primary care"
    },
    "Foundations": {
        "ambition": "We provide excellent workforce and HR services to our customers, in support of the provision of outstanding care",
        "objectives": [
            "Benchmark workforce services with consistent KPIs",
            "Integrate workforce teams to deliver high-impact initiatives",
            "Develop resourcing service for substantive and temporary roles",
            "Embed HR Business Partners in Business Units",
            "Strengthen analytics function with automation",
            "Fully embed People before Process approach",
            "Develop Organisational Training & Development offer in partnership"
        ],
        "focus": "HR services, workforce systems, data analytics, business partnering, training"
    }
}

# --- NEW STRATEGY THEMES (2026-2031) ———————————————————————————

NEW_THEMES_2026_2031 = {
    "People Services": {
        "objectives": [
            "Increase standardisation and efficiency",
            "Embed new approaches to People Business Partnering and People Projects",
            "Adopt and embed new NHS models and systems",
            "Broaden opportunities for professional People skills development",
            "Use data reporting and insights to inform People and Trust decision-making",
            "Equip employee relations services to handle increased casework complexity and volume"
        ],
        "focus": "HR standardization, NHS systems adoption, professional development, data-driven decisions, ER capacity"
    },
    "Inclusion": {
        "objectives": [
            "Design and target interventions based on data; with insight from Staff Networks",
            "Embed inclusive practices as standard practices",
            "Target remedial support and interventions to areas falling below inclusive expectations",
            "Reduce disparity of experience"
        ],
        "focus": "Data-driven inclusion, embedded practices, targeted support, equity outcomes"
    },
    "Talent": {
        "objectives": [
            "Deliver 10YP objectives (apprenticeships, preceptorships etc)",
            "Support talent pipelines in local communities",
            "Codesign refreshed approach to Education, Training & Development at LCH",
            "Leverage benefits of ATS to deliver greater recruitment process efficiency"
        ],
        "focus": "New roles/career paths, NHS 10YP alignment, community talent, recruitment tech, training/development"
    },
    "Staff Experience": {
        "objectives": [
            "Enhance factors underpinning high Staff Engagement",
            "Assess and refresh local HWB and staff benefits offer against staff needs and expectations",
            "Improve Wellbeing at Work procedural delivery and outcomes",
            "Support staff and managers to apply 'Organisation of Adults' approach"
        ],
        "focus": "Engagement, wellbeing, benefits, adult social care framework"
    },
    "Organisation Design": {
        "objectives": [
            "Work in system partnership to implement Neighbourhood Health model",
            "Provide support and skills development to enhance service transformation",
            "Identify and develop inter-organisational opportunities to offer People Services at scale",
            "Provide support to delivery of workforce models and planning to deliver NHS 10YP"
        ],
        "focus": "Neighbourhood health, system partnership, People Services scale, 10YP delivery"
    }
}

# --- ANALYSIS FUNCTIONS ———————————————————————————————————

def map_theme_transitions():
    """Map how old themes transition to new themes."""
    transitions = {
        "Resourcing (2021-25)": {
            "maps_to": ["Talent (2026-31)", "Organisation Design (2026-31)"],
            "explanation": "Recruitment and staffing elements move to Talent; workforce planning moves to Organisation Design"
        },
        "Organisation Design (2021-25)": {
            "maps_to": ["Organisation Design (2026-31)"],
            "explanation": "Mostly retained but with added emphasis on Neighbourhood Health and system partnership"
        },
        "Leadership (2021-25)": {
            "maps_to": ["POTENTIALLY MISSING", "Talent (embedded)"],
            "explanation": "No standalone Leadership theme in 2026-31; some leadership dev embedded in Talent"
        },
        "Inclusion (2021-25)": {
            "maps_to": ["Inclusion (2026-31)"],
            "explanation": "Retained with focus on data-driven and embedded approaches"
        },
        "Wellbeing (2021-25)": {
            "maps_to": ["Staff Experience (2026-31)"],
            "explanation": "Wellbeing becomes part of broader 'Staff Experience' theme"
        },
        "System Partner (2021-25)": {
            "maps_to": ["Organisation Design (embedded)", "POTENTIALLY MISSING"],
            "explanation": "System partnership elements moved to Organisation Design; may lack the strategic emphasis"
        },
        "Foundations (2021-25)": {
            "maps_to": ["People Services (2026-31)"],
            "explanation": "HR services and foundations renamed to 'People Services' with NHS systems emphasis"
        }
    }
    return transitions


def identify_dropped_objectives():
    """Identify objectives from 2021-25 that don't appear in 2026-31."""
    dropped = []

    old_objectives_text = " ".join([
        obj for theme_data in OLD_THEMES_2021_25.values()
        for obj in theme_data.get("objectives", [])
    ])

    new_objectives_text = " ".join([
        obj for theme_data in NEW_THEMES_2026_2031.values()
        for obj in theme_data.get("objectives", [])
    ])

    key_areas = {
        "new leader training": "Require all new leaders to attend Leadership Essentials",
        "360 degree assessment": "Senior leader 360 assessments",
        "mentoring": "Mentoring scheme for new leaders",
        "talent management": "Talent management and succession planning",
        "allyship": "Allyship and Reverse Mentoring programmes",
        "reverse mentoring": "Reverse Mentoring programme",
        "ARRS": "ARRS offer to primary care",
        "GP confederation": "GP Confederation support",
        "hybrid working": "Hybrid Working approach",
        "career pathways": "Career pathway specification and diversity"
    }

    dropped_areas = []
    for area_name, area_desc in key_areas.items():
        if area_name.lower() not in new_objectives_text.lower():
            dropped_areas.append(area_desc)

    return dropped_areas


def identify_new_emphases():
    """Identify new emphases in 2026-31 strategy."""
    new_emphases = [
        ("Neighbourhood Health model", "Specific focus on neighborhood health implementation"),
        ("NHS 10-Year Plan alignment", "Explicit commitment to deliver 10YP objectives"),
        ("ATS/Recruitment technology", "Emphasis on Applicant Tracking Systems for efficiency"),
        ("Organisation of Adults", "Social care framework application (potentially new context)"),
        ("Employee relations capacity", "Specific focus on ER casework complexity and volume"),
        ("Data and insights-driven", "Stronger emphasis on data-driven decision making"),
        ("NHS models and systems adoption", "Adoption of national NHS systems and approaches")
    ]
    return new_emphases


def generate_gap_analysis_report():
    """Generate comprehensive gap analysis report."""
    output = StringIO()

    output.write("# Workforce Strategy Theme Transition Analysis: 2021-25 to 2026-31\n\n")
    output.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    # Executive Summary
    output.write("## Executive Summary\n\n")
    output.write("This analysis compares the LCH Workforce Strategy 2021-25 (7 themes) with the proposed 2026-31 strategy (5 themes).\n\n")
    output.write("**Key Findings:**\n")
    output.write("- 2 themes consolidated (Resourcing → Talent; Wellbeing → Staff Experience)\n")
    output.write("- 1-2 themes potentially missing (Leadership, System Partner prominence)\n")
    output.write("- New emphases on NHS systems, Neighbourhood Health, and 10-year plan\n")
    output.write("- Some valuable objectives may not be retained\n\n")

    # Section 1: Theme Mapping
    output.write("## 1. Theme Transition Mapping\n\n")
    transitions = map_theme_transitions()
    for old_theme, trans_data in transitions.items():
        output.write(f"### {old_theme}\n")
        output.write(f"**Maps to:** {', '.join(trans_data['maps_to'])}\n")
        output.write(f"**Explanation:** {trans_data['explanation']}\n\n")

    # Section 2: Dropped Objectives
    output.write("## 2. Objectives from 2021-25 Not Explicitly in 2026-31\n\n")
    output.write("The following strategic areas from the previous strategy don't appear explicitly in the new theme objectives:\n\n")
    dropped = identify_dropped_objectives()
    for i, obj in enumerate(dropped, 1):
        output.write(f"{i}. **{obj}** - May still be addressed but not explicit in theme objectives\n")
    output.write("\n**Recommendation:** Review whether these dropped areas remain important and, if so, how they're addressed.\n\n")

    # Section 3: New Emphases
    output.write("## 3. New Strategic Emphases in 2026-31\n\n")
    output.write("The new strategy introduces or emphasizes several areas not prominent in 2021-25:\n\n")
    new_emp = identify_new_emphases()
    for area, desc in new_emp:
        output.write(f"- **{area}**: {desc}\n")
    output.write("\n")

    # Section 4: Potentially Missing Themes
    output.write("## 4. Potentially Missing or Under-emphasized Themes\n\n")

    output.write("### 4.1 Leadership Theme\n")
    output.write("**Status:** Not a standalone theme in 2026-31\n\n")
    output.write("**Old Leadership Theme Objectives:**\n")
    for obj in OLD_THEMES_2021_25["Leadership"]["objectives"]:
        output.write(f"- {obj}\n")
    output.write("\n**Assessment:**\n")
    output.write("- Leadership development is mentioned in Talent theme but not with same strategic emphasis\n")
    output.write("- No explicit mention of: 360 assessments, mentoring schemes, talent management focus\n")
    output.write("- Succession planning not visible in new objectives\n")
    output.write("- Leadership diversity and inclusion elements moved to Inclusion theme\n\n")
    output.write("**Recommendation:** Consider whether Leadership warrants reinstatement as standalone theme, especially given:\n")
    output.write("  - NHS People Plan emphasis on leadership for culture change\n")
    output.write("  - Succession planning importance for 5-year period\n")
    output.write("  - Service transformation will require strong leadership capability\n\n")

    output.write("### 4.2 System Partner Theme Prominence\n")
    output.write("**Status:** Elements in Organisation Design but not strategic priority\n\n")
    output.write("**Old System Partner Theme Objectives:**\n")
    for obj in OLD_THEMES_2021_25["System Partner"]["objectives"]:
        output.write(f"- {obj}\n")
    output.write("\n**Assessment:**\n")
    output.write("- System partnership has moved from standalone theme to part of Organisation Design\n")
    output.write("- Some specific objectives missing: #TeamLeeds talent pipeline, GP Confederation maturity, ARRS development\n")
    output.write("- May be underemphasized given ICS/ICP integration importance\n\n")
    output.write("**Recommendation:** Strengthen Organisation Design theme with explicit system partnership objectives, or consider reinstating as standalone theme.\n\n")

    # Section 5: Theme Comparison Table
    output.write("## 5. Detailed Theme Comparison\n\n")

    output.write("### Coverage Analysis\n\n")
    output.write("| Area | 2021-25 Themes (7) | 2026-31 Themes (5) | Status |\n")
    output.write("|------|-------------------|-------------------|--------|\n")
    output.write("| Recruitment/Resourcing | Resourcing | Talent | Consolidated |\n")
    output.write("| Career Pathways | Resourcing/Leadership | Talent | Consolidated |\n")
    output.write("| Leadership Development | Leadership | Talent (embedded) | Downgraded |\n")
    output.write("| Succession Planning | Leadership | NOT VISIBLE | **GAP** |\n")
    output.write("| Inclusion/Diversity | Inclusion | Inclusion | Retained |\n")
    output.write("| Health & Wellbeing | Wellbeing | Staff Experience | Consolidated |\n")
    output.write("| System Integration | System Partner | Organisation Design | Consolidated/Downgraded |\n")
    output.write("| HR Services | Foundations | People Services | Renamed/Enhanced |\n")
    output.write("| Hybrid Working | Organisation Design | NOT VISIBLE | **GAP** |\n")
    output.write("| Workforce Planning | Organisation Design | Organisation Design | Retained |\n")
    output.write("\n")

    # Section 6: Recommendations
    output.write("## 6. Strategic Recommendations\n\n")
    output.write("### Priority 1: Leadership Theme Reinstatement\n")
    output.write("- Reinstate Leadership as standalone theme for 2026-31 strategy\n")
    output.write("- Include: succession planning, 360 assessments, mentoring, leadership diversity\n")
    output.write("- Rationale: Essential for service transformation and culture change\n\n")

    output.write("### Priority 2: System Partner Elevation\n")
    output.write("- Strengthen system partnership strategy given ICS/ICP priorities\n")
    output.write("- OR: Elevate to standalone theme if system integration is strategic priority\n")
    output.write("- Include: #TeamLeeds pipeline, inter-organisational working, primary care partnership\n\n")

    output.write("### Priority 3: Retain Explicit Objectives\n")
    output.write("- Hybrid working approach (retained in objectives or explicit in Organisation Design)\n")
    output.write("- Career pathway diversity and development\n")
    output.write("- ARRS and primary care partnership models\n\n")

    output.write("### Priority 4: Ensure 10YP Alignment\n")
    output.write("- Excellent that new roles/apprenticeships are explicit in Talent theme\n")
    output.write("- Expand to ensure all themes connect to specific 10YP objectives\n")
    output.write("- Create mapping of strategy objectives to 10YP priorities\n\n")

    output.write("### Priority 5: Add Emerging Themes to Consider\n")
    output.write("- **Digital Transformation**: New skills, systems adoption, technology enablement\n")
    output.write("- **Retention and Career Progression**: Critical in tight labour market\n")
    output.write("- **Equity and Health Disparities**: Local health inequalities context\n")
    output.write("- **New Role Development**: Emerging roles from 10YP and Neighbourhood Health\n\n")

    # Final Summary
    output.write("## 7. Conclusion\n\n")
    output.write("The move from 7 to 5 themes consolidates related areas and reflects NHS priorities around systems and the 10-year plan.\n\n")
    output.write("However, consolidation risks losing strategic focus on:\n")
    output.write("- **Leadership capability and succession** - critical for transformation\n")
    output.write("- **System partnership prominence** - important for integrated care\n")
    output.write("- **Explicit workforce planning** - needs continued emphasis\n\n")
    output.write("**Next Steps:**\n")
    output.write("1. Review this analysis with strategy sponsors\n")
    output.write("2. Conduct stakeholder consultation on missing themes\n")
    output.write("3. Map strategy objectives to NHS 10YP deliverables\n")
    output.write("4. Consider adding embedded objectives back into theme descriptions\n")
    output.write("5. Identify metrics aligned with both LCH and NHS priorities\n\n")

    return output.getvalue()


def main():
    """Generate and save theme comparison analysis."""
    report = generate_gap_analysis_report()

    output_path = "theme_transition_analysis.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✓ Theme transition analysis saved to: {output_path}")
    print("\nKey findings:")
    print("- Leadership theme potentially missing")
    print("- System Partner prominence may be reduced")
    print("- Some valuable objectives not explicitly retained")
    print("\nReview the full report for detailed recommendations.")


if __name__ == "__main__":
    main()
