#!/usr/bin/env python3
"""
Workforce Model Transformation Analysis
Integrated Neighborhood Healthcare Systems for Leeds
"""

import sys
sys.path.insert(0, '.')
import os

from dotenv import load_dotenv
load_dotenv('.env')

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from analysis.multi_agent.orchestrator import Orchestrator

print('\n' + '='*80)
print('WORKFORCE MODEL TRANSFORMATION ANALYSIS')
print('Integrated Healthcare Systems & Neighborhood Delivery Model for Leeds')
print('='*80)
print('\n[SETUP] Initializing multi-agent system...\n')

embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory='chroma_db_test', embedding_function=embeddings)
orchestrator = Orchestrator(db, max_iterations=4, verbose=False)

# Comprehensive strategic query
query = """Based on the NHS 10-Year Plan and the principles of integrated neighborhood healthcare systems:

1. WORKFORCE MODEL TRANSFORMATION: What changes will be needed in human resources and workforce management to support integrated healthcare delivery that spans primary care, secondary care, and third sector organizations? What are the key workforce competencies and organizational structures needed?

2. NEIGHBORHOOD DEFINITION & STRUCTURE: If piloting an integrated neighborhood model in Leeds, how should neighborhoods be defined (population size, geography, services, boundaries)? What are best practices and evidence-based approaches for neighborhood definition in integrated systems?

3. BOUNDARY-SPANNING WORKFORCE: How can the workforce be enabled and empowered to deliver care across organizational boundaries? What are the barriers, enablers, and organizational changes required? What models exist for multi-organization team working?

4. IMPLEMENTATION CONSIDERATIONS: What are the critical success factors, risks, and implementation challenges for rolling out this model? What evidence exists on effective change management for integrated care workforce models?

Please synthesize evidence from policy, strategic plans, and implementation guidance across the documents to provide a comprehensive framework for Leeds."""

print('[EXECUTING] Running comprehensive 4-phase analysis...\n')

# Run wide-then-deep analysis
result = orchestrator.run_wide_then_deep_analysis(query)

# SAVE COMPREHENSIVE REPORT
output_file = 'WORKFORCE_INTEGRATED_CARE_ANALYSIS.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('# Workforce Model Transformation for Integrated Neighborhood Healthcare in Leeds\n\n')
    f.write('## Strategic Analysis Report\n\n')
    f.write(f'**Analysis Date:** October 31, 2025\n')
    f.write(f'**Quality Rating:** {result["quality_rating"]}\n')
    f.write(f'**Confidence Score:** {result["confidence_score"]:.0f}%\n')
    f.write(f'**Analysis Depth:** {result["iterations"]} iterations\n')
    f.write(f'**Sources Consulted:** {result["unique_sources"]} documents\n')
    f.write(f'**Evidence Base:** {result["total_chunks"]} evidence chunks\n\n')
    f.write('---\n\n')
    f.write('## Executive Summary\n\n')
    f.write(result['answer'])
    f.write('\n\n---\n\n')
    f.write('## Detailed Analysis Report\n\n')
    f.write(result['final_report'])

print('\n' + '='*80)
print('ANALYSIS COMPLETE')
print('='*80)
print(f'Quality Rating: {result["quality_rating"]}')
print(f'Confidence Score: {result["confidence_score"]:.0f}%')
print(f'Iterations Run: {result["iterations"]}')
print(f'Sources Consulted: {result["unique_sources"]} documents')
print(f'Evidence Chunks: {result["total_chunks"]}')
print(f'\nReport saved to: {output_file}')
print('='*80 + '\n')
