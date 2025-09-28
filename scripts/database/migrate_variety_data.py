#!/usr/bin/env python3
"""
Migrate variety data from existing documents to the new varieties table.

This script extracts variety information from the existing documents table
and populates the new varieties table with structured data.
"""

import sqlite3
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the varieties handler for AI parsing
from scripts.handlers.varieties_handler import VarietiesHandler

def migrate_variety_data(db_path="data/agricultural_documents.db", batch_size=50):
    """Migrate variety data from documents to varieties table."""
    
    # Ensure database path is absolute
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
    
    print(f"Migrating variety data from: {db_path}")
    
    # Check if database exists
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Initialize varieties handler for AI parsing
        print("Initializing VarietiesHandler...")
        varieties_handler = VarietiesHandler()
        
        # Get all documents that might contain variety information
        cursor.execute("""
            SELECT id, content, source 
            FROM documents 
            WHERE content LIKE '%variety%' 
               OR content LIKE '%cultivar%' 
               OR content LIKE '%CG%' 
               OR content LIKE '%Chalimbana%'
               OR content LIKE '%Nsinjiro%'
            ORDER BY source
        """)
        
        documents = cursor.fetchall()
        print(f"Found {len(documents)} documents with potential variety information")
        
        # Process documents in batches
        total_varieties = 0
        processed_docs = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
            
            batch_varieties = process_document_batch(cursor, varieties_handler, batch)
            total_varieties += len(batch_varieties)
            processed_docs += len(batch)
            
            print(f"  - Processed {len(batch)} documents, found {len(batch_varieties)} varieties")
        
        print(f"✅ Migration completed: {total_varieties} varieties from {processed_docs} documents")
        
        # Verify migration results
        cursor.execute("SELECT COUNT(*) FROM varieties")
        count = cursor.fetchone()[0]
        print(f"✅ Total varieties in database: {count}")
        
        # Show breakdown by crop
        cursor.execute("SELECT crop_name, COUNT(*) FROM varieties GROUP BY crop_name ORDER BY COUNT(*) DESC")
        crop_counts = cursor.fetchall()
        print("✅ Varieties by crop:")
        for crop, count in crop_counts:
            print(f"  - {crop}: {count} varieties")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        conn.close()

def process_document_batch(cursor, varieties_handler, documents):
    """Process a batch of documents and extract variety information."""
    varieties = []
    
    for doc_id, content, source in documents:
        try:
            # Determine crop name from content or source
            crop_name = extract_crop_name(content, source)
            if not crop_name:
                continue
            
            # Use AI to parse varieties from this document
            # Create a mock search result for the AI parser
            search_result = {
                'content': content,
                'source': source,
                'score': 1.0
            }
            
            # Parse varieties using AI
            parsed_info = varieties_handler.parse_varieties_with_ai([search_result], crop_name, max_varieties=20)
            
            if parsed_info.get('varieties'):
                for variety_data in parsed_info['varieties']:
                    variety = {
                        'crop_name': crop_name,
                        'variety_name': variety_data.get('name', 'Unknown'),
                        'variety_type': extract_variety_type(variety_data.get('name', '')),
                        'yield_potential': variety_data.get('yield', 'Not specified'),
                        'maturity_days': extract_maturity_days(variety_data.get('maturity_days', '')),
                        'weather_requirements': variety_data.get('weather', 'Not specified'),
                        'soil_requirements': variety_data.get('soil', 'Not specified'),
                        'growing_areas': variety_data.get('areas', 'Not specified'),
                        'disease_resistance': variety_data.get('disease_resistance', 'Not specified'),
                        'planting_time': variety_data.get('planting_time', 'Not specified'),
                        'source_document': source
                    }
                    
                    # Insert variety into database
                    insert_variety(cursor, variety)
                    varieties.append(variety)
        
        except Exception as e:
            print(f"  ⚠️  Error processing document {doc_id}: {e}")
            continue
    
    return varieties

def extract_crop_name(content, source):
    """Extract crop name from document content or source."""
    content_lower = content.lower()
    source_lower = source.lower()
    
    # Common crop names to look for
    crops = ['groundnut', 'maize', 'soybean', 'bean', 'rice', 'sorghum', 'millet', 'cassava']
    
    for crop in crops:
        if crop in content_lower or crop in source_lower:
            return crop
    
    # Default to groundnut if no specific crop found
    return 'groundnut'

def extract_variety_type(variety_name):
    """Extract variety type from variety name."""
    name_lower = variety_name.lower()
    
    if 'cg' in name_lower:
        return 'CG Series'
    elif 'chalimbana' in name_lower:
        return 'Chalimbana'
    elif 'nsinjiro' in name_lower:
        return 'Nsinjiro'
    elif 'kakoma' in name_lower:
        return 'Kakoma'
    elif 'chitala' in name_lower:
        return 'Chitala'
    elif 'baka' in name_lower:
        return 'Baka'
    else:
        return 'Other'

def extract_maturity_days(maturity_str):
    """Extract maturity days as integer from string."""
    if not maturity_str or maturity_str == 'Not specified':
        return None
    
    try:
        # Look for numbers in the string
        import re
        numbers = re.findall(r'\d+', str(maturity_str))
        if numbers:
            return int(numbers[0])
    except:
        pass
    
    return None

def insert_variety(cursor, variety):
    """Insert a variety into the database."""
    insert_sql = """
    INSERT INTO varieties (
        crop_name, variety_name, variety_type, yield_potential, maturity_days,
        weather_requirements, soil_requirements, growing_areas, disease_resistance,
        planting_time, source_document
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    cursor.execute(insert_sql, (
        variety['crop_name'],
        variety['variety_name'],
        variety['variety_type'],
        variety['yield_potential'],
        variety['maturity_days'],
        variety['weather_requirements'],
        variety['soil_requirements'],
        variety['growing_areas'],
        variety['disease_resistance'],
        variety['planting_time'],
        variety['source_document']
    ))

def verify_migration(db_path="data/agricultural_documents.db"):
    """Verify that variety data was migrated correctly."""
    
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Test that varieties are populated
        cursor.execute("SELECT COUNT(*) FROM varieties WHERE crop_name = 'groundnut'")
        count = cursor.fetchone()[0]
        assert count >= 5, f"Should have at least 5 groundnut varieties, got {count}"
        
        # Test specific known varieties exist
        known_varieties = ["CG7", "CG8", "CG9", "Nsinjiro", "Chalimbana"]
        found_varieties = []
        
        for variety in known_varieties:
            cursor.execute("SELECT COUNT(*) FROM varieties WHERE crop_name = 'groundnut' AND variety_name LIKE ?", (f"%{variety}%",))
            count = cursor.fetchone()[0]
            if count > 0:
                found_varieties.append(variety)
        
        print(f"✅ Found {len(found_varieties)}/{len(known_varieties)} known varieties: {found_varieties}")
        
        # Test data quality
        cursor.execute("SELECT variety_name, yield_potential FROM varieties WHERE crop_name = 'groundnut' LIMIT 5")
        samples = cursor.fetchall()
        print("✅ Sample varieties:")
        for name, yield_pot in samples:
            print(f"  - {name}: {yield_pot}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate variety data from documents")
    parser.add_argument("--db-path", default="data/agricultural_documents.db", help="Path to database file")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing documents")
    parser.add_argument("--verify-only", action="store_true", help="Only verify migration results")
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_migration(args.db_path)
    else:
        migrate_variety_data(args.db_path, args.batch_size)
        verify_migration(args.db_path)
