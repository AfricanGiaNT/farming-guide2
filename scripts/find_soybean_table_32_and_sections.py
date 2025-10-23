#!/usr/bin/env python3
"""
Find Soybean Table 32 and Specific Sections
Locate Table 32 and sections 3.2.4.2, 3.2.4.7
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def find_soybean_table_32_and_sections():
    """Find Table 32 and specific soybean sections"""
    
    print("=" * 80)
    print("FINDING SOYBEAN TABLE 32 AND SPECIFIC SECTIONS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Search for Table 32 and specific sections
        for page_num in range(190, 220):  # Search pages 190-220
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check for Table 32
            if 'table 32' in text.lower() or 'table 32' in text:
                print(f"\n{'='*60}")
                print(f"FOUND TABLE 32 ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Extract tables
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    print(f"\nTable {table_idx + 1}: {len(table)} rows")
                    
                    # Check if this is Table 32
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
            
            # Check for section 3.2.4.2 (improved varieties)
            if '3.2.4.2' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.2.4.2 (IMPROVED VARIETIES) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for section 3.2.4.7 (fertilizer recommendations)
            if '3.2.4.7' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.2.4.7 (FERTILIZER RECOMMENDATIONS) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")

def main():
    find_soybean_table_32_and_sections()

if __name__ == "__main__":
    main()
