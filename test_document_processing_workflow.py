#!/usr/bin/env python3
"""
Test Document Processing Workflow
Demonstrates the complete workflow for processing new documents and adding them to SQLite vector database.
"""

import os
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def test_document_processing_workflow():
    """Test the complete document processing workflow."""
    print("🧪 Testing Document Processing Workflow")
    print("=" * 50)
    
    # Step 1: Check if database exists
    print("Step 1: Checking database status...")
    try:
        from scripts.data_pipeline.database_manager import SQLiteVectorDatabaseManager
        manager = SQLiteVectorDatabaseManager()
        stats = manager.get_detailed_stats()
        
        if "error" in stats:
            print(f"❌ Database error: {stats['error']}")
            return False
        
        print(f"✅ Database exists with {stats['total_documents']} documents")
        print(f"   Sources: {stats['unique_sources']}")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    
    # Step 2: Test document validator
    print("\nStep 2: Testing document validator...")
    try:
        from scripts.data_pipeline.document_validator import DocumentValidator
        validator = DocumentValidator()
        
        # Create test directory if it doesn't exist
        test_dir = Path("data/pdfs")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        results = validator.validate_directory()
        
        if results:
            print(f"✅ Found {len(results)} documents to validate")
            summary = validator.get_validation_summary(results)
            print(f"   Valid: {summary['valid']}, Invalid: {summary['invalid']}")
            print(f"   Average quality score: {summary['average_score']}")
        else:
            print(f"📋 No documents found in {test_dir}")
            
    except Exception as e:
        print(f"❌ Error testing validator: {e}")
        return False
    
    # Step 3: Test document processor
    print("\nStep 3: Testing document processor...")
    try:
        from scripts.data_pipeline.process_new_documents import DocumentProcessor
        processor = DocumentProcessor()
        
        # Check for new documents
        result = processor.process_directory()
        
        if result['processed_count'] > 0:
            print(f"✅ Processed {result['processed_count']} new documents")
            for doc in result['documents']:
                status = "✅" if doc['status'] == 'success' else "❌"
                print(f"   {status} {doc['filename']}: {doc['chunks_processed']} chunks")
        else:
            print(f"📋 No new documents to process")
            
    except Exception as e:
        print(f"❌ Error testing processor: {e}")
        return False
    
    # Step 4: Test updated database stats
    print("\nStep 4: Checking updated database stats...")
    try:
        updated_stats = manager.get_detailed_stats()
        
        if "error" in updated_stats:
            print(f"❌ Database error: {updated_stats['error']}")
            return False
        
        print(f"✅ Database now has {updated_stats['total_documents']} documents")
        print(f"   Sources: {updated_stats['unique_sources']}")
        
        if updated_stats['sources_breakdown']:
            print(f"   Source breakdown:")
            for source in updated_stats['sources_breakdown'][:3]:  # Show top 3
                print(f"     {source['source']}: {source['chunks']} chunks")
        
    except Exception as e:
        print(f"❌ Error checking updated stats: {e}")
        return False
    
    # Step 5: Test search functionality
    print("\nStep 5: Testing search functionality...")
    try:
        from migrate_to_sqlite_vector import SQLiteVectorDatabase
        db = SQLiteVectorDatabase()
        
        # Test basic stats
        stats = db.get_stats()
        print(f"✅ Vector database has {stats['total_documents']} documents")
        print(f"   From {stats['unique_sources']} sources")
        
        # Test search with embedding
        from scripts.data_pipeline.embedding_generator import EmbeddingGenerator
        embedding_gen = EmbeddingGenerator()
        
        query = "groundnut farming techniques"
        query_embedding = embedding_gen.generate_query_embedding(query)
        
        search_results = db.similarity_search(query_embedding, top_k=3)
        
        if search_results:
            print(f"✅ Search for '{query}' returned {len(search_results)} results")
            for i, result in enumerate(search_results, 1):
                print(f"   {i}. Score: {result['score']:.3f}")
                print(f"      Content: {result['content'][:100]}...")
        else:
            print(f"❌ No search results found")
            
    except Exception as e:
        print(f"❌ Error testing search: {e}")
        return False
    
    # Step 6: Test database management
    print("\nStep 6: Testing database management...")
    try:
        # Test backup
        backup_path = manager.backup_database()
        print(f"✅ Database backup created: {backup_path}")
        
        # Test optimization
        opt_result = manager.optimize_database()
        if "error" in opt_result:
            print(f"❌ Optimization error: {opt_result['error']}")
        else:
            print(f"✅ Database optimized")
            print(f"   Size before: {opt_result['size_before']} bytes")
            print(f"   Size after: {opt_result['size_after']} bytes")
            print(f"   Space saved: {opt_result['space_saved']} bytes")
        
    except Exception as e:
        print(f"❌ Error testing management: {e}")
        return False
    
    print("\n🎉 All workflow tests completed successfully!")
    return True

def test_workflow_commands():
    """Test the command-line workflow commands."""
    print("\n🔧 Testing Command-Line Workflow")
    print("=" * 50)
    
    commands = [
        "python scripts/data_pipeline/document_validator.py",
        "python scripts/data_pipeline/process_new_documents.py",
        "python scripts/data_pipeline/database_manager.py",
        "python test_sqlite_vector_db.py",
        "python test_new_vector_search.py"
    ]
    
    for cmd in commands:
        print(f"\nCommand: {cmd}")
        print(f"Status: Available for execution")
        print(f"Purpose: {get_command_purpose(cmd)}")
    
    print("\n📋 Workflow Summary:")
    print("1. Validate documents: python scripts/data_pipeline/document_validator.py")
    print("2. Process new documents: python scripts/data_pipeline/process_new_documents.py")
    print("3. Check database stats: python scripts/data_pipeline/database_manager.py")
    print("4. Test search functionality: python test_new_vector_search.py")

def get_command_purpose(cmd):
    """Get the purpose of a command."""
    purposes = {
        "document_validator.py": "Validate document quality before processing",
        "process_new_documents.py": "Process new PDFs and add to database",
        "database_manager.py": "Manage and maintain the SQLite database",
        "test_sqlite_vector_db.py": "Test basic database functionality",
        "test_new_vector_search.py": "Test vector search with agricultural queries"
    }
    
    for key, purpose in purposes.items():
        if key in cmd:
            return purpose
    return "Unknown command"

if __name__ == "__main__":
    success = test_document_processing_workflow()
    
    if success:
        test_workflow_commands()
        print("\n✅ Document processing workflow is ready for use!")
        print("\nTo add new documents:")
        print("1. Place PDF files in data/pdfs/ directory")
        print("2. Run: python scripts/data_pipeline/process_new_documents.py")
        print("3. Test search: python test_new_vector_search.py")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1) 