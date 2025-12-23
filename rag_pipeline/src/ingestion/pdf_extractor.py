"""
PDF text extraction module
"""
import pymupdf as fitz  # PyMuPDF (v1.24+)
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
            
            full_text = '\n'.join([block['text'] for block in text_blocks])
            
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
