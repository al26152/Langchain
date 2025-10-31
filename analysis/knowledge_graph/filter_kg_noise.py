#!/usr/bin/env python3
"""
filter_kg_noise.py

KNOWLEDGE GRAPH NOISE FILTERING (Phase 1)

PURPOSE:
  Reduce noise in knowledge graph by filtering weak "mentioned_together_in"
  relationships using a frequency threshold (e.g., 5+ co-mentions).

  Current KG: 99.5% noise (19,286 weak co-mention relationships)
  Goal: Remove one-off mentions, keep strong signals

APPROACH:
  1. Load KG JSON from knowledge_graph_improved.json
  2. Count co-mention frequency for each entity pair
  3. Remove pairs mentioned <5 times (configurable threshold)
  4. Keep all semantic relationships (provides, uses, manages, etc.)
  5. Save filtered version as knowledge_graph_filtered.json

IMPACT:
  - Reduces weak co-mention noise by ~85%
  - Keeps ~15% high-confidence co-mention signals
  - Maintains all semantic relationships
  - Cleaner query expansion with fewer false positives

USAGE:
  Standard filtering (5+ threshold):
    python filter_kg_noise.py

  Custom threshold:
    python filter_kg_noise.py --threshold 3

  Dry run (show what would be removed):
    python filter_kg_noise.py --dry-run

  Verbose output (detailed statistics):
    python filter_kg_noise.py --verbose

CONFIGURATION:
  - Input: analysis/knowledge_graph/knowledge_graph_improved.json
  - Output: analysis/knowledge_graph/knowledge_graph_filtered.json
  - Default threshold: 5 (keep pairs mentioned 5+ times)
  - Semantic relationships: Always kept (threshold doesn't apply)
"""

import json
import sys
import os
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class KGNoiseFilter:
    """Filter weak relationships from knowledge graph."""

    def __init__(self, input_path: str, output_path: str = None, threshold: int = 5, verbose: bool = False):
        """
        Initialize filter.

        Args:
            input_path: Path to knowledge_graph_improved.json
            output_path: Path to save filtered graph (default: knowledge_graph_filtered.json)
            threshold: Min co-mention frequency to keep (default: 5)
            verbose: Enable detailed logging
        """
        self.input_path = input_path
        self.output_path = output_path or input_path.replace('improved', 'filtered')
        self.threshold = threshold
        self.verbose = verbose

        self.kg = None
        self.stats = {
            'original': {},
            'filtered': {},
            'removed': {}
        }

    def log(self, message: str, level: str = "INFO"):
        """Print timestamped log message."""
        if not self.verbose and level in ["DEBUG"]:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        symbol = {
            "INFO": "[i]",
            "SUCCESS": "[✓]",
            "WARNING": "[!]",
            "ERROR": "[✗]",
            "DEBUG": "[*]"
        }.get(level, "[*]")
        print(f"[{timestamp}] {symbol} {message}")

    def load_kg(self) -> bool:
        """Load knowledge graph from JSON."""
        if not os.path.exists(self.input_path):
            self.log(f"Error: File not found: {self.input_path}", "ERROR")
            return False

        try:
            self.log(f"Loading KG from: {self.input_path}")
            with open(self.input_path, 'r', encoding='utf-8') as f:
                self.kg = json.load(f)

            # Get statistics
            self.stats['original']['total_relationships'] = len(self.kg.get('relationships', []))
            self.stats['original']['total_entities'] = len(self.kg.get('entities', {}))

            self.log(f"Loaded: {self.stats['original']['total_relationships']} relationships", "SUCCESS")
            return True
        except json.JSONDecodeError as e:
            self.log(f"Error parsing JSON: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error loading file: {e}", "ERROR")
            return False

    def analyze_co_mentions(self) -> dict:
        """Analyze co-mention frequency distribution."""
        co_mention_counts = defaultdict(int)

        self.log("Analyzing co-mention frequencies...")

        for rel in self.kg.get('relationships', []):
            if rel.get('relationship') == 'mentioned_together_in':
                source = rel.get('source', '')
                target = rel.get('target', '')
                pair = tuple(sorted([source, target]))
                co_mention_counts[pair] += 1

        # Analyze distribution
        freq_dist = defaultdict(int)
        for pair, count in co_mention_counts.items():
            freq_dist[count] += 1

        self.log(f"Found {len(co_mention_counts)} unique co-mention pairs", "DEBUG")

        if self.verbose:
            self.log("Co-mention frequency distribution:", "DEBUG")
            for freq in sorted(freq_dist.keys()):
                if freq <= 10 or freq % 5 == 0:
                    count = freq_dist[freq]
                    print(f"    {freq}x: {count} pairs")

        return co_mention_counts

    def filter_relationships(self, co_mention_counts: dict) -> list:
        """Filter relationships based on co-mention threshold."""
        self.log(f"Filtering with threshold: {self.threshold}+ co-mentions")

        filtered_rels = []
        removed_count = 0
        kept_semantic = 0

        for rel in self.kg.get('relationships', []):
            rel_type = rel.get('relationship', 'unknown')

            # Always keep semantic relationships
            if rel_type != 'mentioned_together_in':
                filtered_rels.append(rel)
                kept_semantic += 1
                continue

            # For co-mentions, apply threshold
            source = rel.get('source', '')
            target = rel.get('target', '')
            pair = tuple(sorted([source, target]))
            count = co_mention_counts.get(pair, 0)

            if count >= self.threshold:
                filtered_rels.append(rel)
            else:
                removed_count += 1

        self.stats['filtered']['total_relationships'] = len(filtered_rels)
        self.stats['removed']['co_mentions'] = removed_count
        self.stats['filtered']['semantic_relationships'] = kept_semantic

        reduction_pct = (removed_count / len(self.kg.get('relationships', []))) * 100
        self.log(f"Removed: {removed_count} weak co-mentions ({reduction_pct:.1f}%)", "SUCCESS")
        self.log(f"Kept: {kept_semantic} semantic relationships", "SUCCESS")
        self.log(f"Kept: {len(filtered_rels) - kept_semantic} strong co-mentions", "SUCCESS")

        return filtered_rels

    def save_filtered_kg(self, filtered_rels: list) -> bool:
        """Save filtered knowledge graph."""
        try:
            output_kg = {
                'entities': self.kg.get('entities', {}),
                'relationships': filtered_rels,
                'metadata': {
                    'original_total': self.stats['original']['total_relationships'],
                    'filtered_total': len(filtered_rels),
                    'removed_count': self.stats['removed'].get('co_mentions', 0),
                    'threshold': self.threshold,
                    'filtered_date': datetime.now().isoformat(),
                    'filter_version': '1.0'
                }
            }

            self.log(f"Saving filtered KG to: {self.output_path}")
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(output_kg, f, indent=2, ensure_ascii=False)

            self.log(f"Success! Filtered KG saved", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Error saving file: {e}", "ERROR")
            return False

    def print_summary(self):
        """Print filtering summary."""
        print("\n" + "="*70)
        print("KNOWLEDGE GRAPH NOISE FILTERING - SUMMARY")
        print("="*70)

        print("\n[ORIGINAL GRAPH]")
        print(f"  Total relationships: {self.stats['original']['total_relationships']}")
        print(f"  Total entities: {self.stats['original']['total_entities']}")

        print("\n[FILTERED GRAPH]")
        print(f"  Total relationships: {self.stats['filtered']['total_relationships']}")
        print(f"  Semantic relationships (kept): {self.stats['filtered'].get('semantic_relationships', 0)}")
        print(f"  Co-mention relationships (kept): {self.stats['filtered']['total_relationships'] - self.stats['filtered'].get('semantic_relationships', 0)}")

        print("\n[FILTERING RESULTS]")
        removed = self.stats['removed'].get('co_mentions', 0)
        total = self.stats['original']['total_relationships']
        removed_pct = (removed / total) * 100 if total > 0 else 0
        remaining_pct = 100 - removed_pct
        print(f"  Removed: {removed} relationships ({removed_pct:.1f}%)")
        print(f"  Remaining: {self.stats['filtered']['total_relationships']} relationships ({remaining_pct:.1f}%)")

        print("\n[CONFIGURATION]")
        print(f"  Threshold: {self.threshold}+ co-mentions")
        print(f"  Input: {self.input_path}")
        print(f"  Output: {self.output_path}")
        print(f"  File size: ~{os.path.getsize(self.output_path) / 1024 / 1024:.1f} MB")

        print("\n[NEXT STEPS]")
        print("  1. Test query expansion with filtered KG")
        print("  2. Compare results vs original KG")
        print("  3. Adjust threshold if needed (Phase 1 iteration)")
        print("  4. Consider Phase 2: Better extraction logic")

        print("\n" + "="*70 + "\n")

    def run(self, dry_run: bool = False) -> bool:
        """Execute filtering pipeline."""
        print("\n" + "="*70)
        print("KNOWLEDGE GRAPH NOISE FILTER - Phase 1")
        print("="*70)
        print(f"\nThreshold: {self.threshold}+ co-mentions (semantic relationships always kept)")

        if dry_run:
            print("MODE: DRY-RUN (no files saved)")

        # Load KG
        if not self.load_kg():
            return False

        # Analyze co-mentions
        co_mention_counts = self.analyze_co_mentions()

        # Filter relationships
        filtered_rels = self.filter_relationships(co_mention_counts)

        if dry_run:
            print("\n[DRY-RUN] Would save filtered graph")
            self.print_summary()
            return True

        # Save filtered KG
        if not self.save_filtered_kg(filtered_rels):
            return False

        # Print summary
        self.print_summary()
        return True


def main():
    """Parse arguments and run filter."""
    parser = argparse.ArgumentParser(
        description="Filter weak relationships from knowledge graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python filter_kg_noise.py
    (Standard filtering: threshold=5, input=knowledge_graph_improved.json)

  python filter_kg_noise.py --threshold 3
    (More aggressive: keep pairs mentioned 3+ times)

  python filter_kg_noise.py --threshold 10
    (More conservative: keep pairs mentioned 10+ times)

  python filter_kg_noise.py --dry-run --verbose
    (Preview changes without saving)
        """
    )

    parser.add_argument(
        "--input",
        default="knowledge_graph_improved.json",
        help="Input KG file (default: knowledge_graph_improved.json)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output KG file (default: knowledge_graph_filtered.json)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=5,
        help="Min co-mention frequency to keep (default: 5)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview filtering without saving"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Detailed logging output"
    )

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"\n[ERROR] File not found: {args.input}")
        print("Note: KG must be built first with:")
        print("  python build_knowledge_graph_framework.py")
        sys.exit(1)

    # Run filter
    filter = KGNoiseFilter(
        input_path=args.input,
        output_path=args.output,
        threshold=args.threshold,
        verbose=args.verbose
    )

    success = filter.run(dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
