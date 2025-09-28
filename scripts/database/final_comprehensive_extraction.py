#!/usr/bin/env python3
"""
Final comprehensive variety extraction that addresses the core methodology gaps:
1. Systematic extraction from ALL structured tables
2. Pattern matching for variety lists in text
3. Cross-referencing with known variety patterns
4. Multi-pass validation and deduplication
"""

import sqlite3
import os
import sys
import re
from pathlib import Path
from collections import defaultdict

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def get_db_connection(db_path):
    """Establishes and returns a database connection."""
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
    return sqlite3.connect(db_path)

def extract_all_structured_tables(content, source_document):
    """Extract varieties from ALL structured tables and variety lists"""
    varieties = []
    
    # Table patterns - look for any table mentioning varieties, cultivars, or specific crop types
    table_patterns = [
        # Specific table references
        r'Table\s*\d+[a-z]*[^:]*:.*?(?:varieties|cultivars|seed\s+description|recommended).*?(?=Table|\n\n\n|\Z)',
        # Variety recommendation sections
        r'recommended\s+varieties.*?(?=\n\d+\.|Table|\n\n\n|\Z)',
        r'improved\s+varieties.*?(?=\n\d+\.|Table|\n\n\n|\Z)',
        r'varieties\s+include.*?(?=\n\d+\.|Table|\n\n\n|\Z)',
        r'varieties\s+are.*?(?=\n\d+\.|Table|\n\n\n|\Z)',
        # List patterns with specific variety codes
        r'[^.]*(?:PAN|NUA|VTTT|CG|SC|MH|ZM|TGX|NERICA|CB)[^.]*\.', 
    ]
    
    for pattern in table_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            table_content = match.group(0)
            extracted = extract_varieties_from_text_block(table_content, source_document)
            varieties.extend(extracted)
    
    return varieties

def extract_varieties_from_text_block(text_block, source_document):
    """Extract individual varieties from a text block using comprehensive patterns"""
    varieties = []
    
    # Comprehensive variety patterns for all crops
    variety_patterns = {
        # Phaseolus beans
        'phaseolus_bean': [
            r'\b(NUA\s*\d+)\b', r'\b(PAN\s*\d+)\b', r'\b(VTTT\s*\d+/?\d*-?\d*)\b',
            r'\b(Chitedze\s*Bean\s*\d+)\b', r'\b(CB\d+)\b', r'\b(BCMV-[A-Z]\d+)\b',
            r'\b(Cim-Dwarf-\d+-\d+-\d+)\b', r'\b(BC-D/O\(\d+\))\b',
            r'\b(Kholophethe|Kabalabala|Namajengo|Saperekedwa|Kanzama|Kalimtsiro)\b',
            r'\b(Nasaka|Bwenzilaana|Kalima|Bunda\s*\d+|Chimbamba)\b',
            r'\b(Nyambitila|Namtupa)\b'
        ],
        # Maize
        'maize': [
            r'\b(SC\s*\d+)\b', r'\b(PAN\s*\d+[A-Z]*)\b', r'\b(MH\s*\d+[A-Z]*)\b',
            r'\b(ZM\s*\d+)\b', r'\b(DK\s*\d+)\b', r'\b(Pioneer\s*\d+)\b'
        ],
        # Groundnut
        'groundnut': [
            r'\b(CG\s*\d+)\b', r'\b(Chalimbana\s*\d*)\b', 
            r'\b(Nsinjiro|Kakoma|Chitala|Baka)\b'
        ],
        # Soybean
        'soybean': [
            r'\b(TGX\s*\d+[A-Z]*)\b', r'\b(Tikolore|Magoye|Ocepara\s*\d*)\b',
            r'\b(Nasoko|Makwacha|Solitaire|Soprano|Serenade)\b'
        ],
        # Rice
        'rice': [
            r'\b(NERICA\s*\d+)\b', r'\b(WITA\s*\d+)\b', r'\b(Kilombero)\b'
        ],
        # Other crops
        'cowpea': [r'\b(IT\d+|Sudan\s*\d+|Cream)\b'],
        'pigeon_pea': [r'\b(ICEAP\s*\d+)\b'],
        'cassava': [r'\b(Sauti|Kanyama|Chitembwere|Mpale)\b'],
        'sweet_potato': [r'\b(Kaphulira|Zondeni|Semusa|Mugamba)\b'],
        'tomato': [r'\b(Roma|Money\s*Maker|Beef\s*Master|Cherry)\b'],
        'onion': [r'\b(Texas\s*Grano|San\s*F1|Red\s*Creole)\b'],
        'sunflower': [r'\b(Record|Hysun\s*\d+)\b']
    }
    
    for crop, patterns in variety_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text_block, re.IGNORECASE)
            for match in matches:
                variety_name = match.group(1).strip()
                if variety_name and len(variety_name) > 1:
                    varieties.append({
                        'name': variety_name,
                        'crop': crop,
                        'source': source_document,
                        'context': text_block[max(0, match.start()-100):match.end()+100]
                    })
    
    return varieties

def search_for_missing_key_varieties(content, source_document):
    """Specifically search for varieties we know should exist but might be missing"""
    
    key_varieties_to_find = {
        # From your image - Table 29a varieties we might have missed
        'phaseolus_bean': [
            'NUA 45', 'NUA 59', 'NUA 35', 'PAN 148', 'PAN 9249', 
            'VTTT 924/10-4', 'VTTT 924/4-4', 'Kholophethe',
            'Chitedze Bean 1', 'Chitedze Bean 2', 'Chitedze Bean 3',
            'Chitedze Bean 4', 'Chitedze Bean 5', 'Nyambitila', 'Namtupa'
        ],
        # Additional varieties mentioned in documents
        'soybean': [
            'Nasoko', 'Makwacha', 'Solitaire', 'Soprano', 'Serenade'
        ],
        'bean': [
            'Napilira', 'Maluwa', 'Sapatsika', 'Nagaga', 'Kambidzi', 'Mkhalira'
        ]
    }
    
    found_varieties = []
    
    for crop, variety_list in key_varieties_to_find.items():
        for variety in variety_list:
            # Create flexible search pattern
            pattern = re.escape(variety).replace('\\ ', '\\s*')
            if re.search(pattern, content, re.IGNORECASE):
                found_varieties.append({
                    'name': variety,
                    'crop': crop,
                    'source': source_document,
                    'extraction_method': 'targeted_search'
                })
    
    return found_varieties

def final_comprehensive_extraction(db_path="data/agricultural_documents.db"):
    """Final comprehensive extraction addressing all methodology gaps"""
    
    print(f"🔍 Final comprehensive variety extraction from: {db_path}")
    
    # Get all documents
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT content, source FROM documents")
    documents = cursor.fetchall()
    conn.close()
    
    print(f"📚 Processing {len(documents)} documents with improved methodology")
    
    all_varieties = []
    
    for doc_idx, (content, source_document) in enumerate(documents):
        print(f"\n📄 Document {doc_idx + 1}/{len(documents)}: {source_document}")
        
        # Method 1: Extract from ALL structured tables
        table_varieties = extract_all_structured_tables(content, source_document)
        print(f"  📊 Table extraction: {len(table_varieties)} varieties")
        all_varieties.extend(table_varieties)
        
        # Method 2: Search for specific missing key varieties
        key_varieties = search_for_missing_key_varieties(content, source_document)
        print(f"  🎯 Key variety search: {len(key_varieties)} varieties")
        all_varieties.extend(key_varieties)
    
    print(f"\n📊 Raw extraction results: {len(all_varieties)} varieties")
    
    # Deduplicate and organize
    unique_varieties = {}
    crop_counts = defaultdict(int)
    
    for variety in all_varieties:
        variety_name = variety['name'].strip()
        crop = variety['crop']
        source = variety['source']
        
        key = f"{variety_name.lower()}_{crop}_{source}"
        
        if key not in unique_varieties:
            unique_varieties[key] = {
                'variety_name': variety_name,
                'crop_name': crop,
                'source_document': source
            }
            crop_counts[crop] += 1
    
    print(f"📊 Unique varieties after deduplication: {len(unique_varieties)}")
    print(f"📈 Varieties by crop:")
    for crop, count in sorted(crop_counts.items()):
        print(f"  - {crop}: {count} varieties")
    
    # Check current database state
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM varieties")
    current_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT crop_name, COUNT(*) FROM varieties GROUP BY crop_name ORDER BY COUNT(*) DESC")
    current_breakdown = cursor.fetchall()
    
    print(f"\n📊 Current database state:")
    print(f"  - Total varieties: {current_count}")
    print(f"  - Current breakdown:")
    for crop, count in current_breakdown:
        print(f"    • {crop}: {count} varieties")
    
    # Verify key varieties are present
    key_varieties_check = ['NUA 45', 'NUA 59', 'PAN 148', 'Kholophethe']
    print(f"\n🔍 Key varieties verification:")
    
    for variety in key_varieties_check:
        cursor.execute("SELECT crop_name, variety_name FROM varieties WHERE LOWER(variety_name) LIKE ?", (f'%{variety.lower()}%',))
        results = cursor.fetchall()
        if results:
            print(f"  ✅ {variety}: Found as '{results[0][1]}' ({results[0][0]})")
        else:
            print(f"  ❌ {variety}: NOT FOUND")
    
    conn.close()
    
    print(f"\n🎉 Final comprehensive extraction analysis completed!")
    return len(unique_varieties)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Final comprehensive variety extraction.")
    parser.add_argument("--db-path", default="data/agricultural_documents.db", help="Path to the SQLite database.")
    args = parser.parse_args()
    
    final_comprehensive_extraction(args.db_path)
