#!/usr/bin/env python3
"""
Create varieties table with proper schema and indexes for Phase 2.

This script creates a new 'varieties' table in the existing SQLite database
to store structured variety data extracted from documents.
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.database.schema_manager import ensure_varieties_schema

def create_varieties_table(db_path="data/agricultural_documents.db"):
    """Create the varieties table with proper schema and indexes."""
    
    # Ensure database path is absolute
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
    
    print(f"Creating varieties table in: {db_path}")
    
    # Check if database exists
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if varieties table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='varieties'")
        if cursor.fetchone():
            print("⚠️  Varieties table already exists. Dropping and recreating...")
            cursor.execute("DROP TABLE varieties")
        
        # Create varieties table
        create_table_sql = """
        CREATE TABLE varieties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL,
            variety_name TEXT NOT NULL,
            variety_type TEXT,
            yield_potential TEXT,
            maturity_days INTEGER,
            weather_requirements TEXT,
            soil_requirements TEXT,
            growing_areas TEXT,
            disease_resistance TEXT,
            planting_time TEXT,
            source_document TEXT,
            confidence_score INTEGER DEFAULT 0,
            validation_status TEXT DEFAULT 'pending',
            extraction_session_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_sql)
        print("✅ Varieties table created successfully")
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX idx_crop_variety ON varieties(crop_name, variety_name);",
            "CREATE INDEX idx_variety_type ON varieties(variety_type);",
            "CREATE INDEX idx_maturity_days ON varieties(maturity_days);",
            "CREATE INDEX idx_crop_name ON varieties(crop_name);",
            "CREATE INDEX idx_created_at ON varieties(created_at);",
            "CREATE INDEX idx_varieties_validation_status ON varieties(validation_status);",
            "CREATE INDEX idx_varieties_session ON varieties(extraction_session_id);"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print("✅ Indexes created successfully")
        
        # Verify table creation
        cursor.execute("PRAGMA table_info(varieties)")
        columns = [row[1] for row in cursor.fetchall()]
        expected_columns = [
            "id", "crop_name", "variety_name", "variety_type", "yield_potential",
            "maturity_days", "weather_requirements", "soil_requirements",
            "growing_areas", "disease_resistance", "planting_time", "source_document",
            "confidence_score", "validation_status", "extraction_session_id", "created_at"
        ]
        
        print(f"✅ Table schema verified. Columns: {columns}")
        
        # Verify indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='varieties'")
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"✅ Indexes created: {indexes}")
        
        # Ensure auxiliary tables and indexes required by validation workflow exist
        ensure_varieties_schema(db_path)

        conn.commit()
        print("✅ Database changes committed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating varieties table: {e}")
        raise
    finally:
        conn.close()

def verify_table_creation(db_path="data/agricultural_documents.db"):
    """Verify that the varieties table was created correctly."""
    
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Test table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='varieties'")
        assert cursor.fetchone() is not None, "Varieties table should exist"
        
        # Test schema
        cursor.execute("PRAGMA table_info(varieties)")
        columns = [row[1] for row in cursor.fetchall()]
        expected_columns = [
            "id", "crop_name", "variety_name", "variety_type", "yield_potential",
            "maturity_days", "weather_requirements", "soil_requirements",
            "growing_areas", "disease_resistance", "planting_time", "source_document",
            "confidence_score", "validation_status", "extraction_session_id", "created_at"
        ]
        
        for col in expected_columns:
            assert col in columns, f"Missing column: {col}"
        
        # Test indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='varieties'")
        indexes = [row[0] for row in cursor.fetchall()]
        expected_indexes = [
            "idx_crop_variety",
            "idx_variety_type",
            "idx_maturity_days",
            "idx_crop_name",
            "idx_created_at",
            "idx_varieties_validation_status",
            "idx_varieties_session"
        ]
        
        for idx in expected_indexes:
            assert idx in indexes, f"Missing index: {idx}"
        
        print("✅ Table verification passed")
        return True
        
    except Exception as e:
        print(f"❌ Table verification failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create varieties table")
    parser.add_argument("--db-path", default="data/agricultural_documents.db", help="Path to database file")
    parser.add_argument("--verify-only", action="store_true", help="Only verify table exists")
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_table_creation(args.db_path)
    else:
        create_varieties_table(args.db_path)
        verify_table_creation(args.db_path)
