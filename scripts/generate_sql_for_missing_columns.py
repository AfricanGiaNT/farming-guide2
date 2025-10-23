#!/usr/bin/env python3
"""
Generate SQL Commands to Add Missing Columns to Varieties Table
This script generates SQL commands that can be run in Supabase SQL editor
"""

def generate_sql_commands():
    """Generate SQL commands to add missing columns"""
    
    print("=" * 80)
    print("SQL COMMANDS TO ADD MISSING COLUMNS TO VARIETIES TABLE")
    print("=" * 80)
    
    # Define the missing columns that need to be added
    missing_columns = [
        # Status and classification
        "promotion_status VARCHAR(50)",  # 'being_promoted', 'recommended', 'standard', 'discontinued'
        "recommendation_status VARCHAR(50)",  # 'recommended', 'standard', 'experimental'
        "crop_type VARCHAR(50)",  # 'Virginia', 'Spanish', 'Hybrid', 'OPV', etc.
        "market_type VARCHAR(50)",  # 'Confectionery', 'Oil', 'Dual_purpose', 'Industrial', etc.
        
        # Physical characteristics
        "growth_habit VARCHAR(50)",  # 'Bunch', 'Runner', 'Spreading', 'Erect', 'Climbing', etc.
        "seed_color VARCHAR(50)",  # 'Tan', 'Red', 'Pale_tan', 'White', 'Black', etc.
        "seed_size VARCHAR(50)",  # 'Small', 'Medium', 'Large', 'Extra_large'
        
        # Nutritional and quality characteristics
        "oil_content VARCHAR(20)",  # '45%', '48%', etc.
        "protein_content VARCHAR(20)",  # '12%', '15%', etc.
        "starch_content VARCHAR(20)",  # '70%', '75%', etc.
        "sugar_content VARCHAR(20)",  # '15%', '20%', etc.
        
        # Agronomic characteristics
        "altitude_range VARCHAR(100)",  # '200-500m', '1000-1500m', etc.
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
    ]
    
    print(f"Generating SQL commands for {len(missing_columns)} missing columns...")
    print("\nCopy and paste these SQL commands into the Supabase SQL editor:")
    print("\n" + "="*80)
    
    for column_def in missing_columns:
        column_name = column_def.split()[0]
        column_type = ' '.join(column_def.split()[1:])
        
        sql_command = f"ALTER TABLE varieties ADD COLUMN IF NOT EXISTS {column_name} {column_type};"
        print(sql_command)
    
    print("\n" + "="*80)
    print("INSTRUCTIONS:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to the SQL Editor")
    print("3. Copy and paste all the SQL commands above")
    print("4. Click 'Run' to execute the commands")
    print("5. Verify the columns were added successfully")
    
    print(f"\nTotal columns to add: {len(missing_columns)}")
    
    # Also generate a verification query
    print("\n" + "="*80)
    print("VERIFICATION QUERY:")
    print("Run this query after adding the columns to verify they were added:")
    print("\nSELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'varieties' ORDER BY column_name;")
    
    print("\n" + "="*80)
    print("ALTERNATIVE: Single Command Approach")
    print("If you prefer to run all commands at once, use this:")
    print()
    
    # Generate a single command with all columns
    all_columns = []
    for column_def in missing_columns:
        column_name = column_def.split()[0]
        column_type = ' '.join(column_def.split()[1:])
        all_columns.append(f"{column_name} {column_type}")
    
    single_command = f"ALTER TABLE varieties ADD COLUMN IF NOT EXISTS {', ADD COLUMN IF NOT EXISTS '.join(all_columns)};"
    print(single_command)

def main():
    generate_sql_commands()

if __name__ == "__main__":
    main()
