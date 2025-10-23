#!/usr/bin/env python3
"""
Supabase Configuration and Client Setup
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseVarietiesAPI:
    """API for varieties using Supabase"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def get_crops(self):
        """Get all crops"""
        try:
            result = self.supabase.table("crops").select("*").execute()
            return result.data
        except Exception as e:
            print(f"Error fetching crops: {e}")
            return []
    
    def get_crop_by_name(self, crop_name: str):
        """Get crop by name"""
        try:
            result = self.supabase.table("crops").select("*").eq("crop_name", crop_name).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error fetching crop {crop_name}: {e}")
            return None
    
    def get_varieties_by_crop(self, crop_name: str):
        """Get varieties for a specific crop"""
        try:
            # First get the crop ID
            crop = self.get_crop_by_name(crop_name)
            if not crop:
                return []
            
            # Get varieties for this crop
            result = self.supabase.table("varieties").select("*").eq("crop_id", crop["id"]).execute()
            return result.data
        except Exception as e:
            print(f"Error fetching varieties for {crop_name}: {e}")
            return []
    
    def get_variety_by_name(self, crop_name: str, variety_name: str):
        """Get specific variety by crop and variety name"""
        try:
            crop = self.get_crop_by_name(crop_name)
            if not crop:
                return None
            
            result = self.supabase.table("varieties").select("*").eq("crop_id", crop["id"]).eq("variety_name", variety_name).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error fetching variety {variety_name} for {crop_name}: {e}")
            return None
    
    def search_varieties(self, query: str):
        """Search varieties by name"""
        try:
            result = self.supabase.table("varieties").select("*, crops(crop_name)").ilike("variety_name", f"%{query}%").execute()
            return result.data
        except Exception as e:
            print(f"Error searching varieties: {e}")
            return []

# Test the API
if __name__ == "__main__":
    api = SupabaseVarietiesAPI()
    
    print("Testing Supabase Varieties API...")
    print("=" * 40)
    
    # Test getting crops
    crops = api.get_crops()
    print(f"Total crops: {len(crops)}")
    
    # Test getting maize varieties
    maize_varieties = api.get_varieties_by_crop("maize")
    print(f"\nMaize varieties: {len(maize_varieties)}")
    for variety in maize_varieties:
        print(f"  - {variety['variety_name']} ({variety['type']}) - {variety['maturity_days']} days")
    
    # Test getting specific variety
    sc403 = api.get_variety_by_name("maize", "SC403")
    if sc403:
        print(f"\nSC403 details:")
        print(f"  Yield: {sc403['yield_potential']}")
        print(f"  Drought tolerance: {sc403['drought_tolerance']}")
        print(f"  Disease resistance: {sc403['disease_resistance']}")
