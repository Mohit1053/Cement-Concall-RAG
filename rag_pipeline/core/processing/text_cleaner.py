"""
Text preprocessing and cleaning module
"""
import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class TextPreprocessor:
    """Clean and preprocess extracted text"""
    
    def __init__(
        self,
        remove_headers: bool = True,
        remove_urls: bool = True,
        normalize_whitespace: bool = True,
        fix_common_ocr_errors: bool = True
    ):
        self.remove_headers = remove_headers
        self.remove_urls = remove_urls
        self.normalize_whitespace = normalize_whitespace
        self.fix_common_ocr_errors = fix_common_ocr_errors
        
        # Common header/footer patterns in cement concalls
        self.header_patterns = [
            r'Page \d+ of \d+',
            r'^\d+\s*$',  # Page numbers alone
            r'CIN:\s*L\d+[A-Z]+\d+[A-Z]+\d+',  # CIN numbers
            r'www\.[a-zA-Z0-9]+\.com',
            r'Ph?\s*[+\d\s-]+',  # Phone numbers
        ]
        
        # OCR artifacts to clean
        self.ocr_artifacts = {
            '|': '',  # Table separators
            '□': '',
            '▪': '•',
            '●': '•',
            'ﬁ': 'fi',  # Common ligature issues
            'ﬂ': 'fl',
            '–': '-',  # Em dash
            ''': "'",  # Smart quotes
            ''': "'",
            '"': '"',
            '"': '"',
        }
    
    def clean_text(self, text: str, metadata: Dict = None) -> str:
        """
        Clean and preprocess text
        
        Args:
            text: Raw extracted text
            metadata: Optional metadata for context-aware cleaning
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        original_length = len(text)
        
        # Fix OCR errors
        if self.fix_common_ocr_errors:
            text = self._fix_ocr_errors(text)
        
        # Remove URLs
        if self.remove_urls:
            text = self._remove_urls(text)
        
        # Remove headers/footers
        if self.remove_headers:
            text = self._remove_headers_footers(text)
        
        # Normalize whitespace
        if self.normalize_whitespace:
            text = self._normalize_whitespace(text)
        
        # Remove repeated sections
        text = self._remove_duplicates(text)
        
        cleaned_length = len(text)
        reduction = ((original_length - cleaned_length) / original_length * 100) if original_length > 0 else 0
        
        logger.debug(f"Cleaned text: {original_length} -> {cleaned_length} chars ({reduction:.1f}% reduction)")
        
        return text.strip()
    
    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors"""
        for artifact, replacement in self.ocr_artifacts.items():
            text = text.replace(artifact, replacement)
        return text
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        # Remove web URLs
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        return text
    
    def _remove_headers_footers(self, text: str) -> str:
        """Remove common header and footer patterns"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            is_header_footer = False
            
            # Check against patterns
            for pattern in self.header_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_header_footer = True
                    break
            
            # Skip very short lines that are likely page numbers
            if len(line.strip()) < 3 and line.strip().isdigit():
                is_header_footer = True
            
            if not is_header_footer:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace"""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline (paragraph break)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text
    
    def _remove_duplicates(self, text: str) -> str:
        """Remove duplicate consecutive sections"""
        # Split into sentences
        sentences = re.split(r'([.!?]+\s+)', text)
        
        # Remove consecutive duplicates
        cleaned = []
        prev = None
        
        for sentence in sentences:
            if sentence.strip() and sentence != prev:
                cleaned.append(sentence)
            prev = sentence
        
        return ''.join(cleaned)
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract different sections from the transcript
        
        Returns:
            Dictionary with sections: management_discussion, qa_session, etc.
        """
        sections = {
            'full_text': text,
            'management_discussion': '',
            'qa_session': '',
            'financial_highlights': ''
        }
        
        # Common section markers
        qa_markers = [
            'question and answer',
            'q&a session',
            'analyst:',
            'moderator:',
        ]
        
        # Try to identify Q&A section
        text_lower = text.lower()
        
        for marker in qa_markers:
            if marker in text_lower:
                idx = text_lower.index(marker)
                sections['management_discussion'] = text[:idx]
                sections['qa_session'] = text[idx:]
                logger.debug(f"Identified Q&A section starting at position {idx}")
                break
        
        # If no Q&A section found, all is management discussion
        if not sections['qa_session']:
            sections['management_discussion'] = text
        
        return sections
    
    def extract_speaker_segments(self, text: str) -> List[Dict]:
        """
        Extract individual speaker segments from Q&A
        
        Returns:
            List of dicts with speaker and their text
        """
        segments = []
        
        # Pattern to match speaker labels
        speaker_pattern = r'^([A-Z][a-zA-Z\s.]+):\s*(.+?)(?=^[A-Z][a-zA-Z\s.]+:|$)'
        
        matches = re.finditer(speaker_pattern, text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            speaker = match.group(1).strip()
            content = match.group(2).strip()
            
            segments.append({
                'speaker': speaker,
                'text': content,
                'type': self._identify_speaker_type(speaker)
            })
        
        logger.debug(f"Extracted {len(segments)} speaker segments")
        return segments
    
    def _identify_speaker_type(self, speaker: str) -> str:
        """Identify if speaker is moderator, analyst, or management"""
        speaker_lower = speaker.lower()
        
        if 'moderator' in speaker_lower or 'coordinator' in speaker_lower:
            return 'moderator'
        elif any(title in speaker_lower for title in ['analyst', 'mr.', 'ms.']):
            return 'analyst'
        else:
            return 'management'
    
    def extract_financial_data(self, text: str) -> Dict[str, List[str]]:
        """
        Extract financial metrics and numbers from text
        
        Returns:
            Dictionary of metric types and their values
        """
        financial_data = {
            'revenue': [],
            'ebitda': [],
            'margins': [],
            'volumes': [],
            'capacity': [],
            'utilization': []
        }
        
        # Patterns for financial metrics
        patterns = {
            'revenue': r'revenue\s+(?:of\s+)?(?:Rs\.?\s*)?(\d+[,\d]*\.?\d*)\s*(?:crore|cr|million|bn)',
            'ebitda': r'ebitda\s+(?:of\s+)?(?:Rs\.?\s*)?(\d+[,\d]*\.?\d*)\s*(?:crore|cr|million)',
            'margins': r'margin\s+(?:of\s+)?(\d+\.?\d*)\s*(?:%|percent)',
            'volumes': r'volume\s+(?:of\s+)?(\d+[,\d]*\.?\d*)\s*(?:million tonnes|mt|tonnes)',
            'capacity': r'capacity\s+(?:of\s+)?(\d+[,\d]*\.?\d*)\s*(?:million tonnes|mtpa|mt)',
            'utilization': r'(?:capacity\s+)?utilization\s+(?:of\s+)?(\d+\.?\d*)\s*(?:%|percent)',
        }
        
        for metric, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            financial_data[metric] = [m.replace(',', '') for m in matches]
        
        return financial_data
