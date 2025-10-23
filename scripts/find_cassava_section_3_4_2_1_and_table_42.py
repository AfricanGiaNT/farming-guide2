#!/usr/bin/env python3
"""
Find Cassava Section 3.4.2.1 and Table 42
Search specifically for these sections
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def find_cassava_section_3_4_2_1_and_table_42():
    """Find section 3.4.2.1 and Table 42"""
    
    print("=" * 80)
    print("FINDING CASSAVA SECTION 3.4.2.1 AND TABLE 42")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Search for section 3.4.2.1 and Table 42
        for page_num in range(215, 230):  # Search pages 215-230
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check for section 3.4.2.1
            if '3.4.2.1' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.4.2.1 ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for Table 42
            if 'table 42' in text.lower() or '42' in text and 'variety' in text.lower():
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
    find_cassava_section_3_4_2_1_and_table_42()

if __name__ == "__main__":
    main()
