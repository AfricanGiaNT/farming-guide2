#!/usr/bin/env python3
import pdfplumber
import re

pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Malawi Groundnut Production Guide AUG2021.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    
    # Check pages around variety table (page 10)
    for page_num in range(8, 12):
        page = pdf.pages[page_num]
        text = page.extract_text() or ""
        
        print(f"\n{'='*80}")
        print(f"PAGE {page_num + 1}")
        print('='*80)
        print(text[:1500])
        
        # Look for tables
        tables = page.extract_tables()
        if tables:
            print(f"\nFound {len(tables)} tables on page {page_num + 1}")
            
            for table_idx, table in enumerate(tables):
                if table:
                    print(f"\nTable {table_idx + 1}:")
                    for row_idx, row in enumerate(table[:5]):  # Show first 5 rows
                        print(f"  Row {row_idx}: {row}")
