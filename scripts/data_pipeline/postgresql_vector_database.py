"""
PostgreSQL Vector Database implementation using pgvector extension.
Modern alternative to FAISS for the Agricultural Advisor Bot.
"""

import psycopg2
import psycopg2.extras
from psycopg2.extensions import register_adapter, AsIs
import numpy as np
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from scripts.utils.config_loader import config
from scripts.utils.logger import logger


class PostgreSQLVectorDatabase:
    """
    PostgreSQL-based vector database using pgvector extension.
    Drop-in replacement for FAISS with enhanced capabilities.
    """
    
    def __init__(self, 
                 dimension: int = 1536,
                 table_name: str = "document_embeddings",
                 connection_params: Optional[Dict[str, str]] = None):
        """
        Initialize PostgreSQL vector database.
        
        Args:
            dimension: Embedding vector dimension
            table_name: Name of the table to store embeddings
            connection_params: Database connection parameters
        """
        self.dimension = dimension
        self.table_name = table_name
        self.connection_params = connection_params or self._get_default_connection_params()
        self.connection = None
        
        # Register numpy array adapter for PostgreSQL
        register_adapter(np.ndarray, self._adapt_numpy_array)
        
        # Initialize database connection and schema
        self._initialize_database()
        
        logger.info(f"PostgreSQL VectorDatabase initialized with dimension={dimension}")
    
    def _get_default_connection_params(self) -> Dict[str, str]:
        """Get default connection parameters from config."""
        database_url = config.get("DATABASE_URL")
        if database_url:
            # Parse DATABASE_URL (postgresql://user:password@host:port/database)
            import urllib.parse
            parsed = urllib.parse.urlparse(database_url)
            return {
                'host': parsed.hostname or 'localhost',
                'port': parsed.port or 5432,
                'database': parsed.path[1:] if parsed.path else 'farming_guide',
                'user': parsed.username or 'postgres',
                'password': parsed.password or ''
            }
        else:
            return {
                'host': config.get('DB_HOST', 'localhost'),
                'port': int(config.get('DB_PORT', '5432')),
                'database': config.get('DB_NAME', 'farming_guide'),
                'user': config.get('DB_USER', 'postgres'),
                'password': config.get('DB_PASSWORD', '')
            }
    
    def _adapt_numpy_array(self, numpy_array):
        """Adapt numpy array to PostgreSQL array format."""
        return AsIs(f"'{numpy_array.tolist()}'")
    
    def _initialize_database(self):
        """Initialize database connection and create schema."""
        try:
            # Connect to database
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.autocommit = True
            
            # Create pgvector extension if not exists
            self._create_extension()
            
            # Create table schema
            self._create_table_schema()
            
            # Create indexes
            self._create_indexes()
            
            logger.info("PostgreSQL database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL database: {e}")
            raise
    
    def _create_extension(self):
        """Create pgvector extension."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            logger.info("pgvector extension created/verified")
        except Exception as e:
            logger.error(f"Failed to create pgvector extension: {e}")
            raise
    
    def _create_table_schema(self):
        """Create table schema for document embeddings."""
        try:
            with self.connection.cursor() as cursor:
                # Create main embeddings table
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id SERIAL PRIMARY KEY,
                        embedding vector({self.dimension}),
                        text_content TEXT NOT NULL,
                        metadata JSONB,
                        source_document TEXT,
                        document_type TEXT DEFAULT 'agricultural_guide',
                        token_count INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create metadata table for additional document info
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS document_metadata (
                        id SERIAL PRIMARY KEY,
                        document_name TEXT UNIQUE NOT NULL,
                        file_path TEXT,
                        document_type TEXT,
                        total_chunks INTEGER,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB
                    );
                """)
                
                logger.info(f"Table schema created for {self.table_name}")
                
        except Exception as e:
            logger.error(f"Failed to create table schema: {e}")
            raise
    
    def _create_indexes(self):
        """Create indexes for efficient querying."""
        try:
            with self.connection.cursor() as cursor:
                # Vector similarity index (HNSW for fast approximate search)
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {self.table_name}_embedding_idx 
                    ON {self.table_name} USING hnsw (embedding vector_cosine_ops);
                """)
                
                # Metadata indexes
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {self.table_name}_source_doc_idx 
                    ON {self.table_name} (source_document);
                """)
                
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {self.table_name}_doc_type_idx 
                    ON {self.table_name} (document_type);
                """)
                
                # GIN index for JSONB metadata
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {self.table_name}_metadata_idx 
                    ON {self.table_name} USING gin (metadata);
                """)
                
                logger.info("Database indexes created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            # Non-critical, continue without indexes
            pass
    
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
            with self.connection.cursor() as cursor:
                # Prepare batch insert
                insert_query = f"""
                    INSERT INTO {self.table_name} 
                    (embedding, text_content, metadata, source_document, document_type, token_count)
                    VALUES %s
                """
                
                # Prepare data for batch insert
                insert_data = []
                for embedding, chunk in zip(embeddings, chunks):
                    metadata = chunk.get('metadata', {})
                    insert_data.append((
                        embedding,
                        chunk.get('text', ''),
                        json.dumps(metadata),
                        metadata.get('source_document', ''),
                        metadata.get('document_type', 'agricultural_guide'),
                        chunk.get('token_count', 0)
                    ))
                
                # Execute batch insert
                psycopg2.extras.execute_values(
                    cursor,
                    insert_query,
                    insert_data,
                    template=None,
                    page_size=100
                )
                
                logger.info(f"Successfully added {len(embeddings)} vectors to database")
                return True
                
        except Exception as e:
            logger.error(f"Error adding vectors to database: {e}")
            return False
    
    def search(self, 
               query_embedding: List[float], 
               top_k: int = 5,
               threshold: float = 0.7,
               filter_by_document: Optional[str] = None,
               filter_by_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the database.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            filter_by_document: Optional document name filter
            filter_by_type: Optional document type filter
            
        Returns:
            List of search results with metadata and scores
        """
        if not query_embedding:
            logger.warning("Empty query embedding provided")
            return []
        
        try:
            with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Build query with optional filters
                where_conditions = []
                params = [query_embedding, top_k]
                
                if filter_by_document:
                    where_conditions.append("source_document = %s")
                    params.append(filter_by_document)
                
                if filter_by_type:
                    where_conditions.append("document_type = %s")
                    params.append(filter_by_type)
                
                where_clause = ""
                if where_conditions:
                    where_clause = f"WHERE {' AND '.join(where_conditions)}"
                
                # Vector similarity search query
                search_query = f"""
                    SELECT 
                        id as chunk_id,
                        1 - (embedding <=> %s::vector) as score,
                        text_content as text,
                        metadata,
                        source_document,
                        document_type,
                        token_count,
                        created_at
                    FROM {self.table_name}
                    {where_clause}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                """
                
                # Execute search
                cursor.execute(search_query, params)
                results = cursor.fetchall()
                
                # Process results
                processed_results = []
                for i, row in enumerate(results):
                    if row['score'] < threshold:
                        continue
                    
                    # Parse metadata JSON
                    metadata = json.loads(row['metadata']) if row['metadata'] else {}
                    
                    result = {
                        'chunk_id': row['chunk_id'],
                        'score': float(row['score']),
                        'text': row['text'],
                        'metadata': metadata,
                        'source_document': row['source_document'],
                        'document_type': row['document_type'],
                        'token_count': row['token_count'],
                        'rank': i + 1
                    }
                    
                    processed_results.append(result)
                
                logger.info(f"Search returned {len(processed_results)} results above threshold {threshold}")
                return processed_results
                
        except Exception as e:
            logger.error(f"Error searching database: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the database.
        
        Returns:
            Dictionary with database statistics
        """
        try:
            with self.connection.cursor() as cursor:
                # Get total vector count
                cursor.execute(f"SELECT COUNT(*) FROM {self.table_name};")
                total_vectors = cursor.fetchone()[0]
                
                # Get unique documents
                cursor.execute(f"SELECT COUNT(DISTINCT source_document) FROM {self.table_name};")
                unique_documents = cursor.fetchone()[0]
                
                # Get document types
                cursor.execute(f"SELECT document_type, COUNT(*) FROM {self.table_name} GROUP BY document_type;")
                document_types = dict(cursor.fetchall())
                
                # Get storage size
                cursor.execute(f"""
                    SELECT pg_size_pretty(pg_total_relation_size('{self.table_name}')) as table_size;
                """)
                table_size = cursor.fetchone()[0]
                
                return {
                    'total_vectors': total_vectors,
                    'unique_documents': unique_documents,
                    'document_types': document_types,
                    'table_size': table_size,
                    'dimension': self.dimension,
                    'database_type': 'PostgreSQL with pgvector'
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def remove_vectors_by_document(self, document_name: str) -> bool:
        """
        Remove all vectors for a specific document.
        
        Args:
            document_name: Name of document to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE source_document = %s;", (document_name,))
                deleted_count = cursor.rowcount
                
                logger.info(f"Removed {deleted_count} vectors for document: {document_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error removing document vectors: {e}")
            return False
    
    def clear_database(self):
        """Clear all vectors from the database."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name};")
                cursor.execute(f"DELETE FROM document_metadata;")
                
                logger.info("Database cleared successfully")
                
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def __del__(self):
        """Cleanup on object destruction."""
        self.close()


# Factory function for easy switching between database types
def create_vector_database(db_type: str = "postgresql", **kwargs) -> Any:
    """
    Factory function to create vector database instances.
    
    Args:
        db_type: Type of database ('postgresql' or 'faiss')
        **kwargs: Additional parameters for database initialization
        
    Returns:
        Vector database instance
    """
    if db_type.lower() == "postgresql":
        return PostgreSQLVectorDatabase(**kwargs)
    elif db_type.lower() == "faiss":
        from .vector_database import VectorDatabase
        return VectorDatabase(**kwargs)
    else:
        raise ValueError(f"Unsupported database type: {db_type}") 