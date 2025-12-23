"""
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
