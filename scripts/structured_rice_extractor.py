#!/usr/bin/env python3
"""
Structured Rice Variety Extractor
Extract rice variety information from Table 23 and text sections
Focus on ecology information and fertilizer application data
"""

import pdfplumber
import re
import sys
from supabase import create_client, Client
from typing import List, Dict, Tuple, Set

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

class StructuredRiceExtractor:
    """
    Extract structured rice variety data from Table 23 and text sections
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
    
    def extract_fertilizer_info(self, text: str) -> Dict[str, str]:
        """Extract fertilizer application information from rice section"""
        fertilizer_info = {
            "basal_fertilizer": "",
            "top_dressing": "",
            "nitrogen_rate": "",
            "phosphorus_rate": "",
            "potassium_rate": "",
            "application_timing": "",
            "recommended_fertilizer": "",
            "urea_rate": "",
            "phosphate_rate": ""
        }
        
        # Look for specific fertilizer information patterns
        patterns = {
            "recommended_fertilizer": r'recommended.*?fertilizer.*?is\s+([^.]+)',
            "urea_rate": r'(\d+kg.*?urea.*?per hectare)',
            "phosphate_rate": r'(\d+kg.*?phosphate.*?per hectare)',
            "nitrogen_rate": r'(\d+kg.*?nitrogen.*?per hectare)',
            "basal_fertilizer": r'basal.*?fertilizer.*?([^.]+)',
            "top_dressing": r'top.*?dressing.*?([^.]+)',
            "application_timing": r'(\d+.*?days.*?after.*?transplanting)',
            "fertilizer_composition": r'(23:10:5\+6S\+1\.0 Zn)'
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                fertilizer_info[key] = matches[0].strip()
        
        return fertilizer_info
    
    def extract_rice_varieties_from_table23(self) -> List[Dict]:
        """Extract rice varieties from Table 23 with ecology information"""
        
        print("=" * 80)
        print("STRUCTURED RICE VARIETY EXTRACTION")
        print("Extracting from Table 23 (Ecology and Varieties)")
        print("=" * 80)
        
        varieties = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Focus on page 170 where Table 23 is located
            page = pdf.pages[169]  # Page 170 (0-indexed)
            text = page.extract_text() or ""
            
            print(f"\nProcessing page 170 (Table 23)")
            
            tables = page.extract_tables()
            
            for table_idx, table in enumerate(tables):
                if not table or len(table) < 2:
                    continue
                
                print(f"\nTable {table_idx + 1}: {len(table)} rows")
                
                # Check if this is Table 23 (has Ecology and Varieties columns)
                header_row = table[0]
                if not header_row or len(header_row) < 2:
                    continue
                
                # Check for ecology and varieties columns
                header_text = ' '.join(str(col).lower() for col in header_row if col)
                if 'ecology' in header_text and 'varieties' in header_text:
                    print(f"Found Table 23 with columns: {header_row}")
                    
                    # Process each ecology row
                    for row_idx, row in enumerate(table[1:]):  # Skip header
                        if not row or len(row) < 2:
                            continue
                        
                        ecology = str(row[0]).strip() if len(row) > 0 else ""
                        varieties_text = str(row[1]).strip() if len(row) > 1 else ""
                        
                        if not ecology or not varieties_text:
                            continue
                        
                        print(f"\nEcology: {ecology}")
                        print(f"Varieties: {varieties_text}")
                        
                        # Split varieties by common separators
                        variety_names = re.split(r'[,;]|\sand\s', varieties_text)
                        
                        for variety_name in variety_names:
                            variety_name = self.clean_variety_name(variety_name)
                            
                            if not variety_name or len(variety_name) < 2:
                                continue
                            
                            # Skip if it looks like a header or non-variety
                            if any(word in variety_name.lower() for word in ['variety', 'ecology', 'irrigated', 'rainfed']):
                                continue
                            
                            variety_data = {
                                'variety_name': variety_name,
                                'ecology': ecology,
                                'originator': 'Malawi Agricultural Research',  # Default for rice varieties
                                'type': 'Improved',
                                'grain_color': 'White',  # Default for rice
                                'grain_texture': 'Medium',
                                'days_to_maturity': 120,  # Default for rice
                                'potential_yield': '4-6 t/ha',  # Default for rice
                                'table_source': 'Table 23'
                            }
                            
                            varieties.append(variety_data)
                            print(f"  Extracted: {variety_name} ({ecology})")
        
        print(f"\nTotal varieties extracted from Table 23: {len(varieties)}")
        return varieties
    
    def extract_rice_varieties_from_text(self) -> List[Dict]:
        """Extract rice varieties from text sections like 'Use of improved varieties'"""
        
        print("\n" + "=" * 80)
        print("EXTRACTING RICE VARIETIES FROM TEXT SECTIONS")
        print("=" * 80)
        
        varieties = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Process rice section pages (168-175)
            for page_num in range(167, 175):  # Pages 168-175 (0-indexed)
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # Check if this page contains rice content
                if 'rice' not in text.lower():
                    continue
                
                print(f"\nProcessing page {page_num + 1}")
                
                # Look for variety patterns in text - more specific patterns
                variety_patterns = [
                    r'(?:varieties?|cultivars?)\s+(?:include|are|such as|available)[\s:]+([^.]+)',
                    r'recommended\s+varieties?[\s:]+([^.]+)',
                    r'released\s+varieties?[\s:]+([^.]+)',
                    # Specific variety names with context
                    r'(?:NERICA\s+[0-9]+|Changu|Senga|Vyawo|Mtupatupa|Nunkile|Kayanjamalo|Mpatsa|Katete|Mpeta|Nazolo|Wambone|Lifuwu|Faya[0-9-]+)',
                    # Variety descriptions
                    r'([A-Z][a-z]+)\s+\([A-Z0-9]+\)\s+is\s+a\s+recommended\s+variety'
                ]
                
                for pattern in variety_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        # Clean up the match
                        match = match.strip()
                        if len(match) < 3:
                            continue
                        
                        # Split by common separators
                        variety_names = re.split(r'[,;]|\sand\s', match)
                        
                        for variety_name in variety_names:
                            variety_name = self.clean_variety_name(variety_name)
                            
                            if not variety_name or len(variety_name) < 2:
                                continue
                            
                            # Skip if it looks like a header or non-variety
                            skip_words = ['variety', 'cultivar', 'include', 'are', 'such', 'available', 'recommended', 'released', 'hectare', 'kg', 'per', 'ton', 'yield', 'potential', 'days', 'matures', 'season', 'wet', 'dry']
                            if any(word in variety_name.lower() for word in skip_words):
                                continue
                            
                            # Skip if it contains numbers that look like measurements
                            if re.search(r'\d+.*?(kg|ton|hectare|days|season)', variety_name.lower()):
                                continue
                            
                            variety_data = {
                                'variety_name': variety_name,
                                'ecology': 'General',  # Default for text-extracted varieties
                                'originator': 'Malawi Agricultural Research',
                                'type': 'Improved',
                                'grain_color': 'White',
                                'grain_texture': 'Medium',
                                'days_to_maturity': 120,
                                'potential_yield': '4-6 t/ha',
                                'table_source': f'Text Section - Page {page_num + 1}'
                            }
                            
                            varieties.append(variety_data)
                            print(f"  Extracted from text: {variety_name}")
        
        print(f"\nTotal varieties extracted from text: {len(varieties)}")
        return varieties
    
    def extract_fertilizer_application_info(self) -> Dict[str, str]:
        """Extract fertilizer application information for rice"""
        
        print("\n" + "=" * 80)
        print("EXTRACTING RICE FERTILIZER APPLICATION INFO")
        print("=" * 80)
        
        fertilizer_info = {
            "basal_fertilizer": "",
            "top_dressing": "",
            "nitrogen_rate": "",
            "phosphorus_rate": "",
            "potassium_rate": "",
            "application_timing": "",
            "recommended_fertilizer": "",
            "urea_rate": "",
            "phosphate_rate": "",
            "fertilizer_composition": ""
        }
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Process rice section pages (168-175)
            for page_num in range(167, 175):  # Pages 168-175 (0-indexed)
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # Check if this page contains rice content
                if 'rice' not in text.lower():
                    continue
                
                print(f"\nProcessing page {page_num + 1} for fertilizer info")
                
                # Extract fertilizer information
                page_fertilizer_info = self.extract_fertilizer_info(text)
                
                # Merge with existing info
                for key, value in page_fertilizer_info.items():
                    if value and not fertilizer_info[key]:
                        fertilizer_info[key] = value
                        print(f"  Found {key}: {value}")
        
        return fertilizer_info
    
    def insert_rice_varieties(self, varieties: List[Dict]) -> int:
        """Insert rice varieties into database"""
        if not varieties:
            return 0
        
        # Get rice crop ID
        try:
            result = self.supabase.table("crops").select("id").eq("crop_name", "rice").execute()
            if not result.data:
                print("Rice crop not found in database")
                return 0
            crop_id = result.data[0]["id"]
        except Exception as e:
            print(f"Error getting rice crop ID: {e}")
            return 0
        
        inserted = 0
        print(f"\nInserting {len(varieties)} rice varieties:")
        
        for variety in varieties:
            try:
                data = {
                    "crop_id": crop_id,
                    "crop_name": "rice",
                    "variety_name": variety['variety_name'],
                    "type": variety['type'].lower() if variety['type'] else "improved",
                    "maturity_days": variety['days_to_maturity'],
                    "yield_potential": variety['potential_yield'] or "medium",
                    "drought_tolerance": "moderate",
                    "disease_resistance": [],
                    "planting_months": [],
                    "harvest_months": [],
                    "min_rainfall_mm": 600,
                    "max_rainfall_mm": 1200,
                    "optimal_temperature_min": 20,
                    "optimal_temperature_max": 35,
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
                    "ecology": variety['ecology'],
                    "table_source": variety['table_source']
                }
                
                result = self.supabase.table("varieties").insert(data).execute()
                if result.data:
                    inserted += 1
                    print(f"  SUCCESS: Inserted: {variety['variety_name']}")
                else:
                    print(f"  ERROR: Failed to insert: {variety['variety_name']}")
                    
            except Exception as e:
                print(f"  ERROR: Error inserting {variety['variety_name']}: {e}")
        
        return inserted
    
    def run_extraction(self, preview_mode: bool = False):
        """Run the complete rice extraction process"""
        
        print("=" * 80)
        print("RICE VARIETY EXTRACTION PROCESS")
        print("=" * 80)
        
        # Extract varieties from Table 23
        table23_varieties = self.extract_rice_varieties_from_table23()
        
        # Extract varieties from text sections
        text_varieties = self.extract_rice_varieties_from_text()
        
        # Combine all varieties
        all_varieties = table23_varieties + text_varieties
        
        # Remove duplicates based on variety name
        unique_varieties = []
        seen_names = set()
        
        for variety in all_varieties:
            name = variety['variety_name'].lower().strip()
            if name not in seen_names:
                seen_names.add(name)
                unique_varieties.append(variety)
        
        print(f"\nTotal unique rice varieties: {len(unique_varieties)}")
        
        # Extract fertilizer information
        fertilizer_info = self.extract_fertilizer_application_info()
        
        if preview_mode:
            print("\n" + "=" * 80)
            print("PREVIEW MODE - NO DATABASE INSERTION")
            print("=" * 80)
            
            print(f"\nVarieties to be inserted: {len(unique_varieties)}")
            for variety in unique_varieties[:10]:  # Show first 10
                print(f"  - {variety['variety_name']} ({variety['ecology']})")
            
            if len(unique_varieties) > 10:
                print(f"  ... and {len(unique_varieties) - 10} more")
            
            print(f"\nFertilizer Information:")
            for key, value in fertilizer_info.items():
                if value:
                    print(f"  {key}: {value}")
            
            return unique_varieties, fertilizer_info
        
        # Insert into database
        inserted_count = self.insert_rice_varieties(unique_varieties)
        
        print(f"\n" + "=" * 80)
        print("EXTRACTION COMPLETE")
        print("=" * 80)
        print(f"Varieties extracted: {len(unique_varieties)}")
        print(f"Varieties inserted: {inserted_count}")
        print(f"Fertilizer info extracted: {len([v for v in fertilizer_info.values() if v])} fields")
        
        return unique_varieties, fertilizer_info

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        preview_mode = True
    else:
        preview_mode = False
    
    extractor = StructuredRiceExtractor()
    varieties, fertilizer_info = extractor.run_extraction(preview_mode=preview_mode)
    
    if preview_mode:
        print(f"\nTo execute the extraction, run:")
        print(f"python scripts/structured_rice_extractor.py")

if __name__ == "__main__":
    main()
