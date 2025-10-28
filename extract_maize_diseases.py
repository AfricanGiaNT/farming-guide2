#!/usr/bin/env python3
import pdfplumber
import re
from typing import List, Dict
import json

def extract_maize_diseases():
    """Extract maize disease information from Malawi-Maize-disease-brochure.pdf"""
    pdf_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Malawi-Maize-disease-brochure.pdf"
    
    diseases = {}
    current_disease = None
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Scan through pages to find disease information
        for page_num in range(len(pdf.pages)):
            text = pdf.pages[page_num].extract_text() or ""
            
            # Skip empty pages
            if len(text.strip()) < 10:
                continue
            
            # Check if this page has a disease name (usually short text at top of page)
            lines = text.split('\n')
            if len(lines) > 0 and len(lines[0].strip()) > 0 and len(lines[0].strip()) < 30:
                potential_disease = lines[0].strip()
                
                # Verify it's a disease name (not a header or other text)
                if "MAIZE" not in potential_disease.upper() and "PAGE" not in potential_disease.upper():
                    current_disease = potential_disease
                    diseases[current_disease] = {
                        'page': page_num + 1,
                        'symptoms': [],
                        'management': []
                    }
            
            # Extract symptoms and management for current disease
            if current_disease:
                # Extract symptoms
                symptoms_match = re.search(r'Symptoms:(.*?)(?:Management and Control|Causal organism|\Z)', text, re.DOTALL)
                if symptoms_match:
                    symptom_text = symptoms_match.group(1).strip()
                    # Extract numbered points
                    symptom_points = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|$)', symptom_text, re.DOTALL)
                    if symptom_points:
                        diseases[current_disease]['symptoms'] = [point.strip() for point in symptom_points]
                
                # Extract management recommendations
                management_match = re.search(r'Management and Control(.*?)(?:\n\n|\Z)', text, re.DOTALL)
                if management_match:
                    management_text = management_match.group(1).strip()
                    # Extract numbered points
                    management_points = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|$)', management_text, re.DOTALL)
                    if management_points:
                        diseases[current_disease]['management'] = [point.strip() for point in management_points]
    
    return diseases

if __name__ == "__main__":
    diseases = extract_maize_diseases()
    
    print("\n" + "="*80)
    print(f"EXTRACTED {len(diseases)} MAIZE DISEASES")
    print("="*80)
    
    # Print disease information
    for disease, info in diseases.items():
        print(f"\n{disease} (Page {info['page']}):")
        
        if info['symptoms']:
            print("  Symptoms:")
            for symptom in info['symptoms']:
                print(f"    - {symptom}")
        
        if info['management']:
            print("  Management:")
            for management in info['management']:
                if "tolerant hybrids" in management.lower() or "resistant" in management.lower():
                    print(f"    - {management} [RESISTANCE RECOMMENDATION]")
                else:
                    print(f"    - {management}")
        
        print()
