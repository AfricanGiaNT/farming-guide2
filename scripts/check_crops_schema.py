#!/usr/bin/env python3
"""
Check Crops Table Schema
See what columns actually exist in the crops table
"""

from supabase import create_client, Client

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def check_crops_schema():
    """Check the crops table schema"""
    
    print("=" * 80)
    print("CHECKING CROPS TABLE SCHEMA")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get an existing crop to see the schema
        result = supabase.table("crops").select("*").limit(1).execute()
        
        if result.data:
            print("SUCCESS: Found existing crop")
            crop = result.data[0]
            print(f"Crop: {crop['crop_name']}")
            print("\nAvailable columns:")
            for key, value in crop.items():
                print(f"  {key}: {type(value).__name__}")
            
            # Try to add beans with only the columns that exist
            print(f"\nTrying to add beans crop with existing columns...")
            
            beans_data = {}
            for key in crop.keys():
                if key == 'id':
                    continue  # Skip ID
                elif key == 'crop_name':
                    beans_data[key] = 'beans'
                elif key == 'scientific_name':
                    beans_data[key] = 'Phaseolus vulgaris'
                elif key == 'description':
                    beans_data[key] = 'Beans are a good source of protein and income.'
                else:
                    beans_data[key] = crop[key]  # Use same value as existing crop
            
            print(f"Beans data to insert: {beans_data}")
            
            insert_result = supabase.table("crops").insert(beans_data).execute()
            
            if insert_result.data:
                print(f"SUCCESS: Beans crop added successfully: ID {insert_result.data[0]['id']}")
                return insert_result.data[0]['id']
            else:
                print("ERROR: Failed to add beans crop")
                return None
        else:
            print("ERROR: No existing crops found")
            return None
                
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    crop_id = check_crops_schema()
    if crop_id:
        print(f"\nBeans crop ID: {crop_id}")
        print("Ready to insert bean varieties!")
    else:
        print("\nFailed to add beans crop.")

if __name__ == "__main__":
    main()
