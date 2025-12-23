"""
Document retrieval module
"""
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class Retriever:
    """Retrieve relevant documents"""
    
    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Dict = None
    ) -> List[Dict]:
        """
        Retrieve relevant documents for query
        
        Args:
            query: User query
            top_k: Number of results to return
            filters: Metadata filters
            
        Returns:
            List of retrieved documents
        """
        # Embed query
        query_embedding = self.embedder.embed_text(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_vector=query_embedding[0].tolist(),
            limit=top_k,
            filter_dict=filters
        )
        
        documents = []
        for result in results:
            documents.append({
                'text': result.payload.get('text'),
                'metadata': result.payload.get('metadata'),
                'score': result.score
            })
        
        logger.info(f"Retrieved {len(documents)} documents for query")
        return documents
