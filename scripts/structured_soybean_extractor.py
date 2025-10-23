#!/usr/bin/env python3
"""
Structured Soybean Variety Extractor
Extract soybean varieties from Guide to Agriculture Production in Malawi 2021
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

class SoybeanVarietyExtractor:
    def __init__(self):
        self.pdf_path = PDF_PATH
        self.soybean_crop_id = None
        
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
        
        # Look for patterns like "90 to 120 days", "130-150 days", etc.
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
            r'yield\s*of\s*(\d+)\s*kg/ha'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)} kg/ha"
                else:
                    return f"{match.group(1)} kg/ha"
        
        return None
    
    def get_soybean_crop_id(self) -> Optional[int]:
        """Get soybean crop ID from database"""
        try:
            result = supabase.table('crops').select('id').eq('crop_name', 'soybean').execute()
            if result.data:
                return result.data[0]['id']
            else:
                print("Soybean crop not found in database")
                return None
        except Exception as e:
            print(f"Error getting soybean crop ID: {str(e)}")
            return None
    
    def extract_soybean_varieties_from_table32(self) -> List[Dict]:
        """Extract varieties from Table 32"""
        varieties = []
        
        print("Extracting varieties from Table 32...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(195, 200):  # Search around page 197
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if 'table 32' in text.lower():
                    print(f"Found Table 32 on page {page_num + 1}")
                    
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
                                source_material = str(row[1]).strip()
                                maturity_period = str(row[2]).strip()
                                agro_ecologies = str(row[3]).strip()
                                special_attributes = str(row[4]).strip()
                                
                                if variety_name and len(variety_name) > 2:
                                    variety_info = {
                                        'variety_name': variety_name,
                                        'originator': source_material,
                                        'maturity_days': self.parse_days_to_maturity(maturity_period),
                                        'yield_potential': self.parse_yield(special_attributes),
                                        'table_source': 'Table 32'
                                    }
                                    
                                    # Store additional information
                                    additional_info = []
                                    if agro_ecologies:
                                        additional_info.append(f"Agro-ecologies: {agro_ecologies}")
                                    if special_attributes:
                                        additional_info.append(f"Attributes: {special_attributes}")
                                    
                                    variety_info['special_notes'] = '; '.join(additional_info)
                                    
                                    # Extract growth habit from special attributes
                                    if 'indeterminate' in special_attributes.lower():
                                        variety_info['type'] = 'Indeterminate'
                                    elif 'determinate' in special_attributes.lower():
                                        variety_info['type'] = 'Determinate'
                                    
                                    varieties.append(variety_info)
        
        return varieties
    
    def extract_soybean_varieties_from_section_3_2_4_2(self) -> List[Dict]:
        """Extract varieties from section 3.2.4.2 (improved varieties)"""
        varieties = []
        
        print("Extracting varieties from section 3.2.4.2 (improved varieties)...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(194, 198):  # Search around pages 195-196
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.2.4.2' in text and 'improved varieties' in text.lower():
                    print(f"Found section 3.2.4.2 on page {page_num + 1}")
                    
                    # Extract detailed variety information
                    lines = text.split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Look for variety names with detailed descriptions
                        variety_patterns = [
                            r'3\.2\.4\.2\.1\.\s+(Ocepara\s+4.*?)(?=3\.2\.4\.2\.2\.|$)',
                            r'3\.2\.4\.2\.2\.\s+(Nasoko.*?)(?=3\.2\.4\.2\.3\.|$)',
                            r'3\.2\.4\.2\.3\.\s+(Makwacha.*?)(?=3\.2\.4\.2\.4\.|$)',
                            r'3\.2\.4\.2\.7\.\s+(Soprano.*?)(?=3\.2\.4\.2\.8\.|$)',
                            r'3\.2\.4\.2\.8\.\s+(PAN\s+1867.*?)(?=3\.2\.4\.2\.9\.|$)',
                            r'3\.2\.4\.2\.9\.\s+(Solitaire.*?)(?=3\.2\.4\.2\.10\.|$)',
                            r'3\.2\.4\.2\.10\.\s+(SC\s+Serenade.*?)(?=3\.2\.4\.2\.11\.|$)',
                            r'3\.2\.4\.2\.12\.\s+(SC\s+Squire.*?)(?=3\.2\.4\.2\.13\.|$)',
                            r'3\.2\.4\.2\.13\.\s+(SC\s+Sequel.*?)(?=3\.2\.4\.2\.14\.|$)',
                            r'3\.2\.4\.2\.14\.\s+(Tikolore.*?)(?=3\.2\.4\.3\.|$)'
                        ]
                        
                        for pattern in variety_patterns:
                            match = re.search(pattern, line, re.IGNORECASE | re.DOTALL)
                            if match:
                                variety_text = match.group(1)
                                
                                # Extract variety name
                                variety_name_match = re.search(r'^([^(]+)', variety_text)
                                if variety_name_match:
                                    variety_name = self.clean_variety_name(variety_name_match.group(1))
                                    
                                    if variety_name:
                                        variety_info = {
                                            'variety_name': variety_name,
                                            'table_source': 'Section 3.2.4.2'
                                        }
                                        
                                        # Extract additional information
                                        variety_info['maturity_days'] = self.parse_days_to_maturity(variety_text)
                                        variety_info['yield_potential'] = self.parse_yield(variety_text)
                                        
                                        # Store detailed information
                                        variety_info['special_notes'] = variety_text
                                        
                                        # Extract growth habit
                                        if 'indeterminate' in variety_text.lower():
                                            variety_info['type'] = 'Indeterminate'
                                        elif 'determinate' in variety_text.lower():
                                            variety_info['type'] = 'Determinate'
                                        
                                        varieties.append(variety_info)
        
        return varieties
    
    def extract_fertilizer_info(self) -> str:
        """Extract fertilizer information from section 3.2.4.7"""
        fertilizer_info = ""
        
        print("Extracting fertilizer information from section 3.2.4.7...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(197, 201):  # Search around page 198
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.2.4.7' in text and 'fertilizer' in text.lower():
                    print(f"Found fertilizer section on page {page_num + 1}")
                    
                    # Extract fertilizer information
                    lines = text.split('\n')
                    fertilizer_text = []
                    
                    for line in lines:
                        if 'fertilizer' in line.lower() or 'rhizobium' in line.lower() or 'inoculant' in line.lower():
                            fertilizer_text.append(line.strip())
                    
                    fertilizer_info = ' '.join(fertilizer_text)
        
        return fertilizer_info
    
    def insert_soybean_varieties(self, varieties: List[Dict], fertilizer_info: str):
        """Insert soybean varieties into database using only existing columns"""
        
        if not self.soybean_crop_id:
            self.soybean_crop_id = self.get_soybean_crop_id()
            if not self.soybean_crop_id:
                print("Cannot insert varieties without soybean crop ID")
                return
        
        print(f"\nInserting {len(varieties)} soybean varieties into database...")
        
        inserted_count = 0
        for variety in varieties:
            try:
                # Prepare variety data using only essential columns
                variety_data = {
                    'crop_id': self.soybean_crop_id,
                    'crop_name': 'soybean',
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
        
        print(f"\nSuccessfully inserted {inserted_count} out of {len(varieties)} soybean varieties")
    
    def extract_all_soybean_varieties(self):
        """Extract all soybean varieties and information"""
        
        print("=" * 80)
        print("SOYBEAN VARIETY EXTRACTION")
        print("=" * 80)
        
        # Extract varieties from different sources
        varieties_table32 = self.extract_soybean_varieties_from_table32()
        varieties_section = self.extract_soybean_varieties_from_section_3_2_4_2()
        
        # Extract additional information
        fertilizer_info = self.extract_fertilizer_info()
        
        # Combine all varieties
        all_varieties = varieties_table32 + varieties_section
        
        # Remove duplicates based on variety name
        unique_varieties = []
        seen_names = set()
        
        for variety in all_varieties:
            variety_name = variety['variety_name'].lower()
            if variety_name not in seen_names:
                seen_names.add(variety_name)
                unique_varieties.append(variety)
        
        print(f"\nExtraction Summary:")
        print(f"- Varieties from Table 32: {len(varieties_table32)}")
        print(f"- Varieties from section 3.2.4.2: {len(varieties_section)}")
        print(f"- Total unique varieties: {len(unique_varieties)}")
        
        # Insert into database
        self.insert_soybean_varieties(unique_varieties, fertilizer_info)
        
        return unique_varieties, fertilizer_info

def main():
    extractor = SoybeanVarietyExtractor()
    varieties, fertilizer_info = extractor.extract_all_soybean_varieties()
    
    print(f"\nSoybean extraction completed!")
    print(f"Extracted {len(varieties)} unique varieties")

if __name__ == "__main__":
    main()
