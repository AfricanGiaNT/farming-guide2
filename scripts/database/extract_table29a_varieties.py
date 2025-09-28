#!/usr/bin/env python3
"""
Extract varieties specifically from Table 29a: Phaseolus bean seed description
and other similar structured tables that our previous methods missed.
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def get_db_connection(db_path):
    """Establishes and returns a database connection."""
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
    return sqlite3.connect(db_path)

def clear_varieties_table(db_path):
    """Clears all data from the varieties table."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM varieties")
    conn.commit()
    conn.close()
    print("✅ Cleared existing varieties table")

def insert_variety(conn, variety_data):
    """Inserts a single variety into the varieties table, checking for duplicates."""
    cursor = conn.cursor()
    
    # Check for existing variety for the same crop
    cursor.execute(
        "SELECT id FROM varieties WHERE LOWER(variety_name) = ? AND LOWER(crop_name) = ?",
        (variety_data['variety_name'].lower(), variety_data['crop_name'].lower())
    )
    if cursor.fetchone():
        return False # Duplicate
    
    cursor.execute("""
        INSERT INTO varieties (
            crop_name, variety_name, variety_type, yield_potential, maturity_days,
            weather_requirements, soil_requirements, growing_areas, disease_resistance,
            planting_time, source_document
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        variety_data.get('crop_name'),
        variety_data.get('variety_name'),
        variety_data.get('variety_type'),
        variety_data.get('yield_potential'),
        variety_data.get('maturity_days'),
        variety_data.get('weather_requirements'),
        variety_data.get('soil_requirements'),
        variety_data.get('growing_areas'),
        variety_data.get('disease_resistance'),
        variety_data.get('planting_time'),
        variety_data.get('source_document')
    ))
    return True

def extract_table29a_varieties():
    """Extract varieties from Table 29a and similar structured data"""
    
    # Table 29a: Phaseolus bean seed description varieties
    phaseolus_varieties = [
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Kholophethe',
            'variety_type': 'Bush',
            'maturity_days': 95,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'PAN 148',
            'variety_type': 'Bush',
            'maturity_days': 100,
            'yield_potential': '2100 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'PAN 9249',
            'variety_type': 'Bush',
            'maturity_days': 110,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'VTTT 924/10-4',
            'variety_type': 'Bush',
            'maturity_days': 77,
            'yield_potential': '3000 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'VTTT 924/4-4',
            'variety_type': 'Bush',
            'maturity_days': 70,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Cim-Dwarf-01-12-2',
            'variety_type': 'Bush',
            'maturity_days': 85,
            'yield_potential': '3000 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'NUA 35',
            'variety_type': 'Bush',
            'maturity_days': 70,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'NUA 45',
            'variety_type': 'Bush',
            'maturity_days': 70,
            'yield_potential': '1300 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'NUA 59',
            'variety_type': 'Bush',
            'maturity_days': 70,
            'yield_potential': '2000 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Nyambitila',
            'variety_type': 'Bush',
            'maturity_days': 70,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Namtupa',
            'variety_type': 'Bush',
            'maturity_days': 70,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Chitedze Bean 1',
            'variety_type': 'Bush',
            'maturity_days': 70,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Chitedze Bean 2',
            'variety_type': 'Bush',
            'maturity_days': 70,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Chitedze Bean 3',
            'variety_type': 'Bush',
            'maturity_days': 70,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Chitedze Bean 4',
            'variety_type': 'Bush',
            'maturity_days': 72,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Chitedze Bean 5',
            'variety_type': 'Bush',
            'maturity_days': 75,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Namajengo',
            'variety_type': 'Climber',
            'maturity_days': 90,
            'yield_potential': '1200 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Saperekedwa',
            'variety_type': 'Bush',
            'maturity_days': 90,
            'yield_potential': '1500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Kanzama',
            'variety_type': 'Climber',
            'maturity_days': 95,
            'yield_potential': '1500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Kalimtsiro',
            'variety_type': 'Climber',
            'maturity_days': 90,
            'yield_potential': '1200 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Nasaka',
            'variety_type': 'Bush',
            'maturity_days': 80,
            'yield_potential': '1200 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Bwenzilaana',
            'variety_type': 'Bush',
            'maturity_days': 85,
            'yield_potential': '1500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Kalima',
            'variety_type': 'Bush',
            'maturity_days': 90,
            'yield_potential': '1500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Bunda 93',
            'variety_type': 'Climber',
            'maturity_days': 90,
            'yield_potential': '2000 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Chimbamba',
            'variety_type': 'Climber',
            'maturity_days': 90,
            'yield_potential': '1500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Not specified',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'BCMV-B2',
            'variety_type': 'Climber',
            'maturity_days': 85,
            'yield_potential': '2500 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Bean Common Mosaic Virus resistant',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'BCMV-B4',
            'variety_type': 'Climber',
            'maturity_days': 90,
            'yield_potential': '2000 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Bean Common Mosaic Virus resistant',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        },
        {
            'crop_name': 'phaseolus_bean',
            'variety_name': 'Kabalabala',
            'variety_type': 'Indeterminate',
            'maturity_days': 90,
            'yield_potential': '2800 kg/ha',
            'weather_requirements': 'Cool plateau areas',
            'soil_requirements': 'Well-drained soils',
            'growing_areas': 'Cool plateau areas',
            'disease_resistance': 'Disease tolerant, wide adaptation',
            'planting_time': 'December-January',
            'source_document': 'Guide to Agriculture Production in Malawi 2021.pdf'
        }
    ]
    
    return phaseolus_varieties

def targeted_variety_extraction(db_path="data/agricultural_documents.db"):
    """Extract the specific varieties we identified from structured tables"""
    print(f"🎯 Targeted extraction of Table 29a varieties")
    
    # Don't clear table, just add missing varieties
    conn = get_db_connection(db_path)
    
    # Get the phaseolus varieties from Table 29a
    phaseolus_varieties = extract_table29a_varieties()
    
    added_count = 0
    for variety in phaseolus_varieties:
        if insert_variety(conn, variety):
            print(f"  ✅ Added: {variety['variety_name']}")
            added_count += 1
        else:
            print(f"  ⚠️  Duplicate skipped: {variety['variety_name']}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Targeted extraction completed!")
    print(f"✅ Added {added_count} new phaseolus bean varieties")
    
    # Verify NUA 45 is now present
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT crop_name, variety_name FROM varieties WHERE LOWER(variety_name) LIKE '%nua%45%' OR LOWER(variety_name) LIKE '%nua 45%'")
    nua45_result = cursor.fetchall()
    
    if nua45_result:
        print(f"✅ NUA 45 verification: Found as '{nua45_result[0][1]}' ({nua45_result[0][0]})")
    else:
        print(f"❌ NUA 45 still not found!")
    
    # Get final count
    cursor.execute("SELECT COUNT(*) FROM varieties WHERE crop_name = 'phaseolus_bean'")
    phaseolus_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM varieties")
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"📊 Final counts:")
    print(f"  - Phaseolus bean varieties: {phaseolus_count}")
    print(f"  - Total varieties: {total_count}")
    
    return added_count

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract Table 29a varieties specifically.")
    parser.add_argument("--db-path", default="data/agricultural_documents.db", help="Path to the SQLite database.")
    args = parser.parse_args()
    
    targeted_variety_extraction(args.db_path)
