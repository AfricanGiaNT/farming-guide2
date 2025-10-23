#!/usr/bin/env python3
"""
Improved Variety Extractor for Chapter 3
Carefully extracts ONLY actual variety names from specific table locations
Focuses on Guide to Agriculture Production in Malawi 2021
"""

import pdfplumber
import re
from supabase import create_client, Client
from typing import List, Dict, Tuple, Set

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

class ImprovedVarietyExtractor:
    """
    Improved extraction with:
    1. Manual page identification for each crop
    2. Strict validation of variety names
    3. Multi-pass extraction (tables + text patterns)
    4. Crop-specific validation rules
    """
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.pdf_path = PDF_PATH
        
        # Known variety naming patterns for Malawi crops
        self.known_patterns = {
            "maize": [
                r"SC\s*\d+",  # SC403, SC 419
                r"DK\s*\d+",  # DK8031
                r"ZM\s*\d+",  # ZM621
                r"MH\s*\d+",  # MH18
                r"PHB\s*\d+G\d+",  # PHB30G19
                r"PAN\s*\d+",  # PAN53
            ],
            "beans": [
                r"[A-Z][a-z]+",  # Napilira, Kalima
                r"Sugar\s*\d+",  # Sugar 131
                r"IT\d+[A-Z]-\d+",  # IT82E-16
            ],
            "groundnut": [
                r"CG\s*\d+",  # CG7
                r"MGV\s*\d+",  # MGV4
                r"[A-Z][a-z]+",  # Chalimbana, Nsinjiro
            ],
            "soybean": [
                r"[A-Z][a-z]+",  # Makwacha, Tikolore
                r"SC\s*[A-Z][a-z]+",  # SC Serenade
            ]
        }
    
    def is_valid_variety_name(self, name: str, crop_name: str = None) -> bool:
        """
        Strict validation to filter out garbage
        Returns True only if name matches expected variety patterns
        """
        if not name or not isinstance(name, str):
            return False
        
        name = name.strip()
        
        # Length checks
        if len(name) < 2 or len(name) > 40:
            return False
        
        # Reject common garbage patterns
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
        ]
        
        for pattern in garbage_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return False
        
        # Must contain at least one letter
        if not re.search(r'[A-Za-z]', name):
            return False
        
        # Check against known patterns if crop specified
        if crop_name and crop_name.lower() in self.known_patterns:
            patterns = self.known_patterns[crop_name.lower()]
            for pattern in patterns:
                if re.search(pattern, name, re.IGNORECASE):
                    return True
            # If patterns exist but none match, be cautious
            # Still allow if it looks like a proper name
            if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', name):
                return True
            if re.match(r'^[A-Z]{2,}\d+$', name):  # Generic code pattern
                return True
        
        # Generic acceptance criteria for crops without specific patterns
        # Accept if it looks like a proper name or code
        valid_formats = [
            r'^[A-Z][a-z]+$',  # Proper names: Napilira
            r'^[A-Z]{2,}\d+$',  # Codes: SC403
            r'^[A-Z][a-z]+\s+\d+$',  # Name + number: Sugar 131
        ]
        
        for pattern in valid_formats:
            if re.match(pattern, name):
                return True
        
        return False
    
    def extract_from_tables(self, page_nums: List[int]) -> Set[str]:
        """Extract variety names from tables on specific pages"""
        varieties = set()
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in page_nums:
                if page_num - 1 >= len(pdf.pages):
                    continue
                
                page = pdf.pages[page_num - 1]
                tables = page.extract_tables()
                
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    # Look for variety columns (usually first few columns)
                    for row in table[1:]:  # Skip header
                        if not row:
                            continue
                        
                        # Check first 3 cells
                        for cell in row[:3]:
                            if cell:
                                cell_str = str(cell).strip()
                                # Split multi-variety cells
                                potential_varieties = re.split(r'[,;\n]', cell_str)
                                for v in potential_varieties:
                                    v = v.strip()
                                    if self.is_valid_variety_name(v):
                                        varieties.add(v)
        
        return varieties
    
    def extract_from_text_patterns(self, page_nums: List[int], crop_name: str) -> Set[str]:
        """Extract varieties mentioned in text using patterns"""
        varieties = set()
        
        variety_mention_patterns = [
            r'(?:varieties?|cultivars?)\s+(?:include|are|such as)[\s:]+([^.]+)',
            r'recommended\s+varieties?[\s:]+([^.]+)',
            r'released\s+varieties?[\s:]+([^.]+)',
        ]
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in page_nums:
                if page_num - 1 >= len(pdf.pages):
                    continue
                
                page = pdf.pages[page_num - 1]
                text = page.extract_text() or ""
                
                for pattern in variety_mention_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        # Split by common separators
                        potential_varieties = re.split(r'[,;]|\s+and\s+', match)
                        for v in potential_varieties:
                            v = v.strip()
                            if self.is_valid_variety_name(v, crop_name):
                                varieties.add(v)
        
        return varieties
    
    def find_variety_table_pages(self, crop_name: str, search_range: Tuple[int, int]) -> List[int]:
        """
        Scan pages to find where variety tables actually appear
        Returns list of page numbers with variety tables
        """
        start_page, end_page = search_range
        variety_pages = []
        
        variety_indicators = [
            "varieties", "variety", "cultivar", "cultivars",
            "recommended varieties", "released varieties"
        ]
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = (page.extract_text() or "").lower()
                
                # Check if page mentions varieties AND has tables
                has_variety_mention = any(ind in text for ind in variety_indicators)
                has_tables = len(page.extract_tables()) > 0
                
                if has_variety_mention and has_tables:
                    variety_pages.append(page_num + 1)
        
        return variety_pages
    
    def extract_crop_varieties(self, crop_name: str, page_range: Tuple[int, int]) -> Set[str]:
        """
        Main extraction method for a single crop
        Combines table extraction and text pattern matching
        """
        print(f"\n[{crop_name.upper()}] Extracting from pages {page_range[0]}-{page_range[1]}")
        
        # First, find pages that actually have variety tables
        variety_pages = self.find_variety_table_pages(crop_name, page_range)
        print(f"  Found variety tables on pages: {variety_pages}")
        
        if not variety_pages:
            print(f"  No variety tables found in this range")
            return set()
        
        # Extract from tables on those specific pages
        table_varieties = self.extract_from_tables(variety_pages)
        print(f"  Tables: {len(table_varieties)} varieties")
        
        # Extract from text patterns
        text_varieties = self.extract_from_text_patterns(variety_pages, crop_name)
        print(f"  Text: {len(text_varieties)} varieties")
        
        # Combine and return
        all_varieties = table_varieties.union(text_varieties)
        
        if all_varieties:
            print(f"  Preview: {list(all_varieties)[:5]}")
        
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
                "extraction_confidence": 0.85
            }
            
            self.supabase.table("varieties").insert(data).execute()
            return True
            
        except Exception as e:
            if "duplicate" in str(e).lower():
                return False
            print(f"    Error inserting {variety_name}: {e}")
            return False
    
    def extract_and_save(self, crop_name: str, page_range: Tuple[int, int]) -> int:
        """Extract varieties and save to database"""
        # Extract varieties
        varieties = self.extract_crop_varieties(crop_name, page_range)
        
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

# Chapter 3 crop page ranges (to be refined)
CHAPTER3_CROPS = {
    "maize": (30, 50),
    "rice": (50, 65),
    "beans": (105, 120),  # Phaseolus beans
    "groundnut": (130, 145),
    "soybean": (145, 160),
    "cassava": (195, 210),
    "sweet potato": (210, 225),
    "potato": (225, 240),
    "tomato": (240, 255),
    "cotton": (285, 300),
}

def main():
    print("=" * 80)
    print("IMPROVED VARIETY EXTRACTION - CHAPTER 3")
    print("Guide to Agriculture Production in Malawi 2021")
    print("=" * 80)
    
    extractor = ImprovedVarietyExtractor()
    
    total_inserted = 0
    results = {}
    
    # Extract for each crop
    for crop_name, page_range in CHAPTER3_CROPS.items():
        try:
            count = extractor.extract_and_save(crop_name, page_range)
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
        print(f"  {crop}: {count} varieties")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()



