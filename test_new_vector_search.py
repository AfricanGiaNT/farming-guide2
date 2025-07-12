#!/usr/bin/env python3
"""
Test SQLite Vector Database Search
Quick demonstration of the new SQLite vector database functionality.
"""

import sys
import os
import sqlite3
import json
import numpy as np
from typing import List, Dict

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def test_vector_search():
    """Test vector search with agricultural queries."""
    print("🧪 Testing SQLite Vector Database Search...")
    
    try:
        from scripts.data_pipeline.embedding_generator import EmbeddingGenerator
        
        # Initialize embedding generator
        embedding_gen = EmbeddingGenerator()
        
        # Connect to SQLite database
        conn = sqlite3.connect("data/farming_guide_vectors.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test queries
        test_queries = [
            "How to improve groundnut yields in Malawi?",
            "What soil pH is best for groundnuts?",
            "Nitrogen fixation and inoculants for legumes",
            "Gypsum application for groundnut farming"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            
            # Generate query embedding
            query_embedding = embedding_gen.generate_query_embedding(query)
            query_vec = np.array(query_embedding)
            
            # Get all documents and calculate similarity
            cursor.execute("SELECT content, source, embedding FROM documents WHERE length(content) > 50")
            results = []
            
            for row in cursor.fetchall():
                doc_embedding = json.loads(row['embedding'])
                doc_vec = np.array(doc_embedding)
                
                # Cosine similarity
                similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
                
                results.append({
                    'content': row['content'],
                    'source': row['source'],
                    'score': float(similarity)
                })
            
            # Sort by similarity and show top 2 results
            results.sort(key=lambda x: x['score'], reverse=True)
            
            for i, result in enumerate(results[:2], 1):
                content = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                print(f"  {i}. Score: {result['score']:.3f}")
                print(f"     Content: {content}")
                print()
        
        conn.close()
        print("✅ SQLite vector search is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

if __name__ == "__main__":
    test_vector_search() 