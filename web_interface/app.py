"""
Main Streamlit app - Home page for NHS Strategic Analysis System
"""
import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import configuration
try:
    from config import Config
except ImportError:
    print("[WARNING] Could not import config, using defaults")
    Config = None

# Configure Streamlit (using config if available)
if Config:
    page_title = Config.APP_TITLE
    page_icon = Config.APP_ICON
    layout = Config.LAYOUT
else:
    page_title = "NHS Strategic Analysis System"
    page_icon = "🏥"
    layout = "wide"

st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


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


def get_chromadb_stats() -> dict:
    """Get statistics about ChromaDB contents."""
    try:
        vectordb = load_chromadb()
        if vectordb is None:
            return {
                "documents": 0,
                "chunks": 0,
                "last_updated": "Unknown"
            }

        # Get collection stats
        collection = vectordb.get()
        # ChromaDB returns metadatas as separate list
        doc_count = len(set([meta.get("source", "Unknown") for meta in collection.get("metadatas", []) if isinstance(meta, dict)]))
        chunk_count = len(collection.get("documents", []))

        return {
            "documents": doc_count,
            "chunks": chunk_count,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        st.warning(f"Could not fetch ChromaDB stats: {str(e)}")
        return {
            "documents": 0,
            "chunks": 0,
            "last_updated": "Unknown"
        }


def initialize_session_state():
    """Initialize session state variables."""
    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    if "vectordb" not in st.session_state:
        st.session_state.vectordb = load_chromadb()


def display_query_history():
    """Display query history in sidebar."""
    st.sidebar.markdown("### 📚 Query History")

    if st.session_state.query_history:
        for i, query_record in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5
            with st.sidebar.expander(
                f"Query {len(st.session_state.query_history) - i}: "
                f"{query_record['question'][:40]}...",
                expanded=False
            ):
                st.write(f"**Mode:** {query_record['mode']}")
                st.write(f"**Time:** {query_record['timestamp']}")
                if 'confidence_score' in query_record:
                    st.write(f"**Confidence:** {query_record['confidence_score']}%")
    else:
        st.sidebar.info("No queries yet. Start analyzing to build history.")


def main():
    """Main app."""
    # Initialize session state
    initialize_session_state()

    # Header
    st.markdown('<p class="main-header">🏥 NHS Strategic Analysis System</p>', unsafe_allow_html=True)

    # Tagline
    st.markdown("""
    **Intelligent retrieval-augmented generation for NHS strategic documents**

    Ask strategic questions about NHS priorities, workforce challenges, and care delivery pathways.
    The system analyzes 30+ documents using advanced AI to provide comprehensive, multi-source insights.
    """)

    # System Stats
    st.markdown("---")
    st.subheader("📊 System Status")

    # Get stats
    stats = get_chromadb_stats()

    # Display stats in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📄 Documents Indexed",
            stats["documents"],
            delta="Documents in ChromaDB"
        )

    with col2:
        st.metric(
            "🔤 Text Chunks",
            stats["chunks"],
            delta="Semantic units for retrieval"
        )

    with col3:
        st.metric(
            "🕐 Last Updated",
            stats["last_updated"],
            delta="Time of last refresh"
        )

    # Analysis Mode Selection
    st.markdown("---")
    st.subheader("🎯 Choose Your Analysis Mode")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🤖 Multi-Agent Analysis
        **Recommended for strategic decisions**

        - Iterative retrieval with gap detection
        - Confidence scoring (0-100%)
        - Epistemic breakdown (FACT/ASSUMPTION/INFERENCE)
        - Real-time progress tracking
        - Deep analysis: 2-4 minutes, ~$0.15-0.40

        **Best for:** Complex strategic questions requiring comprehensive analysis
        """)

        if st.button("→ Go to Multi-Agent Analysis", key="btn_multi_agent", use_container_width=True):
            st.switch_page("pages/1_🤖_Multi_Agent_Analysis.py")

    with col2:
        st.markdown("""
        ### ⚡ Quick RAG Query
        **For fast, focused answers**

        - Single-pass retrieval
        - Multi-source synthesis
        - Source citations with dates
        - Instant results: 30-60 seconds, ~$0.02-0.10

        **Best for:** Quick lookups, status checks, specific facts
        """)

        if st.button("→ Go to Quick Query", key="btn_quick_rag", use_container_width=True):
            st.switch_page("pages/2_⚡_Quick_Query.py")

    # Documentation section
    st.markdown("---")
    st.subheader("ℹ️ How It Works")

    with st.expander("📖 System Overview"):
        st.markdown("""
        The NHS Strategic Analysis System uses **Retrieval-Augmented Generation (RAG)** to answer questions
        about NHS strategy across 30+ documents:

        **Documents Included:**
        - NHS 10-year plan and strategic frameworks
        - Trust annual reports (LTHT, LCH, LYPFT)
        - Workforce and service delivery strategies
        - Board meeting minutes and policy guidance

        **Two Analysis Approaches:**

        1. **Multi-Agent Analysis** (Iterative)
           - Evidence Agent retrieves relevant information
           - Critique Agent evaluates quality and identifies gaps
           - Loop repeats until sufficient quality achieved
           - Provides confidence scores and epistemic breakdown

        2. **Quick RAG Query** (Direct)
           - Direct semantic search in document collection
           - LLM synthesis of results
           - Fast, multi-source responses
           - Good for simple factual questions

        **Key Features:**
        - 🔄 Multi-source synthesis (forces 3+ documents)
        - 📅 Date-aware retrieval (flags outdated information)
        - 🧠 Knowledge graph enhancement (entity relationships)
        - 🔍 Transparency (confidence scores, gap detection)
        """)

    with st.expander("❓ Frequently Asked Questions"):
        st.markdown("""
        **Q: What questions can I ask?**
        A: Any strategic question about NHS organizations, workforce, services, or policy.
        Examples: "What are LTHT's workforce challenges?" or "How do LCH and LTHT collaborate?"

        **Q: How long does analysis take?**
        A: Quick queries take 30-60 seconds. Multi-agent analysis takes 2-4 minutes depending
        on the number of iterations needed.

        **Q: How accurate are the answers?**
        A: The system provides confidence scores (0-100%) and breaks down each claim as a FACT,
        ASSUMPTION, or INFERENCE. Use the confidence score to gauge reliability.

        **Q: What does "iterative" mean?**
        A: The system makes multiple passes through documents, detecting gaps in evidence
        and searching for additional information until it has high confidence in the answer.

        **Q: Can I download results?**
        A: Yes! Both analysis modes support exporting results as Markdown or JSON.
        """)

    # Display query history
    display_query_history()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.9rem;'>
    <p>NHS Strategic Analysis System | Powered by RAG + LLM</p>
    <p><em>All analysis is based on documents available in the system as of the last ingestion.</em></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
