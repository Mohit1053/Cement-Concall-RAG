"""
ChromaDB vector store implementation (simpler alternative to Qdrant)
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ChromaVectorStore:
    """ChromaDB vector database client"""
    
    def __init__(
        self,
        persist_directory: str = "data/chromadb",
        collection_name: str = "cement_transcripts"
    ):
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client"""
        try:
            # Create persist directory if it doesn't exist
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory)
            )
            
            logger.info(f"ChromaDB initialized at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def create_collection(self, embedding_function=None):
        """Create or get collection"""
        try:
            # Try to get existing collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Cement company conference call transcripts"},
                embedding_function=embedding_function
            )
            
            logger.info(f"Collection '{self.collection_name}' ready")
            logger.info(f"Current count: {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict],
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None
    ):
        """
        Add documents to collection
        
        Args:
            documents: List of text documents
            metadatas: List of metadata dicts
            ids: List of unique IDs
            embeddings: Optional pre-computed embeddings
        """
        try:
            if embeddings:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                    embeddings=embeddings
                )
            else:
                # ChromaDB will compute embeddings automatically
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            
            logger.info(f"Added {len(documents)} documents to collection")
            logger.info(f"Total documents: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(
        self,
        query_text: str = None,
        query_embedding: List[float] = None,
        n_results: int = 5,
        where: Dict = None,
        where_document: Dict = None
    ) -> Dict:
        """
        Search for similar documents
        
        Args:
            query_text: Text query (ChromaDB will embed it)
            query_embedding: Pre-computed query embedding
            n_results: Number of results to return
            where: Metadata filters
            where_document: Document content filters
            
        Returns:
            Search results with documents, metadatas, distances
        """
        try:
            if query_embedding:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where,
                    where_document=where_document
                )
            elif query_text:
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where=where,
                    where_document=where_document
                )
            else:
                raise ValueError("Must provide either query_text or query_embedding")
            
            logger.debug(f"Search returned {len(results['documents'][0])} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        if not self.collection:
            return {}
        
        return {
            'name': self.collection_name,
            'count': self.collection.count(),
            'persist_directory': str(self.persist_directory)
        }
    
    def delete_collection(self):
        """Delete the collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
    
    def reset_collection(self):
        """Reset collection (delete and recreate)"""
        try:
            self.delete_collection()
            self.create_collection()
            logger.info(f"Reset collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
