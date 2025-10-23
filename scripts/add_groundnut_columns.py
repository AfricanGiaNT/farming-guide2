#!/usr/bin/env python3
"""
Add Groundnut-Specific Columns to Varieties Table
Add columns for promotion status, recommendation status, botanical type, growth habit, 
oil content, seed color, pest control info, disease control info, and fertilizer info
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_groundnut_columns():
    """Add groundnut-specific columns to varieties table"""
    
    print("=" * 80)
    print("ADDING GROUNDNUT-SPECIFIC COLUMNS TO VARIETIES TABLE")
    print("=" * 80)
    
    # Define new columns for groundnut varieties
    new_columns = [
        # Promotion and recommendation status
        "promotion_status VARCHAR(50)",  # 'being_promoted', 'recommended', 'standard'
        "recommendation_status VARCHAR(50)",  # 'recommended', 'standard'
        
        # Botanical and growth characteristics
        "botanical_type VARCHAR(50)",  # 'Virginia', 'Spanish'
        "market_type VARCHAR(50)",  # 'Confectionery', 'Oil', 'Dual_purpose'
        "growth_habit VARCHAR(50)",  # 'Bunch', 'Runner', 'Spreading'
        
        # Seed characteristics
        "seed_color VARCHAR(50)",  # 'Tan', 'Red', 'Pale_tan', etc.
        "seed_size VARCHAR(50)",  # 'Small', 'Medium', 'Large'
        "oil_content VARCHAR(20)",  # '45%', '48%', etc.
        
        # Agronomic characteristics
        "maturity_days VARCHAR(50)",  # '90-120', '130-150', etc.
        "altitude_range VARCHAR(100)",  # '200-500m', '1000-1500m', etc.
        "drought_tolerance VARCHAR(50)",  # 'Tolerant', 'Moderate', 'Susceptible'
        "rosette_resistance VARCHAR(50)",  # 'Resistant', 'Tolerant', 'Susceptible'
        
        # Pest and disease control information
        "pest_control_info TEXT",  # Detailed pest control information
        "disease_control_info TEXT",  # Detailed disease control information
        "pest_resistance VARCHAR(200)",  # Specific pest resistances
        "disease_resistance VARCHAR(200)",  # Specific disease resistances
        
        # Fertilizer and nutrition information
        "fertilizer_info TEXT",  # Detailed fertilizer application information
        "basal_fertilizer VARCHAR(200)",  # Basal fertilizer recommendations
        "top_dressing VARCHAR(200)",  # Top dressing recommendations
        "nutrient_requirements TEXT",  # Specific nutrient requirements
        
        # Additional agronomic information
        "planting_spacing VARCHAR(100)",  # Row and hill spacing
        "seed_rate VARCHAR(50)",  # Seed rate per hectare
        "harvesting_notes TEXT",  # Harvesting recommendations
        "storage_notes TEXT",  # Storage recommendations
    ]
    
    print(f"Adding {len(new_columns)} new columns to varieties table...")
    
    # Add each column
    for column_def in new_columns:
        column_name = column_def.split()[0]
        column_type = ' '.join(column_def.split()[1:])
        
        try:
            # Use raw SQL to add column
            sql = f"ALTER TABLE varieties ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
            result = supabase.rpc('execute_sql', {'sql': sql}).execute()
            print(f"✓ Added column: {column_name}")
            
        except Exception as e:
            print(f"✗ Failed to add column {column_name}: {str(e)}")
    
    print(f"\nCompleted adding groundnut-specific columns!")

def verify_columns():
    """Verify that columns were added successfully"""
    
    print("\n" + "=" * 80)
    print("VERIFYING NEW COLUMNS")
    print("=" * 80)
    
    try:
        # Get a sample variety to see all columns
        result = supabase.table('varieties').select('*').limit(1).execute()
        
        if result.data:
            variety = result.data[0]
            print(f"Current columns in varieties table:")
            for key in sorted(variety.keys()):
                print(f"  - {key}")
        else:
            print("No varieties found in table")
            
    except Exception as e:
        print(f"Error verifying columns: {str(e)}")

def main():
    add_groundnut_columns()
    verify_columns()

if __name__ == "__main__":
    main()