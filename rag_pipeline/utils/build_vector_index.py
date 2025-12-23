"""
Build and populate vector database with document embeddings
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingestion.pdf_extractor import PDFExtractor
from processing.text_cleaner import TextPreprocessor
from processing.chunker import DocumentChunker
from processing.metadata_enhancer import MetadataEnhancer
from vectorstore.tfidf_store import TFIDFVectorStore
import logging
from tqdm import tqdm
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def build_vector_index(
    data_dir: str = "../Cement_Concall_Transcripts",
    max_documents: int = None,
    reset_collection: bool = False
):
    """
    Build vector index from PDF documents
    
    Args:
        data_dir: Directory containing PDF files
        max_documents: Maximum number of documents to process (None = all)
        reset_collection: Whether to reset existing collection
    """
    
    logger.info("="*80)
    logger.info("BUILDING VECTOR INDEX")
    logger.info("="*80)
    
    # Initialize components
    logger.info("\n1. Initializing components...")
    pdf_extractor = PDFExtractor()
    text_processor = TextPreprocessor()
    chunker = DocumentChunker(
        chunk_size=800,
        chunk_overlap=150,
        respect_qa_pairs=True
    )
    metadata_enhancer = MetadataEnhancer()
    
    # Initialize TF-IDF vector store (fully offline)
    vector_store = TFIDFVectorStore(persist_dir="data/vector_db")
    
    # Reset if requested
    if reset_collection:
        logger.info("Resetting collection...")
        vector_store.delete_collection()
    
    # Get PDF files
    data_path = Path(data_dir)
    pdf_files = list(data_path.rglob("*.pdf"))
    
    if max_documents:
        pdf_files = pdf_files[:max_documents]
    
    logger.info(f"\n2. Found {len(pdf_files)} PDF files to process")
    
    # Process documents
    total_chunks = 0
    successful_docs = 0
    failed_docs = 0
    
    start_time = time.time()
    
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        try:
            # Extract text
            extracted = pdf_extractor.extract_from_file(pdf_file)
            if not extracted:
                logger.warning(f"Failed to extract: {pdf_file.name}")
                failed_docs += 1
                continue
            
            # Get metadata
            file_metadata = metadata_enhancer.extract_from_filename(pdf_file.name)
            
            # Clean text
            cleaned_text = text_processor.clean_text(extracted['text'], file_metadata)
            
            # Chunk text
            chunks = chunker.chunk_text(cleaned_text, file_metadata)
            
            # Enrich chunks
            enriched_chunks = []
            for i, chunk in enumerate(chunks):
                enriched = metadata_enhancer.enrich_chunk_metadata(
                    chunk, file_metadata, i, len(chunks)
                )
                enriched_chunks.append(enriched)
            
            # Prepare for vector store
            chunks_for_db = []
            
            for i, chunk in enumerate(enriched_chunks):
                chunk_data = {
                    'text': chunk['text'],
                    'company_name': chunk.get('document_metadata', {}).get('company_name', ''),
                    'quarter': chunk.get('document_metadata', {}).get('quarter', ''),
                    'fiscal_year': chunk.get('document_metadata', {}).get('fiscal_year', ''),
                    'year': chunk.get('document_metadata', {}).get('year', ''),
                    'month': chunk.get('document_metadata', {}).get('month', ''),
                    'chunk_type': chunk.get('chunk_type', 'general'),
                    'chunk_index': chunk.get('chunk_index', 0),
                    'source_file': pdf_file.name
                }
                chunks_for_db.append(chunk_data)
            
            # Add to vector store
            added = vector_store.add_documents(chunks_for_db)
            
            total_chunks += added
            successful_docs += 1
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {e}")
            failed_docs += 1
            continue
    
    elapsed_time = time.time() - start_time
    
    # Save index
    vector_store.save()
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("INDEX BUILDING COMPLETE")
    logger.info("="*80)
    
    stats = vector_store.get_stats()
    
    summary = {
        'total_pdfs': len(pdf_files),
        'successful': successful_docs,
        'failed': failed_docs,
        'total_chunks': total_chunks,
        'avg_chunks_per_doc': total_chunks / successful_docs if successful_docs > 0 else 0,
        'time_elapsed': f"{elapsed_time:.1f}s",
        'time_per_doc': f"{elapsed_time/successful_docs:.2f}s" if successful_docs > 0 else "N/A",
        'vector_store_stats': stats
    }
    
    logger.info(f"\nProcessing Summary:")
    logger.info(f"  - PDFs processed: {successful_docs}/{len(pdf_files)}")
    logger.info(f"  - Failed: {failed_docs}")
    logger.info(f"  - Total chunks: {total_chunks}")
    logger.info(f"  - Avg chunks/doc: {summary['avg_chunks_per_doc']:.1f}")
    logger.info(f"  - Time elapsed: {summary['time_elapsed']}")
    logger.info(f"  - Time per doc: {summary['time_per_doc']}")
    
    logger.info(f"\nVector Store Stats:")
    logger.info(f"  - Total vectors: {stats['total_vectors']}")
    logger.info(f"  - Vocabulary size: {stats['vocabulary_size']}")
    logger.info(f"  - Location: {stats['persist_dir']}")
    
    logger.info("\n✅ Vector index built successfully!")
    
    return vector_store, summary

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Build vector index from PDFs')
    parser.add_argument('--max-docs', type=int, default=None, help='Maximum documents to process')
    parser.add_argument('--reset', action='store_true', help='Reset existing collection')
    parser.add_argument('--data-dir', type=str, default='../Cement_Concall_Transcripts', help='Data directory')
    
    args = parser.parse_args()
    
    try:
        vector_store, summary = build_vector_index(
            data_dir=args.data_dir,
            max_documents=args.max_docs,
            reset_collection=args.reset
        )
        
        logger.info("\n🎉 Ready for queries!")
        
    except Exception as e:
        logger.error(f"Failed to build index: {e}", exc_info=True)
