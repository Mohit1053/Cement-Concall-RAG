# 🏭 Cement Industry Concall Analysis with RAG

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-RAG-orange.svg)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Complete RAG-powered system for downloading, indexing, and analyzing cement industry conference call transcripts.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [RAG Pipeline](#-rag-pipeline) • [Companies](#-companies-covered)

</div>

---

## 🎯 Overview

This project provides an end-to-end solution for:
1. **Downloading** conference call transcripts from multiple sources
2. **Processing** and indexing transcripts using vector embeddings
3. **Analyzing** business insights using RAG (Retrieval Augmented Generation)
4. **Querying** through a user-friendly Streamlit interface

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📥 **Auto Downloader** | Downloads concall transcripts from Market |
| 🔍 **Vector Search** | ChromaDB-powered semantic search |
| 🤖 **RAG Analysis** | LangChain-based intelligent Q&A |
| 📊 **Business Insights** | Pre-built analysis tasks for growth, costs, market dynamics |
| 🖥️ **Streamlit UI** | Interactive web interface for queries |
| 📑 **Multi-Company** | Covers 13 major cement companies |

## 🏢 Companies Covered

<table>
<tr>
<td>

- ACC Limited
- Ambuja Cements
- Birla Corporation
- Dalmia Bharat Ltd
- Grasim Industries

</td>
<td>

- India Cements
- J K Cement
- JK Lakshmi Cement
- Nuvoco Vistas

</td>
<td>

- Shree Cement
- Star Cement
- The Ramco Cements
- UltraTech Cement

</td>
</tr>
</table>

## 📦 Installation

### Prerequisites
- Python 3.9+
- OpenAI API Key (for embeddings and LLM)

### Setup

```bash
# Clone the repository
git clone https://github.com/Mohit1053/Cement-Concall-RAG.git
cd Cement-Concall-RAG

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API Key
export OPENAI_API_KEY="your-api-key"  # Linux/Mac
set OPENAI_API_KEY=your-api-key  # Windows
```

## 📂 Project Structure

```
Cement_Concall_Project/
├── 📁 concall_downloader/           # Transcript download scripts
│   ├── download_concalls_final.py   # Main downloader
│   ├── extract_concall_urls_2years.py
│   ├── filter_concalls_2years.py
│   ├── retry_failed_downloads.py
│   └── config.py                    # Credentials (gitignored)
├── 📁 Cement_Concall_Transcripts/   # Downloaded transcripts (56 files)
│   ├── ACC Limited/
│   ├── Ambuja Cements/
│   ├── UltraTech Cement/
│   └── ... (13 companies)
├── 📁 rag_pipeline/                 # RAG system
│   ├── 📁 core/
│   │   ├── vector_store.py          # ChromaDB operations
│   │   ├── text_processor.py        # Text chunking
│   │   └── entity_extraction.py     # Named entity extraction
│   ├── 📁 tasks/                    # Business analysis tasks
│   │   ├── growth_analysis.py
│   │   ├── profitability_analysis.py
│   │   ├── cost_analysis.py
│   │   └── market_dynamics.py
│   ├── 📁 data/vector_db_all/       # Vector database (4,185 chunks)
│   ├── 📁 scripts/                  # Utility scripts
│   ├── 📁 ui/                       # Streamlit interface
│   └── 📁 tests/                    # Test scripts
├── 📜 rag_structure_setup.py        # RAG setup script
├── 📜 rag_requirements.txt          # RAG dependencies
└── 📊 Cement_Companies_Concalls_*.xlsx  # Master data file
```

## 🚀 Usage

### Step 1: Download Transcripts
```bash
cd concall_downloader
python download_concalls_final.py
```

### Step 2: Build Vector Index
```bash
cd rag_pipeline
python scripts/build_index.py
```

### Step 3: Launch Streamlit UI
```bash
cd rag_pipeline/ui
streamlit run app.py
```

### Step 4: Query via Code
```python
from rag_pipeline.core.vector_store import VectorStore

# Initialize
vs = VectorStore("data/vector_db_all")

# Query
results = vs.query("What is UltraTech's capacity expansion plan?", k=5)
for doc in results:
    print(doc.page_content)
```

## 🔧 RAG Pipeline

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF/Docx      │───▶│  Text Chunking   │───▶│   Embeddings    │
│  Transcripts    │    │  (1000 tokens)   │    │   (OpenAI)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    Response     │◀───│   LLM (GPT-4)    │◀───│   ChromaDB      │
│                 │    │   Generation     │    │   Retrieval     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Pre-built Analysis Tasks

| Task | Description |
|------|-------------|
| 📈 **Growth Analysis** | Revenue growth, volume trends, market share |
| 💰 **Profitability** | EBITDA margins, cost optimization, pricing power |
| 🏭 **Cost Analysis** | Fuel costs, logistics, power & fuel mix |
| 📊 **Market Dynamics** | Demand outlook, competitive landscape |

## 📊 Sample Queries

```
1. "What is Shree Cement's capacity utilization rate?"
2. "Compare EBITDA margins across all companies"
3. "What are the key concerns about fuel costs?"
4. "Which companies are expanding in South India?"
5. "What is the demand outlook for FY25?"
```

## 📈 Data Statistics

| Metric | Value |
|--------|-------|
| Companies | 13 |
| Transcripts | 56 |
| Vector Chunks | 4,185 |
| Time Period | 2 Years |

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Concall transcripts are property of respective companies.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built for Cement Industry Research 🏗️**

</div>
