#!/usr/bin/env python3
import pdfplumber
import re

pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\GuidetoSoybeanProduction_finale2.pdf"

with pdfplumber.open(pdf_path) as pdf:
    # Search for the varieties table
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        text = page.extract_text() or ""
        
        # Check if this page mentions varieties
        if "varieties" in text.lower() or "variety" in text.lower():
            print(f"\n=== Page {page_num+1} (mentions varieties) ===")
            print(text[:500])
            
            # Extract tables
            tables = page.extract_tables()
            if tables:
                print(f"\nFound {len(tables)} tables on page {page_num+1}")
                
                for i, table in enumerate(tables):
                    if table:
                        print(f"\nTable {i+1}:")
                        for row in table:
                            print(row)
