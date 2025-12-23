"""
Setup script to create the RAG pipeline directory structure
"""
import os
from pathlib import Path

def create_rag_structure():
    """Create the complete directory structure for RAG pipeline"""
    
    base_dir = Path("cement_rag_pipeline")
    
    # Define directory structure
    structure = {
        "data": ["raw", "processed", "embeddings"],
        "src": [
            "ingestion",
            "processing", 
            "embedding",
            "vectorstore",
            "retrieval",
            "generation",
            "analysis",
            "utils"
        ],
        "notebooks": [],
        "api": [],
        "ui/components": [],
        "tests": [],
        "configs": [],
        "scripts": [],
        "docker": [],
        "logs": []
    }
    
    # Create directories
    print(f"Creating RAG pipeline structure in: {base_dir.absolute()}")
    
    for main_dir, subdirs in structure.items():
        if subdirs:
            for subdir in subdirs:
                path = base_dir / main_dir / subdir
                path.mkdir(parents=True, exist_ok=True)
                print(f"✓ Created: {path}")
                # Create __init__.py for Python packages
                if main_dir == "src":
                    (path / "__init__.py").touch()
        else:
            path = base_dir / main_dir
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {path}")
            if main_dir in ["src", "api", "tests"]:
                (path / "__init__.py").touch()
    
    # Create specific files
    files_to_create = {
        "src/ingestion/pdf_extractor.py": PDF_EXTRACTOR_TEMPLATE,
        "src/ingestion/metadata_parser.py": METADATA_PARSER_TEMPLATE,
        "src/processing/chunker.py": CHUNKER_TEMPLATE,
        "src/embedding/embedder.py": EMBEDDER_TEMPLATE,
        "src/vectorstore/qdrant_client.py": QDRANT_CLIENT_TEMPLATE,
        "src/retrieval/retriever.py": RETRIEVER_TEMPLATE,
        "src/generation/llm_client.py": LLM_CLIENT_TEMPLATE,
        "src/utils/config.py": CONFIG_TEMPLATE,
        "api/main.py": API_MAIN_TEMPLATE,
        "ui/streamlit_app.py": STREAMLIT_TEMPLATE,
        "scripts/build_index.py": BUILD_INDEX_TEMPLATE,
        ".env.example": ENV_TEMPLATE,
        "README.md": README_TEMPLATE,
        "docker/Dockerfile": DOCKERFILE_TEMPLATE,
        "docker/docker-compose.yml": DOCKER_COMPOSE_TEMPLATE,
    }
    
    for file_path, content in files_to_create.items():
        full_path = base_dir / file_path
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Created: {full_path}")
    
    print("\n✅ RAG pipeline structure created successfully!")
    print(f"\nNext steps:")
    print(f"1. cd {base_dir}")
    print(f"2. Copy .env.example to .env and configure")
    print(f"3. pip install -r ../rag_requirements.txt")
    print(f"4. Copy your data to data/raw/")
    print(f"5. Run: python scripts/build_index.py")

# Template contents
PDF_EXTRACTOR_TEMPLATE = '''"""
PDF text extraction module
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Extract text and metadata from PDF files"""
    
    def __init__(self, extract_tables: bool = True):
        self.extract_tables = extract_tables
    
    def extract_from_file(self, pdf_path: Path) -> Dict:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            doc = fitz.open(pdf_path)
            
            text_blocks = []
            for page_num, page in enumerate(doc, 1):
                text = page.get_text()
                text_blocks.append({
                    'page': page_num,
                    'text': text
                })
            
            full_text = '\\n'.join([block['text'] for block in text_blocks])
            
            metadata = {
                'filename': pdf_path.name,
                'num_pages': len(doc),
                'file_size': pdf_path.stat().st_size,
            }
            
            doc.close()
            
            return {
                'text': full_text,
                'text_blocks': text_blocks,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error extracting PDF {pdf_path}: {e}")
            return None
    
    def extract_batch(self, pdf_paths: List[Path]) -> List[Dict]:
        """Extract from multiple PDFs"""
        results = []
        for pdf_path in pdf_paths:
            result = self.extract_from_file(pdf_path)
            if result:
                results.append(result)
        return results
'''

METADATA_PARSER_TEMPLATE = '''"""
CSV metadata parser
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class MetadataParser:
    """Parse and structure metadata from CSV"""
    
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.df = None
    
    def load(self):
        """Load CSV file"""
        try:
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(self.df)} records from {self.csv_path}")
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def get_metadata_for_file(self, filename: str) -> Dict:
        """Get metadata for a specific file"""
        # Match filename to CSV records
        # This needs to be customized based on your filename format
        pass
    
    def get_all_companies(self) -> List[str]:
        """Get list of all companies"""
        if self.df is not None:
            return self.df['CompanyName'].unique().tolist()
        return []
    
    def filter_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Filter records by date range"""
        if self.df is not None:
            return self.df[
                (self.df['Date'] >= start_date) & 
                (self.df['Date'] <= end_date)
            ]
        return pd.DataFrame()
'''

CHUNKER_TEMPLATE = '''"""
Document chunking module
"""
from typing import List, Dict
import re
import logging

logger = logging.getLogger(__name__)

class DocumentChunker:
    """Chunk documents into smaller pieces"""
    
    def __init__(
        self, 
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        min_chunk_size: int = 200
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks
        
        Args:
            text: Full text to chunk
            metadata: Document metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        sentences = self._split_into_sentences(text)
        
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_size + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text) >= self.min_chunk_size:
                    chunks.append({
                        'text': chunk_text,
                        'metadata': metadata or {},
                        'chunk_id': len(chunks)
                    })
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap(current_chunk)
                current_chunk = overlap_sentences
                current_size = sum(len(s) for s in current_chunk)
            
            current_chunk.append(sentence)
            current_size += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append({
                    'text': chunk_text,
                    'metadata': metadata or {},
                    'chunk_id': len(chunks)
                })
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be improved with spaCy)
        sentences = re.split(r'(?<=[.!?])\\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap(self, sentences: List[str]) -> List[str]:
        """Get overlap sentences for next chunk"""
        overlap_chars = 0
        overlap_sentences = []
        
        for sentence in reversed(sentences):
            if overlap_chars + len(sentence) <= self.chunk_overlap:
                overlap_sentences.insert(0, sentence)
                overlap_chars += len(sentence)
            else:
                break
        
        return overlap_sentences
'''

EMBEDDER_TEMPLATE = '''"""
Text embedding module
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Embedder:
    """Generate embeddings for text"""
    
    def __init__(
        self, 
        model_name: str = "BAAI/bge-large-en-v1.5",
        device: str = "cpu"
    ):
        self.model_name = model_name
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load embedding model"""
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text
        
        Args:
            text: Single text or list of texts
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(text, str):
            text = [text]
        
        embeddings = self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        
        return embeddings
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed texts in batches"""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return embeddings
'''

QDRANT_CLIENT_TEMPLATE = '''"""
Qdrant vector database client
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class QdrantVectorStore:
    """Interface to Qdrant vector database"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "cement_transcripts"
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)
    
    def create_collection(self, vector_size: int):
        """Create a new collection"""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
    
    def add_documents(self, documents: List[Dict], embeddings: List):
        """Add documents with embeddings to collection"""
        points = []
        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            point = PointStruct(
                id=idx,
                vector=embedding.tolist(),
                payload=doc
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Added {len(points)} documents to collection")
    
    def search(
        self, 
        query_vector: List[float], 
        limit: int = 5,
        filter_dict: Dict = None
    ):
        """Search for similar documents"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=filter_dict
        )
        return results
'''

RETRIEVER_TEMPLATE = '''"""
Document retrieval module
"""
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class Retriever:
    """Retrieve relevant documents"""
    
    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Dict = None
    ) -> List[Dict]:
        """
        Retrieve relevant documents for query
        
        Args:
            query: User query
            top_k: Number of results to return
            filters: Metadata filters
            
        Returns:
            List of retrieved documents
        """
        # Embed query
        query_embedding = self.embedder.embed_text(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_vector=query_embedding[0].tolist(),
            limit=top_k,
            filter_dict=filters
        )
        
        documents = []
        for result in results:
            documents.append({
                'text': result.payload.get('text'),
                'metadata': result.payload.get('metadata'),
                'score': result.score
            })
        
        logger.info(f"Retrieved {len(documents)} documents for query")
        return documents
'''

LLM_CLIENT_TEMPLATE = '''"""
LLM client for response generation
"""
from openai import OpenAI
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for LLM generation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_response(
        self,
        query: str,
        context_documents: List[Dict],
        system_prompt: str = None
    ) -> str:
        """
        Generate response using LLM
        
        Args:
            query: User query
            context_documents: Retrieved context documents
            system_prompt: System prompt for LLM
            
        Returns:
            Generated response
        """
        # Format context
        context = self._format_context(context_documents)
        
        # Create messages
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        user_message = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""
        
        messages.append({"role": "user", "content": user_message})
        
        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    def _format_context(self, documents: List[Dict]) -> str:
        """Format context documents for prompt"""
        context_parts = []
        for idx, doc in enumerate(documents, 1):
            metadata = doc.get('metadata', {})
            company = metadata.get('company_name', 'Unknown')
            date = metadata.get('date', 'Unknown')
            
            context_parts.append(
                f"[{idx}] Company: {company}, Date: {date}\\n{doc['text']}\\n"
            )
        
        return "\\n".join(context_parts)
'''

CONFIG_TEMPLATE = '''"""
Configuration management
"""
import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: str = "configs/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[Any, Any]:
        """Load configuration from YAML"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
'''

API_MAIN_TEMPLATE = '''"""
FastAPI application
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Cement RAG API")

class Query(BaseModel):
    query: str
    top_k: Optional[int] = 5
    filters: Optional[dict] = None

class Response(BaseModel):
    answer: str
    sources: List[dict]
    confidence: Optional[float] = None

@app.get("/")
def read_root():
    return {"message": "Cement RAG API is running"}

@app.post("/query", response_model=Response)
def query_documents(query: Query):
    """Query the RAG system"""
    try:
        # TODO: Implement RAG pipeline
        # 1. Retrieve relevant documents
        # 2. Generate response with LLM
        # 3. Format and return
        
        return Response(
            answer="Implementation pending",
            sources=[]
        )
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

STREAMLIT_TEMPLATE = '''"""
Streamlit UI for Cement RAG
"""
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Cement Industry RAG Assistant",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Cement Industry RAG Assistant")
st.write("Ask questions about cement company conference calls")

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    companies = st.multiselect(
        "Filter by Companies",
        options=[
            "ACC Limited", "Ambuja Cements", "UltraTech Cement",
            "Shree Cement", "Dalmia Bharat Ltd", "Grasim Industries"
        ]
    )
    
    date_range = st.date_input("Date Range", value=[])
    
    top_k = st.slider("Number of results", 1, 10, 5)

# Main chat interface
query = st.text_input("Enter your question:")

if st.button("Ask"):
    if query:
        with st.spinner("Searching..."):
            # TODO: Implement RAG query
            st.write("Response will appear here")
            
            with st.expander("View Sources"):
                st.write("Source documents will appear here")
    else:
        st.warning("Please enter a question")

# Sample questions
st.sidebar.header("Sample Questions")
sample_questions = [
    "What was ACC's EBITDA margin in Q3 2024?",
    "Compare capacity utilization across companies",
    "What are the key industry trends?"
]

for q in sample_questions:
    if st.sidebar.button(q):
        st.rerun()
'''

BUILD_INDEX_TEMPLATE = '''"""
Script to build vector index from documents
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingestion.pdf_extractor import PDFExtractor
from processing.chunker import DocumentChunker
from embedding.embedder import Embedder
from vectorstore.qdrant_client import QdrantVectorStore
from utils.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Build vector index from PDF documents"""
    
    # Load config
    config = Config()
    
    # Initialize components
    pdf_extractor = PDFExtractor()
    chunker = DocumentChunker(
        chunk_size=config.get('chunking.chunk_size', 800),
        chunk_overlap=config.get('chunking.chunk_overlap', 150)
    )
    embedder = Embedder(
        model_name=config.get('embedding.local.model_name'),
        device=config.get('embedding.local.device', 'cpu')
    )
    vector_store = QdrantVectorStore(
        host=config.get('vectorstore.qdrant.host', 'localhost'),
        port=config.get('vectorstore.qdrant.port', 6333),
        collection_name=config.get('vectorstore.qdrant.collection_name')
    )
    
    # Get PDF files
    data_dir = Path(config.get('data.raw_transcripts_dir'))
    pdf_files = list(data_dir.rglob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    # Create collection
    vector_store.create_collection(vector_size=1024)
    
    # Process documents
    all_chunks = []
    for pdf_file in pdf_files:
        logger.info(f"Processing: {pdf_file.name}")
        
        # Extract text
        extracted = pdf_extractor.extract_from_file(pdf_file)
        if not extracted:
            continue
        
        # Chunk text
        chunks = chunker.chunk_text(
            extracted['text'],
            metadata=extracted['metadata']
        )
        all_chunks.extend(chunks)
    
    logger.info(f"Total chunks: {len(all_chunks)}")
    
    # Generate embeddings
    texts = [chunk['text'] for chunk in all_chunks]
    embeddings = embedder.embed_batch(texts, batch_size=32)
    
    # Add to vector store
    vector_store.add_documents(all_chunks, embeddings)
    
    logger.info("✅ Index built successfully!")

if __name__ == "__main__":
    main()
'''

ENV_TEMPLATE = '''# Environment Variables

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis Configuration (optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# Logging
LOG_LEVEL=INFO
'''

README_TEMPLATE = '''# Cement Industry RAG Pipeline

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
curl -X POST "http://localhost:8000/query" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What was ACC\\'s EBITDA in Q3 2024?", "top_k": 5}'
```

## Project Structure

See `RAG_PIPELINE_DESIGN.md` for detailed architecture documentation.
'''

DOCKERFILE_TEMPLATE = '''FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ../rag_requirements.txt .
RUN pip install --no-cache-dir -r rag_requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

DOCKER_COMPOSE_TEMPLATE = '''version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  qdrant_data:
  redis_data:
'''

if __name__ == "__main__":
    create_rag_structure()
