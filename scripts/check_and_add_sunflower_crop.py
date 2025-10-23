#!/usr/bin/env python3
"""
Check and Add Sunflower Crop
Check if sunflower crop exists in database and add if needed
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_and_add_sunflower_crop():
    """Check if sunflower crop exists and add if needed"""
    
    print("=" * 80)
    print("CHECKING AND ADDING SUNFLOWER CROP")
    print("=" * 80)
    
    try:
        # Check if sunflower crop exists
        result = supabase.table('crops').select('*').eq('crop_name', 'sunflower').execute()
        
        if result.data:
            print("Sunflower crop already exists in database:")
            crop = result.data[0]
            for key, value in crop.items():
                print(f"  {key}: {value}")
            return crop['id']
        else:
            print("Sunflower crop not found. Adding new sunflower crop...")
            
            # Add sunflower crop
            crop_data = {
                'crop_name': 'sunflower',
                'scientific_name': 'Helianthus annuus',
                'local_name': 'Sunflower',
                'category': 'Oil Seeds',
                'general_description': 'Sunflower oil is one of the top quality edible oils and the cake is used in the production of livestock feed. It is therefore important to encourage increased production of sunflower in all suitable areas. A warm, fairly dry climate is considered optimal for sunflower production. The drier warmer areas with an annual rainfall of 650mm to 850mm and a low relative humidity are suitable for the growth of the crop.'
            }
            
            result = supabase.table('crops').insert(crop_data).execute()
            
            if result.data:
                print("OK Successfully added sunflower crop to database")
                print(f"Crop ID: {result.data[0]['id']}")
                return result.data[0]['id']
            else:
                print("X Failed to add sunflower crop")
                return None
                
    except Exception as e:
        print(f"Error checking/adding sunflower crop: {str(e)}")
        return None

def main():
    crop_id = check_and_add_sunflower_crop()
    if crop_id:
        print(f"\nSunflower crop ID: {crop_id}")
    else:
        print("\nFailed to get sunflower crop ID")

if __name__ == "__main__":
    main()
