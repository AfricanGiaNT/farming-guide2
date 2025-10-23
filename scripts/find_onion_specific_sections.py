#!/usr/bin/env python3
"""
Find Onion Specific Sections
Locate sections 3.10.5.1 and management sections
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def find_onion_specific_sections():
    """Find specific onion sections"""
    
    print("=" * 80)
    print("FINDING ONION SPECIFIC SECTIONS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Search for specific sections
        for page_num in range(323, 330):  # Search pages 323-330
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check for section 3.10.5.1 (improving yields)
            if '3.10.5.1' in text:
                print(f"\n{'='*60}")
                print(f"FOUND SECTION 3.10.5.1 ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for recommended varieties
            if 'recommended varieties' in text.lower() and '3.10.5' in text:
                print(f"\n{'='*60}")
                print(f"FOUND RECOMMENDED VARIETIES SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for field preparation
            if 'field preparation' in text.lower() and '3.10.5' in text:
                print(f"\n{'='*60}")
                print(f"FOUND FIELD PREPARATION SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for transplanting
            if 'transplanting' in text.lower() and '3.10.5' in text:
                print(f"\n{'='*60}")
                print(f"FOUND TRANSPLANTING SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for fertilizer application
            if 'fertilizer application' in text.lower() and '3.10.5' in text:
                print(f"\n{'='*60}")
                print(f"FOUND FERTILIZER APPLICATION SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for pest control
            if 'pest control' in text.lower() and '3.10.5' in text:
                print(f"\n{'='*60}")
                print(f"FOUND PEST CONTROL SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")
            
            # Check for weed control
            if 'weed control' in text.lower() and '3.10.5' in text:
                print(f"\n{'='*60}")
                print(f"FOUND WEED CONTROL SECTION ON PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                # Show page text
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  {i+1}: {line.strip()}")

def main():
    find_onion_specific_sections()

if __name__ == "__main__":
    main()
