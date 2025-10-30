"""
Multi-Agent Analysis page - Iterative RAG with real-time progress tracking
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
    display_confidence_badge,
    display_epistemic_chart,
    display_source_metadata_table,
    export_to_markdown,
    create_download_button
)
from components.progress_tracker import ProgressTracker

# Page config
st.set_page_config(
    page_title="Multi-Agent Analysis",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .question-input {
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_chromadb():
    """Load ChromaDB connection."""
    try:
        from langchain_chroma import Chroma
        from langchain_openai import OpenAIEmbeddings

        vectordb = Chroma(
            persist_directory="chroma_db_test",
            embedding_function=OpenAIEmbeddings()
        )
        return vectordb
    except Exception as e:
        st.error(f"Failed to load ChromaDB: {str(e)}")
        return None


@st.cache_resource
def load_llm(model: str = "gpt-4o", temperature: float = 0.5):
    """Load LLM."""
    try:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, temperature=temperature)
    except Exception as e:
        st.error(f"Failed to load LLM: {str(e)}")
        return None


def initialize_session_state():
    """Initialize session state variables."""
    if "vectordb" not in st.session_state:
        st.session_state.vectordb = load_chromadb()

    if "current_analysis_result" not in st.session_state:
        st.session_state.current_analysis_result = None

    if "analysis_in_progress" not in st.session_state:
        st.session_state.analysis_in_progress = False


def transform_orchestrator_result(raw_result: dict) -> dict:
    """Transform orchestrator result format to UI format."""
    # Extract epistemic breakdown
    epistemic_summary = raw_result.get("epistemic_summary", {})
    epistemic_breakdown = {}
    if isinstance(epistemic_summary, dict):
        for key in ["FACT", "ASSUMPTION", "INFERENCE"]:
            count = epistemic_summary.get(f"{key.lower()}_count", 0)
            if count > 0:
                epistemic_breakdown[key] = count

    # Extract sources from iteration results
    sources = []
    seen_sources = set()
    for iteration in raw_result.get("all_iteration_results", []):
        for evidence in iteration.get("evidence", []):
            source_name = evidence.get("source", "Unknown")
            if source_name not in seen_sources:
                seen_sources.add(source_name)
                sources.append({
                    "name": source_name,
                    "date": evidence.get("date", "N/A"),
                    "theme": evidence.get("theme", "N/A"),
                    "chunks": 1
                })
            else:
                # Increment chunk count
                for s in sources:
                    if s["name"] == source_name:
                        s["chunks"] += 1
                        break

    # Build iteration log
    iterations_log = []
    for i, (iteration, critique) in enumerate(zip(
        raw_result.get("all_iteration_results", []),
        raw_result.get("all_critique_results", [])
    ), 1):
        iterations_log.append({
            "iteration": i,
            "chunks_retrieved": len(iteration.get("evidence", [])),
            "documents": len(set(e.get("source") for e in iteration.get("evidence", []))),
            "quality": critique.get("overall_quality", "UNKNOWN"),
            "gaps": [g.get("description", str(g)) for g in critique.get("gaps", [])],
            "decision": "Continue - expand search" if critique.get("continue_iteration") else "Stop - sufficient quality"
        })

    return {
        "question": raw_result.get("query", ""),
        "answer": raw_result.get("answer", ""),
        "confidence_score": raw_result.get("confidence_score", 0),
        "quality_rating": raw_result.get("quality_rating", "UNKNOWN"),
        "unique_sources": raw_result.get("unique_sources", 0),
        "total_chunks": raw_result.get("total_chunks", 0),
        "iterations": raw_result.get("iterations", 0),
        "epistemic_breakdown": epistemic_breakdown,
        "sources": sources,
        "gaps_identified": [],  # Can extract from final critique if needed
        "iterations_log": iterations_log
    }


def run_mock_analysis(question: str, max_iterations: int, model: str, temperature: float, k: int) -> dict:
    """
    Run multi-agent analysis with actual orchestrator.

    Falls back to mock data if analysis modules not available.
    """
    import os
    import traceback

    try:
        # Get paths
        parent_path = str(Path(__file__).parent.parent.parent)
        print(f"DEBUG: parent_path = {parent_path}")
        print(f"DEBUG: Current working dir = {os.getcwd()}")
        print(f"DEBUG: sys.path[0] = {sys.path[0]}")

        # Ensure parent path is in sys.path
        if parent_path not in sys.path:
            sys.path.insert(0, parent_path)
            print(f"DEBUG: Added parent_path to sys.path")

        # Don't change directory - it breaks relative imports
        # Just ensure proper sys.path
        print(f"DEBUG: About to import Orchestrator...")
        from analysis.multi_agent.orchestrator import Orchestrator
        print(f"DEBUG: Successfully imported Orchestrator!")

        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain_chroma import Chroma

        # Load resources
        print(f"DEBUG: Loading ChromaDB...")

        # Use config for database path
        db_path = Config.CHROMA_DB_PATH if Config else "chroma_db_test"

        vectordb = Chroma(
            persist_directory=db_path,
            embedding_function=OpenAIEmbeddings()
        )
        llm = ChatOpenAI(model=model, temperature=temperature)

        # Create orchestrator
        print(f"DEBUG: Creating Orchestrator instance...")
        orchestrator = Orchestrator(vectordb, llm, max_iterations=max_iterations)
        print(f"DEBUG: Orchestrator created successfully!")

        # Run analysis
        print(f"DEBUG: Running analysis for question: {question[:50]}...")
        print(f"[TOKEN-TRACKING] Starting real LLM-based analysis...")
        raw_result = orchestrator.run_analysis(question)
        print(f"DEBUG: Analysis complete!")
        print(f"[TOKEN-TRACKING] Analysis used REAL LLMs - check OpenAI usage for confirmation")

        # Transform orchestrator result to UI format
        result = transform_orchestrator_result(raw_result)
        return result

    except ImportError as e:
        error_msg = str(e)
        tb = traceback.format_exc()
        st.error(f"❌ Import Error: {error_msg}")
        st.code(tb, language="python")
        st.warning("Using demo results instead")
        print(f"[TOKEN-TRACKING] FAILED - Using mock data instead (ImportError)")
        print(f"DEBUG - ImportError: {error_msg}")
        print(tb)
        return get_mock_result(question)
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        tb = traceback.format_exc()
        st.error(f"❌ Analysis Error: {error_msg}")
        st.code(tb, language="python")
        st.warning("Using demo results instead")
        print(f"[TOKEN-TRACKING] FAILED - Using mock data instead ({type(e).__name__})")
        print(f"DEBUG - Exception: {error_msg}")
        print(tb)
        return get_mock_result(question)


def get_mock_result(question: str) -> dict:
    """Generate mock result for demonstration."""
    return {
        "question": question,
        "answer": """Based on analysis of multiple NHS strategic documents, the key priorities include:

1. **Workforce Development**
   - Recruitment and retention challenges across all trusts
   - Skills development in emerging care pathways
   - Leadership pipeline development

2. **Service Integration**
   - Closer collaboration between acute and community services
   - Enhanced discharge planning processes
   - Population health management approaches

3. **Digital Transformation**
   - Implementation of interoperable systems
   - Data-driven decision making
   - Patient-facing digital tools

The analysis identified significant opportunities for LTHT and LCH collaboration in discharge planning and community integration services.""",
        "confidence_score": 87,
        "quality_rating": "EXCELLENT",
        "unique_sources": 6,
        "total_chunks": 18,
        "iterations": 2,
        "epistemic_breakdown": {
            "FACT": 12,
            "ASSUMPTION": 4,
            "INFERENCE": 2
        },
        "sources": [
            {"name": "LTHT Annual Report 2024-25", "date": "2024-10", "theme": "Workforce", "chunks": 5},
            {"name": "LCH Annual Report 2024-25", "date": "2024-10", "theme": "Service Integration", "chunks": 4},
            {"name": "NHS 10-year Plan", "date": "2023-01", "theme": "Strategy", "chunks": 3},
            {"name": "Workforce Strategy 2021-25", "date": "2021-01", "theme": "Workforce", "chunks": 3},
            {"name": "Healthy Leeds Strategy", "date": "2023-06", "theme": "Population Health", "chunks": 2},
            {"name": "Trust Board Minutes Jan 2025", "date": "2025-01", "theme": "Strategy", "chunks": 1}
        ],
        "gaps_identified": ["Limited information on specific service metrics"],
        "iterations_log": [
            {
                "iteration": 1,
                "chunks_retrieved": 12,
                "documents": 4,
                "quality": "ADEQUATE",
                "gaps": ["Missing LCH-specific data"],
                "decision": "Continue - expand search"
            },
            {
                "iteration": 2,
                "chunks_retrieved": 18,
                "documents": 6,
                "quality": "EXCELLENT",
                "gaps": [],
                "decision": "Stop - sufficient quality"
            }
        ]
    }


def display_results(result: dict) -> None:
    """Display analysis results."""
    if not result:
        st.warning("No results to display.")
        return

    st.markdown("---")
    st.subheader("📊 Analysis Results")

    # Top section: Confidence and metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        display_confidence_badge(result.get("confidence_score", 0))

    with col2:
        st.metric(
            "Quality Rating",
            result.get("quality_rating", "UNKNOWN"),
            delta="Analysis quality"
        )

    with col3:
        st.metric(
            "Documents Consulted",
            result.get("unique_sources", 0),
            delta="unique sources"
        )

    with col4:
        st.metric(
            "Evidence Chunks",
            result.get("total_chunks", 0),
            delta="text segments retrieved"
        )

    # Epistemic breakdown
    st.markdown("### 📈 Epistemic Breakdown")
    display_epistemic_chart(result.get("epistemic_breakdown", {}))

    # Answer section
    st.markdown("### 📝 Analysis")
    st.markdown(result.get("answer", "No answer generated"))

    # Sources section
    st.markdown("### 📚 Sources")
    display_source_metadata_table(result.get("sources", []))

    # Gaps section
    if result.get("gaps_identified"):
        st.markdown("### ⚠️ Identified Gaps")
        for gap in result.get("gaps_identified", []):
            st.info(f"• {gap}")

    # Iteration log
    st.markdown("### 📋 Iteration Log")
    iterations = result.get("iterations_log", [])
    for iteration in iterations:
        with st.expander(f"Iteration {iteration.get('iteration', '?')}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Chunks Retrieved", iteration.get("chunks_retrieved", 0))
            with col2:
                st.metric("Documents", iteration.get("documents", 0))
            with col3:
                st.metric("Quality", iteration.get("quality", "UNKNOWN"))

            if iteration.get("gaps"):
                st.write("**Gaps Identified:**")
                for gap in iteration["gaps"]:
                    st.write(f"• {gap}")

            st.write(f"**Decision:** {iteration.get('decision', 'Unknown')}")

    # Export section
    st.markdown("---")
    st.subheader("💾 Export Results")

    col1, col2 = st.columns(2)

    with col1:
        markdown_content = export_to_markdown(result)
        create_download_button(
            markdown_content,
            f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            "markdown"
        )

    with col2:
        json_content = json.dumps(result, indent=2, default=str)
        create_download_button(
            json_content,
            f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "json"
        )


def main():
    """Main app."""
    initialize_session_state()

    st.title("🤖 Multi-Agent Analysis")
    st.markdown("""
    Ask a strategic question about NHS organizations, workforce, services, or policy.
    The system will perform iterative analysis, detecting gaps and refining results
    until achieving high confidence.
    """)

    # Question input
    question = st.text_area(
        "What is your strategic question?",
        height=100,
        placeholder="Example: What are the key workforce challenges facing LTHT and LCH?",
        label_visibility="collapsed"
    )

    # Advanced settings
    with st.expander("⚙️ Advanced Settings", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            # Use config for web interface defaults
            if Config:
                default_iters = Config.WEB_DEFAULT_ITERATIONS
                max_iters = Config.WEB_MAX_ITERATIONS
                models = Config.AVAILABLE_MODELS
            else:
                default_iters = 5
                max_iters = 10
                models = ["gpt-4o", "gpt-4o-mini"]

            max_iterations = st.slider(
                "Maximum Iterations",
                min_value=1,
                max_value=max_iters,
                value=default_iters,
                help="How thoroughly should the analysis search? More iterations = more thorough but slower"
            )

            model = st.selectbox(
                "LLM Model",
                options=models,
                help="GPT-4o is more capable but more expensive. Mini is faster and cheaper."
            )

        with col2:
            # Use config for temperature defaults
            if Config:
                default_temp = Config.WEB_DEFAULT_TEMPERATURE
                default_k = Config.WEB_DEFAULT_K
                max_k = Config.WEB_MAX_K
            else:
                default_temp = 0.5
                default_k = 10
                max_k = 20

            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=default_temp,
                help="Lower = more consistent, Higher = more creative"
            )

            k = st.slider(
                "Retrieval K-value",
                min_value=5,
                max_value=max_k,
                value=default_k,
                help="Number of document chunks to retrieve per search"
            )

    # Analysis button and results
    col1, col2 = st.columns([4, 1])

    with col1:
        run_button = st.button(
            "🚀 Run Multi-Agent Analysis",
            use_container_width=True,
            type="primary",
            disabled=not question.strip()
        )

    with col2:
        if st.session_state.current_analysis_result:
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.current_analysis_result = None
                st.rerun()

    # Run analysis if button clicked
    if run_button:
        if not question.strip():
            st.error("Please enter a question.")
        else:
            with st.spinner("🔄 Starting analysis..."):
                # Run the analysis
                result = run_mock_analysis(question, max_iterations, model, temperature, k)

                # Store in session state
                st.session_state.current_analysis_result = result

                # Add to history
                if "query_history" not in st.session_state:
                    st.session_state.query_history = []

                st.session_state.query_history.append({
                    "question": question,
                    "mode": "Multi-Agent",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "confidence_score": result.get("confidence_score", 0)
                })

    # Display results if available
    if st.session_state.current_analysis_result:
        display_results(st.session_state.current_analysis_result)


if __name__ == "__main__":
    main()
