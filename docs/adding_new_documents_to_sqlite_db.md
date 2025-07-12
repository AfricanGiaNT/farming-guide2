# Adding New Documents to SQLite Vector Database

## 📋 Overview

This guide explains how to process new agricultural documents and add them to your SQLite vector database for the Agricultural Advisor Bot. The process maintains data quality, ensures proper indexing, and expands the knowledge base seamlessly.

## 🎯 Current Database Status

**SQLite Database**: `data/farming_guide_vectors.db`
- **Current Documents**: 386 agricultural chunks
- **Source**: Malawi Groundnut Production Guide
- **Embedding Model**: OpenAI text-embedding-ada-002 (1536 dimensions)
- **Database Schema**: `documents` table with content, source, metadata, embedding columns

## 🔧 Document Processing Workflow

### Step 1: Document Preparation

**Supported Document Types**:
- ✅ PDF files (primary format)
- ✅ Text files (.txt)
- ✅ Word documents (.docx) - requires additional processing
- ✅ Web content (HTML/markdown)

**Document Quality Checklist**:
- [ ] Agricultural content relevant to Malawi/similar climates
- [ ] English language (primary) or translatable content
- [ ] Readable text quality (not scanned images without OCR)
- [ ] Authoritative source (government, research institutions, NGOs)
- [ ] Current information (published within last 10 years preferred)

### Step 2: Text Extraction and Chunking

**Automated Process**:
```bash
# Place new documents in data/pdfs/ directory
cp "new_document.pdf" data/pdfs/

# Run the document processing script
python scripts/data_pipeline/process_new_documents.py
```

**Manual Process**:
```python
# For custom processing
from scripts.data_pipeline.pdf_processor import PDFProcessor
from scripts.data_pipeline.text_chunker import TextChunker

# Initialize processors
pdf_processor = PDFProcessor()
text_chunker = TextChunker(chunk_size=1000, overlap=200)

# Process document
text = pdf_processor.extract_text("path/to/document.pdf")
chunks = text_chunker.chunk_text(text, source="document_name")
```

### Step 3: Embedding Generation

**Using OpenAI Embeddings**:
```python
from scripts.data_pipeline.embedding_generator import EmbeddingGenerator

# Initialize embedding generator
embedding_gen = EmbeddingGenerator()

# Generate embeddings for new chunks
embeddings = []
for chunk in chunks:
    embedding = embedding_gen.generate_query_embedding(chunk['text'])
    embeddings.append(embedding)
```

### Step 4: Database Insertion

**Using SQLite Database Manager**:
```python
from migrate_to_sqlite_vector import SQLiteVectorDatabase

# Connect to database
db = SQLiteVectorDatabase("data/farming_guide_vectors.db")

# Prepare data
texts = [chunk['text'] for chunk in chunks]
metadatas = [chunk['metadata'] for chunk in chunks]

# Add to database
db.add_documents(texts, metadatas, embeddings)
```

## 🛠️ Automated Tools and Scripts

### Tool 1: Bulk Document Processor

**Script**: `scripts/data_pipeline/process_new_documents.py`
```python
#!/usr/bin/env python3
"""
Bulk Document Processor for SQLite Vector Database
Processes all new documents in data/pdfs/ and adds them to the database.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import sqlite3
import json

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
        
        # Get list of already processed documents
        existing_sources = self._get_existing_sources()
        
        for pdf_file in directory.glob("*.pdf"):
            if pdf_file.name not in existing_sources:
                print(f"🔄 Processing: {pdf_file.name}")
                result = self.process_document(pdf_file)
                processed_docs.append(result)
            else:
                print(f"⏭️  Skipping: {pdf_file.name} (already processed)")
        
        return {
            "processed_count": len(processed_docs),
            "documents": processed_docs
        }
    
    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process a single document."""
        try:
            # Extract text
            print(f"  📄 Extracting text...")
            text = self.pdf_processor.extract_text(str(file_path))
            
            # Chunk text
            print(f"  ✂️  Chunking text...")
            chunks = self.text_chunker.chunk_text(text, source=file_path.name)
            
            # Generate embeddings
            print(f"  🧠 Generating embeddings...")
            texts = []
            metadatas = []
            embeddings = []
            
            for chunk in chunks:
                if len(chunk['text'].strip()) > 50:  # Only process meaningful chunks
                    texts.append(chunk['text'])
                    metadatas.append(chunk['metadata'])
                    
                    # Generate embedding
                    embedding = self.embedding_gen.generate_query_embedding(chunk['text'])
                    embeddings.append(embedding)
                    
                    if len(embeddings) % 10 == 0:
                        print(f"    Generated {len(embeddings)} embeddings...")
            
            # Add to database
            print(f"  💾 Adding {len(texts)} chunks to database...")
            self.db.add_documents(texts, metadatas, embeddings)
            
            return {
                "filename": file_path.name,
                "chunks_processed": len(texts),
                "status": "success"
            }
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
            return {
                "filename": file_path.name,
                "chunks_processed": 0,
                "status": "error",
                "error": str(e)
            }
    
    def _get_existing_sources(self) -> set:
        """Get list of already processed document sources."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT source FROM documents")
        sources = {row[0] for row in cursor.fetchall()}
        conn.close()
        return sources

if __name__ == "__main__":
    processor = DocumentProcessor()
    result = processor.process_directory()
    
    print(f"\n🎉 Processing complete!")
    print(f"✅ Processed {result['processed_count']} new documents")
    
    # Show updated database stats
    stats = processor.db.get_stats()
    print(f"📊 Database now contains {stats['total_documents']} documents")
    print(f"📚 From {stats['unique_sources']} unique sources")
```

### Tool 2: Document Quality Validator

**Script**: `scripts/data_pipeline/document_validator.py`
```python
#!/usr/bin/env python3
"""
Document Quality Validator
Validates documents before adding to the knowledge base.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import re

class DocumentValidator:
    """Validate documents for quality and relevance."""
    
    def __init__(self):
        """Initialize validator."""
        self.agricultural_keywords = [
            'crop', 'soil', 'plant', 'farming', 'agriculture', 'harvest',
            'seed', 'fertilizer', 'irrigation', 'pest', 'disease', 'yield',
            'groundnut', 'maize', 'beans', 'cassava', 'sweet potato',
            'malawi', 'africa', 'tropical', 'rainfall', 'climate'
        ]
        
    def validate_document(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single document."""
        validation_result = {
            "filename": file_path.name,
            "is_valid": True,
            "issues": [],
            "quality_score": 0,
            "recommendations": []
        }
        
        try:
            # Check file size
            file_size = file_path.stat().st_size
            if file_size < 1000:  # Very small file
                validation_result["issues"].append("File too small (< 1KB)")
                validation_result["quality_score"] -= 20
            elif file_size > 50 * 1024 * 1024:  # Very large file
                validation_result["issues"].append("File very large (> 50MB)")
                validation_result["quality_score"] -= 10
            else:
                validation_result["quality_score"] += 20
            
            # Check filename for agricultural relevance
            filename_lower = file_path.name.lower()
            agricultural_terms_in_name = sum(1 for keyword in self.agricultural_keywords 
                                           if keyword in filename_lower)
            
            if agricultural_terms_in_name > 0:
                validation_result["quality_score"] += 30
            else:
                validation_result["issues"].append("Filename doesn't suggest agricultural content")
                validation_result["quality_score"] -= 10
            
            # Basic content validation (if we can extract text)
            try:
                from scripts.data_pipeline.pdf_processor import PDFProcessor
                pdf_processor = PDFProcessor()
                text = pdf_processor.extract_text(str(file_path))
                
                # Check text length
                if len(text) < 500:
                    validation_result["issues"].append("Very little text content")
                    validation_result["quality_score"] -= 30
                elif len(text) > 10000:
                    validation_result["quality_score"] += 30
                
                # Check for agricultural keywords in content
                text_lower = text.lower()
                agricultural_terms_in_content = sum(1 for keyword in self.agricultural_keywords 
                                                  if keyword in text_lower)
                
                if agricultural_terms_in_content >= 5:
                    validation_result["quality_score"] += 40
                elif agricultural_terms_in_content >= 2:
                    validation_result["quality_score"] += 20
                else:
                    validation_result["issues"].append("Low agricultural content relevance")
                    validation_result["quality_score"] -= 20
                
                # Check for Malawi-specific content
                malawi_terms = ['malawi', 'lilongwe', 'blantyre', 'mzuzu', 'zomba']
                if any(term in text_lower for term in malawi_terms):
                    validation_result["quality_score"] += 20
                    validation_result["recommendations"].append("Contains Malawi-specific content")
                
            except Exception as e:
                validation_result["issues"].append(f"Could not extract text: {e}")
                validation_result["quality_score"] -= 30
            
            # Final validation
            if validation_result["quality_score"] < 30:
                validation_result["is_valid"] = False
                validation_result["recommendations"].append("Quality score too low - review before adding")
            
            return validation_result
            
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Validation error: {e}")
            return validation_result
    
    def validate_directory(self, directory: str = "data/pdfs/") -> List[Dict[str, Any]]:
        """Validate all documents in directory."""
        directory = Path(directory)
        results = []
        
        for pdf_file in directory.glob("*.pdf"):
            result = self.validate_document(pdf_file)
            results.append(result)
        
        return results

if __name__ == "__main__":
    validator = DocumentValidator()
    results = validator.validate_directory()
    
    print("📋 Document Validation Results:")
    print("=" * 50)
    
    for result in results:
        status = "✅ VALID" if result["is_valid"] else "❌ INVALID"
        print(f"{status} - {result['filename']} (Score: {result['quality_score']})")
        
        if result["issues"]:
            for issue in result["issues"]:
                print(f"  ⚠️  {issue}")
        
        if result["recommendations"]:
            for rec in result["recommendations"]:
                print(f"  💡 {rec}")
        
        print()
```

### Tool 3: Database Management Utilities

**Script**: `scripts/data_pipeline/database_manager.py`
```python
#!/usr/bin/env python3
"""
SQLite Vector Database Management Utilities
Tools for managing and maintaining the SQLite vector database.
"""

import sqlite3
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class SQLiteVectorDatabaseManager:
    """Management utilities for SQLite vector database."""
    
    def __init__(self, db_path: str = "data/farming_guide_vectors.db"):
        """Initialize database manager."""
        self.db_path = db_path
    
    def get_detailed_stats(self) -> Dict[str, Any]:
        """Get detailed database statistics."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Basic stats
        cursor.execute("SELECT COUNT(*) as total FROM documents")
        total_docs = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(DISTINCT source) as sources FROM documents")
        unique_sources = cursor.fetchone()['sources']
        
        # Source breakdown
        cursor.execute("SELECT source, COUNT(*) as count FROM documents GROUP BY source ORDER BY count DESC")
        sources_breakdown = [{"source": row['source'], "chunks": row['count']} 
                           for row in cursor.fetchall()]
        
        # Content length analysis
        cursor.execute("SELECT AVG(LENGTH(content)) as avg_length, MIN(LENGTH(content)) as min_length, MAX(LENGTH(content)) as max_length FROM documents")
        content_stats = cursor.fetchone()
        
        # Recent additions
        cursor.execute("SELECT created_at, source, COUNT(*) as count FROM documents GROUP BY DATE(created_at), source ORDER BY created_at DESC LIMIT 10")
        recent_additions = [{"date": row['created_at'], "source": row['source'], "chunks": row['count']} 
                          for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "total_documents": total_docs,
            "unique_sources": unique_sources,
            "sources_breakdown": sources_breakdown,
            "content_statistics": {
                "average_length": int(content_stats['avg_length']) if content_stats['avg_length'] else 0,
                "min_length": content_stats['min_length'] or 0,
                "max_length": content_stats['max_length'] or 0
            },
            "recent_additions": recent_additions
        }
    
    def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents by text content."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple text search
        cursor.execute(
            "SELECT content, source, metadata FROM documents WHERE content LIKE ? LIMIT ?",
            (f"%{query}%", limit)
        )
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "content": row['content'][:200] + "..." if len(row['content']) > 200 else row['content'],
                "source": row['source'],
                "metadata": json.loads(row['metadata']) if row['metadata'] else {}
            })
        
        conn.close()
        return results
    
    def remove_document_source(self, source: str) -> Dict[str, Any]:
        """Remove all chunks from a specific source."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count chunks to be removed
        cursor.execute("SELECT COUNT(*) FROM documents WHERE source = ?", (source,))
        count_to_remove = cursor.fetchone()[0]
        
        if count_to_remove == 0:
            return {"removed": 0, "message": f"No documents found with source: {source}"}
        
        # Remove chunks
        cursor.execute("DELETE FROM documents WHERE source = ?", (source,))
        conn.commit()
        conn.close()
        
        return {"removed": count_to_remove, "message": f"Removed {count_to_remove} chunks from source: {source}"}
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the database."""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/sqlite_backup_{timestamp}.db"
        
        # Create backup directory
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Copy database
        import shutil
        shutil.copy2(self.db_path, backup_path)
        
        return backup_path
    
    def optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get database size before optimization
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        size_before = cursor.fetchone()[0]
        
        # Run optimization commands
        cursor.execute("VACUUM")
        cursor.execute("REINDEX")
        cursor.execute("ANALYZE")
        
        # Get database size after optimization
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        size_after = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "size_before": size_before,
            "size_after": size_after,
            "space_saved": size_before - size_after,
            "optimization_percentage": ((size_before - size_after) / size_before * 100) if size_before > 0 else 0
        }

if __name__ == "__main__":
    manager = SQLiteVectorDatabaseManager()
    
    print("📊 SQLite Vector Database Management")
    print("=" * 40)
    
    # Show detailed stats
    stats = manager.get_detailed_stats()
    print(f"Total Documents: {stats['total_documents']}")
    print(f"Unique Sources: {stats['unique_sources']}")
    print(f"Average Content Length: {stats['content_statistics']['average_length']} characters")
    
    print("\n📚 Sources Breakdown:")
    for source in stats['sources_breakdown']:
        print(f"  {source['source']}: {source['chunks']} chunks")
    
    if stats['recent_additions']:
        print("\n🆕 Recent Additions:")
        for addition in stats['recent_additions']:
            print(f"  {addition['date']}: {addition['source']} ({addition['chunks']} chunks)")
```

## 📋 Step-by-Step Workflow

### Daily/Weekly Document Addition Process

1. **Document Collection**
   ```bash
   # Place new documents in data/pdfs/
   cp ~/Downloads/new_agricultural_guide.pdf data/pdfs/
   ```

2. **Document Validation**
   ```bash
   # Validate document quality
   python scripts/data_pipeline/document_validator.py
   ```

3. **Document Processing**
   ```bash
   # Process new documents
   python scripts/data_pipeline/process_new_documents.py
   ```

4. **Database Verification**
   ```bash
   # Check database stats
   python scripts/data_pipeline/database_manager.py
   ```

5. **Test Search Functionality**
   ```bash
   # Test vector search
   python test_sqlite_vector_db.py
   ```

### Quality Assurance Checklist

**Pre-Processing**:
- [ ] Document is relevant to agriculture/farming
- [ ] Document is in good quality (readable text)
- [ ] Document is from authoritative source
- [ ] Document filename is descriptive

**Post-Processing**:
- [ ] Document successfully chunked (>10 chunks typically)
- [ ] Embeddings generated without errors
- [ ] Database stats updated correctly
- [ ] Search functionality returns relevant results

### Best Practices

1. **Document Naming**: Use descriptive filenames
   ```
   ✅ Good: "Malawi_Groundnut_Production_Guide_2023.pdf"
   ❌ Bad: "document1.pdf"
   ```

2. **Regular Maintenance**:
   - Monthly database optimization
   - Weekly backups
   - Quality audits of new additions

3. **Content Curation**:
   - Remove outdated or low-quality documents
   - Maintain source diversity
   - Focus on Malawi-relevant content

4. **Performance Monitoring**:
   - Monitor database size growth
   - Track search performance
   - Validate embedding quality

## 🛠️ Advanced Features

### Batch Processing for Large Document Sets

```python
# Process multiple documents at once
from scripts.data_pipeline.process_new_documents import DocumentProcessor

processor = DocumentProcessor()
results = processor.process_directory("data/new_pdfs/")
print(f"Processed {results['processed_count']} documents")
```

### Custom Document Types

```python
# Add support for Word documents
from docx import Document

def process_docx(file_path):
    doc = Document(file_path)
    text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    return text
```

### Embedding Management

```python
# Re-generate embeddings for existing documents
def regenerate_embeddings(source_name):
    # Useful when switching embedding models
    pass
```

## 🔧 Troubleshooting

### Common Issues

1. **Large Document Processing**
   - Break into smaller chunks
   - Process in batches
   - Monitor memory usage

2. **Embedding Generation Failures**
   - Check API key validity
   - Verify text quality
   - Handle rate limits

3. **Database Performance**
   - Regular VACUUM operations
   - Monitor database size
   - Consider indexing improvements

### Error Recovery

```python
# Resume failed processing
def resume_processing(failed_documents):
    for doc in failed_documents:
        try:
            process_document(doc)
        except Exception as e:
            log_error(doc, e)
```

## 📈 Monitoring and Analytics

### Database Growth Tracking

```python
# Track database growth over time
def track_growth():
    stats = manager.get_detailed_stats()
    return {
        "timestamp": datetime.now(),
        "total_documents": stats['total_documents'],
        "unique_sources": stats['unique_sources']
    }
```

### Content Quality Metrics

```python
# Analyze content quality
def analyze_content_quality():
    # Check for duplicate content
    # Analyze text quality
    # Identify gaps in coverage
    pass
```

This comprehensive system ensures your SQLite vector database remains high-quality, up-to-date, and optimally organized for the Agricultural Advisor Bot's knowledge base needs. 