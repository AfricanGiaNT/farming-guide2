#!/usr/bin/env python3
import pdfplumber
import re
from typing import List, Dict, Optional
import json

def extract_soybean_varieties_from_guide():
    """Extract soybean variety information from Guide to Soybean Production"""
    pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\GuidetoSoybeanProduction_finale2.pdf"
    varieties = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # Look for the varieties table - should be around page 5 based on TOC
        for page_num in range(4, 10):  # Check pages 5-10
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check if this page contains the varieties table
            if "List of recommended Soybean varieties" in text:
                print(f"Found varieties table mention on page {page_num+1}")
                print(text[:500])
            
            # Extract tables from the page
            tables = page.extract_tables()
            if tables:
                print(f"Found {len(tables)} tables on page {page_num+1}")
                
                for table_idx, table in enumerate(tables):
                    if table and len(table) > 1:  # Table with at least 2 rows
                        header_row = table[0]
                        
                        # Check if this looks like a varieties table
                        if any("variety" in str(cell).lower() for cell in header_row if cell):
                            print(f"Found variety table on page {page_num+1}, Table {table_idx+1}")
                            print("Header row:", header_row)
                            
                            # Process variety rows
                            for row in table[1:]:  # Skip header
                                if row and any(cell for cell in row):
                                    print("Variety row:", row)
                                    
                                    # Extract variety information
                                    variety_info = {}
                                    for i, cell in enumerate(row):
                                        if cell and i < len(header_row) and header_row[i]:
                                            field = str(header_row[i]).strip().lower()
                                            value = str(cell).strip()
                                            if field and value:
                                                variety_info[field] = value
                                    
                                    if variety_info:
                                        varieties.append(variety_info)
    
    return varieties

def extract_soybean_varieties_from_agriculture_guide():
    """Extract soybean variety information from Guide to Agriculture Production in Malawi"""
    pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"
    varieties = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # Soybean section should be around page 195 based on initial search
        for page_num in range(194, 210):  # Check pages 195-210
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check if this page contains soybean variety information
            if "soybean" in text.lower() and "variet" in text.lower():
                print(f"Found soybean variety information on page {page_num+1}")
                print(text[:500])
                
                # Look for variety names and descriptions
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    # Look for variety name patterns
                    if re.match(r'^[A-Z0-9]', line) and len(line.strip()) < 50:
                        variety_name = line.strip()
                        description = ""
                        
                        # Check if the next line is the description
                        if i+1 < len(lines):
                            description = lines[i+1].strip()
                        
                        print(f"Possible variety: {variety_name}")
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
                        
                        if variety_name and (maturity_days or yield_potential):
                            varieties.append({
                                'variety_name': variety_name,
                                'description': description,
                                'maturity_days': maturity_days,
                                'yield_potential': yield_potential
                            })
            
            # Extract tables from the page
            tables = page.extract_tables()
            if tables:
                print(f"Found {len(tables)} tables on page {page_num+1}")
                
                for table_idx, table in enumerate(tables):
                    if table and len(table) > 1:  # Table with at least 2 rows
                        # Check if this looks like a varieties table
                        if any("variety" in str(cell).lower() for row in table for cell in row if cell):
                            print(f"Found variety table on page {page_num+1}, Table {table_idx+1}")
                            for row in table:
                                print(row)
    
    return varieties

def main():
    print("=" * 80)
    print("EXTRACTING SOYBEAN VARIETIES")
    print("=" * 80)
    
    # Extract from Guide to Soybean Production
    print("\n1. Extracting from Guide to Soybean Production")
    soybean_guide_varieties = extract_soybean_varieties_from_guide()
    
    # Extract from Guide to Agriculture Production
    print("\n2. Extracting from Guide to Agriculture Production")
    agriculture_guide_varieties = extract_soybean_varieties_from_agriculture_guide()
    
    # Combine results
    all_varieties = soybean_guide_varieties + agriculture_guide_varieties
    
    print("\n" + "="*80)
    print(f"FOUND {len(all_varieties)} SOYBEAN VARIETIES")
    print("="*80)
    
    # Print variety information
    for i, variety in enumerate(all_varieties):
        print(f"\n{i+1}. {variety.get('variety_name', 'Unknown')}")
        for key, value in variety.items():
            if key != 'variety_name':
                print(f"   {key}: {value}")

if __name__ == "__main__":
    main()
