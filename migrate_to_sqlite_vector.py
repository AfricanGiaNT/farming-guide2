#!/usr/bin/env python3
"""
SQLite Vector Database Migration Script
Simple, fast migration from FAISS to SQLite vector database.
"""

import os
import sys
import sqlite3
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def print_step(step: str):
    """Print formatted step."""
    print(f"\n🔧 {step}")

def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")

class SQLiteVectorDatabase:
    """
    Simple SQLite vector database using JSON for vectors.
    Drop-in replacement for FAISS.
    """
    
    def __init__(self, db_path: str = "data/farming_guide.db"):
        """Initialize SQLite vector database."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables."""
        cursor = self.conn.cursor()
        
        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                metadata TEXT,
                embedding TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster searching
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source ON documents(source)
        """)
        
        self.conn.commit()
    
    def add_documents(self, texts: List[str], metadatas: List[Dict], embeddings: List[List[float]]):
        """Add documents with embeddings."""
        cursor = self.conn.cursor()
        
        for text, metadata, embedding in zip(texts, metadatas, embeddings):
            cursor.execute("""
                INSERT INTO documents (content, source, metadata, embedding)
                VALUES (?, ?, ?, ?)
            """, (
                text,
                metadata.get('source', ''),
                json.dumps(metadata),
                json.dumps(embedding)
            ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Simple similarity search using cosine similarity."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents")
        
        results = []
        query_vec = np.array(query_embedding)
        
        for row in cursor.fetchall():
            doc_embedding = json.loads(row['embedding'])
            doc_vec = np.array(doc_embedding)
            
            # Cosine similarity
            similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
            
            results.append({
                'content': row['content'],
                'metadata': json.loads(row['metadata']),
                'score': float(similarity)
            })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM documents")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(DISTINCT source) as sources FROM documents")
        sources = cursor.fetchone()['sources']
        
        return {
            'total_documents': total,
            'unique_sources': sources
        }

def migrate_faiss_to_sqlite():
    """Migrate from FAISS to SQLite vector database."""
    print_step("Starting FAISS to SQLite migration...")
    
    # Check if FAISS data exists
    faiss_path = Path("data/vector_db")
    if not faiss_path.exists():
        print_error("FAISS vector database not found. Nothing to migrate.")
        return False
    
    try:
        # Load FAISS data
        print_step("Loading FAISS vector database...")
        from scripts.data_pipeline.vector_database import VectorDatabase
        
        faiss_db = VectorDatabase(storage_path="data/vector_db")
        
        # Get all vectors and metadata
        print_step("Extracting vectors and metadata...")
        
        # Load the index and metadata
        import faiss
        index_path = faiss_path / "faiss_index_flat.index"
        metadata_path = faiss_path / "faiss_index_flat.metadata"
        
        if not index_path.exists() or not metadata_path.exists():
            print_error("FAISS files not found")
            return False
        
        # Load FAISS index
        index = faiss.read_index(str(index_path))
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
        
        # Extract the actual metadata list that contains PDF chunks
        metadata = data['metadata']  # This is the list of actual chunks
        id_to_chunk = data['id_to_chunk']  # This maps IDs to chunks
        
        print_success(f"Loaded {index.ntotal} vectors from FAISS")
        print_success(f"Found {len(metadata)} chunks in metadata")
        
        # Create SQLite database
        print_step("Creating SQLite vector database...")
        sqlite_db = SQLiteVectorDatabase("data/farming_guide_vectors.db")
        
        # Prepare data for SQLite
        print_step("Preparing data from metadata...")
        
        texts = []
        metadatas = []
        embeddings = []
        
        print_step("Generating embeddings using OpenAI...")
        from scripts.data_pipeline.embedding_generator import EmbeddingGenerator
        
        embedding_gen = EmbeddingGenerator()
        
        for i, chunk in enumerate(metadata):
            # Each chunk should have a 'text' field with the actual content
            text = chunk.get('text', '')
            if text.strip() and len(text) > 10:  # Only process meaningful text
                texts.append(text)
                metadatas.append(chunk)
                
                # Generate new embedding
                try:
                    embedding = embedding_gen.generate_query_embedding(text)
                    embeddings.append(embedding)
                    if len(embeddings) % 10 == 0:
                        print(f"  Generated {len(embeddings)} embeddings...")
                except Exception as e:
                    print(f"Warning: Failed to generate embedding for chunk {i}: {e}")
                    continue
        
        # Add to SQLite
        print_step("Adding data to SQLite database...")
        sqlite_db.add_documents(texts, metadatas, embeddings)
        
        # Verify migration
        stats = sqlite_db.get_stats()
        print_success(f"Migration complete! {stats['total_documents']} documents migrated")
        print_success(f"Database location: data/farming_guide_vectors.db")
        
        return True
        
    except Exception as e:
        print_error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SQLite Vector Database Migration")
    print("=====================================")
    
    success = migrate_faiss_to_sqlite()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update your bot configuration to use SQLite")
        print("2. Test the new vector database")
        print("3. Backup the old FAISS data")
    else:
        print("\n❌ Migration failed. Please check the errors above.") 