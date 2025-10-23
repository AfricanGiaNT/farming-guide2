#!/usr/bin/env python3
"""
Check and Add Beans Crop to Database (Simple Version)
Ensure beans crop exists in the crops table before inserting varieties
"""

from supabase import create_client, Client

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def check_and_add_beans_crop():
    """Check if beans crop exists and add if needed"""
    
    print("=" * 80)
    print("CHECKING BEANS CROP IN DATABASE")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Check if beans exists
        result = supabase.table("crops").select("id, crop_name").eq("crop_name", "beans").execute()
        
        if result.data:
            print(f"SUCCESS: Beans crop found: ID {result.data[0]['id']}")
            return result.data[0]['id']
        else:
            print("WARNING: Beans crop not found. Adding beans crop...")
            
            # Add beans crop with minimal required fields
            beans_data = {
                "crop_name": "beans",
                "scientific_name": "Phaseolus vulgaris",
                "category": "legume",
                "description": "Beans are a good source of protein and income. The green leaves are valuable vegetables.",
                "planting_season": "rainy_season",
                "harvest_season": "dry_season",
                "water_requirements": "moderate",
                "soil_type": "well_drained",
                "climate_zone": "tropical",
                "growth_period_days": 85,
                "yield_per_hectare": "2000 kg",
                "nutritional_value": "High protein content",
                "uses": "Food, animal feed",
                "storage_requirements": "Dry storage",
                "pest_resistance": "moderate",
                "disease_resistance": "moderate",
                "drought_tolerance": "moderate",
                "flood_tolerance": "low",
                "fertilizer_requirements": "23:10:5+6S+1.0Zn at 100kg/ha",
                "irrigation_needs": "low",
                "spacing_requirements": "45cm apart",
                "planting_method": "direct_seeding",
                "harvesting_method": "manual",
                "processing_requirements": "threshing",
                "market_demand": "high",
                "price_per_kg": "variable",
                "export_potential": "moderate",
                "local_consumption": "high"
            }
            
            result = supabase.table("crops").insert(beans_data).execute()
            
            if result.data:
                print(f"SUCCESS: Beans crop added successfully: ID {result.data[0]['id']}")
                return result.data[0]['id']
            else:
                print("ERROR: Failed to add beans crop")
                return None
                
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    crop_id = check_and_add_beans_crop()
    if crop_id:
        print(f"\nBeans crop ID: {crop_id}")
        print("Ready to insert bean varieties!")
    else:
        print("\nFailed to ensure beans crop exists. Cannot proceed with variety insertion.")

if __name__ == "__main__":
    main()
