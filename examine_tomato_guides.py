#!/usr/bin/env python3
import pdfplumber
import re
import os

def examine_pdf(pdf_path, search_term="tomato", max_pages=5):
    """Examine a PDF document for tomato information"""
    print(f"\n{'='*80}")
    print(f"Examining: {os.path.basename(pdf_path)}")
    print('='*80)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total pages: {len(pdf.pages)}")
            
            # Look for tomato section in Guide to Agriculture
            if "Guide to Agriculture Production" in pdf_path:
                # Search for Chapter 3 and tomato section
                chapter3_pages = []
                tomato_pages = []
                
                for i in range(len(pdf.pages)):
                    text = pdf.pages[i].extract_text() or ""
                    if "Chapter 3" in text and "Crop Production" in text:
                        chapter3_pages.append(i)
                    if search_term.lower() in text.lower():
                        tomato_pages.append(i)
                
                print(f"\nChapter 3 found on pages: {[p+1 for p in chapter3_pages]}")
                print(f"Tomato information found on {len(tomato_pages)} pages: {[p+1 for p in tomato_pages[:10]]}")
                
                # Show first few tomato pages
                for page_num in tomato_pages[:3]:
                    text = pdf.pages[page_num].extract_text() or ""
                    print(f"\n--- Tomato Info (Page {page_num+1}) ---")
                    print(text[:800])
                    
                    # Look for tables
                    tables = pdf.pages[page_num].extract_tables()
                    if tables:
                        print(f"\nFound {len(tables)} tables on page {page_num+1}")
                        for t_idx, table in enumerate(tables):
                            if table:
                                print(f"\nTable {t_idx+1}:")
                                for row_idx, row in enumerate(table[:5]):
                                    print(f"  Row {row_idx}: {row}")
            
            # For Field-Tomato farming PDF
            else:
                # Look for variety information
                variety_pages = []
                for i in range(len(pdf.pages)):
                    text = pdf.pages[i].extract_text() or ""
                    if "variety" in text.lower() or "varieties" in text.lower():
                        variety_pages.append(i)
                
                print(f"\nVariety information found on {len(variety_pages)} pages: {[p+1 for p in variety_pages[:10]]}")
                
                # Show first few variety pages
                for page_num in variety_pages[:3]:
                    text = pdf.pages[page_num].extract_text() or ""
                    print(f"\n--- Variety Info (Page {page_num+1}) ---")
                    print(text[:800])
                    
                    # Look for tables
                    tables = pdf.pages[page_num].extract_tables()
                    if tables:
                        print(f"\nFound {len(tables)} tables on page {page_num+1}")
                        for t_idx, table in enumerate(tables):
                            if table:
                                print(f"\nTable {t_idx+1}:")
                                for row_idx, row in enumerate(table[:5]):
                                    print(f"  Row {row_idx}: {row}")
    
    except Exception as e:
        print(f"Error examining PDF: {e}")

# Documents to examine
docs = [
    r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf",
    r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Field-Tomato farming.pdf"
]

# Examine each document
for doc in docs:
    examine_pdf(doc, "tomato")
