#!/usr/bin/env python3
"""
Structured Maize Variety Extractor
Extract complete variety information: variety, originator, type, days to maturity, potential yield
Focus on Tables 17a and 17b only
"""

import pdfplumber
import re
from supabase import create_client, Client
from typing import List, Dict, Tuple, Set

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

class StructuredMaizeExtractor:
    """
    Extract structured maize variety data from Tables 17a and 17b
    """
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.pdf_path = PDF_PATH
    
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
    
    def extract_maize_varieties_structured(self) -> List[Dict]:
        """Extract structured maize variety data from Tables 17a and 17b"""
        
        print("=" * 80)
        print("STRUCTURED MAIZE VARIETY EXTRACTION")
        print("Extracting from Tables 17a and 17b")
        print("=" * 80)
        
        varieties = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Focus on page 156 where Tables 17a and 17b are located
            page = pdf.pages[155]  # Page 156 (0-indexed)
            text = page.extract_text() or ""
            
            print(f"\nProcessing page 156 (Tables 17a and 17b)")
            
            tables = page.extract_tables()
            
            for table_idx, table in enumerate(tables):
                if not table or len(table) < 2:
                    continue
                
                print(f"\nTable {table_idx + 1}: {len(table)} rows")
                
                # Check if this is a variety table (has Variety column)
                header_row = table[0]
                if not header_row or 'variety' not in str(header_row).lower():
                    continue
                
                print(f"Found variety table with columns: {header_row}")
                
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
                    
                    # Handle multiple varieties in one cell (like "MH 26, MH 27, MH 28...")
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
                            'table_source': f"Table 17{'a' if table_idx == 0 else 'b'}"
                        }
                        
                        varieties.append(variety_data)
                        print(f"  Extracted: {variety_name} ({originator}, {type_info})")
        
        print(f"\nTotal varieties extracted: {len(varieties)}")
        return varieties
    
    def insert_maize_varieties(self, varieties: List[Dict]) -> int:
        """Insert maize varieties into database"""
        if not varieties:
            return 0
        
        # Get maize crop ID
        try:
            result = self.supabase.table("crops").select("id").eq("crop_name", "maize").execute()
            if not result.data:
                print("Maize crop not found in database")
                return 0
            crop_id = result.data[0]["id"]
        except Exception as e:
            print(f"Error getting maize crop ID: {e}")
            return 0
        
        inserted = 0
        print(f"\nInserting {len(varieties)} maize varieties:")
        
        for variety in varieties:
            try:
                data = {
                    "crop_id": crop_id,
                    "crop_name": "maize",
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
    print("=" * 80)
    print("STRUCTURED MAIZE VARIETY EXTRACTION")
    print("Extracting complete variety information from Tables 17a and 17b")
    print("=" * 80)
    
    extractor = StructuredMaizeExtractor()
    
    # Extract structured variety data
    varieties = extractor.extract_maize_varieties_structured()
    
    if varieties:
        # Insert into database
        inserted = extractor.insert_maize_varieties(varieties)
        
        print(f"\n{'='*80}")
        print(f"MAIZE VARIETY EXTRACTION COMPLETE")
        print(f"Varieties extracted: {len(varieties)}")
        print(f"Varieties inserted: {inserted}")
        print(f"{'='*80}")
        
        # Show sample of extracted data
        print(f"\nSample extracted varieties:")
        for i, variety in enumerate(varieties[:5]):
            print(f"  {i+1}. {variety['variety_name']}")
            print(f"     Originator: {variety['originator']}")
            print(f"     Type: {variety['type']}")
            print(f"     Days to Maturity: {variety['days_to_maturity']}")
            print(f"     Potential Yield: {variety['potential_yield']}")
            print()
    else:
        print("No varieties extracted")

if __name__ == "__main__":
    main()


