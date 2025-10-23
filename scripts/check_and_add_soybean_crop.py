#!/usr/bin/env python3
"""
Check and Add Soybean Crop
Check if soybean crop exists in database and add if needed
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_and_add_soybean_crop():
    """Check if soybean crop exists and add if needed"""
    
    print("=" * 80)
    print("CHECKING AND ADDING SOYBEAN CROP")
    print("=" * 80)
    
    try:
        # Check if soybean crop exists
        result = supabase.table('crops').select('*').eq('crop_name', 'soybean').execute()
        
        if result.data:
            print("Soybean crop already exists in database:")
            crop = result.data[0]
            for key, value in crop.items():
                print(f"  {key}: {value}")
            return crop['id']
        else:
            print("Soybean crop not found. Adding new soybean crop...")
            
            # Add soybean crop
            crop_data = {
                'crop_name': 'soybean',
                'scientific_name': 'Glycine max',
                'local_name': 'Soybean',
                'category': 'Legumes',
                'general_description': 'Soybean is a very important and versatile grain legume because it can be put to many uses. It provides high quality vegetable protein of around 37% CP and oil for humans and livestock consumption. It is used in the production of various other recipes at household and industrial levels such as the production of Likuni Phala, soya milk and soy meat. It is also used in the production of feeds for poultry and other livestock. The crop is also a good nitrogen fixer and it therefore improves soil fertility.'
            }
            
            result = supabase.table('crops').insert(crop_data).execute()
            
            if result.data:
                print("OK Successfully added soybean crop to database")
                print(f"Crop ID: {result.data[0]['id']}")
                return result.data[0]['id']
            else:
                print("X Failed to add soybean crop")
                return None
                
    except Exception as e:
        print(f"Error checking/adding soybean crop: {str(e)}")
        return None

def main():
    crop_id = check_and_add_soybean_crop()
    if crop_id:
        print(f"\nSoybean crop ID: {crop_id}")
    else:
        print("\nFailed to get soybean crop ID")

if __name__ == "__main__":
    main()
