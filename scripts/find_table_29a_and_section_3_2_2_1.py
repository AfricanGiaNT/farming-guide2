#!/usr/bin/env python3
"""
Find Table 29a and Section 3.2.2.1
Locate the specific table and section for beans variety extraction
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def find_table_29a_and_section_3_2_2_1():
    """Find Table 29a and section 3.2.2.1"""
    
    print("=" * 80)
    print("FINDING TABLE 29A AND SECTION 3.2.2.1")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Search for Table 29a and section 3.2.2.1
        for page_num in range(180, 220):  # Search pages 180-220
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check for Table 29a
            if 'table 29a' in text.lower() or 'table 29a' in text:
                print(f"\n{'='*60}")
                print(f"FOUND TABLE 29A ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Extract tables
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    print(f"\nTable {table_idx + 1}: {len(table)} rows")
                    
                    # Check if this is Table 29a
                    header_row = table[0]
                    print(f"Columns: {header_row}")
                    
                    # Show all rows
                    print(f"All rows:")
                    for row_idx, row in enumerate(table):
                        if row:
                            print(f"  Row {row_idx + 1}: {row}")
                
                # Show page text for context
                print(f"\nPage text:")
                lines = text.split('\n')
                for i, line in enumerate(lines[:20]):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for section 3.2.2.1
            if '3.2.2.1' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.2.2.1 ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for section 3.2.2.5 (fertilizer)
            if '3.2.2.5' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.2.2.5 (FERTILIZER) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")

def main():
    find_table_29a_and_section_3_2_2_1()

if __name__ == "__main__":
    main()
