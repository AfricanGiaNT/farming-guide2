#!/usr/bin/env python3
"""
Extract soybean varieties from the Guide to Soybean Production in Malawi
and update the database
"""

from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime
import json

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

class SoybeanVarietyExtractor:
    """
    Extract soybean varieties from the Guide to Soybean Production in Malawi
    """
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def get_existing_varieties(self) -> List[Dict]:
        """Get all existing soybean varieties from database"""
        try:
            result = self.supabase.table("varieties").select("*").eq("crop_name", "soybean").execute()
            return result.data
        except Exception as e:
            print(f"Error getting existing varieties: {e}")
            return []
    
    def extract_varieties_from_table(self) -> List[Dict]:
        """Extract soybean varieties from the table in the guide"""
        # Manually extract varieties from the table shown in the image
        varieties = [
            {
                'variety_name': 'Ocepara-4',
                'source': 'DARS',
                'release_year': 1993,
                'maturity_period': 'Medium to late maturity (120-140 days)',
                'maturity_days': 130,  # Average of 120-140
                'agro_ecology': 'Medium altitude areas',
                'attributes': 'Large seeded with brown helum, produce white flowers and grey hair, exhibits indeterminate growth, resistant to root-knot nematodes and yields up to 2500kg/ha',
                'yield_potential': '2500 kg/ha',
                'disease_resistance': ['root-knot nematodes']
            },
            {
                'variety_name': 'Nasoko',
                'source': 'DARS',
                'release_year': 2002,
                'maturity_period': 'Medium to late maturity (120-140 days)',
                'maturity_days': 130,  # Average of 120-140
                'agro_ecology': 'Medium to high altitude areas',
                'attributes': 'Large seeded with cream colour, white helum, produce white flower and grey hairs, exhibit indeterminate growth and yields up to 3000kg/ha',
                'yield_potential': '3000 kg/ha',
                'disease_resistance': []
            },
            {
                'variety_name': 'Makwacha',
                'source': 'DARS',
                'release_year': 2003,
                'maturity_period': 'Medium to late maturity (120-140 days)',
                'maturity_days': 130,  # Average of 120-140
                'agro_ecology': 'Medium to high altitude areas',
                'attributes': 'Large seeded with light cream colour, white helium, produce white flowers and grey hairs, exhibits indeterminate growth and yields up to 3000kg/ha',
                'yield_potential': '3000 kg/ha',
                'disease_resistance': []
            },
            {
                'variety_name': 'Solitaire',
                'source': 'SeedCo',
                'release_year': None,
                'maturity_period': 'Medium to late maturity (120-140 days)',
                'maturity_days': 130,  # Average of 120-140
                'agro_ecology': 'Widely adapted to most agroecological zones',
                'attributes': 'Large seeded, tolerant to frogeye disease and yields up to 3000kg/ha',
                'yield_potential': '3000 kg/ha',
                'disease_resistance': ['frogeye disease (tolerant)']
            },
            {
                'variety_name': 'Soprano',
                'source': 'SeedCo',
                'release_year': None,
                'maturity_period': 'Early to medium mature (110-120 days)',
                'maturity_days': 115,  # Average of 110-120
                'agro_ecology': 'Medium to high altitude areas',
                'attributes': 'Large seeded, tolerant to frogeye disease and yields up to 3000kg/ha',
                'yield_potential': '3000 kg/ha',
                'disease_resistance': ['frogeye disease (tolerant)']
            },
            {
                'variety_name': 'Tikolore',
                'source': 'DARS/IITA',
                'release_year': None,
                'maturity_period': 'Early maturity (90-110 days)',
                'maturity_days': 100,  # Average of 90-110
                'agro_ecology': 'Low to medium altitude areas',
                'attributes': 'Small seeded, brown helum, promiscuous (may not require inoculation), tolerant to frogeye disease, susceptible to rust and yields up to 2500kg/ha',
                'yield_potential': '2500 kg/ha',
                'disease_resistance': ['frogeye disease (tolerant)']
            },
            {
                'variety_name': 'SC Serenade',
                'source': 'SeedCo',
                'release_year': None,
                'maturity_period': 'Early to medium maturing (110-120 days)',
                'maturity_days': 115,  # Average of 110-120
                'agro_ecology': 'Low to medium altitude areas',
                'attributes': 'Large seeded, exhibits indeterminate growth and yields up to 3000kg/ha',
                'yield_potential': '3000 kg/ha',
                'disease_resistance': []
            },
            {
                'variety_name': 'PAN 1867',
                'source': 'Pannar Seeds',
                'release_year': None,
                'maturity_period': 'Early Maturing (110-120 days)',
                'maturity_days': 115,  # Average of 110-120
                'agro_ecology': 'Low to medium to high altitude areas',
                'attributes': 'Large seeded, exhibit indeterminate growth, yields up to 2500kg/ha',
                'yield_potential': '2500 kg/ha',
                'disease_resistance': []
            },
            {
                'variety_name': 'SC Squire',
                'source': 'SeedCo',
                'release_year': None,
                'maturity_period': 'Medium to late maturity (120-140 days)',
                'maturity_days': 130,  # Average of 120-140
                'agro_ecology': 'Medium to high altitude areas',
                'attributes': 'Medium seeded, yellow seeded with yellow helium, tolerant to Soya Bean Rust, matures in 127 days and yields up to 3000 kg/ha',
                'yield_potential': '3000 kg/ha',
                'disease_resistance': ['Soya Bean Rust (tolerant)']
            },
            {
                'variety_name': 'SC Sequel',
                'source': 'SeedCo',
                'release_year': None,
                'maturity_period': 'Medium to late maturity (120-140 days)',
                'maturity_days': 130,  # Average of 120-140
                'agro_ecology': 'Medium to high altitude areas',
                'attributes': 'High yielding, yellow seeded with black helium, tolerant to Soya Bean Rust, matures in 123 days and yields up to 3000 kg/ha',
                'yield_potential': '3000 kg/ha',
                'disease_resistance': ['Soya Bean Rust (tolerant)']
            }
        ]
        
        return varieties
    
    def insert_soybean_variety(self, variety: Dict) -> bool:
        """Insert a soybean variety into the database"""
        try:
            # Get soybean crop ID
            result = self.supabase.table("crops").select("id").eq("crop_name", "soybean").execute()
            if not result.data:
                print("Soybean crop not found in database")
                # Create soybean crop
                crop_data = {
                    "crop_name": "soybean",
                    "scientific_name": "Glycine max",
                    "crop_type": "legume",
                    "description": "Soybean is a very important and versatile grain legume because it can be put to many uses. It provides high quality vegetable protein of around 37% CP and oil for humans and livestock consumption."
                }
                result = self.supabase.table("crops").insert(crop_data).execute()
                crop_id = result.data[0]["id"]
            else:
                crop_id = result.data[0]["id"]
            
            # Check if variety already exists
            result = self.supabase.table("varieties").select("id").eq("crop_name", "soybean").eq("variety_name", variety['variety_name']).execute()
            if result.data:
                print(f"  - {variety['variety_name']} already exists, updating...")
                # Update existing variety
                variety_id = result.data[0]["id"]
                update_data = {
                    "maturity_days": variety['maturity_days'],
                    "yield_potential": variety['yield_potential'],
                    "disease_resistance": variety['disease_resistance'],
                    "planting_months": [11, 12, 1],  # November to January
                    "min_rainfall_mm": 500,
                    "max_rainfall_mm": 800,
                    "optimal_temperature_min": 20,
                    "optimal_temperature_max": 30,
                    "soil_requirements": "Well-drained soils with pH 6.0 or higher",
                    "spacing_requirements": "45-60cm between rows, 5-10cm between plants",
                    "fertilizer_requirements": "Phosphorus is critical. Apply 200kg/ha 23:21:0+4S. No nitrogen needed due to nitrogen fixation.",
                    "pest_management": "Monitor for aphids, leaf eaters, and pod borers",
                    "disease_management": "Practice crop rotation and use disease-free seed. For Rust control, use tolerant varieties.",
                    "harvesting_guidelines": "Harvest when 95% of pods have turned brown. Moisture content should be around 15%.",
                    "storage_requirements": "Store at 12% moisture content in clean, dry conditions",
                    "source_document": "Guide to Soybean Production in Malawi",
                    "extraction_confidence": 0.95,
                    "updated_at": datetime.now().isoformat()
                }
                self.supabase.table("varieties").update(update_data).eq("id", variety_id).execute()
                return True
            else:
                # Insert new variety
                data = {
                    "crop_id": crop_id,
                    "crop_name": "soybean",
                    "variety_name": variety['variety_name'],
                    "type": "improved",
                    "maturity_days": variety['maturity_days'],
                    "yield_potential": variety['yield_potential'],
                    "drought_tolerance": "moderate",
                    "disease_resistance": variety['disease_resistance'],
                    "planting_months": [11, 12, 1],  # November to January
                    "harvest_months": [4, 5],  # April to May
                    "min_rainfall_mm": 500,
                    "max_rainfall_mm": 800,
                    "optimal_temperature_min": 20,
                    "optimal_temperature_max": 30,
                    "soil_requirements": "Well-drained soils with pH 6.0 or higher",
                    "spacing_requirements": "45-60cm between rows, 5-10cm between plants",
                    "fertilizer_requirements": "Phosphorus is critical. Apply 200kg/ha 23:21:0+4S. No nitrogen needed due to nitrogen fixation.",
                    "pest_management": "Monitor for aphids, leaf eaters, and pod borers",
                    "disease_management": "Practice crop rotation and use disease-free seed. For Rust control, use tolerant varieties.",
                    "harvesting_guidelines": "Harvest when 95% of pods have turned brown. Moisture content should be around 15%.",
                    "storage_requirements": "Store at 12% moisture content in clean, dry conditions",
                    "source_document": "Guide to Soybean Production in Malawi",
                    "extraction_confidence": 0.95,
                    "originator": variety['source'],
                    "agro_ecology": variety['agro_ecology']
                }
                
                self.supabase.table("varieties").insert(data).execute()
                print(f"  + Inserted: {variety['variety_name']}")
                return True
                
        except Exception as e:
            print(f"  ! Error inserting {variety['variety_name']}: {e}")
            return False
    
    def update_all_varieties(self) -> int:
        """
        Extract and update all soybean varieties
        """
        print("=" * 80)
        print("SOYBEAN VARIETY EXTRACTION")
        print("=" * 80)
        
        # Get existing varieties
        existing_varieties = self.get_existing_varieties()
        print(f"\nFound {len(existing_varieties)} existing soybean varieties in database")
        
        # Extract varieties from table
        varieties = self.extract_varieties_from_table()
        print(f"Extracted {len(varieties)} soybean varieties from the guide")
        
        # Insert or update varieties
        inserted = 0
        for variety in varieties:
            if self.insert_soybean_variety(variety):
                inserted += 1
        
        print(f"\n{'='*80}")
        print(f"Updated/inserted {inserted} out of {len(varieties)} varieties")
        print(f"{'='*80}")
        
        return inserted

def main():
    print("=" * 80)
    print("SOYBEAN VARIETY EXTRACTION AND UPDATE")
    print("=" * 80)
    
    extractor = SoybeanVarietyExtractor()
    updated = extractor.update_all_varieties()
    
    print(f"\n+ Extraction complete: {updated} varieties updated/inserted")

if __name__ == "__main__":
    main()
