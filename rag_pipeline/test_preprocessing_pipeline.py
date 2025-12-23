"""
Test script for text preprocessing pipeline
Tests cleaning, chunking, entity extraction, and metadata enhancement
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ingestion.pdf_extractor import PDFExtractor
from processing.text_cleaner import TextPreprocessor
from processing.chunker import DocumentChunker
from processing.entity_extractor import EntityExtractor
from processing.metadata_enhancer import MetadataEnhancer
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_full_pipeline():
    """Test the complete preprocessing pipeline"""
    
    logger.info("="*80)
    logger.info("PREPROCESSING PIPELINE TEST")
    logger.info("="*80)
    
    # Initialize components
    pdf_extractor = PDFExtractor()
    text_processor = TextPreprocessor()
    chunker = DocumentChunker(
        chunk_size=800,
        chunk_overlap=150,
        respect_qa_pairs=True
    )
    entity_extractor = EntityExtractor()
    metadata_enhancer = MetadataEnhancer()
    
    # Get a sample PDF
    base_path = Path("..") / "Cement_Concall_Transcripts"
    pdf_files = list(base_path.rglob("*.pdf"))
    
    if not pdf_files:
        logger.error("No PDF files found")
        return
    
    sample_pdf = pdf_files[0]
    logger.info(f"\nTesting with: {sample_pdf.name}")
    
    # Step 1: Extract PDF
    logger.info("\n" + "="*80)
    logger.info("STEP 1: PDF EXTRACTION")
    logger.info("="*80)
    
    extracted = pdf_extractor.extract_from_file(sample_pdf)
    if not extracted:
        logger.error("PDF extraction failed")
        return
    
    raw_text = extracted['text']
    logger.info(f"✅ Extracted {len(raw_text):,} characters from {extracted['metadata']['num_pages']} pages")
    
    # Step 2: Extract metadata from filename
    logger.info("\n" + "="*80)
    logger.info("STEP 2: METADATA EXTRACTION")
    logger.info("="*80)
    
    file_metadata = metadata_enhancer.extract_from_filename(sample_pdf.name)
    logger.info(f"✅ Extracted metadata:")
    for key, value in file_metadata.items():
        logger.info(f"   - {key}: {value}")
    
    text_metadata = metadata_enhancer.extract_from_text(raw_text)
    logger.info(f"\n✅ Text metadata:")
    logger.info(f"   - Has Q&A: {text_metadata['has_qa']}")
    logger.info(f"   - Questions: {text_metadata['num_questions']}")
    logger.info(f"   - Speakers: {len(text_metadata['speakers'])} found")
    logger.info(f"   - Topics: {', '.join(text_metadata['topics'][:5])}")
    
    # Step 3: Clean text
    logger.info("\n" + "="*80)
    logger.info("STEP 3: TEXT CLEANING")
    logger.info("="*80)
    
    cleaned_text = text_processor.clean_text(raw_text, file_metadata)
    reduction = ((len(raw_text) - len(cleaned_text)) / len(raw_text) * 100)
    logger.info(f"✅ Text cleaned:")
    logger.info(f"   - Original: {len(raw_text):,} chars")
    logger.info(f"   - Cleaned: {len(cleaned_text):,} chars")
    logger.info(f"   - Reduction: {reduction:.1f}%")
    
    # Step 4: Extract sections
    logger.info("\n" + "="*80)
    logger.info("STEP 4: SECTION EXTRACTION")
    logger.info("="*80)
    
    sections = text_processor.extract_sections(cleaned_text)
    logger.info(f"✅ Sections identified:")
    logger.info(f"   - Management Discussion: {len(sections['management_discussion']):,} chars")
    logger.info(f"   - Q&A Session: {len(sections['qa_session']):,} chars")
    
    if sections['qa_session']:
        speaker_segments = text_processor.extract_speaker_segments(sections['qa_session'][:5000])
        logger.info(f"   - Speaker segments: {len(speaker_segments)} found")
        if speaker_segments:
            types = {}
            for seg in speaker_segments:
                types[seg['type']] = types.get(seg['type'], 0) + 1
            logger.info(f"   - Speaker types: {dict(types)}")
    
    # Step 5: Extract entities
    logger.info("\n" + "="*80)
    logger.info("STEP 5: ENTITY EXTRACTION")
    logger.info("="*80)
    
    entities = entity_extractor.extract_all_entities(cleaned_text)
    
    logger.info(f"✅ Entities extracted:")
    logger.info(f"   - Companies: {entities['companies']}")
    logger.info(f"   - Locations: {entities['locations'][:5]}")
    logger.info(f"   - Time periods: {entities['time_periods'][:5]}")
    logger.info(f"   - Key terms: {', '.join(entities['key_terms'][:10])}")
    
    if entities['financial_metrics']:
        logger.info(f"\n   Financial metrics found:")
        for metric, values in entities['financial_metrics'].items():
            logger.info(f"   - {metric}: {len(values)} instances")
            if values:
                logger.info(f"     Example: {values[0]}")
    
    # Step 6: Chunk text
    logger.info("\n" + "="*80)
    logger.info("STEP 6: DOCUMENT CHUNKING")
    logger.info("="*80)
    
    chunks = chunker.chunk_text(cleaned_text, file_metadata)
    logger.info(f"✅ Created {len(chunks)} chunks")
    
    # Analyze chunks
    chunk_types = {}
    chunk_sizes = []
    
    for chunk in chunks:
        chunk_type = chunk.get('chunk_type', 'unknown')
        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        chunk_sizes.append(len(chunk['text']))
    
    avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
    
    logger.info(f"   - Chunk types: {dict(chunk_types)}")
    logger.info(f"   - Average size: {avg_size:.0f} chars")
    logger.info(f"   - Size range: {min(chunk_sizes)} - {max(chunk_sizes)} chars")
    
    # Show sample chunks
    logger.info(f"\n   Sample chunks:")
    for i, chunk in enumerate(chunks[:3], 1):
        logger.info(f"\n   Chunk {i} ({chunk['chunk_type']}):")
        logger.info(f"   {chunk['text'][:200]}...")
    
    # Step 7: Enrich chunk metadata
    logger.info("\n" + "="*80)
    logger.info("STEP 7: METADATA ENRICHMENT")
    logger.info("="*80)
    
    enriched_chunks = []
    for i, chunk in enumerate(chunks):
        enriched = metadata_enhancer.enrich_chunk_metadata(
            chunk, file_metadata, i, len(chunks)
        )
        enriched_chunks.append(enriched)
    
    logger.info(f"✅ Enriched {len(enriched_chunks)} chunks with metadata")
    
    # Show sample enriched chunk
    sample_enriched = enriched_chunks[0]
    logger.info(f"\n   Sample enriched chunk metadata:")
    metadata_keys = ['chunk_index', 'total_chunks', 'position', 'chunk_type']
    for key in metadata_keys:
        if key in sample_enriched:
            logger.info(f"   - {key}: {sample_enriched[key]}")
    
    # Step 8: Create vector payloads
    logger.info("\n" + "="*80)
    logger.info("STEP 8: VECTOR PAYLOAD CREATION")
    logger.info("="*80)
    
    payloads = []
    for chunk in enriched_chunks:
        payload = metadata_enhancer.create_vector_payload(chunk)
        payloads.append(payload)
    
    logger.info(f"✅ Created {len(payloads)} vector payloads")
    
    # Show sample payload
    sample_payload = payloads[0]
    logger.info(f"\n   Sample payload structure:")
    for key in ['company_name', 'quarter', 'fiscal_year', 'chunk_type', 'has_financials']:
        if key in sample_payload:
            logger.info(f"   - {key}: {sample_payload[key]}")
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("PIPELINE SUMMARY")
    logger.info("="*80)
    
    summary = {
        'pdf_file': sample_pdf.name,
        'extraction': {
            'pages': extracted['metadata']['num_pages'],
            'raw_chars': len(raw_text),
            'cleaned_chars': len(cleaned_text),
            'reduction_pct': f"{reduction:.1f}%"
        },
        'metadata': {
            'company': file_metadata.get('company_name'),
            'quarter': file_metadata.get('quarter'),
            'fiscal_year': file_metadata.get('fiscal_year'),
            'has_qa': text_metadata['has_qa']
        },
        'entities': {
            'companies': len(entities['companies']),
            'locations': len(entities['locations']),
            'financial_metrics': len(entities['financial_metrics']),
            'key_terms': len(entities['key_terms'])
        },
        'chunking': {
            'total_chunks': len(chunks),
            'avg_chunk_size': f"{avg_size:.0f}",
            'chunk_types': dict(chunk_types)
        }
    }
    
    logger.info(json.dumps(summary, indent=2))
    
    logger.info("\n" + "="*80)
    logger.info("✅ ALL PIPELINE STEPS COMPLETED SUCCESSFULLY")
    logger.info("="*80)
    
    return {
        'chunks': enriched_chunks,
        'payloads': payloads,
        'summary': summary
    }

if __name__ == "__main__":
    try:
        result = test_full_pipeline()
        if result:
            logger.info("\n✅ Pipeline test passed! Ready for embedding generation.")
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}", exc_info=True)
