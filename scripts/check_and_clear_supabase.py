#!/usr/bin/env python3
"""
Check current state and clear Supabase varieties table
"""

from supabase import create_client, Client
import time

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def check_current_state():
    """Check what's currently in the database"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 70)
    print("CHECKING CURRENT SUPABASE STATE")
    print("=" * 70)
    
    # Get total count
    result = supabase.table("varieties").select("id", count="exact").execute()
    total = result.count
    print(f"\nTotal varieties in database: {total}")
    
    # Sample some varieties
    if total > 0:
        sample = supabase.table("varieties").select("crop_name, variety_name").limit(20).execute()
        print("\nSample varieties:")
        for v in sample.data:
            print(f"  - {v['crop_name']}: {v['variety_name']}")
    
    # Get counts by crop
    crops_result = supabase.table("crops").select("crop_name").execute()
    print(f"\n\nVarieties by crop:")
    for crop in crops_result.data:
        crop_name = crop['crop_name']
        count_result = supabase.table("varieties").select("id", count="exact").eq("crop_name", crop_name).execute()
        count = count_result.count
        if count > 0:
            print(f"  {crop_name}: {count}")
    
    return total

def clear_all_varieties():
    """Clear all varieties using direct SQL-like approach"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("\n" + "=" * 70)
    print("CLEARING ALL VARIETIES")
    print("=" * 70)
    
    try:
        # Get all IDs first
        all_data = supabase.table("varieties").select("id").execute()
        total = len(all_data.data)
        
        print(f"\nFound {total} varieties to delete")
        
        if total == 0:
            print("Table is already empty!")
            return True
        
        print("Deleting in batches...")
        
        deleted = 0
        batch_size = 50  # Smaller batches for reliability
        
        for i in range(0, total, batch_size):
            batch = all_data.data[i:i+batch_size]
            for item in batch:
                try:
                    supabase.table("varieties").delete().eq("id", item["id"]).execute()
                    deleted += 1
                except Exception as e:
                    print(f"  Error deleting ID {item['id']}: {e}")
            
            print(f"  Progress: {deleted}/{total} deleted")
            time.sleep(0.1)  # Small delay to avoid rate limits
        
        print(f"\nDeleted {deleted} varieties")
        return True
        
    except Exception as e:
        print(f"\nError during deletion: {e}")
        return False

def verify_empty():
    """Verify table is empty"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    result = supabase.table("varieties").select("id", count="exact").execute()
    count = result.count
    
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    if count == 0:
        print("\nSUCCESS: Varieties table is empty")
        return True
    else:
        print(f"\nWARNING: Still {count} varieties in table")
        return False

def main():
    print("\nSUPABASE VARIETIES TABLE - CHECK AND CLEAR\n")
    
    # Check current state
    current = check_current_state()
    
    if current == 0:
        print("\n\nTable is already empty - nothing to do")
        return
    
    # Clear all
    print("\n\nProceeding to clear all varieties...")
    time.sleep(1)
    
    if clear_all_varieties():
        time.sleep(1)
        verify_empty()
    
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()



