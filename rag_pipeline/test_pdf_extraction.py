"""
Test script for PDF extraction
Tests if PDFs are readable and text can be extracted properly
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ingestion.pdf_extractor import PDFExtractor
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_single_pdf(pdf_path: Path):
    """Test extraction on a single PDF"""
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing: {pdf_path.name}")
    logger.info(f"{'='*80}")
    
    extractor = PDFExtractor(extract_tables=True)
    result = extractor.extract_from_file(pdf_path)
    
    if result:
        logger.info(f"✅ Extraction successful!")
        logger.info(f"   - Pages: {result['metadata']['num_pages']}")
        logger.info(f"   - File size: {result['metadata']['file_size']:,} bytes")
        logger.info(f"   - Text length: {len(result['text']):,} characters")
        logger.info(f"   - Text blocks: {len(result['text_blocks'])}")
        
        # Show first 500 characters
        logger.info(f"\n--- First 500 characters ---")
        logger.info(result['text'][:500])
        logger.info(f"...\n")
        
        # Check for common keywords in cement concalls
        keywords = ['EBITDA', 'revenue', 'cement', 'capacity', 'quarter', 'volume', 'margin']
        found_keywords = [kw for kw in keywords if kw.lower() in result['text'].lower()]
        logger.info(f"✓ Found keywords: {', '.join(found_keywords)}")
        
        return True
    else:
        logger.error(f"❌ Extraction failed for {pdf_path.name}")
        return False

def test_multiple_companies():
    """Test extraction across different companies"""
    # Path to transcripts
    base_path = Path("..") / "Cement_Concall_Transcripts"
    
    if not base_path.exists():
        logger.error(f"Transcripts directory not found: {base_path.absolute()}")
        return
    
    # Get one PDF from each company
    company_dirs = [d for d in base_path.iterdir() if d.is_dir()]
    logger.info(f"Found {len(company_dirs)} company directories")
    
    test_results = {}
    total_tested = 0
    successful = 0
    
    for company_dir in company_dirs[:5]:  # Test first 5 companies
        pdf_files = list(company_dir.glob("*.pdf"))
        if pdf_files:
            pdf_file = pdf_files[0]  # Test first PDF from each company
            total_tested += 1
            
            success = test_single_pdf(pdf_file)
            test_results[company_dir.name] = success
            
            if success:
                successful += 1
    
    # Summary
    logger.info(f"\n{'='*80}")
    logger.info(f"EXTRACTION TEST SUMMARY")
    logger.info(f"{'='*80}")
    logger.info(f"Total PDFs tested: {total_tested}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {total_tested - successful}")
    logger.info(f"Success rate: {(successful/total_tested)*100:.1f}%")
    
    logger.info(f"\nResults by company:")
    for company, success in test_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"  {status} - {company}")

def test_text_quality():
    """Test the quality of extracted text"""
    base_path = Path("..") / "Cement_Concall_Transcripts"
    
    # Get a sample PDF
    pdf_files = list(base_path.rglob("*.pdf"))
    if not pdf_files:
        logger.error("No PDF files found")
        return
    
    sample_pdf = pdf_files[0]
    logger.info(f"\n{'='*80}")
    logger.info(f"TEXT QUALITY TEST")
    logger.info(f"{'='*80}")
    logger.info(f"Sample file: {sample_pdf.name}")
    
    extractor = PDFExtractor()
    result = extractor.extract_from_file(sample_pdf)
    
    if result:
        text = result['text']
        
        # Check various quality metrics
        checks = {
            'Has content': len(text) > 100,
            'Not all uppercase': not text.isupper(),
            'Has punctuation': any(p in text for p in '.,;:!?'),
            'Has numbers': any(c.isdigit() for c in text),
            'Has newlines': '\n' in text,
            'Reasonable char density': 100 < len(text) < 500000
        }
        
        logger.info("\nQuality checks:")
        for check_name, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"  {status} - {check_name}")
        
        # Word count and statistics
        words = text.split()
        logger.info(f"\nText statistics:")
        logger.info(f"  - Total words: {len(words):,}")
        logger.info(f"  - Unique words: {len(set(words)):,}")
        logger.info(f"  - Average word length: {sum(len(w) for w in words) / len(words):.1f}")
        
        # Check for OCR artifacts
        artifacts = ['|', '□', '▪', '●']
        found_artifacts = [a for a in artifacts if a in text]
        if found_artifacts:
            logger.warning(f"  ⚠️  Potential OCR artifacts found: {found_artifacts}")
        else:
            logger.info(f"  ✅ No obvious OCR artifacts detected")

def main():
    """Run all PDF extraction tests"""
    logger.info("Starting PDF Extraction Tests")
    logger.info("=" * 80)
    
    try:
        # Test 1: Multiple companies
        test_multiple_companies()
        
        # Test 2: Text quality
        test_text_quality()
        
        logger.info("\n" + "=" * 80)
        logger.info("All tests completed!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)

if __name__ == "__main__":
    main()
