#!/usr/bin/env python3
"""
Check and Add Cassava Crop
Check if cassava crop exists in database and add if needed
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_and_add_cassava_crop():
    """Check if cassava crop exists and add if needed"""
    
    print("=" * 80)
    print("CHECKING AND ADDING CASSAVA CROP")
    print("=" * 80)
    
    try:
        # Check if cassava crop exists
        result = supabase.table('crops').select('*').eq('crop_name', 'cassava').execute()
        
        if result.data:
            print("Cassava crop already exists in database:")
            crop = result.data[0]
            for key, value in crop.items():
                print(f"  {key}: {value}")
            return crop['id']
        else:
            print("Cassava crop not found. Adding new cassava crop...")
            
            # Add cassava crop
            crop_data = {
                'crop_name': 'cassava',
                'scientific_name': 'Manihot esculenta',
                'local_name': 'Cassava',
                'category': 'Root and Tuber Crops',
                'general_description': 'Cassava is a staple food crop in the lake shore areas of Nkhotakota, Nkhata bay, Rumphi and Karonga. In some districts of Malawi such as Mzimba, Kasungu, Lilongwe, Dedza, Dowa, Machinga and Mulanje cassava is becoming a major cash crop. The main advantages of growing cassava are its drought tolerance, ability to yield well on marginal soils, tolerance to some pests and diseases, minimal labour requirement and that yields fluctuate less compared to grain crops.'
            }
            
            result = supabase.table('crops').insert(crop_data).execute()
            
            if result.data:
                print("OK Successfully added cassava crop to database")
                print(f"Crop ID: {result.data[0]['id']}")
                return result.data[0]['id']
            else:
                print("X Failed to add cassava crop")
                return None
                
    except Exception as e:
        print(f"Error checking/adding cassava crop: {str(e)}")
        return None

def main():
    crop_id = check_and_add_cassava_crop()
    if crop_id:
        print(f"\nCassava crop ID: {crop_id}")
    else:
        print("\nFailed to get cassava crop ID")

if __name__ == "__main__":
    main()
