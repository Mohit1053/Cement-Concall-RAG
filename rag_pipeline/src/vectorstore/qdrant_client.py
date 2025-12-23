"""
Qdrant vector database client
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class QdrantVectorStore:
    """Interface to Qdrant vector database"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "cement_transcripts"
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)
    
    def create_collection(self, vector_size: int):
        """Create a new collection"""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
    
    def add_documents(self, documents: List[Dict], embeddings: List):
        """Add documents with embeddings to collection"""
        points = []
        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            point = PointStruct(
                id=idx,
                vector=embedding.tolist(),
                payload=doc
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Added {len(points)} documents to collection")
    
    def search(
        self, 
        query_vector: List[float], 
        limit: int = 5,
        filter_dict: Dict = None
    ):
        """Search for similar documents"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=filter_dict
        )
        return results
