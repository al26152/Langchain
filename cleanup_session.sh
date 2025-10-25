#!/bin/bash
# Cleanup script to remove development/test files

cd "C:\Users\al261\OneDrive\Documents\Langchain"

echo "Cleaning up development and test files..."
echo "=========================================="

# Remove old version scripts
echo "Removing old version scripts..."
rm -f build_knowledge_graph_v2.py
rm -f build_knowledge_graph_v3.py
rm -f build_single_doc_graph.py

# Remove test/analysis scripts
echo "Removing test and analysis scripts..."
rm -f build_knowledge_graph_explicit.py
rm -f build_knowledge_graph_context_aware.py
rm -f analyze_entity_coverage.py
rm -f analyze_document_structure.py
rm -f check_lch_relationships.py
rm -f check_metadata.py
rm -f deduplicate_organizations.py
rm -f fix_missing_entities.py
rm -f investigate_lch_services.py
rm -f query_graph.py
rm -f search_lch.py
rm -f visualize_improved_graph.py
rm -f visualize_with_implicit_rels.py
rm -f cleanup_reserved_files.py

# Remove test JSON outputs
echo "Removing test JSON outputs..."
rm -f knowledge_graph_explicit.json
rm -f knowledge_graph_context_aware.json

# Remove old visualizations (keep only the cleaned one)
echo "Removing old visualizations..."
rm -f knowledge_graph_balanced_visualization.html
rm -f knowledge_graph_framework_visualization.html

# Remove old analysis markdown files (keep only the final ones)
echo "Removing old analysis files..."
rm -f ANALYSIS_OUTPUTS_COMPARISON.md
rm -f ORGANIZATIONAL_ALIGNMENT_ANALYSIS.md
rm -f ORGANIZATIONAL_ALIGNMENT_FACT_INFERENCE_ANALYSIS.md
rm -f PAIN_POINTS_CLEAR_ANALYSIS.md
rm -f PAIN_POINTS_FACT_VS_INFERENCE.md
rm -f RAG_PATHWAY_COMPREHENSIVE_SYNTHESIS.md

# Remove logs
echo "Removing log files..."
rm -f rag_full_output.log

# Remove temporary directories
echo "Removing temporary directories..."
rm -rf _ul

echo ""
echo "=========================================="
echo "Cleanup complete!"
echo ""
