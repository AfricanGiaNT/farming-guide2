#!/usr/bin/env python3
"""
Structured Beans Variety Extractor
Extract bean variety information from Table 29a and text sections
Focus on yield information and fertilizer application data
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

class StructuredBeansExtractor:
    """
    Extract structured bean variety data from Table 29a and text sections
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
        """Parse days to maturity from string like '75-80' or '95'"""
        if not days_str:
            return None
        
        # Extract numbers
        numbers = re.findall(r'\d+', days_str)
        if not numbers:
            return None
        
        # If range like "75-80", take the average
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
        
        # If it's a number, add kg/ha
        if yield_str.isdigit():
            return f"{yield_str} kg/ha"
        
        # If it already has units, keep as is
        if 'kg' in yield_str.lower() or 'ha' in yield_str.lower():
            return yield_str
        
        return yield_str
    
    def parse_seed_weight(self, weight_str: str) -> str:
        """Parse 100 seed weight"""
        if not weight_str:
            return None
        
        # Clean up weight string
        weight_str = weight_str.strip()
        
        # If it's a number, add g
        if weight_str.isdigit():
            return f"{weight_str} g"
        
        return weight_str
    
    def extract_fertilizer_info(self, text: str) -> Dict[str, str]:
        """Extract fertilizer application information from beans section"""
        fertilizer_info = {
            "recommended_fertilizer": "",
            "fertilizer_rate": "",
            "application_method": "",
            "timing": "",
            "alternative": ""
        }
        
        # Look for specific fertilizer information patterns
        patterns = {
            "recommended_fertilizer": r'(23:10:5\+6S\+1\.0Zn)',
            "fertilizer_rate": r'(\d+kg.*?per hectare)',
            "application_method": r'(Apply.*?per.*?metres)',
            "timing": r'(initial.*?stages.*?growth)',
            "alternative": r'(manure.*?not.*?available)'
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                fertilizer_info[key] = matches[0].strip()
        
        return fertilizer_info
    
    def extract_beans_varieties_from_table29a(self) -> List[Dict]:
        """Extract bean varieties from Table 29a with comprehensive information"""
        
        print("=" * 80)
        print("STRUCTURED BEANS VARIETY EXTRACTION")
        print("Extracting from Table 29a (Phaseolus bean seed description)")
        print("=" * 80)
        
        varieties = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Focus on page 185 where Table 29a is located
            page = pdf.pages[184]  # Page 185 (0-indexed)
            text = page.extract_text() or ""
            
            print(f"\nProcessing page 185 (Table 29a)")
            
            tables = page.extract_tables()
            
            for table_idx, table in enumerate(tables):
                if not table or len(table) < 2:
                    continue
                
                print(f"\nTable {table_idx + 1}: {len(table)} rows")
                
                # Check if this is Table 29a (has Name, Growth Habit, Day To Maturity, etc.)
                header_row = table[0]
                if not header_row or len(header_row) < 6:
                    continue
                
                # Check for expected columns
                header_text = ' '.join(str(col).lower() for col in header_row if col)
                if 'name' in header_text and 'growth' in header_text and 'maturity' in header_text:
                    print(f"Found Table 29a with columns: {header_row}")
                    
                    # Process each variety row
                    for row_idx, row in enumerate(table[1:]):  # Skip header
                        if not row or len(row) < 6:
                            continue
                        
                        # Extract data from columns
                        variety_name = str(row[0]).strip() if len(row) > 0 else ""
                        growth_habit = str(row[1]).strip() if len(row) > 1 else ""
                        days_to_maturity = str(row[2]).strip() if len(row) > 2 else ""
                        potential_yield = str(row[3]).strip() if len(row) > 3 else ""
                        seed_weight = str(row[4]).strip() if len(row) > 4 else ""
                        seed_color = str(row[5]).strip() if len(row) > 5 else ""
                        
                        if not variety_name or len(variety_name) < 2:
                            continue
                        
                        variety_data = {
                            'variety_name': self.clean_variety_name(variety_name),
                            'growth_habit': growth_habit,
                            'days_to_maturity': self.parse_days_to_maturity(days_to_maturity),
                            'potential_yield': self.parse_yield(potential_yield),
                            'seed_weight': self.parse_seed_weight(seed_weight),
                            'seed_color': seed_color,
                            'originator': 'Malawi Agricultural Research',  # Default
                            'type': 'Improved',
                            'ecology': 'General',  # Default for beans
                            'table_source': 'Table 29a'
                        }
                        
                        varieties.append(variety_data)
                        print(f"  Extracted: {variety_data['variety_name']} ({growth_habit}, {days_to_maturity} days, {potential_yield})")
        
        print(f"\nTotal varieties extracted from Table 29a: {len(varieties)}")
        return varieties
    
    def extract_beans_varieties_from_text(self) -> List[Dict]:
        """Extract bean varieties from text sections like section 3.2.2.1"""
        
        print("\n" + "=" * 80)
        print("EXTRACTING BEANS VARIETIES FROM TEXT SECTIONS")
        print("=" * 80)
        
        varieties = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Process beans section pages (184-189)
            for page_num in range(183, 190):  # Pages 184-189 (0-indexed)
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # Check if this page contains beans content
                if 'beans' not in text.lower() and 'phaseolus' not in text.lower():
                    continue
                
                print(f"\nProcessing page {page_num + 1}")
                
                # Look for variety patterns in text - specific to section 3.2.2.1
                variety_patterns = [
                    r'(?:varieties?|cultivars?)\s+(?:include|are|such as|available)[\s:]+([^.]+)',
                    r'recommended\s+varieties?[\s:]+([^.]+)',
                    r'released\s+varieties?[\s:]+([^.]+)',
                    # Specific variety names mentioned in text
                    r'(PAN\s+148|PAN\s+9249|VTTT\s+924/10-4|Cim-Dwarf-01-12-2|NUA\s+35|Nasaka|Bwenzilaana|Sapelekedwa|Kamtsilo|Napilira|Maluwa|Nagaga|Mkhalira|Kambidzi|Kalima|Sapatsika|Chimbamba|BCMV-B2|BCMV-B4|BC-D/O\(19\)|Kholophethe|Kabalabala|NUA\s+45|NUA\s+59|VTT\s+924/4-4|Kanzama|Bunda\s+93|Namajengo)',
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
                                'growth_habit': 'Unknown',  # Default for text-extracted varieties
                                'days_to_maturity': 85,  # Default for beans
                                'potential_yield': '2000 kg/ha',  # Default for beans
                                'seed_weight': '45 g',  # Default
                                'seed_color': 'Red',  # Default
                                'originator': 'Malawi Agricultural Research',
                                'type': 'Improved',
                                'ecology': 'General',
                                'table_source': f'Text Section - Page {page_num + 1}'
                            }
                            
                            varieties.append(variety_data)
                            print(f"  Extracted from text: {variety_name}")
        
        print(f"\nTotal varieties extracted from text: {len(varieties)}")
        return varieties
    
    def extract_fertilizer_application_info(self) -> Dict[str, str]:
        """Extract fertilizer application information for beans"""
        
        print("\n" + "=" * 80)
        print("EXTRACTING BEANS FERTILIZER APPLICATION INFO")
        print("=" * 80)
        
        fertilizer_info = {
            "recommended_fertilizer": "",
            "fertilizer_rate": "",
            "application_method": "",
            "timing": "",
            "alternative": ""
        }
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Process beans section pages (184-189)
            for page_num in range(183, 190):  # Pages 184-189 (0-indexed)
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # Check if this page contains beans content
                if 'beans' not in text.lower() and 'phaseolus' not in text.lower():
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
    
    def insert_beans_varieties(self, varieties: List[Dict]) -> int:
        """Insert bean varieties into database"""
        if not varieties:
            return 0
        
        # Get beans crop ID
        try:
            result = self.supabase.table("crops").select("id").eq("crop_name", "beans").execute()
            if not result.data:
                print("Beans crop not found in database")
                return 0
            crop_id = result.data[0]["id"]
        except Exception as e:
            print(f"Error getting beans crop ID: {e}")
            return 0
        
        inserted = 0
        print(f"\nInserting {len(varieties)} bean varieties:")
        
        for variety in varieties:
            try:
                data = {
                    "crop_id": crop_id,
                    "crop_name": "beans",
                    "variety_name": variety['variety_name'],
                    "type": variety['type'].lower() if variety['type'] else "improved",
                    "maturity_days": variety['days_to_maturity'],
                    "yield_potential": variety['potential_yield'] or "medium",
                    "drought_tolerance": "moderate",
                    "disease_resistance": [],
                    "planting_months": [],
                    "harvest_months": [],
                    "min_rainfall_mm": 400,
                    "max_rainfall_mm": 1200,
                    "optimal_temperature_min": 15,
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
                    "grain_color": variety['seed_color'],
                    "grain_texture": variety['growth_habit'],
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
        """Run the complete beans extraction process"""
        
        print("=" * 80)
        print("BEANS VARIETY EXTRACTION PROCESS")
        print("=" * 80)
        
        # Extract varieties from Table 29a
        table29a_varieties = self.extract_beans_varieties_from_table29a()
        
        # Extract varieties from text sections
        text_varieties = self.extract_beans_varieties_from_text()
        
        # Combine all varieties
        all_varieties = table29a_varieties + text_varieties
        
        # Remove duplicates based on variety name
        unique_varieties = []
        seen_names = set()
        
        for variety in all_varieties:
            name = variety['variety_name'].lower().strip()
            if name not in seen_names:
                seen_names.add(name)
                unique_varieties.append(variety)
        
        print(f"\nTotal unique bean varieties: {len(unique_varieties)}")
        
        # Extract fertilizer information
        fertilizer_info = self.extract_fertilizer_application_info()
        
        if preview_mode:
            print("\n" + "=" * 80)
            print("PREVIEW MODE - NO DATABASE INSERTION")
            print("=" * 80)
            
            print(f"\nVarieties to be inserted: {len(unique_varieties)}")
            for variety in unique_varieties[:10]:  # Show first 10
                print(f"  - {variety['variety_name']} ({variety['growth_habit']}, {variety['potential_yield']})")
            
            if len(unique_varieties) > 10:
                print(f"  ... and {len(unique_varieties) - 10} more")
            
            print(f"\nFertilizer Information:")
            for key, value in fertilizer_info.items():
                if value:
                    print(f"  {key}: {value}")
            
            return unique_varieties, fertilizer_info
        
        # Insert into database
        inserted_count = self.insert_beans_varieties(unique_varieties)
        
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
    
    extractor = StructuredBeansExtractor()
    varieties, fertilizer_info = extractor.run_extraction(preview_mode=preview_mode)
    
    if preview_mode:
        print(f"\nTo execute the extraction, run:")
        print(f"python scripts/structured_beans_extractor.py")

if __name__ == "__main__":
    main()
