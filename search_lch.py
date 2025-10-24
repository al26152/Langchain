#!/usr/bin/env python3
"""
search_lch.py

Search ChromaDB for mentions of Leeds Community Healthcare (LCH)
"""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vectordb = Chroma(persist_directory="chroma_db_test", embedding_function=embeddings)

print("=" * 80)
print("SEARCHING FOR LEEDS COMMUNITY HEALTHCARE (LCH) IN DOCUMENTS")
print("=" * 80)

search_terms = [
    "Leeds Community Healthcare NHS Trust",
    "LCH",
    "Leeds Community Healthcare",
    "Community Healthcare Trust Leeds",
]

for term in search_terms:
    print(f"\n[{term}]")
    try:
        results = vectordb.similarity_search(term, k=5)
        if results:
            print(f"Found {len(results)} relevant chunks:\n")
            for i, doc in enumerate(results[:3], 1):
                source = doc.metadata.get('source', 'unknown')
                content = doc.page_content[:250].replace('\n', ' ')
                print(f"  {i}. Source: {source}")
                print(f"     {content}...\n")
        else:
            print("  No results found\n")
    except Exception as e:
        print(f"  Error: {e}\n")

print("=" * 80)
