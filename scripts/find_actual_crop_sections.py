#!/usr/bin/env python3
"""
Find actual crop sections in the PDF
"""

import pdfplumber

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def find_crop_sections():
    """Find where crop sections actually start"""
    
    with pdfplumber.open(PDF_PATH) as pdf:
        print("Finding actual crop section starts...\n")
        
        # Look for section headers
        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            text = page.extract_text() or ""
            
            # Look for section headers (usually start with 3.x.x)
            if re.search(r'3\.\d+\.\d+', text):
                lines = text.split('\n')
                for line in lines[:10]:  # Check first 10 lines
                    if re.search(r'3\.\d+\.\d+', line) and len(line) < 200:
                        print(f"Page {page_num}: {line.strip()}")

def examine_crop_pages():
    """Examine pages where crops are mentioned"""
    
    crop_pages = {
        "maize": [156, 167],  # Found in scan
        "rice": [168, 170],   # Found in scan  
        "beans": [184, 186], # Found in scan
        "groundnut": [189, 192], # Found in scan
        "cassava": [219, 220], # Found in scan
        "potato": [226, 227], # Found in scan
        "tomato": [322, 323], # Found in scan
    }
    
    with pdfplumber.open(PDF_PATH) as pdf:
        for crop, pages in crop_pages.items():
            print(f"\n{'='*60}")
            print(f"{crop.upper()} SECTION")
            print(f"{'='*60}")
            
            for page_num in pages:
                if page_num - 1 >= len(pdf.pages):
                    continue
                
                page = pdf.pages[page_num - 1]
                text = page.extract_text() or ""
                tables = page.extract_tables()
                
                print(f"\nPage {page_num}:")
                print(f"Tables: {len(tables)}")
                
                # Show text around variety mentions
                variety_keywords = ["variety", "varieties", "cultivar", "recommended"]
                for keyword in variety_keywords:
                    if keyword in text.lower():
                        # Find context around keyword
                        lines = text.split('\n')
                        for i, line in enumerate(lines):
                            if keyword in line.lower():
                                start = max(0, i-2)
                                end = min(len(lines), i+3)
                                context = '\n'.join(lines[start:end])
                                print(f"\nFound '{keyword}' context:")
                                print(context)
                                break
                
                # Show table preview
                if tables:
                    for i, table in enumerate(tables):
                        print(f"\nTable {i+1}:")
                        if table and len(table) > 0:
                            for row in table[:3]:
                                print(f"  {row}")

if __name__ == "__main__":
    import re
    
    find_crop_sections()
    examine_crop_pages()


