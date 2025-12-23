# Task-Based RAG Pipeline - Quick Start Guide

## 🎯 What Changed?

Your cement RAG pipeline has been **restructured from technical components to business tasks**.

### Before (Technical Structure):
```
src/
  ingestion/
  processing/
  vectorstore/
scripts/
  test_*.py
  build_*.py
```

### After (Task-Based Structure):
```
tasks/                          # 7 business question categories
  growth_analysis/              ✅ READY - Revenue growth guidance
  profitability_analysis/       📋 Template ready
  capacity_utilization/         📋 Template ready
  cost_analysis/                📋 Template ready
  market_dynamics/              📋 Template ready
  financial_health/             📋 Template ready
  esg_sustainability/           📋 Template ready

core/                           # Technical components (preserved)
  data_ingestion/
  data_processing/
  vector_store/

data/                           # Data storage
  vector_db/                    # 4,185 chunks indexed
```

---

## 🚀 Quick Start - Run Your First Task

### Task 1: Growth Analysis (Already Complete)
```bash
python tasks/growth_analysis/run_analysis.py
```

**Output:** Revenue growth guidance for all 13 cement companies with:
- Formal capacity targets (Ambuja: 140 MT by FY28)
- Capex commitments (JK Cement: Rs 1,800-2,000 cr)
- Industry growth outlook (6% FY25)

---

## 📋 Create New Tasks - 3 Easy Steps

### Example: Create "Profitability Analysis"

**Step 1:** Navigate to task
```bash
cd tasks/profitability_analysis
```

**Step 2:** Edit the template
```python
# query_template.py already has:
queries = [
    "EBITDA margins guidance and trends",
    "Cost reduction initiatives and savings",
    "Operational efficiency improvements"
]
```

**Step 3:** Run it
```bash
python query_template.py
```

---

## 📊 All 7 Business Tasks

| # | Task | Status | Questions Answered |
|---|------|--------|-------------------|
| 1 | **Growth Analysis** | ✅ Complete | Revenue guidance, capacity expansion, CAGR |
| 2 | **Profitability** | 📋 Template | EBITDA margins, cost savings, efficiency |
| 3 | **Capacity Utilization** | 📋 Template | Plant utilization, regional performance |
| 4 | **Cost Analysis** | 📋 Template | Fuel costs, raw materials, energy |
| 5 | **Market Dynamics** | 📋 Template | Demand trends, pricing, competition |
| 6 | **Financial Health** | 📋 Template | Cash flow, debt, working capital |
| 7 | **ESG & Sustainability** | 📋 Template | Renewable energy, green cement, carbon |

---

## 🎓 How to Use Templates

Every task folder has a `query_template.py` that you can customize:

```python
# 1. Define your questions
queries = [
    "What was EBITDA per ton guidance?",
    "Cost reduction target for FY26?",
    # Add more questions...
]

# 2. Run the script
# It automatically:
#   - Loads the vector database
#   - Searches across all 4,185 chunks
#   - Groups results by company
#   - Shows relevant excerpts
```

---

## 📁 Directory Navigation

```
cement_rag_pipeline/
│
├── tasks/                      👈 START HERE for business questions
│   ├── growth_analysis/        ← Already completed with full report
│   ├── profitability_analysis/ ← Ready to customize
│   ├── capacity_utilization/   ← Ready to customize
│   ├── cost_analysis/          ← Ready to customize
│   ├── market_dynamics/        ← Ready to customize
│   ├── financial_health/       ← Ready to customize
│   └── esg_sustainability/     ← Ready to customize
│
├── core/                       🔧 Technical RAG components (don't touch)
│   ├── data_ingestion/
│   ├── data_processing/
│   └── vector_store/
│
├── data/                       💾 Data storage
│   └── vector_db/              ← 4,185 indexed chunks
│
├── tests/                      🧪 Test scripts
├── utils/                      🛠️ Utility scripts
├── docs/                       📚 Documentation
└── README_TASK_BASED.md        📖 Full documentation
```

---

## 💡 Example Workflow

### Scenario: Analyst wants to compare cost structures

```bash
# 1. Run cost analysis
cd tasks/cost_analysis
python query_template.py

# 2. Results show:
#    - Fuel cost: Rs 1.82/kcal (Shree Cement)
#    - Power cost reduction: 60% renewable by FY26 (Ambuja)
#    - Logistics optimization initiatives

# 3. Cross-reference with profitability
cd ../profitability_analysis
python query_template.py

# 4. Get insights on how cost savings impact EBITDA margins
```

---

## 🔄 What Wasn't Changed

✅ Vector database (4,185 chunks) - still works perfectly
✅ All core components - just moved to `core/` directory  
✅ Original `src/` and `scripts/` - preserved for reference
✅ Test scripts - moved to `tests/` directory

---

## 🎯 Key Benefits

### Before:
- "Where do I find growth analysis code?"
- "How do I query for profitability?"
- Technical file structure

### After:
- "I want growth analysis" → `tasks/growth_analysis/`
- "I need cost breakdown" → `tasks/cost_analysis/`
- **Business-first organization**

---

## 📖 Full Documentation

See `README_TASK_BASED.md` for complete details including:
- Detailed task descriptions
- API reference
- Customization guide
- Advanced queries

---

## 🚨 Troubleshooting

### Issue: "Failed to load vector store"
**Solution:** Vector DB path is relative. Run from project root:
```bash
cd C:\Users\mohit1\Desktop\Data_Scraping\cement_rag_pipeline
python tasks/growth_analysis/run_analysis.py
```

### Issue: "ModuleNotFoundError"
**Solution:** The script adds paths automatically, but if you see this:
```python
# Add to top of your script:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
```

### Issue: Unicode encoding errors
**Solution:** Use `run_analysis.py` instead of `query_*.py` for Windows console

---

## ✅ Next Steps

1. ✅ Growth analysis already done - see report in `tasks/growth_analysis/`
2. 📝 Pick next task (e.g., profitability, costs)
3. 🔧 Customize template queries
4. ▶️ Run and get insights
5. 📊 Compare across tasks for comprehensive analysis

---

**Created:** December 2, 2025  
**Structure:** Task-based business questions  
**Data:** 55 quarterly concalls, 13 companies, 2 years  
**Ready to use:** ✅ All templates functional
