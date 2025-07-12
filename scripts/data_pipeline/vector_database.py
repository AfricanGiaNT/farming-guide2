"""
Vector Database module using FAISS for efficient similarity search.
Week 4 implementation for Agricultural Advisor Bot.
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
from scripts.utils.logger import logger


class VectorDatabase:
    """
    FAISS-based vector database for storing and searching document embeddings.
    Optimized for agricultural document retrieval.
    """
    
    def __init__(self, 
                 dimension: int = 1536,
                 index_type: str = "flat",
                 storage_path: str = "data/vector_db"):
        """
        Initialize the vector database.
        
        Args:
            dimension: Embedding vector dimension
            index_type: FAISS index type ('flat', 'ivf', 'hnsw')
            storage_path: Path to store index and metadata
        """
        self.dimension = dimension
        self.index_type = index_type
        self.storage_path = storage_path
        self.index = None
        self.metadata = []  # Store chunk metadata
        self.id_to_chunk = {}  # Map vector IDs to chunk data
        
        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize FAISS index
        self._initialize_index()
        
        logger.info(f"VectorDatabase initialized with dimension={dimension}, type={index_type}")
    
    def _initialize_index(self):
        """Initialize FAISS index based on type."""
        try:
            if self.index_type == "flat":
                # Simple flat index (exact search)
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
                
            elif self.index_type == "ivf":
                # IVF index (approximate search, faster for large datasets)
                nlist = 100  # Number of clusters
                quantizer = faiss.IndexFlatIP(self.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
                
            elif self.index_type == "hnsw":
                # HNSW index (hierarchical navigable small world)
                m = 16  # Number of connections
                self.index = faiss.IndexHNSWFlat(self.dimension, m)
                
            else:
                raise ValueError(f"Unsupported index type: {self.index_type}")
                
            logger.info(f"FAISS index initialized: {self.index_type}")
            
        except Exception as e:
            logger.error(f"Error initializing FAISS index: {str(e)}")
            raise
    
    def add_vectors(self, embeddings: List[List[float]], chunks: List[Dict[str, Any]]) -> bool:
        """
        Add vectors and associated metadata to the database.
        
        Args:
            embeddings: List of embedding vectors
            chunks: List of chunk dictionaries with metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not embeddings or not chunks:
            logger.warning("Empty embeddings or chunks provided")
            return False
        
        if len(embeddings) != len(chunks):
            logger.error("Embeddings and chunks length mismatch")
            return False
        
        try:
            # Convert embeddings to numpy array
            embedding_matrix = np.array(embeddings, dtype=np.float32)
            
            # Normalize for cosine similarity (if using Inner Product index)
            if self.index_type == "flat":
                faiss.normalize_L2(embedding_matrix)
            
            # Train index if necessary (for IVF)
            if self.index_type == "ivf" and not self.index.is_trained:
                logger.info("Training IVF index...")
                self.index.train(embedding_matrix)
            
            # Add vectors to index
            start_id = self.index.ntotal
            self.index.add(embedding_matrix)
            
            # Store metadata
            for i, chunk in enumerate(chunks):
                vector_id = start_id + i
                self.metadata.append(chunk)
                self.id_to_chunk[vector_id] = chunk
            
            logger.info(f"Successfully added {len(embeddings)} vectors to database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding vectors to database: {str(e)}")
            return False
    
    def search(self, 
               query_embedding: List[float], 
               top_k: int = 5,
               threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the database.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of search results with metadata and scores
        """
        if not query_embedding:
            logger.warning("Empty query embedding provided")
            return []
        
        if self.index.ntotal == 0:
            logger.warning("No vectors in database")
            return []
        
        try:
            # Convert query to numpy array
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Normalize for cosine similarity
            if self.index_type == "flat":
                faiss.normalize_L2(query_vector)
            
            # Search
            scores, indices = self.index.search(query_vector, top_k)
            
            # Process results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # No more results
                    break
                    
                if score < threshold:  # Below threshold
                    continue
                
                # Get chunk data
                chunk_data = self.id_to_chunk.get(idx, {})
                
                result = {
                    'chunk_id': idx,
                    'score': float(score),
                    'text': chunk_data.get('text', ''),
                    'metadata': chunk_data.get('metadata', {}),
                    'source_document': chunk_data.get('metadata', {}).get('source_document', ''),
                    'token_count': chunk_data.get('token_count', 0),
                    'rank': i + 1
                }
                
                results.append(result)
            
            logger.info(f"Search returned {len(results)} results above threshold {threshold}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching database: {str(e)}")
            return []
    
    def batch_search(self, 
                    query_embeddings: List[List[float]], 
                    top_k: int = 5,
                    threshold: float = 0.7) -> List[List[Dict[str, Any]]]:
        """
        Search for multiple queries at once.
        
        Args:
            query_embeddings: List of query embedding vectors
            top_k: Number of top results per query
            threshold: Minimum similarity threshold
            
        Returns:
            List of search results for each query
        """
        results = []
        for query_embedding in query_embeddings:
            query_results = self.search(query_embedding, top_k, threshold)
            results.append(query_results)
        
        return results
    
    def save_index(self, filename: Optional[str] = None) -> bool:
        """
        Save the FAISS index and metadata to disk.
        
        Args:
            filename: Optional filename, defaults to index type
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if filename is None:
                filename = f"faiss_index_{self.index_type}"
            
            index_path = os.path.join(self.storage_path, f"{filename}.index")
            metadata_path = os.path.join(self.storage_path, f"{filename}.metadata")
            
            # Save FAISS index
            faiss.write_index(self.index, index_path)
            
            # Save metadata
            with open(metadata_path, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata,
                    'id_to_chunk': self.id_to_chunk,
                    'dimension': self.dimension,
                    'index_type': self.index_type
                }, f)
            
            logger.info(f"Index saved to {index_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            return False
    
    def load_index(self, filename: Optional[str] = None) -> bool:
        """
        Load the FAISS index and metadata from disk.
        
        Args:
            filename: Optional filename, defaults to index type
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if filename is None:
                filename = f"faiss_index_{self.index_type}"
            
            index_path = os.path.join(self.storage_path, f"{filename}.index")
            metadata_path = os.path.join(self.storage_path, f"{filename}.metadata")
            
            if not os.path.exists(index_path) or not os.path.exists(metadata_path):
                logger.warning(f"Index files not found: {filename}")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load metadata
            with open(metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.metadata = data['metadata']
                self.id_to_chunk = data['id_to_chunk']
                self.dimension = data['dimension']
                self.index_type = data['index_type']
            
            logger.info(f"Index loaded from {index_path}, {len(self.metadata)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the database.
        
        Returns:
            Dictionary with database statistics
        """
        stats = {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'storage_path': self.storage_path,
            'metadata_count': len(self.metadata),
            'is_trained': self.index.is_trained if hasattr(self.index, 'is_trained') else True
        }
        
        # Add document statistics
        if self.metadata:
            documents = set()
            for chunk in self.metadata:
                doc_name = chunk.get('metadata', {}).get('source_document', '')
                if doc_name:
                    documents.add(doc_name)
            stats['unique_documents'] = len(documents)
        
        return stats
    
    def clear_database(self):
        """Clear all vectors and metadata from the database."""
        try:
            self._initialize_index()
            self.metadata = []
            self.id_to_chunk = {}
            logger.info("Database cleared")
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
    
    def remove_vectors_by_document(self, document_name: str) -> bool:
        """
        Remove all vectors for a specific document.
        Note: This is a limitation of FAISS - we need to rebuild the index.
        
        Args:
            document_name: Name of document to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find chunks that don't belong to the document
            keep_chunks = []
            keep_embeddings = []
            
            for chunk in self.metadata:
                if chunk.get('metadata', {}).get('source_document', '') != document_name:
                    keep_chunks.append(chunk)
                    # Note: This is inefficient - we'd need to store embeddings separately
                    # For now, this is a placeholder for the functionality
            
            # For a full implementation, we'd need to:
            # 1. Store embeddings separately or rebuild from text
            # 2. Create new index with remaining vectors
            # 3. Update metadata
            
            logger.warning(f"Remove by document not fully implemented for {document_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error removing document vectors: {str(e)}")
            return False 