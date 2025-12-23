# Cement Industry RAG Pipeline - Task-Based Structure

## 📊 Business Analysis Tasks

### 1. Growth Analysis
**Location:** `tasks/growth_analysis/`

**Questions Answered:**
- What revenue growth guidance has each company provided?
- What are the capacity expansion plans?
- What is the implied revenue CAGR from capacity additions?

**Run Analysis:**
```bash
python tasks/growth_analysis/query_revenue_guidance.py
```

**Key Files:**
- `query_revenue_guidance.py` - Interactive query script
- `REVENUE_GROWTH_GUIDANCE_ANALYSIS.md` - Detailed report

---

### 2. Profitability Analysis
**Location:** `tasks/profitability_analysis/`

**Questions Answered:**
- What are EBITDA margin trends and guidance?
- What cost reduction initiatives are underway?
- How is operational efficiency improving?

**Template:** `query_template.py`

---

### 3. Capacity Utilization
**Location:** `tasks/capacity_utilization/`

**Questions Answered:**
- What are plant utilization rates by region?
- Which plants have headroom for volume growth?
- What is the commissioning timeline for new capacity?

**Template:** `query_template.py`

---

### 4. Cost Analysis
**Location:** `tasks/cost_analysis/`

**Questions Answered:**
- What are fuel cost trends (per kilocalorie)?
- How are raw material costs evolving?
- What power and energy cost initiatives exist?

**Template:** `query_template.py`

---

### 5. Market Dynamics
**Location:** `tasks/market_dynamics/`

**Questions Answered:**
- What is the demand outlook by region?
- How intense is competitive pricing?
- What infrastructure spending catalysts exist?

**Template:** `query_template.py`

---

### 6. Financial Health
**Location:** `tasks/financial_health/`

**Questions Answered:**
- What are cash flow and FCF trends?
- What are debt levels and leverage ratios?
- How is working capital managed?

**Template:** `query_template.py`

---

### 7. ESG & Sustainability
**Location:** `tasks/esg_sustainability/`

**Questions Answered:**
- What renewable energy plans exist?
- What are green cement initiatives?
- What carbon reduction targets are set?

**Template:** `query_template.py`

---

## 🔧 Core RAG Components

### Data Ingestion
**Location:** `core/data_ingestion/`

- `pdf_extractor.py` - Extract text from PDF transcripts
- Test: `tests/test_pdf_extraction.py`

### Data Processing
**Location:** `core/data_processing/`

- `text_cleaner.py` - Clean and preprocess text
- `chunker.py` - Chunk documents with Q&A awareness
- `entity_extractor.py` - Extract entities and metrics
- `metadata_enhancer.py` - Enrich with metadata

### Vector Store
**Location:** `core/vector_store/`

- `tfidf_store.py` - TF-IDF based vector database (active)
- `faiss_store.py` - FAISS alternative (offline)
- `chroma_client.py` - ChromaDB client (alternative)

Test: `tests/test_search.py`

---

## 📁 Data Organization

```
data/
├── raw/              # Raw PDF concall transcripts (link to ../Cement_Concall_Transcripts)
├── processed/        # Processed chunks and metadata
└── vector_db/        # TF-IDF vector database (4,185 chunks indexed)
```

---

## 🚀 Quick Start

### 1. Build Vector Index (if not already built)
```bash
python utils/build_vector_index.py --reset
```

### 2. Run a Task Analysis
```bash
# Growth analysis (ready to use)
python tasks/growth_analysis/query_revenue_guidance.py

# Other tasks (use templates)
python tasks/profitability_analysis/query_template.py
```

### 3. Create Custom Queries
Copy a template and modify the queries list:
```python
queries = [
    "Your custom question here",
    "Another question"
]
```

---

## 📊 Current Index Stats

- **Total Chunks:** 4,185
- **Companies:** 13 cement companies
- **Time Period:** 2 years (8 quarters)
- **Vocabulary:** 1,189 terms
- **Search Method:** TF-IDF with cosine similarity

---

## 🛠️ Utilities

**Location:** `utils/`

- `build_vector_index.py` - Build/rebuild vector database
- `download_model.py` - Download embedding models (if needed)

---

## 📚 Documentation

**Location:** `docs/`

- `RAG_PIPELINE_DESIGN.md` - Complete system architecture
- `IMPLEMENTATION_PROGRESS.md` - Development progress
- `PDF_EXTRACTION_TEST_RESULTS.md` - Extraction test results

---

## 🧪 Testing

**Location:** `tests/`

- `test_pdf_extraction.py` - Test PDF extraction (✅ 100% pass)
- `test_preprocessing_pipeline.py` - Test full pipeline (✅ 100% pass)
- `test_search.py` - Test vector search

---

## ⚙️ Configuration

**Location:** `configs/`

- `cement_rag_config.yaml` - Pipeline configuration

---

## 📈 Adding New Tasks

1. Create directory: `tasks/your_task_name/`
2. Copy template: `cp tasks/profitability_analysis/query_template.py tasks/your_task_name/`
3. Modify queries in the template
4. Run: `python tasks/your_task_name/query_template.py`

---

## 🎯 Task Priority Map

| Priority | Task | Status |
|----------|------|--------|
| ⭐⭐⭐⭐⭐ | Growth Analysis | ✅ Complete |
| ⭐⭐⭐⭐ | Profitability Analysis | 🔨 Template Ready |
| ⭐⭐⭐⭐ | Cost Analysis | 🔨 Template Ready |
| ⭐⭐⭐ | Capacity Utilization | 🔨 Template Ready |
| ⭐⭐⭐ | Market Dynamics | 🔨 Template Ready |
| ⭐⭐ | Financial Health | 🔨 Template Ready |
| ⭐⭐ | ESG & Sustainability | 🔨 Template Ready |

---

## 💡 Tips

1. **Refine queries** - More specific queries yield better results
2. **Use filters** - Filter by company, quarter, or fiscal year
3. **Combine tasks** - Cross-reference insights across tasks
4. **Iterate** - Adjust search terms based on initial results

---

## 🔄 Migration Notes

- Old structure preserved in `src/` and `scripts/` directories
- All functionality maintained, just reorganized
- Path updates in imports handled automatically
- Vector database unchanged (no reindexing needed)

---

**Last Updated:** December 2, 2025
