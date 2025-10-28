#!/usr/bin/env python3
"""
Examine specific pages from the PDF to understand structure
"""

import pdfplumber

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def examine_pages(page_nums):
    """Examine specific pages"""
    
    with pdfplumber.open(PDF_PATH) as pdf:
        print(f"Total pages in PDF: {len(pdf.pages)}\n")
        
        for page_num in page_nums:
            if page_num - 1 >= len(pdf.pages):
                print(f"Page {page_num} doesn't exist")
                continue
            
            page = pdf.pages[page_num - 1]
            text = page.extract_text() or ""
            tables = page.extract_tables()
            
            print("=" * 80)
            print(f"PAGE {page_num}")
            print("=" * 80)
            
            # Show first 500 characters
            print("\nText preview:")
            print(text[:500])
            print(f"\n... ({len(text)} total characters)")
            
            # Show table info
            print(f"\nTables found: {len(tables)}")
            if tables:
                for i, table in enumerate(tables):
                    print(f"\nTable {i+1}: {len(table)} rows x {len(table[0]) if table else 0} columns")
                    if table and len(table) > 0:
                        print("First few rows:")
                        for row in table[:3]:
                            print(f"  {row}")
            
            print("\n")

def scan_for_crop_sections():
    """Scan to find where crop sections actually start"""
    print("Scanning for crop section headers...\n")
    
    crops = ["maize", "rice", "beans", "groundnut", "soybean", "cassava", "potato", "tomato"]
    
    with pdfplumber.open(PDF_PATH) as pdf:
        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            text = (page.extract_text() or "").lower()
            
            for crop in crops:
                # Look for crop as section header
                if crop in text:
                    lines = text.split('\n')[:10]
                    for line in lines:
                        if crop in line and len(line) < 100:
                            print(f"Page {page_num}: {crop.upper()} - '{line.strip()}'")
                            break

def main():
    print("\nEXAMINING PDF STRUCTURE\n")
    
    # First, scan to find crop sections
    scan_for_crop_sections()
    
    print("\n" + "=" * 80)
    print("\nNow examining specific pages (30-35 for maize):")
    print("=" * 80 + "\n")
    
    # Examine maize pages
    examine_pages([30, 31, 32, 33, 34, 35])

if __name__ == "__main__":
    main()





