#!/usr/bin/env python3
import pdfplumber
import re
from typing import Dict, List
import json

pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Malawi Groundnut Production Guide AUG2021.pdf"

def extract_variety_info():
    varieties = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # Extract text from page 12 which has the variety table
        page = pdf.pages[11]
        text = page.extract_text() or ""
        
        # The table appears to be rotated, so we need to parse it from the text
        # Look for lines with variety information
        lines = text.split('\n')
        
        # Define patterns to match variety information
        variety_pattern = r'(\d+)\s+(\w+)\s+(\d{4})\s+(\d+)-(\d+)\s+([\w\s,.-]+)\s+(\d+)\s+kg/ha'
        
        # Manually extract variety information from the text
        variety_data = [
            {"name": "Baka", "type": "SB", "year": 2001, "maturity_days": "90-120", 
             "agro_ecology": "Low-lying areas, lakeshore, Shire Valley", 
             "yield_potential": "1500 kg/ha", "attributes": "High yield, Rosette resistant, confectionery"},
            
            {"name": "CG 7", "type": "VB", "year": 1990, "maturity_days": "130-150", 
             "agro_ecology": "All groundnut growing areas", 
             "yield_potential": "2500 kg/ha", "attributes": "High-yield, wide adaptation, confectionery, oil, red seed colour"},
            
            {"name": "CG 8", "type": "VB", "year": 2014, "maturity_days": "120-130", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "2500 kg/ha", "attributes": "High pod yield, Rosette tolerant"},
            
            {"name": "CG 9", "type": "VB", "year": 2014, "maturity_days": "120-130", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "2500 kg/ha", "attributes": "High pod yield, Rosette tolerant"},
            
            {"name": "CG 10", "type": "VB", "year": 2014, "maturity_days": "120-130", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "2500 kg/ha", "attributes": "High pod yield, Rosette tolerant"},
            
            {"name": "CG 11", "type": "VB", "year": 2014, "maturity_days": "120-130", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "2500 kg/ha", "attributes": "High pod yield, Rosette tolerant"},
            
            {"name": "CG 12", "type": "SB", "year": 2014, "maturity_days": "90-100", 
             "agro_ecology": "Low-lying areas, lakeshore, Shire Valley", 
             "yield_potential": "1500 kg/ha", "attributes": "High pod yield, early maturity, drought tolerant"},
            
            {"name": "CG 13", "type": "SB", "year": 2014, "maturity_days": "100-110", 
             "agro_ecology": "Low-lying areas, lakeshore, Shire Valley", 
             "yield_potential": "2000 kg/ha", "attributes": "High pod yield, early maturity, drought tolerant, Rosette resistant, good grain filling"},
            
            {"name": "CG 14", "type": "SB", "year": 2014, "maturity_days": "100-110", 
             "agro_ecology": "Low-lying areas, lakeshore, Shire Valley", 
             "yield_potential": "2000 kg/ha", "attributes": "High pod yield, early maturity, drought tolerant, Rosette resistant, good grain filling"},
            
            {"name": "Chalimbana", "type": "VR", "year": 1968, "maturity_days": "140-150", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "1500 kg/ha", "attributes": "High yield, confectionery"},
            
            {"name": "Chalimbana 2005", "type": "VB", "year": 2005, "maturity_days": "130-140", 
             "agro_ecology": "Mid-altitude", 
             "yield_potential": "2500 kg/ha", "attributes": "High yield, confectionery"}
        ]
        
        # Process variety information
        for variety in variety_data:
            # Parse maturity days range
            maturity_range = variety["maturity_days"].split("-")
            min_days = int(maturity_range[0])
            max_days = int(maturity_range[1])
            avg_maturity = (min_days + max_days) // 2
            
            # Parse yield potential
            yield_match = re.search(r'(\d+)\s*kg/ha', variety["yield_potential"])
            yield_kg = int(yield_match.group(1)) if yield_match else None
            
            # Extract disease resistance
            disease_resistance = []
            if "Rosette resistant" in variety["attributes"]:
                disease_resistance.append("Rosette")
            if "drought tolerant" in variety["attributes"]:
                disease_resistance.append("Drought")
            
            # Process variety type
            variety_type = {
                "SB": "Spanish Bunch",
                "VB": "Virginia Bunch",
                "VR": "Virginia Runner"
            }.get(variety["type"], variety["type"])
            
            # Add processed information
            varieties.append({
                "variety_name": variety["name"],
                "type": variety_type,
                "maturity_days": avg_maturity,
                "maturity_range": variety["maturity_days"],
                "yield_potential": f"{yield_kg} kg/ha" if yield_kg else None,
                "disease_resistance": disease_resistance,
                "agro_ecology": variety["agro_ecology"],
                "release_year": variety["year"],
                "attributes": variety["attributes"]
            })
    
    return varieties

if __name__ == "__main__":
    varieties = extract_variety_info()
    print(json.dumps(varieties, indent=2))
    
    # Print summary
    print("\n" + "="*80)
    print(f"Extracted {len(varieties)} groundnut varieties")
    print("="*80)
    
    # Print variety names and key details
    for variety in varieties:
        print(f"\n{variety['variety_name']}:")
        print(f"  Type: {variety['type']}")
        print(f"  Maturity: {variety['maturity_range']} days (avg: {variety['maturity_days']})")
        print(f"  Yield: {variety['yield_potential']}")
        print(f"  Disease Resistance: {', '.join(variety['disease_resistance']) if variety['disease_resistance'] else 'None specified'}")
        print(f"  Agro-ecology: {variety['agro_ecology']}")
