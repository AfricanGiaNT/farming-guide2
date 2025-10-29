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
    try:
        # Try to get from environment first (for Render deployment)
        url = os.getenv('SUPABASE_URL', SUPABASE_URL)
        key = os.getenv('SUPABASE_KEY', SUPABASE_KEY)
        return create_client(url, key)
    except TypeError as e:
        # Handle version compatibility issues
        if 'proxy' in str(e).lower() or 'unexpected keyword' in str(e).lower():
            # Try without any additional parameters
            from supabase import create_client as create_supabase_client
            return create_supabase_client(url, key)
        raise
    except Exception as e:
        print(f"⚠️ Error creating Supabase client: {e}")
        raise

class SupabaseVarietiesAPI:
    """API for varieties using Supabase"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 3
    
    def _ensure_connection(self):
        """Ensure Supabase connection is active, reconnect if needed"""
        try:
            # Simple health check - try to query crops table
            self.supabase.table("crops").select("id").limit(1).execute()
            self._reconnect_attempts = 0  # Reset on success
        except Exception as e:
            if "disconnected" in str(e).lower() or "connection" in str(e).lower():
                print(f"⚠️ Supabase connection issue detected: {e}")
                if self._reconnect_attempts < self._max_reconnect_attempts:
                    self._reconnect_attempts += 1
                    print(f"🔄 Reconnecting to Supabase (attempt {self._reconnect_attempts}/{self._max_reconnect_attempts})...")
                    self.supabase = get_supabase_client()
                else:
                    print(f"❌ Max reconnection attempts reached")
                    raise
            else:
                raise
    
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
            self._ensure_connection()
            result = self.supabase.table("crops").select("*").eq("crop_name", crop_name).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error fetching crop {crop_name}: {e}")
            return None
    
    def get_varieties_by_crop(self, crop_name: str):
        """Get varieties for a specific crop - tries multiple name variants"""
        try:
            self._ensure_connection()
            # Try the given crop name first
            crop = self.get_crop_by_name(crop_name)
            
            # If not found, try common variants
            if not crop:
                # Common name variants to try as fallbacks
                variant_map = {
                    'beans': ['phaseolus beans', 'phaseolus-beans', 'phaseolus_beans'],
                    'phaseolus beans': ['beans', 'phaseolus-beans', 'phaseolus_beans'],
                    'phaseolus-beans': ['beans', 'phaseolus beans', 'phaseolus_beans'],
                    'groundnuts': ['groundnut'],
                    'groundnut': ['groundnuts'],
                }
                
                crop_lower = crop_name.lower()
                if crop_lower in variant_map:
                    for variant in variant_map[crop_lower]:
                        crop = self.get_crop_by_name(variant)
                        if crop:
                            print(f"✅ Found crop '{variant}' instead of '{crop_name}'")
                            break
                else:
                    # Try a few common variations for any crop name
                    # Remove spaces, add spaces, etc.
                    alt_names = [
                        crop_name.replace(' ', '_'),
                        crop_name.replace('_', ' '),
                        crop_name.replace('-', ' '),
                        crop_name.replace(' ', '-'),
                    ]
                    for alt in set(alt_names):  # Use set to avoid duplicates
                        if alt.lower() != crop_lower:
                            crop = self.get_crop_by_name(alt)
                            if crop:
                                print(f"✅ Found crop '{alt}' instead of '{crop_name}'")
                                break
            
            if not crop:
                print(f"No crop found for '{crop_name}' (tried variants)")
                return []
            
            # Get varieties for this crop
            self._ensure_connection()
            crop_id = crop.get("id")
            if not crop_id:
                print(f"⚠️ Crop found but has no ID: {crop}")
                return []
            
            print(f"🔍 Querying varieties for crop_id={crop_id}, crop_name='{crop.get('crop_name', 'unknown')}'")
            result = self.supabase.table("varieties").select("*").eq("crop_id", crop_id).execute()
            varieties_count = len(result.data) if result.data else 0
            print(f"✅ Found {varieties_count} varieties for crop '{crop.get('crop_name', 'unknown')}'")
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
