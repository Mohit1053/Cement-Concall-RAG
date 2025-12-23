"""
Document chunking module with semantic awareness
"""
from typing import List, Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)

class DocumentChunker:
    """Chunk documents into smaller pieces with semantic boundaries"""
    
    def __init__(
        self, 
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        min_chunk_size: int = 200,
        respect_qa_pairs: bool = True,
        respect_paragraphs: bool = True
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.respect_qa_pairs = respect_qa_pairs
        self.respect_paragraphs = respect_paragraphs
        
        # Q&A pattern
        self.qa_pattern = re.compile(
            r'([A-Z][a-zA-Z\s.]+):\s*(.+?)(?=\n[A-Z][a-zA-Z\s.]+:|$)',
            re.DOTALL
        )
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with semantic awareness
        
        Args:
            text: Full text to chunk
            metadata: Document metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries
        """
        # Try to identify Q&A sections
        if self.respect_qa_pairs and self._has_qa_section(text):
            chunks = self._chunk_with_qa_awareness(text, metadata)
        else:
            chunks = self._chunk_by_sentences(text, metadata)
        
        # Enrich chunks with additional info
        for i, chunk in enumerate(chunks):
            chunk['chunk_id'] = i
            chunk['chunk_type'] = self._identify_chunk_type(chunk['text'])
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def _chunk_by_sentences(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Standard sentence-based chunking"""
        chunks = []
        
        # Try paragraph-based splitting first
        if self.respect_paragraphs:
            paragraphs = text.split('\n\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
        else:
            paragraphs = [text]
        
        for paragraph in paragraphs:
            sentences = self._split_into_sentences(paragraph)
            
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
                        })
                    
                    # Start new chunk with overlap
                    overlap_sentences = self._get_overlap(current_chunk)
                    current_chunk = overlap_sentences
                    current_size = sum(len(s) for s in current_chunk)
                
                current_chunk.append(sentence)
                current_size += sentence_length
            
            # Add remaining chunk
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text) >= self.min_chunk_size:
                    chunks.append({
                        'text': chunk_text,
                        'metadata': metadata or {},
                    })
        
        return chunks
    
    def _chunk_with_qa_awareness(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Chunk Q&A sections keeping question-answer pairs together"""
        chunks = []
        
        # Find Q&A matches
        matches = list(self.qa_pattern.finditer(text))
        
        if not matches:
            return self._chunk_by_sentences(text, metadata)
        
        current_chunk = []
        current_size = 0
        
        for match in matches:
            speaker = match.group(1)
            content = match.group(2).strip()
            qa_text = f"{speaker}: {content}"
            qa_length = len(qa_text)
            
            # If this Q&A is too big, chunk it separately
            if qa_length > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append({
                        'text': '\n'.join(current_chunk),
                        'metadata': metadata or {},
                        'section': 'qa'
                    })
                    current_chunk = []
                    current_size = 0
                
                # Chunk the large Q&A
                qa_chunks = self._chunk_by_sentences(qa_text, metadata)
                chunks.extend(qa_chunks)
                continue
            
            # Check if adding this Q&A exceeds chunk size
            if current_size + qa_length > self.chunk_size and current_chunk:
                chunks.append({
                    'text': '\n'.join(current_chunk),
                    'metadata': metadata or {},
                    'section': 'qa'
                })
                current_chunk = []
                current_size = 0
            
            current_chunk.append(qa_text)
            current_size += qa_length
        
        # Add remaining chunk
        if current_chunk:
            chunks.append({
                'text': '\n'.join(current_chunk),
                'metadata': metadata or {},
                'section': 'qa'
            })
        
        return chunks
    
    def _has_qa_section(self, text: str) -> bool:
        """Check if text contains Q&A section"""
        qa_indicators = ['moderator:', 'analyst:', 'question:', 'q&a']
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in qa_indicators)
    
    def _identify_chunk_type(self, text: str) -> str:
        """Identify the type of chunk"""
        text_lower = text.lower()
        
        # Check for financial data
        if any(kw in text_lower for kw in ['ebitda', 'revenue', 'crore', 'margin', 'profit']):
            if any(kw in text_lower for kw in ['analyst:', 'moderator:']):
                return 'qa_financial'
            return 'financial_data'
        
        # Check for Q&A
        if any(kw in text_lower for kw in ['analyst:', 'moderator:', 'question:']):
            return 'qa_pair'
        
        # Check for strategic discussion
        if any(kw in text_lower for kw in ['expansion', 'acquisition', 'strategy', 'plan']):
            return 'strategic'
        
        return 'general'
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be improved with spaCy)
        sentences = re.split(r'(?<=[.!?])\s+', text)
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
