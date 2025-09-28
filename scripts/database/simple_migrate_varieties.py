#!/usr/bin/env python3
"""
Simple migration script to populate varieties table from existing documents.
This version avoids complex imports and focuses on basic variety extraction.
"""

import sqlite3
import os
import sys
import re
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def migrate_variety_data(db_path="data/agricultural_documents.db"):
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
        # Get all documents that might contain variety information
        cursor.execute("""
            SELECT id, content, source 
            FROM documents 
            WHERE content LIKE '%variety%' 
               OR content LIKE '%cultivar%' 
               OR content LIKE '%CG%' 
               OR content LIKE '%Chalimbana%'
               OR content LIKE '%Nsinjiro%'
               OR content LIKE '%Kakoma%'
               OR content LIKE '%Chitala%'
               OR content LIKE '%Baka%'
            ORDER BY source
        """)
        
        documents = cursor.fetchall()
        print(f"Found {len(documents)} documents with potential variety information")
        
        # Process documents and extract varieties
        total_varieties = 0
        processed_docs = 0
        
        for doc_id, content, source in documents:
            try:
                # Determine crop name from content or source
                crop_name = extract_crop_name(content, source)
                if not crop_name:
                    continue
                
                # Extract varieties using simple pattern matching
                varieties = extract_varieties_simple(content, crop_name, source)
                
                # Insert varieties into database
                for variety in varieties:
                    insert_variety(cursor, variety)
                    total_varieties += 1
                
                processed_docs += 1
                print(f"  - Processed {source}: found {len(varieties)} varieties")
                
            except Exception as e:
                print(f"  ⚠️  Error processing document {doc_id}: {e}")
                continue
        
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

def extract_varieties_simple(content, crop_name, source):
    """Extract varieties using simple pattern matching."""
    varieties = []
    
    # Known variety patterns
    variety_patterns = [
        r'CG\s*[0-9]+',  # CG7, CG 8, etc.
        r'Chalimbana\s*2005?',  # Chalimbana 2005
        r'Nsinjiro',  # Nsinjiro
        r'Kakoma',  # Kakoma
        r'Chitala',  # Chitala
        r'Baka',  # Baka
    ]
    
    # Find all variety names in content
    found_varieties = set()
    for pattern in variety_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            found_varieties.add(match.strip())
    
    # Create variety records
    for variety_name in found_varieties:
        variety = {
            'crop_name': crop_name,
            'variety_name': variety_name,
            'variety_type': extract_variety_type(variety_name),
            'yield_potential': 'Not specified',
            'maturity_days': None,
            'weather_requirements': 'Not specified',
            'soil_requirements': 'Not specified',
            'growing_areas': 'Not specified',
            'disease_resistance': 'Not specified',
            'planting_time': 'Not specified',
            'source_document': source
        }
        varieties.append(variety)
    
    return varieties

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
        print(f"✅ Groundnut varieties: {count}")
        
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
        cursor.execute("SELECT variety_name, variety_type FROM varieties WHERE crop_name = 'groundnut' LIMIT 10")
        samples = cursor.fetchall()
        print("✅ Sample varieties:")
        for name, variety_type in samples:
            print(f"  - {name} ({variety_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple variety data migration")
    parser.add_argument("--db-path", default="data/agricultural_documents.db", help="Path to database file")
    parser.add_argument("--verify-only", action="store_true", help="Only verify migration results")
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_migration(args.db_path)
    else:
        migrate_variety_data(args.db_path)
        verify_migration(args.db_path)
