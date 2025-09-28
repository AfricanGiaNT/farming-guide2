#!/usr/bin/env python3
"""
AI-powered migration script that uses the existing VarietiesHandler AI parsing
to extract ALL crop varieties from ALL documents comprehensively.
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

def migrate_variety_data_with_ai(db_path="data/agricultural_documents.db"):
    """Migrate variety data using AI parsing for comprehensive extraction."""
    
    # Ensure database path is absolute
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
    
    print(f"AI-powered migration from: {db_path}")
    
    # Check if database exists
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Import the varieties handler for AI parsing
        # We'll import here to avoid the PyPDF2 import issues
        sys.path.append(str(project_root))
        os.environ['OPENAI_API_KEY'] = get_openai_key()
        
        from scripts.handlers.varieties_handler import VarietiesHandler
        varieties_handler = VarietiesHandler()
        print("✅ VarietiesHandler initialized")
        
        # Clear existing varieties to start fresh
        cursor.execute("DELETE FROM varieties")
        print("✅ Cleared existing varieties table")
        
        # Get documents grouped by source to avoid processing same doc multiple times
        cursor.execute("""
            SELECT source, GROUP_CONCAT(content, ' ') as combined_content
            FROM documents 
            GROUP BY source
            ORDER BY source
        """)
        
        all_documents = cursor.fetchall()
        print(f"Found {len(all_documents)} documents to analyze")
        
        # Process each document with AI to determine crops and extract varieties
        total_varieties = 0
        all_varieties_set = set()  # Track unique varieties
        
        for source, combined_content in all_documents:
            try:
                print(f"\n📄 Processing: {source}")
                
                # Determine what crops this document covers
                crops_in_doc = identify_crops_with_ai(combined_content, source, varieties_handler)
                print(f"  🌱 Detected crops: {crops_in_doc}")
                
                # For each crop, extract varieties using AI
                for crop_name in crops_in_doc:
                    print(f"  🔍 Extracting {crop_name} varieties...")
                    
                    # Create search results format for AI parser
                    search_results = [{
                        'content': combined_content,
                        'source': source,
                        'score': 1.0
                    }]
                    
                    # Use AI to parse varieties for this crop
                    parsed_info = varieties_handler.parse_varieties_with_ai(
                        search_results, crop_name, max_varieties=50
                    )
                    
                    if parsed_info.get('varieties'):
                        doc_varieties = 0
                        for variety_data in parsed_info['varieties']:
                            variety_name = variety_data.get('name', 'Unknown')
                            
                            # Create unique key to avoid duplicates
                            variety_key = (crop_name.lower(), variety_name.lower().strip())
                            
                            if variety_key not in all_varieties_set and variety_name != 'Unknown':
                                all_varieties_set.add(variety_key)
                                
                                variety = create_variety_record(variety_data, crop_name, source)
                                insert_variety(cursor, variety)
                                total_varieties += 1
                                doc_varieties += 1
                        
                        print(f"    ✅ Found {doc_varieties} unique {crop_name} varieties")
                    else:
                        print(f"    ⚠️  No {crop_name} varieties found")
                        
            except Exception as e:
                print(f"  ❌ Error processing {source}: {e}")
                continue
        
        print(f"\n✅ Migration completed: {total_varieties} unique varieties")
        
        # Commit changes
        conn.commit()
        
        # Verify results
        verify_comprehensive_migration(cursor)
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        conn.close()

def identify_crops_with_ai(content, source, varieties_handler):
    """Use AI to identify what crops are covered in this document."""
    
    # Simple heuristic first - check document title/source
    source_lower = source.lower()
    content_preview = content[:2000].lower()  # First 2000 chars
    
    crops = []
    
    # Check for obvious crop indicators in filename and content
    crop_indicators = {
        'groundnut': ['groundnut', 'peanut', 'arachis'],
        'maize': ['maize', 'corn', 'zea mays'],
        'soybean': ['soybean', 'soya', 'glycine max'],
        'bean': ['bean', 'phaseolus', 'common bean'],
        'rice': ['rice', 'oryza'],
        'sorghum': ['sorghum', 'grain sorghum'],
        'millet': ['millet', 'pearl millet'],
        'cassava': ['cassava', 'manioc'],
        'sweet_potato': ['sweet potato', 'ipomoea'],
        'cowpea': ['cowpea', 'vigna'],
        'pigeon_pea': ['pigeon pea', 'cajanus']
    }
    
    for crop, indicators in crop_indicators.items():
        score = 0
        for indicator in indicators:
            score += source_lower.count(indicator) * 2  # Filename gets higher weight
            score += content_preview.count(indicator)
        
        if score > 0:
            crops.append(crop)
    
    # If no crops detected, try to use AI to identify
    if not crops:
        # Create a simple search result for AI analysis
        search_results = [{
            'content': content[:3000],  # Use first 3000 chars
            'source': source,
            'score': 1.0
        }]
        
        # Try with generic "crop" to see what AI finds
        try:
            parsed_info = varieties_handler.parse_varieties_with_ai(
                search_results, "crop", max_varieties=10
            )
            if parsed_info.get('varieties'):
                crops.append('mixed')  # Generic category
        except:
            pass
    
    # Default to at least one crop if nothing found
    if not crops:
        crops = ['mixed']
    
    return crops

def create_variety_record(variety_data, crop_name, source):
    """Create a variety record from AI-parsed data."""
    return {
        'crop_name': crop_name,
        'variety_name': variety_data.get('name', 'Unknown'),
        'variety_type': extract_variety_type(variety_data.get('name', ''), crop_name),
        'yield_potential': variety_data.get('yield', variety_data.get('yield_potential', 'Not specified')),
        'maturity_days': extract_maturity_days(variety_data.get('maturity_days', '')),
        'weather_requirements': variety_data.get('weather', variety_data.get('weather_requirements', 'Not specified')),
        'soil_requirements': variety_data.get('soil', variety_data.get('soil_requirements', 'Not specified')),
        'growing_areas': variety_data.get('areas', variety_data.get('growing_areas', 'Not specified')),
        'disease_resistance': variety_data.get('disease_resistance', 'Not specified'),
        'planting_time': variety_data.get('planting_time', 'Not specified'),
        'source_document': source
    }

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
        if 'sc' in name_lower or 'single cross' in name_lower:
            return 'Single Cross'
        elif 'dk' in name_lower:
            return 'DK Series'
        elif 'pan' in name_lower:
            return 'PAN Series'
        elif 'pioneer' in name_lower:
            return 'Pioneer'
        elif 'hybrid' in name_lower:
            return 'Hybrid'
    elif crop_name == 'soybean':
        if 'tikolore' in name_lower:
            return 'Tikolore'
        elif 'magoye' in name_lower:
            return 'Magoye'
        elif name_lower.startswith('tgx'):
            return 'TGX Series'
    
    return 'Other'

def extract_maturity_days(maturity_str):
    """Extract maturity days as integer from string."""
    if not maturity_str or maturity_str == 'Not specified':
        return None
    
    try:
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

def verify_comprehensive_migration(cursor):
    """Verify the comprehensive migration results."""
    
    # Total varieties
    cursor.execute("SELECT COUNT(*) FROM varieties")
    total_count = cursor.fetchone()[0]
    print(f"\n✅ Total varieties: {total_count}")
    
    # Breakdown by crop
    cursor.execute("SELECT crop_name, COUNT(*) FROM varieties GROUP BY crop_name ORDER BY COUNT(*) DESC")
    crop_counts = cursor.fetchall()
    print("✅ Varieties by crop:")
    for crop, count in crop_counts:
        print(f"  - {crop}: {count} varieties")
    
    # Sample varieties for each crop
    print("\n✅ Sample varieties by crop:")
    for crop, _ in crop_counts[:5]:  # Top 5 crops
        cursor.execute("SELECT variety_name FROM varieties WHERE crop_name = ? LIMIT 5", (crop,))
        samples = [row[0] for row in cursor.fetchall()]
        print(f"  - {crop}: {', '.join(samples)}")
    
    # Check for duplicates
    cursor.execute("""
        SELECT crop_name, variety_name, COUNT(*) 
        FROM varieties 
        GROUP BY crop_name, variety_name 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"⚠️  Found {len(duplicates)} duplicate varieties")
    else:
        print("✅ No duplicate varieties found")

def get_openai_key():
    """Get OpenAI API key from config file."""
    try:
        config_path = os.path.join(project_root, 'config', 'openai_key.env')
        with open(config_path, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    
    # Try environment variable
    return os.environ.get('OPENAI_API_KEY', '')

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-powered comprehensive variety migration")
    parser.add_argument("--db-path", default="data/agricultural_documents.db", help="Path to database file")
    
    args = parser.parse_args()
    
    migrate_variety_data_with_ai(args.db_path)
