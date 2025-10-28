#!/usr/bin/env python3
"""
Update maize varieties with detailed information from Malawi Maize Growers Guide and Disease Brochure
"""

import pdfplumber
import re
from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime
import json

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

class MaizeVarietyUpdater:
    """
    Update maize varieties with detailed information from the Malawi Maize Growers Guide
    """
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.growers_guide_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Malawi-Maize-Growers-Guide_1.pdf"
        self.disease_brochure_path = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Malawi-Maize-disease-brochure.pdf"
    
    def get_existing_varieties(self) -> List[Dict]:
        """Get all existing maize varieties from database"""
        try:
            result = self.supabase.table("varieties").select("*").eq("crop_name", "maize").execute()
            return result.data
        except Exception as e:
            print(f"Error getting existing varieties: {e}")
            return []
    
    def extract_maturity_info(self) -> Dict:
        """Extract maturity information from the Malawi Maize Growers Guide"""
        maturity_info = {}
        
        with pdfplumber.open(self.growers_guide_path) as pdf:
            # Based on TOC, variety information is on page 14-16
            for page_num in range(13, 16):  # 0-indexed, so 14-16 becomes 13-15
                text = pdf.pages[page_num].extract_text() or ""
                
                # Extract early vs. medium-late maturity info
                early_maturity_match = re.search(r'Early maturing hybrids take between (\d+) and (\d+) days', text)
                if early_maturity_match:
                    maturity_info['early_maturity'] = {
                        'min': int(early_maturity_match.group(1)),
                        'max': int(early_maturity_match.group(2))
                    }
                
                medium_late_match = re.search(r'medium to late maturing varieties take between (\d+) and (\d+) days', text)
                if medium_late_match:
                    maturity_info['medium_late_maturity'] = {
                        'min': int(medium_late_match.group(1)),
                        'max': int(medium_late_match.group(2))
                    }
                
                # Look for series information
                series_match = re.search(r'700 series.*?600 Series.*?500 series.*?400 series', text, re.DOTALL)
                if series_match:
                    series_text = series_match.group(0)
                    
                    # Extract series and examples
                    series_700 = re.search(r'700 series e\.g\.,\s+(.*?)(?:\n|$)', series_text)
                    if series_700:
                        maturity_info['700_series'] = series_700.group(1).strip()
                    
                    series_600 = re.search(r'600 Series e\.g\.,\s+(.*?)(?:\n|$)', series_text)
                    if series_600:
                        maturity_info['600_series'] = series_600.group(1).strip()
                    
                    series_500 = re.search(r'500 series e\.g\.,\s+(.*?)(?:\n|$)', series_text)
                    if series_500:
                        maturity_info['500_series'] = series_500.group(1).strip()
                    
                    series_400 = re.search(r'400 series e\.g\.,\s+(.*?)(?:\n|$)', series_text)
                    if series_400:
                        maturity_info['400_series'] = series_400.group(1).strip()
        
        return maturity_info
    
    def extract_disease_management(self) -> Dict:
        """Extract disease management information from the Malawi Maize Disease Brochure"""
        diseases = {}
        current_disease = None
        
        with pdfplumber.open(self.disease_brochure_path) as pdf:
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
                    # Extract management recommendations
                    management_match = re.search(r'Management and Control(.*?)(?:\n\n|\Z)', text, re.DOTALL)
                    if management_match:
                        management_text = management_match.group(1).strip()
                        # Extract numbered points
                        management_points = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|$)', management_text, re.DOTALL)
                        if management_points:
                            diseases[current_disease]['management'] = [point.strip() for point in management_points]
        
        return diseases
    
    def determine_maturity_days(self, variety_name: str, maturity_info: Dict) -> Optional[int]:
        """Determine maturity days based on variety name and series"""
        # Check if variety is in a specific series
        if '700' in variety_name or any(series in variety_name for series in ['719', '727', '737']):
            # 700 series - late maturing
            return maturity_info.get('medium_late_maturity', {}).get('max', 155)
        elif '600' in variety_name or any(series in variety_name for series in ['627', '649', '653']):
            # 600 series - medium-late maturing
            return maturity_info.get('medium_late_maturity', {}).get('min', 145)
        elif '500' in variety_name or any(series in variety_name for series in ['529', '537']):
            # 500 series - medium maturing
            return (maturity_info.get('early_maturity', {}).get('max', 140) + 
                   maturity_info.get('medium_late_maturity', {}).get('min', 141)) // 2
        elif '400' in variety_name or any(series in variety_name for series in ['403', '419', '423']):
            # 400 series - early maturing
            return maturity_info.get('early_maturity', {}).get('min', 120)
        
        # Default based on whether it seems early or late maturing
        if any(term in variety_name.lower() for term in ['early', 'quick']):
            return maturity_info.get('early_maturity', {}).get('min', 120)
        elif any(term in variety_name.lower() for term in ['late', 'long']):
            return maturity_info.get('medium_late_maturity', {}).get('max', 155)
        
        # Default to middle range
        return (maturity_info.get('early_maturity', {}).get('max', 140) + 
               maturity_info.get('medium_late_maturity', {}).get('min', 141)) // 2
    
    def extract_disease_resistance(self, diseases: Dict) -> Dict[str, List[str]]:
        """Extract disease resistance recommendations for varieties"""
        resistance_info = {}
        
        for disease, info in diseases.items():
            for management in info.get('management', []):
                # Look for hybrid recommendations
                if "tolerant hybrids" in management.lower() or "resistant" in management.lower():
                    # Check if specific varieties are mentioned
                    variety_match = re.search(r'(SC\s*\d+|MH\s*\d+|PAN\s*\d+)', management)
                    if variety_match:
                        variety = variety_match.group(1).replace(' ', '')
                        if variety not in resistance_info:
                            resistance_info[variety] = []
                        resistance_info[variety].append(disease)
        
        return resistance_info
    
    def compile_disease_management_guidelines(self, diseases: Dict) -> str:
        """Compile disease management guidelines from all diseases"""
        guidelines = []
        
        for disease, info in diseases.items():
            for management in info.get('management', []):
                if ("tolerant hybrids" in management.lower() or 
                    "resistant" in management.lower() or 
                    "rotation" in management.lower() or
                    "fungicide" in management.lower()):
                    guidelines.append(f"For {disease}: {management}")
        
        # Limit to most important guidelines
        if len(guidelines) > 5:
            guidelines = guidelines[:5]
        
        return " ".join(guidelines)
    
    def update_variety_details(self, variety: Dict, maturity_info: Dict, diseases: Dict, disease_resistance: Dict) -> bool:
        """
        Update a variety with detailed information
        """
        try:
            variety_name = variety.get('variety_name', '').strip()
            
            # Determine maturity days if not already set
            maturity_days = variety.get('maturity_days')
            if not maturity_days:
                maturity_days = self.determine_maturity_days(variety_name, maturity_info)
            
            # Check for disease resistance
            disease_resistance_list = []
            for var_pattern, diseases_list in disease_resistance.items():
                if var_pattern in variety_name:
                    disease_resistance_list.extend(diseases_list)
            
            # If no specific resistance found, keep existing
            if not disease_resistance_list and variety.get('disease_resistance'):
                disease_resistance_list = variety.get('disease_resistance')
            
            # Compile disease management guidelines
            disease_management = self.compile_disease_management_guidelines(diseases)
            
            # Prepare update data
            update_data = {
                'updated_at': datetime.now().isoformat(),
                'source_document': "Malawi Maize Growers Guide and Disease Brochure"
            }
            
            # Only update fields if we have new information
            if maturity_days:
                update_data['maturity_days'] = maturity_days
            
            if disease_resistance_list:
                update_data['disease_resistance'] = disease_resistance_list
            
            if disease_management:
                update_data['disease_management'] = disease_management
            
            # Update variety in database
            self.supabase.table("varieties").update(update_data).eq("id", variety['id']).execute()
            
            print(f"  + Updated: {variety_name}")
            return True
            
        except Exception as e:
            print(f"  - Error updating {variety.get('variety_name', '')}: {e}")
            return False
    
    def update_all_varieties(self) -> int:
        """
        Update all maize varieties with detailed information
        """
        print("=" * 80)
        print("MAIZE DETAILED INFORMATION EXTRACTION")
        print("=" * 80)
        
        # Get existing varieties
        varieties = self.get_existing_varieties()
        print(f"\nFound {len(varieties)} maize varieties in database")
        
        # Extract maturity information
        maturity_info = self.extract_maturity_info()
        print(f"Extracted maturity information from Malawi Maize Growers Guide")
        
        # Extract disease information
        diseases = self.extract_disease_management()
        print(f"Extracted {len(diseases)} diseases from Malawi Maize Disease Brochure")
        
        # Extract disease resistance information
        disease_resistance = self.extract_disease_resistance(diseases)
        print(f"Found disease resistance information for {len(disease_resistance)} variety patterns")
        
        updated = 0
        for variety in varieties:
            if self.update_variety_details(variety, maturity_info, diseases, disease_resistance):
                updated += 1
        
        print(f"\n{'='*80}")
        print(f"Updated {updated} out of {len(varieties)} varieties")
        print(f"{'='*80}")
        
        return updated

def main():
    print("=" * 80)
    print("MAIZE DETAILED INFORMATION EXTRACTION")
    print("Extracting detailed production information from Malawi Maize Guides")
    print("=" * 80)
    
    updater = MaizeVarietyUpdater()
    updated = updater.update_all_varieties()
    
    print(f"\n+ Extraction complete: {updated} varieties updated")

if __name__ == "__main__":
    main()
