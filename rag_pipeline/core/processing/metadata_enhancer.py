"""
Enhanced metadata extraction and enrichment
"""
import re
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MetadataEnhancer:
    """Enhance chunk metadata with additional context"""
    
    def __init__(self):
        self.company_mappings = {
            'acc limited': 'ACC Limited',
            'ambuja': 'Ambuja Cements',
            'ultratech': 'UltraTech Cement',
            'shree cement': 'Shree Cement',
            'dalmia': 'Dalmia Bharat Ltd',
            'birla corporation': 'Birla Corporation',
            'grasim': 'Grasim Industries',
            'india cements': 'India Cements',
            'jk cement': 'J K Cement',
            'jk lakshmi': 'JK Lakshmi Cement',
            'nuvoco': 'Nuvoco Vistas',
            'star cement': 'Star Cement',
            'ramco': 'The Ramco Cements',
        }
        
        self.quarter_months = {
            1: 'Q4', 2: 'Q4', 3: 'Q4',  # Jan-Mar
            4: 'Q1', 5: 'Q1', 6: 'Q1',  # Apr-Jun
            7: 'Q2', 8: 'Q2', 9: 'Q2',  # Jul-Sep
            10: 'Q3', 11: 'Q3', 12: 'Q3' # Oct-Dec
        }
    
    def extract_from_filename(self, filename: str) -> Dict:
        """
        Extract metadata from filename
        
        Example: "ACC Limited_August_2024_Concall.pdf"
        """
        metadata = {
            'filename': filename,
            'company_name': None,
            'month': None,
            'year': None,
            'quarter': None,
            'fiscal_year': None,
        }
        
        # Extract company name (before first underscore)
        parts = filename.replace('.pdf', '').split('_')
        if parts:
            company = parts[0].lower()
            for key, value in self.company_mappings.items():
                if key in company:
                    metadata['company_name'] = value
                    break
            if not metadata['company_name']:
                metadata['company_name'] = parts[0]
        
        # Extract month and year
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        filename_lower = filename.lower()
        for month_name, month_num in months.items():
            if month_name in filename_lower:
                metadata['month'] = month_name.capitalize()
                metadata['quarter'] = self.quarter_months[month_num]
                break
        
        # Extract year
        year_match = re.search(r'(20\d{2})', filename)
        if year_match:
            year = int(year_match.group(1))
            metadata['year'] = year
            
            # Calculate fiscal year (Apr-Mar in India)
            if metadata['month']:
                month_num = months.get(metadata['month'].lower(), 1)
                if month_num >= 4:
                    metadata['fiscal_year'] = f"FY{year}-{str(year+1)[-2:]}"
                else:
                    metadata['fiscal_year'] = f"FY{year-1}-{str(year)[-2:]}"
        
        return metadata
    
    def extract_from_text(self, text: str) -> Dict:
        """
        Extract metadata from document text
        """
        metadata = {
            'has_qa': False,
            'num_questions': 0,
            'speakers': [],
            'topics': [],
        }
        
        # Check for Q&A section
        qa_indicators = ['question and answer', 'q&a', 'analyst:', 'moderator:']
        text_lower = text.lower()
        metadata['has_qa'] = any(indicator in text_lower for indicator in qa_indicators)
        
        # Count questions (rough estimate)
        metadata['num_questions'] = text.count('?')
        
        # Extract speakers
        speaker_pattern = r'^([A-Z][a-zA-Z\s.]+):'
        speakers = set(re.findall(speaker_pattern, text, re.MULTILINE))
        metadata['speakers'] = list(speakers)[:10]  # Limit to 10
        
        # Extract key topics (simple keyword extraction)
        topics = []
        topic_keywords = [
            'expansion', 'capacity', 'demand', 'pricing', 'coal',
            'sustainability', 'green', 'acquisition', 'merger',
            'margins', 'volume', 'realization', 'cost'
        ]
        
        for keyword in topic_keywords:
            if keyword in text_lower:
                topics.append(keyword)
        
        metadata['topics'] = topics
        
        return metadata
    
    def enrich_chunk_metadata(
        self,
        chunk: Dict,
        doc_metadata: Dict,
        chunk_index: int,
        total_chunks: int
    ) -> Dict:
        """
        Enrich chunk with comprehensive metadata
        """
        enriched = {
            **chunk,
            'chunk_index': chunk_index,
            'total_chunks': total_chunks,
            'position': chunk_index / total_chunks if total_chunks > 0 else 0,
            'document_metadata': doc_metadata,
        }
        
        # Add searchable fields
        enriched['searchable_text'] = self._create_searchable_text(chunk, doc_metadata)
        
        # Add timestamp
        enriched['processed_at'] = datetime.now().isoformat()
        
        return enriched
    
    def _create_searchable_text(self, chunk: Dict, doc_metadata: Dict) -> str:
        """
        Create enriched searchable text with metadata keywords
        """
        parts = [chunk.get('text', '')]
        
        # Add company name for better retrieval
        if doc_metadata.get('company_name'):
            parts.append(f"Company: {doc_metadata['company_name']}")
        
        # Add temporal information
        if doc_metadata.get('quarter') and doc_metadata.get('fiscal_year'):
            parts.append(f"Period: {doc_metadata['quarter']} {doc_metadata['fiscal_year']}")
        
        return ' '.join(parts)
    
    def create_vector_payload(self, chunk: Dict, embedding: list = None) -> Dict:
        """
        Create payload for vector database
        """
        payload = {
            'text': chunk.get('text', ''),
            'chunk_id': chunk.get('chunk_id'),
            'chunk_index': chunk.get('chunk_index'),
            'company_name': chunk.get('document_metadata', {}).get('company_name'),
            'quarter': chunk.get('document_metadata', {}).get('quarter'),
            'fiscal_year': chunk.get('document_metadata', {}).get('fiscal_year'),
            'year': chunk.get('document_metadata', {}).get('year'),
            'month': chunk.get('document_metadata', {}).get('month'),
            'chunk_type': chunk.get('chunk_type', 'general'),
            'has_financials': self._has_financial_keywords(chunk.get('text', '')),
            'section': chunk.get('section', 'unknown'),
        }
        
        return payload
    
    def _has_financial_keywords(self, text: str) -> bool:
        """Check if text contains financial keywords"""
        keywords = ['ebitda', 'revenue', 'margin', 'volume', 'capacity', 'crore', 'profit']
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)
