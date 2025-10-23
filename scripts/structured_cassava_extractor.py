#!/usr/bin/env python3
"""
Structured Cassava Variety Extractor
Extract cassava varieties from Guide to Agriculture Production in Malawi 2021
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

class CassavaVarietyExtractor:
    def __init__(self):
        self.pdf_path = PDF_PATH
        self.cassava_crop_id = None
        
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
    
    def parse_maturity_period(self, text: str) -> Optional[str]:
        """Parse maturity period from text"""
        if not text:
            return None
        
        # Look for patterns like "12-15 months", "9-18 months", etc.
        patterns = [
            r'(\d+)\s*-\s*(\d+)\s*months?',
            r'(\d+)\s*to\s*(\d+)\s*months?',
            r'(\d+)\s*months?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)} months"
                else:
                    return f"{match.group(1)} months"
        
        return None
    
    def parse_yield(self, text: str) -> Optional[str]:
        """Parse yield information from text"""
        if not text:
            return None
        
        # Look for yield patterns
        patterns = [
            r'(\d+)\s*tonnes?/ha',
            r'(\d+)\s*tonnes?\s*per\s*hectare',
            r'(\d+)\s*t/ha',
            r'(\d+)\s*-\s*(\d+)\s*tonnes?/ha',
            r'(\d+)\s*-\s*(\d+)\s*tonnes?\s*per\s*hectare'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)} tonnes/ha"
                else:
                    return f"{match.group(1)} tonnes/ha"
        
        return None
    
    def get_cassava_crop_id(self) -> Optional[int]:
        """Get cassava crop ID from database"""
        try:
            result = supabase.table('crops').select('id').eq('crop_name', 'cassava').execute()
            if result.data:
                return result.data[0]['id']
            else:
                print("Cassava crop not found in database")
                return None
        except Exception as e:
            print(f"Error getting cassava crop ID: {str(e)}")
            return None
    
    def extract_cassava_varieties_from_table_42(self) -> List[Dict]:
        """Extract varieties from Table 42"""
        varieties = []
        
        print("Extracting varieties from Table 42...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(218, 222):  # Search around pages 219-220
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if 'table 42' in text.lower():
                    print(f"Found Table 42 on page {page_num + 1}")
                    
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 2:
                            continue
                        
                        header_row = table[0]
                        if header_row and 'variety' in str(header_row).lower():
                            print(f"Found variety table: {header_row}")
                            
                            # Process table rows
                            for row_idx, row in enumerate(table[1:]):  # Skip header
                                if not row or len(row) < 5:
                                    continue
                                
                                variety_name = self.clean_variety_name(str(row[0]))
                                taste = str(row[1]).strip()
                                special_attribute = str(row[2]).strip()
                                maturity_period = str(row[3]).strip()
                                yield_potential = str(row[4]).strip()
                                
                                if variety_name and len(variety_name) > 2:
                                    variety_info = {
                                        'variety_name': variety_name,
                                        'taste': taste,
                                        'special_attribute': special_attribute,
                                        'maturity_period': self.parse_maturity_period(maturity_period),
                                        'yield_potential': self.parse_yield(yield_potential),
                                        'table_source': 'Table 42'
                                    }
                                    
                                    # Store additional information
                                    additional_info = []
                                    if taste:
                                        additional_info.append(f"Taste: {taste}")
                                    if special_attribute:
                                        additional_info.append(f"Special attribute: {special_attribute}")
                                    
                                    variety_info['special_notes'] = '; '.join(additional_info)
                                    
                                    varieties.append(variety_info)
        
        return varieties
    
    def extract_cassava_varieties_from_section_3_4_2_1(self) -> List[Dict]:
        """Extract varieties from section 3.4.2.1 (improved yields)"""
        varieties = []
        
        print("Extracting varieties from section 3.4.2.1 (improved yields)...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(218, 222):  # Search around pages 219-220
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.4.2.1' in text and 'improved varieties' in text.lower():
                    print(f"Found section 3.4.2.1 on page {page_num + 1}")
                    
                    # Extract variety information from text
                    lines = text.split('\n')
                    
                    # Look for sweet varieties
                    sweet_varieties = ['Chamandanda', 'Chinangwa 1', 'Chinangwa 2', 'Mpale', 'Kalawe', 'Mbundumali/Manyokola']
                    bitter_varieties = ['Gomani', 'Chitembwere', 'Silira', 'Maunjiri', 'Mkondezi', 'Sauti', 'Yizaso', 'Phoso', 'Mulola', 'Sagonja', 'Chiombola']
                    
                    for variety_name in sweet_varieties + bitter_varieties:
                        variety_info = {
                            'variety_name': self.clean_variety_name(variety_name),
                            'taste': 'Sweet' if variety_name in sweet_varieties else 'Bitter',
                            'table_source': 'Section 3.4.2.1'
                        }
                        
                        variety_info['special_notes'] = f"Taste: {variety_info['taste']}"
                        
                        varieties.append(variety_info)
        
        return varieties
    
    def extract_management_info(self) -> Dict[str, str]:
        """Extract management information from various sections"""
        management_info = {
            'seed_rate': '',
            'planting_time': '',
            'plant_population': '',
            'pest_control': '',
            'weed_control': '',
            'disease_control': ''
        }
        
        print("Extracting management information...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(220, 230):  # Search around pages 221-230
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # Extract seed rate information
                if '3.4.2.2.4' in text and 'seed rate' in text.lower():
                    print(f"Found seed rate section on page {page_num + 1}")
                    lines = text.split('\n')
                    seed_rate_lines = []
                    for line in lines:
                        if 'bundle' in line.lower() or 'hectare' in line.lower() or 'meter' in line.lower():
                            seed_rate_lines.append(line.strip())
                    management_info['seed_rate'] = ' '.join(seed_rate_lines)
                
                # Extract planting time information
                if '3.4.2.2.5' in text and 'time of planting' in text.lower():
                    print(f"Found planting time section on page {page_num + 1}")
                    lines = text.split('\n')
                    planting_lines = []
                    for line in lines:
                        if 'planting' in line.lower() or 'rain' in line.lower():
                            planting_lines.append(line.strip())
                    management_info['planting_time'] = ' '.join(planting_lines)
                
                # Extract plant population information
                if '3.4.2.2.6' in text and 'plant population' in text.lower():
                    print(f"Found plant population section on page {page_num + 1}")
                    lines = text.split('\n')
                    population_lines = []
                    for line in lines:
                        if 'population' in line.lower() or 'spacing' in line.lower() or 'cm' in line.lower():
                            population_lines.append(line.strip())
                    management_info['plant_population'] = ' '.join(population_lines)
                
                # Extract pest control information
                if '3.4.2.3' in text and 'pest control' in text.lower():
                    print(f"Found pest control section on page {page_num + 1}")
                    lines = text.split('\n')
                    pest_lines = []
                    for line in lines:
                        if 'pest' in line.lower() or 'insect' in line.lower() or 'mealy bug' in line.lower():
                            pest_lines.append(line.strip())
                    management_info['pest_control'] = ' '.join(pest_lines)
                
                # Extract weed control information
                if '3.4.2.3.1' in text and 'weed control' in text.lower():
                    print(f"Found weed control section on page {page_num + 1}")
                    lines = text.split('\n')
                    weed_lines = []
                    for line in lines:
                        if 'weed' in line.lower():
                            weed_lines.append(line.strip())
                    management_info['weed_control'] = ' '.join(weed_lines)
                
                # Extract disease control information
                if '3.4.2.3.3' in text and 'disease control' in text.lower():
                    print(f"Found disease control section on page {page_num + 1}")
                    lines = text.split('\n')
                    disease_lines = []
                    for line in lines:
                        if 'disease' in line.lower() or 'mosaic' in text.lower() or 'brown streak' in text.lower():
                            disease_lines.append(line.strip())
                    management_info['disease_control'] = ' '.join(disease_lines)
        
        return management_info
    
    def insert_cassava_varieties(self, varieties: List[Dict], management_info: Dict[str, str]):
        """Insert cassava varieties into database using only existing columns"""
        
        if not self.cassava_crop_id:
            self.cassava_crop_id = self.get_cassava_crop_id()
            if not self.cassava_crop_id:
                print("Cannot insert varieties without cassava crop ID")
                return
        
        print(f"\nInserting {len(varieties)} cassava varieties into database...")
        
        inserted_count = 0
        for variety in varieties:
            try:
                # Prepare variety data using only essential columns
                variety_data = {
                    'crop_id': self.cassava_crop_id,
                    'crop_name': 'cassava',
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
                if variety.get('maturity_period'):
                    harvesting_info.append(f"Maturity: {variety['maturity_period']}")
                if variety.get('taste'):
                    harvesting_info.append(f"Taste: {variety['taste']}")
                if variety.get('special_attribute'):
                    harvesting_info.append(f"Special attribute: {variety['special_attribute']}")
                if variety.get('special_notes'):
                    harvesting_info.append(variety['special_notes'])
                
                if harvesting_info:
                    variety_data['harvesting_guidelines'] = '; '.join(harvesting_info)
                
                # Add management information to existing fields
                management_text = []
                if management_info.get('seed_rate'):
                    management_text.append(f"Seed rate: {management_info['seed_rate']}")
                if management_info.get('planting_time'):
                    management_text.append(f"Planting time: {management_info['planting_time']}")
                if management_info.get('plant_population'):
                    management_text.append(f"Plant population: {management_info['plant_population']}")
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
        
        print(f"\nSuccessfully inserted {inserted_count} out of {len(varieties)} cassava varieties")
    
    def extract_all_cassava_varieties(self):
        """Extract all cassava varieties and information"""
        
        print("=" * 80)
        print("CASSAVA VARIETY EXTRACTION")
        print("=" * 80)
        
        # Extract varieties from different sources
        varieties_table42 = self.extract_cassava_varieties_from_table_42()
        varieties_section = self.extract_cassava_varieties_from_section_3_4_2_1()
        
        # Extract management information
        management_info = self.extract_management_info()
        
        # Combine all varieties
        all_varieties = varieties_table42 + varieties_section
        
        # Remove duplicates based on variety name
        unique_varieties = []
        seen_names = set()
        
        for variety in all_varieties:
            variety_name = variety['variety_name'].lower()
            if variety_name not in seen_names:
                seen_names.add(variety_name)
                unique_varieties.append(variety)
        
        print(f"\nExtraction Summary:")
        print(f"- Varieties from Table 42: {len(varieties_table42)}")
        print(f"- Varieties from section 3.4.2.1: {len(varieties_section)}")
        print(f"- Total unique varieties: {len(unique_varieties)}")
        
        # Insert into database
        self.insert_cassava_varieties(unique_varieties, management_info)
        
        return unique_varieties, management_info

def main():
    extractor = CassavaVarietyExtractor()
    varieties, management_info = extractor.extract_all_cassava_varieties()
    
    print(f"\nCassava extraction completed!")
    print(f"Extracted {len(varieties)} unique varieties")

if __name__ == "__main__":
    main()
