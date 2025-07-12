"""
Embedding Generation module for converting text to vectors using OpenAI.
Week 4 implementation for Agricultural Advisor Bot.
"""

from openai import OpenAI
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional
from scripts.utils.config_loader import config
from scripts.utils.logger import logger


class EmbeddingGenerator:
    """
    Handles text embedding generation using OpenAI's embedding API.
    Optimized for agricultural document processing.
    """
    
    def __init__(self, 
                 model: str = "text-embedding-ada-002",
                 batch_size: int = 100,
                 max_retries: int = 3):
        """
        Initialize the embedding generator.
        
        Args:
            model: OpenAI embedding model to use
            batch_size: Number of texts to process in each batch
            max_retries: Maximum number of retry attempts
        """
        self.model = model
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.client = None
        self.embedding_cache = {}  # Simple cache for repeated texts
        
        # Initialize OpenAI client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client with API key."""
        try:
            api_key = config.get_required("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key)
            logger.info(f"EmbeddingGenerator initialized with model: {self.model}")
        except ValueError as e:
            logger.error(f"OpenAI API key not found: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            logger.warning("Empty text list provided for embedding generation")
            return []
        
        try:
            # Filter out empty texts
            valid_texts = [text for text in texts if text and text.strip()]
            if not valid_texts:
                logger.warning("No valid texts found for embedding generation")
                return []
            
            # Check cache first
            cached_embeddings = []
            uncached_texts = []
            uncached_indices = []
            
            for i, text in enumerate(valid_texts):
                cache_key = self._generate_cache_key(text)
                if cache_key in self.embedding_cache:
                    cached_embeddings.append((i, self.embedding_cache[cache_key]))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            # Process uncached texts in batches
            all_embeddings = [None] * len(valid_texts)
            
            # Add cached embeddings
            for idx, embedding in cached_embeddings:
                all_embeddings[idx] = embedding
            
            # Generate embeddings for uncached texts
            if uncached_texts:
                new_embeddings = self._generate_embeddings_batch(uncached_texts)
                
                # Cache and store new embeddings
                for i, (text, embedding) in enumerate(zip(uncached_texts, new_embeddings)):
                    cache_key = self._generate_cache_key(text)
                    self.embedding_cache[cache_key] = embedding
                    all_embeddings[uncached_indices[i]] = embedding
            
            logger.info(f"Successfully generated {len(all_embeddings)} embeddings")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def generate_embeddings_for_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for text chunks with metadata.
        
        Args:
            chunks: List of chunk dictionaries with text and metadata
            
        Returns:
            List of chunks with embeddings added
        """
        if not chunks:
            return []
        
        try:
            # Extract texts from chunks
            texts = [chunk['text'] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.generate_embeddings(texts)
            
            # Add embeddings to chunks
            enhanced_chunks = []
            for chunk, embedding in zip(chunks, embeddings):
                enhanced_chunk = chunk.copy()
                enhanced_chunk['embedding'] = embedding
                enhanced_chunk['embedding_model'] = self.model
                enhanced_chunks.append(enhanced_chunk)
            
            return enhanced_chunks
            
        except Exception as e:
            logger.error(f"Error generating embeddings for chunks: {str(e)}")
            raise
    
    def _generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_embeddings = self._call_embedding_api(batch_texts)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    def _call_embedding_api(self, texts: List[str]) -> List[List[float]]:
        """
        Call OpenAI embedding API with retry logic.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.model
                )
                
                # Extract embeddings from response
                embeddings = [item.embedding for item in response.data]
                
                logger.info(f"Successfully generated embeddings for {len(texts)} texts")
                return embeddings
                
            except Exception as e:
                logger.warning(f"Embedding API call attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All embedding API attempts failed: {str(e)}")
                    raise
                
                # Wait before retry
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return []
    
    async def generate_embeddings_async(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings asynchronously.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Run synchronous embedding generation in executor
            embeddings = await asyncio.get_event_loop().run_in_executor(
                None, self.generate_embeddings, texts
            )
            return embeddings
            
        except Exception as e:
            logger.error(f"Error in async embedding generation: {str(e)}")
            raise
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        
        Args:
            query: Search query text
            
        Returns:
            Query embedding vector
        """
        if not query or not query.strip():
            logger.warning("Empty query provided for embedding generation")
            return []
        
        try:
            embeddings = self.generate_embeddings([query])
            return embeddings[0] if embeddings else []
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
    
    def _generate_cache_key(self, text: str) -> str:
        """
        Generate cache key for text.
        
        Args:
            text: Text to generate key for
            
        Returns:
            Cache key string
        """
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for the current model.
        
        Returns:
            Embedding dimension
        """
        # Known dimensions for OpenAI models
        model_dimensions = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072
        }
        
        return model_dimensions.get(self.model, 1536)
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self.embedding_cache.clear()
        logger.info("Embedding cache cleared")
    
    def get_cache_size(self) -> int:
        """Get the current cache size."""
        return len(self.embedding_cache)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self.embedding_cache),
            'model': self.model,
            'batch_size': self.batch_size,
            'max_retries': self.max_retries
        } 