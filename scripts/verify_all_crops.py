#!/usr/bin/env python3
"""
Verify All Crops
Verifies all extracted crops for duplicates and quality
"""

from supabase import create_client, Client
import sys

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def verify_all_crops():
    """Verify all crops for duplicates and quality"""
    
    print("=" * 80)
    print("VERIFYING ALL EXTRACTED CROPS")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all varieties grouped by crop
        result = supabase.table("varieties").select("*").execute()
        
        if not result.data:
            print("No varieties found in database")
            return
        
        varieties = result.data
        
        # Group by crop
        crops = {}
        for variety in varieties:
            crop_name = variety["crop_name"]
            if crop_name not in crops:
                crops[crop_name] = []
            crops[crop_name].append(variety)
        
        print(f"Total varieties: {len(varieties)}")
        print(f"Crops with varieties: {len(crops)}")
        
        total_duplicates = 0
        total_similar = 0
        
        for crop_name, crop_varieties in crops.items():
            print(f"\n{'='*60}")
            print(f"CROP: {crop_name.upper()}")
            print(f"Varieties: {len(crop_varieties)}")
            
            # Check for duplicates
            variety_names = [v["variety_name"] for v in crop_varieties]
            unique_names = set(variety_names)
            
            if len(variety_names) != len(unique_names):
                print(f"DUPLICATES FOUND: {len(variety_names) - len(unique_names)}")
                total_duplicates += len(variety_names) - len(unique_names)
                
                from collections import Counter
                name_counts = Counter(variety_names)
                duplicates = {name: count for name, count in name_counts.items() if count > 1}
                
                for name, count in duplicates.items():
                    print(f"  - {name}: {count} times")
            else:
                print("No duplicates found")
            
            # Check for missing data
            missing_originator = sum(1 for v in crop_varieties if not v.get("originator"))
            missing_maturity = sum(1 for v in crop_varieties if not v.get("maturity_days"))
            missing_yield = sum(1 for v in crop_varieties if not v.get("yield_potential") or v.get("yield_potential") == "medium")
            
            if missing_originator or missing_maturity or missing_yield:
                print(f"Missing data:")
                if missing_originator:
                    print(f"  - Originator: {missing_originator}")
                if missing_maturity:
                    print(f"  - Maturity days: {missing_maturity}")
                if missing_yield:
                    print(f"  - Yield info: {missing_yield}")
            else:
                print("All data complete")
            
            # Show sample varieties
            print(f"Sample varieties:")
            for i, variety in enumerate(crop_varieties[:3], 1):
                print(f"  {i}. {variety['variety_name']}")
                print(f"     Originator: {variety.get('originator', 'N/A')}")
                print(f"     Type: {variety.get('type', 'N/A')}")
                print(f"     Maturity: {variety.get('maturity_days', 'N/A')} days")
                print(f"     Yield: {variety.get('yield_potential', 'N/A')}")
        
        # Overall summary
        print(f"\n{'='*80}")
        print("OVERALL VERIFICATION SUMMARY")
        print(f"{'='*80}")
        print(f"Total varieties: {len(varieties)}")
        print(f"Crops processed: {len(crops)}")
        print(f"Total duplicates: {total_duplicates}")
        
        if total_duplicates == 0:
            print("STATUS: ALL CLEAN - No duplicates found")
        else:
            print("STATUS: ISSUES FOUND - Duplicates detected")
        
        # Show crop breakdown
        print(f"\nCrop breakdown:")
        for crop_name, crop_varieties in sorted(crops.items()):
            print(f"  {crop_name}: {len(crop_varieties)} varieties")
        
        return total_duplicates == 0
        
    except Exception as e:
        print(f"Error verifying crops: {e}")
        return False

def main():
    print("VERIFY ALL EXTRACTED CROPS")
    print("Checking for duplicates and data quality")
    
    is_clean = verify_all_crops()
    
    print(f"\n{'='*80}")
    if is_clean:
        print("VERIFICATION COMPLETE - ALL CLEAN")
    else:
        print("VERIFICATION COMPLETE - ISSUES FOUND")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

