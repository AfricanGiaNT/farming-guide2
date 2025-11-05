#!/usr/bin/env python3
"""
Extract Crop Production Information from PDFs
Extracts general crop production information (not variety-specific) from PDF documents
"""

import os
import sys
import pdfplumber
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv('config/openai_key.env')

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available. Install with: pip install openai")

from scripts.utils.crop_production_info_handler import CropProductionInfoHandler

class CropProductionInfoExtractor:
    """Extract general crop production information from PDFs"""
    
    def __init__(self, pdf_directory: str = "data/pdfs"):
        """Initialize the extractor"""
        self.pdf_directory = Path(pdf_directory)
        self.handler = CropProductionInfoHandler()
        
        # Initialize OpenAI client if available
        self.openai_client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                print("Warning: OPENAI_API_KEY not found in environment")
    
    def find_crop_pdfs(self, crop_name: str) -> List[Path]:
        """Find all crop-related PDF files"""
        # Map crop names to keywords
        crop_keywords = {
            'maize': ['maize', 'corn'],
            'groundnut': ['groundnut', 'ground nut', 'peanut', 'arachis'],
            'groundnuts': ['groundnut', 'ground nut', 'peanut', 'arachis'],
            'beans': ['bean', 'phaseolus', 'common bean', 'haricot bean'],
            'phaseolus beans': ['bean', 'phaseolus', 'common bean', 'haricot bean'],
            'soybean': ['soybean', 'soya', 'soy', 'glycine max'],
            'soybeans': ['soybean', 'soya', 'soy', 'glycine max'],
            'soyabean': ['soybean', 'soya', 'soy', 'glycine max'],
            'cassava': ['cassava', 'manihot', 'manioc'],
        }
        
        keywords = crop_keywords.get(crop_name.lower(), [crop_name.lower()])
        crop_pdfs = []
        
        # Exclude keywords for certain crops
        exclude_keywords = {
            'beans': ['soybean', 'soya'],
            'phaseolus beans': ['soybean', 'soya'],
            'soybean': ['phaseolus', 'common bean', 'haricot bean'],
            'soybeans': ['phaseolus', 'common bean', 'haricot bean'],
            'soyabean': ['phaseolus', 'common bean', 'haricot bean'],
        }
        exclude = exclude_keywords.get(crop_name.lower(), [])
        
        for pdf_file in self.pdf_directory.glob("*.pdf"):
            filename_lower = pdf_file.name.lower()
            # Check if it matches crop keywords
            matches_crop = any(keyword in filename_lower for keyword in keywords)
            # Check if it should be excluded
            should_exclude = any(exclude_kw in filename_lower for exclude_kw in exclude)
            
            if matches_crop and not should_exclude:
                crop_pdfs.append(pdf_file)
        
        # Also include the main guide
        main_guide = self.pdf_directory / "Guide to Agriculture Production in Malawi 2021.pdf"
        if main_guide.exists() and main_guide not in crop_pdfs:
            crop_pdfs.append(main_guide)
        
        return sorted(crop_pdfs)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text content from PDF"""
        try:
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return "\n\n".join(text_parts)
        except Exception as e:
            print(f"Error extracting text from {pdf_path.name}: {e}")
            return ""
    
    def find_crop_section_in_guide(self, text: str, crop_name: str) -> str:
        """Find the crop section in the main guide"""
        # Look for crop section (usually starts with "3.x.x" or similar)
        patterns = [
            rf'3\.\d+\.\d+.*?{crop_name}.*?(?=3\.\d+\.\d+|$)',
            rf'{crop_name}.*?production.*?(?=3\.\d+\.\d+|$)',
            rf'section.*?{crop_name}.*?(?=section|$)',
        ]
        
        text_lower = text.lower()
        crop_start = text_lower.find(crop_name.lower())
        
        if crop_start == -1:
            return text[:10000]  # Return first 10000 chars if no crop found
        
        # Extract context around crop section (10000 chars before and 30000 after for comprehensive extraction)
        start = max(0, crop_start - 10000)
        end = min(len(text), crop_start + 30000)
        return text[start:end]
    
    def extract_production_info_ai(self, text: str, pdf_name: str, crop_name: str = "maize") -> Dict[str, Any]:
        """Use AI to extract production information from text"""
        if not self.openai_client:
            return {}
        
        prompt = f"""
You are an expert agricultural data extractor. Extract comprehensive general {crop_name} production information from the following text. Extract information that applies to {crop_name} in general, NOT specific varieties.

CRITICAL: Extract ALL available information with high quality and detail. Be thorough and comprehensive.

Focus on extracting detailed information for:

1. **Production Notes**: 
   - Disease management practices and recommendations
   - Pest management strategies
   - Drought tolerance characteristics
   - Water requirements and irrigation needs
   - Temperature requirements
   - General production guidelines and best practices
   - Any warnings or important considerations

2. **Land Preparation**: 
   - Detailed land preparation methods (plowing, harrowing, ridging)
   - Soil requirements and soil preparation
   - Field preparation procedures
   - Timing for land preparation
   - Any specific soil conditions needed

3. **Manure Application**: 
   - Manure/compost application rates (specify in tons per hectare)
   - Timing of application (before planting, during preparation, etc.)
   - Methods of application and incorporation
   - Types of manure recommended
   - Benefits of manure application

4. **Planting Information**: 
   - Planting time/seasons (specific months or conditions)
   - Spacing requirements (between rows, between plants)
   - Seed rate per hectare (specify exact amount)
   - Planting depth
   - Planting methods and guidelines
   - Best practices for planting

5. **Fertilizer Application**: 
   - Types of fertilizers (NPK ratios if mentioned)
   - Application rates (specify in kg/ha)
   - Timing (at planting, top-dressing, split application)
   - Application methods
   - Nutrient requirements

6. **Weeding**: 
   - Timing (specific weeks after planting)
   - Frequency of weeding
   - Methods (hand weeding, hoeing, herbicides)
   - Best practices for weed control
   - Critical periods for weed control

7. **Storing**: 
   - Storage conditions (temperature, humidity, ventilation requirements)
   - Drying requirements before storage
   - Container types recommended
   - Pest and moisture protection methods
   - Harvest timing and methods
   - Post-harvest handling
   - Storage duration and maintenance

Text to extract from:
{pdf_name}

---
{text[:18000]}  # Increased limit for better extraction
---

Return a JSON object with these exact keys. Return PLAIN TEXT STRINGS, not nested objects:
{{
    "production_notes": "comprehensive extracted text as a single string or null",
    "land_preparation": "comprehensive extracted text as a single string or null",
    "manure_application": "comprehensive extracted text as a single string or null",
    "planting_info": "comprehensive extracted text as a single string or null",
    "fertilizer_application": "comprehensive extracted text as a single string or null",
    "weeding": "comprehensive extracted text as a single string or null",
    "storing": "comprehensive extracted text as a single string or null"
}}

CRITICAL REQUIREMENTS:
- Return PLAIN TEXT STRINGS only, NOT nested JSON objects or dictionaries
- Extract ALL relevant information, not just summaries
- Include specific numbers, rates, and measurements (e.g., "5-10 tons per hectare", "75cm spacing")
- Include multiple methods if mentioned, separated by sentences
- Combine all related information into coherent paragraphs
- Be thorough - quality over brevity
- Only use null if absolutely no relevant information is found for that field
- Format as readable text that can be directly displayed to users
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert agricultural data extractor. Extract crop production information from text and return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                import json
                extracted = json.loads(json_match.group())
                
                # Convert nested dictionaries to readable text
                processed = {}
                for key, value in extracted.items():
                    if value and value != 'null':
                        if isinstance(value, dict):
                            # Convert dict to readable text
                            text_parts = []
                            for k, v in value.items():
                                if v and v != 'null':
                                    if isinstance(v, list):
                                        text_parts.append(f"{k}: {', '.join(str(item) for item in v)}")
                                    else:
                                        text_parts.append(f"{k}: {v}")
                            processed[key] = ". ".join(text_parts) if text_parts else None
                        elif isinstance(value, list):
                            processed[key] = ". ".join(str(item) for item in value)
                        else:
                            processed[key] = str(value)
                    else:
                        processed[key] = None
                
                return processed
            
            return {}
            
        except Exception as e:
            print(f"Error in AI extraction: {e}")
            return {}
    
    def extract_production_info_pattern(self, text: str) -> Dict[str, Any]:
        """Fallback pattern-based extraction"""
        info = {}
        
        # Land preparation patterns
        land_patterns = [
            r'land\s+preparation[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
            r'prepare\s+land[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
            r'plowing[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
        ]
        
        # Manure patterns
        manure_patterns = [
            r'manure[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
            r'farmyard\s+manure[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
            r'compost[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
        ]
        
        # Planting patterns
        planting_patterns = [
            r'planting[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
            r'spacing[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
            r'seed\s+rate[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
        ]
        
        # Fertilizer patterns
        fertilizer_patterns = [
            r'fertilizer[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
            r'NPK[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
            r'application\s+rate[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
        ]
        
        # Weeding patterns
        weeding_patterns = [
            r'weeding[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
            r'weed\s+control[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
        ]
        
        # Storage patterns
        storage_patterns = [
            r'storage[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
            r'harvest[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
            r'storing[:\s]+([^.!?]+(?:[.!?]+[^.!?]+){0,5})',
        ]
        
        text_lower = text.lower()
        
        # Extract land preparation
        for pattern in land_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                info['land_preparation'] = match.group(1).strip()
                break
        
        # Extract manure
        for pattern in manure_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                info['manure_application'] = match.group(1).strip()
                break
        
        # Extract planting
        for pattern in planting_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                if 'planting_info' not in info:
                    info['planting_info'] = ""
                info['planting_info'] += match.group(1).strip() + ". "
        
        # Extract fertilizer
        for pattern in fertilizer_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                info['fertilizer_application'] = match.group(1).strip()
                break
        
        # Extract weeding
        for pattern in weeding_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                info['weeding'] = match.group(1).strip()
                break
        
        # Extract storage
        for pattern in storage_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                info['storing'] = match.group(1).strip()
                break
        
        return info
    
    def merge_production_info(self, info_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge production information from multiple sources"""
        merged = {}
        
        for info in info_list:
            for key, value in info.items():
                if value and value != 'null':
                    if key not in merged:
                        merged[key] = []
                    merged[key].append(str(value).strip())
        
        # Combine and deduplicate
        result = {}
        for key, values in merged.items():
            # Remove duplicates while preserving order
            unique_values = []
            seen = set()
            for v in values:
                if v and v.lower() not in seen:
                    unique_values.append(v)
                    seen.add(v.lower())
            
            if unique_values:
                result[key] = "\n\n".join(unique_values)
        
        return result
    
    def extract_crop_production_info(self, crop_name: str) -> Dict[str, Any]:
        """Extract crop production information from all relevant PDFs"""
        print("=" * 80)
        print(f"EXTRACTING {crop_name.upper()} PRODUCTION INFORMATION")
        print("=" * 80)
        
        crop_pdfs = self.find_crop_pdfs(crop_name)
        print(f"\nFound {len(crop_pdfs)} {crop_name}-related PDFs:")
        for pdf in crop_pdfs:
            print(f"  - {pdf.name}")
        
        if not crop_pdfs:
            print(f"\n⚠️  No PDFs found for {crop_name}")
            return {}
        
        all_extracted_info = []
        
        for pdf_path in crop_pdfs:
            print(f"\n{'='*80}")
            print(f"Processing: {pdf_path.name}")
            print(f"{'='*80}")
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                print(f"  ⚠️  No text extracted from {pdf_path.name}")
                continue
            
            print(f"  ✓ Extracted {len(text)} characters")
            
            # If it's the main guide, extract just the crop section
            if "Guide to Agriculture Production" in pdf_path.name:
                text = self.find_crop_section_in_guide(text, crop_name)
                print(f"  ✓ Extracted {crop_name} section ({len(text)} characters)")
            
            # Extract information using AI if available
            if self.openai_client:
                print("  Using AI extraction...")
                info = self.extract_production_info_ai(text, pdf_path.name, crop_name)
            else:
                print("  Using pattern-based extraction...")
                info = self.extract_production_info_pattern(text)
            
            # Add source document
            info['source_document'] = pdf_path.name
            
            # Show what was extracted
            print(f"\n  Extracted fields:")
            for key, value in info.items():
                if value and value != 'null':
                    preview = str(value)[:150] + "..." if len(str(value)) > 150 else str(value)
                    print(f"    ✓ {key}: {preview}")
                else:
                    print(f"    ✗ {key}: Not found")
            
            all_extracted_info.append(info)
        
        # Merge all extracted information
        print(f"\n{'='*80}")
        print("MERGING INFORMATION FROM ALL SOURCES")
        print(f"{'='*80}")
        merged_info = self.merge_production_info(all_extracted_info)
        
        # Add combined source documents
        source_docs = [info.get('source_document', '') for info in all_extracted_info if info.get('source_document')]
        merged_info['source_document'] = "; ".join(set(source_docs))
        
        return merged_info
    
    def save_to_database(self, production_info: Dict[str, Any], crop_name: str = "maize") -> bool:
        """Save production information to database"""
        print(f"\n{'='*80}")
        print(f"SAVING TO DATABASE")
        print(f"{'='*80}")
        
        result = self.handler.insert_production_info(
            crop_name=crop_name,
            production_notes=production_info.get('production_notes'),
            land_preparation=production_info.get('land_preparation'),
            manure_application=production_info.get('manure_application'),
            planting_info=production_info.get('planting_info'),
            fertilizer_application=production_info.get('fertilizer_application'),
            weeding=production_info.get('weeding'),
            storing=production_info.get('storing'),
            source_document=production_info.get('source_document'),
            extraction_confidence=85
        )
        
        if result['success']:
            print(f"✓ Successfully saved production info for {crop_name}")
            return True
        else:
            print(f"✗ Error saving: {result.get('error', 'Unknown error')}")
            return False

def main():
    """Main execution"""
    import sys
    
    # Get crop name from command line or default to maize
    crop_name = sys.argv[1] if len(sys.argv) > 1 else "maize"
    
    extractor = CropProductionInfoExtractor()
    
    # Extract crop production information
    production_info = extractor.extract_crop_production_info(crop_name)
    
    # Display summary
    print(f"\n{'='*80}")
    print(f"EXTRACTION SUMMARY FOR {crop_name.upper()}")
    print(f"{'='*80}")
    for key, value in production_info.items():
        if value and value != 'null':
            print(f"\n{key.upper()}:")
            # Show first 300 characters for better preview
            preview = str(value)[:300] + "..." if len(str(value)) > 300 else str(value)
            print(f"  {preview}")
        else:
            print(f"\n{key.upper()}: Not found")
    
    # Save to database
    if production_info:
        save = input(f"\n\nSave {crop_name} production info to database? (y/n): ").strip().lower()
        if save == 'y':
            extractor.save_to_database(production_info, crop_name=crop_name)
        else:
            print("Skipped saving to database")
    else:
        print(f"\n⚠️  No production information extracted for {crop_name}")

if __name__ == "__main__":
    main()

