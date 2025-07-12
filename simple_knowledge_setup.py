#!/usr/bin/env python3
"""
Simple Knowledge Base Setup - Minimal Processing
Bypasses complex text cleaning to avoid hanging issues
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
    from scripts.data_pipeline.embedding_generator import EmbeddingGenerator
    from scripts.data_pipeline.vector_database import VectorDatabase
    from scripts.utils.logger import logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class SimpleTextChunker:
    """Simplified text chunker that avoids complex cleaning logic."""
    
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Simple character-based chunking."""
        if not text or not text.strip():
            return []
        
        # Simple character-based chunking (no tiktoken complexity)
        chunks = []
        chunk_id = 0
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at a word boundary
            if end < len(text):
                # Look for the last space within the chunk
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunk = {
                    'text': chunk_text,
                    'chunk_id': chunk_id,
                    'start_char': start,
                    'end_char': end,
                    'char_count': len(chunk_text),
                    'metadata': metadata or {}
                }
                chunks.append(chunk)
                chunk_id += 1
            
            # Move to next chunk with overlap
            start = end - self.overlap
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks


class SimpleKnowledgeSetup:
    """Simplified setup with minimal processing."""
    
    def __init__(self):
        print("🚀 Simple Knowledge Base Setup")
        print("=" * 40)
        
        # Initialize components
        self.pdf_processor = PDFProcessor()
        self.text_chunker = SimpleTextChunker(chunk_size=800, overlap=100)
        self.embedding_generator = EmbeddingGenerator()
        
        # Get embedding dimension and init vector DB
        embedding_dim = self.embedding_generator.get_embedding_dimension()
        self.vector_db = VectorDatabase(dimension=embedding_dim, storage_path="data/vector_db")
        
        print("✅ All components initialized")
    
    def process_pdfs_simple(self, pdf_directory: str = "data/pdfs") -> bool:
        """Process PDFs with minimal complexity."""
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
            
            print(f"📚 Found {len(pdf_files)} PDF files")
            
            # Process all PDFs
            all_chunks = []
            
            for i, pdf_path in enumerate(pdf_files, 1):
                print(f"\n🔄 Processing {i}/{len(pdf_files)}: {os.path.basename(pdf_path)}")
                
                # Extract text
                print("  📖 Extracting text...")
                text = self.pdf_processor.extract_text_from_pdf(pdf_path)
                
                if not text:
                    print("  ❌ No text extracted")
                    continue
                
                print(f"  ✅ Extracted {len(text):,} characters")
                
                # Simple chunking
                print("  🔪 Creating chunks...")
                doc_name = os.path.basename(pdf_path)
                metadata = {
                    'source_document': doc_name,
                    'file_path': pdf_path,
                    'document_type': 'agricultural_guide'
                }
                
                chunks = self.text_chunker.chunk_text(text, metadata)
                print(f"  ✅ Created {len(chunks)} chunks")
                
                all_chunks.extend(chunks)
            
            if not all_chunks:
                print("❌ No chunks created")
                return False
            
            print(f"\n🧠 Generating embeddings for {len(all_chunks)} chunks...")
            
            # Generate embeddings in small batches
            batch_size = 5  # Very small batches
            all_embeddings = []
            texts = [chunk['text'] for chunk in all_chunks]
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                print(f"  🔄 Batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} ({len(batch)} chunks)")
                
                try:
                    embeddings = self.embedding_generator.generate_embeddings(batch)
                    if embeddings:
                        all_embeddings.extend(embeddings)
                        print(f"    ✅ Generated {len(embeddings)} embeddings")
                    else:
                        print("    ❌ No embeddings generated")
                        return False
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    return False
            
            print(f"✅ Total embeddings generated: {len(all_embeddings)}")
            
            # Add to vector database
            print("💾 Adding to vector database...")
            success = self.vector_db.add_vectors(all_embeddings, all_chunks)
            
            if success:
                print("✅ Added to vector database")
                
                # Save index
                print("💾 Saving index...")
                self.vector_db.save_index()
                print("✅ Index saved")
                
                return True
            else:
                print("❌ Failed to add to vector database")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def quick_test(self):
        """Test the setup quickly."""
        print("\n🔍 Testing search...")
        
        try:
            query = "maize planting"
            print(f"Query: '{query}'")
            
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_query_embedding(query)
            if not query_embedding:
                print("❌ Failed to generate query embedding")
                return
            
            # Search
            results = self.vector_db.search(query_embedding, top_k=2, threshold=0.7)
            print(f"✅ Found {len(results)} results")
            
            for i, result in enumerate(results, 1):
                source = result.get('source_document', 'Unknown')
                score = result.get('score', 0)
                text = result.get('text', '')[:100] + "..."
                print(f"  {i}. {source} (Score: {score:.3f})")
                print(f"     {text}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")


def main():
    """Main function."""
    setup = SimpleKnowledgeSetup()
    
    print(f"\n🚀 Starting at {datetime.now().strftime('%H:%M:%S')}")
    
    # Process PDFs
    success = setup.process_pdfs_simple()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        setup.quick_test()
        
        print(f"\n✅ Complete at {datetime.now().strftime('%H:%M:%S')}")
        print("\nKnowledge base is ready!")
        print("Run: python main.py (to start the bot)")
        
    else:
        print("\n❌ Setup failed!")


if __name__ == "__main__":
    main() 