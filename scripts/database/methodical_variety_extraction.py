#!/usr/bin/env python3
"""
Methodical variety extraction that processes documents chunk by chunk,
validates crop associations, and ensures data quality.
"""

import sqlite3
import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def methodical_variety_extraction(db_path="data/agricultural_documents.db"):
    """Extract varieties methodically with quality checks."""
    
    # Ensure database path is absolute
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
    
    print(f"🔍 Starting methodical variety extraction from: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear existing varieties to start fresh
        cursor.execute("DELETE FROM varieties")
        print("✅ Cleared existing varieties table")
        
        # Track all varieties we've found to avoid duplicates
        found_varieties: Set[Tuple[str, str]] = set()  # (crop_name, variety_name)
        
        # Get all documents one by one
        cursor.execute("SELECT DISTINCT source FROM documents ORDER BY source")
        document_sources = [row[0] for row in cursor.fetchall()]
        print(f"📚 Processing {len(document_sources)} documents individually")
        
        total_varieties = 0
        
        for doc_idx, source in enumerate(document_sources, 1):
            print(f"\n📄 Document {doc_idx}/{len(document_sources)}: {source}")
            
            # Get all chunks for this document
            cursor.execute("SELECT content FROM documents WHERE source = ? ORDER BY id", (source,))
            document_chunks = [row[0] for row in cursor.fetchall()]
            print(f"  📝 Processing {len(document_chunks)} chunks")
            
            # Determine what crops this document is about
            document_crops = identify_document_crops(document_chunks, source)
            if not document_crops:
                print("  ⚠️  No clear crop focus found, skipping document")
                continue
            
            print(f"  🌱 Document focuses on: {', '.join(document_crops)}")
            
            # Process each chunk for each identified crop
            doc_varieties = 0
            for crop in document_crops:
                print(f"    🔍 Extracting {crop} varieties...")
                
                crop_varieties = extract_varieties_for_crop(document_chunks, crop, source)
                
                # Validate and insert varieties
                for variety_data in crop_varieties:
                    variety_key = (crop, variety_data['variety_name'].lower().strip())
                    
                    if variety_key not in found_varieties:
                        if validate_variety_crop_association(variety_data, crop, document_chunks):
                            found_varieties.add(variety_key)
                            insert_variety(cursor, variety_data)
                            doc_varieties += 1
                            total_varieties += 1
                            print(f"      ✅ Added: {variety_data['variety_name']}")
                        else:
                            print(f"      ❌ Invalid crop association: {variety_data['variety_name']} for {crop}")
                    else:
                        print(f"      ⚠️  Duplicate skipped: {variety_data['variety_name']}")
            
            print(f"  📊 Added {doc_varieties} varieties from this document")
        
        print(f"\n🎉 Methodical extraction completed: {total_varieties} unique, validated varieties")
        
        # Commit changes
        conn.commit()
        
        # Final verification
        verify_extraction_quality(cursor)
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

def identify_document_crops(chunks: List[str], source: str) -> List[str]:
    """Identify what crops a document is actually about."""
    
    # Combine all chunks for analysis
    full_content = " ".join(chunks).lower()
    source_lower = source.lower()
    
    # Crop indicators with stronger patterns
    crop_patterns = {
        'groundnut': {
            'keywords': ['groundnut', 'peanut', 'arachis'],
            'strong_indicators': ['groundnut production', 'groundnut varieties', 'groundnut guide'],
            'variety_patterns': [r'cg\s*[0-9]+', r'chalimbana', r'nsinjiro', r'kakoma', r'chitala', r'baka']
        },
        'maize': {
            'keywords': ['maize', 'corn', 'zea mays'],
            'strong_indicators': ['maize production', 'maize varieties', 'maize guide', 'maize growers'],
            'variety_patterns': [r'sc\s*[0-9]+', r'dk\s*[0-9]+', r'pan\s*[0-9]+', r'pioneer', r'hybrid']
        },
        'soybean': {
            'keywords': ['soybean', 'soya', 'glycine max'],
            'strong_indicators': ['soybean production', 'soybean varieties', 'soybean guide'],
            'variety_patterns': [r'tgx\s*[0-9]+', r'tikolore', r'magoye']
        },
        'bean': {
            'keywords': ['bean', 'phaseolus', 'common bean'],
            'strong_indicators': ['bean production', 'bean varieties', 'bean farmers'],
            'variety_patterns': [r'glp\s*[0-9]+', r'rosecoco', r'canadian wonder']
        },
        'rice': {
            'keywords': ['rice', 'oryza', 'paddy'],
            'strong_indicators': ['rice production', 'rice varieties'],
            'variety_patterns': [r'nerica\s*[0-9]+', r'wita\s*[0-9]+', r'kilombero']
        },
        'cassava': {
            'keywords': ['cassava', 'manioc', 'manihot'],
            'strong_indicators': ['cassava production', 'cassava varieties'],
            'variety_patterns': [r'sauti', r'kanyama', r'chitembwere']
        },
        'tomato': {
            'keywords': ['tomato', 'lycopersicon', 'solanum lycopersicum'],
            'strong_indicators': ['tomato production', 'tomato varieties', 'tomato farming'],
            'variety_patterns': [r'roma', r'money maker', r'beef master', r'cherry']
        },
        'onion': {
            'keywords': ['onion', 'allium cepa'],
            'strong_indicators': ['onion production', 'onion varieties', 'onion farming'],
            'variety_patterns': [r'red creole', r'white globe', r'yellow globe']
        },
        'sunflower': {
            'keywords': ['sunflower', 'helianthus'],
            'strong_indicators': ['sunflower production', 'sunflower varieties'],
            'variety_patterns': [r'record', r'hysun', r'pannar']
        },
        'cowpea': {
            'keywords': ['cowpea', 'vigna unguiculata', 'black eyed pea'],
            'strong_indicators': ['cowpea production', 'cowpea varieties'],
            'variety_patterns': [r'sudan\s*1', r'blackeye', r'cream']
        },
        'pigeon_pea': {
            'keywords': ['pigeon pea', 'cajanus cajan'],
            'strong_indicators': ['pigeon pea production', 'pigeon pea varieties'],
            'variety_patterns': [r'iceap', r'mbaazi']
        }
    }
    
    identified_crops = []
    
    for crop, patterns in crop_patterns.items():
        score = 0
        
        # Check source filename (high weight)
        for keyword in patterns['keywords']:
            if keyword in source_lower:
                score += 10
        
        # Check strong indicators in content (high weight)
        for indicator in patterns['strong_indicators']:
            score += full_content.count(indicator) * 5
        
        # Check general keywords (medium weight)
        for keyword in patterns['keywords']:
            score += full_content.count(keyword) * 2
        
        # Check for variety patterns (strong evidence)
        for pattern in patterns['variety_patterns']:
            matches = re.findall(pattern, full_content, re.IGNORECASE)
            if matches:
                score += len(matches) * 3
        
        # Crop is identified if score is significant
        if score >= 5:  # Threshold for crop identification
            identified_crops.append(crop)
            print(f"    🎯 {crop}: score {score}")
    
    return identified_crops

def extract_varieties_for_crop(chunks: List[str], crop: str, source: str) -> List[Dict[str, Any]]:
    """Extract varieties for a specific crop from document chunks."""
    
    varieties = []
    
    # Crop-specific variety extraction patterns
    variety_patterns = {
        'groundnut': [
            r'\b(CG\s*[0-9]+)\b',
            r'\b(Chalimbana\s*(?:2005)?)\b',
            r'\b(Nsinjiro)\b',
            r'\b(Kakoma)\b',
            r'\b(Chitala)\b',
            r'\b(Baka)\b',
        ],
        'maize': [
            r'\b(SC\s*[0-9]+[A-Z]*)\b',
            r'\b(DK\s*[0-9]+[A-Z]*)\b',
            r'\b(PAN\s*[0-9]+[A-Z]*)\b',
            r'\b(Pioneer\s*[0-9]+[A-Z]*)\b',
            r'\b(ZM\s*[0-9]+[A-Z]*)\b',
            r'\b(MH\s*[0-9]+[A-Z]*)\b',
        ],
        'soybean': [
            r'\b(TGX\s*[0-9]+[A-Z-]*)\b',
            r'\b(Tikolore)\b',
            r'\b(Magoye)\b',
            r'\b(Ocepara\s*[0-9]*)\b',
        ],
        'bean': [
            r'\b(GLP\s*[0-9]+)\b',
            r'\b(Rosecoco)\b',
            r'\b(Canadian\s*Wonder)\b',
            r'\b(Red\s*Kidney)\b',
            r'\b(Navy\s*Bean)\b',
        ],
        'rice': [
            r'\b(NERICA\s*[0-9]+)\b',
            r'\b(WITA\s*[0-9]+)\b',
            r'\b(Kilombero)\b',
            r'\b(Pussa\s*[0-9]+)\b',
        ],
        'cassava': [
            r'\b(Sauti)\b',
            r'\b(Kanyama)\b',
            r'\b(Chitembwere)\b',
            r'\b(Mpale)\b',
        ],
        'tomato': [
            r'\b(Roma)\b',
            r'\b(Money\s*Maker)\b',
            r'\b(Beef\s*Master)\b',
            r'\b(Cherry)\b',
            r'\b(Determinate)\b',
            r'\b(Indeterminate)\b',
        ],
        'onion': [
            r'\b(Red\s*Creole)\b',
            r'\b(White\s*Globe)\b',
            r'\b(Yellow\s*Globe)\b',
            r'\b(Bombay\s*Red)\b',
        ],
        'sunflower': [
            r'\b(Record)\b',
            r'\b(Hysun\s*[0-9]+)\b',
            r'\b(Pannar\s*[0-9]+)\b',
            r'\b(Confectionery)\b',
            r'\b(Oil\s*type)\b',
        ],
        'cowpea': [
            r'\b(Sudan\s*1)\b',
            r'\b(Blackeye)\b',
            r'\b(Cream)\b',
            r'\b(IT\s*[0-9]+)\b',
        ],
        'pigeon_pea': [
            r'\b(ICEAP\s*[0-9]+)\b',
            r'\b(Mbaazi)\b',
            r'\b(Long\s*duration)\b',
            r'\b(Short\s*duration)\b',
        ]
    }
    
    if crop not in variety_patterns:
        return varieties
    
    patterns = variety_patterns[crop]
    found_variety_names = set()
    
    # Search through all chunks
    for chunk in chunks:
        for pattern in patterns:
            matches = re.findall(pattern, chunk, re.IGNORECASE)
            for match in matches:
                # Clean up the variety name
                clean_name = re.sub(r'\s+', ' ', match.strip())
                
                if clean_name and clean_name.lower() not in found_variety_names:
                    found_variety_names.add(clean_name.lower())
                    
                    # Extract additional context around the variety
                    context = extract_variety_context(chunk, clean_name)
                    
                    variety_data = {
                        'crop_name': crop,
                        'variety_name': clean_name,
                        'variety_type': determine_variety_type(clean_name, crop),
                        'yield_potential': extract_yield_from_context(context),
                        'maturity_days': extract_maturity_from_context(context),
                        'weather_requirements': 'Not specified',
                        'soil_requirements': 'Not specified',
                        'growing_areas': 'Not specified',
                        'disease_resistance': 'Not specified',
                        'planting_time': 'Not specified',
                        'source_document': source,
                        'context': context  # For validation
                    }
                    
                    varieties.append(variety_data)
    
    return varieties

def extract_variety_context(chunk: str, variety_name: str) -> str:
    """Extract context around a variety mention for validation."""
    
    # Find the variety in the chunk
    variety_pos = chunk.lower().find(variety_name.lower())
    if variety_pos == -1:
        return chunk[:200]  # Return beginning if not found
    
    # Extract 100 characters before and after the variety mention
    start = max(0, variety_pos - 100)
    end = min(len(chunk), variety_pos + len(variety_name) + 100)
    
    return chunk[start:end].strip()

def extract_yield_from_context(context: str) -> str:
    """Extract yield information from context."""
    
    # Look for yield patterns
    yield_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:tons?|tonnes?|kg|mt)\s*(?:per|/)\s*(?:ha|hectare)',
        r'yield\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\s*(?:tons?|tonnes?|kg|mt)',
        r'(\d+(?:\.\d+)?)\s*(?:tons?|tonnes?|kg|mt)\s*yield'
    ]
    
    for pattern in yield_patterns:
        matches = re.findall(pattern, context.lower(), re.IGNORECASE)
        if matches:
            return f"{matches[0]} per hectare"
    
    return 'Not specified'

def extract_maturity_from_context(context: str) -> int:
    """Extract maturity days from context."""
    
    # Look for maturity patterns
    maturity_patterns = [
        r'(\d+)\s*days?\s*(?:to\s*)?(?:maturity|mature)',
        r'matur(?:e|ity)\s*(?:in|at)?\s*(\d+)\s*days?',
        r'(\d+)[-\s]*day\s*(?:variety|cultivar)'
    ]
    
    for pattern in maturity_patterns:
        matches = re.findall(pattern, context.lower(), re.IGNORECASE)
        if matches:
            try:
                return int(matches[0])
            except:
                continue
    
    return None

def validate_variety_crop_association(variety_data: Dict[str, Any], crop: str, chunks: List[str]) -> bool:
    """Validate that a variety is actually associated with the specified crop."""
    
    variety_name = variety_data['variety_name']
    context = variety_data.get('context', '')
    
    # Check if the variety name appears in context with the crop
    crop_keywords = {
        'groundnut': ['groundnut', 'peanut'],
        'maize': ['maize', 'corn'],
        'soybean': ['soybean', 'soya'],
        'bean': ['bean'],
        'rice': ['rice'],
        'cassava': ['cassava'],
        'tomato': ['tomato'],
        'onion': ['onion'],
        'sunflower': ['sunflower'],
        'cowpea': ['cowpea'],
        'pigeon_pea': ['pigeon pea', 'pigeon-pea']
    }
    
    if crop not in crop_keywords:
        return False
    
    # Look for crop keywords near the variety mention
    context_lower = context.lower()
    variety_lower = variety_name.lower()
    
    for keyword in crop_keywords[crop]:
        # Check if crop keyword appears in the same context as variety
        if keyword in context_lower and variety_lower in context_lower:
            return True
    
    # Additional validation: check if variety name pattern matches crop expectations
    crop_specific_patterns = {
        'groundnut': [r'cg\s*[0-9]+', r'chalimbana', r'nsinjiro', r'kakoma', r'chitala', r'baka'],
        'maize': [r'sc\s*[0-9]+', r'dk\s*[0-9]+', r'pan\s*[0-9]+', r'pioneer', r'zm\s*[0-9]+', r'mh\s*[0-9]+'],
        'soybean': [r'tgx\s*[0-9]+', r'tikolore', r'magoye'],
        'bean': [r'glp\s*[0-9]+', r'rosecoco', r'canadian\s*wonder'],
        'rice': [r'nerica\s*[0-9]+', r'wita\s*[0-9]+', r'kilombero'],
        'cassava': [r'sauti', r'kanyama', r'chitembwere'],
        'tomato': [r'roma', r'money\s*maker', r'beef\s*master', r'cherry'],
        'onion': [r'red\s*creole', r'white\s*globe', r'yellow\s*globe', r'bombay\s*red'],
        'sunflower': [r'record', r'hysun', r'pannar', r'confectionery'],
        'cowpea': [r'sudan\s*1', r'blackeye', r'cream', r'it\s*[0-9]+'],
        'pigeon_pea': [r'iceap\s*[0-9]+', r'mbaazi', r'long\s*duration', r'short\s*duration']
    }
    
    if crop in crop_specific_patterns:
        for pattern in crop_specific_patterns[crop]:
            if re.search(pattern, variety_lower, re.IGNORECASE):
                return True
    
    return False

def determine_variety_type(variety_name: str, crop: str) -> str:
    """Determine variety type based on name patterns."""
    
    name_lower = variety_name.lower()
    
    type_mappings = {
        'groundnut': {
            'CG Series': [r'cg\s*[0-9]+'],
            'Chalimbana': [r'chalimbana'],
            'Nsinjiro': [r'nsinjiro'],
            'Kakoma': [r'kakoma'],
            'Chitala': [r'chitala'],
            'Baka': [r'baka']
        },
        'maize': {
            'Single Cross': [r'sc\s*[0-9]+'],
            'DK Series': [r'dk\s*[0-9]+'],
            'PAN Series': [r'pan\s*[0-9]+'],
            'Pioneer': [r'pioneer'],
            'ZM Series': [r'zm\s*[0-9]+'],
            'MH Series': [r'mh\s*[0-9]+']
        },
        'soybean': {
            'TGX Series': [r'tgx\s*[0-9]+'],
            'Tikolore': [r'tikolore'],
            'Magoye': [r'magoye']
        }
    }
    
    if crop in type_mappings:
        for variety_type, patterns in type_mappings[crop].items():
            for pattern in patterns:
                if re.search(pattern, name_lower, re.IGNORECASE):
                    return variety_type
    
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
    
    # Remove context before inserting (it was just for validation)
    variety_clean = {k: v for k, v in variety.items() if k != 'context'}
    
    cursor.execute(insert_sql, (
        variety_clean['crop_name'],
        variety_clean['variety_name'],
        variety_clean['variety_type'],
        variety_clean['yield_potential'],
        variety_clean['maturity_days'],
        variety_clean['weather_requirements'],
        variety_clean['soil_requirements'],
        variety_clean['growing_areas'],
        variety_clean['disease_resistance'],
        variety_clean['planting_time'],
        variety_clean['source_document']
    ))

def verify_extraction_quality(cursor):
    """Verify the quality of extracted varieties."""
    
    print(f"\n📊 FINAL EXTRACTION REPORT")
    print("=" * 50)
    
    # Total varieties
    cursor.execute("SELECT COUNT(*) FROM varieties")
    total_count = cursor.fetchone()[0]
    print(f"✅ Total varieties: {total_count}")
    
    # Breakdown by crop
    cursor.execute("SELECT crop_name, COUNT(*) FROM varieties GROUP BY crop_name ORDER BY COUNT(*) DESC")
    crop_counts = cursor.fetchall()
    print(f"\n📈 Varieties by crop:")
    for crop, count in crop_counts:
        print(f"  - {crop}: {count} varieties")
    
    # Sample varieties for each crop
    print(f"\n🔍 Sample varieties by crop:")
    for crop, _ in crop_counts:
        cursor.execute("SELECT variety_name, variety_type FROM varieties WHERE crop_name = ? ORDER BY variety_name LIMIT 3", (crop,))
        samples = cursor.fetchall()
        print(f"  - {crop}:")
        for name, vtype in samples:
            print(f"    • {name} ({vtype})")
    
    # Check data quality
    cursor.execute("SELECT COUNT(*) FROM varieties WHERE variety_name = 'Unknown' OR variety_name = ''")
    unknown_count = cursor.fetchone()[0]
    print(f"\n🎯 Data quality:")
    print(f"  - Unknown/empty varieties: {unknown_count}")
    print(f"  - Valid varieties: {total_count - unknown_count}")
    print(f"  - Quality rate: {((total_count - unknown_count) / total_count * 100):.1f}%")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Methodical variety extraction with quality validation")
    parser.add_argument("--db-path", default="data/agricultural_documents.db", help="Path to database file")
    
    args = parser.parse_args()
    
    success = methodical_variety_extraction(args.db_path)
    if success:
        print("\n🎉 Methodical variety extraction completed successfully!")
    else:
        print("\n❌ Variety extraction failed. Check the logs above.")
        sys.exit(1)
