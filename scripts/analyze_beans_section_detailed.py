#!/usr/bin/env python3
"""
Beans Section Detailed Analysis
Examine beans section to find variety tables, fertilizer info, and yield data
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def analyze_beans_section():
    """Analyze beans section in detail"""
    
    print("=" * 80)
    print("DETAILED BEANS SECTION ANALYSIS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # First, let's find the beans section by searching for section 3.2.2
        beans_pages = []
        
        # Search through pages to find beans section
        for page_num in range(180, 300):  # Search pages 180-300
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Look for beans section markers
            if '3.2.2' in text and ('beans' in text.lower() or 'phaseolus' in text.lower()):
                beans_pages.append(page_num + 1)
                print(f"Found beans section on page {page_num + 1}")
        
        print(f"\nBeans section found on pages: {beans_pages}")
        
        # Analyze each beans page
        for page_num in beans_pages:
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
                '3.2.2.1',
                '3.2.2.5',
                'table 29a',
                'table 29',
                'varieties',
                'fertilizer',
                'yield'
            ]
            
            found_sections = []
            for section in sections:
                if section in text.lower():
                    found_sections.append(section)
            
            if found_sections:
                print(f"Sections found: {', '.join(found_sections)}")
            
            # Look for variety-related content
            variety_keywords = ['variety', 'varieties', 'cultivar', 'cultivars', 'improved', 'released']
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
            
            # Look for yield-related content
            yield_keywords = ['yield', 'kg/ha', 'tonnes', 'tons', 'production', 'potential']
            yield_lines = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in yield_keywords):
                    yield_lines.append(line.strip())
            
            if yield_lines:
                print(f"\nYIELD INFORMATION FOUND:")
                for line in yield_lines[:10]:  # Show first 10
                    print(f"  {line}")
                if len(yield_lines) > 10:
                    print(f"  ... and {len(yield_lines) - 10} more lines")
            
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
                    if header_row and any(word in str(header_row).lower() for word in ["variety", "cultivar", "yield"]):
                        print(f"  *** VARIETY/YIELD TABLE FOUND ***")
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
    analyze_beans_section()

if __name__ == "__main__":
    main()
