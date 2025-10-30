"""
Quick RAG Query page - Simple single-pass retrieval for fast answers
"""
import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import configuration
try:
    from config import Config
except ImportError:
    print("[WARNING] Could not import config, using defaults")
    Config = None

from components.results_display import (
    display_source_metadata_table,
    export_to_markdown,
    create_download_button
)

# Page config
st.set_page_config(
    page_title="Quick RAG Query",
    page_icon="⚡",
    layout="wide"
)


@st.cache_resource
def load_chromadb():
    """Load ChromaDB connection."""
    try:
        from langchain_chroma import Chroma
        from langchain_openai import OpenAIEmbeddings

        # Use config for database path
        db_path = Config.CHROMA_DB_PATH if Config else "chroma_db_test"

        vectordb = Chroma(
            persist_directory=db_path,
            embedding_function=OpenAIEmbeddings()
        )
        return vectordb
    except Exception as e:
        st.error(f"Failed to load ChromaDB: {str(e)}")
        return None


@st.cache_resource
def load_llm(model: str = None, temperature: float = None):
    """Load LLM."""
    try:
        from langchain_openai import ChatOpenAI

        # Use config for defaults
        if Config:
            model = model or Config.DEFAULT_LLM_MODEL
            temperature = temperature if temperature is not None else Config.DEFAULT_TEMPERATURE
        else:
            model = model or "gpt-4o"
            temperature = temperature if temperature is not None else 0.5

        return ChatOpenAI(model=model, temperature=temperature)
    except Exception as e:
        st.error(f"Failed to load LLM: {str(e)}")
        return None


def initialize_session_state():
    """Initialize session state variables."""
    if "vectordb" not in st.session_state:
        st.session_state.vectordb = load_chromadb()

    if "current_query_result" not in st.session_state:
        st.session_state.current_query_result = None


def run_rag_query(question: str, k: int = 10, model: str = "gpt-4o") -> dict:
    """
    Run a simple RAG query.

    Args:
        question: The query question
        k: Number of chunks to retrieve
        model: Which LLM model to use

    Returns:
        Result dictionary with answer and sources
    """
    try:
        # Ensure parent path is in sys.path
        import os
        parent_path = str(Path(__file__).parent.parent.parent)
        if parent_path not in sys.path:
            sys.path.insert(0, parent_path)

        # Change to parent directory to help with relative imports
        original_cwd = os.getcwd()
        os.chdir(parent_path)

        try:
            from langchain_chroma import Chroma
            from langchain_openai import OpenAIEmbeddings, ChatOpenAI
            from langchain.chains import RetrievalQA

            # Load resources (use config for defaults)
            db_path = Config.CHROMA_DB_PATH if Config else "chroma_db_test"
            default_temp = Config.DEFAULT_TEMPERATURE if Config else 0.5

            vectordb = Chroma(
                persist_directory=db_path,
                embedding_function=OpenAIEmbeddings()
            )
            llm = ChatOpenAI(model=model, temperature=default_temp)

            # Create QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectordb.as_retriever(search_kwargs={"k": k}),
                return_source_documents=True
            )

            # Run query
            response = qa_chain.invoke({"query": question})

            # Process sources
            sources = []
            unique_docs = set()

            for doc in response.get("source_documents", []):
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                source_name = metadata.get("source", "Unknown")
                unique_docs.add(source_name)

                sources.append({
                    "name": source_name,
                    "date": metadata.get("date", "N/A"),
                    "theme": metadata.get("theme", "N/A"),
                    "audience": metadata.get("audience", "N/A"),
                    "chunks": 1
                })

            # Deduplicate sources by name and count chunks
            sources_dict = {}
            for source in sources:
                name = source["name"]
                if name not in sources_dict:
                    sources_dict[name] = source
                else:
                    sources_dict[name]["chunks"] += 1

            sources = list(sources_dict.values())

            return {
                "question": question,
                "answer": response.get("result", "No answer generated"),
                "sources": sources,
                "unique_sources": len(unique_docs),
                "total_chunks": len(response.get("source_documents", [])),
                "model_used": model
            }
        finally:
            os.chdir(original_cwd)

    except ImportError as e:
        # Show import error so we can debug
        st.warning(f"ℹ️ Using demo results (import: {str(e)[:100]}...)")
        return get_mock_result(question)
    except Exception as e:
        # Show actual runtime errors
        st.error(f"⚠️ Query error: {type(e).__name__}: {str(e)[:200]}")
        st.info("Using demo results instead. Check the error above.")
        return get_mock_result(question)


def get_mock_result(question: str) -> dict:
    """Generate mock result for demonstration."""
    return {
        "question": question,
        "answer": """Based on the available documents, LTHT focuses on:

1. **Service Excellence** - Delivering high-quality acute care services
2. **Workforce Development** - Building capability and resilience in staffing
3. **Integrated Care** - Collaborating with community partners like LCH

Key partnerships are being strengthened through the Integrated Care Board and regular Board-to-Board meetings.""",
        "sources": [
            {"name": "LTHT Annual Report 2024-25", "date": "2024-10", "theme": "Workforce", "audience": "Board Members", "chunks": 3},
            {"name": "NHS 10-year Plan", "date": "2023-01", "theme": "Strategy", "audience": "All", "chunks": 2},
            {"name": "Trust Board Minutes Jan 2025", "date": "2025-01", "theme": "Strategy", "audience": "Board Members", "chunks": 1}
        ],
        "unique_sources": 3,
        "total_chunks": 6,
        "model_used": "gpt-4o"
    }


def display_quick_result(result: dict) -> None:
    """Display quick query results."""
    if not result:
        st.warning("No results to display.")
        return

    st.markdown("---")
    st.subheader("📋 Query Result")

    # Metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Documents Consulted",
            result.get("unique_sources", 0),
            delta="unique sources"
        )

    with col2:
        st.metric(
            "Evidence Chunks",
            result.get("total_chunks", 0),
            delta="text segments"
        )

    with col3:
        st.metric(
            "Model Used",
            result.get("model_used", "gpt-4o"),
            delta="LLM"
        )

    # Answer
    st.markdown("### 📝 Answer")
    st.markdown(result.get("answer", "No answer generated"))

    # Sources
    st.markdown("### 📚 Sources")
    display_source_metadata_table(result.get("sources", []))

    # Export
    st.markdown("---")
    st.subheader("💾 Export Result")

    col1, col2 = st.columns(2)

    # Prepare markdown content
    markdown_content = f"""# Quick Query Result
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Question
{result.get('question', 'N/A')}

## Answer
{result.get('answer', 'No answer generated')}

## Sources
"""

    for source in result.get('sources', []):
        markdown_content += f"- **{source.get('name', 'Unknown')}** ({source.get('date', 'N/A')}) - {source.get('theme', 'N/A')}\n"

    with col1:
        create_download_button(
            markdown_content,
            f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            "markdown"
        )

    with col2:
        json_content = json.dumps(result, indent=2, default=str)
        create_download_button(
            json_content,
            f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "json"
        )


def main():
    """Main app."""
    initialize_session_state()

    st.title("⚡ Quick RAG Query")
    st.markdown("""
    Ask a quick question about NHS documents. Get instant answers with source citations.
    Perfect for lookups, status checks, and factual questions.
    """)

    # Question input (single line)
    question = st.text_input(
        "Enter your question:",
        placeholder="E.g., What are LTHT's strategic priorities?",
        label_visibility="collapsed"
    )

    # Settings in expander
    with st.expander("⚙️ Settings", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            # Use config for k defaults
            if Config:
                default_k = Config.WEB_DEFAULT_K
                max_k = Config.WEB_MAX_K
            else:
                default_k = 10
                max_k = 20

            k = st.slider(
                "Number of Sources (k)",
                min_value=5,
                max_value=max_k,
                value=default_k,
                help="More sources = broader but slower answers"
            )

        with col2:
            # Use config for model options
            if Config:
                models = Config.AVAILABLE_MODELS
            else:
                models = ["gpt-4o", "gpt-4o-mini"]

            model = st.selectbox(
                "Model",
                options=models,
                help="Choose LLM model"
            )

    # Query button
    col1, col2 = st.columns([4, 1])

    with col1:
        query_button = st.button(
            "🔍 Ask Question",
            use_container_width=True,
            type="primary",
            disabled=not question.strip()
        )

    with col2:
        if st.session_state.current_query_result:
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.current_query_result = None
                st.rerun()

    # Run query if button clicked
    if query_button:
        if not question.strip():
            st.error("Please enter a question.")
        else:
            with st.spinner("⏳ Searching documents..."):
                result = run_rag_query(question, k, model)
                st.session_state.current_query_result = result

                # Add to history
                if "query_history" not in st.session_state:
                    st.session_state.query_history = []

                st.session_state.query_history.append({
                    "question": question,
                    "mode": "Quick Query",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "sources": result.get("unique_sources", 0)
                })

    # Display results if available
    if st.session_state.current_query_result:
        display_quick_result(st.session_state.current_query_result)


if __name__ == "__main__":
    main()
