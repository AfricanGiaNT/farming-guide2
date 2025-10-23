#!/usr/bin/env python3
"""
Clean Supabase Varieties Table
Remove all invalid/garbage entries before fresh extraction
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def cleanup_varieties():
    """Delete all varieties from Supabase"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 70)
    print("CLEANING VARIETIES TABLE")
    print("=" * 70)
    
    # Get current count
    try:
        result = supabase.table("varieties").select("id", count="exact").execute()
        current_count = result.count
        print(f"\nCurrent varieties count: {current_count}")
    except Exception as e:
        print(f"Error getting count: {e}")
        return False
    
    if current_count == 0:
        print("Table is already empty")
        return True
    
    # Confirm deletion
    print(f"\nWARNING: This will delete ALL {current_count} varieties from Supabase")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        print("Cancelled. No changes made.")
        return False
    
    print("\nStarting deletion...")
    
    # Delete all varieties
    try:
        print("\nDeleting varieties...")
        # Supabase doesn't have a simple "delete all" - we need to delete in batches
        
        # Get all variety IDs
        all_varieties = supabase.table("varieties").select("id").execute()
        variety_ids = [v["id"] for v in all_varieties.data]
        
        deleted = 0
        batch_size = 100
        
        for i in range(0, len(variety_ids), batch_size):
            batch = variety_ids[i:i+batch_size]
            for vid in batch:
                supabase.table("varieties").delete().eq("id", vid).execute()
                deleted += 1
            print(f"  Deleted {deleted}/{len(variety_ids)} varieties...")
        
        print(f"\nSuccessfully deleted {deleted} varieties")
        print("Varieties table is now clean")
        
        return True
        
    except Exception as e:
        print(f"\nError deleting varieties: {e}")
        return False

def verify_cleanup():
    """Verify table is empty"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        result = supabase.table("varieties").select("id", count="exact").execute()
        count = result.count
        
        if count == 0:
            print("\nVerification passed: Table is empty")
            return True
        else:
            print(f"\nVerification failed: Still {count} varieties remaining")
            return False
    except Exception as e:
        print(f"Error verifying: {e}")
        return False

def main():
    print("\nSUPABASE VARIETIES TABLE CLEANUP\n")
    
    if cleanup_varieties():
        verify_cleanup()
        print("\n" + "=" * 70)
        print("CLEANUP COMPLETE - Ready for fresh extraction")
        print("=" * 70 + "\n")
    else:
        print("\nCleanup failed or cancelled\n")

if __name__ == "__main__":
    main()

