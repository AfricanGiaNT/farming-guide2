#!/usr/bin/env python3
"""
Process missing PDF documents and add them to the agricultural documents database.
This script specifically targets the new documents we identified.
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def process_missing_documents(db_path="data/agricultural_documents.db", pdfs_dir="farming-guide2/data/pdfs/"):
    """Process missing PDF documents and add them to the database."""
    
    # Ensure database path is absolute
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
    
    if not os.path.isabs(pdfs_dir):
        pdfs_dir = os.path.join(project_root, pdfs_dir)
    
    print(f"🔍 Processing missing documents")
    print(f"   Database: {db_path}")
    print(f"   PDFs directory: {pdfs_dir}")
    
    # Get existing documents in database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT source FROM documents")
    existing_docs = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    # Get all PDF files
    pdf_files = list(Path(pdfs_dir).glob("*.pdf"))
    missing_docs = [f for f in pdf_files if f.name not in existing_docs]
    
    print(f"📊 Found {len(pdf_files)} total PDFs")
    print(f"📊 Found {len(existing_docs)} already processed")
    print(f"📊 Found {len(missing_docs)} missing documents to process")
    
    if not missing_docs:
        print("✅ No missing documents to process")
        return True
    
    print(f"\n📄 Missing documents:")
    for doc in missing_docs:
        print(f"  - {doc.name}")
    
    # Use the existing document processing script but with correct paths
    try:
        # Import the document processor with the correct database path
        from scripts.data_pipeline.process_new_documents import DocumentProcessor
        
        # Create processor with correct database path
        processor = DocumentProcessor(db_path=db_path)
        
        # Process only the missing documents
        print(f"\n🚀 Starting document processing...")
        results = process_specific_documents(processor, missing_docs)
        
        if results:
            print(f"\n✅ Successfully processed {results['processed_count']} new documents")
            return True
        else:
            print(f"\n❌ Failed to process documents")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up document processor: {e}")
        print("📝 This might be due to missing dependencies. Let's try a simpler approach...")
        
        # Fallback: Use a simpler text extraction method
        return process_documents_simple(missing_docs, db_path)

def process_specific_documents(processor, document_paths):
    """Process specific document files."""
    
    processed_docs = []
    
    for i, pdf_file in enumerate(document_paths, 1):
        print(f"\n🔄 Processing {i}/{len(document_paths)}: {pdf_file.name}")
        print(f"   File size: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        try:
            result = processor.process_document(pdf_file)
            processed_docs.append(result)
            
            # Show progress
            if result['status'] == 'success':
                print(f"   ✅ Successfully processed {result['chunks_processed']} chunks")
            else:
                print(f"   ❌ Failed: {result['error']}")
                
        except Exception as e:
            print(f"   ❌ Error processing {pdf_file.name}: {e}")
            processed_docs.append({
                'filename': pdf_file.name,
                'status': 'error',
                'error': str(e)
            })
    
    return {
        "processed_count": len([d for d in processed_docs if d.get('status') == 'success']),
        "documents": processed_docs
    }

def process_documents_simple(document_paths, db_path):
    """Simple fallback document processing without complex dependencies."""
    
    print(f"\n📝 Using simple document processing fallback...")
    
    try:
        import PyPDF2
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        processed_count = 0
        
        for pdf_file in document_paths:
            print(f"📄 Processing: {pdf_file.name}")
            
            try:
                # Extract text using PyPDF2
                with open(pdf_file, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        try:
                            page_text = page.extract_text()
                            text += page_text + "\n"
                        except Exception as e:
                            print(f"  ⚠️  Error extracting page {page_num}: {e}")
                            continue
                
                if text.strip():
                    # Simple chunking - split into ~1000 character chunks
                    chunks = simple_chunk_text(text, chunk_size=1000)
                    
                    # Insert chunks into database
                    for chunk in chunks:
                        cursor.execute("""
                            INSERT INTO documents (content, source) 
                            VALUES (?, ?)
                        """, (chunk, pdf_file.name))
                    
                    print(f"  ✅ Added {len(chunks)} chunks")
                    processed_count += 1
                else:
                    print(f"  ⚠️  No text extracted")
                    
            except Exception as e:
                print(f"  ❌ Error processing {pdf_file.name}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Simple processing completed: {processed_count} documents processed")
        return processed_count > 0
        
    except ImportError:
        print("❌ PyPDF2 not available for fallback processing")
        return False
    except Exception as e:
        print(f"❌ Error in simple processing: {e}")
        return False

def simple_chunk_text(text, chunk_size=1000, overlap=200):
    """Simple text chunking function."""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at a sentence or word boundary
        if end < len(text):
            # Look for sentence boundary
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            
            if last_period > start + chunk_size // 2:
                end = last_period + 1
            elif last_newline > start + chunk_size // 2:
                end = last_newline + 1
            else:
                # Look for word boundary
                last_space = text.rfind(' ', start, end)
                if last_space > start + chunk_size // 2:
                    end = last_space
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process missing PDF documents")
    parser.add_argument("--db-path", default="data/agricultural_documents.db", help="Path to database file")
    parser.add_argument("--pdfs-dir", default="farming-guide2/data/pdfs/", help="Path to PDFs directory")
    
    args = parser.parse_args()
    
    success = process_missing_documents(args.db_path, args.pdfs_dir)
    if success:
        print("\n🎉 Missing documents processed successfully!")
    else:
        print("\n❌ Failed to process missing documents.")
        sys.exit(1)
