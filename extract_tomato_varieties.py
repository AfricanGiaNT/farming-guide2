#!/usr/bin/env python3
import pdfplumber
import re
from typing import List, Dict, Optional
import json

def find_tomato_section_in_guide():
    """Find tomato section in Guide to Agriculture Production in Malawi"""
    pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"
    tomato_pages = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # Search for tomato section
        for i in range(len(pdf.pages)):
            text = pdf.pages[i].extract_text() or ""
            if "tomato" in text.lower():
                tomato_pages.append(i)
        
        print(f"Found tomato mentions on {len(tomato_pages)} pages")
        print(f"First 10 pages with tomato mentions: {[p+1 for p in tomato_pages[:10]]}")
        
        # Check specific pages with tomato content
        for page_num in tomato_pages:
            text = pdf.pages[page_num].extract_text() or ""
            if "3.7" in text and "tomato" in text.lower():
                print(f"\nFound tomato section on page {page_num+1}")
                print(text[:500])

def extract_tomato_varieties_from_guide():
    """Extract tomato variety information from Guide to Agriculture Production in Malawi"""
    pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"
    varieties = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # Based on TOC, tomato section should be around page 320-330
        for page_num in range(310, 340):
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check if this page contains tomato variety information
            if "tomato" in text.lower() and ("variety" in text.lower() or "varieties" in text.lower()):
                print(f"\n--- Tomato Variety Info (Page {page_num+1}) ---")
                print(text[:800])
                
                # Look for variety names and descriptions
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    # Look for variety name patterns
                    if re.match(r'^[A-Z0-9]', line) and len(line.strip()) < 50 and i+1 < len(lines):
                        variety_name = line.strip()
                        description = lines[i+1].strip()
                        
                        print(f"\nPossible variety: {variety_name}")
                        print(f"Description: {description}")
                        
                        # Extract variety information
                        maturity_days = None
                        maturity_match = re.search(r'matures? in (\d+)\s*(?:to|-)\s*(\d+) days', description, re.IGNORECASE)
                        if maturity_match:
                            min_days = int(maturity_match.group(1))
                            max_days = int(maturity_match.group(2))
                            maturity_days = (min_days + max_days) // 2
                        
                        yield_potential = None
                        yield_match = re.search(r'yield potential of ([\d,]+)\s*kg', description, re.IGNORECASE)
                        if yield_match:
                            yield_kg = yield_match.group(1).replace(',', '')
                            yield_potential = f"{yield_kg} kg/ha"
                        
                        if variety_name and (maturity_days or yield_potential or len(description) > 20):
                            varieties.append({
                                'variety_name': variety_name,
                                'description': description,
                                'maturity_days': maturity_days,
                                'yield_potential': yield_potential
                            })
            
            # Extract tables from the page
            tables = page.extract_tables()
            if tables:
                print(f"\nFound {len(tables)} tables on page {page_num+1}")
                
                for table_idx, table in enumerate(tables):
                    if table and len(table) > 1:
                        # Check if this looks like a varieties table
                        if any("variety" in str(cell).lower() for row in table for cell in row if cell):
                            print(f"\nFound variety table on page {page_num+1}, Table {table_idx+1}")
                            for row in table:
                                print(row)
    
    return varieties

def extract_tomato_varieties_from_field_guide():
    """Extract tomato variety information from Field-Tomato farming PDF"""
    pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Field-Tomato farming.pdf"
    varieties = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # Search for variety information
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check if this page contains variety information
            if "variety" in text.lower() or "varieties" in text.lower():
                print(f"\n--- Field Guide Variety Info (Page {page_num+1}) ---")
                print(text[:800])
                
                # Look for variety names
                variety_match = re.search(r'varieties.*?(?:include|available).*?((?:[A-Z][a-zA-Z0-9\s]+(?:,|\sand\s|\.|\n|$))+)', text, re.IGNORECASE | re.DOTALL)
                if variety_match:
                    variety_text = variety_match.group(1)
                    print(f"\nVariety list: {variety_text}")
                    
                    # Extract individual varieties
                    variety_names = re.findall(r'([A-Z][a-zA-Z0-9\s]+?)(?:,|\sand\s|\.|\n|$)', variety_text)
                    for name in variety_names:
                        name = name.strip()
                        if name and len(name) > 2:
                            varieties.append({
                                'variety_name': name,
                                'source': 'Field-Tomato farming.pdf'
                            })
                            print(f"Extracted variety: {name}")
                
                # Extract tables from the page
                tables = page.extract_tables()
                if tables:
                    print(f"\nFound {len(tables)} tables on page {page_num+1}")
                    
                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 1:
                            print(f"\nTable {table_idx+1}:")
                            for row in table:
                                print(row)
                                
                                # Check if row contains variety information
                                if row and len(row) > 1:
                                    first_cell = str(row[0]).strip() if row[0] else ""
                                    if first_cell and re.match(r'^[A-Z]', first_cell) and len(first_cell) < 30:
                                        varieties.append({
                                            'variety_name': first_cell,
                                            'description': str(row[1]).strip() if len(row) > 1 and row[1] else "",
                                            'source': 'Field-Tomato farming.pdf'
                                        })
                                        print(f"Extracted variety from table: {first_cell}")
    
    return varieties

def main():
    print("=" * 80)
    print("EXTRACTING TOMATO VARIETIES")
    print("=" * 80)
    
    # Find tomato section in Guide to Agriculture Production
    print("\n1. Finding tomato section in Guide to Agriculture Production")
    find_tomato_section_in_guide()
    
    # Extract from Guide to Agriculture Production
    print("\n2. Extracting from Guide to Agriculture Production")
    guide_varieties = extract_tomato_varieties_from_guide()
    
    # Extract from Field-Tomato farming
    print("\n3. Extracting from Field-Tomato farming")
    field_guide_varieties = extract_tomato_varieties_from_field_guide()
    
    # Combine results
    all_varieties = guide_varieties + field_guide_varieties
    
    print("\n" + "="*80)
    print(f"FOUND {len(all_varieties)} TOMATO VARIETIES")
    print("="*80)
    
    # Print variety information
    for i, variety in enumerate(all_varieties):
        print(f"\n{i+1}. {variety.get('variety_name', 'Unknown')}")
        for key, value in variety.items():
            if key != 'variety_name':
                print(f"   {key}: {value}")

if __name__ == "__main__":
    main()
