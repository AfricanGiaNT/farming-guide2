#!/usr/bin/env python3
"""
Final Cleanup of Beans Varieties
Remove remaining problematic entries that are not Phaseolus bean varieties
"""

from supabase import create_client, Client
import re

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def final_cleanup_beans_varieties():
    """Final cleanup of remaining problematic bean variety entries"""
    
    print("=" * 80)
    print("FINAL CLEANUP OF BEANS VARIETIES")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all beans varieties
        result = supabase.table("varieties").select("id, variety_name, table_source").eq("crop_name", "beans").execute()
        
        if not result.data:
            print("No beans varieties found in database")
            return
        
        print(f"Found {len(result.data)} beans varieties")
        
        # Define remaining problematic patterns (groundnut varieties and text fragments)
        problematic_patterns = [
            r'.*disease.*caused.*bacteria.*',  # Text fragments with disease info
            r'Baka',  # Groundnut variety
            r'Chitala',  # Groundnut variety
            r'Kakoma',  # Groundnut variety
            r'Nsinjiro',  # Groundnut variety
        ]
        
        problematic_varieties = []
        
        for variety in result.data:
            variety_name = variety['variety_name']
            
            # Check if variety name matches problematic patterns
            for pattern in problematic_patterns:
                if re.search(pattern, variety_name, re.IGNORECASE):
                    problematic_varieties.append(variety)
                    break
        
        print(f"\nFound {len(problematic_varieties)} remaining problematic varieties:")
        for variety in problematic_varieties:
            print(f"  - {variety['variety_name']} (ID: {variety['id']}, Source: {variety['table_source']})")
        
        if problematic_varieties:
            print(f"\nDeleting {len(problematic_varieties)} remaining problematic varieties...")
            
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
            print("\nNo remaining problematic varieties found. All beans varieties are clean!")
        
        # Show final count
        final_result = supabase.table("varieties").select("id").eq("crop_name", "beans").execute()
        print(f"\nFinal beans variety count: {len(final_result.data)}")
        
        # Show remaining varieties
        print("\nFinal clean beans varieties:")
        varieties_result = supabase.table("varieties").select("variety_name, grain_texture, table_source").eq("crop_name", "beans").order("variety_name").execute()
        
        for variety in varieties_result.data:
            print(f"  - {variety['variety_name']} ({variety['grain_texture']}) - {variety['table_source']}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    final_cleanup_beans_varieties()

if __name__ == "__main__":
    main()
