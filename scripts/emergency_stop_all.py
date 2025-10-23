#!/usr/bin/env python3
"""
Emergency Stop - Kill all extraction processes and clear database
"""

import subprocess
import sys
import os
from supabase import create_client, Client

SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def stop_extraction_processes():
    """Stop any running extraction processes"""
    print("=" * 70)
    print("STOPPING ALL EXTRACTION PROCESSES")
    print("=" * 70)
    
    extraction_files = [
        "ai_powered_chapter3_extraction.py",
        "extract_chapter3_varieties.py",
        "extract_maize_bean_varieties.py",
        "extract_chapter3_varieties",
        "ai_powered_chapter3_extraction"
    ]
    
    try:
        # Get all Python processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\nPython processes found:")
            print(result.stdout)
            
            # Kill processes running extraction scripts
            for line in result.stdout.split('\n'):
                if any(script in line for script in extraction_files):
                    print(f"\nFound extraction process: {line}")
                    # Extract PID and kill
                    parts = line.split(',')
                    if len(parts) > 1:
                        pid = parts[1].strip('"')
                        print(f"Killing PID {pid}...")
                        subprocess.run(['taskkill', '/PID', pid, '/F'])
        
        print("\nExtraction processes stopped")
        
    except Exception as e:
        print(f"Error stopping processes: {e}")

def clear_varieties_fast():
    """Fast clear of varieties table"""
    print("\n" + "=" * 70)
    print("CLEARING VARIETIES TABLE")
    print("=" * 70)
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Check current count
        result = supabase.table("varieties").select("id", count="exact").execute()
        count = result.count
        print(f"\nCurrent count: {count} varieties")
        
        if count == 0:
            print("Table is already empty")
            return True
        
        # Delete all
        print(f"Deleting all {count} varieties...")
        all_data = supabase.table("varieties").select("id").execute()
        
        deleted = 0
        for item in all_data.data:
            supabase.table("varieties").delete().eq("id", item["id"]).execute()
            deleted += 1
            if deleted % 100 == 0:
                print(f"  Deleted {deleted}/{count}...")
        
        print(f"\nDeleted {deleted} varieties")
        
        # Verify
        result = supabase.table("varieties").select("id", count="exact").execute()
        final_count = result.count
        
        if final_count == 0:
            print("SUCCESS: Table is empty")
            return True
        else:
            print(f"WARNING: Still {final_count} varieties remaining")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("\nEMERGENCY STOP - EXTRACTION PROCESSES AND DATABASE CLEAR\n")
    
    # Stop all extraction processes first
    stop_extraction_processes()
    
    # Wait a moment
    import time
    time.sleep(2)
    
    # Clear database
    clear_varieties_fast()
    
    print("\n" + "=" * 70)
    print("EMERGENCY STOP COMPLETE")
    print("All extraction processes stopped")
    print("Varieties table cleared")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()



