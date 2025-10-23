#!/usr/bin/env python3
"""
Groundnut Section Detailed Analysis
Examine groundnut section to find variety tables, fertilizer info, pest control, and disease control
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def analyze_groundnut_section():
    """Analyze groundnut section in detail"""
    
    print("=" * 80)
    print("DETAILED GROUNDNUT SECTION ANALYSIS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # First, let's find the groundnut section by searching for section 3.2.3
        groundnut_pages = []
        
        # Search through pages to find groundnut section
        for page_num in range(180, 300):  # Search pages 180-300
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Look for groundnut section markers
            if '3.2.3' in text and ('groundnut' in text.lower() or 'arachis' in text.lower()):
                groundnut_pages.append(page_num + 1)
                print(f"Found groundnut section on page {page_num + 1}")
        
        print(f"\nGroundnut section found on pages: {groundnut_pages}")
        
        # Analyze each groundnut page
        for page_num in groundnut_pages:
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
                '3.2.3.1',
                '3.2.3.2',
                '3.2.3.6.2',
                '3.2.3.7',
                '3.2.3.8',
                'table 30',
                'varieties',
                'fertilizer',
                'pest',
                'disease'
            ]
            
            found_sections = []
            for section in sections:
                if section in text.lower():
                    found_sections.append(section)
            
            if found_sections:
                print(f"Sections found: {', '.join(found_sections)}")
            
            # Look for variety-related content
            variety_keywords = ['variety', 'varieties', 'cultivar', 'cultivars', 'improved', 'promoted', 'recommended']
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
            
            # Look for pest control content
            pest_keywords = ['pest', 'insect', 'control', 'spray', 'insecticide', 'aphid', 'thrips', 'beetle']
            pest_lines = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in pest_keywords):
                    pest_lines.append(line.strip())
            
            if pest_lines:
                print(f"\nPEST CONTROL INFORMATION FOUND:")
                for line in pest_lines[:10]:  # Show first 10
                    print(f"  {line}")
                if len(pest_lines) > 10:
                    print(f"  ... and {len(pest_lines) - 10} more lines")
            
            # Look for disease control content
            disease_keywords = ['disease', 'fungus', 'bacterial', 'viral', 'control', 'spray', 'fungicide', 'resistance']
            disease_lines = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in disease_keywords):
                    disease_lines.append(line.strip())
            
            if disease_lines:
                print(f"\nDISEASE CONTROL INFORMATION FOUND:")
                for line in disease_lines[:10]:  # Show first 10
                    print(f"  {line}")
                if len(disease_lines) > 10:
                    print(f"  ... and {len(disease_lines) - 10} more lines")
            
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
    analyze_groundnut_section()

if __name__ == "__main__":
    main()
