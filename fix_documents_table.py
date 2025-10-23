#!/usr/bin/env python3
"""
Fix the missing 'documents' table in the SQLite database
This script creates the documents table if it doesn't exist
"""

import sqlite3
import os
import sys

def create_documents_table():
    """Create the documents table if it doesn't exist"""
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Connect to the database
        conn = sqlite3.connect('data/agricultural_documents.db')
        cursor = conn.cursor()
        
        # Check if documents table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating documents table...")
            
            # Create the documents table
            cursor.execute('''
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                metadata TEXT,
                embedding BLOB,
                source_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            ''')
            
            print("Documents table created successfully!")
        else:
            print("Documents table already exists.")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error creating documents table: {e}")
        return False

def check_database_structure():
    """Check the database structure after fixing"""
    try:
        conn = sqlite3.connect('data/agricultural_documents.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nDatabase tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check documents table structure
        print("\nDocuments table structure:")
        cursor.execute("PRAGMA table_info(documents);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error checking database structure: {e}")
        return False

if __name__ == "__main__":
    print("Fixing documents table in SQLite database...")
    success = create_documents_table()
    
    if success:
        check_database_structure()
        print("\nDatabase fix completed successfully!")
        sys.exit(0)
    else:
        print("\nFailed to fix database.")
        sys.exit(1)
