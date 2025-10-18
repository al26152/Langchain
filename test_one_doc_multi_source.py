"""
test_one_doc_multi_source.py

Enhanced version that explicitly leverages multiple sources in QA responses.
Uses a refined prompt strategy to force synthesis across multiple documents.
"""

import os
import re
import shutil
import sys
from io import StringIO
from typing import List, Dict, Any, Tuple

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

from utils import auto_tag
from unstructured.partition.auto import partition
from unstructured.documents.elements import Title, NarrativeText, ListItem, Table, Text

# --- CONFIGURATION ——————————————————————————————————————————————————

DOCS_PATH = "docs"
STORE_DIR = "chroma_db_test"
FULL_REBUILD = False
MIN_ELEMENT_TEXT_LENGTH = 50

# --- MULTI-SOURCE AWARE PROMPTS ———————————————————————————————————

# Prompt that explicitly asks for multi-source synthesis
MULTI_SOURCE_STRATEGIC_PROMPT = """You are an AI assistant specialized in strategic analysis of health documents.

Your task is to synthesize information from MULTIPLE sources to provide comprehensive insights.

IMPORTANT INSTRUCTIONS:
1. You have received context from multiple documents and document sections.
2. For your answer, YOU MUST explicitly cite and synthesize information from AT LEAST 3 different sources.
3. When mentioning a fact or insight, reference which document(s) it comes from using the format [Source: filename].
4. Look for patterns, contradictions, and complementary perspectives across the sources.
5. Clearly separate different viewpoints or priorities from different documents.
6. If sources agree on a point, highlight this consensus. If they differ, explain the difference.

CONTEXT FROM MULTIPLE SOURCES:
{context}

QUESTION: {question}

ANSWER (Must cite at least 3 different sources and synthesize across them):"""

# Simpler multi-source prompt
SIMPLE_MULTI_SOURCE_PROMPT = """You are analyzing healthcare documents. Use information from multiple sources to answer comprehensively.

IMPORTANT: Cite which document each key point comes from using [Source: filename].

Context from multiple documents:
{context}

Question: {question}

Answer:"""


# --- MAIN INGESTION + QA PIPELINE ———————————————————————————————————

def main():
    # Capture all output for Markdown
    original_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    print("# Strategic Analysis Pipeline - Multi-Source Enhanced\n")

    print("## Initialization\n")
    print("Starting document ingestion and QA pipeline with multi-source synthesis...\n")

    # 1. Full rebuild if enabled
    if FULL_REBUILD:
        print(f"Detected FULL_REBUILD = True. Deleting existing ChromaDB at `{STORE_DIR}`...")
        shutil.rmtree(STORE_DIR, ignore_errors=True)
        print("[DONE] ChromaDB wiped clean.\n")

    if not os.path.exists(STORE_DIR):
        print(f"Creating ChromaDB persistence directory: `{STORE_DIR}`\n")
        os.makedirs(STORE_DIR)

    print("## Embedding & Vector Store Setup\n")
    embeddings = OpenAIEmbeddings()
    print("[OK] Initialized OpenAI Embeddings client.\n")
    vectordb = Chroma(persist_directory=STORE_DIR, embedding_function=embeddings)
    print("[OK] ChromaDB vector store initialized.\n")

    existing_sources_in_db = set()
    try:
        all_db_data = vectordb._collection.get(include=["metadatas"])
        for metadata_entry in all_db_data.get("metadatas", []):
            if "source" in metadata_entry:
                existing_sources_in_db.add(metadata_entry["source"])
        print(f"Found **{len(existing_sources_in_db)}** existing document sources in ChromaDB.\n")
    except Exception as e:
        print(f"Could not retrieve existing document sources (possibly empty DB): {e}\n")

    if not os.path.exists(DOCS_PATH):
        print(f"[ERROR] Document path `{DOCS_PATH}` does not exist. Please add your documents.")
        sys.stdout = original_stdout
        return

    print(f"## Processing Documents from `{DOCS_PATH}`\n")
    processed_files_count = 0
    all_chunks_to_add = []

    for filename in sorted(os.listdir(DOCS_PATH)):
        if not filename.endswith((".md", ".txt")):
            continue

        file_path = os.path.join(DOCS_PATH, filename)
        print(f"### Processing File: `{filename}`")

        if not FULL_REBUILD and filename in existing_sources_in_db:
            print(f"- Removing old chunks for `{filename}`...")
            vectordb._collection.delete(where={"source": filename})

        try:
            elements = partition(filename=file_path)
            print(f"- Partitioned into {len(elements)} raw elements.")
        except Exception as e:
            print(f"[WARN] Error partitioning `{filename}`: {e}")
            continue

        doc_content_for_tagging = ""
        for element in elements:
            if hasattr(element, "text") and isinstance(element.text, str) and element.text.strip():
                if isinstance(element, (Title, NarrativeText, Text)):
                    doc_content_for_tagging += element.text + " "
                if len(doc_content_for_tagging) >= 1000:
                    break

        theme, audience = "unknown", "unknown"
        if doc_content_for_tagging.strip():
            try:
                theme, audience = auto_tag(doc_content_for_tagging.strip())
                print(f"- Auto-tagged: **Theme = '{theme}'**, **Audience = '{audience}'**")
            except Exception as e:
                print(f"[WARN] Auto-tagging error: {e}")
        else:
            print("- No sufficient text for auto-tagging. Using defaults.")

        current_document_chunks = []
        for i, element in enumerate(elements):
            if not hasattr(element, "text") or not isinstance(element.text, str):
                continue
            text_content = element.text.strip()
            if not text_content or len(text_content) < MIN_ELEMENT_TEXT_LENGTH:
                continue

            chunk_id = f"{filename}_element_{i}_{hash(text_content[:min(len(text_content), 500)])}"
            metadata = {
                "id": chunk_id,
                "source": filename,
                "theme": theme,
                "audience": audience,
                "element_type": type(element).__name__,
                "page_number": getattr(element.metadata, "page_number", "N/A"),
            }

            for key in [
                "filename", "file_directory", "filetype", "languages", "category", "url",
                "last_modified", "sent_from", "sent_to", "subject"
            ]:
                value = getattr(element.metadata, key, None)
                if value is not None and key not in metadata:
                    if isinstance(value, (str, int, float, bool)):
                        metadata[key] = value
                    elif key == "languages" and isinstance(value, list) and value:
                        metadata[key] = ", ".join(value)

            current_document_chunks.append(Document(page_content=text_content, metadata=metadata))

        if current_document_chunks:
            all_chunks_to_add.extend(current_document_chunks)
            processed_files_count += 1
            print(f"- [OK] Added {len(current_document_chunks)} chunks.\n")
        else:
            print(f"- [WARN] No valid chunks extracted.\n")

    print(f"## Ingestion Summary\n")
    print(f"- Processed Files: **{processed_files_count}**")
    print(f"- Total Chunks Ready: **{len(all_chunks_to_add)}**\n")

    if all_chunks_to_add:
        print("### Updating ChromaDB...")
        vectordb.add_documents(all_chunks_to_add)
        print("[OK] ChromaDB updated successfully.\n")
    else:
        print("[INFO] No updates made to ChromaDB.\n")

    print("## Building Multi-Source Strategic QA Chain\n")
    qa_llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

    # Use the multi-source aware prompt
    multi_source_prompt = PromptTemplate.from_template(MULTI_SOURCE_STRATEGIC_PROMPT)
    print(f"Using MULTI-SOURCE aware prompt to force synthesis across documents.\n")

    qa = RetrievalQA.from_chain_type(
        llm=qa_llm,
        chain_type="stuff",
        retriever=vectordb.as_retriever(search_kwargs={"k": 10}),  # Retrieve MORE chunks
        return_source_documents=True,
        chain_type_kwargs={"prompt": multi_source_prompt}
    )

    print("## Executing Sample Strategic Queries with Multi-Source Synthesis\n")
    sample_queries = [
        "What are the overarching strategic priorities for the health sector outlined in these documents?",
        "Analyze the key challenges and obstacles identified in achieving these priorities.",
        "Identify emerging trends or innovative approaches discussed for future development.",
        "What are the primary workforce development strategies across documents?",
        "Compare community health initiatives versus acute care services."
    ]

    for i, query in enumerate(sample_queries):
        print(f"\n### Query {i+1}: {query}\n")
        response = qa.invoke({"query": query})
        print(f"**Answer:**\n{response['result']}\n")

        if "source_documents" in response and response["source_documents"]:
            # Analyze source diversity
            sources_used = {}
            for doc in response["source_documents"]:
                src = doc.metadata.get("source", "N/A")
                sources_used[src] = sources_used.get(src, 0) + 1

            unique_sources = len(sources_used)
            print(f"**Source Summary:** {unique_sources} unique document(s) referenced\n")

            print("**All Retrieved Chunks:**")
            for j, doc in enumerate(response["source_documents"]):
                src = doc.metadata.get("source", "N/A")
                pg = doc.metadata.get("page_number", "N/A")
                theme = doc.metadata.get("theme", "N/A")
                elem = doc.metadata.get("element_type", "N/A")
                print(f"- {j+1}. `{src}` | Theme: {theme}")
                print(f"    Snippet: {doc.page_content[:200].replace(chr(10), ' ')}...\n")

    print("---\n[COMPLETE] Multi-source strategic analysis complete.\n")

    # --- Save Markdown Output ---
    sys.stdout = original_stdout
    md_output_path = "strategic_analysis_output_multi_source.md"
    with open(md_output_path, "w", encoding="utf-8") as md_file:
        md_file.write(captured_output.getvalue())

    print(f"\nENHANCED MARKDOWN REPORT SAVED: {md_output_path}")
    print("Compare this with strategic_analysis_output.md to see the improvements in multi-source synthesis!")


if __name__ == "__main__":
    main()
