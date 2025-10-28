#!/usr/bin/env python3
import pdfplumber
import re

pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\GuidetoSoybeanProduction_finale2.pdf"

with pdfplumber.open(pdf_path) as pdf:
    # Check page 5 where the varieties table should be
    page = pdf.pages[4]  # 0-indexed, so page 5 is index 4
    
    print(f"=== Page 5 Content ===")
    print(page.extract_text())
    
    # Extract tables
    tables = page.extract_tables()
    print(f"\nFound {len(tables)} tables on page 5")
    
    for i, table in enumerate(tables):
        print(f"\nTable {i+1}:")
        for row in table:
            print(row)
    
    # Check page 4 for variety information
    print("\n\n=== Page 4 Content ===")
    page = pdf.pages[3]
    print(page.extract_text())
    
    # Extract tables
    tables = page.extract_tables()
    print(f"\nFound {len(tables)} tables on page 4")
    
    for i, table in enumerate(tables):
        print(f"\nTable {i+1}:")
        for row in table:
            print(row)
