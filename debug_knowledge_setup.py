#!/usr/bin/env python3
"""
Debug Knowledge Base Setup - With Progress Tracking
Shows real-time progress for PDF processing and embedding generation
"""

import os
import sys
import time
from typing import List, Dict, Any
from datetime import datetime

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from scripts.data_pipeline.pdf_processor import PDFProcessor
    from scripts.data_pipeline.text_chunker import TextChunker
    from scripts.data_pipeline.embedding_generator import EmbeddingGenerator
    from scripts.data_pipeline.vector_database import VectorDatabase
    from scripts.utils.logger import logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class DebugKnowledgeSetup:
    """Debug version with progress tracking."""
    
    def __init__(self):
        """Initialize debug setup."""
        print("🔧 Debug Knowledge Base Setup")
        print("=" * 50)
        
        # Initialize components
        self.pdf_processor = PDFProcessor()
        self.text_chunker = TextChunker(chunk_size=500, overlap=100)  # Smaller chunks
        self.embedding_generator = EmbeddingGenerator()
        
        # Get embedding dimension and init vector DB
        embedding_dim = self.embedding_generator.get_embedding_dimension()
        self.vector_db = VectorDatabase(dimension=embedding_dim, storage_path="data/vector_db")
        
        print("✅ All components initialized")
        
    def process_pdfs_with_progress(self, pdf_directory: str = "data/pdfs") -> bool:
        """Process PDFs with detailed progress tracking."""
        try:
            # Find PDFs
            pdf_files = []
            if os.path.exists(pdf_directory):
                for file in os.listdir(pdf_directory):
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(pdf_directory, file))
            
            if not pdf_files:
                print(f"📁 No PDF files found in {pdf_directory}")
                return False
            
            print(f"📚 Found {len(pdf_files)} PDF files:")
            for pdf_file in pdf_files:
                print(f"  • {os.path.basename(pdf_file)}")
            
            # Process each PDF individually with progress
            for i, pdf_path in enumerate(pdf_files, 1):
                print(f"\n🔄 Processing PDF {i}/{len(pdf_files)}: {os.path.basename(pdf_path)}")
                
                # Step 1: Extract text
                print("  📖 Extracting text...")
                start_time = time.time()
                text = self.pdf_processor.extract_text_from_pdf(pdf_path)
                extraction_time = time.time() - start_time
                print(f"  ✅ Extracted {len(text):,} characters in {extraction_time:.2f}s")
                
                if not text:
                    print(f"  ❌ No text extracted from {pdf_path}")
                    continue
                
                # Step 2: Create chunks
                print("  🔪 Creating text chunks...")
                start_time = time.time()
                doc_name = os.path.basename(pdf_path)
                metadata = {
                    'source_document': doc_name,
                    'file_path': pdf_path,
                    'document_type': 'agricultural_guide'
                }
                chunks = self.text_chunker.chunk_text(text, metadata)
                chunking_time = time.time() - start_time
                print(f"  ✅ Created {len(chunks)} chunks in {chunking_time:.2f}s")
                
                # Step 3: Generate embeddings with progress
                print(f"  🧠 Generating embeddings for {len(chunks)} chunks...")
                texts = [chunk['text'] for chunk in chunks]
                
                # Process in small batches to show progress
                batch_size = 10
                all_embeddings = []
                
                for batch_start in range(0, len(texts), batch_size):
                    batch_end = min(batch_start + batch_size, len(texts))
                    batch_texts = texts[batch_start:batch_end]
                    
                    print(f"    🔄 Processing batch {batch_start//batch_size + 1}/{(len(texts)-1)//batch_size + 1} ({len(batch_texts)} chunks)...")
                    
                    start_time = time.time()
                    try:
                        batch_embeddings = self.embedding_generator.generate_embeddings(batch_texts)
                        batch_time = time.time() - start_time
                        
                        if batch_embeddings:
                            all_embeddings.extend(batch_embeddings)
                            print(f"    ✅ Batch completed in {batch_time:.2f}s (avg {batch_time/len(batch_texts):.2f}s per embedding)")
                        else:
                            print(f"    ❌ Batch failed - no embeddings returned")
                            return False
                            
                    except Exception as e:
                        print(f"    ❌ Batch failed with error: {e}")
                        return False
                
                if not all_embeddings:
                    print(f"  ❌ No embeddings generated for {pdf_path}")
                    continue
                
                print(f"  ✅ Generated {len(all_embeddings)} embeddings total")
                
                # Step 4: Add to vector database
                print("  💾 Adding to vector database...")
                start_time = time.time()
                success = self.vector_db.add_vectors(all_embeddings, chunks)
                db_time = time.time() - start_time
                
                if success:
                    print(f"  ✅ Added to database in {db_time:.2f}s")
                else:
                    print(f"  ❌ Failed to add to database")
                    return False
            
            # Save the index
            print("\n💾 Saving vector database...")
            self.vector_db.save_index()
            print("✅ Vector database saved successfully!")
            
            # Show final status
            total_vectors = len(self.vector_db.vectors) if hasattr(self.vector_db, 'vectors') else 0
            total_metadata = len(self.vector_db.metadata) if hasattr(self.vector_db, 'metadata') else 0
            
            print(f"\n📊 Final Status:")
            print(f"  • Documents processed: {len(pdf_files)}")
            print(f"  • Total vectors: {total_vectors}")
            print(f"  • Total metadata entries: {total_metadata}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_quick_search(self):
        """Test the search functionality quickly."""
        print("\n🔍 Testing search functionality...")
        
        test_queries = [
            "maize planting",
            "soil preparation", 
            "groundnut cultivation"
        ]
        
        for query in test_queries:
            print(f"\n❓ Testing query: '{query}'")
            try:
                # Generate query embedding
                query_embedding = self.embedding_generator.generate_query_embedding(query)
                if not query_embedding:
                    print("  ❌ Failed to generate query embedding")
                    continue
                
                # Search
                results = self.vector_db.search(query_embedding, top_k=3, threshold=0.7)
                print(f"  ✅ Found {len(results)} results")
                
                for i, result in enumerate(results, 1):
                    score = result.get('score', 0)
                    source = result.get('source_document', 'Unknown')
                    text_preview = result.get('text', '')[:100] + "..."
                    print(f"    {i}. {source} (Score: {score:.3f})")
                    print(f"       {text_preview}")
                    
            except Exception as e:
                print(f"  ❌ Search failed: {e}")
    
    def monitor_system_resources(self):
        """Monitor system resources during processing."""
        import psutil
        
        process = psutil.Process()
        print(f"\n📊 System Resources:")
        print(f"  • CPU Usage: {process.cpu_percent()}%")
        print(f"  • Memory Usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
        print(f"  • Open Files: {len(process.open_files())}")


def main():
    """Main debug function."""
    setup = DebugKnowledgeSetup()
    
    print(f"\n🚀 Starting debug processing at {datetime.now().strftime('%H:%M:%S')}")
    
    # Monitor initial resources
    setup.monitor_system_resources()
    
    # Process PDFs with progress tracking
    success = setup.process_pdfs_with_progress()
    
    if success:
        print("\n🎉 Processing completed successfully!")
        
        # Test search functionality
        setup.test_quick_search()
        
        # Final resource check
        setup.monitor_system_resources()
        
        print(f"\n✅ Debug processing complete at {datetime.now().strftime('%H:%M:%S')}")
        print("\nNext steps:")
        print("• Knowledge base is ready for enhanced recommendations")
        print("• Run: python main.py (to start the Telegram bot)")
        print("• Test enhanced recommendations with PDF knowledge")
        
    else:
        print("\n❌ Processing failed!")
        print("Check the detailed output above for specific error information")


if __name__ == "__main__":
    main() 