#!/usr/bin/env python3
"""Test constraint issue"""

import sqlite3

def test_insert():
    conn = sqlite3.connect('data/agricultural_documents.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO varieties (
                crop_id, variety_name, type, maturity_days, drought_tolerance,
                disease_resistance, yield_potential, planting_months, harvest_months,
                min_rainfall_mm, max_rainfall_mm, optimal_temperature_min, optimal_temperature_max,
                soil_requirements, spacing_requirements, fertilizer_requirements,
                pest_management, disease_management, harvesting_guidelines, storage_requirements,
                source_document, extraction_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1,  # crop_id
            "TEST",  # variety_name
            "hybrid",  # type
            120,  # maturity_days
            "moderate",  # drought_tolerance
            "[]",  # disease_resistance
            "high",  # yield_potential
            "[]",  # planting_months
            "[]",  # harvest_months
            450,  # min_rainfall_mm
            800,  # max_rainfall_mm
            18,  # optimal_temperature_min
            30,  # optimal_temperature_max
            "test",  # soil_requirements
            "test",  # spacing_requirements
            "test",  # fertilizer_requirements
            "test",  # pest_management
            "test",  # disease_management
            "test",  # harvesting_guidelines
            "test",  # storage_requirements
            "test",  # source_document
            1.0  # extraction_confidence
        ))
        
        print("Test insert successful!")
        conn.commit()
        
    except Exception as e:
        print(f"Error: {e}")
    
    conn.close()

if __name__ == "__main__":
    test_insert()
