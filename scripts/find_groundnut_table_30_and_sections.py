#!/usr/bin/env python3
"""
Find Groundnut Table 30 and Specific Sections
Locate Table 30 and sections 3.2.3.1, 3.2.3.2, 3.2.3.6.2, 3.2.3.7, 3.2.3.8
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def find_groundnut_table_30_and_sections():
    """Find Table 30 and specific groundnut sections"""
    
    print("=" * 80)
    print("FINDING GROUNDNUT TABLE 30 AND SPECIFIC SECTIONS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Search for Table 30 and specific sections
        for page_num in range(180, 220):  # Search pages 180-220
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check for Table 30
            if 'table 30' in text.lower() or 'table 30' in text:
                print(f"\n{'='*60}")
                print(f"FOUND TABLE 30 ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Extract tables
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    print(f"\nTable {table_idx + 1}: {len(table)} rows")
                    
                    # Check if this is Table 30
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
            
            # Check for section 3.2.3.1 (varieties being promoted)
            if '3.2.3.1' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.2.3.1 (VARIETIES BEING PROMOTED) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for section 3.2.3.2 (recommended improved varieties)
            if '3.2.3.2' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.2.3.2 (RECOMMENDED IMPROVED VARIETIES) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for section 3.2.3.6.2 (disease control)
            if '3.2.3.6.2' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.2.3.6.2 (DISEASE CONTROL) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for section 3.2.3.7 (insect pest control)
            if '3.2.3.7' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.2.3.7 (INSECT PEST CONTROL) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for section 3.2.3.8 (fertilizer)
            if '3.2.3.8' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.2.3.8 (FERTILIZER) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")

def main():
    find_groundnut_table_30_and_sections()

if __name__ == "__main__":
    main()
