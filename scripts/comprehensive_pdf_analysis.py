#!/usr/bin/env python3
"""
Comprehensive PDF Analysis - Find ALL variety tables for ALL crops
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def find_all_crop_sections():
    """Find all crop sections and their variety tables"""
    
    with pdfplumber.open(PDF_PATH) as pdf:
        print("=" * 80)
        print("COMPREHENSIVE CROP SECTION ANALYSIS")
        print("Finding ALL crops and their variety tables")
        print("=" * 80)
        
        crop_sections = {}
        variety_pages = {}
        
        # Scan all pages for crop sections
        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            text = page.extract_text() or ""
            text_lower = text.lower()
            
            # Look for section headers (3.x.x format)
            section_matches = re.findall(r'3\.\d+\.\d+[^.]*', text)
            for match in section_matches:
                if len(match) < 100:  # Reasonable section header length
                    print(f"Page {page_num}: {match.strip()}")
                    
                    # Extract crop name from section header
                    crop_name = extract_crop_name(match)
                    if crop_name:
                        if crop_name not in crop_sections:
                            crop_sections[crop_name] = []
                        crop_sections[crop_name].append(page_num)
        
        print(f"\nFound {len(crop_sections)} crop sections")
        
        # Now find variety tables for each crop
        print("\n" + "=" * 80)
        print("FINDING VARIETY TABLES FOR EACH CROP")
        print("=" * 80)
        
        for crop_name, pages in crop_sections.items():
            print(f"\n{crop_name.upper()}:")
            variety_pages[crop_name] = []
            
            for page_num in pages:
                # Check if this page has variety tables
                page = pdf.pages[page_num - 1]
                text = page.extract_text() or ""
                tables = page.extract_tables()
                
                # Look for variety indicators
                variety_indicators = [
                    "variety", "varieties", "cultivar", "cultivars",
                    "recommended varieties", "released varieties",
                    "improved varieties", "available varieties"
                ]
                
                has_variety_mention = any(ind in text.lower() for ind in variety_indicators)
                has_tables = len(tables) > 0
                
                if has_variety_mention and has_tables:
                    variety_pages[crop_name].append(page_num)
                    print(f"  Page {page_num}: Found variety tables ({len(tables)} tables)")
                    
                    # Show table preview
                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 0:
                            print(f"    Table {table_idx + 1}: {len(table)} rows")
                            # Show first row (header)
                            if len(table) > 0:
                                print(f"      Header: {table[0]}")
        
        return crop_sections, variety_pages

def extract_crop_name(section_text):
    """Extract crop name from section header"""
    # Common crop names to look for
    crops = [
        "maize", "rice", "sorghum", "wheat", "millet", "pearl millet", "finger millet",
        "bean", "beans", "phaseolus", "cowpea", "groundnut", "soybean", "soyabean",
        "pigeonpea", "bambara", "chickpea", "field pea", "grams", "guar",
        "sunflower", "sesame", "castor",
        "cassava", "sweet potato", "potato",
        "tobacco", "cotton",
        "citrus", "banana", "pineapple", "mango", "avocado", "pawpaw", "guava",
        "apple", "pear", "plum", "peach",
        "cashew", "macadamia", "coconut",
        "chilli", "turmeric", "ginger", "cardamom", "pepper", "coriander", "paprika", "cinnamon",
        "cabbage", "tomato", "onion", "garlic", "lettuce", "okra", "carrot", "eggplant", "cucumber",
        "mushroom"
    ]
    
    text_lower = section_text.lower()
    for crop in crops:
        if crop in text_lower:
            return crop
    
    return None

def analyze_specific_tables():
    """Analyze specific variety tables in detail"""
    
    # Known variety table locations from previous analysis
    known_tables = {
        "maize": [156, 167],
        "rice": [170],
        "groundnut": [192],
        "cassava": [220],
        "potato": [227],
        "tomato": [322],
    }
    
    print("\n" + "=" * 80)
    print("DETAILED TABLE ANALYSIS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        for crop, pages in known_tables.items():
            print(f"\n{crop.upper()}:")
            
            for page_num in pages:
                if page_num - 1 >= len(pdf.pages):
                    continue
                
                page = pdf.pages[page_num - 1]
                tables = page.extract_tables()
                
                print(f"  Page {page_num}: {len(tables)} tables")
                
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    print(f"    Table {table_idx + 1}: {len(table)} rows x {len(table[0])} columns")
                    
                    # Show all rows
                    for row_idx, row in enumerate(table):
                        if row_idx < 5:  # Show first 5 rows
                            print(f"      Row {row_idx}: {row}")
                        elif row_idx == 5:
                            print(f"      ... ({len(table) - 5} more rows)")

def main():
    print("\nCOMPREHENSIVE PDF ANALYSIS")
    print("Finding ALL crops and variety tables in Chapter 3\n")
    
    # Find all crop sections
    crop_sections, variety_pages = find_all_crop_sections()
    
    # Analyze specific tables
    analyze_specific_tables()
    
    # Summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal crops found: {len(crop_sections)}")
    print(f"Crops with variety tables: {len([c for c, p in variety_pages.items() if p])}")
    
    print("\nCrops with variety tables:")
    for crop, pages in variety_pages.items():
        if pages:
            print(f"  {crop}: Pages {pages}")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()


