#!/usr/bin/env python3
"""
Clean Up Beans Varieties
Remove problematic variety entries that were incorrectly extracted
"""

from supabase import create_client, Client
import re

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def clean_up_beans_varieties():
    """Clean up problematic bean variety entries"""
    
    print("=" * 80)
    print("CLEANING UP BEANS VARIETIES")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all beans varieties
        result = supabase.table("varieties").select("id, variety_name, table_source").eq("crop_name", "beans").execute()
        
        if not result.data:
            print("No beans varieties found in database")
            return
        
        print(f"Found {len(result.data)} beans varieties")
        
        # Define problematic patterns (including CG varieties which are groundnut varieties, not beans)
        problematic_patterns = [
            r'^CG\s+\d+$',  # CG 7, CG 8, etc. (these are groundnut varieties, not beans)
            r'^\d+\s+\d+\s+\d+$',  # 457 598 215, etc.
            r'^\d+\s+\d+$',  # 547, 091 534 176, etc.
            r'^\d+$',  # Only numbers
            r'^[0-9\s]+$',  # Only numbers and spaces
            r'^[0-9]+[a-zA-Z]*$',  # Numbers followed by letters
            r'^\(.*\)',  # Starts with parentheses
            r'being promoted',  # Text fragments
            r'Average \d+',  # Average 331
            r'Spanish types',  # Spanish types - CG 12
            r'Chalimbana Average',  # Chalimbana Average 331
            r'893 2005',  # Specific problematic entries
            r'091 534 176',  # Specific problematic entries
            r'457 598 215',  # Specific problematic entries
            r'547',  # Specific problematic entries
            r'CG 7',  # Groundnut varieties (should be in groundnut crop, not beans)
            r'CG 8',  # Groundnut varieties
            r'CG 9',  # Groundnut varieties
            r'CG 10',  # Groundnut varieties
            r'CG 11',  # Groundnut varieties
            r'CG 12',  # Groundnut varieties
            r'CG 13',  # Groundnut varieties
            r'CG 14',  # Groundnut varieties
        ]
        
        problematic_varieties = []
        
        for variety in result.data:
            variety_name = variety['variety_name']
            
            # Check if variety name matches problematic patterns
            for pattern in problematic_patterns:
                if re.match(pattern, variety_name, re.IGNORECASE):
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
            print("\nNo problematic varieties found. All beans varieties are clean!")
        
        # Show final count
        final_result = supabase.table("varieties").select("id").eq("crop_name", "beans").execute()
        print(f"\nFinal beans variety count: {len(final_result.data)}")
        
        # Show remaining varieties
        print("\nRemaining beans varieties:")
        varieties_result = supabase.table("varieties").select("variety_name, grain_texture, table_source").eq("crop_name", "beans").order("variety_name").execute()
        
        for variety in varieties_result.data:
            print(f"  - {variety['variety_name']} ({variety['grain_texture']}) - {variety['table_source']}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    clean_up_beans_varieties()

if __name__ == "__main__":
    main()
