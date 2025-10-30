# Hardcoded Values Audit

**Complete audit of hardcoded values in the NHS Strategic Analysis RAG Pipeline**

---

## 🔴 **Critical - High Impact**

### 1. **Database Path** (`chroma_db_test`)
**Found in:** 15+ files
- web_interface/app.py:53
- web_interface/pages/1_🤖_Multi_Agent_Analysis.py:53, 181
- web_interface/pages/2_⚡_Quick_Query.py:40, 100
- analysis/multi_agent/run_multi_agent.py:84
- analysis/rag/analyze_pipeline.py:67
- pipeline/ingest_pipeline.py:87
- And 8 more files...

**Impact:** Cannot rename database folder without changing 15+ files
**Recommendation:** Create `config.py` with `CHROMA_DB_PATH = "chroma_db_test"`

---

### 2. **Quality Thresholds** (critique_agent.py)
**Why you only see 2 iterations!**

```python
# Line 32-50
min_sources: int = 5           # Needs 5 sources minimum for ADEQUATE
min_coverage_percent: float = 15.0   # 15% coverage minimum
min_recent_percent: float = 30.0     # 30% recent docs
max_iterations: int = 5              # Max 5 iterations

# Line 146-189: Scoring system
source_count >= 10: +40 points  # ← With entity resolution, easily achieved!
source_count >= 7:  +30 points
source_count >= 5:  +20 points

coverage_percent >= 30: +30 points
coverage_percent >= 20: +20 points
coverage_percent >= 10: +10 points

theme_count >= 4: +20 points
theme_count >= 3: +15 points
theme_count >= 2: +10 points

recent_percent >= 50: +10 points
recent_percent >= 30: +5 points

# STOPPING THRESHOLDS - TOO LENIENT SINCE ENTITY RESOLUTION!
score >= 80: "EXCELLENT" → STOPS IMMEDIATELY
score >= 60: "GOOD" → ALSO STOPS
score >= 40: "ADEQUATE"
score < 40:  "WEAK"
```

**Impact:**
- Entity resolution improved retrieval → now hits EXCELLENT/GOOD on iteration 2
- System stops too early (intelligent but conservative)
- Can't easily adjust thresholds without code changes

**Example Calculation (with Entity Resolution):**
```
Iteration 2 typical scores:
  9 sources     → 30 points
  25% coverage  → 20 points
  3 themes      → 15 points
  40% recent    → 5 points
  TOTAL: 70 points = "GOOD" → STOPS
```

**Recommendations:**
- Make thresholds configurable
- Increase EXCELLENT threshold to 90+ points
- Add minimum iteration requirement (e.g., always do 3 iterations minimum)

---

### 3. **Synthesis Context Limit** (synthesis_agent.py:165)
```python
for i, e in enumerate(evidence[:20], 1):  # Max 20 evidence chunks
```

**Impact:** Can only use 20 chunks for synthesis even if you have 50
**Recommendation:** Make configurable, increase to 30-40 for richer context

---

## 🟡 **Medium Impact**

### 4. **Model Names**
Hardcoded in multiple agents:

```python
# evidence_agent.py:64
ChatOpenAI(model="gpt-4o-mini", temperature=0.3)  # For epistemic classification

# orchestrator.py:91
ChatOpenAI(model="gpt-4o", temperature=0.5)  # For orchestration

# synthesis_agent.py:54
ChatOpenAI(model="gpt-4o", temperature=0.5)  # For final synthesis

# utils/utils.py:49
ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)  # For metadata tagging

# web_interface dropdown
options=["gpt-4o", "gpt-4o-mini"]  # Only 2 choices
```

**Impact:** Can't easily switch to GPT-4.5, Claude, or other models
**Recommendation:** Environment variables or config file

---

### 5. **Knowledge Graph Path** (`knowledge_graph_improved.json`)
**Found in:** 8 files
- analysis/multi_agent/knowledge_graph_agent.py:39
- clean_duplicate_organizations.py:21, 171
- visualize_balanced.py:24
- And 4 more...

**Impact:** Must be in root directory, can't relocate
**Recommendation:** Make configurable path

---

### 6. **Retrieval K Values**
```python
# evidence_agent.py:139 - Always retrieves 20 chunks
k=20

# web_interface quick query default - 10 chunks
k=10

# web_interface slider range
min_value=5, max_value=20, value=10  # Can't go above 20
```

**Impact:** Can't tune retrieval depth easily
**Recommendation:** Make configurable, allow higher k (up to 50)

---

### 7. **Temperature Values**
Hardcoded across agents:

```python
temperature=0.3  # evidence_agent (epistemic classification)
temperature=0.5  # orchestrator, synthesis_agent (main synthesis)
temperature=0.2  # utils (metadata tagging)
```

**Impact:** Can't adjust creativity vs consistency without code changes
**Recommendation:** Environment variables or config

---

## 🟢 **Low Impact - Usually Reasonable**

### 8. **Entity Resolution Limits**
```python
# entity_resolver.py
max_aliases_per_entity=2  # Default when expanding queries
fuzzy_threshold=0.85      # Minimum similarity for typo correction
```

**Impact:** Minimal - these are good defaults
**Status:** OK as-is

---

### 9. **Web Interface Defaults**
```python
# Max iterations slider
min_value=1, max_value=10, value=5

# Temperature slider
min_value=0.0, max_value=1.0, value=0.5

# K-value slider
min_value=5, max_value=20, value=10
```

**Impact:** Reasonable ranges, but could expose more advanced options
**Status:** OK for now

---

### 10. **Document Count Fallback** (evidence_agent.py:77)
```python
def _count_total_documents(self) -> int:
    try:
        # ... count logic
    except:
        return 30  # Assumes 30 documents if count fails
```

**Impact:** Only used on error, usually correct
**Status:** OK as-is

---

### 11. **Date Thresholds**
```python
# evidence_agent.py:203-210
if years_old < 1:
    date_counts["recent"] += 1     # < 1 year = recent
elif years_old < 3:
    date_counts["moderate"] += 1   # 1-3 years = moderate
else:
    date_counts["old"] += 1        # 3+ years = old
```

**Impact:** Reasonable for NHS context
**Status:** OK as-is

---

### 12. **Epistemic Classification Indicators** (evidence_agent.py:330-380)
Hardcoded keyword lists for FACT/ASSUMPTION/INFERENCE:

```python
fact_indicators = [
    "according to", "reported", "stated", "data shows",
    "statistics", "figures show", "recorded", "measured"
]

assumption_indicators = [
    "projected", "estimated", "expected", "anticipated",
    "assuming", "likely", "predicted", "forecasted"
]

inference_indicators = [
    "therefore", "thus", "consequently", "implies",
    "suggests that", "indicates that"
]
```

**Impact:** Works well for NHS documents
**Status:** OK as-is, but could be enhanced with LLM

---

## 📊 **Impact Summary**

| Priority | What's Hardcoded | Files Affected | Recommendation |
|----------|------------------|----------------|----------------|
| 🔴 **CRITICAL** | Quality thresholds | critique_agent.py | **Fix NOW - causing 2-iteration stops** |
| 🔴 **CRITICAL** | Database path | 15+ files | Create config file |
| 🔴 **CRITICAL** | Synthesis context limit | synthesis_agent.py | Increase to 30-40 chunks |
| 🟡 Medium | Model names | 10+ files | Environment variables |
| 🟡 Medium | KG path | 8 files | Config file |
| 🟡 Medium | Retrieval k values | evidence_agent, web UI | Make configurable |
| 🟡 Medium | Temperature values | 10+ files | Config file |
| 🟢 Low | Entity resolution limits | entity_resolver.py | OK as-is |
| 🟢 Low | Web UI defaults | web_interface | OK as-is |
| 🟢 Low | Document count fallback | evidence_agent.py | OK as-is |

---

## 🔧 **Recommended Fixes**

### **Fix #1: Quality Thresholds** (HIGHEST PRIORITY)

**Why:** System now stops at iteration 2 due to entity resolution improving scores

**Option A - Quick Fix:** Increase thresholds in critique_agent.py:
```python
# Line 182-189
if score >= 90:      # Increased from 80
    rating = "EXCELLENT"
elif score >= 75:    # Increased from 60
    rating = "GOOD"
elif score >= 50:    # Increased from 40
    rating = "ADEQUATE"
else:
    rating = "WEAK"
```

**Option B - Better Fix:** Make thresholds configurable:
```python
class CritiqueAgent:
    def __init__(
        self,
        min_sources: int = 5,
        min_coverage_percent: float = 15.0,
        min_recent_percent: float = 30.0,
        max_iterations: int = 5,
        excellent_threshold: int = 90,  # NEW
        good_threshold: int = 75,       # NEW
        adequate_threshold: int = 50,   # NEW
    ):
```

---

### **Fix #2: Create Config File**

Create `config/settings.py`:
```python
# Database
CHROMA_DB_PATH = "chroma_db_test"
KNOWLEDGE_GRAPH_PATH = "knowledge_graph_improved.json"

# Models
DEFAULT_LLM_MODEL = "gpt-4o"
EPISTEMIC_LLM_MODEL = "gpt-4o-mini"
TAGGING_LLM_MODEL = "gpt-3.5-turbo"

# Temperatures
DEFAULT_TEMPERATURE = 0.5
EPISTEMIC_TEMPERATURE = 0.3
TAGGING_TEMPERATURE = 0.2

# Retrieval
DEFAULT_K = 20
MAX_K = 50
MAX_SYNTHESIS_CHUNKS = 30

# Quality Thresholds
EXCELLENT_THRESHOLD = 90
GOOD_THRESHOLD = 75
ADEQUATE_THRESHOLD = 50
MIN_SOURCES = 5
MIN_COVERAGE_PERCENT = 15.0
```

Then import:
```python
from config.settings import CHROMA_DB_PATH, DEFAULT_LLM_MODEL
```

---

### **Fix #3: Increase Synthesis Context**

**File:** synthesis_agent.py:165
```python
# Change from:
for i, e in enumerate(evidence[:20], 1):

# To:
for i, e in enumerate(evidence[:30], 1):  # Use more evidence
```

---

## 🎯 **Quick Wins**

If you only have time for 3 fixes:

1. **Adjust quality thresholds** (90/75/50 instead of 80/60/40)
2. **Increase synthesis context** (30 chunks instead of 20)
3. **Create config.py** for database/KG paths

This will:
- ✅ Fix the 2-iteration problem
- ✅ Improve answer quality (more evidence)
- ✅ Make system more maintainable

---

**Next Steps:**
Would you like me to implement these fixes? I can:
1. Adjust quality thresholds to get 3-4 iterations
2. Increase synthesis context limit
3. Create a config file for common paths
