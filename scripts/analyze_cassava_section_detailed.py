#!/usr/bin/env python3
"""
Cassava Section Detailed Analysis
Examine cassava section to find variety tables, management info, and section structure
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def analyze_cassava_section():
    """Analyze cassava section in detail"""
    
    print("=" * 80)
    print("DETAILED CASSAVA SECTION ANALYSIS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # First, let's find the cassava section by searching for section 3.4.2
        cassava_pages = []
        
        # Search through pages to find cassava section
        for page_num in range(220, 300):  # Search pages 220-300
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Look for cassava section markers
            if '3.4.2' in text and ('cassava' in text.lower() or 'manihot' in text.lower()):
                cassava_pages.append(page_num + 1)
                print(f"Found cassava section on page {page_num + 1}")
        
        print(f"\nCassava section found on pages: {cassava_pages}")
        
        # Analyze each cassava page
        for page_num in cassava_pages:
            page_idx = page_num - 1
            if page_idx >= len(pdf.pages):
                continue
                
            page = pdf.pages[page_idx]
            text = page.extract_text() or ""
            
            print(f"\n{'='*60}")
            print(f"PAGE {page_num}")
            print(f"{'='*60}")
            
            # Look for specific sections
            sections = [
                '3.4.2.1',
                '3.4.2.2',
                '3.4.2.3',
                '3.4.2.3.1',
                '3.4.3.3',
                'table 42',
                'varieties',
                'improved',
                'seed rate',
                'planting',
                'population',
                'pest',
                'weed',
                'disease'
            ]
            
            found_sections = []
            for section in sections:
                if section in text.lower():
                    found_sections.append(section)
            
            if found_sections:
                print(f"Sections found: {', '.join(found_sections)}")
            
            # Look for variety-related content
            variety_keywords = ['variety', 'varieties', 'cultivar', 'cultivars', 'improved', 'yields']
            variety_lines = []
            
            lines = text.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in variety_keywords):
                    variety_lines.append(line.strip())
            
            if variety_lines:
                print(f"\nVARIETY INFORMATION FOUND:")
                for line in variety_lines[:10]:  # Show first 10
                    print(f"  {line}")
                if len(variety_lines) > 10:
                    print(f"  ... and {len(variety_lines) - 10} more lines")
            
            # Look for management-related content
            management_keywords = ['seed rate', 'planting', 'population', 'pest', 'weed', 'disease', 'control']
            management_lines = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in management_keywords):
                    management_lines.append(line.strip())
            
            if management_lines:
                print(f"\nMANAGEMENT INFORMATION FOUND:")
                for line in management_lines[:10]:  # Show first 10
                    print(f"  {line}")
                if len(management_lines) > 10:
                    print(f"  ... and {len(management_lines) - 10} more lines")
            
            # Extract tables
            tables = page.extract_tables()
            if tables:
                print(f"\nTABLES FOUND: {len(tables)}")
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    print(f"\nTable {table_idx + 1}: {len(table)} rows")
                    
                    # Check if this looks like a variety table
                    header_row = table[0]
                    if header_row and any(word in str(header_row).lower() for word in ["variety", "cultivar", "yield", "name"]):
                        print(f"  *** VARIETY TABLE FOUND ***")
                        print(f"  Columns: {header_row}")
                        
                        # Show first few rows
                        print(f"  First 3 rows:")
                        for row_idx, row in enumerate(table[:3]):
                            if row:
                                print(f"    Row {row_idx + 1}: {row}")
            
            # Show first few lines for context
            print(f"\nFIRST 10 LINES:")
            for i, line in enumerate(lines[:10]):
                if line.strip():
                    print(f"  {i+1}: {line.strip()}")

def main():
    analyze_cassava_section()

if __name__ == "__main__":
    main()
