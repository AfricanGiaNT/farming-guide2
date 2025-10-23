#!/usr/bin/env python3
"""
Debug Sunflower Variety Extraction
Debug why varieties aren't being extracted
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def debug_sunflower_extraction():
    """Debug sunflower variety extraction"""
    
    print("=" * 80)
    print("DEBUG SUNFLOWER VARIETY EXTRACTION")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        for page_num in range(213, 217):  # Search around pages 214-215
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            if '3.3.2.1' in text or 'sunflower' in text.lower():
                print(f"\n{'='*60}")
                print(f"PAGE {page_num + 1}")
                print(f"{'='*60}")
                
                lines = text.split('\n')
                
                # Look for variety names
                variety_names = []
                for line in lines:
                    line = line.strip()
                    if any(name in line for name in ['PAN 7351', 'PAN 7049', 'PAN 7232', 'SO 323', 'Super 430', 'Super 530', 'Agsun 51', 'Agsun 57', 'HV3037']):
                        variety_names.append(line)
                        print(f"FOUND VARIETY: {line}")
                
                # Show all lines that might contain variety info
                print(f"\nAll lines containing variety keywords:")
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in ['variety', 'varieties', 'pan', 'super', 'agsun', 'hv']):
                        print(f"  {i+1}: {line}")
                
                # Show lines around variety mentions
                print(f"\nLines around variety mentions:")
                for i, line in enumerate(lines):
                    if any(name in line for name in ['PAN', 'Super', 'Agsun', 'HV']):
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        print(f"  Context around line {i+1}:")
                        for j in range(start, end):
                            marker = ">>> " if j == i else "    "
                            print(f"  {marker}{j+1}: {lines[j]}")

def main():
    debug_sunflower_extraction()

if __name__ == "__main__":
    main()
