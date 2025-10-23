#!/usr/bin/env python3
"""
Check Varieties in Database
Verify what varieties are actually in the varieties table
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_varieties_in_database():
    """Check what varieties are in the database"""
    
    print("=" * 80)
    print("CHECKING VARIETIES IN DATABASE")
    print("=" * 80)
    
    try:
        # Get all varieties
        result = supabase.table('varieties').select('*').execute()
        
        if result.data:
            print(f"Total varieties in database: {len(result.data)}")
            print("\nAll varieties:")
            
            # Group by crop
            crops = {}
            for variety in result.data:
                crop_name = variety.get('crop_name', 'Unknown')
                if crop_name not in crops:
                    crops[crop_name] = []
                crops[crop_name].append(variety)
            
            for crop_name, varieties in crops.items():
                print(f"\n{crop_name.upper()} ({len(varieties)} varieties):")
                for variety in varieties:
                    variety_name = variety.get('variety_name', 'Unknown')
                    table_source = variety.get('table_source', 'Unknown')
                    print(f"  - {variety_name} (from {table_source})")
            
            # Show detailed info for recent varieties
            print(f"\nDetailed information for recent varieties:")
            for variety in result.data[-5:]:  # Last 5 varieties
                print(f"\nVariety: {variety.get('variety_name', 'Unknown')}")
                print(f"  Crop: {variety.get('crop_name', 'Unknown')}")
                print(f"  Source: {variety.get('table_source', 'Unknown')}")
                print(f"  Originator: {variety.get('originator', 'N/A')}")
                print(f"  Type: {variety.get('type', 'N/A')}")
                print(f"  Yield: {variety.get('yield_potential', 'N/A')}")
                print(f"  Created: {variety.get('created_at', 'N/A')}")
                
        else:
            print("No varieties found in database")
            
    except Exception as e:
        print(f"Error checking varieties: {str(e)}")

def check_specific_crops():
    """Check varieties for specific crops"""
    
    print("\n" + "=" * 80)
    print("CHECKING SPECIFIC CROPS")
    print("=" * 80)
    
    crops_to_check = ['groundnut', 'soybean', 'rice', 'beans']
    
    for crop_name in crops_to_check:
        try:
            result = supabase.table('varieties').select('*').eq('crop_name', crop_name).execute()
            
            if result.data:
                print(f"\n{crop_name.upper()}: {len(result.data)} varieties")
                for variety in result.data:
                    variety_name = variety.get('variety_name', 'Unknown')
                    table_source = variety.get('table_source', 'Unknown')
                    print(f"  - {variety_name} (from {table_source})")
            else:
                print(f"\n{crop_name.upper()}: No varieties found")
                
        except Exception as e:
            print(f"Error checking {crop_name}: {str(e)}")

def main():
    check_varieties_in_database()
    check_specific_crops()

if __name__ == "__main__":
    main()
