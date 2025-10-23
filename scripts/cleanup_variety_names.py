#!/usr/bin/env python3
"""
Clean Up Rice Variety Names
Remove trailing periods and other formatting issues
"""

from supabase import create_client, Client

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def clean_up_variety_names():
    """Clean up rice variety names"""
    
    print("=" * 80)
    print("CLEANING UP RICE VARIETY NAMES")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all rice varieties
        result = supabase.table("varieties").select("id, variety_name").eq("crop_name", "rice").execute()
        
        if not result.data:
            print("No rice varieties found in database")
            return
        
        print(f"Found {len(result.data)} rice varieties")
        
        # Clean up variety names
        cleaned_count = 0
        for variety in result.data:
            original_name = variety['variety_name']
            cleaned_name = original_name.strip().rstrip('.,;')
            
            if original_name != cleaned_name:
                print(f"Cleaning: '{original_name}' -> '{cleaned_name}'")
                
                update_result = supabase.table("varieties").update({
                    "variety_name": cleaned_name
                }).eq("id", variety['id']).execute()
                
                if update_result.data:
                    print(f"  SUCCESS: Updated variety name")
                    cleaned_count += 1
                else:
                    print(f"  ERROR: Failed to update variety name")
        
        print(f"\nCleaned {cleaned_count} variety names")
        
        # Show final varieties
        print("\nFinal rice varieties:")
        varieties_result = supabase.table("varieties").select("variety_name, ecology, table_source").eq("crop_name", "rice").order("variety_name").execute()
        
        for variety in varieties_result.data:
            print(f"  - {variety['variety_name']} ({variety['ecology']}) - {variety['table_source']}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    clean_up_variety_names()

if __name__ == "__main__":
    main()
