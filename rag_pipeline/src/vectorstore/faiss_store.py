"""
FAISS-based vector store implementation with OpenAI embeddings.
Works without HuggingFace connectivity issues.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import faiss
from openai import OpenAI


class FAISSVectorStore:
    """FAISS-based vector database for semantic search."""
    
    def __init__(self, api_key: Optional[str] = None,
                 model: str = "text-embedding-3-small",
                 persist_dir: str = "./vector_db"):
        """Initialize FAISS store with OpenAI embeddings.
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: OpenAI embedding model
            persist_dir: Directory to store index and metadata
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.model = model
        self.embedding_dim = 1536  # text-embedding-3-small dimension
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        
        # Store metadata
        self.metadata: List[Dict] = []
        self.texts: List[str] = []
        
        print(f"✓ FAISS store initialized with OpenAI embeddings (dim={self.embedding_dim})")
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using OpenAI."""
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings, dtype='float32')
    
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
        
        # Generate embeddings via OpenAI
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self._get_embeddings(texts)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Store metadata and texts
        self.metadata.extend(chunks)
        self.texts.extend(texts)
        
        print(f"✓ Added {len(chunks)} chunks (total: {self.index.ntotal})")
        return len(chunks)
    
    def search(self, query: str, 
               top_k: int = 5,
               filters: Optional[Dict] = None) -> List[Dict]:
        """Search for similar chunks.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Metadata filters (e.g., {'company': 'ACC Limited'})
            
        Returns:
            List of matching chunks with scores
        """
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self._get_embeddings([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, 
                                           min(top_k * 3, self.index.ntotal))
        
        # Collect results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            
            chunk = self.metadata[idx].copy()
            chunk['score'] = float(score)
            
            # Apply filters
            if filters:
                if not self._match_filters(chunk, filters):
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
        """Save index and metadata to disk."""
        # Save FAISS index
        index_path = self.persist_dir / "faiss.index"
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        metadata_path = self.persist_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': self.metadata,
                'texts': self.texts
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved index to {self.persist_dir}")
    
    def load(self) -> bool:
        """Load index and metadata from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        index_path = self.persist_dir / "faiss.index"
        metadata_path = self.persist_dir / "metadata.json"
        
        if not index_path.exists() or not metadata_path.exists():
            return False
        
        # Load FAISS index
        self.index = faiss.read_index(str(index_path))
        
        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.metadata = data['metadata']
            self.texts = data['texts']
        
        print(f"✓ Loaded {self.index.ntotal} vectors from {self.persist_dir}")
        return True
    
    def delete_collection(self) -> None:
        """Reset the index."""
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.metadata = []
        self.texts = []
        
        # Delete persisted files
        index_path = self.persist_dir / "faiss.index"
        metadata_path = self.persist_dir / "metadata.json"
        
        if index_path.exists():
            index_path.unlink()
        if metadata_path.exists():
            metadata_path.unlink()
        
        print("✓ Collection deleted")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        return {
            'total_vectors': self.index.ntotal,
            'embedding_dim': self.embedding_dim,
            'metadata_count': len(self.metadata),
            'persist_dir': str(self.persist_dir)
        }


if __name__ == "__main__":
    # Test the vector store
    store = FAISSVectorStore(persist_dir="./test_vector_db")
    
    # Sample data
    chunks = [
        {
            'text': 'ACC Limited reported revenue of 5000 crores in Q2 FY2025',
            'company': 'ACC Limited',
            'quarter': 'Q2',
            'fiscal_year': 'FY2024-25'
        },
        {
            'text': 'UltraTech Cement announced capacity expansion of 10 million tonnes',
            'company': 'UltraTech Cement',
            'quarter': 'Q2',
            'fiscal_year': 'FY2024-25'
        }
    ]
    
    # Add documents
    store.add_documents(chunks)
    
    # Search
    results = store.search("What was ACC's revenue?", top_k=2)
    print(f"\nSearch results:")
    for result in results:
        print(f"  Score: {result['score']:.3f}")
        print(f"  Company: {result['company']}")
        print(f"  Text: {result['text'][:80]}...")
    
    # Save
    store.save()
    
    # Load
    new_store = FAISSVectorStore(persist_dir="./test_vector_db")
    new_store.load()
    print(f"\nStats: {new_store.get_stats()}")
