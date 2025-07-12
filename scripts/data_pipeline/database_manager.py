#!/usr/bin/env python3
"""
SQLite Vector Database Management Utilities
Tools for managing and maintaining the SQLite vector database.
"""

import sqlite3
import json
import numpy as np
import shutil
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
        if not Path(self.db_path).exists():
            return {
                "error": "Database file does not exist",
                "total_documents": 0,
                "unique_sources": 0,
                "sources_breakdown": [],
                "content_statistics": {"average_length": 0, "min_length": 0, "max_length": 0},
                "recent_additions": []
            }
        
        try:
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
        except Exception as e:
            return {
                "error": str(e),
                "total_documents": 0,
                "unique_sources": 0,
                "sources_breakdown": [],
                "content_statistics": {"average_length": 0, "min_length": 0, "max_length": 0},
                "recent_additions": []
            }
    
    def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents by text content."""
        if not Path(self.db_path).exists():
            return []
        
        try:
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
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def remove_document_source(self, source: str) -> Dict[str, Any]:
        """Remove all chunks from a specific source."""
        if not Path(self.db_path).exists():
            return {"removed": 0, "message": "Database file does not exist"}
        
        try:
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
        except Exception as e:
            return {"removed": 0, "message": f"Error removing documents: {e}"}
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the database."""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database file {self.db_path} does not exist")
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/sqlite_backup_{timestamp}.db"
        
        # Create backup directory
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Copy database
        shutil.copy2(self.db_path, backup_path)
        
        return backup_path
    
    def optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance."""
        if not Path(self.db_path).exists():
            return {"error": "Database file does not exist"}
        
        try:
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
        except Exception as e:
            return {"error": str(e)}
    
    def list_sources(self) -> List[str]:
        """Get list of all document sources."""
        if not Path(self.db_path).exists():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT source FROM documents ORDER BY source")
            sources = [row[0] for row in cursor.fetchall()]
            conn.close()
            return sources
        except Exception as e:
            print(f"Error listing sources: {e}")
            return []
    
    def get_source_stats(self, source: str) -> Dict[str, Any]:
        """Get statistics for a specific source."""
        if not Path(self.db_path).exists():
            return {"error": "Database file does not exist"}
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count, AVG(LENGTH(content)) as avg_length FROM documents WHERE source = ?", (source,))
            stats = cursor.fetchone()
            
            cursor.execute("SELECT content FROM documents WHERE source = ? LIMIT 3", (source,))
            samples = [row['content'][:100] + "..." if len(row['content']) > 100 else row['content'] 
                      for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                "source": source,
                "chunk_count": stats['count'],
                "average_length": int(stats['avg_length']) if stats['avg_length'] else 0,
                "sample_content": samples
            }
        except Exception as e:
            return {"error": str(e)}

def main():
    """Main function for command-line usage."""
    manager = SQLiteVectorDatabaseManager()
    
    print("📊 SQLite Vector Database Management")
    print("=" * 40)
    
    # Show detailed stats
    stats = manager.get_detailed_stats()
    
    if "error" in stats:
        print(f"❌ Error: {stats['error']}")
        return
    
    print(f"📈 Database Statistics:")
    print(f"  Total Documents: {stats['total_documents']}")
    print(f"  Unique Sources: {stats['unique_sources']}")
    print(f"  Average Content Length: {stats['content_statistics']['average_length']} characters")
    print(f"  Min Content Length: {stats['content_statistics']['min_length']} characters")
    print(f"  Max Content Length: {stats['content_statistics']['max_length']} characters")
    
    if stats['sources_breakdown']:
        print(f"\n📚 Sources Breakdown:")
        for source in stats['sources_breakdown']:
            print(f"  {source['source']}: {source['chunks']} chunks")
    
    if stats['recent_additions']:
        print(f"\n🆕 Recent Additions:")
        for addition in stats['recent_additions']:
            print(f"  {addition['date']}: {addition['source']} ({addition['chunks']} chunks)")
    
    # Database health check
    print(f"\n🔍 Database Health Check:")
    file_size = Path(manager.db_path).stat().st_size / (1024 * 1024)  # MB
    print(f"  Database file size: {file_size:.2f} MB")
    
    if file_size > 100:
        print(f"  ⚠️  Database is large - consider optimization")
    else:
        print(f"  ✅ Database size is healthy")

if __name__ == "__main__":
    main() 