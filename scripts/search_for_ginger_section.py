#!/usr/bin/env python3
"""
Search for Ginger Section
Broad search to locate ginger section in the PDF
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def search_for_ginger_section():
    """Search for ginger section across the entire PDF"""
    
    print("=" * 80)
    print("SEARCHING FOR GINGER SECTION")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        ginger_pages = []
        
        # Search through all pages
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Look for ginger-related content
            if ('ginger' in text.lower() or 'zingiber' in text.lower() or '3.9.3' in text):
                ginger_pages.append(page_num + 1)
                print(f"Found ginger-related content on page {page_num + 1}")
                
                # Show context around ginger mentions
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'ginger' in line.lower() or 'zingiber' in line.lower() or '3.9.3' in line:
                        print(f"  Context: {line.strip()}")
                        # Show a few lines before and after
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        for j in range(start, end):
                            if j != i:
                                print(f"    {j+1}: {lines[j].strip()}")
                        print()
        
        print(f"\nGinger-related content found on pages: {ginger_pages}")
        
        # Also search for section 3.9.3 specifically
        print(f"\nSearching for section 3.9.3...")
        section_3_9_3_pages = []
        
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            if '3.9.3' in text:
                section_3_9_3_pages.append(page_num + 1)
                print(f"Found section 3.9.3 on page {page_num + 1}")
                
                # Show the section content
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if '3.9.3' in line:
                        print(f"  Section: {line.strip()}")
                        # Show a few lines after
                        for j in range(i+1, min(len(lines), i+5)):
                            if lines[j].strip():
                                print(f"    {j+1}: {lines[j].strip()}")
                        print()
        
        print(f"\nSection 3.9.3 found on pages: {section_3_9_3_pages}")

def main():
    search_for_ginger_section()

if __name__ == "__main__":
    main()
