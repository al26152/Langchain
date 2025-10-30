# NHS Strategic Analysis System - Web Interface

A Streamlit web interface for the NHS Strategic Analysis RAG Pipeline. Provides intuitive access to multi-agent analysis and quick RAG queries across 30+ NHS strategic documents.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (set in `.env` file in root directory)
- ChromaDB already populated (run `python run_full_pipeline.py` first)

### Installation

1. **Install dependencies:**
   ```bash
   cd web_interface
   pip install -r requirements_web.txt
   ```

2. **Verify .env file exists** in the parent directory with your OpenAI API key:
   ```bash
   # In root directory (C:\Users\al261\OneDrive\Documents\Langchain\)
   cat .env
   # Should show: OPENAI_API_KEY=sk-...
   ```

3. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

   The app will open at: **http://localhost:8501**

---

## 📋 Features

### 🏠 Home Page (`app.py`)
- System overview and statistics
- Documents indexed count
- Last updated timestamp
- Navigation to analysis modes
- Query history sidebar

### 🤖 Multi-Agent Analysis (`pages/1_🤖_Multi_Agent_Analysis.py`)
**Recommended for strategic decisions**

**Features:**
- Iterative retrieval with gap detection
- Real-time progress tracking
- Confidence scoring (0-100%)
- Epistemic breakdown (FACT/ASSUMPTION/INFERENCE)
- Detailed iteration logs
- Export to Markdown and JSON

**Advanced Controls:**
- Max Iterations (1-10, default 5)
- Model selection (GPT-4o, GPT-4o-mini)
- Temperature (0-1, default 0.5)
- Retrieval k-value (5-20, default 10)

**Performance:**
- Duration: 2-4 minutes
- Cost: ~$0.15-0.40 per query

### ⚡ Quick RAG Query (`pages/2_⚡_Quick_Query.py`)
**For fast, focused answers**

**Features:**
- Single-pass retrieval
- Multi-source synthesis
- Source citations with metadata
- Instant results
- Export options

**Customization:**
- Number of sources (5-20)
- Model selection (GPT-4o, GPT-4o-mini)

**Performance:**
- Duration: 30-60 seconds
- Cost: ~$0.02-0.10 per query

---

## 🔧 How It Works

### Architecture

```
app.py (Home)
├── pages/1_🤖_Multi_Agent_Analysis.py
│   ├── components/results_display.py
│   ├── components/progress_tracker.py
│   └── Connects to: analysis/multi_agent/orchestrator.py
└── pages/2_⚡_Quick_Query.py
    └── components/results_display.py
        └── Uses: LangChain RetrievalQA
```

### Data Flow

**Multi-Agent Analysis:**
```
User Question
    ↓
Orchestrator.run_analysis()
    ↓
Evidence Agent → Retrieves chunks from ChromaDB
    ↓
Critique Agent → Evaluates quality & detects gaps
    ↓
Knowledge Graph Agent → Expands retrieval (silent)
    ↓
Loop until sufficient quality OR max iterations
    ↓
Synthesis Agent → Generates final report
    ↓
Display results with confidence scores
```

**Quick RAG Query:**
```
User Question
    ↓
ChromaDB semantic search (k chunks)
    ↓
LLM synthesis with multi-source requirement
    ↓
Return answer + source citations
```

---

## 🎯 Usage Examples

### Multi-Agent Analysis
**Question:** "What are the key workforce challenges facing LTHT and LCH?"

**Expected Output:**
- Confidence: 85-95%
- Quality: GOOD to EXCELLENT
- Duration: 2-3 minutes
- Sources: 5-7 documents
- Shows iteration log with gap detection

### Quick RAG Query
**Question:** "When was the NHS 10-year plan published?"

**Expected Output:**
- Instant answer
- Duration: 30-60 seconds
- Sources: 2-3 documents
- Quick metadata table

---

## ⚙️ Configuration

### Session State (Automatically Managed)
```python
st.session_state:
  - vectordb: Chroma database connection (cached)
  - query_history: List of past queries
  - current_analysis_result: Latest analysis
  - current_query_result: Latest quick query
```

### Environment Variables
Required in root `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

### Model Selection
- **gpt-4o** (default): More capable, ~$0.02/1K input, $0.06/1K output
- **gpt-4o-mini**: Faster, cheaper, ~$0.15/1M input, $0.60/1M output

---

## 🐛 Troubleshooting

### Issue: "Failed to load ChromaDB"
**Solution:** Run ingestion pipeline first:
```bash
python run_full_pipeline.py
```

### Issue: "OPENAI_API_KEY not found"
**Solution:** Create `.env` in root directory:
```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

### Issue: "Module not found" for analysis modules
**Solution:** Make sure you're running from the correct directory:
```bash
cd "C:\Users\al261\OneDrive\Documents\Langchain"
cd web_interface
streamlit run app.py
```

### Issue: Streamlit not found
**Solution:** Install from web_interface directory:
```bash
pip install -r requirements_web.txt
```

---

## 📊 Performance Notes

### Query Performance
| Mode | Duration | Cost | Use Case |
|------|----------|------|----------|
| Multi-Agent | 2-4 min | $0.15-0.40 | Strategic decisions, complex analysis |
| Quick Query | 30-60 sec | $0.02-0.10 | Lookups, quick facts, status checks |

### Caching
- ChromaDB connection: Cached (shared across users)
- Query results: Session-based (per browser session)
- Document metadata: Cached with 1-hour TTL

### Optimization Tips
1. Use Quick Query for simple questions
2. Use Multi-Agent only for complex strategic questions
3. Reduce k-value to 5-10 for faster queries
4. Use gpt-4o-mini for simple questions

---

## 🔒 Security Considerations (Localhost)

Since this runs on localhost:
- ✅ No authentication needed for development
- ✅ .env file is not exposed to web
- ✅ All queries stay local (ChromaDB)
- ⚠️ For production: Add authentication, enable HTTPS, restrict access

---

## 📚 File Structure

```
web_interface/
├── app.py                              # Home page
├── pages/
│   ├── 1_🤖_Multi_Agent_Analysis.py   # Multi-agent analysis
│   └── 2_⚡_Quick_Query.py             # Quick RAG queries
├── components/
│   ├── __init__.py
│   ├── results_display.py             # Result formatting components
│   └── progress_tracker.py            # Iteration tracking UI
├── requirements_web.txt               # Dependencies
└── README_WEB.md                      # This file
```

---

## 🔄 Integration with Pipeline

The web interface assumes the main pipeline is already running:

```bash
# Terminal 1: Run once to populate ChromaDB
python run_full_pipeline.py

# Terminal 2: Start web interface
cd web_interface
streamlit run app.py
```

To add new documents:
```bash
# 1. Add document to docs/ directory
# 2. Run pipeline again
python run_full_pipeline.py
# 3. Refresh web interface (Ctrl+R)
```

---

## 🚀 Next Steps (Future Enhancements)

- [ ] Document upload interface in web UI
- [ ] Knowledge graph visualization
- [ ] Batch query processing
- [ ] User authentication
- [ ] Custom prompt templates
- [ ] Query analytics dashboard
- [ ] Scheduled document updates
- [ ] Multi-language support

---

## 📞 Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Verify ChromaDB is populated: `chroma_db_test/` directory should exist
3. Check API key is set: `cat .env` should show OPENAI_API_KEY
4. Review Streamlit logs in terminal

---

## 📝 License

This web interface is part of the NHS Strategic Analysis System.

---

**Last Updated:** October 29, 2025
**Version:** 1.0.0
