#!/usr/bin/env python3
import pdfplumber
import re
from typing import List, Dict
import json

def extract_maize_varieties():
    """Extract maize variety information from Malawi-Maize-Growers-Guide_1.pdf"""
    pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Malawi-Maize-Growers-Guide_1.pdf"
    
    varieties = []
    variety_info = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        # Based on TOC, variety information is on page 14-16
        for page_num in range(13, 16):  # 0-indexed, so 14-16 becomes 13-15
            text = pdf.pages[page_num].extract_text() or ""
            print(f"\n--- Page {page_num+1} ---")
            print(text[:1000])
            
            # Look for specific variety information
            if page_num == 14:  # Page 15
                # Extract early vs. medium-late maturity info
                early_maturity_match = re.search(r'Early maturing hybrids take between (\d+) and (\d+) days', text)
                if early_maturity_match:
                    variety_info['early_maturity'] = f"{early_maturity_match.group(1)}-{early_maturity_match.group(2)} days"
                
                medium_late_match = re.search(r'medium to late maturing varieties take between (\d+) and (\d+) days', text)
                if medium_late_match:
                    variety_info['medium_late_maturity'] = f"{medium_late_match.group(1)}-{medium_late_match.group(2)} days"
    
    # Extract disease information from disease brochure
    disease_pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Malawi-Maize-disease-brochure.pdf"
    disease_info = {}
    
    with pdfplumber.open(disease_pdf_path) as pdf:
        # Look for disease management recommendations
        for page_num in range(min(20, len(pdf.pages))):
            text = pdf.pages[page_num].extract_text() or ""
            
            # Look for disease names and management
            if "Management and Control" in text:
                # Extract disease name from page
                disease_name = None
                lines = text.split('\n')
                for line in lines[:5]:  # Check first few lines for disease name
                    if len(line.strip()) > 0 and len(line.strip()) < 30 and ":" not in line:
                        disease_name = line.strip()
                        break
                
                if disease_name:
                    # Extract management recommendations
                    management_match = re.search(r'Management and Control(.*?)(?:\n\n|\Z)', text, re.DOTALL)
                    if management_match:
                        management_text = management_match.group(1).strip()
                        disease_info[disease_name] = management_text
    
    # Compile information from both sources
    result = {
        'variety_maturity': variety_info,
        'disease_management': disease_info
    }
    
    return result

if __name__ == "__main__":
    info = extract_maize_varieties()
    print("\n" + "="*80)
    print("EXTRACTED MAIZE INFORMATION")
    print("="*80)
    
    # Print variety maturity info
    if 'variety_maturity' in info:
        print("\nVariety Maturity Information:")
        for category, days in info['variety_maturity'].items():
            print(f"  {category.replace('_', ' ').title()}: {days}")
    
    # Print disease management info
    if 'disease_management' in info:
        print("\nDisease Management Information:")
        for disease, management in info['disease_management'].items():
            print(f"\n  {disease}:")
            print(f"    {management[:200]}...")
