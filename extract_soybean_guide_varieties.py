#!/usr/bin/env python3
import pdfplumber
import re
from typing import List, Dict, Optional
import json

def extract_soybean_varieties_from_soybean_guide():
    """Extract soybean variety information from Guide to Soybean Production"""
    pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\GuidetoSoybeanProduction_finale2.pdf"
    varieties = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # Based on TOC, variety information should be around page 5
        for page_num in range(3, 7):  # Check pages 4-7
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            print(f"\n--- Page {page_num+1} ---")
            print(text[:500])
            
            # Extract tables from the page
            tables = page.extract_tables()
            if tables:
                print(f"Found {len(tables)} tables on page {page_num+1}")
                
                for table_idx, table in enumerate(tables):
                    if table:
                        print(f"\nTable {table_idx+1}:")
                        for row in table:
                            print(row)
    
    return varieties

def main():
    print("=" * 80)
    print("EXTRACTING SOYBEAN VARIETIES FROM GUIDE TO SOYBEAN PRODUCTION")
    print("=" * 80)
    
    varieties = extract_soybean_varieties_from_soybean_guide()
    
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
