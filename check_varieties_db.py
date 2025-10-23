#!/usr/bin/env python3
"""Check current varieties in database"""

import sqlite3
import os

def check_varieties():
    db_path = 'data/agricultural_documents.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check maize varieties
    cursor.execute("""
        SELECT variety_name, type, maturity_days, yield_potential, drought_tolerance, disease_resistance 
        FROM varieties 
        WHERE crop_id IN (SELECT id FROM crops WHERE crop_name = 'maize') 
        LIMIT 10
    """)
    
    print("=== MAIZE VARIETIES ===")
    for row in cursor.fetchall():
        print(f"Name: {row[0]}")
        print(f"Type: {row[1]}")
        print(f"Maturity: {row[2]} days")
        print(f"Yield: {row[3]}")
        print(f"Drought: {row[4]}")
        print(f"Disease: {row[5]}")
        print("-" * 40)
    
    # Check total counts
    cursor.execute("SELECT COUNT(*) FROM crops")
    crop_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM varieties")
    variety_count = cursor.fetchone()[0]
    
    print(f"\nTotal crops: {crop_count}")
    print(f"Total varieties: {variety_count}")
    
    conn.close()

if __name__ == "__main__":
    check_varieties()
