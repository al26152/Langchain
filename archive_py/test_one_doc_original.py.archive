# --- START OF FILE test_one_doc.py ---

"""
test_one_doc.py

End-to-end ingestion, auto-tagging, document structure-aware chunking,
Chroma vector store persistence (with overwrite on update), and a sample RetrievalQA query.

This version also saves a formatted Markdown report of all outputs.
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

# --- MAIN INGESTION + QA PIPELINE ———————————————————————————————————

def main():
    # Capture all output for Markdown
    original_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    print("# Strategic Analysis Pipeline Run\n")

    print("## Initialization\n")
    print("Starting document ingestion and QA pipeline...")

    # 1. Full rebuild if enabled
    if FULL_REBUILD:
        print(f"Detected FULL_REBUILD = True. Deleting existing ChromaDB at `{STORE_DIR}`...")
        shutil.rmtree(STORE_DIR, ignore_errors=True)
        print("✅ ChromaDB wiped clean.")

    if not os.path.exists(STORE_DIR):
        print(f"Creating ChromaDB persistence directory: `{STORE_DIR}`")
        os.makedirs(STORE_DIR)

    print("\n## Embedding & Vector Store Setup\n")
    embeddings = OpenAIEmbeddings()
    print("Initialized OpenAI Embeddings client.")
    vectordb = Chroma(persist_directory=STORE_DIR, embedding_function=embeddings)
    print("ChromaDB vector store initialized.")

    existing_sources_in_db = set()
    try:
        all_db_data = vectordb._collection.get(include=["metadatas"])
        for metadata_entry in all_db_data.get("metadatas", []):
            if "source" in metadata_entry:
                existing_sources_in_db.add(metadata_entry["source"])
        print(f"Found **{len(existing_sources_in_db)}** existing document sources in ChromaDB.")
    except Exception as e:
        print(f"Could not retrieve existing document sources (possibly empty DB): {e}")

    if not os.path.exists(DOCS_PATH):
        print(f"❌ Error: Document path `{DOCS_PATH}` does not exist. Please add your documents.")
        sys.stdout = original_stdout
        return

    print(f"\n## Processing Documents from `{DOCS_PATH}`\n")
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
            print(f"⚠️ Error partitioning `{filename}`: {e}")
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
                print(f"- 🏷️ Auto-tagged: **Theme = '{theme}'**, **Audience = '{audience}'**")
            except Exception as e:
                print(f"⚠️ Auto-tagging error: {e}")
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
            print(f"- ✅ Added {len(current_document_chunks)} chunks.")
        else:
            print(f"- ⚠️ No valid chunks extracted.")

    print(f"\n## Ingestion Summary\n")
    print(f"- Processed Files: **{processed_files_count}**")
    print(f"- Total Chunks Ready: **{len(all_chunks_to_add)}**")

    if all_chunks_to_add:
        print("\n### Updating ChromaDB...")
        vectordb.add_documents(all_chunks_to_add)
        print("✅ ChromaDB updated successfully.")
    else:
        print("ℹ️ No updates made to ChromaDB.")

    print("\n## Building Strategic QA Chain\n")
    qa_llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    strategic_prompt_path = "prompts/strategic_foundation_analysis.md"

    default_strategic_qa_prompt = PromptTemplate.from_template(
        "You are an AI assistant specialized in strategic analysis of health documents.\n"
        "Use the following pieces of context to answer the question at the end. "
        "Focus on extracting and synthesizing strategic insights, overarching priorities, key challenges, and emerging trends.\n"
        "If the answer cannot be found in the provided context, state that you don't know.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\nStrategic Analysis Answer:"
    )

    if os.path.exists(strategic_prompt_path):
        with open(strategic_prompt_path, "r", encoding="utf-8") as f:
            custom_prompt = f.read()
        qa_prompt = PromptTemplate.from_template(custom_prompt)
        print(f"Using custom prompt from `{strategic_prompt_path}`")
    else:
        qa_prompt = default_strategic_qa_prompt
        print("Custom strategic prompt not found; using default.")

    qa = RetrievalQA.from_chain_type(
        llm=qa_llm,
        chain_type="stuff",
        retriever=vectordb.as_retriever(search_kwargs={"k": 7}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": qa_prompt}
    )

    print("\n## Executing Sample Strategic Queries\n")
    sample_queries = [
        "What are the overarching strategic priorities for the health sector outlined in these documents?",
        "Analyze the key challenges and obstacles identified in achieving these priorities.",
        "Identify emerging trends or innovative approaches discussed for future development.",
        "What are the primary workforce development strategies across documents?",
        "Compare community health initiatives versus acute care services."
    ]

    for i, query in enumerate(sample_queries):
        print(f"\n### Query {i+1}: {query}")
        response = qa.invoke({"query": query})
        print(f"\n**Answer:**\n{response['result']}\n")

        if "source_documents" in response and response["source_documents"]:
            print("**Key Supporting Documents:**")
            for j, doc in enumerate(response["source_documents"]):
                src = doc.metadata.get("source", "N/A")
                pg = doc.metadata.get("page_number", "N/A")
                theme = doc.metadata.get("theme", "N/A")
                elem = doc.metadata.get("element_type", "N/A")
                print(f"- {j+1}. `{src}` | Page: {pg} | Theme: {theme} | Element: {elem}")

    print("\n---\n✅ Strategic analysis complete.\n")

    # --- Save Markdown Output ---
    sys.stdout = original_stdout
    md_output_path = "strategic_analysis_output.md"
    with open(md_output_path, "w", encoding="utf-8") as md_file:
        md_file.write(captured_output.getvalue())

    print(f"\n✅ Markdown report saved as: {md_output_path}")


if __name__ == "__main__":
    main()

# --- END OF FILE test_one_doc.py ---
