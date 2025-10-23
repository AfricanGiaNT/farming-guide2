#!/usr/bin/env python3
"""
Add General Agricultural Columns to Varieties Table
Add general columns that can be used for any crop variety information
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_existing_columns():
    """Check what columns already exist in the varieties table"""
    
    print("=" * 80)
    print("CHECKING EXISTING COLUMNS IN VARIETIES TABLE")
    print("=" * 80)
    
    try:
        # Get a sample variety to see all columns
        result = supabase.table('varieties').select('*').limit(1).execute()
        
        if result.data:
            variety = result.data[0]
            print(f"Current columns in varieties table:")
            for key in sorted(variety.keys()):
                print(f"  - {key}")
            return list(variety.keys())
        else:
            print("No varieties found in table")
            return []
            
    except Exception as e:
        print(f"Error checking columns: {str(e)}")
        return []

def add_general_columns():
    """Add general agricultural columns to varieties table"""
    
    print("\n" + "=" * 80)
    print("ADDING GENERAL AGRICULTURAL COLUMNS TO VARIETIES TABLE")
    print("=" * 80)
    
    # Define general columns that can be used for any crop
    new_columns = [
        # Status and classification
        "promotion_status VARCHAR(50)",  # 'being_promoted', 'recommended', 'standard', 'discontinued'
        "recommendation_status VARCHAR(50)",  # 'recommended', 'standard', 'experimental'
        "crop_type VARCHAR(50)",  # 'Virginia', 'Spanish', 'Hybrid', 'OPV', etc.
        "market_type VARCHAR(50)",  # 'Confectionery', 'Oil', 'Dual_purpose', 'Industrial', etc.
        
        # Physical characteristics
        "growth_habit VARCHAR(50)",  # 'Bunch', 'Runner', 'Spreading', 'Erect', 'Climbing', etc.
        "seed_color VARCHAR(50)",  # 'Tan', 'Red', 'Pale_tan', 'White', 'Black', etc.
        "seed_size VARCHAR(50)",  # 'Small', 'Medium', 'Large', 'Extra_large'
        "grain_color VARCHAR(50)",  # For cereals - 'White', 'Yellow', 'Red', etc.
        "grain_texture VARCHAR(50)",  # 'Hard', 'Soft', 'Medium', etc.
        
        # Nutritional and quality characteristics
        "oil_content VARCHAR(20)",  # '45%', '48%', etc.
        "protein_content VARCHAR(20)",  # '12%', '15%', etc.
        "starch_content VARCHAR(20)",  # '70%', '75%', etc.
        "sugar_content VARCHAR(20)",  # '15%', '20%', etc.
        
        # Agronomic characteristics
        "maturity_days VARCHAR(50)",  # '90-120', '130-150', etc.
        "altitude_range VARCHAR(100)",  # '200-500m', '1000-1500m', etc.
        "drought_tolerance VARCHAR(50)",  # 'Tolerant', 'Moderate', 'Susceptible'
        "disease_resistance VARCHAR(200)",  # Specific disease resistances
        "pest_resistance VARCHAR(200)",  # Specific pest resistances
        
        # Management information
        "pest_control_info TEXT",  # Detailed pest control information
        "disease_control_info TEXT",  # Detailed disease control information
        "fertilizer_info TEXT",  # Detailed fertilizer application information
        "basal_fertilizer VARCHAR(200)",  # Basal fertilizer recommendations
        "top_dressing VARCHAR(200)",  # Top dressing recommendations
        "nutrient_requirements TEXT",  # Specific nutrient requirements
        
        # Planting and harvesting information
        "planting_spacing VARCHAR(100)",  # Row and hill spacing
        "seed_rate VARCHAR(50)",  # Seed rate per hectare
        "planting_depth VARCHAR(50)",  # Planting depth recommendations
        "harvesting_notes TEXT",  # Harvesting recommendations
        "storage_notes TEXT",  # Storage recommendations
        "post_harvest_handling TEXT",  # Post-harvest handling recommendations
        
        # Additional information
        "special_characteristics TEXT",  # Any special traits or characteristics
        "suitable_climates TEXT",  # Suitable climate conditions
        "suitable_soils TEXT",  # Suitable soil types
        "rotation_notes TEXT",  # Crop rotation recommendations
        "yield_potential VARCHAR(100)",  # Yield potential information
    ]
    
    print(f"Attempting to add {len(new_columns)} general columns to varieties table...")
    print("Note: This will show which columns already exist vs which need to be added.")
    
    # Check existing columns first
    existing_columns = check_existing_columns()
    
    # Add each column
    added_count = 0
    for column_def in new_columns:
        column_name = column_def.split()[0]
        column_type = ' '.join(column_def.split()[1:])
        
        if column_name in existing_columns:
            print(f"SKIP Column already exists: {column_name}")
        else:
            print(f"NEED TO ADD: {column_name} {column_type}")
            added_count += 1
    
    print(f"\nSummary:")
    print(f"- Total columns to check: {len(new_columns)}")
    print(f"- Columns already exist: {len(new_columns) - added_count}")
    print(f"- Columns that need to be added: {added_count}")
    
    if added_count > 0:
        print(f"\nNote: You'll need to add these columns manually through the Supabase dashboard")
        print(f"or use a database migration tool to add the missing columns.")

def main():
    check_existing_columns()
    add_general_columns()

if __name__ == "__main__":
    main()