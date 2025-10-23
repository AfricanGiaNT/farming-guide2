#!/usr/bin/env python3
"""
Check and Add Tomato Crop
Check if tomato crop exists in database and add if needed
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_and_add_tomato_crop():
    """Check if tomato crop exists and add if needed"""
    
    print("=" * 80)
    print("CHECKING AND ADDING TOMATO CROP")
    print("=" * 80)
    
    try:
        # Check if tomato crop exists
        result = supabase.table('crops').select('*').eq('crop_name', 'tomato').execute()
        
        if result.data:
            print("Tomato crop already exists in database:")
            crop = result.data[0]
            for key, value in crop.items():
                print(f"  {key}: {value}")
            return crop['id']
        else:
            print("Tomato crop not found. Adding new tomato crop...")
            
            # Add tomato crop
            crop_data = {
                'crop_name': 'tomato',
                'scientific_name': 'Lycopersicon esculentum',
                'local_name': 'Tomato',
                'category': 'Vegetables',
                'general_description': 'Tomatoes are widely grown throughout the country but there is need to improve quality and availability throughout the year. They can be grown all year round except in extremely hot dry conditions because, heat retards growth and fruit set. The soil should be free draining and rich in organic matter. Potential yield for tomatoes ranges from 18,000 to 50,000kg per hectare depending on variety.'
            }
            
            result = supabase.table('crops').insert(crop_data).execute()
            
            if result.data:
                print("OK Successfully added tomato crop to database")
                print(f"Crop ID: {result.data[0]['id']}")
                return result.data[0]['id']
            else:
                print("X Failed to add tomato crop")
                return None
                
    except Exception as e:
        print(f"Error checking/adding tomato crop: {str(e)}")
        return None

def main():
    crop_id = check_and_add_tomato_crop()
    if crop_id:
        print(f"\nTomato crop ID: {crop_id}")
    else:
        print("\nFailed to get tomato crop ID")

if __name__ == "__main__":
    main()
