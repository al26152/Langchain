# --- START OF FILE interactive_query.py (MODIFIED) ---

"""
interactive_query.py

A standalone script to test queries against your Chroma vector store
without modifying the main ingestion pipeline.
"""

import os
from langchain_chroma import Chroma # Corrected import
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from utils import auto_tag # Importing to ensure .env is loaded via utils.py

# --- CONFIGURATION (should match your test_one_doc.py or utils.py) ---
STORE_DIR = "chroma_db_test" # Where Chroma persists embeddings

# --- Initialize Components ---
print("Initializing OpenAI Embeddings client...")
embeddings = OpenAIEmbeddings()

print(f"Loading ChromaDB vector store from {STORE_DIR}...")
if not os.path.exists(STORE_DIR):
    print(f"Error: ChromaDB directory '{STORE_DIR}' not found. "
          "Please run test_one_doc.py first to ingest documents.")
    exit()

vectordb = Chroma(
    persist_directory=STORE_DIR,
    embedding_function=embeddings
)
print("ChromaDB loaded.")

print("Initializing LLM for interactive QA...")
qa_llm = ChatOpenAI(model="gpt-4o", temperature=0.4) # Keep temperature for general Q&A, or try 0.7 for more inference

# --- DEBUGGING PROMPT: This prompt will force the LLM to summarize the context it received ---
# This is TEMPORARY for debugging purposes. You'll switch back to a more direct prompt later.
debugging_qa_prompt = PromptTemplate.from_template(
    "You are an AI assistant helping to understand documents. "
    "First, carefully read and summarize the provided context below, identifying the main topics and any specific entities (e.g., organizations, locations, initiatives) mentioned.\n"
    "Then, based on your understanding of the context, try to answer the question at the end. "
    "If the context *does not contain* relevant information to directly answer or infer the answer to the question, state that clearly and explain why the context was insufficient.\n\n"
    "Context:\n"
    "{context}\n\n"
    "Question: {question}\n"
    "Analysis and Answer:"
)

# Use this debugging prompt for now
interactive_qa_prompt = debugging_qa_prompt


qa_chain = RetrievalQA.from_chain_type(
    llm=qa_llm,
    chain_type="stuff",
    retriever=vectordb.as_retriever(search_kwargs={"k": 8}), # Retrieve more chunks for debugging
    return_source_documents=True,
    chain_type_kwargs={"prompt": interactive_qa_prompt} # Use the debugging prompt
)
print("RetrievalQA chain ready for interactive queries.")

# --- Interactive Query Loop ---
print("\nEnter your questions (type 'exit' or 'quit' to end):")
print("NOTE: For debugging, the AI will first summarize the context it received, then try to answer.")
while True:
    user_query = input("\nYour Question: ")
    if user_query.lower() in ["exit", "quit"]:
        break

    if not user_query.strip():
        print("Please enter a question.")
        continue

    print("Searching for answer...")
    try:
        response = qa_chain.invoke({"query": user_query})
        print("\n--- AI's Analysis and Answer ---")
        print(response["result"])

        if "source_documents" in response and response["source_documents"]:
            print("\n--- Sources Used ---")
            for i, doc in enumerate(response["source_documents"]):
                source_info = f"Source: {doc.metadata.get('source', 'N/A')}"
                page_info = f"Page: {doc.metadata.get('page_number', 'N/A')}"
                theme_info = f"Theme: {doc.metadata.get('theme', 'N/A')}"
                element_type_info = f"Element Type: {doc.metadata.get('element_type', 'N/A')}"
                # Now we will always print snippets to help you debug
                print(f"  [{i+1}] {source_info}, {page_info}, {theme_info}, {element_type_info}")
                print(f"    Snippet: {doc.page_content[:500].replace('\n', ' ')}...") # Print more context

        else:
            print("No specific source documents were retrieved for this query.")

    except Exception as e:
        print(f"An error occurred during the query: {e}")

print("\nExiting interactive query session. Goodbye!")

# --- END OF FILE interactive_query.py (MODIFIED) ---