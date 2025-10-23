#!/usr/bin/env python3
"""
Check and Add Groundnut Crop
Check if groundnut crop exists in database and add if needed
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_and_add_groundnut_crop():
    """Check if groundnut crop exists and add if needed"""
    
    print("=" * 80)
    print("CHECKING AND ADDING GROUNDNUT CROP")
    print("=" * 80)
    
    try:
        # Check if groundnut crop exists
        result = supabase.table('crops').select('*').eq('crop_name', 'groundnut').execute()
        
        if result.data:
            print("Groundnut crop already exists in database:")
            crop = result.data[0]
            for key, value in crop.items():
                print(f"  {key}: {value}")
            return crop['id']
        else:
            print("Groundnut crop not found. Adding new groundnut crop...")
            
            # Add groundnut crop
            crop_data = {
                'crop_name': 'groundnut',
                'scientific_name': 'Arachis hypogaea',
                'local_name': 'Groundnut',
                'category': 'Legumes',
                'general_description': 'Groundnut is one of the most important food and cash crops in Malawi. It is a good source of protein, vitamins and vegetable oils. Groundnut is capable of fixing atmospheric nitrogen and improves soil fertility when grown in rotation with other crops.'
            }
            
            result = supabase.table('crops').insert(crop_data).execute()
            
            if result.data:
                print("OK Successfully added groundnut crop to database")
                print(f"Crop ID: {result.data[0]['id']}")
                return result.data[0]['id']
            else:
                print("X Failed to add groundnut crop")
                return None
                
    except Exception as e:
        print(f"Error checking/adding groundnut crop: {str(e)}")
        return None

def main():
    crop_id = check_and_add_groundnut_crop()
    if crop_id:
        print(f"\nGroundnut crop ID: {crop_id}")
    else:
        print("\nFailed to get groundnut crop ID")

if __name__ == "__main__":
    main()
