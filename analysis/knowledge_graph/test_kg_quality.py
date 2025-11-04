"""
Knowledge Graph Quality Assessment & Testing Suite

Measures KG quality across multiple dimensions:
- Entity coverage and deduplication
- Relationship accuracy and diversity
- Query expansion effectiveness
- Semantic relationship presence
"""

import json
import os
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple
import statistics


class KGQualityAnalyzer:
    """Analyze and measure knowledge graph quality."""

    def __init__(self, kg_path: str = "knowledge_graph_improved.json"):
        """Initialize with KG file."""
        self.kg_path = kg_path
        self.kg = self._load_kg()
        self.metrics = {}

    def _load_kg(self) -> Dict:
        """Load knowledge graph from JSON."""
        if not os.path.exists(self.kg_path):
            print(f"[ERROR] KG file not found: {self.kg_path}")
            return {"entities": {}, "relationships": []}

        with open(self.kg_path, 'r') as f:
            return json.load(f)

    def analyze_all(self) -> Dict:
        """Run all quality metrics."""
        print("\n" + "="*80)
        print("KNOWLEDGE GRAPH QUALITY ANALYSIS")
        print("="*80 + "\n")

        # Entity Metrics
        self._analyze_entities()

        # Relationship Metrics
        self._analyze_relationships()

        # Connectivity Metrics
        self._analyze_connectivity()

        # Semantic Quality
        self._analyze_semantic_quality()

        # Query Expansion Potential
        self._analyze_expansion_potential()

        # Print Summary
        self._print_summary()

        return self.metrics

    def _analyze_entities(self):
        """Analyze entity coverage and quality."""
        print("\n[ENTITY ANALYSIS]")

        entities = self.kg.get("entities", {})
        total_entities = 0
        type_counts = {}

        for entity_type, entity_list in entities.items():
            count = len(entity_list)
            type_counts[entity_type] = count
            total_entities += count
            print(f"  {entity_type}: {count}")

        self.metrics["total_entities"] = total_entities
        self.metrics["entity_types"] = type_counts

        # Check for duplicates within types
        print("\n  [Duplicate Check]")
        for entity_type, entity_list in entities.items():
            unique = len(set(entity_list))
            duplicates = len(entity_list) - unique
            if duplicates > 0:
                print(f"    WARNING: {entity_type} has {duplicates} duplicates")
            else:
                print(f"    {entity_type}: Clean (no duplicates)")

        self.metrics["has_duplicates"] = any(
            len(entity_list) != len(set(entity_list))
            for entity_list in entities.values()
        )

    def _analyze_relationships(self):
        """Analyze relationship quality and distribution."""
        print("\n[RELATIONSHIP ANALYSIS]")

        relationships = self.kg.get("relationships", [])
        total_rels = len(relationships)

        # Relationship type distribution
        rel_types = Counter(r.get("relationship", "unknown") for r in relationships)

        print(f"  Total relationships: {total_rels}")
        print(f"  Relationship types: {len(rel_types)}")
        print("\n  [Distribution]")

        for rel_type, count in rel_types.most_common():
            percentage = 100 * count / total_rels if total_rels > 0 else 0
            print(f"    {rel_type}: {count} ({percentage:.1f}%)")

        self.metrics["total_relationships"] = total_rels
        self.metrics["relationship_types"] = dict(rel_types)

        # Semantic vs Co-mention ratio
        semantic_rels = total_rels - rel_types.get("mentioned_together_in", 0)
        semantic_ratio = 100 * semantic_rels / total_rels if total_rels > 0 else 0

        print(f"\n  [Semantic Quality]")
        print(f"    Semantic relationships: {semantic_rels} ({semantic_ratio:.2f}%)")
        print(f"    Co-mention relationships: {rel_types.get('mentioned_together_in', 0)} ({100-semantic_ratio:.2f}%)")

        self.metrics["semantic_ratio"] = semantic_ratio
        self.metrics["semantic_count"] = semantic_rels

    def _analyze_connectivity(self):
        """Analyze graph connectivity."""
        print("\n[CONNECTIVITY ANALYSIS]")

        relationships = self.kg.get("relationships", [])
        entities = self.kg.get("entities", {})

        # Build degree map
        degree = defaultdict(int)
        for rel in relationships:
            source = rel.get("source")
            target = rel.get("target")
            if source:
                degree[source] += 1
            if target:
                degree[target] += 1

        # All defined entities
        defined_entities = {e for etype_list in entities.values() for e in etype_list}
        connected_entities = set(degree.keys())

        print(f"  Defined entities: {len(defined_entities)}")
        print(f"  Connected entities: {len(connected_entities)}")
        print(f"  Isolated entities: {len(defined_entities - connected_entities)}")

        # Degree distribution
        if degree:
            degrees = list(degree.values())
            print(f"\n  [Degree Distribution]")
            print(f"    Min degree: {min(degrees)}")
            print(f"    Max degree: {max(degrees)}")
            print(f"    Mean degree: {statistics.mean(degrees):.1f}")
            print(f"    Median degree: {statistics.median(degrees):.1f}")

            # Dead ends (degree 1)
            dead_ends = sum(1 for d in degrees if d == 1)
            print(f"    Dead ends (degree=1): {dead_ends} ({100*dead_ends/len(degree):.1f}%)")

            self.metrics["avg_degree"] = statistics.mean(degrees)
            self.metrics["dead_ends"] = dead_ends

    def _analyze_semantic_quality(self):
        """Analyze semantic relationship quality."""
        print("\n[SEMANTIC QUALITY]")

        relationships = self.kg.get("relationships", [])

        # Filter to semantic relationships
        semantic = [r for r in relationships if r.get("relationship") != "mentioned_together_in"]

        rel_dist = Counter(r.get("relationship") for r in semantic)

        print(f"  High-value relationships: {len(semantic)}")
        print("\n  [Semantic Types]")
        for rel_type, count in rel_dist.most_common(10):
            print(f"    {rel_type}: {count}")

        # Check for confidence scores
        has_confidence = any("confidence" in r for r in relationships)
        print(f"\n  [Confidence Scores]")
        print(f"    Present: {has_confidence}")

        self.metrics["semantic_relationships"] = len(semantic)
        self.metrics["has_confidence"] = has_confidence

    def _analyze_expansion_potential(self):
        """Analyze potential for query expansion."""
        print("\n[QUERY EXPANSION POTENTIAL]")

        relationships = self.kg.get("relationships", [])

        # Find key organizations
        entities = self.kg.get("entities", {})
        orgs = entities.get("ORGANIZATIONS", [])

        print(f"  Key organizations: {len(orgs)}")

        if orgs:
            # Check relationships per org
            org_rels = defaultdict(int)
            for rel in relationships:
                if rel.get("source") in orgs:
                    org_rels[rel.get("source")] += 1
                if rel.get("target") in orgs:
                    org_rels[rel.get("target")] += 1

            if org_rels:
                print(f"\n  [Top Organizations by Connectivity]")
                for org, count in sorted(org_rels.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"    {org}: {count} relationships")

                avg_org_rels = statistics.mean(org_rels.values())
                print(f"\n  Average relationships per org: {avg_org_rels:.1f}")
                self.metrics["avg_org_relationships"] = avg_org_rels

    def _print_summary(self):
        """Print quality summary and recommendations."""
        print("\n" + "="*80)
        print("QUALITY SUMMARY & RECOMMENDATIONS")
        print("="*80 + "\n")

        issues = []
        recommendations = []

        # Check noise level
        semantic_ratio = self.metrics.get("semantic_ratio", 0)
        if semantic_ratio < 5:
            issues.append(f"CRITICAL: Only {semantic_ratio:.2f}% semantic relationships (should be >20%)")
            recommendations.append("Apply noise filtering and enhance relationship extraction")

        # Check for confidence scores
        if not self.metrics.get("has_confidence", False):
            issues.append("No confidence scores on relationships")
            recommendations.append("Add confidence scoring to relationship extraction")

        # Check for duplicates
        if self.metrics.get("has_duplicates", False):
            issues.append("Entity duplicates detected")
            recommendations.append("Run entity deduplication")

        # Check connectivity
        dead_ends = self.metrics.get("dead_ends", 0)
        if dead_ends > 100:
            issues.append(f"High number of isolated entities: {dead_ends}")
            recommendations.append("Remove or enrich isolated entities")

        # Check semantic diversity
        semantic_types = len(self.metrics.get("relationship_types", {})) - 1  # Exclude co-mention
        if semantic_types < 5:
            issues.append(f"Limited semantic relationship types: {semantic_types}")
            recommendations.append("Expand relationship type coverage (partnerships, pathways, etc.)")

        # Print issues
        if issues:
            print("ISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        else:
            print("No major issues detected!")

        # Print recommendations
        if recommendations:
            print("\nRECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        # Quality score
        print(f"\n[QUALITY SCORE]")
        score = self._calculate_quality_score()
        print(f"  Overall: {score}/100")

        if score >= 80:
            print("  Grade: A (Excellent)")
        elif score >= 60:
            print("  Grade: B (Good)")
        elif score >= 40:
            print("  Grade: C (Fair)")
        else:
            print("  Grade: D (Poor)")

    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score (0-100)."""
        score = 50  # Baseline

        # Semantic ratio (0-30 points)
        semantic_ratio = self.metrics.get("semantic_ratio", 0)
        score += min(30, semantic_ratio / 3)  # Max 30 at 90%+ semantic

        # Entity count (0-10 points)
        entity_count = self.metrics.get("total_entities", 0)
        score += min(10, entity_count / 50)  # Max 10 at 500+ entities

        # Relationship diversity (0-10 points)
        rel_types = len(self.metrics.get("relationship_types", {}))
        score += min(10, rel_types)  # Max 10 at 10+ types

        # Connectivity (0-10 points)
        avg_degree = self.metrics.get("avg_degree", 0)
        score += min(10, avg_degree / 5)  # Max 10 at degree 5+

        # No issues bonuses
        if not self.metrics.get("has_duplicates", False):
            score += 5

        if self.metrics.get("has_confidence", False):
            score += 5

        return min(100, score)


def compare_kg_versions(before_path: str, after_path: str):
    """Compare two KG versions."""
    print("\n" + "="*80)
    print("KNOWLEDGE GRAPH COMPARISON (Before vs After)")
    print("="*80 + "\n")

    before = KGQualityAnalyzer(before_path)
    after = KGQualityAnalyzer(after_path)

    before_metrics = before._load_kg() and before.metrics
    after_metrics = after._load_kg() and after.metrics

    # Run analysis if not done
    if not before.metrics:
        before.analyze_all()
    if not after.metrics:
        after.analyze_all()

    print("\n[COMPARISON RESULTS]\n")

    # Entity comparison
    before_entities = before.metrics.get("total_entities", 0)
    after_entities = after.metrics.get("total_entities", 0)
    print(f"Entities: {before_entities} -> {after_entities} ({after_entities-before_entities:+d})")

    # Relationship comparison
    before_rels = before.metrics.get("total_relationships", 0)
    after_rels = after.metrics.get("total_relationships", 0)
    print(f"Relationships: {before_rels} -> {after_rels} ({after_rels-before_rels:+d} / {100*(after_rels-before_rels)/before_rels:+.1f}%)")

    # Semantic ratio
    before_semantic = before.metrics.get("semantic_ratio", 0)
    after_semantic = after.metrics.get("semantic_ratio", 0)
    print(f"Semantic Ratio: {before_semantic:.2f}% -> {after_semantic:.2f}% ({after_semantic-before_semantic:+.2f}%)")

    # Quality score
    before_score = before._calculate_quality_score()
    after_score = after._calculate_quality_score()
    print(f"Quality Score: {before_score:.0f} -> {after_score:.0f} ({after_score-before_score:+.0f})")


if __name__ == "__main__":
    # Analyze current KG
    analyzer = KGQualityAnalyzer("knowledge_graph_improved.json")
    analyzer.analyze_all()

    # Optional: Compare with another version
    # compare_kg_versions("knowledge_graph_improved.json", "knowledge_graph_filtered.json")
