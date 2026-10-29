# Cement Concall RAG

Search and guidance extraction over the earnings-call transcripts of 13 listed Indian cement companies.

## Problem

Management guidance on volume growth, capacity additions and capex is spread across many quarterly earnings-call transcripts per company, and most of it sits in the analyst Q&A rather than in the prepared remarks. Reading the calls company by company is slow, and plain PDF search loses the question that gives an answer its meaning.

## What it does

1. **Collect.** A Selenium downloader in `concall_downloader/` gathers transcript PDFs for each company from screener.in, filters them to a date window and retries failed downloads. It needs your own login in `concall_downloader/config.py`, which is not committed. The transcripts it collected are already in the repo.
2. **Index.** `rag_pipeline/build_all_concalls_index.py` extracts text with PyMuPDF, cleans it, splits it into overlapping chunks that keep each analyst question with its management answer, tags every chunk with company, quarter and fiscal year, and builds a TF-IDF index. It runs offline and needs no API key.
3. **Query.** `rag_pipeline/query_rag.py` detects the companies and topics in a question, ranks chunks with boosts for company match, guidance terms and figures, removes duplicates, and prints a short answer with sources followed by the supporting transcript passages.
4. **Report.** `generate_q1_report.py` and `generate_q2_report.py` run two fixed questions across every company: revenue-growth guidance and upcoming capex. Saved outputs are in `rag_pipeline/Q1_Revenue_Growth_Guidance_Report_FINAL.txt` and `rag_pipeline/Q2_Capex_Guidance_Report_FINAL.txt`, with a written summary in [rag_pipeline/FINAL_ANALYSIS_SUMMARY.md](rag_pipeline/FINAL_ANALYSIS_SUMMARY.md).

Companies covered: ACC, Ambuja Cements, Birla Corporation, Dalmia Bharat, Grasim Industries, India Cements, J K Cement, JK Lakshmi Cement, Nuvoco Vistas, Shree Cement, Star Cement, The Ramco Cements and UltraTech Cement.

## Run it

Tested with Python 3.12.

```bash
git clone https://github.com/Mohit1053/Cement-Concall-RAG.git
cd Cement-Concall-RAG
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install pymupdf scikit-learn numpy

cd rag_pipeline
python build_all_concalls_index.py   # about 170 transcripts -> about 12,000 chunks, under a minute
python query_rag.py "What capex guidance did UltraTech give?"
python query_rag.py                  # interactive mode
python generate_q2_report.py         # capex guidance for every company
```

The steps above need only the three packages shown. `requirements.txt` lists the wider stack tried during development (LangChain, ChromaDB, the OpenAI client, Streamlit). The downloader also needs Selenium and Chrome.

## Layout

| Path | Contents |
|---|---|
| `concall_downloader/` | Downloader scripts, download logs and the collected transcripts |
| `Cement_Concall_Transcripts/` | A smaller sample set of transcripts |
| `rag_pipeline/core/` | PDF extraction, cleaning, chunking, metadata, vector-store adapters |
| `rag_pipeline/build_all_concalls_index.py` | Builds the TF-IDF index from all transcripts |
| `rag_pipeline/query_rag.py` | Question answering from the command line |
| `rag_pipeline/generate_q1_report.py`, `generate_q2_report.py` | Cross-company guidance reports |
| `rag_pipeline/tasks/` | Query templates for further analysis themes (profitability, costs, capacity, ESG) |

## Tech

Python, PyMuPDF, scikit-learn (TF-IDF), NumPy, Selenium. Adapters for ChromaDB, FAISS and Qdrant and an OpenAI client are in `rag_pipeline/core/` but are not used by the scripts above.

## Note

The transcripts are public company disclosures and remain the property of the respective companies. This is a research project.

## License

MIT. See [LICENSE](LICENSE).
