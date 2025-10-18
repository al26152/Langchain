"""
interactive_query_multi_source.py

Enhanced interactive query interface that explicitly tracks and enforces
multi-source synthesis in answers.
"""

import os
from collections import defaultdict
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from utils import auto_tag  # Ensures .env is loaded

# --- CONFIGURATION ---
STORE_DIR = "chroma_db_test"

# --- MULTI-SOURCE SYNTHESIS PROMPT ---
MULTI_SOURCE_PROMPT = """You are an AI assistant specialized in strategic analysis of healthcare documents.

CRITICAL INSTRUCTION: You MUST synthesize information from MULTIPLE sources (at least 3) in your answer.

When answering:
1. Explicitly cite which document each key fact comes from: [Source: document_name]
2. Identify agreements between documents (consensus)
3. Identify disagreements or different priorities between documents
4. Synthesize insights that combine perspectives from multiple sources
5. Explain how different documents complement or inform each other

CONTEXT (from multiple documents):
{context}

QUESTION: {question}

ANSWER (Must cite and synthesize from at least 3 different sources):"""

# --- UTILITY FUNCTIONS ---

def analyze_source_coverage(source_documents):
    """Analyze how many unique sources were retrieved."""
    source_counts = defaultdict(int)
    for doc in source_documents:
        source = doc.metadata.get("source", "Unknown")
        source_counts[source] += 1
    return source_counts


def print_source_analysis(source_documents):
    """Pretty print source coverage statistics."""
    source_counts = analyze_source_coverage(source_documents)
    print("\n📊 SOURCE COVERAGE ANALYSIS:")
    print(f"   Total chunks retrieved: {len(source_documents)}")
    print(f"   Unique sources: {len(source_counts)}")
    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {source}: {count} chunk(s)")


# --- INITIALIZE COMPONENTS ---
print("Initializing OpenAI Embeddings client...")
embeddings = OpenAIEmbeddings()

print(f"Loading ChromaDB vector store from {STORE_DIR}...")
if not os.path.exists(STORE_DIR):
    print(f"❌ Error: ChromaDB directory '{STORE_DIR}' not found.")
    print("   Please run test_one_doc.py first to ingest documents.")
    exit()

vectordb = Chroma(
    persist_directory=STORE_DIR,
    embedding_function=embeddings
)
print("✅ ChromaDB loaded.\n")

print("Initializing LLM for multi-source QA...")
qa_llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

# Create multi-source aware prompt
multi_source_prompt = PromptTemplate.from_template(MULTI_SOURCE_PROMPT)

# Build the QA chain with higher k value to retrieve more sources
qa_chain = RetrievalQA.from_chain_type(
    llm=qa_llm,
    chain_type="stuff",
    retriever=vectordb.as_retriever(search_kwargs={"k": 10}),  # Retrieve 10 chunks instead of 7-8
    return_source_documents=True,
    chain_type_kwargs={"prompt": multi_source_prompt}
)

print("✅ RetrievalQA chain ready.\n")
print("=" * 70)
print("MULTI-SOURCE INTERACTIVE QUERY SESSION")
print("This version explicitly enforces synthesis across multiple documents.")
print("=" * 70)
print("\nEnter your questions (type 'exit' or 'quit' to end):\n")

# --- INTERACTIVE LOOP ---
while True:
    user_query = input("\n🔍 Your Question: ").strip()

    if user_query.lower() in ["exit", "quit"]:
        print("\n👋 Exiting. Goodbye!")
        break

    if not user_query:
        print("⚠️  Please enter a question.")
        continue

    print("\n⏳ Searching for answer across multiple sources...\n")

    try:
        response = qa_chain.invoke({"query": user_query})

        # Display answer
        print("=" * 70)
        print("📝 ANSWER:")
        print("=" * 70)
        print(response["result"])
        print()

        # Display source analysis
        if "source_documents" in response and response["source_documents"]:
            print_source_analysis(response["source_documents"])

            # Display detailed source info
            print("\n📚 DETAILED SOURCES:")
            source_counts = analyze_source_coverage(response["source_documents"])

            for i, doc in enumerate(response["source_documents"]):
                source = doc.metadata.get("source", "Unknown")
                theme = doc.metadata.get("theme", "N/A")
                element = doc.metadata.get("element_type", "N/A")

                print(f"\n   [{i+1}] Source: {source}")
                print(f"       Theme: {theme}")
                print(f"       Type: {element}")
                print(f"       Snippet: {doc.page_content[:150].replace(chr(10), ' ')}...")

        print("\n" + "=" * 70)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please try again with a different question.")

print("\n✨ Query session ended.")
