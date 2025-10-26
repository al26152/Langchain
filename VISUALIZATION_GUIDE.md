# Knowledge Graph Visualization Guide

**Created**: October 26, 2025
**Tools**: Custom visualization scripts + vis.js interactive networks

---

## Available Visualizations

You now have **3 interactive knowledge graph visualizations** to explore your Leeds healthcare system:

### 1. **Full Knowledge Graph**
`knowledge_graph_cleaned_visualization.html` (Original)
- **All** 19,374 relationships
- **All** entities across all types
- **Best for**: Comprehensive system overview

### 2. **Entity Network Visualization** 🆕
`entity_network.html`
- **Focused** on LTHT & LCH + 1-hop connections
- **195 entities**, 383 relationships
- **Best for**: Understanding specific organization networks

### 3. **Organization-Focused Network** 🆕 ⭐ **RECOMMENDED**
`org_network.html`
- **16 Organizations** + **25 Pathways**
- **902 connections** showing how orgs relate through pathways
- **Best for**: Strategic understanding of system partnerships

---

## How to Use the Visualizations

### Opening the Visualizations

Simply double-click any `.html` file, or:

```bash
# Windows
start org_network.html
start entity_network.html
start knowledge_graph_cleaned_visualization.html

# Mac/Linux
open org_network.html
xdg-open entity_network.html  # Linux
```

### Interactive Features

All visualizations support:

✅ **Click nodes** - Highlight connected entities
✅ **Drag nodes** - Rearrange the network
✅ **Zoom/Pan** - Mouse wheel to zoom, drag background to pan
✅ **Hover** - See full entity names and relationships
✅ **Physics toggle** - Freeze/unfreeze the layout
✅ **Reset view** - Fit all nodes in view

### Organization-Focused Network (Recommended)

**Special features:**
- 🔍 **Focus Leeds Orgs** button - Zooms to LTHT, LCH, LYPFT
- 🌐 **Show All** button - Reset to full view
- **Color coding**:
  - 🔴 **Red** = Organizations (NHS Trusts, Councils)
  - 🟢 **Green** = Pathways (D2A, Collaboratives, Care pathways)
  - 🔵 **Blue** = Services

**How to explore:**
1. Click **LTHT** or **LCH** node → See all their connections light up
2. Click **Focus Leeds Orgs** → Zoom to Leeds-specific organizations
3. Click any **Pathway** (green) → See which organizations share it

---

## Creating Custom Visualizations

### For Specific Entities

Use the `visualize_entity_network.py` script:

```bash
# Visualize a single organization
python visualize_entity_network.py LTHT

# Visualize multiple organizations
python visualize_entity_network.py LTHT LCH LYPFT

# Use full names
python visualize_entity_network.py "Leeds Teaching Hospitals NHS Trust"

# Focus on a service
python visualize_entity_network.py "Elective Care"

# Explore pathways
python visualize_entity_network.py "Discharge to Assessment (D2A) pathways"
```

**Output**: `entity_network.html` (overwrites each time)

### For Organization Networks

Use the `visualize_org_focused.py` script:

```bash
python visualize_org_focused.py
```

**Output**: `org_network.html` (clean strategic view)

---

## What Each Visualization Shows

### 1. Full Knowledge Graph
**Nodes**: 200+ entities
**Relationships**: 19,374

**Entity types:**
- 16 Organizations
- 115 Services
- 25 Pathways
- 9 Roles
- 35 Conditions

**Use case**: "I want to see EVERYTHING in the system"

---

### 2. Entity Network (LTHT + LCH)
**Nodes**: 195 entities (1-hop from LTHT & LCH)
**Relationships**: 383

**What you see:**
- LTHT & LCH (center)
- All services they provide
- All pathways they use
- All organizations they collaborate with
- All conditions they treat

**Entity breakdown:**
- 115 Services
- 33 Conditions
- 22 Pathways
- 12 Organizations
- 9 Roles
- 4 Unknown

**Top relationships:**
- `mentioned_together_in` (328) - Co-occurrence in documents
- `provides` (52) - Organization → Service
- `uses` (3) - Organization → Pathway

**Use case**: "What services and pathways connect LTHT and LCH?"

---

### 3. Organization-Focused Network
**Nodes**: 41 entities (16 orgs + 25 pathways)
**Relationships**: 902

**What you see:**
- All NHS Trusts, ICBs, Councils
- All care pathways and collaboratives
- How organizations connect through shared pathways

**Example connections you'll discover:**
```
LTHT ──provides──> Elective Operations
LCH ──provides──> Community Care
LCH ──uses──> Discharge to Assessment (D2A) pathways
LTHT ──mentioned_together_in──> West Yorkshire Collaborative
```

**Use case**: "How do Leeds organizations work together strategically?"

---

## Key Insights from the Visualizations

### Finding #1: Hub Organizations

**Leeds Community Healthcare NHS Trust (LCH)** is a major hub:
- Connected to **100+ services**
- Uses **multiple pathways** (D2A, Community Care, Primary Care)
- Collaborates with **Leeds City Council** (Homefirst initiative)
- Member of **West Yorkshire Community Health Services Provider Collaborative**

### Finding #2: Critical Pathways

**Discharge to Assessment (D2A) pathways** connect multiple organizations:
- Used by LCH
- Mentioned alongside LTHT acute services
- Critical for elective care flow (as we discovered in the analysis!)

### Finding #3: System-Wide Collaboratives

**West Yorkshire Community Health Services Provider Collaborative**:
- Includes 8 community providers
- LCH is a key member
- Enables resource sharing across trusts

**Mental Health, Learning Disabilities, and Autism Collaborative**:
- Cross-organization partnership
- Connects LYPFT with other trusts

### Finding #4: The "Mentioned Together" Network

The most common relationship is `mentioned_together_in` (328 instances):
- Shows which entities are discussed together in documents
- Reveals implicit connections not explicitly stated
- Example: LTHT + "Elective Operations" + "Discharge pathways" appear together frequently

---

## Practical Use Cases

### Use Case 1: Strategic Planning Meeting
**Scenario**: Board wants to understand LTHT-LCH partnership landscape

**Steps:**
1. Open `org_network.html`
2. Click **"Focus Leeds Orgs"** button
3. Click **LTHT** node → See all LTHT connections
4. Click **LCH** node → See all LCH connections
5. Identify shared pathways (green nodes connected to both)

**Insight**: Quickly see D2A pathways, collaboratives, shared services

---

### Use Case 2: Service Redesign
**Scenario**: Redesigning discharge processes, need to understand current pathways

**Steps:**
1. Run: `python visualize_entity_network.py "Discharge to Assessment (D2A) pathways"`
2. Open `entity_network.html`
3. See all organizations using D2A pathways
4. Identify all connected services

**Insight**: Comprehensive view of discharge ecosystem

---

### Use Case 3: Partnership Exploration
**Scenario**: Exploring collaboration opportunities with external organizations

**Steps:**
1. Open `org_network.html`
2. Click **Leeds City Council** node
3. See all pathways/services where they already collaborate
4. Identify potential new partnership areas

**Insight**: Evidence-based partnership strategy

---

### Use Case 4: Multi-Agent Query Validation
**Scenario**: Multi-agent system found a relationship - you want to verify it visually

**Steps:**
1. Note the entities from the analysis report
2. Run: `python visualize_entity_network.py "Entity 1" "Entity 2"`
3. Open `entity_network.html`
4. Visually confirm the relationship path

**Insight**: Visual validation of AI-discovered insights

---

## Color Coding Reference

### Organization-Focused Network

| Color | Entity Type | Size | Example |
|-------|-------------|------|---------|
| 🔴 **Red** | Organizations | Large (50px) | LTHT, LCH, LYPFT |
| 🟢 **Green** | Pathways | Medium (30px) | D2A, Primary Care Partnership |
| 🔵 **Blue** | Services | Small (20px) | Elective Care, Community Care |

**Leeds organizations are 50% larger and bold** for easy identification

### Entity Network

| Color | Entity Type | Example |
|-------|-------------|---------|
| 🔴 **Red** | Organizations | NHS Trusts, ICBs |
| 🔵 **Blue** | Services | Cancer care, Mental Health |
| 🟢 **Green** | Pathways | Clinical pathways, Collaboratives |
| 🟠 **Orange** | Roles | Medical Directors, Clinicians |
| 🟣 **Purple** | Conditions | COVID-19, Long-term conditions |

---

## Technical Details

### Visualization Technology
- **Library**: vis.js (network visualization)
- **Format**: Standalone HTML (no server needed)
- **Data source**: `knowledge_graph_improved.json`

### Performance
- **Large networks** (19K relationships): May take 10-30 seconds to stabilize
- **Medium networks** (400 relationships): 2-5 seconds
- **Small networks** (40 entities): Instant

**Tip**: Click "Toggle Physics" to freeze the layout once it's stabilized

### Customization

Want to change colors or layout? Edit the visualization scripts:
- `visualize_entity_network.py` (lines 110-140) - Node colors/sizes
- `visualize_org_focused.py` (lines 60-90) - Color scheme

Then re-run the script to regenerate.

---

## Comparison: Knowledge Graph vs Multi-Agent RAG

### Knowledge Graph Visualization
✅ **Strengths:**
- Visual understanding of system structure
- Discover implicit connections
- Strategic planning tool
- No API costs (static graph)

❌ **Limitations:**
- Shows relationships, not evidence quality
- Can't answer "why" questions
- May miss nuanced context

### Multi-Agent RAG (KG-Enhanced)
✅ **Strengths:**
- Uses KG to expand searches
- Provides evidence with confidence scores
- Answers complex questions
- Epistemic tagging (FACT/ASSUMPTION/INFERENCE)

❌ **Limitations:**
- Costs $0.15-0.40 per query
- Harder to see full system structure

### Best Practice: Use Both Together

1. **Start with visualization** → Understand system structure
2. **Form questions** → Based on what you see
3. **Run multi-agent query** → Get evidence-based answers
4. **Return to visualization** → Validate findings visually

**Example workflow:**
```
1. Open org_network.html
2. See LTHT connected to "Elective Operations"
3. Question: "What elective care challenges does LTHT face?"
4. Run: python analysis/multi_agent/run_multi_agent.py --question "..."
5. Review evidence (85% confidence, 8 sources)
6. Return to visualization to see pathway connections
```

---

## Next Steps

### Explore Your Visualizations

1. ⭐ **Start here**: Open `org_network.html`
   - Click "Focus Leeds Orgs"
   - Click LTHT → See connections
   - Click LCH → See connections
   - Identify shared pathways

2. 🔍 **Deep dive**: Create custom visualizations
   ```bash
   python visualize_entity_network.py "Discharge to Assessment (D2A) pathways"
   ```

3. 📊 **Validate findings**: Use visualizations to validate multi-agent discoveries

### Advanced Explorations

Try these custom visualizations:

```bash
# Mental health ecosystem
python visualize_entity_network.py LYPFT "Mental Health"

# Community care network
python visualize_entity_network.py LCH "Community Care"

# Elective care pathways
python visualize_entity_network.py "Elective Care" "Discharge Pathway"

# Full Leeds system
python visualize_entity_network.py LTHT LCH LYPFT "Leeds City Council"
```

---

## Files Reference

| File | Purpose | Size |
|------|---------|------|
| `knowledge_graph_improved.json` | Source data (19K relationships) | 2.5 MB |
| `knowledge_graph_cleaned_visualization.html` | Full graph (original) | Interactive |
| `entity_network.html` | Entity-focused (LTHT+LCH) | 195 nodes |
| `org_network.html` | Org-focused (strategic view) | 41 nodes |
| `visualize_entity_network.py` | Script: Custom entity networks | Tool |
| `visualize_org_focused.py` | Script: Organization network | Tool |

---

**Happy Exploring! 🎉**

Your knowledge graph is now fully integrated and visualized. Use these tools to:
- ✅ Understand system structure visually
- ✅ Validate multi-agent findings
- ✅ Support strategic planning
- ✅ Explore entity relationships interactively
