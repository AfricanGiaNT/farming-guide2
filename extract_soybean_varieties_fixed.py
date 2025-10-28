#!/usr/bin/env python3
import pdfplumber
import re
from typing import List, Dict, Optional
import json

def extract_soybean_varieties_from_agriculture_guide():
    """Extract soybean variety information from Guide to Agriculture Production in Malawi"""
    pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"
    varieties = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # Soybean section starts around page 195 based on initial search
        # Variety table is on page 197
        page = pdf.pages[196]  # Page 197 (0-indexed)
        tables = page.extract_tables()
        
        if tables and len(tables) > 0:
            variety_table = tables[0]
            
            # Extract header row
            header_row = variety_table[0]
            print("Header row:", header_row)
            
            # Process variety rows
            for row in variety_table[1:]:  # Skip header
                if row and len(row) >= 5:
                    variety_name = row[0].strip() if row[0] else ""
                    source = row[1].strip() if row[1] else ""
                    maturity_period = row[2].strip() if row[2] else ""
                    agro_ecology = row[3].strip() if row[3] else ""
                    attributes = row[4].strip() if row[4] else ""
                    
                    # Extract maturity days
                    maturity_days = None
                    maturity_match = re.search(r'(\d+)-(\d+)\s*days', maturity_period, re.IGNORECASE)
                    if maturity_match:
                        min_days = int(maturity_match.group(1))
                        max_days = int(maturity_match.group(2))
                        maturity_days = (min_days + max_days) // 2
                    
                    # Extract yield potential
                    yield_potential = None
                    yield_match = re.search(r'yields up to (\d+)kg/ha', attributes, re.IGNORECASE)
                    if yield_match:
                        yield_kg = yield_match.group(1)
                        yield_potential = f"{yield_kg} kg/ha"
                    
                    # Extract disease resistance
                    disease_resistance = []
                    if "resistant to" in attributes.lower():
                        resistance_match = re.search(r'resistant to ([^,\.]+)', attributes, re.IGNORECASE)
                        if resistance_match:
                            disease_resistance.append(resistance_match.group(1).strip())
                    
                    if "tolerant to" in attributes.lower():
                        tolerance_matches = re.findall(r'tolerant to ([^,\.]+)', attributes, re.IGNORECASE)
                        for match in tolerance_matches:
                            disease_resistance.append(f"{match.strip()} (tolerant)")
                    
                    # Create variety entry
                    if variety_name:
                        variety = {
                            'variety_name': variety_name,
                            'source': source,
                            'maturity_period': maturity_period,
                            'maturity_days': maturity_days,
                            'agro_ecology': agro_ecology,
                            'yield_potential': yield_potential,
                            'disease_resistance': disease_resistance,
                            'attributes': attributes
                        }
                        varieties.append(variety)
    
    return varieties

def main():
    print("=" * 80)
    print("EXTRACTING SOYBEAN VARIETIES")
    print("=" * 80)
    
    # Extract from Guide to Agriculture Production
    print("\nExtracting from Guide to Agriculture Production")
    varieties = extract_soybean_varieties_from_agriculture_guide()
    
    print("\n" + "="*80)
    print(f"FOUND {len(varieties)} SOYBEAN VARIETIES")
    print("="*80)
    
    # Print variety information
    for i, variety in enumerate(varieties):
        print(f"\n{i+1}. {variety.get('variety_name', 'Unknown')}")
        for key, value in variety.items():
            if key != 'variety_name':
                print(f"   {key}: {value}")

if __name__ == "__main__":
    main()
