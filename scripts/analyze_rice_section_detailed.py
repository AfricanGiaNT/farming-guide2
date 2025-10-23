#!/usr/bin/env python3
"""
Rice Section Detailed Analysis
Examine rice pages in detail to find fertilizer information and improve variety extraction
"""

import pdfplumber
import re

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def analyze_rice_section():
    """Analyze rice section in detail"""
    
    print("=" * 80)
    print("DETAILED RICE SECTION ANALYSIS")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Process rice section pages (168-175)
        for page_num in range(167, 175):  # Pages 168-175 (0-indexed)
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check if this page contains rice content
            if 'rice' not in text.lower():
                continue
            
            print(f"\n{'='*60}")
            print(f"PAGE {page_num + 1}")
            print(f"{'='*60}")
            
            # Look for fertilizer-related content
            fertilizer_keywords = ['fertilizer', 'nitrogen', 'phosphorus', 'potassium', 'basal', 'top dressing', 'application']
            fertilizer_lines = []
            
            lines = text.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in fertilizer_keywords):
                    fertilizer_lines.append(line.strip())
            
            if fertilizer_lines:
                print(f"\nFERTILIZER INFORMATION FOUND:")
                for line in fertilizer_lines:
                    print(f"  {line}")
            
            # Look for variety-related content
            variety_keywords = ['variety', 'varieties', 'cultivar', 'nerica', 'changu', 'senga', 'vyawo']
            variety_lines = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in variety_keywords):
                    variety_lines.append(line.strip())
            
            if variety_lines:
                print(f"\nVARIETY INFORMATION FOUND:")
                for line in variety_lines[:10]:  # Show first 10
                    print(f"  {line}")
                if len(variety_lines) > 10:
                    print(f"  ... and {len(variety_lines) - 10} more lines")
            
            # Look for specific sections
            sections = [
                'use of improved varieties',
                'fertilizer application',
                'fertilizer requirements',
                'nutrient management',
                'soil fertility'
            ]
            
            found_sections = []
            for section in sections:
                if section in text.lower():
                    found_sections.append(section)
            
            if found_sections:
                print(f"\nSECTIONS FOUND: {', '.join(found_sections)}")
            
            # Show first few lines of text for context
            print(f"\nFIRST 10 LINES:")
            for i, line in enumerate(lines[:10]):
                if line.strip():
                    print(f"  {i+1}: {line.strip()}")

def main():
    analyze_rice_section()

if __name__ == "__main__":
    main()
