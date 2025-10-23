#!/usr/bin/env python3
"""
Find Sunflower Specific Sections
Locate sections 3.3.2.1 and 3.3.2.4
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def find_sunflower_specific_sections():
    """Find specific sunflower sections"""
    
    print("=" * 80)
    print("FINDING SUNFLOWER SPECIFIC SECTIONS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Search for specific sections
        for page_num in range(210, 220):  # Search pages 210-220
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check for section 3.3.2.1 (improved yields)
            if '3.3.2.1' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.3.2.1 (IMPROVED YIELDS) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for section 3.3.2.4 (fertilizer application)
            if '3.3.2.4' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.3.2.4 (FERTILIZER APPLICATION) ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")

def main():
    find_sunflower_specific_sections()

if __name__ == "__main__":
    main()
