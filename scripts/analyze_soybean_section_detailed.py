#!/usr/bin/env python3
"""
Soybean Section Detailed Analysis
Examine soybean section to find variety tables, fertilizer info, and section structure
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def analyze_soybean_section():
    """Analyze soybean section in detail"""
    
    print("=" * 80)
    print("DETAILED SOYBEAN SECTION ANALYSIS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # First, let's find the soybean section by searching for section 3.2.4
        soybean_pages = []
        
        # Search through pages to find soybean section
        for page_num in range(190, 250):  # Search pages 190-250
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Look for soybean section markers
            if '3.2.4' in text and ('soybean' in text.lower() or 'soya' in text.lower() or 'glycine' in text.lower()):
                soybean_pages.append(page_num + 1)
                print(f"Found soybean section on page {page_num + 1}")
        
        print(f"\nSoybean section found on pages: {soybean_pages}")
        
        # Analyze each soybean page
        for page_num in soybean_pages:
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
                '3.2.4.2',
                '3.2.4.7',
                'table 32',
                'varieties',
                'fertilizer',
                'improved'
            ]
            
            found_sections = []
            for section in sections:
                if section in text.lower():
                    found_sections.append(section)
            
            if found_sections:
                print(f"Sections found: {', '.join(found_sections)}")
            
            # Look for variety-related content
            variety_keywords = ['variety', 'varieties', 'cultivar', 'cultivars', 'improved', 'recommended']
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
            
            # Look for fertilizer-related content
            fertilizer_keywords = ['fertilizer', 'nitrogen', 'phosphorus', 'potassium', 'basal', 'top dressing', 'application', 'nutrient']
            fertilizer_lines = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in fertilizer_keywords):
                    fertilizer_lines.append(line.strip())
            
            if fertilizer_lines:
                print(f"\nFERTILIZER INFORMATION FOUND:")
                for line in fertilizer_lines[:10]:  # Show first 10
                    print(f"  {line}")
                if len(fertilizer_lines) > 10:
                    print(f"  ... and {len(fertilizer_lines) - 10} more lines")
            
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
    analyze_soybean_section()

if __name__ == "__main__":
    main()
