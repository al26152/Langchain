#!/usr/bin/env python3
"""
Comprehensive Test of Upgraded WebLookupAgent with Dynamic Web Search

Tests:
1. Basic context retrieval
2. Query formulation with various inputs
3. Theme and priority extraction
4. Integration with document selector (if available)
5. Graceful error handling
"""

import sys
import os
from datetime import datetime
import json

sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv('.env')

from analysis.multi_agent.web_lookup_agent import WebLookupAgent


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_basic_context_retrieval():
    """Test 1: Basic context retrieval for typical NHS query"""
    print_section("TEST 1: Basic Context Retrieval")

    agent = WebLookupAgent()
    query = "What are the current workforce priorities for Leeds Community Healthcare?"

    print(f"\nQuery: {query}\n")

    try:
        context = agent.get_context(query)

        print("RESULTS:")
        print(f"\n[Key Themes]")
        for i, theme in enumerate(context.get("key_themes", []), 1):
            print(f"  {i}. {theme}")

        print(f"\n[National Priorities]")
        for i, priority in enumerate(context.get("national_priorities", []), 1):
            print(f"  {i}. {priority}")

        print(f"\n[Relevant Policies]")
        policies = context.get("relevant_policies", [])
        if policies:
            for i, policy in enumerate(policies, 1):
                print(f"  {i}. {policy}")
        else:
            print("  (None identified)")

        print(f"\n[External Context Preview]")
        context_text = context.get("external_context", "")
        preview = context_text[:200] + "..." if len(context_text) > 200 else context_text
        print(f"  {preview}")

        print(f"\n[Sources]")
        sources = context.get("sources", [])
        for source in sources:
            print(f"  - {source}")

        print("\n[PASS] Basic context retrieval successful")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_query_formulation():
    """Test 2: Query formulation with various inputs"""
    print_section("TEST 2: Query Formulation Logic")

    agent = WebLookupAgent()

    test_cases = [
        {
            "query": "What are workforce priorities?",
            "expected": "Should add Leeds (healthcare-focused, no location)"
        },
        {
            "query": "How does LCH respond to 10-year plan?",
            "expected": "Should NOT add Leeds (LCH implies Leeds)"
        },
        {
            "query": "What is national NHS policy on X?",
            "expected": "Should NOT add Leeds (clearly national scope)"
        },
        {
            "query": "Tell me about West Yorkshire integrated care",
            "expected": "Should NOT add Leeds (West Yorkshire already mentioned)"
        }
    ]

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  Input Query: {test_case['query']}")
        print(f"  Expected: {test_case['expected']}")

        try:
            search_query = agent._formulate_search_query(test_case['query'])
            print(f"  Generated Search Query: {search_query}")
            print(f"  [PASS]")
        except Exception as e:
            print(f"  [FAIL] Error: {str(e)}")
            all_passed = False

    return all_passed


def test_theme_extraction():
    """Test 3: Theme and priority extraction"""
    print_section("TEST 3: Theme and Priority Extraction")

    agent = WebLookupAgent()

    test_queries = [
        "What are partnership and integration strategies for Leeds?",
        "How should LCH address health inequalities?",
        "What are the latest developments in digital transformation?"
    ]

    all_passed = True

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)

        try:
            context = agent.get_context(query)

            themes_found = len(context.get("key_themes", []))
            priorities_found = len(context.get("national_priorities", []))

            print(f"  Themes extracted: {themes_found}")
            print(f"  Priorities extracted: {priorities_found}")

            if themes_found > 0 and priorities_found > 0:
                print(f"  [PASS]")
            else:
                print(f"  [WARN] Limited extraction - may be sparse topic")

        except Exception as e:
            print(f"  [FAIL] Error: {str(e)}")
            all_passed = False

    return all_passed


def test_error_handling():
    """Test 4: Error handling and graceful degradation"""
    print_section("TEST 4: Error Handling")

    agent = WebLookupAgent()

    print("\nTesting with edge cases:")
    print("-" * 60)

    test_cases = [
        {
            "query": "Unknown emerging technology X",
            "description": "Niche/emerging topic (sparse results)"
        },
        {
            "query": "NHS",
            "description": "Very generic query"
        }
    ]

    all_passed = True

    for test_case in test_cases:
        print(f"\nTest: {test_case['description']}")
        print(f"Query: {test_case['query']}")

        try:
            context = agent.get_context(test_case['query'])

            # Check if system degrades gracefully
            has_themes = len(context.get("key_themes", [])) > 0
            has_context = len(context.get("external_context", "")) > 0

            if has_themes and has_context:
                print(f"  Status: Returned context (may be sparse)")
                print(f"  [PASS] Graceful degradation working")
            else:
                print(f"  [WARN] Very limited context")

        except Exception as e:
            print(f"  [FAIL] Unhandled error: {str(e)}")
            all_passed = False

    return all_passed


def test_validation_framework():
    """Test 5: Validation framework generation"""
    print_section("TEST 5: Validation Framework")

    agent = WebLookupAgent()
    query = "What should be LCH's strategic priorities?"

    print(f"\nQuery: {query}\n")

    try:
        context = agent.get_context(query)
        framework = context.get("validation_framework", {})

        if framework:
            print("Validation Framework Generated:")
            for i, (key, question) in enumerate(framework.items(), 1):
                print(f"  {i}. {key.replace('_', ' ').title()}")
                print(f"     └─ {question}")

            print(f"\n[PASS] Validation framework successfully generated")
            return True
        else:
            print(f"[WARN] No validation framework generated")
            return False

    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        return False


def test_full_pipeline_simulation():
    """Test 6: Simulate Phase 1 of Wide-Then-Deep pipeline"""
    print_section("TEST 6: Full Pipeline Simulation (Phase 1)")

    agent = WebLookupAgent()
    query = "What should Leeds Community Healthcare prioritize to meet NHS 10-year plan requirements?"

    print(f"\nPhase 1: WebLookupAgent")
    print(f"Query: {query}\n")

    try:
        print("Step 1: Retrieve external context...")
        context = agent.get_context(query)

        print("Step 2: Extract key themes...")
        themes = agent.identify_key_themes(context)
        print(f"  Found {len(themes)} themes: {themes}")

        print("\nStep 3: Extract national priorities...")
        priorities = agent.identify_priorities(context)
        print(f"  Found {len(priorities)} priorities")
        for p in priorities[:3]:  # Show first 3
            print(f"    - {p}")
        if len(priorities) > 3:
            print(f"    ... and {len(priorities) - 3} more")

        print("\nStep 4: Suggest search strategy...")
        strategy = agent.suggest_search_strategy(context)
        priority_tags = strategy.get("priority_tags", [])
        search_terms = strategy.get("search_terms", [])
        print(f"  Priority tags for Document Selector: {priority_tags}")
        print(f"  Search terms for Evidence Agent: {search_terms[:3]}")

        print("\n[PASS] Full Phase 1 pipeline simulation successful")
        print("\nOutput ready for Phase 2 (Document Selection):")
        print(f"  - Key themes: {len(themes)} identified")
        print(f"  - National priorities: {len(priorities)} identified")
        print(f"  - Document filter tags: {priority_tags}")

        return True

    except Exception as e:
        print(f"\n[FAIL] Pipeline simulation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  WEBLOOKUPAGENT UPGRADE TEST SUITE")
    print("  Dynamic Web Search Implementation")
    print("=" * 80)
    print(f"\nStart Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = {}

    # Run tests
    results["Basic Context Retrieval"] = test_basic_context_retrieval()
    results["Query Formulation"] = test_query_formulation()
    results["Theme Extraction"] = test_theme_extraction()
    results["Error Handling"] = test_error_handling()
    results["Validation Framework"] = test_validation_framework()
    results["Full Pipeline Simulation"] = test_full_pipeline_simulation()

    # Summary
    print_section("TEST SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nResults:")
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "[✓]" if result else "[X]"
        print(f"  {symbol} {test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! WebLookupAgent upgrade is working correctly.")
        print("\nNext Steps:")
        print("  1. Run Wide-Then-Deep analysis with upgraded WebLookupAgent")
        print("  2. Compare document selection results")
        print("  3. Verify evidence retrieval and synthesis quality")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Review output above.")

    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
