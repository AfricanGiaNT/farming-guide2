#!/usr/bin/env python3
"""
One-Crop-At-A-Time Variety Extractor
Extract varieties for ONE crop at a time with maximum accuracy
Focus on quality over quantity
"""

import pdfplumber
import re
from supabase import create_client, Client
from typing import List, Dict, Tuple, Set

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

class OneCropVarietyExtractor:
    """
    Extract varieties for ONE crop at a time with maximum accuracy
    """
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.pdf_path = PDF_PATH
        
        # Get all crops from database
        self.crops = self.get_all_crops()
        
        # Precise crop sections in Chapter 3
        self.crop_sections = {
            "maize": {"pages": (153, 175), "keywords": ["maize", "zea mays"]},
            "rice": {"pages": (168, 175), "keywords": ["rice", "oryza sativa"]},
            "sorghum": {"pages": (175, 180), "keywords": ["sorghum", "sorghum bicolor"]},
            "wheat": {"pages": (181, 185), "keywords": ["wheat", "triticum"]},
            "pearl millet": {"pages": (178, 182), "keywords": ["pearl millet", "pennisetum"]},
            "finger millet": {"pages": (180, 185), "keywords": ["finger millet", "eleusine"]},
            "beans": {"pages": (184, 195), "keywords": ["beans", "phaseolus vulgaris"]},
            "cowpea": {"pages": (204, 215), "keywords": ["cowpea", "vigna unguiculata"]},
            "groundnut": {"pages": (189, 200), "keywords": ["groundnut", "arachis hypogaea"]},
            "soybean": {"pages": (195, 210), "keywords": ["soybean", "soyabean", "glycine max"]},
            "pigeonpea": {"pages": (199, 210), "keywords": ["pigeonpea", "pigeon pea", "cajanus cajan"]},
            "bambara": {"pages": (206, 215), "keywords": ["bambara", "vigna subterranea"]},
            "chickpea": {"pages": (208, 215), "keywords": ["chickpea", "cicer arietinum"]},
            "field pea": {"pages": (210, 220), "keywords": ["field pea", "pisum sativum"]},
            "sunflower": {"pages": (214, 225), "keywords": ["sunflower", "helianthus annuus"]},
            "sesame": {"pages": (216, 225), "keywords": ["sesame", "sesamum indicum"]},
            "cassava": {"pages": (219, 230), "keywords": ["cassava", "manihot esculenta"]},
            "sweet potato": {"pages": (224, 235), "keywords": ["sweet potato", "sweetpotato", "ipomoea batatas"]},
            "potato": {"pages": (226, 240), "keywords": ["potato", "solanum tuberosum"]},
            "tobacco": {"pages": (231, 270), "keywords": ["tobacco", "nicotiana", "burley", "flue cured"]},
            "cotton": {"pages": (265, 280), "keywords": ["cotton", "gossypium"]},
            "tomato": {"pages": (322, 330), "keywords": ["tomato", "lycopersicon esculentum"]},
            "cabbage": {"pages": (321, 330), "keywords": ["cabbage", "brassica oleracea"]},
            "onion": {"pages": (324, 335), "keywords": ["onion", "allium cepa"]},
            "garlic": {"pages": (325, 335), "keywords": ["garlic", "allium sativum"]},
            "citrus": {"pages": (277, 290), "keywords": ["citrus", "orange", "lemon"]},
            "banana": {"pages": (281, 295), "keywords": ["banana", "musa"]},
            "mango": {"pages": (285, 295), "keywords": ["mango", "mangifera indica"]},
            "avocado": {"pages": (287, 295), "keywords": ["avocado", "persea americana"]},
            "pawpaw": {"pages": (288, 295), "keywords": ["pawpaw", "papaya", "carica papaya"]},
        }
    
    def get_all_crops(self) -> List[Dict]:
        """Get all crops from database"""
        try:
            result = self.supabase.table("crops").select("id, crop_name").execute()
            return result.data
        except Exception as e:
            print(f"Error getting crops: {e}")
            return []
    
    def is_valid_variety_name(self, name: str) -> bool:
        """Strict validation for variety names"""
        if not name or not isinstance(name, str):
            return False
        
        name = name.strip()
        
        # Remove common noise
        name = re.sub(r'\n+', ' ', name)
        name = name.strip()
        
        # Length checks
        if len(name) < 2 or len(name) > 50:
            return False
        
        # Reject garbage patterns
        garbage_patterns = [
            r'^\d+$',
            r'^\d+\)$',
            r'and\s+\d+',
            r'^(to|from|of|or|and|but|the|a|an)\s',
            r'\d+\s*(kg|ha|t|%|mm|cm|mk|USD|days|months)',
            r'^\d+\s*-\s*\d+$',
            r'^[A-Z\s]+$',
            r'total|average|cost|profit|margin|income|yield|maturity',
            r'table|figure|source|page',
            r'season|month|week|year|day',
            r'district|region|area|zone',
            r'^\d+\.\d+',
            r'^\s*-\s*$',
            r'^[A-Z]{2,}\s*$',
        ]
        
        for pattern in garbage_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return False
        
        # Must contain at least one letter
        if not re.search(r'[A-Za-z]', name):
            return False
        
        # Accept patterns that look like variety names
        valid_patterns = [
            r'^[A-Z]{2,}\d+$',
            r'^[A-Z][a-z]+\s*\d+$',
            r'^[A-Z][a-z]+$',
            r'^[A-Z]{2,}\s+[A-Z][a-z]+$',
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',
            r'^[A-Z][a-z]+\s+\d+[A-Z]?$',
            r'^[A-Z][a-z]+\s+\d+-\d+[A-Z]?$',
        ]
        
        for pattern in valid_patterns:
            if re.match(pattern, name):
                return True
        
        return False
    
    def extract_varieties_for_crop(self, crop_name: str) -> Set[str]:
        """Extract ALL varieties for ONE specific crop"""
        if crop_name not in self.crop_sections:
            print(f"Crop '{crop_name}' not found in Chapter 3 sections")
            return set()
        
        section = self.crop_sections[crop_name]
        start_page, end_page = section["pages"]
        keywords = section["keywords"]
        
        varieties = set()
        
        print(f"\n{'='*60}")
        print(f"EXTRACTING VARIETIES FOR: {crop_name.upper()}")
        print(f"Pages: {start_page}-{end_page}")
        print(f"Keywords: {', '.join(keywords)}")
        print(f"{'='*60}")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # Check if this page is about the crop
                is_crop_page = any(keyword in text.lower() for keyword in keywords)
                if not is_crop_page:
                    continue
                
                print(f"\nPage {page_num + 1}: Found {crop_name} content")
                
                # Extract from tables
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    print(f"  Table {table_idx + 1}: {len(table)} rows")
                    for row_idx, row in enumerate(table[1:]):  # Skip header
                        if not row:
                            continue
                        
                        for cell_idx, cell in enumerate(row):
                            if cell:
                                cell_str = str(cell).strip()
                                potential_varieties = re.split(r'[,;\n]', cell_str)
                                for v in potential_varieties:
                                    v = v.strip()
                                    if self.is_valid_variety_name(v):
                                        varieties.add(v)
                                        print(f"    Found variety: {v}")
                
                # Extract from text sections
                variety_patterns = [
                    r'(?:varieties?|cultivars?)\s+(?:include|are|such as|available)[\s:]+([^.]+)',
                    r'recommended\s+varieties?[\s:]+([^.]+)',
                    r'released\s+varieties?[\s:]+([^.]+)',
                    r'improved\s+varieties?[\s:]+([^.]+)',
                    r'available\s+varieties?[\s:]+([^.]+)',
                ]
                
                for pattern in variety_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        potential_varieties = re.split(r'[,;]|\s+and\s+|\s+or\s+', match)
                        for v in potential_varieties:
                            v = v.strip()
                            if self.is_valid_variety_name(v):
                                varieties.add(v)
                                print(f"    Found variety: {v}")
        
        print(f"\nTotal varieties found for {crop_name}: {len(varieties)}")
        if varieties:
            print(f"Varieties: {sorted(varieties)}")
        
        return varieties
    
    def insert_varieties_for_crop(self, crop_id: int, crop_name: str, varieties: Set[str]) -> int:
        """Insert all varieties for one crop"""
        if not varieties:
            return 0
        
        inserted = 0
        print(f"\nInserting varieties for {crop_name}:")
        
        for variety in sorted(varieties):
            try:
                data = {
                    "crop_id": crop_id,
                    "crop_name": crop_name,
                    "variety_name": variety,
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
                print(f"  + {variety}")
                inserted += 1
                
            except Exception as e:
                if "duplicate" in str(e).lower():
                    print(f"  - {variety} (already exists)")
                else:
                    print(f"  ! Error inserting {variety}: {e}")
        
        print(f"\nInserted {inserted} varieties for {crop_name}")
        return inserted
    
    def process_one_crop(self, crop_name: str) -> int:
        """Process ONE crop completely"""
        print(f"\n{'='*80}")
        print(f"PROCESSING CROP: {crop_name.upper()}")
        print(f"{'='*80}")
        
        # Get crop ID
        crop_data = next((c for c in self.crops if c["crop_name"] == crop_name), None)
        if not crop_data:
            print(f"Crop '{crop_name}' not found in database")
            return 0
        
        crop_id = crop_data["id"]
        
        # Extract varieties
        varieties = self.extract_varieties_for_crop(crop_name)
        
        # Insert varieties
        inserted = self.insert_varieties_for_crop(crop_id, crop_name, varieties)
        
        return inserted

def main():
    print("=" * 80)
    print("ONE-CROP-AT-A-TIME VARIETY EXTRACTION")
    print("Guide to Agriculture Production in Malawi 2021 - Chapter 3")
    print("Quality-focused extraction, one crop at a time")
    print("=" * 80)
    
    extractor = OneCropVarietyExtractor()
    
    # Start with maize as an example
    crop_name = "maize"
    
    print(f"\nStarting with crop: {crop_name}")
    print("This will extract ALL varieties for this crop before moving to the next.")
    
    inserted = extractor.process_one_crop(crop_name)
    
    print(f"\n{'='*80}")
    print(f"COMPLETED: {crop_name.upper()}")
    print(f"Varieties inserted: {inserted}")
    print(f"{'='*80}")
    
    print(f"\nTo process the next crop, run:")
    print(f"python scripts/one_crop_extractor.py --crop <crop_name>")
    print(f"\nAvailable crops: {', '.join(extractor.crop_sections.keys())}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2 and sys.argv[1] == "--crop":
        crop_name = sys.argv[2]
        extractor = OneCropVarietyExtractor()
        inserted = extractor.process_one_crop(crop_name)
        print(f"\nCompleted {crop_name}: {inserted} varieties inserted")
    else:
        main()


