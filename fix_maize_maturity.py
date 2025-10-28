#!/usr/bin/env python3
"""
Fix incorrect maturity days for maize varieties
"""

from supabase import create_client
from typing import List, Dict
import json

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def fix_maize_maturity():
    """Fix incorrect maturity days for maize varieties"""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get all maize varieties
    result = supabase.table("varieties").select("id, variety_name, maturity_days").eq("crop_name", "maize").execute()
    varieties = result.data
    
    # Find varieties with incorrect maturity days
    incorrect_varieties = []
    for variety in varieties:
        if variety.get('maturity_days', 0) > 200:  # Anything over 200 days is likely incorrect
            incorrect_varieties.append(variety)
    
    print(f"Found {len(incorrect_varieties)} varieties with potentially incorrect maturity days:")
    for variety in incorrect_varieties:
        print(f"  {variety['variety_name']}: {variety['maturity_days']} days (ID: {variety['id']})")
    
    # Fix incorrect values
    fixed = 0
    for variety in incorrect_varieties:
        # Determine correct maturity days based on variety name
        correct_maturity = None
        
        # DK and DKC varieties are typically medium-late maturing
        if "DK" in variety['variety_name']:
            if "777" in variety['variety_name']:  # 700 series - late maturing
                correct_maturity = 155
            elif "803" in variety['variety_name']:  # 800 series - late maturing
                correct_maturity = 155
            else:
                correct_maturity = 145  # Default to medium-late maturity
        
        # Update variety if we determined a correct maturity value
        if correct_maturity:
            try:
                # Update the variety
                supabase.table("varieties").update({"maturity_days": correct_maturity}).eq("id", variety['id']).execute()
                print(f"  + Fixed {variety['variety_name']}: {variety['maturity_days']} -> {correct_maturity} days")
                fixed += 1
            except Exception as e:
                print(f"  - Error fixing {variety['variety_name']}: {e}")
    
    print(f"\nFixed {fixed} out of {len(incorrect_varieties)} varieties")
    return fixed

if __name__ == "__main__":
    print("=" * 80)
    print("FIXING INCORRECT MAIZE MATURITY DAYS")
    print("=" * 80)
    
    fixed = fix_maize_maturity()
    
    print(f"\n{'='*80}")
    print(f"COMPLETED: Fixed {fixed} varieties")
    print(f"{'='*80}")
