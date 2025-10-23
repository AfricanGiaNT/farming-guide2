#!/usr/bin/env python3
"""
Structured Sunflower Variety Extractor
Extract sunflower varieties from Guide to Agriculture Production in Malawi 2021
"""

import pdfplumber
import re
import os
from supabase import create_client, Client
from typing import List, Dict, Optional

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

class SunflowerVarietyExtractor:
    def __init__(self):
        self.pdf_path = PDF_PATH
        self.sunflower_crop_id = None
        
    def clean_variety_name(self, name: str) -> str:
        """Clean variety name"""
        if not name:
            return ""
        
        # Remove extra whitespace and clean up
        name = re.sub(r'\s+', ' ', str(name).strip())
        
        # Remove common prefixes/suffixes
        name = re.sub(r'^(variety|cultivar|name):\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\(.*?\)$', '', name)  # Remove trailing parentheses
        
        return name.strip()
    
    def parse_days_to_maturity(self, text: str) -> Optional[str]:
        """Parse days to maturity from text"""
        if not text:
            return None
        
        # Look for patterns like "90 to 100 days", "100-125 days", etc.
        patterns = [
            r'(\d+)\s*to\s*(\d+)\s*days?',
            r'(\d+)\s*-\s*(\d+)\s*days?',
            r'(\d+)\s*days?',
            r'matures?\s*in\s*(\d+)\s*to\s*(\d+)\s*days?',
            r'matures?\s*in\s*(\d+)\s*days?',
            r'maturity\s*\((\d+)\s*-\s*(\d+)\s*days?\)',
            r'maturing\s*\((\d+)\s*-\s*(\d+)\s*days?\)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)}"
                else:
                    return match.group(1)
        
        return None
    
    def parse_yield(self, text: str) -> Optional[str]:
        """Parse yield information from text"""
        if not text:
            return None
        
        # Look for yield patterns
        patterns = [
            r'(\d+)\s*kg\s*per\s*hectare',
            r'(\d+)\s*kg/ha',
            r'yield\s*potential\s*of\s*(\d+)\s*kg',
            r'(\d+)\s*-\s*(\d+)\s*kg\s*per\s*hectare',
            r'(\d+)\s*-\s*(\d+)\s*kg/ha',
            r'yields?\s*up\s*to\s*(\d+)\s*kg/ha',
            r'yield\s*of\s*(\d+)\s*kg/ha',
            r'potential\s*yield\s*of\s*(\d+)\s*kg'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)} kg/ha"
                else:
                    return f"{match.group(1)} kg/ha"
        
        return None
    
    def parse_oil_content(self, text: str) -> Optional[str]:
        """Parse oil content percentage"""
        if not text:
            return None
        
        # Look for oil content patterns
        patterns = [
            r'oil\s*content\s*of\s*(\d+)%',
            r'(\d+)%\s*oil',
            r'with\s*oil\s*content\s*of\s*(\d+)%',
            r'oil\s*content\s*(\d+)%'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{match.group(1)}%"
        
        return None
    
    def get_sunflower_crop_id(self) -> Optional[int]:
        """Get sunflower crop ID from database"""
        try:
            result = supabase.table('crops').select('id').eq('crop_name', 'sunflower').execute()
            if result.data:
                return result.data[0]['id']
            else:
                print("Sunflower crop not found in database")
                return None
        except Exception as e:
            print(f"Error getting sunflower crop ID: {str(e)}")
            return None
    
    def extract_sunflower_varieties_from_section_3_3_2_1(self) -> List[Dict]:
        """Extract varieties from section 3.3.2.1 (improved yields)"""
        varieties = []
        
        print("Extracting varieties from section 3.3.2.1 (improved yields)...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(213, 217):  # Search around pages 214-215
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.3.2.1' in text and 'improved yields' in text.lower():
                    print(f"Found section 3.3.2.1 on page {page_num + 1}")
                    
                    # Extract variety information
                    lines = text.split('\n')
                    
                    # Look for variety patterns
                    variety_patterns = [
                        r'PAN\s+7351',
                        r'PAN\s+7049', 
                        r'PAN\s+7232',
                        r'SO\s+323',
                        r'Super\s+430',
                        r'Super\s+530',
                        r'Agsun\s+51',
                        r'Agsun\s+57',
                        r'HV3037'
                    ]
                    
                    current_variety = None
                    variety_text = ""
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Check if this line contains a variety name
                        for pattern in variety_patterns:
                            match = re.search(pattern, line, re.IGNORECASE)
                            if match:
                                # Save previous variety if exists
                                if current_variety and variety_text:
                                    variety_info = self.extract_variety_details(current_variety, variety_text)
                                    if variety_info:
                                        varieties.append(variety_info)
                                
                                # Start new variety
                                current_variety = match.group(0)
                                variety_text = line
                                break
                        else:
                            # Continue building current variety description
                            if current_variety:
                                variety_text += " " + line
                    
                    # Don't forget the last variety
                    if current_variety and variety_text:
                        variety_info = self.extract_variety_details(current_variety, variety_text)
                        if variety_info:
                            varieties.append(variety_info)
        
        return varieties
    
    def extract_variety_details(self, variety_name: str, variety_text: str) -> Dict:
        """Extract details for a specific variety"""
        variety_info = {
            'variety_name': self.clean_variety_name(variety_name),
            'table_source': 'Section 3.3.2.1'
        }
        
        # Extract additional information
        variety_info['maturity_days'] = self.parse_days_to_maturity(variety_text)
        variety_info['yield_potential'] = self.parse_yield(variety_text)
        variety_info['oil_content'] = self.parse_oil_content(variety_text)
        
        # Store detailed information
        variety_info['special_notes'] = variety_text
        
        # Extract seed color
        if 'black' in variety_text.lower():
            variety_info['seed_color'] = 'Black'
        elif 'striped' in variety_text.lower():
            variety_info['seed_color'] = 'Striped'
        
        # Extract maturity type
        if 'early' in variety_text.lower() or 'nearly' in variety_text.lower():
            variety_info['type'] = 'Early maturing'
        elif 'medium' in variety_text.lower():
            variety_info['type'] = 'Medium maturing'
        
        return variety_info
    
    def extract_fertilizer_info(self) -> str:
        """Extract fertilizer information from section 3.3.2.4"""
        fertilizer_info = ""
        
        print("Extracting fertilizer information from section 3.3.2.4...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(214, 218):  # Search around page 215
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.3.2.4' in text and 'fertilizer' in text.lower():
                    print(f"Found fertilizer section on page {page_num + 1}")
                    
                    # Extract fertilizer information
                    lines = text.split('\n')
                    fertilizer_text = []
                    
                    for line in lines:
                        if 'fertilizer' in line.lower() or 'kg' in line.lower() or 'application' in line.lower():
                            fertilizer_text.append(line.strip())
                    
                    fertilizer_info = ' '.join(fertilizer_text)
        
        return fertilizer_info
    
    def insert_sunflower_varieties(self, varieties: List[Dict], fertilizer_info: str):
        """Insert sunflower varieties into database using only existing columns"""
        
        if not self.sunflower_crop_id:
            self.sunflower_crop_id = self.get_sunflower_crop_id()
            if not self.sunflower_crop_id:
                print("Cannot insert varieties without sunflower crop ID")
                return
        
        print(f"\nInserting {len(varieties)} sunflower varieties into database...")
        
        inserted_count = 0
        for variety in varieties:
            try:
                # Prepare variety data using only essential columns
                variety_data = {
                    'crop_id': self.sunflower_crop_id,
                    'crop_name': 'sunflower',
                    'variety_name': variety['variety_name'],
                    'table_source': variety.get('table_source', ''),
                    'source_document': 'Guide to Agriculture Production in Malawi 2021',
                    'extraction_confidence': 0.9
                }
                
                # Only add fields that have values to avoid empty string issues
                if variety.get('originator'):
                    variety_data['originator'] = variety['originator']
                if variety.get('type'):
                    variety_data['type'] = variety['type']
                if variety.get('yield_potential'):
                    variety_data['yield_potential'] = variety['yield_potential']
                
                # Store maturity information and additional details in text field
                harvesting_info = []
                if variety.get('maturity_days'):
                    harvesting_info.append(f"Maturity: {variety['maturity_days']}")
                if variety.get('oil_content'):
                    harvesting_info.append(f"Oil content: {variety['oil_content']}")
                if variety.get('seed_color'):
                    harvesting_info.append(f"Seed color: {variety['seed_color']}")
                if variety.get('special_notes'):
                    harvesting_info.append(variety['special_notes'])
                
                if harvesting_info:
                    variety_data['harvesting_guidelines'] = '; '.join(harvesting_info)
                
                # Add general information to existing fields
                variety_data['fertilizer_requirements'] = fertilizer_info
                
                # Insert into database
                result = supabase.table('varieties').insert(variety_data).execute()
                
                if result.data:
                    inserted_count += 1
                    print(f"OK Inserted: {variety['variety_name']}")
                else:
                    print(f"X Failed to insert: {variety['variety_name']}")
                    
            except Exception as e:
                print(f"X Error inserting {variety['variety_name']}: {str(e)}")
        
        print(f"\nSuccessfully inserted {inserted_count} out of {len(varieties)} sunflower varieties")
    
    def extract_all_sunflower_varieties(self):
        """Extract all sunflower varieties and information"""
        
        print("=" * 80)
        print("SUNFLOWER VARIETY EXTRACTION")
        print("=" * 80)
        
        # Extract varieties from different sources
        varieties_section = self.extract_sunflower_varieties_from_section_3_3_2_1()
        
        # Extract additional information
        fertilizer_info = self.extract_fertilizer_info()
        
        # Combine all varieties
        all_varieties = varieties_section
        
        # Remove duplicates based on variety name
        unique_varieties = []
        seen_names = set()
        
        for variety in all_varieties:
            variety_name = variety['variety_name'].lower()
            if variety_name not in seen_names:
                seen_names.add(variety_name)
                unique_varieties.append(variety)
        
        print(f"\nExtraction Summary:")
        print(f"- Varieties from section 3.3.2.1: {len(varieties_section)}")
        print(f"- Total unique varieties: {len(unique_varieties)}")
        
        # Insert into database
        self.insert_sunflower_varieties(unique_varieties, fertilizer_info)
        
        return unique_varieties, fertilizer_info

def main():
    extractor = SunflowerVarietyExtractor()
    varieties, fertilizer_info = extractor.extract_all_sunflower_varieties()
    
    print(f"\nSunflower extraction completed!")
    print(f"Extracted {len(varieties)} unique varieties")

if __name__ == "__main__":
    main()
