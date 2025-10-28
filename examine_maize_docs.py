#!/usr/bin/env python3
import pdfplumber
import os

def examine_pdf(pdf_path, max_pages=5):
    """Examine a PDF document and print its first few pages"""
    print(f"\n{'='*80}")
    print(f"Examining: {os.path.basename(pdf_path)}")
    print('='*80)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total pages: {len(pdf.pages)}")
            
            # Look for table of contents
            toc_found = False
            for i in range(min(10, len(pdf.pages))):
                text = pdf.pages[i].extract_text() or ""
                if "table of contents" in text.lower() or "contents" in text.lower():
                    print(f"\n--- Table of Contents (Page {i+1}) ---")
                    print(text[:1500])
                    toc_found = True
                    break
            
            if not toc_found:
                print("\nNo table of contents found in first 10 pages.")
            
            # Print first few pages
            for i in range(min(max_pages, len(pdf.pages))):
                text = pdf.pages[i].extract_text() or ""
                print(f"\n--- Page {i+1} ---")
                print(text[:500])
                
            # Look for variety information
            variety_pages = []
            for i in range(len(pdf.pages)):
                text = pdf.pages[i].extract_text() or ""
                if "variety" in text.lower() and ("table" in text.lower() or "characteristics" in text.lower()):
                    variety_pages.append(i)
                    
            if variety_pages:
                print(f"\n--- Found potential variety information on pages: {[p+1 for p in variety_pages]} ---")
                for page_num in variety_pages[:2]:  # Show first 2 variety pages
                    text = pdf.pages[page_num].extract_text() or ""
                    print(f"\n--- Variety Info (Page {page_num+1}) ---")
                    print(text[:1000])
                    
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
    r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Malawi-Maize-Growers-Guide_1.pdf",
    r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Malawi-Maize-disease-brochure.pdf"
]

# Examine each document
for doc in docs:
    examine_pdf(doc)
