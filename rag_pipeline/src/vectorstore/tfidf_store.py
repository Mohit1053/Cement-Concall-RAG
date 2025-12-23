"""
TF-IDF based vector store - fully offline, no API required.
Simple but effective for semantic search on domain-specific documents.
"""
import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFVectorStore:
    """TF-IDF based vector database for semantic search."""
    
    def __init__(self, persist_dir: str = "./vector_db"):
        """Initialize TF-IDF store.
        
        Args:
            persist_dir: Directory to store index and metadata
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize TF-IDF vectorizer with domain-specific settings
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),  # unigrams, bigrams, trigrams
            min_df=2,  # minimum document frequency
            max_df=0.8,  # ignore terms in >80% of docs
            stop_words='english',
            sublinear_tf=True,  # use log scaling for term frequency
            norm='l2'  # L2 normalization
        )
        
        self.tfidf_matrix = None
        self.metadata: List[Dict] = []
        self.texts: List[str] = []
        self.is_fitted = False
        
        print(f"✓ TF-IDF store initialized (offline mode)")
    
    def add_documents(self, chunks: List[Dict]) -> int:
        """Add document chunks to the vector store.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and metadata
            
        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        print(f"Building TF-IDF vectors for {len(texts)} chunks...")
        
        # If first batch, fit the vectorizer
        if not self.is_fitted:
            self.tfidf_matrix = self.vectorizer.fit_transform(texts).toarray()
            self.is_fitted = True
        else:
            # Transform new texts and append
            new_vectors = self.vectorizer.transform(texts).toarray()
            if self.tfidf_matrix is not None:
                self.tfidf_matrix = np.vstack([self.tfidf_matrix, new_vectors])
        
        # Store metadata and texts
        self.metadata.extend(chunks)
        self.texts.extend(texts)
        
        print(f"✓ Added {len(chunks)} chunks (total: {len(self.texts)})")
        return len(chunks)
    
    def search(self, query: str, 
               top_k: int = 5,
               filters: Optional[Dict] = None) -> List[Dict]:
        """Search for similar chunks.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Metadata filters (e.g., {'company_name': 'ACC Limited'})
            
        Returns:
            List of matching chunks with scores
        """
        if not self.is_fitted or len(self.texts) == 0:
            return []
        
        # Transform query to TF-IDF vector
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        # Get top indices
        top_indices = np.argsort(similarities)[::-1]
        
        # Collect results with filtering
        results = []
        for idx in top_indices:
            chunk = self.metadata[idx].copy()
            chunk['score'] = float(similarities[idx])
            
            # Apply filters
            if filters:
                if not self._match_filters(chunk, filters):
                    continue
            
            # Skip very low scores
            if chunk['score'] < 0.01:
                continue
            
            results.append(chunk)
            
            if len(results) >= top_k:
                break
        
        return results
    
    def _match_filters(self, chunk: Dict, filters: Dict) -> bool:
        """Check if chunk matches all filters."""
        for key, value in filters.items():
            if key not in chunk:
                return False
            if isinstance(value, list):
                if chunk[key] not in value:
                    return False
            elif chunk[key] != value:
                return False
        return True
    
    def save(self) -> None:
        """Save vectorizer, matrix, and metadata to disk."""
        # Save vectorizer
        vectorizer_path = self.persist_dir / "vectorizer.pkl"
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        # Save TF-IDF matrix
        matrix_path = self.persist_dir / "tfidf_matrix.npy"
        if self.tfidf_matrix is not None:
            np.save(matrix_path, self.tfidf_matrix)
        
        # Save metadata
        metadata_path = self.persist_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': self.metadata,
                'texts': self.texts,
                'is_fitted': self.is_fitted
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved index to {self.persist_dir}")
    
    def load(self) -> bool:
        """Load vectorizer, matrix, and metadata from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        vectorizer_path = self.persist_dir / "vectorizer.pkl"
        matrix_path = self.persist_dir / "tfidf_matrix.npy"
        metadata_path = self.persist_dir / "metadata.json"
        
        if not all(p.exists() for p in [vectorizer_path, metadata_path]):
            return False
        
        # Load vectorizer
        with open(vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
        
        # Load matrix
        if matrix_path.exists():
            self.tfidf_matrix = np.load(matrix_path)
        
        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.metadata = data['metadata']
            self.texts = data['texts']
            self.is_fitted = data.get('is_fitted', False)
        
        print(f"✓ Loaded {len(self.texts)} vectors from {self.persist_dir}")
        return True
    
    def delete_collection(self) -> None:
        """Reset the index."""
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.8,
            stop_words='english',
            sublinear_tf=True,
            norm='l2'
        )
        self.tfidf_matrix = None
        self.metadata = []
        self.texts = []
        self.is_fitted = False
        
        # Delete persisted files
        for fname in ['vectorizer.pkl', 'tfidf_matrix.npy', 'metadata.json']:
            path = self.persist_dir / fname
            if path.exists():
                path.unlink()
        
        print("✓ Collection deleted")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        vocab_size = len(self.vectorizer.vocabulary_) if self.is_fitted else 0
        return {
            'total_vectors': len(self.texts),
            'vocabulary_size': vocab_size,
            'metadata_count': len(self.metadata),
            'is_fitted': self.is_fitted,
            'persist_dir': str(self.persist_dir)
        }


if __name__ == "__main__":
    # Test the vector store
    store = TFIDFVectorStore(persist_dir="./test_tfidf_db")
    
    # Sample data
    chunks = [
        {
            'text': 'ACC Limited reported revenue of 5000 crores with strong EBITDA margins in Q2 FY2025. The cement demand remained robust.',
            'company_name': 'ACC Limited',
            'quarter': 'Q2',
            'fiscal_year': 'FY2024-25'
        },
        {
            'text': 'UltraTech Cement announced capacity expansion of 10 million tonnes. Capital expenditure increased significantly.',
            'company_name': 'UltraTech Cement',
            'quarter': 'Q2',
            'fiscal_year': 'FY2024-25'
        },
        {
            'text': 'ACC Limited Q2 results show improved operational efficiency with lower fuel costs and better pricing power.',
            'company_name': 'ACC Limited',
            'quarter': 'Q2',
            'fiscal_year': 'FY2024-25'
        }
    ]
    
    # Add documents
    store.add_documents(chunks)
    
    # Search
    print("\n" + "="*60)
    results = store.search("What was ACC's revenue and margins?", top_k=2)
    print(f"Search results for 'What was ACC's revenue and margins?':")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   Company: {result['company_name']}")
        print(f"   Text: {result['text'][:100]}...")
    
    # Filter search
    print("\n" + "="*60)
    results = store.search("capacity expansion", top_k=2, 
                          filters={'company_name': 'UltraTech Cement'})
    print(f"Filtered search results for UltraTech:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   Text: {result['text'][:100]}...")
    
    # Save
    store.save()
    
    # Load
    new_store = TFIDFVectorStore(persist_dir="./test_tfidf_db")
    new_store.load()
    print(f"\n✓ Stats: {new_store.get_stats()}")
