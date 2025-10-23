#!/usr/bin/env python3
"""
Find Cassava Specific Sections
Locate sections 3.4.2.1, 3.4.2.3, 3.4.2.3.1, 3.4.3.3 and Table 42
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def find_cassava_specific_sections():
    """Find specific cassava sections"""
    
    print("=" * 80)
    print("FINDING CASSAVA SPECIFIC SECTIONS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Search for specific sections
        for page_num in range(220, 250):  # Search pages 220-250
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check for section 3.4.2.1 (improved yields)
            if '3.4.2.1' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.4.2.1 (IMPROVED YIELDS) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for section 3.4.2.3 (seed rate, planting, population)
            if '3.4.2.3' in text and ('seed rate' in text.lower() or 'planting' in text.lower() or 'population' in text.lower()):
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.4.2.3 (SEED RATE/PLANTING/POPULATION) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for section 3.4.2.3.1 (pest and weed control)
            if '3.4.2.3.1' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.4.2.3.1 (PEST AND WEED CONTROL) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for section 3.4.3.3 (disease control)
            if '3.4.3.3' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.4.3.3 (DISEASE CONTROL) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for Table 42
            if 'table 42' in text.lower():
                print(f"\n{'='*60}")
                print(f"FOUND TABLE 42 ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Extract tables
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    print(f"\nTable {table_idx + 1}: {len(table)} rows")
                    print(f"Columns: {table[0]}")
                    
                    # Show all rows
                    for row_idx, row in enumerate(table):
                        if row:
                            print(f"  Row {row_idx + 1}: {row}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")

def main():
    find_cassava_specific_sections()

if __name__ == "__main__":
    main()
