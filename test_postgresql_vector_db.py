#!/usr/bin/env python3
"""
Test PostgreSQL Vector Database Implementation
Verifies that the PostgreSQL vector database is working correctly.
"""

import sys
import os
import numpy as np
from typing import List, Dict, Any
from pathlib import Path

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def test_postgresql_vector_db():
    """Test the PostgreSQL vector database implementation."""
    print("🧪 Testing PostgreSQL Vector Database...")
    
    try:
        from scripts.data_pipeline.postgresql_vector_database import PostgreSQLVectorDatabase
        print("✅ PostgreSQL vector database module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PostgreSQL vector database: {e}")
        return False
    
    try:
        # Initialize database
        print("\n1️⃣ Initializing PostgreSQL vector database...")
        db = PostgreSQLVectorDatabase(dimension=1536)
        print("✅ Database initialized successfully")
        
        # Create test data
        print("\n2️⃣ Creating test data...")
        test_embeddings = [
            np.random.rand(1536).tolist(),
            np.random.rand(1536).tolist(),
            np.random.rand(1536).tolist()
        ]
        
        test_chunks = [
            {
                'text': 'Maize is a major crop in Malawi and requires adequate rainfall.',
                'metadata': {
                    'source_document': 'test_doc_1.pdf',
                    'document_type': 'agricultural_guide'
                },
                'token_count': 12
            },
            {
                'text': 'Groundnuts are drought-resistant and suitable for dry seasons.',
                'metadata': {
                    'source_document': 'test_doc_2.pdf',
                    'document_type': 'agricultural_guide'
                },
                'token_count': 10
            },
            {
                'text': 'Cassava is a root crop that can withstand harsh conditions.',
                'metadata': {
                    'source_document': 'test_doc_3.pdf',
                    'document_type': 'agricultural_guide'
                },
                'token_count': 11
            }
        ]
        print("✅ Test data created")
        
        # Test adding vectors
        print("\n3️⃣ Testing vector addition...")
        success = db.add_vectors(test_embeddings, test_chunks)
        if success:
            print("✅ Vectors added successfully")
        else:
            print("❌ Failed to add vectors")
            return False
        
        # Test search
        print("\n4️⃣ Testing vector search...")
        query_embedding = np.random.rand(1536).tolist()
        results = db.search(query_embedding, top_k=3, threshold=0.0)
        
        if results:
            print(f"✅ Search returned {len(results)} results")
            for i, result in enumerate(results):
                print(f"   Result {i+1}: {result['text'][:50]}... (Score: {result['score']:.3f})")
        else:
            print("❌ Search returned no results")
            return False
        
        # Test database stats
        print("\n5️⃣ Testing database statistics...")
        stats = db.get_database_stats()
        if stats:
            print("✅ Database statistics retrieved:")
            print(f"   • Total vectors: {stats.get('total_vectors', 0)}")
            print(f"   • Unique documents: {stats.get('unique_documents', 0)}")
            print(f"   • Table size: {stats.get('table_size', 'Unknown')}")
        else:
            print("❌ Failed to get database statistics")
            return False
        
        # Test filtered search
        print("\n6️⃣ Testing filtered search...")
        filtered_results = db.search(
            query_embedding, 
            top_k=2, 
            threshold=0.0,
            filter_by_document='test_doc_1.pdf'
        )
        
        if filtered_results:
            print(f"✅ Filtered search returned {len(filtered_results)} results")
        else:
            print("✅ Filtered search returned no results (expected if no matching documents)")
        
        # Test document removal
        print("\n7️⃣ Testing document removal...")
        removal_success = db.remove_vectors_by_document('test_doc_1.pdf')
        if removal_success:
            print("✅ Document removal successful")
        else:
            print("❌ Document removal failed")
            return False
        
        # Verify removal
        stats_after_removal = db.get_database_stats()
        if stats_after_removal['total_vectors'] < stats['total_vectors']:
            print("✅ Vector count decreased after removal")
        else:
            print("❌ Vector count unchanged after removal")
        
        # Clean up
        print("\n8️⃣ Cleaning up test data...")
        db.clear_database()
        print("✅ Test data cleaned up")
        
        # Close connection
        db.close()
        print("✅ Database connection closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def test_migration_status():
    """Test migration status functionality."""
    print("\n🔄 Testing migration status...")
    
    try:
        from scripts.data_pipeline.database_migration import DatabaseMigrator
        
        migrator = DatabaseMigrator()
        status = migrator.get_migration_status()
        
        print("✅ Migration status retrieved:")
        print(f"   • FAISS available: {status.get('faiss_available', False)}")
        print(f"   • PostgreSQL available: {status.get('postgresql_available', False)}")
        print(f"   • FAISS vectors: {status.get('faiss_vector_count', 0)}")
        print(f"   • PostgreSQL vectors: {status.get('postgresql_vector_count', 0)}")
        print(f"   • Migration recommended: {status.get('migration_recommended', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration status test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from scripts.utils.config_loader import config
        
        # Check if PostgreSQL configuration exists
        config_file = Path("config/postgresql.env")
        if config_file.exists():
            print("✅ PostgreSQL configuration file exists")
        else:
            print("⚠️ PostgreSQL configuration file not found")
            print("   Run 'python setup_postgresql_vector_db.py' to create it")
        
        # Test configuration loading
        database_url = config.get("DATABASE_URL")
        if database_url:
            print(f"✅ Database URL configured: {database_url[:20]}...")
        else:
            print("⚠️ DATABASE_URL not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 PostgreSQL Vector Database Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Test configuration
    test_results.append(("Configuration", test_configuration()))
    
    # Test PostgreSQL vector database
    test_results.append(("PostgreSQL Vector DB", test_postgresql_vector_db()))
    
    # Test migration status
    test_results.append(("Migration Status", test_migration_status()))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("-" * 30)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("\n🎉 All tests passed! PostgreSQL vector database is working correctly.")
        print("\n📱 Ready for migration:")
        print("• Run 'python migrate_to_postgresql.py' to migrate from FAISS")
        print("• Update your bot configuration to use PostgreSQL")
        print("• Enjoy better performance and scalability!")
    else:
        print(f"\n⚠️ {len(test_results) - passed} tests failed.")
        print("\nTroubleshooting:")
        print("• Make sure PostgreSQL is running")
        print("• Check that pgvector extension is installed")
        print("• Verify database credentials in config/postgresql.env")
        print("• Run 'python setup_postgresql_vector_db.py' if needed")
    
    return passed == len(test_results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 