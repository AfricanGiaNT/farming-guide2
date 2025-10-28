#!/usr/bin/env python3
"""
Verify the varieties table stays empty (no new records being added)
"""

from supabase import create_client, Client
import time

SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def check_count():
    """Get current varieties count"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    result = supabase.table("varieties").select("id", count="exact").execute()
    return result.count

def main():
    print("\nMONITORING VARIETIES TABLE")
    print("Checking if new records are being added...")
    print("Will check every 3 seconds for 15 seconds")
    print("=" * 60)
    
    checks = []
    
    for i in range(5):
        count = check_count()
        timestamp = time.strftime("%H:%M:%S")
        checks.append((timestamp, count))
        print(f"{timestamp} - Count: {count} varieties")
        
        if i < 4:
            time.sleep(3)
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    
    counts = [c[1] for c in checks]
    
    if all(c == 0 for c in counts):
        print("SUCCESS: Table stayed empty - no new records being added")
        print("Safe to proceed with new extraction")
    elif all(c == counts[0] for c in counts):
        print(f"STABLE: Table has {counts[0]} records but not increasing")
    else:
        print("WARNING: Record count is changing!")
        print("There may still be a process inserting data")
        print(f"Counts: {counts}")
        print("\nYou need to find and stop the insertion process!")
    
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()





