#!/usr/bin/env python3
"""
Fixed migration script to properly populate varieties table from existing documents.
This version fixes duplicate entries and improves crop detection.
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
        # Clear existing varieties to avoid duplicates
        cursor.execute("DELETE FROM varieties")
        print("✅ Cleared existing varieties table")
        
        # Get all documents grouped by source to avoid duplicates
        cursor.execute("""
            SELECT source, GROUP_CONCAT(content, ' ') as combined_content
            FROM documents 
            WHERE content LIKE '%variety%' 
               OR content LIKE '%cultivar%' 
               OR content LIKE '%CG%' 
               OR content LIKE '%Chalimbana%'
               OR content LIKE '%Nsinjiro%'
               OR content LIKE '%Kakoma%'
               OR content LIKE '%Chitala%'
               OR content LIKE '%Baka%'
               OR content LIKE '%maize%'
               OR content LIKE '%soybean%'
               OR content LIKE '%bean%'
            GROUP BY source
            ORDER BY source
        """)
        
        documents = cursor.fetchall()
        print(f"Found {len(documents)} documents with potential variety information")
        
        # Process documents and extract varieties
        total_varieties = 0
        processed_docs = 0
        all_varieties = set()  # Use set to track unique varieties
        
        for source, content in documents:
            try:
                # Determine crop name from content or source
                crop_name = extract_crop_name(content, source)
                if not crop_name:
                    continue
                
                # Extract varieties using improved pattern matching
                varieties = extract_varieties_improved(content, crop_name, source)
                
                # Filter out duplicates and add to set
                for variety in varieties:
                    variety_key = (crop_name, variety['variety_name'])
                    if variety_key not in all_varieties:
                        all_varieties.add(variety_key)
                        insert_variety(cursor, variety)
                        total_varieties += 1
                
                processed_docs += 1
                print(f"  - Processed {source}: found {len(varieties)} varieties for {crop_name}")
                
            except Exception as e:
                print(f"  ⚠️  Error processing document {source}: {e}")
                continue
        
        print(f"✅ Migration completed: {total_varieties} unique varieties from {processed_docs} documents")
        
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
    """Extract crop name from document content or source with improved detection."""
    content_lower = content.lower()
    source_lower = source.lower()
    
    # More comprehensive crop detection
    crop_keywords = {
        'groundnut': ['groundnut', 'peanut', 'arachis', 'nut'],
        'maize': ['maize', 'corn', 'zea mays', 'grain'],
        'soybean': ['soybean', 'soya', 'glycine max', 'soy'],
        'bean': ['bean', 'phaseolus', 'common bean', 'kidney bean'],
        'rice': ['rice', 'oryza', 'paddy'],
        'sorghum': ['sorghum', 'millet', 'sorghum bicolor'],
        'cassava': ['cassava', 'manioc', 'manihot'],
        'sweet_potato': ['sweet potato', 'ipomoea', 'kumara']
    }
    
    # Count keyword matches for each crop
    crop_scores = {}
    for crop, keywords in crop_keywords.items():
        score = 0
        for keyword in keywords:
            score += content_lower.count(keyword) + source_lower.count(keyword)
        crop_scores[crop] = score
    
    # Return crop with highest score, or default to groundnut
    if crop_scores:
        best_crop = max(crop_scores, key=crop_scores.get)
        if crop_scores[best_crop] > 0:
            return best_crop
    
    return 'groundnut'

def extract_varieties_improved(content, crop_name, source):
    """Extract varieties using improved pattern matching for different crops."""
    varieties = []
    
    # Crop-specific variety patterns
    variety_patterns = {
        'groundnut': [
            r'CG\s*[0-9]+',  # CG7, CG 8, etc.
            r'Chalimbana\s*2005?',  # Chalimbana 2005
            r'Nsinjiro',  # Nsinjiro
            r'Kakoma',  # Kakoma
            r'Chitala',  # Chitala
            r'Baka',  # Baka
        ],
        'maize': [
            r'SC\s*[0-9]+',  # SC varieties
            r'MH\s*[0-9]+',  # MH varieties
            r'DK\s*[0-9]+',  # DK varieties
            r'PAN\s*[0-9]+',  # PAN varieties
            r'ZP\s*[0-9]+',  # ZP varieties
            r'Pioneer\s*[0-9]+',  # Pioneer varieties
            r'Hybrid\s*[0-9]+',  # Hybrid varieties
        ],
        'soybean': [
            r'TG\s*[0-9]+',  # TG varieties
            r'SC\s*[0-9]+',  # SC varieties
            r'Pioneer\s*[0-9]+',  # Pioneer varieties
            r'Hybrid\s*[0-9]+',  # Hybrid varieties
        ],
        'bean': [
            r'GLP\s*[0-9]+',  # GLP varieties
            r'SC\s*[0-9]+',  # SC varieties
            r'PAN\s*[0-9]+',  # PAN varieties
        ]
    }
    
    # Get patterns for this crop
    patterns = variety_patterns.get(crop_name, variety_patterns['groundnut'])
    
    # Find all variety names in content
    found_varieties = set()
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            # Clean up the variety name
            clean_name = re.sub(r'\s+', ' ', match.strip())
            found_varieties.add(clean_name)
    
    # Create variety records
    for variety_name in found_varieties:
        variety = {
            'crop_name': crop_name,
            'variety_name': variety_name,
            'variety_type': extract_variety_type(variety_name, crop_name),
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

def extract_variety_type(variety_name, crop_name):
    """Extract variety type from variety name and crop."""
    name_lower = variety_name.lower()
    
    if crop_name == 'groundnut':
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
    elif crop_name == 'maize':
        if 'sc' in name_lower:
            return 'SC Series'
        elif 'mh' in name_lower:
            return 'MH Series'
        elif 'dk' in name_lower:
            return 'DK Series'
        elif 'pan' in name_lower:
            return 'PAN Series'
        elif 'pioneer' in name_lower:
            return 'Pioneer'
        elif 'hybrid' in name_lower:
            return 'Hybrid'
    elif crop_name == 'soybean':
        if 'tg' in name_lower:
            return 'TG Series'
        elif 'sc' in name_lower:
            return 'SC Series'
        elif 'pioneer' in name_lower:
            return 'Pioneer'
        elif 'hybrid' in name_lower:
            return 'Hybrid'
    elif crop_name == 'bean':
        if 'glp' in name_lower:
            return 'GLP Series'
        elif 'sc' in name_lower:
            return 'SC Series'
        elif 'pan' in name_lower:
            return 'PAN Series'
    
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
        cursor.execute("SELECT COUNT(*) FROM varieties")
        total_count = cursor.fetchone()[0]
        print(f"✅ Total varieties: {total_count}")
        
        # Show breakdown by crop
        cursor.execute("SELECT crop_name, COUNT(*) FROM varieties GROUP BY crop_name ORDER BY COUNT(*) DESC")
        crop_counts = cursor.fetchall()
        print("✅ Varieties by crop:")
        for crop, count in crop_counts:
            print(f"  - {crop}: {count} varieties")
        
        # Test for duplicates
        cursor.execute("SELECT crop_name, variety_name, COUNT(*) FROM varieties GROUP BY crop_name, variety_name HAVING COUNT(*) > 1")
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} duplicate varieties:")
            for crop, variety, count in duplicates[:5]:  # Show first 5
                print(f"  - {crop}: {variety} ({count} times)")
        else:
            print("✅ No duplicate varieties found")
        
        # Test specific known varieties exist
        known_varieties = ["CG7", "CG8", "CG9", "Nsinjiro", "Chalimbana"]
        found_varieties = []
        
        for variety in known_varieties:
            cursor.execute("SELECT COUNT(*) FROM varieties WHERE crop_name = 'groundnut' AND variety_name LIKE ?", (f"%{variety}%",))
            count = cursor.fetchone()[0]
            if count > 0:
                found_varieties.append(variety)
        
        print(f"✅ Found {len(found_varieties)}/{len(known_varieties)} known groundnut varieties: {found_varieties}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fixed variety data migration")
    parser.add_argument("--db-path", default="data/agricultural_documents.db", help="Path to database file")
    parser.add_argument("--verify-only", action="store_true", help="Only verify migration results")
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_migration(args.db_path)
    else:
        migrate_variety_data(args.db_path)
        verify_migration(args.db_path)
