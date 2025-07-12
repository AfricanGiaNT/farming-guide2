#!/usr/bin/env python3
"""
Bulk Document Processor for SQLite Vector Database
Processes all new documents in data/pdfs/ and adds them to the database.
Enhanced with progress feedback and better error handling.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import sqlite3
import json
from datetime import datetime

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from scripts.data_pipeline.pdf_processor import PDFProcessor
from scripts.data_pipeline.text_chunker import TextChunker
from scripts.data_pipeline.embedding_generator import EmbeddingGenerator
from migrate_to_sqlite_vector import SQLiteVectorDatabase

class DocumentProcessor:
    """Process new documents and add to SQLite vector database."""
    
    def __init__(self, db_path: str = "data/farming_guide_vectors.db"):
        """Initialize document processor."""
        self.db_path = db_path
        self.pdf_processor = PDFProcessor()
        self.text_chunker = TextChunker(chunk_size=1000, overlap=200)
        self.embedding_gen = EmbeddingGenerator()
        self.db = SQLiteVectorDatabase(db_path)
        
    def process_directory(self, directory: str = "data/pdfs/") -> Dict[str, Any]:
        """Process all new documents in directory."""
        directory = Path(directory)
        processed_docs = []
        
        # Create directory if it doesn't exist
        directory.mkdir(parents=True, exist_ok=True)
        
        # Get list of already processed documents
        print("🔍 Checking for already processed documents...")
        existing_sources = self._get_existing_sources()
        print(f"   Found {len(existing_sources)} already processed documents")
        
        # Get all PDF files
        pdf_files = list(directory.glob("*.pdf"))
        new_files = [f for f in pdf_files if f.name not in existing_sources]
        
        print(f"📁 Found {len(pdf_files)} total PDFs, {len(new_files)} new to process")
        
        if not new_files:
            print("✅ No new documents to process")
            return {"processed_count": 0, "documents": []}
        
        # Process each new file
        for i, pdf_file in enumerate(new_files, 1):
            print(f"\n🔄 Processing {i}/{len(new_files)}: {pdf_file.name}")
            print(f"   File size: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
            
            result = self.process_document(pdf_file)
            processed_docs.append(result)
            
            # Show progress
            if result['status'] == 'success':
                print(f"   ✅ Successfully processed {result['chunks_processed']} chunks")
            else:
                print(f"   ❌ Failed: {result['error']}")
        
        return {
            "processed_count": len([d for d in processed_docs if d['status'] == 'success']),
            "documents": processed_docs
        }
    
    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process a single document with detailed progress feedback."""
        try:
            start_time = time.time()
            
            # Extract text
            print(f"  📄 Extracting text...")
            text = self.pdf_processor.extract_text_from_pdf(str(file_path))
            
            if not text or len(text.strip()) < 100:
                return {
                    "filename": file_path.name,
                    "chunks_processed": 0,
                    "status": "error",
                    "error": "No meaningful text content found"
                }
            
            text_length = len(text)
            print(f"     Extracted {text_length:,} characters")
            
            # Chunk text with progress feedback
            print(f"  ✂️  Chunking text...")
            print(f"     Text length: {text_length:,} characters")
            
            metadata = {
                'source': file_path.name,
                'document_type': 'agricultural_guide',
                'processed_date': datetime.now().isoformat()
            }
            
            # Add progress callback for chunking
            chunks = self._chunk_text_with_progress(text, metadata)
            
            if not chunks:
                return {
                    "filename": file_path.name,
                    "chunks_processed": 0,
                    "status": "error",
                    "error": "No chunks generated from text"
                }
            
            print(f"     Created {len(chunks)} chunks")
            
            # Generate embeddings with progress
            print(f"  🧠 Generating embeddings...")
            texts = []
            metadatas = []
            embeddings = []
            
            valid_chunks = 0
            for i, chunk in enumerate(chunks):
                if len(chunk['text'].strip()) > 50:  # Only process meaningful chunks
                    valid_chunks += 1
                    texts.append(chunk['text'])
                    
                    # Create metadata for the chunk
                    chunk_metadata = {
                        'source': file_path.name,
                        'document_type': 'agricultural_guide',
                        'processed_date': datetime.now().isoformat(),
                        'chunk_id': chunk.get('chunk_id', i),
                        'token_count': chunk.get('token_count', 0)
                    }
                    metadatas.append(chunk_metadata)
                    
                    # Generate embedding
                    embedding = self.embedding_gen.generate_query_embedding(chunk['text'])
                    embeddings.append(embedding)
                    
                    # Progress feedback every 5 embeddings
                    if valid_chunks % 5 == 0:
                        print(f"     Generated {valid_chunks}/{len(chunks)} embeddings...")
            
            if not texts:
                return {
                    "filename": file_path.name,
                    "chunks_processed": 0,
                    "status": "error",
                    "error": "No meaningful chunks generated"
                }
            
            # Add to database
            print(f"  💾 Adding {len(texts)} chunks to database...")
            self.db.add_documents(texts, metadatas, embeddings)
            
            processing_time = time.time() - start_time
            print(f"     Processing completed in {processing_time:.2f} seconds")
            
            return {
                "filename": file_path.name,
                "chunks_processed": len(texts),
                "status": "success",
                "processing_time": processing_time
            }
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
            return {
                "filename": file_path.name,
                "chunks_processed": 0,
                "status": "error",
                "error": str(e)
            }
    
    def _chunk_text_with_progress(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk text with progress feedback."""
        try:
            print(f"     Tokenizing text...")
            
            # First, get token count to estimate chunks
            tokens = self.text_chunker.encoding.encode(text)
            estimated_chunks = max(1, len(tokens) // self.text_chunker.chunk_size)
            print(f"     Text tokens: {len(tokens):,}, estimated chunks: {estimated_chunks}")
            
            # If very large document, warn about processing time
            if len(tokens) > 50000:
                print(f"     ⚠️  Large document detected - this may take several minutes...")
            
            # Define progress callback with new signature
            def progress_callback(chunk_num, total_chunks, progress_pct):
                print(f"     📝 Creating chunk {chunk_num}/{total_chunks} ({progress_pct:.1f}% complete)")
            
            # Chunk the text with progress callback
            print(f"     Starting chunking process...")
            chunks = self.text_chunker.chunk_text(text, metadata, progress_callback)
            
            print(f"     ✅ Chunking complete: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            print(f"     ❌ Error during chunking: {e}")
            raise
    
    def _get_existing_sources(self) -> set:
        """Get list of already processed document sources."""
        try:
            # Check if database exists
            if not os.path.exists(self.db_path):
                return set()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='documents'
            """)
            
            if not cursor.fetchone():
                conn.close()
                return set()
            
            cursor.execute("SELECT DISTINCT source FROM documents")
            sources = {row[0] for row in cursor.fetchall()}
            conn.close()
            return sources
            
        except Exception as e:
            print(f"⚠️  Warning: Could not get existing sources: {e}")
            return set()
    
    def show_processing_summary(self, results: Dict[str, Any]) -> None:
        """Show detailed processing summary."""
        print(f"\n🎉 Processing Summary")
        print("=" * 50)
        
        successful = [d for d in results['documents'] if d['status'] == 'success']
        failed = [d for d in results['documents'] if d['status'] == 'error']
        
        print(f"✅ Successfully processed: {len(successful)} documents")
        print(f"❌ Failed: {len(failed)} documents")
        
        if successful:
            total_chunks = sum(d['chunks_processed'] for d in successful)
            print(f"📊 Total chunks added: {total_chunks}")
            
            print(f"\n📋 Success Details:")
            for doc in successful:
                time_str = f" ({doc.get('processing_time', 0):.1f}s)" if 'processing_time' in doc else ""
                print(f"  ✅ {doc['filename']}: {doc['chunks_processed']} chunks{time_str}")
        
        if failed:
            print(f"\n❌ Failed Documents:")
            for doc in failed:
                print(f"  ❌ {doc['filename']}: {doc['error']}")
        
        # Show updated database stats
        try:
            stats = self.db.get_stats()
            print(f"\n📊 Updated Database Stats:")
            print(f"  Total documents: {stats['total_documents']}")
            print(f"  Unique sources: {stats['unique_sources']}")
        except Exception as e:
            print(f"⚠️  Warning: Could not get database stats: {e}")

if __name__ == "__main__":
    print("🚀 SQLite Vector Database - Document Processor")
    print("=" * 50)
    
    processor = DocumentProcessor()
    result = processor.process_directory()
    
    # Show detailed summary
    processor.show_processing_summary(result) 