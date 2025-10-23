#!/usr/bin/env python3
"""
Analyze Chapter 3 Structure - Find Exact Variety Table Locations
Manually identify where variety tables actually appear for each crop
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def analyze_chapter3():
    """Analyze Chapter 3 to find variety table locations"""
    
    print("=" * 80)
    print("CHAPTER 3 STRUCTURE ANALYSIS")
    print("Guide to Agriculture Production in Malawi 2021")
    print("=" * 80)
    
    # Chapter 3 typical page range (needs verification)
    chapter3_start = 30
    chapter3_end = 320
    
    crop_keywords = [
        "maize", "rice", "sorghum", "wheat", "millet", "pearl millet", "finger millet",
        "bean", "beans", "phaseolus", "cowpea", "groundnut", "soybean", "soyabean",
        "cassava", "sweet potato", "potato", "tomato", "cotton", "tobacco",
        "cabbage", "onion", "sunflower", "bambara"
    ]
    
    variety_indicators = [
        "variety", "varieties", "cultivar", "cultivars",
        "recommended varieties", "available varieties",
        "released varieties", "certified varieties"
    ]
    
    print("\nScanning for crop sections and variety tables...\n")
    
    with pdfplumber.open(PDF_PATH) as pdf:
        current_crop = None
        crop_sections = {}
        
        for page_num in range(chapter3_start - 1, min(chapter3_end, len(pdf.pages))):
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            text_lower = text.lower()
            
            # Detect crop section headers
            for crop in crop_keywords:
                # Look for crop name in headers or section titles
                pattern = rf"\b{crop}\b"
                if re.search(pattern, text_lower):
                    # Check if it's a section header (usually larger font, start of page, or clear title)
                    lines = text.split('\n')[:5]  # Check first 5 lines
                    for line in lines:
                        if crop in line.lower() and len(line) < 50:
                            if current_crop != crop:
                                current_crop = crop
                                if crop not in crop_sections:
                                    crop_sections[crop] = {
                                        "start_page": page_num + 1,
                                        "variety_pages": [],
                                        "has_table": False
                                    }
            
            # Detect variety tables
            if current_crop:
                for indicator in variety_indicators:
                    if indicator in text_lower:
                        tables = page.extract_tables()
                        if tables:
                            crop_sections[current_crop]["variety_pages"].append(page_num + 1)
                            crop_sections[current_crop]["has_table"] = True
                            
                            # Show preview
                            print(f"📄 Page {page_num + 1} - {current_crop.upper()}")
                            print(f"   Found '{indicator}' with {len(tables)} table(s)")
                            
                            # Preview first table
                            if tables[0] and len(tables[0]) > 0:
                                print(f"   Table preview: {tables[0][0][:3]}")
                            print()
    
    # Summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    
    for crop, info in sorted(crop_sections.items()):
        print(f"\n{crop.upper()}:")
        print(f"  Start page: {info['start_page']}")
        print(f"  Variety table pages: {info['variety_pages']}")
        print(f"  Has tables: {info['has_table']}")
    
    return crop_sections

if __name__ == "__main__":
    analyze_chapter3()



