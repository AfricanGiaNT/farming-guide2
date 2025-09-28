#!/usr/bin/env python3
"""
Comprehensive variety extraction using the working API endpoint.
This approach uses the existing, working API to systematically extract varieties
for all crops from all documents.
"""

import sqlite3
import os
import sys
import json
import requests
import time
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

API_BASE_URL = "http://localhost:8000"

def comprehensive_variety_extraction(db_path="data/agricultural_documents.db"):
    """Extract varieties comprehensively using the working API."""
    
    # Ensure database path is absolute
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
    
    print(f"🚀 Comprehensive variety extraction from: {db_path}")
    
    # Check if API is running
    if not check_api_health():
        print("❌ API is not running. Please start the API server first.")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear existing varieties
        cursor.execute("DELETE FROM varieties")
        print("✅ Cleared existing varieties table")
        
        # Get all unique document sources
        cursor.execute("SELECT DISTINCT source FROM documents ORDER BY source")
        document_sources = [row[0] for row in cursor.fetchall()]
        print(f"📚 Found {len(document_sources)} documents to process")
        
        # Define all crops to try extracting
        crops_to_extract = [
            'groundnut', 'maize', 'soybean', 'bean', 'rice', 'sorghum', 
            'millet', 'cassava', 'sweet_potato', 'cowpea', 'pigeon_pea',
            'tobacco', 'cotton', 'sunflower', 'sesame'
        ]
        
        total_varieties = 0
        all_varieties_found = {}  # Track varieties by crop
        
        # Process each crop systematically
        for crop in crops_to_extract:
            print(f"\n🌱 Extracting {crop} varieties...")
            
            # Use the API to get varieties for this crop
            varieties_data = get_varieties_from_api(crop, limit=50)
            
            if varieties_data and varieties_data.get('varieties'):
                crop_varieties = varieties_data['varieties']
                print(f"  📊 API returned {len(crop_varieties)} {crop} varieties")
                
                # Process each variety
                unique_varieties = set()
                for variety_data in crop_varieties:
                    variety_name = variety_data.get('name', 'Unknown')
                    
                    # Skip generic names
                    if is_valid_variety_name(variety_name):
                        variety_key = variety_name.lower().strip()
                        
                        if variety_key not in unique_varieties:
                            unique_varieties.add(variety_key)
                            
                            # Insert into database
                            variety_record = create_variety_record_from_api(variety_data, crop)
                            insert_variety(cursor, variety_record)
                            total_varieties += 1
                
                if unique_varieties:
                    all_varieties_found[crop] = len(unique_varieties)
                    print(f"  ✅ Added {len(unique_varieties)} unique {crop} varieties")
                else:
                    print(f"  ⚠️  No valid {crop} varieties found")
            else:
                print(f"  ⚠️  No {crop} varieties returned by API")
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        print(f"\n🎉 Extraction completed: {total_varieties} total varieties")
        print("📊 Varieties found by crop:")
        for crop, count in all_varieties_found.items():
            print(f"  - {crop}: {count} varieties")
        
        # Commit changes
        conn.commit()
        
        # Verify results
        verify_extraction_results(cursor)
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

def check_api_health():
    """Check if the API is running and healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            return health_data.get('status') == 'healthy' and health_data.get('components', {}).get('varieties_handler', False)
        return False
    except:
        return False

def get_varieties_from_api(crop_name, limit=50):
    """Get varieties for a specific crop from the API."""
    try:
        url = f"{API_BASE_URL}/api/varieties/{crop_name}?limit={limit}"
        response = requests.get(url, timeout=30)  # Longer timeout for AI processing
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"    ⚠️  API returned status {response.status_code} for {crop_name}")
            return None
    except Exception as e:
        print(f"    ❌ Error calling API for {crop_name}: {e}")
        return None

def is_valid_variety_name(name):
    """Check if a variety name is valid (not generic)."""
    if not name or name == 'Unknown':
        return False
    
    name_lower = name.lower().strip()
    
    # Skip generic terms
    generic_terms = [
        'unknown', 'variety', 'cultivar', 'hybrid', 'type', 'strain',
        'not specified', 'local variety', 'improved variety', 'open pollinated',
        'traditional', 'landrace', 'selection', 'population'
    ]
    
    if name_lower in generic_terms:
        return False
    
    # Must be at least 2 characters
    if len(name_lower) < 2:
        return False
    
    return True

def create_variety_record_from_api(variety_data, crop_name):
    """Create a variety record from API response data."""
    return {
        'crop_name': crop_name,
        'variety_name': variety_data.get('name', 'Unknown'),
        'variety_type': determine_variety_type(variety_data.get('name', ''), crop_name),
        'yield_potential': variety_data.get('yield_potential', 'Not specified'),
        'maturity_days': parse_maturity_days(variety_data.get('maturity_days')),
        'weather_requirements': variety_data.get('weather_requirements', 'Not specified'),
        'soil_requirements': variety_data.get('soil_requirements', 'Not specified'),
        'growing_areas': variety_data.get('growing_areas', 'Not specified'),
        'disease_resistance': variety_data.get('disease_resistance', 'Not specified'),
        'planting_time': variety_data.get('planting_time', 'Not specified'),
        'source_document': 'Multiple sources (API extraction)'
    }

def determine_variety_type(variety_name, crop_name):
    """Determine variety type based on name and crop."""
    name_lower = variety_name.lower()
    
    type_patterns = {
        'groundnut': {
            'CG Series': ['cg'],
            'Chalimbana': ['chalimbana'],
            'Nsinjiro': ['nsinjiro'],
            'Kakoma': ['kakoma'],
            'Chitala': ['chitala'],
            'Baka': ['baka']
        },
        'maize': {
            'Single Cross': ['sc', 'single cross'],
            'DK Series': ['dk'],
            'PAN Series': ['pan'],
            'Pioneer': ['pioneer'],
            'Hybrid': ['hybrid']
        },
        'soybean': {
            'TGX Series': ['tgx'],
            'Tikolore': ['tikolore'],
            'Magoye': ['magoye']
        }
    }
    
    if crop_name in type_patterns:
        for variety_type, patterns in type_patterns[crop_name].items():
            if any(pattern in name_lower for pattern in patterns):
                return variety_type
    
    return 'Other'

def parse_maturity_days(maturity_value):
    """Parse maturity days from various formats."""
    if not maturity_value:
        return None
    
    try:
        # If it's already an integer
        if isinstance(maturity_value, int):
            return maturity_value
        
        # Extract numbers from string
        import re
        numbers = re.findall(r'\d+', str(maturity_value))
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

def verify_extraction_results(cursor):
    """Verify the extraction results."""
    
    # Total varieties
    cursor.execute("SELECT COUNT(*) FROM varieties")
    total_count = cursor.fetchone()[0]
    print(f"\n✅ Total varieties in database: {total_count}")
    
    # Breakdown by crop
    cursor.execute("SELECT crop_name, COUNT(*) FROM varieties GROUP BY crop_name ORDER BY COUNT(*) DESC")
    crop_counts = cursor.fetchall()
    print("✅ Final varieties by crop:")
    for crop, count in crop_counts:
        print(f"  - {crop}: {count} varieties")
    
    # Sample varieties for top crops
    print("\n✅ Sample varieties:")
    for crop, count in crop_counts[:3]:  # Top 3 crops
        cursor.execute("SELECT variety_name FROM varieties WHERE crop_name = ? ORDER BY variety_name LIMIT 5", (crop,))
        samples = [row[0] for row in cursor.fetchall()]
        print(f"  - {crop}: {', '.join(samples)}")
    
    # Check for duplicates
    cursor.execute("""
        SELECT crop_name, variety_name, COUNT(*) 
        FROM varieties 
        GROUP BY crop_name, variety_name 
        HAVING COUNT(*) > 1
        LIMIT 5
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"⚠️  Found duplicate varieties (showing first 5):")
        for crop, variety, count in duplicates:
            print(f"  - {crop}: {variety} ({count} times)")
    else:
        print("✅ No duplicate varieties found")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive variety extraction using API")
    parser.add_argument("--db-path", default="data/agricultural_documents.db", help="Path to database file")
    
    args = parser.parse_args()
    
    success = comprehensive_variety_extraction(args.db_path)
    if success:
        print("\n🎉 Comprehensive variety extraction completed successfully!")
    else:
        print("\n❌ Variety extraction failed. Check the logs above.")
        sys.exit(1)
