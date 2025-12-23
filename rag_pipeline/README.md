# Cement Industry RAG Pipeline

A Retrieval-Augmented Generation (RAG) system for querying cement company conference call transcripts.

## Features

- PDF text extraction from conference call transcripts
- Semantic document chunking
- Vector embeddings with sentence-transformers
- Qdrant vector database for efficient retrieval
- LLM-powered response generation
- FastAPI backend and Streamlit frontend

## Setup

1. Install dependencies:
```bash
pip install -r ../rag_requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Start Qdrant (using Docker):
```bash
docker-compose up -d
```

4. Copy your data:
```bash
# Copy PDFs to data/raw/
```

5. Build the index:
```bash
python scripts/build_index.py
```

6. Run the UI:
```bash
streamlit run ui/streamlit_app.py
```

## API Usage

Start the API server:
```bash
python api/main.py
```

Query the API:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What was ACC\'s EBITDA in Q3 2024?", "top_k": 5}'
```

## Project Structure

See `RAG_PIPELINE_DESIGN.md` for detailed architecture documentation.
