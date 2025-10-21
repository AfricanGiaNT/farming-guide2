"""
Targeted Chapter 3 Crop Varieties Extractor
Based on the structure of "Guide to Agriculture Production in Malawi 2021" Chapter 3
"""

import os
import re
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

import PyPDF2
from openai import OpenAI

from scripts.varieties_extraction.database_manager import VarietiesDatabaseManager
from scripts.utils.logger import BotLogger

logger = BotLogger()

class TargetedChapter3Extractor:
    """Extract crop varieties specifically from Chapter 3 of the agriculture guide"""
    
    def __init__(self, db_manager: VarietiesDatabaseManager, openai_key: Optional[str] = None):
        self.db_manager = db_manager
        self.openai_client = OpenAI(api_key=openai_key) if openai_key else None
        
        # Define crop categories based on Chapter 3 structure
        self.crop_categories = {
            'cereal': ['maize', 'rice', 'sorghum', 'pearl millet', 'finger millet', 'wheat'],
            'legume': ['phaseolus beans', 'groundnut', 'soyabean', 'pigeonpea', 'cowpea', 
                      'bambara nut', 'ground beans', 'chickpea', 'field pea', 'green grams', 
                      'black grams', 'guar', 'cluster bean'],
            'oilseed': ['sunflower', 'sesame', 'castor seed'],
            'tuber': ['cassava', 'sweet potato', 'potato'],
            'cash_crop': ['tobacco', 'cotton'],
            'fruit': ['citrus', 'bananas', 'plantains', 'pineapples', 'mangoes', 'avocado', 
                     'pawpaw', 'guava'],
            'tree_nut': ['cashew nut', 'macadamia', 'coconut'],
            'spice': ['chillies', 'tumeric', 'ginger', 'cardamom', 'pepper', 'coriander', 
                     'paprika', 'cinnamon'],
            'vegetable': ['cabbage', 'tomatoes', 'onions', 'garlic', 'leafy vegetables', 
                         'okra', 'carrot', 'eggplant', 'lettuce', 'cucumber', 'mushroom']
        }
        
        # Page ranges for each crop section (will be discovered)
        self.crop_page_ranges = {}
        
    def discover_crop_page_ranges(self, pdf_path: str) -> Dict[str, Tuple[int, int]]:
        """Discover page ranges for each crop section in Chapter 3"""
        logger.info("Discovering crop page ranges from Chapter 3")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_ranges = {}
            
            # Start from page 131 (Chapter 3 start)
            start_page = 130  # 0-indexed
            
            for page_num in range(start_page, len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                
                # Look for crop section headers
                for category, crops in self.crop_categories.items():
                    for crop in crops:
                        # Look for crop name patterns
                        crop_patterns = [
                            rf'\b{crop}\b',
                            rf'{crop}\s+varieties?',
                            rf'{crop}\s+production',
                            rf'{crop}\s+cultivation'
                        ]
                        
                        for pattern in crop_patterns:
                            if re.search(pattern, page_text, re.IGNORECASE):
                                if crop not in page_ranges:
                                    page_ranges[crop] = page_num + 1
                                break
                
                # Stop if we've moved beyond Chapter 3 (look for Chapter 4)
                if 'Chapter 4' in page_text:
                    break
            
            logger.info(f"Discovered page ranges for {len(page_ranges)} crops")
            return page_ranges
    
    def extract_crop_section_text(self, pdf_path: str, crop_name: str, start_page: int, end_page: int = None) -> str:
        """Extract text for a specific crop section"""
        logger.info(f"Extracting text for {crop_name} from pages {start_page}-{end_page or 'end'}")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            if end_page is None:
                end_page = len(pdf_reader.pages)
            
            crop_text = ""
            for page_num in range(start_page - 1, min(end_page, len(pdf_reader.pages))):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                crop_text += page_text + "\n"
                
                # Stop if we hit the next crop section
                if page_num > start_page - 1:
                    next_crop_found = False
                    for other_crop in self.crop_categories.values():
                        for other_crop_name in other_crop:
                            if other_crop_name != crop_name and re.search(rf'\b{other_crop_name}\b', page_text, re.IGNORECASE):
                                next_crop_found = True
                                break
                        if next_crop_found:
                            break
                    if next_crop_found:
                        break
            
            return crop_text
    
    def extract_varieties_from_text(self, crop_name: str, text: str) -> List[Dict[str, Any]]:
        """Extract variety information from crop text using pattern matching and AI"""
        logger.info(f"Extracting varieties for {crop_name}")
        
        varieties = []
        
        # Pattern-based extraction for common variety patterns
        variety_patterns = [
            r'(?:variety|varieties?|cultivar|cultivars?)\s*:?\s*([A-Z0-9\s\-]+)',
            r'(?:recommended|suitable|common)\s+(?:variety|varieties?)\s*:?\s*([A-Z0-9\s\-]+)',
            r'([A-Z]{2,}\d{2,})',  # Common variety codes like SC403, MH18
            r'([A-Z][a-z]+\s+\d+)',  # Names with numbers
        ]
        
        for pattern in variety_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                variety_name = match.strip()
                if len(variety_name) > 2 and variety_name not in [v.get('variety_name', '') for v in varieties]:
                    varieties.append({
                        'variety_name': variety_name,
                        'extraction_method': 'pattern',
                        'confidence': 0.7
                    })
        
        # AI-powered extraction if available
        if self.openai_client and len(text) > 100:
            try:
                ai_varieties = self._extract_varieties_with_ai(crop_name, text)
                for ai_variety in ai_varieties:
                    # Avoid duplicates
                    if not any(v.get('variety_name', '').lower() == ai_variety.get('variety_name', '').lower() for v in varieties):
                        varieties.append(ai_variety)
            except Exception as e:
                logger.warning(f"AI extraction failed for {crop_name}: {e}")
        
        logger.info(f"Found {len(varieties)} varieties for {crop_name}")
        return varieties
    
    def _extract_varieties_with_ai(self, crop_name: str, text: str) -> List[Dict[str, Any]]:
        """Use AI to extract variety information"""
        prompt = f"""
        Extract crop variety information from the following text about {crop_name}:
        
        Text: {text[:2000]}
        
        Please identify all crop varieties mentioned and extract the following information for each:
        - Variety name
        - Maturity period (days)
        - Yield potential (low/medium/high)
        - Drought tolerance (low/medium/high)
        - Disease resistance (list any mentioned)
        - Planting months
        - Harvest months
        - Any special characteristics
        
        Return the information as a JSON array of objects.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        try:
            ai_data = json.loads(response.choices[0].message.content)
            varieties = []
            
            for item in ai_data:
                variety = {
                    'variety_name': item.get('variety_name', ''),
                    'maturity_days': self._parse_maturity_days(item.get('maturity_period', '')),
                    'yield_potential': item.get('yield_potential', 'medium'),
                    'drought_tolerance': item.get('drought_tolerance', 'medium'),
                    'disease_resistance': json.dumps(item.get('disease_resistance', [])),
                    'planting_months': json.dumps(item.get('planting_months', [])),
                    'harvest_months': json.dumps(item.get('harvest_months', [])),
                    'extraction_method': 'ai',
                    'confidence': 0.9
                }
                varieties.append(variety)
            
            return varieties
            
        except Exception as e:
            logger.error(f"Failed to parse AI response for {crop_name}: {e}")
            return []
    
    def _parse_maturity_days(self, maturity_text: str) -> Optional[int]:
        """Parse maturity period text to extract days"""
        if not maturity_text:
            return None
        
        # Look for number patterns
        numbers = re.findall(r'\d+', maturity_text)
        if numbers:
            return int(numbers[0])
        
        # Common maturity periods
        maturity_map = {
            'short': 90,
            'medium': 120,
            'long': 150,
            'early': 100,
            'late': 140
        }
        
        for key, days in maturity_map.items():
            if key in maturity_text.lower():
                return days
        
        return None
    
    def extract_farming_processes(self, crop_name: str, text: str) -> List[Dict[str, Any]]:
        """Extract farming process steps from crop text"""
        logger.info(f"Extracting farming processes for {crop_name}")
        
        processes = []
        
        # Common farming process patterns
        process_patterns = [
            r'(?:land\s+preparation|soil\s+preparation)',
            r'(?:planting|sowing)',
            r'(?:fertilizer|fertilization)',
            r'(?:irrigation|watering)',
            r'(?:weeding|weed\s+control)',
            r'(?:pest\s+control|pest\s+management)',
            r'(?:disease\s+control|disease\s+management)',
            r'(?:harvesting|harvest)',
            r'(?:post\s+harvest|storage)'
        ]
        
        for i, pattern in enumerate(process_patterns):
            if re.search(pattern, text, re.IGNORECASE):
                processes.append({
                    'process_type': self._map_process_type(pattern),
                    'step_number': i + 1,
                    'step_description': f"{pattern.replace('(?:', '').replace(')', '')} for {crop_name}",
                    'timing': 'As recommended',
                    'tools_required': json.dumps([]),
                    'notes': f"Extracted from agriculture guide"
                })
        
        return processes
    
    def _map_process_type(self, pattern: str) -> str:
        """Map process pattern to process type"""
        if 'land' in pattern or 'soil' in pattern:
            return 'land_preparation'
        elif 'planting' in pattern or 'sowing' in pattern:
            return 'planting'
        elif 'harvest' in pattern:
            return 'harvesting'
        else:
            return 'maintenance'
    
    def determine_crop_category(self, crop_name: str) -> str:
        """Determine crop category based on crop name"""
        crop_lower = crop_name.lower()
        
        for category, crops in self.crop_categories.items():
            for crop in crops:
                if crop.lower() in crop_lower or crop_lower in crop.lower():
                    return category
        
        return 'other'
    
    def process_crop(self, pdf_path: str, crop_name: str, start_page: int) -> bool:
        """Process a single crop and save to database"""
        logger.info(f"Processing crop: {crop_name}")
        
        try:
            # Extract crop text
            crop_text = self.extract_crop_section_text(pdf_path, crop_name, start_page)
            
            if not crop_text.strip():
                logger.warning(f"No text found for {crop_name}")
                return False
            
            # Determine category
            category = self.determine_crop_category(crop_name)
            
            # Save crop to database
            crop_id = self.db_manager.save_crop({
                'crop_name': crop_name,
                'category': category,
                'general_description': f"Agricultural information for {crop_name} from Malawi Agriculture Guide",
                'source_document': 'Guide to Agriculture Production in Malawi 2021'
            })
            
            if not crop_id:
                logger.error(f"Failed to save crop {crop_name}")
                return False
            
            # Extract varieties
            varieties = self.extract_varieties_from_text(crop_name, crop_text)
            
            # Save varieties
            for variety_data in varieties:
                variety_data.update({
                    'crop_id': crop_id,
                    'source_document': 'Guide to Agriculture Production in Malawi 2021',
                    'extraction_session_id': f"chapter3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                })
                
                variety_id = self.db_manager.save_variety(variety_data)
                
                if variety_id:
                    # Extract farming processes
                    processes = self.extract_farming_processes(crop_name, crop_text)
                    
                    for process_data in processes:
                        process_data['variety_id'] = variety_id
                        self.db_manager.save_farming_process(process_data)
            
            logger.info(f"Successfully processed {crop_name} with {len(varieties)} varieties")
            return True
            
        except Exception as e:
            logger.error(f"Error processing crop {crop_name}: {e}")
            return False
    
    def run_extraction(self, pdf_path: str) -> Dict[str, Any]:
        """Run the complete extraction process for Chapter 3"""
        logger.info("Starting targeted Chapter 3 extraction")
        
        # Discover page ranges
        page_ranges = self.discover_crop_page_ranges(pdf_path)
        
        # Create extraction session
        session_id = f"chapter3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.db_manager.create_extraction_session(session_id, 'pattern')
        
        results = {
            'session_id': session_id,
            'crops_processed': 0,
            'varieties_extracted': 0,
            'errors': []
        }
        
        # Process each crop
        for crop_name, start_page in page_ranges.items():
            try:
                success = self.process_crop(pdf_path, crop_name, start_page)
                if success:
                    results['crops_processed'] += 1
                    
                    # Count varieties for this crop
                    crop_id = self.db_manager.get_crop_id(crop_name)
                    if crop_id:
                        variety_count = self.db_manager.get_variety_count(crop_id)
                        results['varieties_extracted'] += variety_count
                        
            except Exception as e:
                error_msg = f"Error processing {crop_name}: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Update session status
        self.db_manager.update_extraction_session(session_id, {
            'extraction_status': 'completed',
            'total_crops_found': results['crops_processed'],
            'total_varieties_extracted': results['varieties_extracted'],
            'error_log': json.dumps(results['errors']) if results['errors'] else None
        })
        
        logger.info(f"Chapter 3 extraction completed: {results['crops_processed']} crops, {results['varieties_extracted']} varieties")
        return results

if __name__ == "__main__":
    # Test the extractor
    db_manager = VarietiesDatabaseManager('data/agricultural_documents.db')
    extractor = TargetedChapter3Extractor(db_manager)
    
    pdf_path = 'data/pdfs/Guide to Agriculture Production in Malawi 2021.pdf'
    results = extractor.run_extraction(pdf_path)
    
    print(f"Extraction Results: {results}")
