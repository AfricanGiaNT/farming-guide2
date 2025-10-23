#!/usr/bin/env python3
"""
Check and Add Onion Crop
Check if onion crop exists in database and add if needed
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_and_add_onion_crop():
    """Check if onion crop exists and add if needed"""
    
    print("=" * 80)
    print("CHECKING AND ADDING ONION CROP")
    print("=" * 80)
    
    try:
        # Check if onion crop exists
        result = supabase.table('crops').select('*').eq('crop_name', 'onion').execute()
        
        if result.data:
            print("Onion crop already exists in database:")
            crop = result.data[0]
            for key, value in crop.items():
                print(f"  {key}: {value}")
            return crop['id']
        else:
            print("Onion crop not found. Adding new onion crop...")
            
            # Add onion crop
            crop_data = {
                'crop_name': 'onion',
                'scientific_name': 'Allium cepa',
                'local_name': 'Onion',
                'category': 'Vegetables',
                'general_description': 'Onions are widely grown throughout the country both for food and for cash. They require cool to warm seasons for good bulb formation. Soils should be rich in organic matter and free draining. The crop should be sown from mid-February to April. Potential yields for onions range from 22,000kg to 24,000kg per hectare.'
            }
            
            result = supabase.table('crops').insert(crop_data).execute()
            
            if result.data:
                print("OK Successfully added onion crop to database")
                print(f"Crop ID: {result.data[0]['id']}")
                return result.data[0]['id']
            else:
                print("X Failed to add onion crop")
                return None
                
    except Exception as e:
        print(f"Error checking/adding onion crop: {str(e)}")
        return None

def main():
    crop_id = check_and_add_onion_crop()
    if crop_id:
        print(f"\nOnion crop ID: {crop_id}")
    else:
        print("\nFailed to get onion crop ID")

if __name__ == "__main__":
    main()
