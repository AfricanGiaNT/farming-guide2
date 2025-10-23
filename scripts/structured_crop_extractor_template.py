#!/usr/bin/env python3
"""
Structured Crop Extractor Template
Template for creating crop-specific variety extractors
"""

import pdfplumber
import re
from supabase import create_client, Client
from typing import List, Dict, Tuple, Set
import sys

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

class StructuredCropExtractor:
    """
    Template for structured crop variety extraction
    """
    
    def __init__(self, crop_name: str, page_range: Tuple[int, int], keywords: List[str]):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.pdf_path = PDF_PATH
        self.crop_name = crop_name
        self.start_page, self.end_page = page_range
        self.keywords = keywords
    
    def clean_variety_name(self, name: str) -> str:
        """Clean variety name"""
        if not name:
            return ""
        
        # Remove extra whitespace and newlines
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Remove trailing commas and semicolons
        name = re.sub(r'[,;]+$', '', name)
        
        return name
    
    def parse_days_to_maturity(self, days_str: str) -> int:
        """Parse days to maturity from string like '110-120' or '120'"""
        if not days_str:
            return None
        
        # Extract numbers
        numbers = re.findall(r'\d+', days_str)
        if not numbers:
            return None
        
        # If range like "110-120", take the average
        if len(numbers) == 2:
            return int((int(numbers[0]) + int(numbers[1])) / 2)
        elif len(numbers) == 1:
            return int(numbers[0])
        
        return None
    
    def parse_yield(self, yield_str: str) -> str:
        """Parse yield information"""
        if not yield_str:
            return None
        
        # Clean up yield string
        yield_str = yield_str.strip()
        
        # If it's a range like "7-10t/ha", keep as is
        if 't/ha' in yield_str.lower():
            return yield_str
        
        return yield_str
    
    def extract_varieties_structured(self) -> List[Dict]:
        """Extract structured variety data"""
        
        print(f"=" * 80)
        print(f"STRUCTURED {self.crop_name.upper()} VARIETY EXTRACTION")
        print(f"Extracting from pages {self.start_page}-{self.end_page}")
        print(f"=" * 80)
        
        varieties = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(self.start_page - 1, min(self.end_page, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # Check if this page is about the crop
                is_crop_page = any(keyword in text.lower() for keyword in self.keywords)
                if not is_crop_page:
                    continue
                
                print(f"\nProcessing page {page_num + 1}")
                
                tables = page.extract_tables()
                
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    print(f"  Table {table_idx + 1}: {len(table)} rows")
                    
                    # Check if this is a variety table (has Variety column)
                    header_row = table[0]
                    if not header_row or 'variety' not in str(header_row).lower():
                        continue
                    
                    print(f"    *** VARIETY TABLE FOUND ***")
                    print(f"    Columns: {header_row}")
                    
                    # Process each variety row
                    for row_idx, row in enumerate(table[1:]):  # Skip header
                        if not row or len(row) < 3:
                            continue
                        
                        # Extract data from columns
                        variety_raw = str(row[0]).strip() if len(row) > 0 else ""
                        originator = str(row[1]).strip() if len(row) > 1 else ""
                        type_info = str(row[2]).strip() if len(row) > 2 else ""
                        grain_color = str(row[3]).strip() if len(row) > 3 else ""
                        grain_texture = str(row[4]).strip() if len(row) > 4 else ""
                        ecology = str(row[5]).strip() if len(row) > 5 else ""
                        days_to_maturity = str(row[6]).strip() if len(row) > 6 else ""
                        potential_yield = str(row[7]).strip() if len(row) > 7 else ""
                        
                        # Handle multiple varieties in one cell
                        variety_names = re.split(r'[,;]|\sand\s', variety_raw)
                        
                        for variety_name in variety_names:
                            variety_name = self.clean_variety_name(variety_name)
                            
                            if not variety_name or len(variety_name) < 2:
                                continue
                            
                            # Skip if it looks like a header or non-variety
                            if any(word in variety_name.lower() for word in ['variety', 'originator', 'type', 'grain', 'ecology', 'days', 'potential']):
                                continue
                            
                            variety_data = {
                                'variety_name': variety_name,
                                'originator': originator,
                                'type': type_info,
                                'grain_color': grain_color,
                                'grain_texture': grain_texture,
                                'ecology': ecology,
                                'days_to_maturity': self.parse_days_to_maturity(days_to_maturity),
                                'potential_yield': self.parse_yield(potential_yield),
                                'table_source': f"Page {page_num + 1}, Table {table_idx + 1}"
                            }
                            
                            varieties.append(variety_data)
                            print(f"    Extracted: {variety_name} ({originator}, {type_info})")
        
        print(f"\nTotal varieties extracted: {len(varieties)}")
        return varieties
    
    def insert_varieties(self, varieties: List[Dict]) -> int:
        """Insert varieties into database"""
        if not varieties:
            return 0
        
        # Get crop ID
        try:
            result = self.supabase.table("crops").select("id").eq("crop_name", self.crop_name).execute()
            if not result.data:
                print(f"{self.crop_name} crop not found in database")
                return 0
            crop_id = result.data[0]["id"]
        except Exception as e:
            print(f"Error getting {self.crop_name} crop ID: {e}")
            return 0
        
        inserted = 0
        print(f"\nInserting {len(varieties)} {self.crop_name} varieties:")
        
        for variety in varieties:
            try:
                data = {
                    "crop_id": crop_id,
                    "crop_name": self.crop_name,
                    "variety_name": variety['variety_name'],
                    "type": variety['type'].lower() if variety['type'] else "improved",
                    "maturity_days": variety['days_to_maturity'],
                    "yield_potential": variety['potential_yield'] or "medium",
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
                    "source_document": f"Guide to Agriculture Production Malawi 2021 - Chapter 3 - {variety['table_source']}",
                    "extraction_confidence": 0.95,
                    # Additional structured data
                    "originator": variety['originator'],
                    "grain_color": variety['grain_color'],
                    "grain_texture": variety['grain_texture'],
                    "ecology": variety['ecology']
                }
                
                self.supabase.table("varieties").insert(data).execute()
                print(f"  + {variety['variety_name']} ({variety['originator']}, {variety['type']})")
                inserted += 1
                
            except Exception as e:
                if "duplicate" in str(e).lower():
                    print(f"  - {variety['variety_name']} (already exists)")
                else:
                    print(f"  ! Error inserting {variety['variety_name']}: {e}")
        
        return inserted

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/structured_crop_extractor_template.py <crop_name> [--preview]")
        print("\nExample: python scripts/structured_crop_extractor_template.py rice --preview")
        return
    
    crop_name = sys.argv[1]
    preview_mode = "--preview" in sys.argv
    
    # Configure crop-specific parameters
    crop_configs = {
        "rice": {"pages": (168, 175), "keywords": ["rice", "oryza sativa"]},
        "groundnut": {"pages": (189, 200), "keywords": ["groundnut", "arachis hypogaea"]},
        "cassava": {"pages": (219, 230), "keywords": ["cassava", "manihot esculenta"]},
        "potato": {"pages": (226, 240), "keywords": ["potato", "solanum tuberosum"]},
        "tobacco": {"pages": (231, 270), "keywords": ["tobacco", "nicotiana"]},
    }
    
    if crop_name not in crop_configs:
        print(f"Crop '{crop_name}' not configured. Available crops:")
        for crop in crop_configs.keys():
            print(f"  - {crop}")
        return
    
    config = crop_configs[crop_name]
    extractor = StructuredCropExtractor(
        crop_name=crop_name,
        page_range=config["pages"],
        keywords=config["keywords"]
    )
    
    print(f"STRUCTURED {crop_name.upper()} VARIETY EXTRACTION")
    print(f"Mode: {'PREVIEW' if preview_mode else 'FULL EXTRACTION'}")
    
    # Extract varieties
    varieties = extractor.extract_varieties_structured()
    
    if varieties:
        if preview_mode:
            print(f"\nPREVIEW MODE - {len(varieties)} varieties found:")
            for i, variety in enumerate(varieties[:10], 1):
                print(f"  {i}. {variety['variety_name']}")
                print(f"     Originator: {variety['originator']}")
                print(f"     Type: {variety['type']}")
                print(f"     Days to Maturity: {variety['days_to_maturity']}")
                print(f"     Yield: {variety['potential_yield']}")
                print()
            if len(varieties) > 10:
                print(f"  ... and {len(varieties) - 10} more varieties")
        else:
            # Insert into database
            inserted = extractor.insert_varieties(varieties)
            
            print(f"\n{'='*80}")
            print(f"{crop_name.upper()} VARIETY EXTRACTION COMPLETE")
            print(f"Varieties extracted: {len(varieties)}")
            print(f"Varieties inserted: {inserted}")
            print(f"{'='*80}")
    else:
        print(f"No varieties found for {crop_name}")

if __name__ == "__main__":
    main()

