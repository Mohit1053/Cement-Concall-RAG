"""
Test script for embedding generation
Tests embedding model loading and vector generation
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from embedding.embedder import Embedder
from ingestion.pdf_extractor import PDFExtractor
from processing.text_cleaner import TextPreprocessor
from processing.chunker import DocumentChunker
import logging
import numpy as np
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_embedding_generation():
    """Test embedding model and generation"""
    
    logger.info("="*80)
    logger.info("EMBEDDING GENERATION TEST")
    logger.info("="*80)
    
    # Step 1: Load embedding model
    logger.info("\nSTEP 1: Loading Embedding Model")
    logger.info("="*80)
    
    try:
        embedder = Embedder(
            model_name="BAAI/bge-small-en-v1.5",  # Using smaller model for testing
            device="cpu"
        )
        logger.info(f"✅ Model loaded successfully")
        logger.info(f"   - Model: {embedder.model_name}")
        logger.info(f"   - Device: {embedder.device}")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        logger.info("\n⚠️  Installing sentence-transformers...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "sentence-transformers"])
        return
    
    # Step 2: Test single text embedding
    logger.info("\nSTEP 2: Single Text Embedding")
    logger.info("="*80)
    
    sample_text = "ACC Limited reported strong Q2 results with EBITDA margin of 18.5%"
    
    start_time = time.time()
    embedding = embedder.embed_text(sample_text)
    embed_time = time.time() - start_time
    
    logger.info(f"✅ Generated embedding for sample text")
    logger.info(f"   - Text: {sample_text[:80]}...")
    logger.info(f"   - Embedding shape: {embedding.shape}")
    logger.info(f"   - Embedding dim: {embedding.shape[1]}")
    logger.info(f"   - Time taken: {embed_time:.3f} seconds")
    logger.info(f"   - First 5 values: {embedding[0][:5]}")
    
    # Step 3: Test batch embedding
    logger.info("\nSTEP 3: Batch Text Embedding")
    logger.info("="*80)
    
    batch_texts = [
        "ACC Limited Q2 FY2024 earnings call transcript",
        "Capacity utilization remained strong at 75%",
        "Management discussed expansion plans in Eastern region",
        "Coal costs have moderated compared to previous quarter",
        "Demand outlook remains positive for infrastructure sector"
    ]
    
    start_time = time.time()
    batch_embeddings = embedder.embed_batch(batch_texts, batch_size=8)
    batch_time = time.time() - start_time
    
    logger.info(f"✅ Generated embeddings for {len(batch_texts)} texts")
    logger.info(f"   - Embeddings shape: {batch_embeddings.shape}")
    logger.info(f"   - Time taken: {batch_time:.3f} seconds")
    logger.info(f"   - Time per text: {batch_time/len(batch_texts):.3f} seconds")
    
    # Step 4: Test similarity computation
    logger.info("\nSTEP 4: Similarity Computation")
    logger.info("="*80)
    
    # Compute cosine similarity between first two texts
    from numpy.linalg import norm
    
    def cosine_similarity(a, b):
        return np.dot(a, b) / (norm(a) * norm(b))
    
    sim_1_2 = cosine_similarity(batch_embeddings[0], batch_embeddings[1])
    sim_1_3 = cosine_similarity(batch_embeddings[0], batch_embeddings[2])
    sim_2_3 = cosine_similarity(batch_embeddings[1], batch_embeddings[2])
    
    logger.info(f"✅ Similarity scores computed:")
    logger.info(f"   - Text 1 vs Text 2: {sim_1_2:.4f}")
    logger.info(f"   - Text 1 vs Text 3: {sim_1_3:.4f}")
    logger.info(f"   - Text 2 vs Text 3: {sim_2_3:.4f}")
    
    # Step 5: Test with real document chunks
    logger.info("\nSTEP 5: Real Document Embedding")
    logger.info("="*80)
    
    # Get sample document
    base_path = Path("..") / "Cement_Concall_Transcripts"
    pdf_files = list(base_path.rglob("*.pdf"))
    
    if pdf_files:
        sample_pdf = pdf_files[0]
        logger.info(f"Processing: {sample_pdf.name}")
        
        # Extract and chunk
        pdf_extractor = PDFExtractor()
        text_processor = TextPreprocessor()
        chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)
        
        extracted = pdf_extractor.extract_from_file(sample_pdf)
        if extracted:
            cleaned_text = text_processor.clean_text(extracted['text'])
            chunks = chunker.chunk_text(cleaned_text)
            
            # Take first 10 chunks
            sample_chunks = chunks[:10]
            chunk_texts = [c['text'] for c in sample_chunks]
            
            logger.info(f"   - Extracted {len(chunks)} chunks")
            logger.info(f"   - Embedding first {len(chunk_texts)} chunks...")
            
            start_time = time.time()
            chunk_embeddings = embedder.embed_batch(chunk_texts, batch_size=8)
            chunk_time = time.time() - start_time
            
            logger.info(f"✅ Generated embeddings for document chunks")
            logger.info(f"   - Embeddings shape: {chunk_embeddings.shape}")
            logger.info(f"   - Time taken: {chunk_time:.3f} seconds")
            logger.info(f"   - Time per chunk: {chunk_time/len(chunk_texts):.3f} seconds")
            
            # Estimate full document processing time
            total_estimate = (len(chunks) / len(chunk_texts)) * chunk_time
            logger.info(f"   - Estimated time for all {len(chunks)} chunks: {total_estimate:.1f} seconds")
    
    # Step 6: Performance benchmarks
    logger.info("\nSTEP 6: Performance Benchmarks")
    logger.info("="*80)
    
    # Test different batch sizes
    test_texts = ["Sample text for benchmark"] * 50
    
    batch_sizes = [1, 8, 16, 32]
    for batch_size in batch_sizes:
        start_time = time.time()
        _ = embedder.embed_batch(test_texts, batch_size=batch_size)
        elapsed = time.time() - start_time
        throughput = len(test_texts) / elapsed
        
        logger.info(f"   - Batch size {batch_size:2d}: {elapsed:.3f}s total, {throughput:.1f} texts/sec")
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("EMBEDDING TEST SUMMARY")
    logger.info("="*80)
    
    summary = {
        'model': embedder.model_name,
        'embedding_dimension': embedding.shape[1],
        'single_embed_time': f"{embed_time:.3f}s",
        'batch_embed_time': f"{batch_time:.3f}s",
        'batch_size': len(batch_texts),
        'avg_time_per_text': f"{batch_time/len(batch_texts):.3f}s",
    }
    
    for key, value in summary.items():
        logger.info(f"   - {key}: {value}")
    
    logger.info("\n" + "="*80)
    logger.info("✅ ALL EMBEDDING TESTS PASSED")
    logger.info("="*80)
    
    return embedder

if __name__ == "__main__":
    try:
        embedder = test_embedding_generation()
        if embedder:
            logger.info("\n✅ Embedding generation ready! Next: Vector database setup")
    except Exception as e:
        logger.error(f"Embedding test failed: {e}", exc_info=True)
