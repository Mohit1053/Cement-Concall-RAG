"""
Text embedding module
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Embedder:
    """Generate embeddings for text"""
    
    def __init__(
        self, 
        model_name: str = "BAAI/bge-large-en-v1.5",
        device: str = "cpu"
    ):
        self.model_name = model_name
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load embedding model"""
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text
        
        Args:
            text: Single text or list of texts
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(text, str):
            text = [text]
        
        embeddings = self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        
        return embeddings
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed texts in batches"""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return embeddings
