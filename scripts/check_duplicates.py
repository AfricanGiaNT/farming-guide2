#!/usr/bin/env python3
"""
Check for Duplicates in Maize Varieties
Verify no duplicate varieties were inserted
"""

from supabase import create_client, Client

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def check_duplicates():
    """Check for duplicate varieties"""
    
    print("=" * 80)
    print("CHECKING FOR DUPLICATE MAIZE VARIETIES")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all maize varieties
        result = supabase.table("varieties").select("*").eq("crop_name", "maize").execute()
        
        if not result.data:
            print("No maize varieties found in database")
            return
        
        varieties = result.data
        print(f"Total maize varieties in database: {len(varieties)}")
        
        # Check for duplicates by variety name
        variety_names = [v["variety_name"] for v in varieties]
        unique_names = set(variety_names)
        
        print(f"Unique variety names: {len(unique_names)}")
        
        if len(variety_names) != len(unique_names):
            print("\nDUPLICATES FOUND!")
            
            # Find duplicates
            from collections import Counter
            name_counts = Counter(variety_names)
            duplicates = {name: count for name, count in name_counts.items() if count > 1}
            
            print(f"Duplicate varieties:")
            for name, count in duplicates.items():
                print(f"  - {name}: {count} times")
                
                # Show details of duplicate entries
                duplicate_entries = [v for v in varieties if v["variety_name"] == name]
                for i, entry in enumerate(duplicate_entries, 1):
                    print(f"    Entry {i}: ID={entry['id']}, Originator={entry.get('originator', 'N/A')}")
        else:
            print("\nNO DUPLICATES FOUND!")
            print("All maize varieties are unique")
        
        # Check for similar names that might be duplicates
        print(f"\nChecking for similar variety names...")
        similar_pairs = []
        
        for i, name1 in enumerate(unique_names):
            for j, name2 in enumerate(list(unique_names)[i+1:], i+1):
                # Check for very similar names
                if (name1.lower().replace(" ", "") == name2.lower().replace(" ", "") or
                    name1.lower().replace("-", "") == name2.lower().replace("-", "") or
                    (len(name1) > 3 and len(name2) > 3 and 
                     name1.lower()[:4] == name2.lower()[:4] and 
                     abs(len(name1) - len(name2)) <= 2)):
                    similar_pairs.append((name1, name2))
        
        if similar_pairs:
            print(f"\nPOTENTIALLY SIMILAR NAMES:")
            for name1, name2 in similar_pairs:
                print(f"  - {name1} vs {name2}")
        else:
            print(f"\nNo similar names found")
        
        # Show sample of varieties with their details
        print(f"\nSample of extracted varieties:")
        for i, variety in enumerate(varieties[:10], 1):
            print(f"  {i}. {variety['variety_name']}")
            print(f"     Originator: {variety.get('originator', 'N/A')}")
            print(f"     Type: {variety.get('type', 'N/A')}")
            print(f"     Days to Maturity: {variety.get('maturity_days', 'N/A')}")
            print(f"     Yield: {variety.get('yield_potential', 'N/A')}")
            print()
        
        return len(variety_names) == len(unique_names)
        
    except Exception as e:
        print(f"Error checking duplicates: {e}")
        return False

def main():
    print("DUPLICATE CHECK FOR MAIZE VARIETIES")
    print("Verifying data integrity after extraction")
    
    is_clean = check_duplicates()
    
    print("\n" + "=" * 80)
    if is_clean:
        print("DATA INTEGRITY VERIFIED")
        print("No duplicates found - extraction is clean")
    else:
        print("DATA INTEGRITY ISSUES FOUND")
        print("Duplicates detected - manual review needed")
    print("=" * 80)

if __name__ == "__main__":
    main()

