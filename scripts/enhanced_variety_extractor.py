#!/usr/bin/env python3
"""
Enhanced Variety Extractor - Extract more varieties from tables
"""

import pdfplumber
import re
from supabase import create_client, Client
from typing import List, Dict, Tuple, Set

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

class EnhancedVarietyExtractor:
    """
    Enhanced extraction to get more varieties from tables
    """
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.pdf_path = PDF_PATH
        
        # Actual variety table locations
        self.crop_variety_pages = {
            "maize": [156, 167],
            "rice": [170],
            "groundnut": [192],
            "cassava": [220],
            "potato": [227],
            "tomato": [322],
            "soybean": [196],
            "sweet potato": [226],
        }
    
    def is_valid_variety_name(self, name: str) -> bool:
        """Strict validation for variety names"""
        if not name or not isinstance(name, str):
            return False
        
        name = name.strip()
        
        # Length checks
        if len(name) < 2 or len(name) > 50:
            return False
        
        # Reject garbage patterns
        garbage_patterns = [
            r'^\d+$',  # Just numbers
            r'^\d+\)$',  # "1)", "2)"
            r'and\s+\d+',  # "and 10"
            r'^(to|from|of|or|and|but|the|a|an)\s',  # Starting with conjunctions
            r'\d+\s*(kg|ha|t|%|mm|cm|mk|USD)',  # Measurements
            r'^\d+\s*-\s*\d+$',  # Ranges like "10-20"
            r'^[A-Z\s]+$',  # All caps (likely headers)
            r'total|average|cost|profit|margin|income',  # Financial terms
            r'table|figure|source|page',  # Document references
            r'season|month|week|year|day',  # Time references
            r'district|region|area|zone',  # Geographic terms
            r'^\d+\.\d+',  # Decimals like "5.5"
            r'^\s*-\s*$',  # Just dashes
            r'^[A-Z]{2,}\s*$',  # Just letters (likely headers)
        ]
        
        for pattern in garbage_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return False
        
        # Must contain at least one letter
        if not re.search(r'[A-Za-z]', name):
            return False
        
        # Accept patterns that look like variety names
        valid_patterns = [
            r'^[A-Z]{2,}\d+$',  # SC403, MH18, PAN33
            r'^[A-Z][a-z]+\s*\d+$',  # Peacock 10, Chitedze 2
            r'^[A-Z][a-z]+$',  # Napilira, Chalimbana
            r'^[A-Z]{2,}\s+[A-Z][a-z]+$',  # SC Serenade
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',  # Sugar 131
        ]
        
        for pattern in valid_patterns:
            if re.match(pattern, name):
                return True
        
        return False
    
    def extract_all_from_table(self, page_num: int) -> Set[str]:
        """Extract all varieties from all tables on a page"""
        varieties = set()
        
        with pdfplumber.open(self.pdf_path) as pdf:
            if page_num - 1 >= len(pdf.pages):
                return varieties
            
            page = pdf.pages[page_num - 1]
            tables = page.extract_tables()
            
            print(f"    Found {len(tables)} tables on page {page_num}")
            
            for table_idx, table in enumerate(tables):
                if not table or len(table) < 2:
                    continue
                
                print(f"    Table {table_idx + 1}: {len(table)} rows")
                
                # Look through all columns for variety names
                for row_idx, row in enumerate(table[1:]):  # Skip header
                    if not row:
                        continue
                    
                    # Check all cells in the row
                    for cell_idx, cell in enumerate(row):
                        if cell:
                            cell_str = str(cell).strip()
                            
                            # Handle multi-variety cells
                            potential_varieties = re.split(r'[,;\n]', cell_str)
                            for v in potential_varieties:
                                v = v.strip()
                                if self.is_valid_variety_name(v):
                                    varieties.add(v)
                                    print(f"      Found: {v}")
        
        return varieties
    
    def extract_crop_varieties(self, crop_name: str) -> Set[str]:
        """Extract all varieties for a crop"""
        if crop_name not in self.crop_variety_pages:
            return set()
        
        pages = self.crop_variety_pages[crop_name]
        all_varieties = set()
        
        print(f"\n[{crop_name.upper()}] Extracting from pages {pages}")
        
        for page_num in pages:
            varieties = self.extract_all_from_table(page_num)
            all_varieties.update(varieties)
        
        print(f"  Total: {len(all_varieties)} varieties")
        if all_varieties:
            print(f"  All varieties: {sorted(all_varieties)}")
        
        return all_varieties
    
    def get_crop_id(self, crop_name: str) -> int:
        """Get crop ID from database"""
        try:
            result = self.supabase.table("crops").select("id").eq("crop_name", crop_name).execute()
            if result.data:
                return result.data[0]["id"]
            return None
        except Exception as e:
            print(f"  Error getting crop ID: {e}")
            return None
    
    def insert_variety(self, crop_id: int, crop_name: str, variety_name: str) -> bool:
        """Insert variety into database"""
        try:
            data = {
                "crop_id": crop_id,
                "crop_name": crop_name,
                "variety_name": variety_name,
                "type": "improved",
                "maturity_days": None,
                "yield_potential": "medium",
                "drought_tolerance": "moderate",
                "disease_resistance": [],
                "planting_months": [],
                "harvest_months": [],
                "min_rainfall_mm": 400,
                "max_rainfall_mm": 1000,
                "optimal_temperature_min": 18,
                "optimal_temperature_max": 30,
                "soil_requirements": "Well-drained fertile soils",
                "spacing_requirements": "As recommended",
                "fertilizer_requirements": "Follow recommendations",
                "pest_management": "IPM practices",
                "disease_management": "Use certified seed",
                "harvesting_guidelines": "Harvest at maturity",
                "storage_requirements": "Proper storage",
                "source_document": "Guide to Agriculture Production Malawi 2021 - Chapter 3",
                "extraction_confidence": 0.90
            }
            
            self.supabase.table("varieties").insert(data).execute()
            return True
            
        except Exception as e:
            if "duplicate" in str(e).lower():
                return False
            print(f"    Error inserting {variety_name}: {e}")
            return False
    
    def extract_and_save(self, crop_name: str) -> int:
        """Extract varieties and save to database"""
        # Extract varieties
        varieties = self.extract_crop_varieties(crop_name)
        
        if not varieties:
            return 0
        
        # Get crop ID
        crop_id = self.get_crop_id(crop_name)
        if not crop_id:
            print(f"  Crop '{crop_name}' not found in database")
            return 0
        
        # Insert varieties
        inserted = 0
        for variety in sorted(varieties):
            if self.insert_variety(crop_id, crop_name, variety):
                print(f"    + {variety}")
                inserted += 1
        
        print(f"  Inserted: {inserted} varieties")
        return inserted

def main():
    print("=" * 80)
    print("ENHANCED VARIETY EXTRACTION - CHAPTER 3")
    print("Guide to Agriculture Production in Malawi 2021")
    print("Extracting all varieties from tables")
    print("=" * 80)
    
    extractor = EnhancedVarietyExtractor()
    
    # Test with maize first
    crops_to_extract = ["maize"]
    
    total_inserted = 0
    results = {}
    
    for crop_name in crops_to_extract:
        try:
            count = extractor.extract_and_save(crop_name)
            total_inserted += count
            results[crop_name] = count
        except Exception as e:
            print(f"\n  ERROR processing {crop_name}: {e}")
            results[crop_name] = 0
    
    # Summary
    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\nTotal varieties extracted: {total_inserted}")
    print("\nBreakdown by crop:")
    for crop, count in sorted(results.items()):
        if count > 0:
            print(f"  {crop}: {count} varieties")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()




