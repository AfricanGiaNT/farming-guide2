#!/usr/bin/env python3
"""
Check and Add Ginger Crop
Check if ginger crop exists in database and add if needed
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_and_add_ginger_crop():
    """Check if ginger crop exists and add if needed"""
    
    print("=" * 80)
    print("CHECKING AND ADDING GINGER CROP")
    print("=" * 80)
    
    try:
        # Check if ginger crop exists
        result = supabase.table('crops').select('*').eq('crop_name', 'ginger').execute()
        
        if result.data:
            print("Ginger crop already exists in database:")
            crop = result.data[0]
            for key, value in crop.items():
                print(f"  {key}: {value}")
            return crop['id']
        else:
            print("Ginger crop not found. Adding new ginger crop...")
            
            # Add ginger crop
            crop_data = {
                'crop_name': 'ginger',
                'scientific_name': 'Zingiber officinale',
                'local_name': 'Ginger',
                'category': 'Spices',
                'general_description': 'Ginger is grown in Malawi as an annual crop. Freshly harvested ginger consists of tangled clumps of interconnected rhizomes known as races or hands and branches known as fingers. Ginger is used mainly for food seasoning, in baking, brewing and in the wine industry. The crop grows in altitude of up to 1,500m above sea level. It thrives under hot and humid conditions. High rainfall of 1,500 to 3,000 mm per year, well distributed over the 8 months growing period is ideal. Ginger grows well in different soil types with free draining characteristics.'
            }
            
            result = supabase.table('crops').insert(crop_data).execute()
            
            if result.data:
                print("OK Successfully added ginger crop to database")
                print(f"Crop ID: {result.data[0]['id']}")
                return result.data[0]['id']
            else:
                print("X Failed to add ginger crop")
                return None
                
    except Exception as e:
        print(f"Error checking/adding ginger crop: {str(e)}")
        return None

def main():
    crop_id = check_and_add_ginger_crop()
    if crop_id:
        print(f"\nGinger crop ID: {crop_id}")
    else:
        print("\nFailed to get ginger crop ID")

if __name__ == "__main__":
    main()
