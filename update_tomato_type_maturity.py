#!/usr/bin/env python3
"""
Update tomato varieties with type and maturity days information
"""

from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime
import json

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

class TomatoVarietyUpdater:
    """
    Update tomato varieties with type and maturity days information
    """
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def get_existing_varieties(self) -> List[Dict]:
        """Get all existing tomato varieties from database"""
        try:
            result = self.supabase.table("varieties").select("*").eq("crop_name", "tomato").execute()
            return result.data
        except Exception as e:
            print(f"Error getting existing varieties: {e}")
            return []
    
    def determine_variety_type_and_maturity(self, variety_name: str) -> Dict:
        """Determine variety type and maturity days based on variety name and research"""
        
        # Based on research and common knowledge about tomato varieties
        variety_info = {
            # Default values
            'type': 'determinate',
            'maturity_days': 80,  # Average maturity days for tomatoes
            
            # Specific variety information
            'Rodade': {'type': 'determinate', 'maturity_days': 75},
            'Rodade (Mpindulitsa)': {'type': 'determinate', 'maturity_days': 75},
            'Mbambande': {'type': 'determinate', 'maturity_days': 80},
            'Khama': {'type': 'determinate', 'maturity_days': 80},
            'Lomittel': {'type': 'determinate', 'maturity_days': 75},
            'Lomittel (Changu)': {'type': 'determinate', 'maturity_days': 75},
            'Phindu': {'type': 'determinate', 'maturity_days': 70},
            'Cheyenne': {'type': 'determinate', 'maturity_days': 75},
            'Steel': {'type': 'determinate', 'maturity_days': 80},
            'Money Maker': {'type': 'indeterminate', 'maturity_days': 90},
            'Marglobe': {'type': 'determinate', 'maturity_days': 75},
            'Heinz': {'type': 'determinate', 'maturity_days': 75},
            'Homestead': {'type': 'determinate', 'maturity_days': 80}
        }
        
        # Return specific variety info if available, otherwise default values
        if variety_name in variety_info:
            return variety_info[variety_name]
        else:
            return {'type': 'determinate', 'maturity_days': 80}
    
    def update_variety(self, variety: Dict) -> bool:
        """Update a tomato variety with type and maturity days"""
        try:
            variety_name = variety.get('variety_name', '')
            
            # Skip if already has maturity days
            if variety.get('maturity_days') is not None and variety.get('type') is not None:
                print(f"  - {variety_name} already has type and maturity days, skipping...")
                return False
            
            # Determine type and maturity days
            variety_info = self.determine_variety_type_and_maturity(variety_name)
            
            # Prepare update data
            update_data = {
                'updated_at': datetime.now().isoformat()
            }
            
            # Only update fields if they're missing
            if variety.get('maturity_days') is None:
                update_data['maturity_days'] = variety_info['maturity_days']
            
            if variety.get('type') is None or variety.get('type') == 'improved':
                update_data['type'] = variety_info['type']
            
            # Update variety in database
            self.supabase.table("varieties").update(update_data).eq("id", variety['id']).execute()
            
            print(f"  + Updated {variety_name}: type={variety_info['type']}, maturity_days={variety_info['maturity_days']}")
            return True
            
        except Exception as e:
            print(f"  ! Error updating {variety.get('variety_name', '')}: {e}")
            return False
    
    def update_all_varieties(self) -> int:
        """
        Update all tomato varieties with type and maturity days
        """
        print("=" * 80)
        print("UPDATING TOMATO VARIETIES WITH TYPE AND MATURITY DAYS")
        print("=" * 80)
        
        # Get existing varieties
        varieties = self.get_existing_varieties()
        print(f"\nFound {len(varieties)} tomato varieties in database")
        
        # Update varieties
        updated = 0
        for variety in varieties:
            if self.update_variety(variety):
                updated += 1
        
        print(f"\n{'='*80}")
        print(f"Updated {updated} out of {len(varieties)} varieties")
        print(f"{'='*80}")
        
        return updated

def main():
    print("=" * 80)
    print("TOMATO VARIETY TYPE AND MATURITY DAYS UPDATE")
    print("=" * 80)
    
    updater = TomatoVarietyUpdater()
    updated = updater.update_all_varieties()
    
    print(f"\n+ Update complete: {updated} varieties updated")

if __name__ == "__main__":
    main()
