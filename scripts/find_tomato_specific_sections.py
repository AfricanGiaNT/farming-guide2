#!/usr/bin/env python3
"""
Find Tomato Specific Sections
Locate sections 3.10.4.1, Table 67, and management sections
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def find_tomato_specific_sections():
    """Find specific tomato sections"""
    
    print("=" * 80)
    print("FINDING TOMATO SPECIFIC SECTIONS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Search for specific sections
        for page_num in range(320, 330):  # Search pages 320-330
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check for section 3.10.4.1 (improved yields)
            if '3.10.4.1' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.10.4.1 ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for Table 67
            if 'table 67' in text.lower():
                print(f"\n{'='*60}")
                print(f"FOUND TABLE 67 ON PAGE {page_num + 1}")
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
            
            # Check for fertilizer application
            if 'fertilizer' in text.lower() and '3.10.4' in text:
                print(f"\n{'='*60}")
                print(f"FOUND FERTILIZER SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for transplanting and spacing
            if ('transplanting' in text.lower() or 'spacing' in text.lower()) and '3.10.4' in text:
                print(f"\n{'='*60}")
                print(f"FOUND TRANSPLANTING/SPACING SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for pest control
            if 'pest' in text.lower() and '3.10.4' in text:
                print(f"\n{'='*60}")
                print(f"FOUND PEST CONTROL SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for weed control
            if 'weed' in text.lower() and '3.10.4' in text:
                print(f"\n{'='*60}")
                print(f"FOUND WEED CONTROL SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")

def main():
    find_tomato_specific_sections()

if __name__ == "__main__":
    main()
