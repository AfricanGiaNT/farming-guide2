#!/usr/bin/env python3
"""
Search for Tomato Section
Search more broadly for tomato section 3.10.4
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def search_for_tomato_section():
    """Search for tomato section more broadly"""
    
    print("=" * 80)
    print("SEARCHING FOR TOMATO SECTION")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Search through more pages
        for page_num in range(300, 600):  # Search pages 300-600
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Look for tomato-related content
            if 'tomato' in text.lower() or 'lycopersicon' in text.lower():
                print(f"\n{'='*60}")
                print(f"FOUND TOMATO CONTENT ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show first few lines
                lines = text.split('\n')
                for i, line in enumerate(lines[:15]):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
                
                # Check for specific sections
                if '3.10.4' in text:
                    print(f"\n*** FOUND SECTION 3.10.4 ON PAGE {page_num + 1} ***")
                
                if 'table 67' in text.lower():
                    print(f"\n*** FOUND TABLE 67 ON PAGE {page_num + 1} ***")
                
                # Extract tables if any
                tables = page.extract_tables()
                if tables:
                    print(f"\nTABLES FOUND: {len(tables)}")
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 2:
                            continue
                        
                        print(f"\nTable {table_idx + 1}: {len(table)} rows")
                        print(f"Columns: {table[0]}")
                        
                        # Show first few rows
                        for row_idx, row in enumerate(table[:3]):
                            if row:
                                print(f"  Row {row_idx + 1}: {row}")

def main():
    search_for_tomato_section()

if __name__ == "__main__":
    main()
