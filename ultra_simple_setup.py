#!/usr/bin/env python3
"""
Ultra Simple Knowledge Setup - Minimal Text Processing
Process very small chunks with extensive debugging
"""

import os
import sys
import time
from datetime import datetime

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from scripts.data_pipeline.pdf_processor import PDFProcessor
    from scripts.data_pipeline.embedding_generator import EmbeddingGenerator
    from scripts.data_pipeline.vector_database import VectorDatabase
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class UltraSimpleChunker:
    """Ultra simple chunker with minimal processing."""
    
    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size
        print(f"📏 Chunker initialized with size: {chunk_size}")
    
    def chunk_text_minimal(self, text: str, doc_name: str) -> list:
        """Minimal chunking with detailed progress."""
        print(f"  🔍 Starting chunking for {doc_name}")
        print(f"  📝 Text length: {len(text):,} characters")
        
        if not text:
            print("  ⚠️  Empty text")
            return []
        
        # Ultra simple splitting - just by character count
        chunks = []
        start = 0
        chunk_id = 0
        
        print(f"  🔄 Processing chunks of {self.chunk_size} characters...")
        
        while start < len(text):
            print(f"    📍 Chunk {chunk_id}: position {start:,} to {min(start + self.chunk_size, len(text)):,}")
            
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            
            # Minimal cleaning - just strip whitespace
            chunk_text = chunk_text.strip()
            
            if chunk_text:
                chunk = {
                    'text': chunk_text,
                    'chunk_id': chunk_id,
                    'source_document': doc_name,
                    'char_count': len(chunk_text)
                }
                chunks.append(chunk)
                print(f"    ✅ Added chunk {chunk_id} ({len(chunk_text)} chars)")
                chunk_id += 1
            else:
                print(f"    ⚠️  Skipped empty chunk {chunk_id}")
            
            start = end
            
            # Progress check every 10 chunks
            if chunk_id % 10 == 0 and chunk_id > 0:
                print(f"    📊 Progress: {chunk_id} chunks created")
        
        print(f"  ✅ Chunking complete: {len(chunks)} chunks created")
        return chunks


class UltraSimpleSetup:
    """Ultra minimal setup with extensive debugging."""
    
    def __init__(self):
        print("🚀 Ultra Simple Knowledge Setup")
        print("=" * 50)
        
        try:
            print("1️⃣ Initializing PDF processor...")
            self.pdf_processor = PDFProcessor()
            print("✅ PDF processor ready")
            
            print("2️⃣ Initializing chunker...")
            self.chunker = UltraSimpleChunker(chunk_size=300)  # Very small chunks
            print("✅ Chunker ready")
            
            print("3️⃣ Initializing embedding generator...")
            self.embedding_generator = EmbeddingGenerator()
            print("✅ Embedding generator ready")
            
            print("4️⃣ Initializing vector database...")
            embedding_dim = self.embedding_generator.get_embedding_dimension()
            self.vector_db = VectorDatabase(dimension=embedding_dim, storage_path="data/vector_db")
            print("✅ Vector database ready")
            
            print("🎯 All components initialized successfully!")
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            raise
    
    def process_single_pdf(self, pdf_path: str) -> bool:
        """Process a single PDF with extensive debugging."""
        print(f"\n🔄 Processing: {os.path.basename(pdf_path)}")
        
        try:
            # Step 1: Extract text
            print("📖 Step 1: Extracting text...")
            start_time = time.time()
            text = self.pdf_processor.extract_text_from_pdf(pdf_path)
            extract_time = time.time() - start_time
            
            if not text:
                print("❌ No text extracted")
                return False
            
            print(f"✅ Extracted {len(text):,} characters in {extract_time:.2f}s")
            
            # Step 2: Chunk text (this is where it might get stuck)
            print("🔪 Step 2: Chunking text...")
            start_time = time.time()
            
            chunks = self.chunker.chunk_text_minimal(text, os.path.basename(pdf_path))
            
            chunk_time = time.time() - start_time
            print(f"✅ Chunked into {len(chunks)} pieces in {chunk_time:.2f}s")
            
            if not chunks:
                print("❌ No chunks created")
                return False
            
            # Step 3: Process in tiny batches
            print("🧠 Step 3: Processing embeddings...")
            batch_size = 2  # Ultra small batches
            total_processed = 0
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                print(f"  🔄 Batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}: {len(batch)} chunks")
                
                # Extract text from chunks
                texts = [chunk['text'] for chunk in batch]
                
                try:
                    start_time = time.time()
                    embeddings = self.embedding_generator.generate_embeddings(texts)
                    embed_time = time.time() - start_time
                    
                    if embeddings:
                        # Add to vector database
                        success = self.vector_db.add_vectors(embeddings, batch)
                        if success:
                            total_processed += len(batch)
                            print(f"    ✅ Processed {len(batch)} chunks in {embed_time:.2f}s")
                        else:
                            print(f"    ❌ Failed to add to database")
                            return False
                    else:
                        print(f"    ❌ No embeddings generated")
                        return False
                        
                except Exception as e:
                    print(f"    ❌ Batch error: {e}")
                    return False
                
                # Small delay to prevent overwhelming the API
                time.sleep(0.5)
            
            print(f"✅ Successfully processed {total_processed} chunks from {os.path.basename(pdf_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing {pdf_path}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_minimal_setup(self):
        """Run ultra minimal setup."""
        print(f"\n🚀 Starting at {datetime.now().strftime('%H:%M:%S')}")
        
        # Find PDFs
        pdf_dir = "data/pdfs"
        if not os.path.exists(pdf_dir):
            print(f"❌ Directory {pdf_dir} not found")
            return False
        
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
        if not pdf_files:
            print(f"❌ No PDF files found in {pdf_dir}")
            return False
        
        print(f"📚 Found {len(pdf_files)} PDF files")
        
        # Process just the first PDF for testing
        pdf_path = os.path.join(pdf_dir, pdf_files[0])
        print(f"🎯 Processing only: {pdf_files[0]} (for testing)")
        
        success = self.process_single_pdf(pdf_path)
        
        if success:
            print("\n💾 Saving vector database...")
            self.vector_db.save_index()
            print("✅ Database saved")
            
            print(f"\n🎉 Test complete at {datetime.now().strftime('%H:%M:%S')}")
            return True
        else:
            print(f"\n❌ Test failed at {datetime.now().strftime('%H:%M:%S')}")
            return False


def main():
    """Main function."""
    try:
        setup = UltraSimpleSetup()
        success = setup.run_minimal_setup()
        
        if success:
            print("\n🎉 Ultra simple setup succeeded!")
            print("This confirms the basic pipeline works.")
            print("Run the full setup when ready.")
        else:
            print("\n❌ Ultra simple setup failed!")
            print("Check the detailed output above for the bottleneck.")
            
    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 