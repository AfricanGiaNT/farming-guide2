#!/usr/bin/env python3
"""
Sunflower Section Detailed Analysis
Examine sunflower section to find variety tables, fertilizer info, and section structure
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def analyze_sunflower_section():
    """Analyze sunflower section in detail"""
    
    print("=" * 80)
    print("DETAILED SUNFLOWER SECTION ANALYSIS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # First, let's find the sunflower section by searching for section 3.3.2
        sunflower_pages = []
        
        # Search through pages to find sunflower section
        for page_num in range(210, 280):  # Search pages 210-280
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Look for sunflower section markers
            if '3.3.2' in text and ('sunflower' in text.lower() or 'helianthus' in text.lower()):
                sunflower_pages.append(page_num + 1)
                print(f"Found sunflower section on page {page_num + 1}")
        
        print(f"\nSunflower section found on pages: {sunflower_pages}")
        
        # Analyze each sunflower page
        for page_num in sunflower_pages:
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
                '3.3.2.1',
                '3.3.2.4',
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
    analyze_sunflower_section()

if __name__ == "__main__":
    main()
