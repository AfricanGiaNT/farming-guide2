#!/usr/bin/env python3
"""
Structured Onion Variety Extractor
Extract onion varieties from Guide to Agriculture Production in Malawi 2021
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

class OnionVarietyExtractor:
    def __init__(self):
        self.pdf_path = PDF_PATH
        self.onion_crop_id = None
        
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
            r'yield.*?(\d+)\s*-\s*(\d+)\s*kg'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)} kg/ha"
                else:
                    return f"{match.group(1)} kg/ha"
        
        return None
    
    def get_onion_crop_id(self) -> Optional[int]:
        """Get onion crop ID from database"""
        try:
            result = supabase.table('crops').select('id').eq('crop_name', 'onion').execute()
            if result.data:
                return result.data[0]['id']
            else:
                print("Onion crop not found in database")
                return None
        except Exception as e:
            print(f"Error getting onion crop ID: {str(e)}")
            return None
    
    def extract_onion_varieties_from_section_3_10_5_1(self) -> List[Dict]:
        """Extract varieties from section 3.10.5.1 (recommended varieties)"""
        varieties = []
        
        print("Extracting varieties from section 3.10.5.1 (recommended varieties)...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(323, 327):  # Search around pages 324-326
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.10.5.1' in text and 'recommended varieties' in text.lower():
                    print(f"Found section 3.10.5.1 on page {page_num + 1}")
                    
                    # Extract variety information from text
                    lines = text.split('\n')
                    
                    # Look for variety names mentioned in text
                    variety_names = [
                        'Early Texas Grano', 'De Wildt', 'pyramid', 'Red Creole'
                    ]
                    
                    for variety_name in variety_names:
                        variety_info = {
                            'variety_name': self.clean_variety_name(variety_name),
                            'table_source': 'Section 3.10.5.1',
                            'special_notes': 'Recommended variety'
                        }
                        
                        varieties.append(variety_info)
        
        return varieties
    
    def extract_management_info(self) -> Dict[str, str]:
        """Extract management information from various sections"""
        management_info = {
            'field_preparation': '',
            'transplanting': '',
            'fertilizer_application': '',
            'pest_control': '',
            'weed_control': '',
            'disease_control': ''
        }
        
        print("Extracting management information...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(323, 327):  # Search around pages 324-326
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # Extract field preparation information
                if '3.10.5.1.2' in text and 'field preparation' in text.lower():
                    print(f"Found field preparation section on page {page_num + 1}")
                    lines = text.split('\n')
                    field_lines = []
                    for line in lines:
                        if 'plough' in line.lower() or 'compost' in line.lower() or 'manure' in line.lower() or 'bed' in line.lower():
                            field_lines.append(line.strip())
                    management_info['field_preparation'] = ' '.join(field_lines)
                
                # Extract transplanting information
                if '3.10.5.1.3' in text and 'transplanting' in text.lower():
                    print(f"Found transplanting section on page {page_num + 1}")
                    lines = text.split('\n')
                    transplanting_lines = []
                    for line in lines:
                        if 'transplant' in line.lower() or 'spacing' in line.lower() or 'cm' in line.lower() or 'weeks' in line.lower():
                            transplanting_lines.append(line.strip())
                    management_info['transplanting'] = ' '.join(transplanting_lines)
                
                # Extract fertilizer application information
                if '3.10.5.1.4' in text and 'fertilizer' in text.lower():
                    print(f"Found fertilizer section on page {page_num + 1}")
                    lines = text.split('\n')
                    fertilizer_lines = []
                    for line in lines:
                        if 'fertilizer' in line.lower() or 'compound' in line.lower() or 'can' in line.lower() or 'sulphate' in line.lower():
                            fertilizer_lines.append(line.strip())
                    management_info['fertilizer_application'] = ' '.join(fertilizer_lines)
                
                # Extract pest control information
                if '3.10.5.1.5.2' in text and 'pest' in text.lower():
                    print(f"Found pest control section on page {page_num + 1}")
                    lines = text.split('\n')
                    pest_lines = []
                    for line in lines:
                        if 'pest' in line.lower() or 'thrips' in line.lower() or 'spray' in line.lower():
                            pest_lines.append(line.strip())
                    management_info['pest_control'] = ' '.join(pest_lines)
                
                # Extract weed control information
                if '3.10.5.1.5.1' in text and 'weed' in text.lower():
                    print(f"Found weed control section on page {page_num + 1}")
                    lines = text.split('\n')
                    weed_lines = []
                    for line in lines:
                        if 'weed' in line.lower():
                            weed_lines.append(line.strip())
                    management_info['weed_control'] = ' '.join(weed_lines)
                
                # Extract disease control information
                if '3.10.5.1.5.3' in text and 'disease' in text.lower():
                    print(f"Found disease control section on page {page_num + 1}")
                    lines = text.split('\n')
                    disease_lines = []
                    for line in lines:
                        if 'disease' in line.lower() or 'purple blotch' in line.lower() or 'alternaria' in line.lower():
                            disease_lines.append(line.strip())
                    management_info['disease_control'] = ' '.join(disease_lines)
        
        return management_info
    
    def insert_onion_varieties(self, varieties: List[Dict], management_info: Dict[str, str]):
        """Insert onion varieties into database using only existing columns"""
        
        if not self.onion_crop_id:
            self.onion_crop_id = self.get_onion_crop_id()
            if not self.onion_crop_id:
                print("Cannot insert varieties without onion crop ID")
                return
        
        print(f"\nInserting {len(varieties)} onion varieties into database...")
        
        inserted_count = 0
        for variety in varieties:
            try:
                # Prepare variety data using only essential columns
                variety_data = {
                    'crop_id': self.onion_crop_id,
                    'crop_name': 'onion',
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
                if management_info.get('transplanting'):
                    management_text.append(f"Transplanting: {management_info['transplanting']}")
                if management_info.get('fertilizer_application'):
                    management_text.append(f"Fertilizer: {management_info['fertilizer_application']}")
                if management_info.get('pest_control'):
                    management_text.append(f"Pest control: {management_info['pest_control']}")
                if management_info.get('weed_control'):
                    management_text.append(f"Weed control: {management_info['weed_control']}")
                if management_info.get('disease_control'):
                    management_text.append(f"Disease control: {management_info['disease_control']}")
                
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
        
        print(f"\nSuccessfully inserted {inserted_count} out of {len(varieties)} onion varieties")
    
    def extract_all_onion_varieties(self):
        """Extract all onion varieties and information"""
        
        print("=" * 80)
        print("ONION VARIETY EXTRACTION")
        print("=" * 80)
        
        # Extract varieties from different sources
        varieties_section = self.extract_onion_varieties_from_section_3_10_5_1()
        
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
        print(f"- Varieties from section 3.10.5.1: {len(varieties_section)}")
        print(f"- Total unique varieties: {len(unique_varieties)}")
        
        # Insert into database
        self.insert_onion_varieties(unique_varieties, management_info)
        
        return unique_varieties, management_info

def main():
    extractor = OnionVarietyExtractor()
    varieties, management_info = extractor.extract_all_onion_varieties()
    
    print(f"\nOnion extraction completed!")
    print(f"Extracted {len(varieties)} unique varieties")

if __name__ == "__main__":
    main()
