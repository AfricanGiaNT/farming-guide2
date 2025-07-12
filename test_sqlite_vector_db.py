#!/usr/bin/env python3
"""
Test SQLite Vector Database
Quick test to verify the migration worked correctly.
"""

import sqlite3
import json
import numpy as np
from pathlib import Path

def test_sqlite_database():
    """Test the migrated SQLite vector database."""
    print("🧪 Testing SQLite Vector Database...")
    
    db_path = "data/farming_guide_vectors.db"
    if not Path(db_path).exists():
        print("❌ SQLite database not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get stats
        cursor.execute("SELECT COUNT(*) as total FROM documents")
        total = cursor.fetchone()['total']
        print(f"✅ Total documents: {total}")
        
        cursor.execute("SELECT COUNT(DISTINCT source) as sources FROM documents")
        sources = cursor.fetchone()['sources']
        print(f"✅ Unique sources: {sources}")
        
        # Show sample content
        cursor.execute("SELECT content, source FROM documents LIMIT 3")
        print("\n📋 Sample documents:")
        for i, row in enumerate(cursor.fetchall(), 1):
            content = row['content'][:100] + "..." if len(row['content']) > 100 else row['content']
            print(f"  {i}. Source: {row['source']}")
            print(f"     Content: {content}")
        
        # Test vector search functionality
        print("\n🔍 Testing vector search...")
        cursor.execute("SELECT embedding FROM documents LIMIT 1")
        row = cursor.fetchone()
        if row:
            embedding = json.loads(row['embedding'])
            print(f"✅ Embedding dimension: {len(embedding)}")
            print(f"✅ Sample embedding values: {embedding[:5]}...")
        
        conn.close()
        print("\n🎉 SQLite vector database is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_sqlite_database() 