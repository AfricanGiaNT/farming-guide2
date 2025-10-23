#!/usr/bin/env python3
"""
Structured Ginger Variety Extractor
Extract ginger varieties from Guide to Agriculture Production in Malawi 2021
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

class GingerVarietyExtractor:
    def __init__(self):
        self.pdf_path = PDF_PATH
        self.ginger_crop_id = None
        
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
    
    def parse_yield(self, text: str) -> Optional[str]:
        """Parse yield information from text"""
        if not text:
            return None
        
        # Look for yield patterns
        patterns = [
            r'(\d+)\s*kg\s*per\s*hectare',
            r'(\d+)\s*kg/ha',
            r'(\d+)\s*-\s*(\d+)\s*kg\s*per\s*hectare',
            r'(\d+)\s*-\s*(\d+)\s*kg/ha',
            r'yield.*?(\d+)\s*to\s*(\d+)\s*kg',
            r'yield.*?(\d+)\s*-\s*(\d+)\s*kg',
            r'up to\s*(\d+)\s*kg',
            r'(\d+)\s*to\s*(\d+)\s*kg'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)} kg/ha"
                else:
                    return f"{match.group(1)} kg/ha"
        
        return None
    
    def get_ginger_crop_id(self) -> Optional[int]:
        """Get ginger crop ID from database"""
        try:
            result = supabase.table('crops').select('id').eq('crop_name', 'ginger').execute()
            if result.data:
                return result.data[0]['id']
            else:
                print("Ginger crop not found in database")
                return None
        except Exception as e:
            print(f"Error getting ginger crop ID: {str(e)}")
            return None
    
    def extract_ginger_varieties_from_section_3_9_3_2_1(self) -> List[Dict]:
        """Extract varieties from section 3.9.3.2.1 (use of selected cultivars)"""
        varieties = []
        
        print("Extracting varieties from section 3.9.3.2.1 (use of selected cultivars)...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(305, 308):  # Search around pages 306-307
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.9.3.2.1' in text and 'cultivars' in text.lower():
                    print(f"Found section 3.9.3.2.1 on page {page_num + 1}")
                    
                    # Extract variety information from text
                    lines = text.split('\n')
                    
                    # Look for variety information - note that it says "no recommended varieties"
                    # but mentions "local cultivars"
                    variety_info = {
                        'variety_name': 'Local Cultivars',
                        'table_source': 'Section 3.9.3.2.1',
                        'special_notes': 'Currently there are no recommended ginger varieties. Farmers are encouraged to grow local cultivars.'
                    }
                    
                    varieties.append(variety_info)
        
        return varieties
    
    def extract_management_info(self) -> Dict[str, str]:
        """Extract management information from various sections"""
        management_info = {
            'field_preparation': '',
            'planting': '',
            'fertilizer_application': '',
            'mulching': '',
            'pest_control': '',
            'disease_control': '',
            'harvesting': '',
            'potential_yield': ''
        }
        
        print("Extracting management information...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(305, 308):  # Search around pages 306-307
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # Extract field preparation information
                if '3.9.3.2.2' in text and 'field preparation' in text.lower():
                    print(f"Found field preparation section on page {page_num + 1}")
                    lines = text.split('\n')
                    field_lines = []
                    for line in lines:
                        if 'field' in line.lower() or 'bed' in line.lower() or 'manure' in line.lower() or 'tilth' in line.lower():
                            field_lines.append(line.strip())
                    management_info['field_preparation'] = ' '.join(field_lines)
                
                # Extract planting information
                if '3.9.3.2.3' in text and 'planting' in text.lower():
                    print(f"Found planting section on page {page_num + 1}")
                    lines = text.split('\n')
                    planting_lines = []
                    for line in lines:
                        if 'plant' in line.lower() or 'seed' in line.lower() or 'row' in line.lower() or 'cm' in line.lower():
                            planting_lines.append(line.strip())
                    management_info['planting'] = ' '.join(planting_lines)
                
                # Extract fertilizer application information
                if '3.9.3.2.4' in text and 'fertilizer' in text.lower():
                    print(f"Found fertilizer section on page {page_num + 1}")
                    lines = text.split('\n')
                    fertilizer_lines = []
                    for line in lines:
                        if 'fertilizer' in line.lower() or 'phosphate' in line.lower() or 'can' in line.lower() or 'urea' in line.lower():
                            fertilizer_lines.append(line.strip())
                    management_info['fertilizer_application'] = ' '.join(fertilizer_lines)
                
                # Extract mulching information
                if '3.9.3.2.5' in text and 'mulching' in text.lower():
                    print(f"Found mulching section on page {page_num + 1}")
                    lines = text.split('\n')
                    mulching_lines = []
                    for line in lines:
                        if 'mulch' in line.lower() or 'grass' in line.lower():
                            mulching_lines.append(line.strip())
                    management_info['mulching'] = ' '.join(mulching_lines)
                
                # Extract pest control information
                if '3.9.3.3' in text and 'pest' in text.lower():
                    print(f"Found pest control section on page {page_num + 1}")
                    lines = text.split('\n')
                    pest_lines = []
                    for line in lines:
                        if 'pest' in line.lower() or 'weed' in line.lower() or 'nematode' in line.lower():
                            pest_lines.append(line.strip())
                    management_info['pest_control'] = ' '.join(pest_lines)
                
                # Extract disease control information
                if '3.9.3.3.3' in text and 'disease' in text.lower():
                    print(f"Found disease control section on page {page_num + 1}")
                    lines = text.split('\n')
                    disease_lines = []
                    for line in lines:
                        if 'disease' in line.lower() or 'rot' in line.lower() or 'wilt' in line.lower():
                            disease_lines.append(line.strip())
                    management_info['disease_control'] = ' '.join(disease_lines)
                
                # Extract harvesting information
                if '3.9.3.3.5' in text and 'harvesting' in text.lower():
                    print(f"Found harvesting section on page {page_num + 1}")
                    lines = text.split('\n')
                    harvesting_lines = []
                    for line in lines:
                        if 'harvest' in line.lower() or 'month' in line.lower() or 'lift' in line.lower():
                            harvesting_lines.append(line.strip())
                    management_info['harvesting'] = ' '.join(harvesting_lines)
                
                # Extract potential yield information
                if 'yield' in text.lower() and ('12,000' in text or 'kg' in text):
                    print(f"Found yield information on page {page_num + 1}")
                    lines = text.split('\n')
                    yield_lines = []
                    for line in lines:
                        if 'yield' in line.lower() and 'kg' in line.lower():
                            yield_lines.append(line.strip())
                    management_info['potential_yield'] = ' '.join(yield_lines)
        
        return management_info
    
    def insert_ginger_varieties(self, varieties: List[Dict], management_info: Dict[str, str]):
        """Insert ginger varieties into database using only existing columns"""
        
        if not self.ginger_crop_id:
            self.ginger_crop_id = self.get_ginger_crop_id()
            if not self.ginger_crop_id:
                print("Cannot insert varieties without ginger crop ID")
                return
        
        print(f"\nInserting {len(varieties)} ginger varieties into database...")
        
        inserted_count = 0
        for variety in varieties:
            try:
                # Prepare variety data using only essential columns
                variety_data = {
                    'crop_id': self.ginger_crop_id,
                    'crop_name': 'ginger',
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
                
                # Store additional information in text field
                harvesting_info = []
                if variety.get('special_notes'):
                    harvesting_info.append(variety['special_notes'])
                
                if harvesting_info:
                    variety_data['harvesting_guidelines'] = '; '.join(harvesting_info)
                
                # Add management information to existing fields
                management_text = []
                if management_info.get('field_preparation'):
                    management_text.append(f"Field preparation: {management_info['field_preparation']}")
                if management_info.get('planting'):
                    management_text.append(f"Planting: {management_info['planting']}")
                if management_info.get('fertilizer_application'):
                    management_text.append(f"Fertilizer: {management_info['fertilizer_application']}")
                if management_info.get('mulching'):
                    management_text.append(f"Mulching: {management_info['mulching']}")
                if management_info.get('pest_control'):
                    management_text.append(f"Pest control: {management_info['pest_control']}")
                if management_info.get('disease_control'):
                    management_text.append(f"Disease control: {management_info['disease_control']}")
                if management_info.get('harvesting'):
                    management_text.append(f"Harvesting: {management_info['harvesting']}")
                if management_info.get('potential_yield'):
                    management_text.append(f"Potential yield: {management_info['potential_yield']}")
                
                if management_text:
                    variety_data['fertilizer_requirements'] = '; '.join(management_text)
                
                # Insert into database
                result = supabase.table('varieties').insert(variety_data).execute()
                
                if result.data:
                    inserted_count += 1
                    print(f"OK Inserted: {variety['variety_name']}")
                else:
                    print(f"X Failed to insert: {variety['variety_name']}")
                    
            except Exception as e:
                print(f"X Error inserting {variety['variety_name']}: {str(e)}")
        
        print(f"\nSuccessfully inserted {inserted_count} out of {len(varieties)} ginger varieties")
    
    def extract_all_ginger_varieties(self):
        """Extract all ginger varieties and information"""
        
        print("=" * 80)
        print("GINGER VARIETY EXTRACTION")
        print("=" * 80)
        
        # Extract varieties from different sources
        varieties_section = self.extract_ginger_varieties_from_section_3_9_3_2_1()
        
        # Extract management information
        management_info = self.extract_management_info()
        
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
        print(f"- Varieties from section 3.9.3.2.1: {len(varieties_section)}")
        print(f"- Total unique varieties: {len(unique_varieties)}")
        
        # Insert into database
        self.insert_ginger_varieties(unique_varieties, management_info)
        
        return unique_varieties, management_info

def main():
    extractor = GingerVarietyExtractor()
    varieties, management_info = extractor.extract_all_ginger_varieties()
    
    print(f"\nGinger extraction completed!")
    print(f"Extracted {len(varieties)} unique varieties")

if __name__ == "__main__":
    main()
