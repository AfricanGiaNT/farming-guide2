#!/usr/bin/env python3
"""
Clean Up Rice Varieties
Remove any problematic variety entries that were incorrectly extracted
"""

from supabase import create_client, Client

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def clean_up_rice_varieties():
    """Clean up problematic rice variety entries"""
    
    print("=" * 80)
    print("CLEANING UP RICE VARIETIES")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all rice varieties
        result = supabase.table("varieties").select("id, variety_name, table_source").eq("crop_name", "rice").execute()
        
        if not result.data:
            print("No rice varieties found in database")
            return
        
        print(f"Found {len(result.data)} rice varieties")
        
        # Define problematic patterns
        problematic_patterns = [
            r'^\d+',  # Starts with numbers
            r'^\d+\s+to\s+\d+',  # Number ranges
            r'^\d+\s+\d+',  # Multiple numbers
            r'^\d+$',  # Only numbers
            r'^[0-9\s]+$',  # Only numbers and spaces
            r'^[0-9]+[a-zA-Z]*$',  # Numbers followed by letters
        ]
        
        import re
        problematic_varieties = []
        
        for variety in result.data:
            variety_name = variety['variety_name']
            
            # Check if variety name matches problematic patterns
            for pattern in problematic_patterns:
                if re.match(pattern, variety_name):
                    problematic_varieties.append(variety)
                    break
        
        print(f"\nFound {len(problematic_varieties)} problematic varieties:")
        for variety in problematic_varieties:
            print(f"  - {variety['variety_name']} (ID: {variety['id']}, Source: {variety['table_source']})")
        
        if problematic_varieties:
            print(f"\nDeleting {len(problematic_varieties)} problematic varieties...")
            
            for variety in problematic_varieties:
                try:
                    delete_result = supabase.table("varieties").delete().eq("id", variety['id']).execute()
                    if delete_result.data:
                        print(f"  SUCCESS: Deleted {variety['variety_name']}")
                    else:
                        print(f"  ERROR: Failed to delete {variety['variety_name']}")
                except Exception as e:
                    print(f"  ERROR: Error deleting {variety['variety_name']}: {e}")
        else:
            print("\nNo problematic varieties found. All rice varieties are clean!")
        
        # Show final count
        final_result = supabase.table("varieties").select("id").eq("crop_name", "rice").execute()
        print(f"\nFinal rice variety count: {len(final_result.data)}")
        
        # Show remaining varieties
        print("\nRemaining rice varieties:")
        varieties_result = supabase.table("varieties").select("variety_name, ecology, table_source").eq("crop_name", "rice").order("variety_name").execute()
        
        for variety in varieties_result.data:
            print(f"  - {variety['variety_name']} ({variety['ecology']}) - {variety['table_source']}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    clean_up_rice_varieties()

if __name__ == "__main__":
    main()
