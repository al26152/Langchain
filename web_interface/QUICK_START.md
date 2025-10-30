# Quick Start Guide - NHS Strategic Analysis Web Interface

## 🚀 Get Started in 2 Minutes

### Step 1: Install Dependencies (1-2 min)
```bash
cd web_interface
pip install -r requirements_web.txt
```

### Step 2: Verify ChromaDB is Ready
```bash
# Go to parent directory and run:
python run_full_pipeline.py
# (Only needed if you haven't done this yet)
```

### Step 3: Start the Web Interface
```bash
# From web_interface directory:
streamlit run app.py
```

**That's it!** 🎉 Your browser should open to http://localhost:8501

---

## 🎯 What You Can Do

### 🤖 Multi-Agent Analysis (Deep Dive)
1. Click "Multi-Agent Analysis"
2. Ask a strategic question:
   - "What are LTHT's workforce challenges?"
   - "How do LTHT and LCH collaborate?"
   - "What does the NHS 10-year plan say about workforce?"
3. (Optional) Adjust settings: iterations, model, temperature
4. Click "Run Multi-Agent Analysis"
5. Watch the analysis progress in real-time
6. Review results with confidence scores
7. Download as Markdown or JSON

**Perfect for:** Strategic decisions, comprehensive analysis, complex questions

### ⚡ Quick RAG Query (Fast Lookup)
1. Click "Quick Query"
2. Ask a simple question:
   - "When was the NHS 10-year plan published?"
   - "What are LCH's main services?"
   - "What is LTHT's mission?"
3. Hit "Ask Question"
4. Get instant answer with source citations
5. Download result if needed

**Perfect for:** Quick facts, status checks, specific lookups

---

## 📁 File Structure

```
web_interface/
├── app.py                          ← Home page (landing page)
├── pages/
│   ├── 1_🤖_Multi_Agent_Analysis.py   ← Deep analysis
│   └── 2_⚡_Quick_Query.py             ← Quick queries
├── components/
│   ├── results_display.py          ← Result formatting
│   └── progress_tracker.py         ← Progress UI
├── requirements_web.txt            ← Dependencies
├── run_web_interface.bat           ← Windows quick start
├── README_WEB.md                   ← Full documentation
└── QUICK_START.md                  ← This file
```

---

## ⚙️ Configuration

### .env File (in root directory)
```
OPENAI_API_KEY=sk-your-key-here
```

### Advanced Settings (in web UI)

**Multi-Agent Analysis:**
- Max Iterations: How thorough (1-10, default 5)
- Model: GPT-4o (powerful) or GPT-4o-mini (fast)
- Temperature: Consistency vs creativity (0-1, default 0.5)
- K-value: Sources to retrieve (5-20, default 10)

**Quick Query:**
- Number of sources: 5-20 (default 10)
- Model: GPT-4o or GPT-4o-mini

---

## 💡 Tips & Tricks

### ✅ Best Practices
- **Use Multi-Agent** for strategic questions requiring deep analysis
- **Use Quick Query** for simple factual questions
- **Use gpt-4o-mini** for quick/cheap queries
- **Use gpt-4o** for complex analysis
- **Reduce k-value** to 5-10 for faster results
- **Increase max_iterations** (7-10) for complex questions

### ❌ Common Mistakes
- ❌ Running from wrong directory → cd web_interface first
- ❌ Missing .env file → Create it with OPENAI_API_KEY
- ❌ ChromaDB not populated → Run run_full_pipeline.py first
- ❌ Using Multi-Agent for simple questions → Use Quick Query instead

### 📊 Performance Estimates
| Mode | Time | Cost | Best For |
|------|------|------|----------|
| Multi-Agent (5 iter) | 2-3 min | $0.15-0.30 | Strategic questions |
| Multi-Agent (10 iter) | 3-4 min | $0.30-0.50 | Very complex analysis |
| Quick Query | 30-60 sec | $0.02-0.10 | Simple questions |

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements_web.txt
```

### Issue: "Failed to load ChromaDB"
```bash
# Go to parent directory and run:
python run_full_pipeline.py
```

### Issue: "OPENAI_API_KEY not found"
```bash
# Create .env in root directory with:
OPENAI_API_KEY=sk-your-actual-key
```

### Issue: App won't start on localhost:8501
```bash
# Port might be in use. Try:
streamlit run app.py --server.port=8502
```

### Issue: Slow responses
- Reduce k-value to 5-10
- Use gpt-4o-mini instead of gpt-4o
- Reduce max_iterations to 3-5

---

## 🔗 Key Features

### 🔄 Real-Time Progress Tracking
Watch the system work through iterations:
1. Evidence Agent finds relevant information
2. Critique Agent evaluates quality
3. Shows detected gaps
4. Decides whether to search again
5. Shows final confidence score

### 📊 Confidence Scores
- 🟢 **85-100%**: EXCELLENT
- 🟡 **70-84%**: GOOD
- 🟠 **50-69%**: ADEQUATE
- 🔴 **<50%**: WEAK

### 🏷️ Epistemic Breakdown
Every answer categorized as:
- **FACT**: Information directly from documents
- **ASSUMPTION**: Reasonable interpretation
- **INFERENCE**: Logical deduction

### 💾 Export Options
- **Markdown**: For reports, emails, documents
- **JSON**: For data analysis, integration

### 📚 Query History
- Automatic tracking of all queries
- Access from sidebar
- Shows timestamp and result type
- Click to review past analyses

---

## 🚀 Advanced Usage

### Custom Query Parameters
```
In Multi-Agent Analysis page:
- Increase max_iterations to 7-10 for very complex questions
- Lower temperature (0.1-0.3) for consistent, factual responses
- Increase k-value (15-20) for comprehensive analysis
- Use gpt-4o for important strategic decisions
```

### Batch Analysis (Future)
Currently: Query one at a time
Future: Support for batch query processing

### Document Updates
1. Add new document to `docs/` directory
2. Run: `python run_full_pipeline.py`
3. Refresh web interface (F5)

---

## 📖 Examples

### Example 1: Strategic Question (Multi-Agent)
**Question:** "What are the key workforce challenges identified across all NHS documents, and how do they compare between acute and community sectors?"

**Settings:**
- Max iterations: 7
- Model: gpt-4o
- Temperature: 0.4

**Expected:**
- Duration: 3-4 minutes
- Confidence: 85-95%
- Sources: 6-8 documents
- Quality: GOOD to EXCELLENT

### Example 2: Quick Lookup (Quick Query)
**Question:** "When was the NHS 10-year plan released?"

**Settings:**
- Default (k=10, gpt-4o-mini)

**Expected:**
- Duration: 30-45 seconds
- Cost: ~$0.05
- Sources: 2-3 documents

---

## 📞 Need Help?

1. **Check the README_WEB.md** for detailed documentation
2. **Review this QUICK_START.md** for common patterns
3. **Check the Troubleshooting section** above
4. **Verify your .env file** has OPENAI_API_KEY

---

## 🎓 Understanding the System

### What's Different Between Analysis Modes?

**Multi-Agent:**
- Multiple passes through documents
- Detects gaps and refines search
- Provides confidence scores
- Epistemic breakdown (FACT/ASSUMPTION/INFERENCE)
- Slower but more thorough

**Quick RAG:**
- Single pass through documents
- Direct semantic search
- Instant results
- Good for simple questions
- Faster and cheaper

### Document Collection
- 30+ NHS strategic documents
- 16,000+ indexed text chunks
- Metadata: date, theme, audience, source
- Includes: strategy plans, annual reports, board minutes, workforce data

---

## 🎯 Success Criteria

**Good Multi-Agent Response:**
- ✅ Confidence > 80%
- ✅ Quality: GOOD or EXCELLENT
- ✅ Multiple sources (4+)
- ✅ Clear answer with evidence
- ✅ Identified gaps are reasonable

**Good Quick Query Response:**
- ✅ Answer is clear and factual
- ✅ Sources are relevant
- ✅ Results in < 1 minute
- ✅ Low cost (< $0.10)

---

**Last Updated:** October 29, 2025
**Version:** 1.0
