"""
Build vector index for all downloaded cement concalls (176 PDFs)
"""
import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "core"))

from ingestion.pdf_extractor import PDFExtractor
from processing.text_cleaner import TextPreprocessor
from processing.chunker import DocumentChunker
from processing.metadata_enhancer import MetadataEnhancer
from vector_store.tfidf_store import TFIDFVectorStore
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build_all_concalls_index.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Build index for all concalls."""
    
    print("="*80)
    print("BUILDING VECTOR INDEX - ALL CEMENT CONCALLS (176 PDFs)")
    print("="*80)
    
    # Paths
    pdf_dir = Path(__file__).parent.parent / "concall_downloader" / "Cement_Concall_Transcripts_All"
    output_dir = Path(__file__).parent / "data" / "vector_db_all"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nPDF Directory: {pdf_dir}")
    print(f"Output Directory: {output_dir}")
    
    # Find all PDFs
    pdf_files = list(pdf_dir.glob("**/*.pdf"))
    print(f"\nFound {len(pdf_files)} PDF files")
    
    # Initialize components
    print("\nInitializing components...")
    pdf_extractor = PDFExtractor()
    text_processor = TextPreprocessor()
    chunker = DocumentChunker(chunk_size=800, chunk_overlap=150, respect_qa_pairs=True)
    metadata_enhancer = MetadataEnhancer()
    vector_store = TFIDFVectorStore(persist_dir=str(output_dir))
    
    # Process documents
    print(f"\nProcessing {len(pdf_files)} documents...")
    
    all_chunks = []
    success_count = 0
    fail_count = 0
    start_time = time.time()
    
    for i, pdf_path in enumerate(pdf_files, 1):
        try:
            # Extract company name from path
            company_name = pdf_path.parent.name
            
            print(f"\n[{i}/{len(pdf_files)}] {company_name}/{pdf_path.name}")
            
            # Extract text
            pdf_data = pdf_extractor.extract_from_file(pdf_path)
            doc_text = pdf_data['text']
            
            if not doc_text or len(doc_text) < 100:
                print(f"  ✗ Too short ({len(doc_text)} chars)")
                fail_count += 1
                continue
            
            print(f"  Extracted: {len(doc_text):,} characters")
            
            # Clean text
            cleaned_text = text_processor.clean_text(doc_text)
            print(f"  Cleaned: {len(cleaned_text):,} characters")
            
            # Chunk document
            chunks = chunker.chunk_text(cleaned_text)
            print(f"  Chunks: {len(chunks)}")
            
            # Add company name to each chunk's metadata
            for chunk in chunks:
                if 'metadata' not in chunk:
                    chunk['metadata'] = {}
                chunk['metadata']['company_name'] = company_name
                chunk['metadata']['source_file'] = pdf_path.name
            
            all_chunks.extend(chunks)
            success_count += 1
            print(f"  ✓ Success (Total chunks: {len(all_chunks)})")
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:100]}")
            fail_count += 1
    
    # Add to vector store
    print(f"\n{'='*80}")
    print("Adding chunks to vector database...")
    print(f"{'='*80}")
    
    if all_chunks:
        vector_store.add_documents(all_chunks)
        vector_store.save()
        print(f"\n✓ Vector database saved to: {output_dir}")
    
    # Summary
    elapsed = time.time() - start_time
    print(f"\n{'='*80}")
    print("BUILD SUMMARY")
    print(f"{'='*80}")
    print(f"Total PDFs: {len(pdf_files)}")
    print(f"Successfully processed: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Time elapsed: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print(f"Average: {elapsed/len(pdf_files):.2f} seconds per document")
    
    # By company
    print(f"\nChunks by company:")
    company_chunks = {}
    for chunk in all_chunks:
        company = chunk.get('company_name', 'Unknown')
        company_chunks[company] = company_chunks.get(company, 0) + 1
    
    for company in sorted(company_chunks.keys()):
        print(f"  {company}: {company_chunks[company]} chunks")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
