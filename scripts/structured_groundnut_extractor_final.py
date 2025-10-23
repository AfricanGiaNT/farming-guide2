#!/usr/bin/env python3
"""
Structured Groundnut Variety Extractor - Using Existing Columns Only
Extract groundnut varieties from Guide to Agriculture Production in Malawi 2021
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

class GroundnutVarietyExtractor:
    def __init__(self):
        self.pdf_path = PDF_PATH
        self.groundnut_crop_id = None
        
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
            r'matures?\s*in\s*(\d+)\s*days?'
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
            r'(\d+)\s*-\s*(\d+)\s*kg/ha'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)} kg/ha"
                else:
                    return f"{match.group(1)} kg/ha"
        
        return None
    
    def get_groundnut_crop_id(self) -> Optional[int]:
        """Get groundnut crop ID from database"""
        try:
            result = supabase.table('crops').select('id').eq('crop_name', 'groundnut').execute()
            if result.data:
                return result.data[0]['id']
            else:
                print("Groundnut crop not found in database")
                return None
        except Exception as e:
            print(f"Error getting groundnut crop ID: {str(e)}")
            return None
    
    def extract_groundnut_varieties_from_table30(self) -> List[Dict]:
        """Extract varieties from Table 30"""
        varieties = []
        
        print("Extracting varieties from Table 30...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(190, 195):  # Search around page 192
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if 'table 30' in text.lower():
                    print(f"Found Table 30 on page {page_num + 1}")
                    
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 2:
                            continue
                        
                        header_row = table[0]
                        if header_row and 'varieties' in str(header_row).lower():
                            print(f"Found variety table: {header_row}")
                            
                            # Process table rows
                            for row_idx, row in enumerate(table[1:]):  # Skip header
                                if not row or len(row) < 2:
                                    continue
                                
                                botanical_group = str(row[0]).strip()
                                variety_names = str(row[1]).strip()
                                spacing = str(row[2]).strip() if len(row) > 2 else ""
                                seed_rate = str(row[3]).strip() if len(row) > 3 else ""
                                
                                # Parse individual variety names
                                variety_list = re.split(r'[,;\n]', variety_names)
                                
                                for variety_name in variety_list:
                                    variety_name = self.clean_variety_name(variety_name)
                                    if variety_name and len(variety_name) > 2:
                                        # Store additional info in existing fields
                                        additional_info = []
                                        if botanical_group:
                                            additional_info.append(f"Botanical Group: {botanical_group}")
                                        if spacing:
                                            additional_info.append(f"Spacing: {spacing}")
                                        if seed_rate:
                                            additional_info.append(f"Seed Rate: {seed_rate}")
                                        
                                        varieties.append({
                                            'variety_name': variety_name,
                                            'type': botanical_group,
                                            'spacing_requirements': spacing,
                                            'special_notes': '; '.join(additional_info),
                                            'table_source': 'Table 30'
                                        })
        
        return varieties
    
    def extract_groundnut_varieties_from_section_3_2_3_1(self) -> List[Dict]:
        """Extract varieties from section 3.2.3.1 (being promoted)"""
        varieties = []
        
        print("Extracting varieties from section 3.2.3.1 (being promoted)...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(188, 192):  # Search around page 189
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.2.3.1' in text and 'being promoted' in text.lower():
                    print(f"Found section 3.2.3.1 on page {page_num + 1}")
                    
                    # Look for variety lists
                    lines = text.split('\n')
                    for line in lines:
                        if 'being promoted' in line.lower() and 'varieties' in line.lower():
                            # Extract variety names from this line and following lines
                            variety_text = line
                            
                            # Look for variety patterns
                            variety_patterns = [
                                r'CG\s+\d+',
                                r'Chalimbana\s+\d+',
                                r'Nsinjiro',
                                r'Chitala',
                                r'Kakoma',
                                r'Baka'
                            ]
                            
                            for pattern in variety_patterns:
                                matches = re.findall(pattern, variety_text, re.IGNORECASE)
                                for match in matches:
                                    variety_name = self.clean_variety_name(match)
                                    if variety_name:
                                        varieties.append({
                                            'variety_name': variety_name,
                                            'type': 'Promoted Variety',
                                            'special_notes': 'Being promoted by national programme',
                                            'table_source': 'Section 3.2.3.1'
                                        })
        
        return varieties
    
    def extract_groundnut_varieties_from_section_3_2_3_2(self) -> List[Dict]:
        """Extract varieties from section 3.2.3.2 (recommended improved varieties)"""
        varieties = []
        
        print("Extracting varieties from section 3.2.3.2 (recommended improved varieties)...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(189, 193):  # Search around page 190
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.2.3.2' in text and 'recommended' in text.lower():
                    print(f"Found section 3.2.3.2 on page {page_num + 1}")
                    
                    # Extract detailed variety information
                    lines = text.split('\n')
                    current_variety = None
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Look for variety names with detailed descriptions
                        variety_patterns = [
                            r'\(i\)\s+(CG\s+\d+.*?)\)',
                            r'\(ii\)\s+(Nsinjiro.*?)\)',
                            r'\(iii\)\s+(Chalimbana\s+\d+.*?)\)',
                            r'\(iv\)\s+(Kakoma.*?)\)',
                            r'\(v\)\s+(Baka.*?)\)',
                            r'\(vi\)\s+(Chitala.*?)\)'
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
                                            'type': 'Recommended Variety',
                                            'table_source': 'Section 3.2.3.2'
                                        }
                                        
                                        # Extract additional information
                                        variety_info['maturity_days'] = self.parse_days_to_maturity(variety_text)
                                        variety_info['yield_potential'] = self.parse_yield(variety_text)
                                        
                                        # Store detailed information in existing fields
                                        variety_info['special_notes'] = variety_text
                                        
                                        varieties.append(variety_info)
        
        return varieties
    
    def extract_fertilizer_info(self) -> str:
        """Extract fertilizer information from section 3.2.3.8"""
        fertilizer_info = ""
        
        print("Extracting fertilizer information from section 3.2.3.8...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(192, 196):  # Search around page 193
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.2.3.8' in text and 'fertilizer' in text.lower():
                    print(f"Found fertilizer section on page {page_num + 1}")
                    
                    # Extract fertilizer information
                    lines = text.split('\n')
                    fertilizer_text = []
                    
                    for line in lines:
                        if 'fertilizer' in line.lower() or 'basal' in line.lower() or 'top dressing' in line.lower():
                            fertilizer_text.append(line.strip())
                    
                    fertilizer_info = ' '.join(fertilizer_text)
        
        return fertilizer_info
    
    def extract_pest_control_info(self) -> str:
        """Extract pest control information from section 3.2.3.7"""
        pest_info = ""
        
        print("Extracting pest control information from section 3.2.3.7...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(192, 196):  # Search around page 193
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.2.3.7' in text and 'pest' in text.lower():
                    print(f"Found pest control section on page {page_num + 1}")
                    
                    # Extract pest control information
                    lines = text.split('\n')
                    pest_text = []
                    
                    for line in lines:
                        if 'pest' in line.lower() or 'insect' in line.lower() or 'control' in line.lower():
                            pest_text.append(line.strip())
                    
                    pest_info = ' '.join(pest_text)
        
        return pest_info
    
    def extract_disease_control_info(self) -> str:
        """Extract disease control information from section 3.2.3.6.2"""
        disease_info = ""
        
        print("Extracting disease control information from section 3.2.3.6.2...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(191, 195):  # Search around page 192
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                if '3.2.3.6.2' in text and 'disease' in text.lower():
                    print(f"Found disease control section on page {page_num + 1}")
                    
                    # Extract disease control information
                    lines = text.split('\n')
                    disease_text = []
                    
                    for line in lines:
                        if 'disease' in line.lower() or 'resistance' in line.lower() or 'control' in line.lower():
                            disease_text.append(line.strip())
                    
                    disease_info = ' '.join(disease_text)
        
        return disease_info
    
    def insert_groundnut_varieties(self, varieties: List[Dict], fertilizer_info: str, pest_info: str, disease_info: str):
        """Insert groundnut varieties into database using only existing columns"""
        
        if not self.groundnut_crop_id:
            self.groundnut_crop_id = self.get_groundnut_crop_id()
            if not self.groundnut_crop_id:
                print("Cannot insert varieties without groundnut crop ID")
                return
        
        print(f"\nInserting {len(varieties)} groundnut varieties into database...")
        
        inserted_count = 0
        for variety in varieties:
            try:
                # Prepare variety data using only essential columns
                variety_data = {
                    'crop_id': self.groundnut_crop_id,
                    'crop_name': 'groundnut',
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
                if variety.get('maturity_days'):
                    variety_data['maturity_days'] = variety['maturity_days']
                if variety.get('yield_potential'):
                    variety_data['yield_potential'] = variety['yield_potential']
                
                # Store additional information in existing text fields
                if variety.get('special_notes'):
                    variety_data['harvesting_guidelines'] = variety['special_notes']
                
                if variety.get('spacing_requirements'):
                    variety_data['spacing_requirements'] = variety['spacing_requirements']
                
                # Add general information to existing fields
                variety_data['fertilizer_requirements'] = fertilizer_info
                variety_data['pest_management'] = pest_info
                variety_data['disease_management'] = disease_info
                
                # Insert into database
                result = supabase.table('varieties').insert(variety_data).execute()
                
                if result.data:
                    inserted_count += 1
                    print(f"OK Inserted: {variety['variety_name']}")
                else:
                    print(f"X Failed to insert: {variety['variety_name']}")
                    
            except Exception as e:
                print(f"X Error inserting {variety['variety_name']}: {str(e)}")
        
        print(f"\nSuccessfully inserted {inserted_count} out of {len(varieties)} groundnut varieties")
    
    def extract_all_groundnut_varieties(self):
        """Extract all groundnut varieties and information"""
        
        print("=" * 80)
        print("GROUNDNUT VARIETY EXTRACTION")
        print("=" * 80)
        
        # Extract varieties from different sources
        varieties_table30 = self.extract_groundnut_varieties_from_table30()
        varieties_promoted = self.extract_groundnut_varieties_from_section_3_2_3_1()
        varieties_recommended = self.extract_groundnut_varieties_from_section_3_2_3_2()
        
        # Extract additional information
        fertilizer_info = self.extract_fertilizer_info()
        pest_info = self.extract_pest_control_info()
        disease_info = self.extract_disease_control_info()
        
        # Combine all varieties
        all_varieties = varieties_table30 + varieties_promoted + varieties_recommended
        
        # Remove duplicates based on variety name
        unique_varieties = []
        seen_names = set()
        
        for variety in all_varieties:
            variety_name = variety['variety_name'].lower()
            if variety_name not in seen_names:
                seen_names.add(variety_name)
                unique_varieties.append(variety)
        
        print(f"\nExtraction Summary:")
        print(f"- Varieties from Table 30: {len(varieties_table30)}")
        print(f"- Varieties from section 3.2.3.1 (promoted): {len(varieties_promoted)}")
        print(f"- Varieties from section 3.2.3.2 (recommended): {len(varieties_recommended)}")
        print(f"- Total unique varieties: {len(unique_varieties)}")
        
        # Insert into database
        self.insert_groundnut_varieties(unique_varieties, fertilizer_info, pest_info, disease_info)
        
        return unique_varieties, fertilizer_info, pest_info, disease_info

def main():
    extractor = GroundnutVarietyExtractor()
    varieties, fertilizer_info, pest_info, disease_info = extractor.extract_all_groundnut_varieties()
    
    print(f"\nGroundnut extraction completed!")
    print(f"Extracted {len(varieties)} unique varieties")

if __name__ == "__main__":
    main()
