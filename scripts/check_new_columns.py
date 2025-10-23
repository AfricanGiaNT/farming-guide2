#!/usr/bin/env python3
"""
Check if New Columns Were Actually Added
Verify if the new columns exist in the database
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_new_columns():
    """Check if new columns were actually added"""
    
    print("=" * 80)
    print("CHECKING IF NEW COLUMNS WERE ACTUALLY ADDED")
    print("=" * 80)
    
    # List of columns we tried to add
    new_columns = [
        'promotion_status', 'recommendation_status', 'crop_type', 'market_type',
        'growth_habit', 'seed_color', 'seed_size', 'oil_content', 'protein_content',
        'starch_content', 'sugar_content', 'altitude_range', 'pest_resistance',
        'pest_control_info', 'disease_control_info', 'fertilizer_info',
        'basal_fertilizer', 'top_dressing', 'nutrient_requirements',
        'planting_spacing', 'seed_rate', 'planting_depth', 'harvesting_notes',
        'storage_notes', 'post_harvest_handling', 'special_characteristics',
        'suitable_climates', 'suitable_soils', 'rotation_notes'
    ]
    
    try:
        # Get current columns
        result = supabase.table('varieties').select('*').limit(1).execute()
        
        if result.data:
            variety = result.data[0]
            current_columns = set(variety.keys())
            
            print(f"Current columns in varieties table: {len(current_columns)}")
            print("\nChecking for new columns:")
            
            found_new_columns = []
            missing_columns = []
            
            for column in new_columns:
                if column in current_columns:
                    found_new_columns.append(column)
                    print(f"  OK {column} - EXISTS")
                else:
                    missing_columns.append(column)
                    print(f"  X {column} - MISSING")
            
            print(f"\nSummary:")
            print(f"- New columns found: {len(found_new_columns)}")
            print(f"- New columns missing: {len(missing_columns)}")
            
            if missing_columns:
                print(f"\nMissing columns that need to be added:")
                for column in missing_columns:
                    print(f"  - {column}")
                
                print(f"\nThe SQL command may not have executed successfully.")
                print(f"Please check the Supabase SQL editor for any error messages.")
            
            return len(found_new_columns) > 0
            
        else:
            print("No varieties found in table")
            return False
            
    except Exception as e:
        print(f"Error checking columns: {str(e)}")
        return False

def generate_simple_sql():
    """Generate simple SQL commands to add missing columns one by one"""
    
    print("\n" + "=" * 80)
    print("SIMPLE SQL COMMANDS TO ADD MISSING COLUMNS")
    print("=" * 80)
    
    # Essential columns for groundnut extraction
    essential_columns = [
        "promotion_status VARCHAR(50)",
        "recommendation_status VARCHAR(50)", 
        "crop_type VARCHAR(50)",
        "market_type VARCHAR(50)",
        "growth_habit VARCHAR(50)",
        "seed_color VARCHAR(50)",
        "oil_content VARCHAR(20)",
        "altitude_range VARCHAR(100)",
        "planting_spacing VARCHAR(100)",
        "seed_rate VARCHAR(50)",
        "special_characteristics TEXT"
    ]
    
    print("Copy and paste these SQL commands one by one:")
    print("(Run each command separately to identify any issues)")
    print()
    
    for column_def in essential_columns:
        column_name = column_def.split()[0]
        column_type = ' '.join(column_def.split()[1:])
        sql_command = f"ALTER TABLE varieties ADD COLUMN IF NOT EXISTS {column_name} {column_type};"
        print(sql_command)
    
    print("\n" + "=" * 80)
    print("INSTRUCTIONS:")
    print("1. Go to Supabase SQL Editor")
    print("2. Run each command above one by one")
    print("3. Check for any error messages")
    print("4. If successful, run the groundnut extraction again")

def main():
    success = check_new_columns()
    
    if not success:
        generate_simple_sql()
    else:
        print("\nGreat! New columns are available. You can now run the groundnut extraction.")

if __name__ == "__main__":
    main()