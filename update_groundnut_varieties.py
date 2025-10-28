#!/usr/bin/env python3
"""
Update groundnut varieties with detailed information from Malawi Groundnut Production Guide
"""

import pdfplumber
import re
from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime
import json

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Malawi Groundnut Production Guide AUG2021.pdf"

class GroundnutVarietyUpdater:
    """
    Update groundnut varieties with detailed information from the Malawi Groundnut Production Guide
    """
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.pdf_path = PDF_PATH
    
    def get_existing_varieties(self) -> List[Dict]:
        """Get all existing groundnut varieties from database"""
        try:
            result = self.supabase.table("varieties").select("*").eq("crop_name", "groundnut").execute()
            return result.data
        except Exception as e:
            print(f"Error getting existing varieties: {e}")
            return []
    
    def extract_variety_info(self) -> List[Dict]:
        """Extract variety information from the Malawi Groundnut Production Guide"""
        varieties = []
        
        # Manually extracted variety information from the PDF table on page 12
        variety_data = [
            {"name": "Baka", "type": "SB", "year": 2001, "maturity_days": "90-120", 
             "agro_ecology": "Low-lying areas, lakeshore, Shire Valley", 
             "yield_potential": "1500 kg/ha", "attributes": "High yield, Rosette resistant, confectionery"},
            
            {"name": "CG 7", "type": "VB", "year": 1990, "maturity_days": "130-150", 
             "agro_ecology": "All groundnut growing areas", 
             "yield_potential": "2500 kg/ha", "attributes": "High-yield, wide adaptation, confectionery, oil, red seed colour"},
            
            {"name": "CG 8", "type": "VB", "year": 2014, "maturity_days": "120-130", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "2500 kg/ha", "attributes": "High pod yield, Rosette tolerant"},
            
            {"name": "CG 9", "type": "VB", "year": 2014, "maturity_days": "120-130", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "2500 kg/ha", "attributes": "High pod yield, Rosette tolerant"},
            
            {"name": "CG 10", "type": "VB", "year": 2014, "maturity_days": "120-130", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "2500 kg/ha", "attributes": "High pod yield, Rosette tolerant"},
            
            {"name": "CG 11", "type": "VB", "year": 2014, "maturity_days": "120-130", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "2500 kg/ha", "attributes": "High pod yield, Rosette tolerant"},
            
            {"name": "CG 12", "type": "SB", "year": 2014, "maturity_days": "90-100", 
             "agro_ecology": "Low-lying areas, lakeshore, Shire Valley", 
             "yield_potential": "1500 kg/ha", "attributes": "High pod yield, early maturity, drought tolerant"},
            
            {"name": "CG 13", "type": "SB", "year": 2014, "maturity_days": "100-110", 
             "agro_ecology": "Low-lying areas, lakeshore, Shire Valley", 
             "yield_potential": "2000 kg/ha", "attributes": "High pod yield, early maturity, drought tolerant, Rosette resistant, good grain filling"},
            
            {"name": "CG 14", "type": "SB", "year": 2014, "maturity_days": "100-110", 
             "agro_ecology": "Low-lying areas, lakeshore, Shire Valley", 
             "yield_potential": "2000 kg/ha", "attributes": "High pod yield, early maturity, drought tolerant, Rosette resistant, good grain filling"},
            
            {"name": "Chalimbana", "type": "VR", "year": 1968, "maturity_days": "140-150", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "1500 kg/ha", "attributes": "High yield, confectionery"},
            
            {"name": "Chalimbana 2005", "type": "VB", "year": 2005, "maturity_days": "130-140", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "2500 kg/ha", "attributes": "High yield, confectionery"}
        ]
        
        # Process variety information
        for variety in variety_data:
            # Parse maturity days range
            maturity_range = variety["maturity_days"].split("-")
            min_days = int(maturity_range[0])
            max_days = int(maturity_range[1])
            avg_maturity = (min_days + max_days) // 2
            
            # Parse yield potential
            yield_match = re.search(r'(\d+)\s*kg/ha', variety["yield_potential"])
            yield_kg = int(yield_match.group(1)) if yield_match else None
            
            # Extract disease resistance
            disease_resistance = []
            if "Rosette resistant" in variety["attributes"]:
                disease_resistance.append("Rosette")
            elif "Rosette tolerant" in variety["attributes"]:
                disease_resistance.append("Rosette (tolerant)")
            if "drought tolerant" in variety["attributes"]:
                disease_resistance.append("Drought")
            
            # Process variety type
            variety_type = {
                "SB": "Spanish Bunch",
                "VB": "Virginia Bunch",
                "VR": "Virginia Runner"
            }.get(variety["type"], variety["type"])
            
            # Extract planting months based on agro-ecology
            planting_months = [12, 1]  # Default December-January
            if "Low-lying areas" in variety["agro_ecology"]:
                planting_months = [11, 12]  # November-December for low-lying areas
            
            # Extract rainfall requirements based on agro-ecology
            min_rainfall = 500
            max_rainfall = 700
            if "Mid-altitude" in variety["agro_ecology"]:
                min_rainfall = 600
                max_rainfall = 800
            
            # Add processed information
            varieties.append({
                "variety_name": variety["name"],
                "type": variety_type,
                "maturity_days": avg_maturity,
                "yield_potential": f"{yield_kg} kg/ha" if yield_kg else None,
                "disease_resistance": disease_resistance,
                "planting_months": planting_months,
                "min_rainfall_mm": min_rainfall,
                "max_rainfall_mm": max_rainfall,
                "agro_ecology": variety["agro_ecology"],
                "spacing_requirements": "75cm x 15cm x 1 seed" if "VB" in variety["type"] or "VR" in variety["type"] else "75cm x 10cm x 1 seed",
                "fertilizer_requirements": "Apply phosphorus (P) at planting. No nitrogen needed due to nitrogen fixation.",
                "pest_management": "Monitor for aphids (especially for Rosette virus control), thrips, and termites.",
                "disease_management": "Practice crop rotation and use disease-free seed. For Rosette control, plant early and control aphids.",
                "harvesting_guidelines": "Harvest at optimal maturity when 70-80% of pods have dark internal hull. Timely harvest prevents aflatoxin.",
                "storage_requirements": "Dry to 8-10% moisture content. Store in clean, dry conditions to prevent aflatoxin contamination."
            })
        
        return varieties
    
    def update_variety_details(self, variety: Dict, new_info: Dict) -> bool:
        """
        Update a variety with detailed information
        """
        try:
            # Match variety name (handle case differences and spacing)
            variety_name = variety.get('variety_name', '').strip()
            new_variety_name = new_info.get('variety_name', '').strip()
            
            if variety_name.lower() == new_variety_name.lower():
                # Prepare update data
                update_data = {
                    'maturity_days': new_info.get('maturity_days'),
                    'yield_potential': new_info.get('yield_potential'),
                    'disease_resistance': new_info.get('disease_resistance'),
                    'planting_months': new_info.get('planting_months'),
                    'min_rainfall_mm': new_info.get('min_rainfall_mm'),
                    'max_rainfall_mm': new_info.get('max_rainfall_mm'),
                    'spacing_requirements': new_info.get('spacing_requirements'),
                    'fertilizer_requirements': new_info.get('fertilizer_requirements'),
                    'pest_management': new_info.get('pest_management'),
                    'disease_management': new_info.get('disease_management'),
                    'harvesting_guidelines': new_info.get('harvesting_guidelines'),
                    'storage_requirements': new_info.get('storage_requirements'),
                    'updated_at': datetime.now().isoformat(),
                    'source_document': "Malawi Groundnut Production Guide AUG2021 - Table 3.1"
                }
                
                # Update variety in database
                self.supabase.table("varieties").update(update_data).eq("id", variety['id']).execute()
                
                print(f"  + Updated: {variety_name} with detailed information")
                return True
            
            return False
            
        except Exception as e:
            print(f"  - Error updating {variety_name}: {e}")
            return False
    
    def update_all_varieties(self) -> int:
        """
        Update all groundnut varieties with detailed information
        """
        print("=" * 80)
        print("GROUNDNUT DETAILED INFORMATION EXTRACTION")
        print("=" * 80)
        
        # Get existing varieties
        existing_varieties = self.get_existing_varieties()
        print(f"\nFound {len(existing_varieties)} groundnut varieties in database")
        
        # Extract detailed variety information
        new_variety_info = self.extract_variety_info()
        print(f"Extracted {len(new_variety_info)} varieties from Malawi Groundnut Production Guide")
        
        # Create a lookup dictionary for new variety info
        variety_info_lookup = {v['variety_name'].lower(): v for v in new_variety_info}
        
        updated = 0
        for variety in existing_varieties:
            variety_name = variety.get('variety_name', '').strip()
            
            # Check for exact match
            if variety_name.lower() in variety_info_lookup:
                if self.update_variety_details(variety, variety_info_lookup[variety_name.lower()]):
                    updated += 1
            # Check for partial match
            else:
                matched = False
                for new_name, new_info in variety_info_lookup.items():
                    if new_name in variety_name.lower() or variety_name.lower() in new_name:
                        if self.update_variety_details(variety, new_info):
                            updated += 1
                            matched = True
                            break
                
                if not matched:
                    print(f"  ? No match found for: {variety_name}")
        
        print(f"\n{'='*80}")
        print(f"Updated {updated} out of {len(existing_varieties)} varieties")
        print(f"{'='*80}")
        
        return updated

def main():
    print("=" * 80)
    print("GROUNDNUT DETAILED INFORMATION EXTRACTION")
    print("Extracting detailed production information from Malawi Groundnut Production Guide")
    print("=" * 80)
    
    updater = GroundnutVarietyUpdater()
    updated = updater.update_all_varieties()
    
    print(f"\n+ Extraction complete: {updated} varieties updated")

if __name__ == "__main__":
    main()
