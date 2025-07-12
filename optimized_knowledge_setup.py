#!/usr/bin/env python3
"""
Optimized Knowledge Setup - Larger Batches, Better Progress
Process all PDFs efficiently with realistic time estimates
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from scripts.data_pipeline.pdf_processor import PDFProcessor
    from scripts.data_pipeline.embedding_generator import EmbeddingGenerator
    from scripts.data_pipeline.vector_database import VectorDatabase
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class OptimizedTextChunker:
    """Optimized chunker with efficient processing."""
    
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text_optimized(self, text: str, doc_name: str) -> List[Dict[str, Any]]:
        """Optimized chunking with minimal overhead."""
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Word boundary detection
            if end < len(text):
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'chunk_id': chunk_id,
                    'source_document': doc_name,
                    'char_count': len(chunk_text)
                })
                chunk_id += 1
            
            start = end - self.overlap
            if start >= len(text):
                break
        
        return chunks


class OptimizedKnowledgeSetup:
    """Optimized setup with larger batches and better progress."""
    
    def __init__(self):
        print("🚀 Optimized Knowledge Base Setup")
        print("=" * 50)
        
        self.pdf_processor = PDFProcessor()
        self.chunker = OptimizedTextChunker(chunk_size=800, overlap=100)
        self.embedding_generator = EmbeddingGenerator()
        
        embedding_dim = self.embedding_generator.get_embedding_dimension()
        self.vector_db = VectorDatabase(dimension=embedding_dim, storage_path="data/vector_db")
        
        print("✅ All components initialized")
    
    def process_all_pdfs_optimized(self, pdf_directory: str = "data/pdfs") -> bool:
        """Process all PDFs with optimized batching."""
        print(f"\n🚀 Starting full processing at {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Find all PDFs
            pdf_files = []
            if os.path.exists(pdf_directory):
                for file in os.listdir(pdf_directory):
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(pdf_directory, file))
            
            if not pdf_files:
                print(f"❌ No PDFs found in {pdf_directory}")
                return False
            
            print(f"📚 Processing {len(pdf_files)} PDF files:")
            for pdf_file in pdf_files:
                print(f"  • {os.path.basename(pdf_file)}")
            
            # Process all PDFs first, then batch embeddings
            all_chunks = []
            
            # Step 1: Extract and chunk all PDFs
            print("\n📖 Phase 1: Text extraction and chunking")
            for i, pdf_path in enumerate(pdf_files, 1):
                print(f"  {i}/{len(pdf_files)}: {os.path.basename(pdf_path)}")
                
                # Extract text
                text = self.pdf_processor.extract_text_from_pdf(pdf_path)
                if not text:
                    print(f"    ❌ No text extracted")
                    continue
                
                # Chunk text
                chunks = self.chunker.chunk_text_optimized(text, os.path.basename(pdf_path))
                all_chunks.extend(chunks)
                
                print(f"    ✅ {len(text):,} chars → {len(chunks)} chunks")
            
            if not all_chunks:
                print("❌ No chunks created")
                return False
            
            total_chunks = len(all_chunks)
            print(f"\n📊 Total: {total_chunks} chunks from {len(pdf_files)} PDFs")
            
            # Step 2: Generate embeddings in optimized batches
            print(f"\n🧠 Phase 2: Embedding generation")
            batch_size = 10  # Optimized batch size
            total_batches = (total_chunks + batch_size - 1) // batch_size
            
            # Time estimation
            estimated_time = total_batches * 0.8  # ~0.8 seconds per batch
            print(f"📅 Estimated completion: {estimated_time/60:.1f} minutes")
            
            all_embeddings = []
            texts = [chunk['text'] for chunk in all_chunks]
            
            start_time = time.time()
            
            for i in range(0, len(texts), batch_size):
                batch_num = i // batch_size + 1
                batch = texts[i:i + batch_size]
                
                # Progress indicator
                progress = (batch_num / total_batches) * 100
                elapsed = time.time() - start_time
                
                if batch_num > 1:
                    eta = (elapsed / (batch_num - 1)) * (total_batches - batch_num)
                    print(f"  🔄 Batch {batch_num}/{total_batches} ({progress:.1f}%) - ETA: {eta/60:.1f}m")
                else:
                    print(f"  🔄 Batch {batch_num}/{total_batches} ({progress:.1f}%)")
                
                try:
                    embeddings = self.embedding_generator.generate_embeddings(batch)
                    if embeddings:
                        all_embeddings.extend(embeddings)
                    else:
                        print(f"    ❌ Failed to generate embeddings for batch {batch_num}")
                        return False
                        
                except Exception as e:
                    print(f"    ❌ Error in batch {batch_num}: {e}")
                    return False
                
                # Show progress every 10 batches
                if batch_num % 10 == 0:
                    elapsed_min = elapsed / 60
                    rate = batch_num / elapsed_min if elapsed_min > 0 else 0
                    print(f"    📊 Progress: {batch_num * batch_size} embeddings, {rate:.1f} batches/min")
            
            total_time = time.time() - start_time
            print(f"✅ Generated {len(all_embeddings)} embeddings in {total_time/60:.1f} minutes")
            
            # Step 3: Add to vector database
            print("\n💾 Phase 3: Vector database storage")
            success = self.vector_db.add_vectors(all_embeddings, all_chunks)
            
            if success:
                print("✅ Added to vector database")
                
                # Save index
                self.vector_db.save_index()
                print("✅ Index saved")
                
                # Final summary
                print(f"\n🎉 COMPLETE at {datetime.now().strftime('%H:%M:%S')}")
                print(f"📊 Final Results:")
                print(f"  • Documents processed: {len(pdf_files)}")
                print(f"  • Total chunks: {total_chunks}")
                print(f"  • Total embeddings: {len(all_embeddings)}")
                print(f"  • Processing time: {total_time/60:.1f} minutes")
                
                return True
            else:
                print("❌ Failed to add to vector database")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_knowledge_base(self):
        """Test the completed knowledge base."""
        print("\n🔍 Testing knowledge base...")
        
        test_queries = [
            "maize planting recommendations",
            "groundnut cultivation practices",
            "soil preparation techniques"
        ]
        
        for query in test_queries:
            print(f"\n❓ Query: '{query}'")
            try:
                query_embedding = self.embedding_generator.generate_query_embedding(query)
                if query_embedding:
                    results = self.vector_db.search(query_embedding, top_k=3, threshold=0.7)
                    print(f"  ✅ Found {len(results)} relevant results")
                    
                    for i, result in enumerate(results, 1):
                        source = result.get('source_document', 'Unknown')
                        score = result.get('score', 0)
                        print(f"    {i}. {source} (Score: {score:.3f})")
                else:
                    print("  ❌ Failed to generate query embedding")
                    
            except Exception as e:
                print(f"  ❌ Query failed: {e}")


def main():
    """Main optimized setup function."""
    setup = OptimizedKnowledgeSetup()
    
    success = setup.process_all_pdfs_optimized()
    
    if success:
        print("\n🎉 Knowledge base setup completed successfully!")
        
        # Test the knowledge base
        setup.test_knowledge_base()
        
        print("\n🚀 Ready for enhanced recommendations!")
        print("Next steps:")
        print("• Run: python main.py (to start Telegram bot)")
        print("• Test: /crops Lilongwe (enhanced with PDF knowledge)")
        
    else:
        print("\n❌ Setup failed!")
        print("Check the output above for specific error details")


if __name__ == "__main__":
    main() 