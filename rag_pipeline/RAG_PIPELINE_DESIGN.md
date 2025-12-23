# RAG Pipeline for Cement Company Conference Calls

## Overview
This document outlines a comprehensive Retrieval-Augmented Generation (RAG) system for querying and analyzing cement company conference call transcripts spanning 2 years across 13 major cement companies.

## Data Summary
- **Companies**: 13 cement companies (ACC, Ambuja, UltraTech, Shree Cement, etc.)
- **Time Period**: 2 years (2024-2025)
- **Data Format**: PDF transcripts of quarterly earnings calls
- **Total Documents**: ~65 conference calls
- **Metadata Available**: Company name, date, script code, company ID, URLs

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG PIPELINE ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. DATA INGESTION → 2. PROCESSING → 3. EMBEDDING           │
│         ↓                  ↓              ↓                  │
│  4. VECTOR STORAGE → 5. RETRIEVAL → 6. GENERATION           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Data Ingestion Layer

### Components:
- **PDF Parser**: Extract text from conference call PDFs
- **Metadata Extractor**: Parse CSV for structured metadata
- **Audio Processor** (optional): Transcribe audio files where available

### Implementation:
```python
# Tools: PyPDF2, pdfplumber, or PyMuPDF (fitz)
# Extract: Text content, tables, financial figures
# Preserve: Document structure, speaker annotations
```

### Metadata Schema:
```json
{
  "document_id": "unique_id",
  "company_name": "ACC Limited",
  "script_code": "ACC",
  "company_id": "6",
  "quarter": "Q3",
  "fiscal_year": "FY2024",
  "date": "2024-11-01",
  "document_type": "transcript",
  "source_url": "https://...",
  "file_path": "Cement_Concall_Transcripts/ACC Limited/..."
}
```

---

## 2. Document Processing Layer

### Text Preprocessing:
1. **Clean extracted text**:
   - Remove headers/footers
   - Fix OCR errors
   - Normalize whitespace
   - Handle special characters

2. **Structure Detection**:
   - Identify sections (Management Discussion, Q&A, Financial Highlights)
   - Extract speaker labels
   - Detect question-answer pairs
   - Parse financial tables

3. **Entity Recognition**:
   - Financial metrics (revenue, EBITDA, margins, volumes)
   - Geographic locations (plants, markets)
   - Time periods (quarters, years)
   - Key personnel names

### Chunking Strategy:

#### Option A: Semantic Chunking (Recommended)
- **Chunk by Topic**: Use NLP to identify topic boundaries
- **Chunk Size**: 500-1000 tokens with 100-token overlap
- **Benefits**: Maintains context, better semantic coherence

#### Option B: Structural Chunking
- **By Section**: Separate chunks for Q&A, management remarks, financials
- **By Speaker**: Group statements by individual speakers
- **By Question-Answer Pairs**: Keep Q&A intact

#### Option C: Hybrid Approach (Best)
```python
Chunk Types:
1. Executive Summary Chunks (500 tokens)
2. Financial Statement Chunks (300 tokens)
3. Q&A Pair Chunks (variable, keep complete)
4. Management Commentary Chunks (700 tokens)
```

### Chunk Metadata Enhancement:
```json
{
  "chunk_id": "uuid",
  "parent_document_id": "doc_uuid",
  "chunk_type": "qa_pair|management_statement|financial_data",
  "section": "Q&A Session",
  "speaker": "CFO Name",
  "position_in_doc": 5,
  "entities": {
    "metrics": ["EBITDA", "Capacity Utilization"],
    "locations": ["Eastern Region", "Gujarat"],
    "competitors": ["UltraTech", "Ambuja"]
  },
  "financial_figures": {
    "revenue": 2500,
    "ebitda_margin": 18.5
  }
}
```

---

## 3. Embedding & Vectorization Layer

### Embedding Models (Choose one):

#### Option 1: OpenAI Embeddings
- **Model**: `text-embedding-3-large` (3072 dimensions)
- **Pros**: High quality, proven performance
- **Cons**: API costs, rate limits
- **Cost**: ~$0.13 per 1M tokens

#### Option 2: Open-Source Models (Recommended)
- **Model**: `BAAI/bge-large-en-v1.5` (1024 dimensions)
- **Alternative**: `sentence-transformers/all-mpnet-base-v2`
- **Pros**: Free, runs locally, good performance
- **Cons**: Requires GPU for speed

#### Option 3: Domain-Specific Fine-tuning
- **Base Model**: BGE-large or MPNet
- **Fine-tune on**: Financial documents, earnings calls
- **Dataset**: SEC filings, earnings transcripts (publicly available)

### Multi-Vector Strategy:
```python
For each chunk, create multiple embeddings:
1. Dense Embedding: Full semantic representation
2. Sparse Embedding: BM25/SPLADE for keyword matching
3. Financial Embedding: Specialized for numbers/metrics
```

---

## 4. Vector Database Layer

### Database Options:

#### Option 1: Qdrant (Recommended for Local)
```python
Pros:
- Fast and efficient
- Excellent filtering capabilities
- Easy local deployment
- Good documentation
- Payload filtering support

Setup:
- Docker container or Python library
- Persistent storage
- HNSW index for fast search
```

#### Option 2: ChromaDB (Simplest)
```python
Pros:
- Easy to set up
- Built-in metadata filtering
- Good for prototyping
- Lightweight

Cons:
- Less performant at scale
```

#### Option 3: Pinecone (Cloud)
```python
Pros:
- Managed service
- Scalable
- Built-in hybrid search

Cons:
- Costs money
- Requires internet
```

#### Option 4: PostgreSQL + pgvector (Enterprise)
```python
Pros:
- Use existing database
- ACID compliance
- Complex SQL queries with vector search

Setup:
- PostgreSQL with pgvector extension
```

### Collection Structure:
```python
Collections:
1. main_transcripts: Full semantic chunks
2. financial_metrics: Extracted financial data
3. qa_pairs: Question-answer specific
4. company_summaries: High-level company info
```

### Indexing Strategy:
```python
Indexes:
- Vector Index: HNSW (M=16, efConstruction=200)
- Metadata Indexes: 
  - company_name
  - date (range queries)
  - chunk_type
  - financial metrics (for filtering)
```

---

## 5. Retrieval Layer

### Multi-Stage Retrieval Pipeline:

#### Stage 1: Initial Retrieval
```python
def initial_retrieval(query, top_k=20):
    # Hybrid search combining:
    # 1. Dense vector similarity (70% weight)
    # 2. Sparse keyword matching (30% weight)
    # 3. Apply metadata filters
    return candidates
```

#### Stage 2: Reranking
```python
def rerank(query, candidates, top_k=5):
    # Use cross-encoder model:
    # - Model: ms-marco-MiniLM or bge-reranker
    # - Score query-chunk relevance
    # - Select top-k most relevant
    return reranked_results
```

#### Stage 3: Context Enhancement
```python
def enhance_context(chunks):
    # For each chunk:
    # 1. Fetch parent document context
    # 2. Retrieve adjacent chunks
    # 3. Add financial metadata
    # 4. Include company comparison data
    return enhanced_chunks
```

### Query Processing:

#### Query Classification:
```python
Query Types:
1. Factual: "What was ACC's EBITDA in Q3 2024?"
2. Comparative: "Compare UltraTech and Ambuja margins"
3. Trend: "How has cement demand changed over time?"
4. Strategic: "What expansion plans did companies discuss?"
5. Aggregation: "Average capacity utilization across companies"
```

#### Query Expansion:
```python
def expand_query(query):
    # Add synonyms: "EBITDA" → ["EBITDA", "operating margin", "profitability"]
    # Add company variants: "ACC" → ["ACC Limited", "ACC Cement"]
    # Add time context: implicit quarter mapping
    return expanded_query
```

### Filtering Strategy:
```python
Dynamic Filters:
- Date Range: last_n_quarters, specific_year
- Companies: single or multiple
- Metrics: financial_only, strategic_only
- Section Type: qa_only, management_only
```

---

## 6. Generation Layer

### LLM Selection:

#### Option 1: OpenAI GPT-4
- **Model**: GPT-4-turbo or GPT-4
- **Context**: 128K tokens
- **Pros**: Best quality, reliable
- **Cons**: Expensive (~$10/1M input tokens)

#### Option 2: Anthropic Claude
- **Model**: Claude 3.5 Sonnet
- **Context**: 200K tokens
- **Pros**: Great reasoning, large context
- **Cons**: API costs

#### Option 3: Open-Source (Local)
- **Model**: Llama 3.1 70B or Mixtral 8x7B
- **Quantization**: 4-bit for consumer GPU
- **Pros**: Free, private, customizable
- **Cons**: Needs powerful hardware

### Prompt Engineering:

#### System Prompt Template:
```python
SYSTEM_PROMPT = """You are a financial analyst specializing in the Indian cement industry. 
You have access to conference call transcripts from 13 major cement companies over 2 years.

Your role is to:
1. Provide accurate, data-driven insights from the transcripts
2. Compare companies when relevant
3. Identify trends and patterns
4. Cite specific sources with company name and date
5. Acknowledge when information is not available in the data

Key Guidelines:
- Always cite the source (Company name + Quarter/Year)
- Distinguish between management statements and analyst questions
- Highlight financial metrics with units
- Note if data is preliminary or audited
- Flag contradictions or inconsistencies across calls
"""
```

#### Query Prompt Template:
```python
QUERY_PROMPT = """Based on the following conference call excerpts, answer the user's question.

User Question: {query}

Retrieved Context:
{context_chunks}

Instructions:
1. Answer the question directly and concisely
2. Use specific data points from the context
3. Cite sources: [Company, Quarter Year]
4. If comparing, present in structured format
5. Highlight key insights or trends
6. If information is incomplete, state what's missing

Answer:"""
```

### Response Enhancement:

#### Citation Tracking:
```python
def add_citations(response, chunks):
    # Add footnote-style references
    # Link back to source documents
    # Include page numbers if available
    return response_with_citations
```

#### Structured Output:
```python
Response Format:
{
    "answer": "Main answer text with [1][2] citations",
    "key_metrics": {
        "ACC EBITDA Q3 2024": "450 Cr",
        "UltraTech Revenue Q3 2024": "5600 Cr"
    },
    "sources": [
        {"company": "ACC", "date": "2024-11-01", "chunk_id": "..."},
    ],
    "confidence": 0.92,
    "follow_up_questions": [
        "How does this compare to previous quarters?",
        "What factors drove this change?"
    ]
}
```

---

## 7. Advanced Features

### A. Multi-Document Reasoning
```python
# Compare across companies and time periods
# Identify industry-wide trends
# Detect correlations between companies
```

### B. Financial Analysis Tools
```python
Tools:
1. Metric Calculator: Compute ratios, growth rates
2. Trend Analyzer: Time-series analysis
3. Peer Comparator: Company benchmarking
4. Sentiment Analyzer: Management tone/confidence
```

### C. Query Routing
```python
def route_query(query):
    if is_factual(query):
        return simple_retrieval_pipeline()
    elif is_analytical(query):
        return multi_doc_reasoning_pipeline()
    elif is_comparative(query):
        return comparative_analysis_pipeline()
```

### D. Conversation Memory
```python
# Maintain conversation context
# Remember previously discussed companies
# Track multi-turn queries
# Enable follow-up questions
```

---

## 8. Evaluation & Monitoring

### Metrics to Track:

#### Retrieval Metrics:
- **Recall@k**: Are relevant docs in top-k?
- **MRR**: Mean Reciprocal Rank
- **NDCG**: Normalized Discounted Cumulative Gain

#### Generation Metrics:
- **Answer Accuracy**: Manual evaluation
- **Citation Accuracy**: Are sources correctly referenced?
- **Hallucination Rate**: Unsupported claims
- **Response Time**: Latency measurement

#### User Experience:
- **User Satisfaction**: Thumbs up/down
- **Query Success Rate**: Did user get answer?
- **Refinement Rate**: How often users rephrase?

### Evaluation Dataset:
```python
Create test queries:
- 50 factual questions with known answers
- 25 comparative questions
- 25 analytical questions

Example:
Q: "What was UltraTech's cement capacity in Q2 2024?"
Expected: Specific number + source citation
```

---

## 9. Implementation Roadmap

### Phase 1: MVP (Week 1-2)
- [ ] PDF text extraction
- [ ] Basic chunking (500 tokens)
- [ ] ChromaDB setup
- [ ] OpenAI embeddings
- [ ] Simple retrieval (top-5)
- [ ] GPT-3.5/4 generation
- [ ] Basic Streamlit UI

### Phase 2: Enhancement (Week 3-4)
- [ ] Metadata extraction and indexing
- [ ] Hybrid search (dense + sparse)
- [ ] Reranker integration
- [ ] Citation tracking
- [ ] Query classification
- [ ] Improved chunking strategy

### Phase 3: Advanced (Week 5-6)
- [ ] Multi-document reasoning
- [ ] Financial analysis tools
- [ ] Comparison dashboards
- [ ] Conversation memory
- [ ] User feedback loop
- [ ] Performance optimization

### Phase 4: Production (Week 7-8)
- [ ] Switch to local LLM (optional)
- [ ] Deploy to Qdrant/Pinecone
- [ ] API development
- [ ] Comprehensive testing
- [ ] Documentation
- [ ] Monitoring & logging

---

## 10. Technical Stack Recommendations

### Recommended Stack (Balanced):
```python
# Data Processing
- PDF Extraction: PyMuPDF (fitz)
- Text Processing: spaCy, nltk
- CSV Handling: pandas

# Embeddings
- Model: BAAI/bge-large-en-v1.5
- Framework: sentence-transformers
- Reranker: bge-reranker-large

# Vector Database
- Primary: Qdrant (Docker)
- Alternative: ChromaDB for testing

# LLM
- Development: OpenAI GPT-4-turbo
- Production: Claude 3.5 Sonnet or Llama 3.1

# Framework
- RAG Framework: LangChain or LlamaIndex
- API: FastAPI
- UI: Streamlit or Gradio

# Monitoring
- Observability: Langfuse or Arize
- Logging: Python logging + file rotation
```

### Cost-Optimized Stack (Local):
```python
- Embeddings: sentence-transformers (local)
- Vector DB: ChromaDB or Qdrant (local)
- LLM: Llama 3.1 70B (4-bit quantized)
- Inference: Ollama or vLLM
- Total cost: ~$0 (hardware dependent)
```

### Production Stack (Scalable):
```python
- Embeddings: OpenAI text-embedding-3-large
- Vector DB: Pinecone or Weaviate Cloud
- LLM: OpenAI GPT-4-turbo with caching
- Framework: LangChain + LangSmith
- Deployment: Docker + Kubernetes
- Monitoring: Full observability stack
```

---

## 11. Directory Structure

```
cement_rag_pipeline/
├── data/
│   ├── raw/                          # Original PDFs and CSV
│   ├── processed/                    # Cleaned and structured data
│   └── embeddings/                   # Cached embeddings
├── src/
│   ├── ingestion/
│   │   ├── pdf_extractor.py         # PDF text extraction
│   │   ├── metadata_parser.py       # CSV metadata processing
│   │   └── audio_transcriber.py     # Audio processing (optional)
│   ├── processing/
│   │   ├── text_cleaner.py          # Text preprocessing
│   │   ├── chunker.py               # Document chunking
│   │   ├── entity_extractor.py      # NER for financial entities
│   │   └── metadata_enhancer.py     # Chunk metadata enrichment
│   ├── embedding/
│   │   ├── embedder.py              # Embedding generation
│   │   └── model_loader.py          # Model management
│   ├── vectorstore/
│   │   ├── qdrant_client.py         # Vector DB operations
│   │   └── indexer.py               # Indexing logic
│   ├── retrieval/
│   │   ├── retriever.py             # Main retrieval logic
│   │   ├── reranker.py              # Reranking module
│   │   ├── query_processor.py       # Query expansion/classification
│   │   └── filters.py               # Metadata filtering
│   ├── generation/
│   │   ├── llm_client.py            # LLM interface
│   │   ├── prompt_templates.py      # Prompt management
│   │   └── response_formatter.py    # Output formatting
│   ├── analysis/
│   │   ├── financial_tools.py       # Metric calculators
│   │   ├── comparator.py            # Company comparison
│   │   └── trend_analyzer.py        # Time-series analysis
│   └── utils/
│       ├── config.py                # Configuration
│       ├── logger.py                # Logging setup
│       └── helpers.py               # Utility functions
├── notebooks/
│   ├── 01_data_exploration.ipynb    # EDA
│   ├── 02_chunking_experiments.ipynb
│   ├── 03_embedding_evaluation.ipynb
│   └── 04_retrieval_testing.ipynb
├── api/
│   ├── main.py                      # FastAPI app
│   ├── models.py                    # Pydantic models
│   └── endpoints.py                 # API endpoints
├── ui/
│   ├── streamlit_app.py             # Streamlit interface
│   └── components/                  # UI components
├── tests/
│   ├── test_retrieval.py
│   ├── test_generation.py
│   └── test_e2e.py
├── configs/
│   ├── config.yaml                  # Main configuration
│   └── prompts.yaml                 # Prompt templates
├── scripts/
│   ├── build_index.py               # Build vector index
│   ├── evaluate.py                  # Evaluation script
│   └── deploy.py                    # Deployment script
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── README.md
└── .env                             # Environment variables
```

---

## 12. Sample Usage Examples

### Example 1: Factual Query
```
User: "What was ACC Limited's EBITDA margin in Q3 2024?"

Process:
1. Extract entities: Company=ACC, Metric=EBITDA margin, Period=Q3 2024
2. Filter: company_name="ACC Limited", date="2024-11-01"
3. Retrieve: Chunks with financial data from ACC Q3 2024
4. Generate: Extract specific number with citation

Response: "ACC Limited reported an EBITDA margin of 18.5% in Q3 FY2024 
[ACC Limited, November 2024 Earnings Call]"
```

### Example 2: Comparative Query
```
User: "Compare capacity utilization between UltraTech and Ambuja in 2024"

Process:
1. Identify comparison: Companies=[UltraTech, Ambuja], Metric=Capacity utilization
2. Retrieve: All 2024 calls for both companies with capacity data
3. Aggregate: Extract quarterly figures
4. Generate: Structured comparison

Response: 
"Capacity Utilization Comparison (2024):
- UltraTech: Q1: 75%, Q2: 78%, Q3: 72%
- Ambuja: Q1: 71%, Q2: 74%, Q3: 69%

UltraTech maintained higher utilization throughout 2024, averaging 75% 
vs Ambuja's 71.3%. Both companies saw a dip in Q3 due to monsoon season.
[Sources: UltraTech Q1-Q3 2024, Ambuja Q1-Q3 2024 calls]"
```

### Example 3: Trend Analysis
```
User: "What are the key themes in cement industry discussions over the past year?"

Process:
1. Broad retrieval: All companies, all sections, last 4 quarters
2. Topic modeling: Identify recurring themes
3. Frequency analysis: Count mentions across companies
4. Generate: Synthesized insights

Response:
"Key themes in cement industry discussions (2024):

1. Demand Recovery (mentioned in 12/13 companies):
   - Infrastructure push driving demand
   - Housing sector showing resilience

2. Cost Pressures (universal concern):
   - Coal prices moderating vs. 2023
   - Logistics costs remain elevated

3. Capacity Expansion (8/13 companies):
   - UltraTech, Ambuja, Dalmia announcing new plants
   - Focus on clinkerization capacity

4. Sustainability Initiatives (growing focus):
   - Green energy adoption
   - Blended cement push

[Analysis based on 52 conference calls from 13 companies]"
```

---

## 13. Optimization Tips

### Performance Optimization:
```python
1. Caching:
   - Cache embeddings (save re-computation)
   - Cache frequently asked queries
   - Cache LLM responses for identical queries

2. Batch Processing:
   - Embed documents in batches
   - Batch API calls to LLM provider

3. Async Operations:
   - Parallel retrieval from vector DB
   - Async LLM calls
   - Background indexing

4. Smart Filtering:
   - Pre-filter by metadata before vector search
   - Use date indexes for temporal queries
   - Company-specific collections
```

### Cost Optimization:
```python
1. Embedding Costs:
   - Use smaller embedding models for less critical chunks
   - Batch embed to reduce API calls
   - Consider local models

2. LLM Costs:
   - Use GPT-3.5 for simple queries, GPT-4 for complex
   - Implement response caching
   - Compress context (remove redundancy)
   - Use smaller context windows when possible

3. Storage:
   - Compress older embeddings
   - Implement data lifecycle policies
   - Use efficient serialization (msgpack vs JSON)
```

---

## 14. Security & Privacy Considerations

```python
1. Data Access:
   - Role-based access control
   - Audit logging for queries
   - Rate limiting on API

2. Data Privacy:
   - Ensure compliance with data usage rights
   - Anonymize PII if present in transcripts
   - Secure storage of embeddings

3. API Security:
   - API key management
   - Input validation and sanitization
   - Prevent prompt injection attacks
```

---

## Next Steps

1. **Review this design document**
2. **Choose your tech stack based on requirements**
3. **Start with Phase 1 MVP**
4. **Create evaluation dataset**
5. **Iterate based on performance metrics**

Would you like me to proceed with implementing any specific component of this pipeline?
