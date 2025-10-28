#!/usr/bin/env python3
import pdfplumber
import re
import os

def examine_pdf(pdf_path, search_term="soybean", max_pages=5):
    """Examine a PDF document for soybean information"""
    print(f"\n{'='*80}")
    print(f"Examining: {os.path.basename(pdf_path)}")
    print('='*80)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total pages: {len(pdf.pages)}")
            
            # Look for table of contents
            toc_found = False
            for i in range(min(20, len(pdf.pages))):
                text = pdf.pages[i].extract_text() or ""
                if "table of contents" in text.lower() or "contents" in text.lower():
                    print(f"\n--- Table of Contents (Page {i+1}) ---")
                    print(text[:1500])
                    toc_found = True
                    break
            
            if not toc_found:
                print("\nNo table of contents found in first 20 pages.")
            
            # Look for soybean section
            soybean_pages = []
            for i in range(len(pdf.pages)):
                text = pdf.pages[i].extract_text() or ""
                if search_term.lower() in text.lower():
                    soybean_pages.append(i)
            
            if soybean_pages:
                print(f"\n--- Found {search_term} information on {len(soybean_pages)} pages: {[p+1 for p in soybean_pages[:10]]} ---")
                
                # Show first few pages with soybean info
                for page_num in soybean_pages[:3]:  # First 3 soybean pages
                    text = pdf.pages[page_num].extract_text() or ""
                    print(f"\n--- {search_term.title()} Info (Page {page_num+1}) ---")
                    print(text[:800])
                    
                    # Look for tables
                    tables = pdf.pages[page_num].extract_tables()
                    if tables:
                        print(f"\nFound {len(tables)} tables on page {page_num+1}")
                        for t_idx, table in enumerate(tables):
                            if table:
                                print(f"\nTable {t_idx+1}:")
                                for row_idx, row in enumerate(table[:5]):  # First 5 rows
                                    print(f"  Row {row_idx}: {row}")
            else:
                print(f"\nNo {search_term} information found.")
                
            # Look for variety information
            variety_pages = []
            for i in range(len(pdf.pages)):
                text = pdf.pages[i].extract_text() or ""
                if search_term.lower() in text.lower() and ("variety" in text.lower() or "varieties" in text.lower()):
                    variety_pages.append(i)
            
            if variety_pages:
                print(f"\n--- Found {search_term} variety information on pages: {[p+1 for p in variety_pages[:5]]} ---")
                for page_num in variety_pages[:2]:  # First 2 variety pages
                    text = pdf.pages[page_num].extract_text() or ""
                    print(f"\n--- {search_term.title()} Variety Info (Page {page_num+1}) ---")
                    print(text[:800])
                    
                    # Look for tables
                    tables = pdf.pages[page_num].extract_tables()
                    if tables:
                        print(f"\nFound {len(tables)} tables on page {page_num+1}")
                        for t_idx, table in enumerate(tables):
                            if table:
                                print(f"\nTable {t_idx+1}:")
                                for row_idx, row in enumerate(table[:5]):  # First 5 rows
                                    print(f"  Row {row_idx}: {row}")
    
    except Exception as e:
        print(f"Error examining PDF: {e}")

# Documents to examine
docs = [
    r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf",
    r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\soybeans farming in malawi.pdf",
    r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\GUIDE TO SOYBEAN PRODUCTION (1)_0.pdf",
    r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\GuidetoSoybeanProduction_finale2.pdf"
]

# Examine each document
for doc in docs:
    examine_pdf(doc, "soybean")
