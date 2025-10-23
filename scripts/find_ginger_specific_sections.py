#!/usr/bin/env python3
"""
Find Ginger Specific Sections
Locate sections 3.9.3 and management sections
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def find_ginger_specific_sections():
    """Find specific ginger sections"""
    
    print("=" * 80)
    print("FINDING GINGER SPECIFIC SECTIONS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Search for specific sections on pages 306-307
        for page_num in range(305, 309):  # Search pages 306-308
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check for section 3.9.3.2 (improving yields)
            if '3.9.3.2' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.9.3.2 ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for field preparation
            if '3.9.3.2.2' in text and 'field preparation' in text.lower():
                print(f"\n{'='*60}")
                print(f"FOUND FIELD PREPARATION SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for planting
            if '3.9.3.2.3' in text and 'planting' in text.lower():
                print(f"\n{'='*60}")
                print(f"FOUND PLANTING SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for fertilizer application
            if '3.9.3.2.4' in text and 'fertilizer' in text.lower():
                print(f"\n{'='*60}")
                print(f"FOUND FERTILIZER APPLICATION SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for mulching
            if '3.9.3.2.5' in text and 'mulching' in text.lower():
                print(f"\n{'='*60}")
                print(f"FOUND MULCHING SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for pest control
            if '3.9.3.3' in text and 'pest' in text.lower():
                print(f"\n{'='*60}")
                print(f"FOUND PEST CONTROL SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for disease control
            if '3.9.3.3.3' in text and 'disease' in text.lower():
                print(f"\n{'='*60}")
                print(f"FOUND DISEASE CONTROL SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for harvesting
            if '3.9.3.3.5' in text and 'harvesting' in text.lower():
                print(f"\n{'='*60}")
                print(f"FOUND HARVESTING SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")

def main():
    find_ginger_specific_sections()

if __name__ == "__main__":
    main()
