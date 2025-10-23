#!/usr/bin/env python3
"""
Structured Tomato Variety Extractor
Extract tomato varieties from Guide to Agriculture Production in Malawi 2021
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

class TomatoVarietyExtractor:
    def __init__(self):
        self.pdf_path = PDF_PATH
        self.tomato_crop_id = None
        
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
            r'(\d+\.?\d*)\s*mt/ha',
            r'(\d+\.?\d*)\s*tonnes?/ha',
            r'(\d+\.?\d*)\s*tonnes?\s*per\s*hectare',
            r'(\d+\.?\d*)\s*t/ha',
            r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s*mt/ha',
            r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s*tonnes?/ha'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)} mt/ha"
                else:
                    return f"{match.group(1)} mt/ha"
        
        return None
    
    def get_tomato_crop_id(self) -> Optional[int]:
        """Get tomato crop ID from database"""
        try:
            result = supabase.table('crops').select('id').eq('crop_name', 'tomato').execute()
            if result.data:
                return result.data[0]['id']
            else:
                print("Tomato crop not found in database")
                return None
        except Exception as e:
            print(f"Error getting tomato crop ID: {str(e)}")
            return None
    
    def extract_tomato_varieties_from_table_67(self) -> List[Dict]:
        """Extract varieties from Table 67"""
        varieties = []
        
        print("Extracting varieties from Table 67...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(321, 325):  # Search around pages 322-324
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if 'table 67' in text.lower():
                    print(f"Found Table 67 on page {page_num + 1}")
                    
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 2:
                            continue
                        
                        header_row = table[0]
                        if header_row and 'variety' in str(header_row).lower():
                            print(f"Found variety table: {header_row}")
                            
                            # Process table rows
                            for row_idx, row in enumerate(table[1:]):  # Skip header
                                if not row or len(row) < 2:
                                    continue
                                
                                variety_name = self.clean_variety_name(str(row[0]))
                                yield_potential = str(row[1]).strip()
                                
                                if variety_name and len(variety_name) > 2:
                                    variety_info = {
                                        'variety_name': variety_name,
                                        'yield_potential': self.parse_yield(yield_potential),
                                        'table_source': 'Table 67'
                                    }
                                    
                                    # Store additional information
                                    variety_info['special_notes'] = f"Yield: {yield_potential}"
                                    
                                    varieties.append(variety_info)
        
        return varieties
    
    def extract_tomato_varieties_from_section_3_10_4_1(self) -> List[Dict]:
        """Extract varieties from section 3.10.4.1 (improved yields)"""
        varieties = []
        
        print("Extracting varieties from section 3.10.4.1 (improved yields)...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(321, 325):  # Search around pages 322-324
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.10.4.1' in text and 'improved yields' in text.lower():
                    print(f"Found section 3.10.4.1 on page {page_num + 1}")
                    
                    # Extract variety information from text
                    lines = text.split('\n')
                    
                    # Look for variety names mentioned in text
                    variety_names = [
                        'Money Maker', 'Marglobe', 'Heinz', 'Homestead', 'Roma VF',
                        'Mpindulitsa', 'Mbambande', 'Khama', 'Changu', 'Cheyenne', 'Steel'
                    ]
                    
                    for variety_name in variety_names:
                        variety_info = {
                            'variety_name': self.clean_variety_name(variety_name),
                            'table_source': 'Section 3.10.4.1'
                        }
                        
                        # Add special notes based on variety type
                        if variety_name in ['Money Maker', 'Marglobe', 'Heinz', 'Homestead', 'Roma VF']:
                            variety_info['special_notes'] = 'Traditional variety'
                            if variety_name == 'Roma VF':
                                variety_info['special_notes'] += '; Suitable for processing industry'
                        else:
                            variety_info['special_notes'] = 'Newly released variety'
                        
                        varieties.append(variety_info)
        
        return varieties
    
    def extract_management_info(self) -> Dict[str, str]:
        """Extract management information from various sections"""
        management_info = {
            'fertilizer_application': '',
            'transplanting_time': '',
            'spacing': '',
            'pest_control': '',
            'weed_control': '',
            'disease_control': ''
        }
        
        print("Extracting management information...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(322, 326):  # Search around pages 323-325
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # Extract fertilizer application information
                if '3.10.4.1.3' in text and 'fertilizer' in text.lower():
                    print(f"Found fertilizer section on page {page_num + 1}")
                    lines = text.split('\n')
                    fertilizer_lines = []
                    for line in lines:
                        if 'fertilizer' in line.lower() or 'compound' in line.lower() or 'can' in line.lower():
                            fertilizer_lines.append(line.strip())
                    management_info['fertilizer_application'] = ' '.join(fertilizer_lines)
                
                # Extract transplanting time and spacing information
                if '3.10.4.1.4' in text and ('transplanting' in text.lower() or 'spacing' in text.lower()):
                    print(f"Found transplanting/spacing section on page {page_num + 1}")
                    lines = text.split('\n')
                    transplanting_lines = []
                    for line in lines:
                        if 'transplant' in line.lower() or 'spacing' in line.lower() or 'cm' in line.lower():
                            transplanting_lines.append(line.strip())
                    management_info['transplanting_time'] = ' '.join(transplanting_lines)
                
                # Extract pest control information
                if '3.10.4.1.5.2' in text and 'pest' in text.lower():
                    print(f"Found pest control section on page {page_num + 1}")
                    lines = text.split('\n')
                    pest_lines = []
                    for line in lines:
                        if 'pest' in line.lower() or 'aphid' in line.lower() or 'caterpillar' in line.lower() or 'mite' in line.lower():
                            pest_lines.append(line.strip())
                    management_info['pest_control'] = ' '.join(pest_lines)
                
                # Extract weed control information
                if '3.10.4.1.5.1' in text and 'weed' in text.lower():
                    print(f"Found weed control section on page {page_num + 1}")
                    lines = text.split('\n')
                    weed_lines = []
                    for line in lines:
                        if 'weed' in line.lower():
                            weed_lines.append(line.strip())
                    management_info['weed_control'] = ' '.join(weed_lines)
                
                # Extract disease control information
                if '3.10.4.1.5.4' in text and 'disease' in text.lower():
                    print(f"Found disease control section on page {page_num + 1}")
                    lines = text.split('\n')
                    disease_lines = []
                    for line in lines:
                        if 'disease' in line.lower() or 'blight' in line.lower() or 'wilt' in line.lower():
                            disease_lines.append(line.strip())
                    management_info['disease_control'] = ' '.join(disease_lines)
        
        return management_info
    
    def insert_tomato_varieties(self, varieties: List[Dict], management_info: Dict[str, str]):
        """Insert tomato varieties into database using only existing columns"""
        
        if not self.tomato_crop_id:
            self.tomato_crop_id = self.get_tomato_crop_id()
            if not self.tomato_crop_id:
                print("Cannot insert varieties without tomato crop ID")
                return
        
        print(f"\nInserting {len(varieties)} tomato varieties into database...")
        
        inserted_count = 0
        for variety in varieties:
            try:
                # Prepare variety data using only essential columns
                variety_data = {
                    'crop_id': self.tomato_crop_id,
                    'crop_name': 'tomato',
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
                if management_info.get('fertilizer_application'):
                    management_text.append(f"Fertilizer: {management_info['fertilizer_application']}")
                if management_info.get('transplanting_time'):
                    management_text.append(f"Transplanting: {management_info['transplanting_time']}")
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
        
        print(f"\nSuccessfully inserted {inserted_count} out of {len(varieties)} tomato varieties")
    
    def extract_all_tomato_varieties(self):
        """Extract all tomato varieties and information"""
        
        print("=" * 80)
        print("TOMATO VARIETY EXTRACTION")
        print("=" * 80)
        
        # Extract varieties from different sources
        varieties_table67 = self.extract_tomato_varieties_from_table_67()
        varieties_section = self.extract_tomato_varieties_from_section_3_10_4_1()
        
        # Extract management information
        management_info = self.extract_management_info()
        
        # Combine all varieties
        all_varieties = varieties_table67 + varieties_section
        
        # Remove duplicates based on variety name
        unique_varieties = []
        seen_names = set()
        
        for variety in all_varieties:
            variety_name = variety['variety_name'].lower()
            if variety_name not in seen_names:
                seen_names.add(variety_name)
                unique_varieties.append(variety)
        
        print(f"\nExtraction Summary:")
        print(f"- Varieties from Table 67: {len(varieties_table67)}")
        print(f"- Varieties from section 3.10.4.1: {len(varieties_section)}")
        print(f"- Total unique varieties: {len(unique_varieties)}")
        
        # Insert into database
        self.insert_tomato_varieties(unique_varieties, management_info)
        
        return unique_varieties, management_info

def main():
    extractor = TomatoVarietyExtractor()
    varieties, management_info = extractor.extract_all_tomato_varieties()
    
    print(f"\nTomato extraction completed!")
    print(f"Extracted {len(varieties)} unique varieties")

if __name__ == "__main__":
    main()
