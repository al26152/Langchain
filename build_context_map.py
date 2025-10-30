#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_context_map.py

Builds the intra-corpus context map without re-ingesting documents.
Creates document relationships, concept groups, and evidence chains.

USAGE:
  python build_context_map.py
"""

import sys
import os
import json
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from analysis.multi_agent.context_mapper import ContextMapBuilder

def main():
    """Build and save the context map."""
    print("\n" + "="*70)
    print("INTRA-CORPUS CONTEXT MAP BUILDER")
    print("="*70)

    # Load environment
    load_dotenv()

    # Initialize ChromaDB
    print("\n[INIT] Loading ChromaDB...")
    try:
        embeddings = OpenAIEmbeddings()
        db = Chroma(
            persist_directory="chroma_db_test",
            embedding_function=embeddings
        )
        print("   [OK] ChromaDB loaded")
    except Exception as e:
        print("   [ERROR] Failed to load ChromaDB: {}".format(e))
        sys.exit(1)

    # Build context map
    print("\n[BUILD] Building context map...")
    try:
        builder = ContextMapBuilder(db)
        context_map = builder.build_map()
    except Exception as e:
        print("   [ERROR] Failed to build context map: {}".format(e))
        sys.exit(1)

    # Save context map
    print("\n[SAVE] Saving context map...")
    try:
        output_path = "context_map.json"
        context_map.save(output_path)
        print("   [OK] Saved to {}".format(output_path))
    except Exception as e:
        print("   [ERROR] Failed to save context map: {}".format(e))
        sys.exit(1)

    # Show details
    print("\n" + "="*70)
    print("CONTEXT MAP DETAILS")
    print("="*70)

    print("\nDocuments: {}".format(len(context_map.documents)))
    print("Concepts: {}".format(len(context_map.concepts)))
    print("Relationships: {}".format(len(context_map.relationships)))
    print("Evidence Chains: {}".format(len(context_map.evidence_chains)))
    print("Concept Groups: {}".format(len(context_map.concept_groups)))

    print("\nCONCEPT GROUPS:")
    for group_name, group in context_map.concept_groups.items():
        print("  {}:".format(group_name))
        print("    - Documents: {}".format(len(group.documents)))
        print("    - Key concepts: {}".format(len(group.concepts)))

    print("\nEVIDENCE CHAINS:")
    for chain in context_map.evidence_chains:
        print("  {}:".format(chain.concept))
        print("    - Problem: {}".format(chain.problem_doc))
        print("    - Response: {}".format(chain.response_doc))
        if chain.effectiveness_doc:
            print("    - Effectiveness: {}".format(chain.effectiveness_doc))

    print("\n" + "="*70)
    print("CONTEXT MAP BUILT SUCCESSFULLY")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
