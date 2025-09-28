#!/usr/bin/env python3
"""
Variety Data Extraction Pipeline
Combines rule-based extraction with AI fallback for comprehensive variety data extraction
"""

import sqlite3
import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.handlers.varieties_handler import VarietiesHandler

class VarietyExtractionPipeline:
    """Pipeline for extracting variety data using rule-based and AI methods"""
    
    def __init__(self, db_path: str = "data/agricultural_documents.db"):
        self.db_path = db_path
        if not os.path.isabs(self.db_path):
            self.db_path = os.path.join(project_root, self.db_path)
        
        # Initialize AI handler for fallback
        self.varieties_handler = VarietiesHandler()
        
        # Rule-based patterns for different crops
        self.variety_patterns = {
            'groundnut': {
                'patterns': [
                    r'\b(CG\s*\d+)\b',  # CG 7, CG8, etc.
                    r'\b(Chalimbana\s*\d*)\b',  # Chalimbana 2005
                    r'\b(Nsinjiro|Kakoma|Chitala|Baka)\b'
                ],
                'context_keywords': ['groundnut', 'peanut', 'virginia', 'spanish']
            },
            'maize': {
                'patterns': [
                    r'\b(SC\s*\d+)\b',  # SC 301, SC403, etc.
                    r'\b(PAN\s*\d+[A-Z]*)\b',  # PAN 12, PAN53, etc.
                    r'\b(MH\s*\d+[A-Z]*)\b',  # MH 18, MH26, etc.
                    r'\b(ZM\s*\d+)\b',  # ZM 309, etc.
                    r'\b(DK\s*\d+)\b'   # DK varieties
                ],
                'context_keywords': ['maize', 'corn', 'hybrid']
            },
            'soybean': {
                'patterns': [
                    r'\b(TGX\s*\d+[A-Z]*)\b',  # TGX varieties
                    r'\b(Tikolore|Magoye|Ocepara\s*\d*)\b',
                    r'\b(Nasoko|Makwacha|Solitaire|Soprano|Serenade)\b'
                ],
                'context_keywords': ['soybean', 'soya', 'legume']
            },
            'phaseolus_bean': {
                'patterns': [
                    r'\b(NUA\s*\d+)\b',  # NUA 45, NUA 59
                    r'\b(PAN\s*\d+)\b',  # PAN 148, PAN 9249
                    r'\b(VTTT\s*\d+/?\d*-?\d*)\b',  # VTTT 924/10-4
                    r'\b(Chitedze\s*Bean\s*\d+|CB\d+)\b',
                    r'\b(Kholophethe|Kabalabala|Namajengo)\b'
                ],
                'context_keywords': ['phaseolus', 'bean', 'climbing', 'bush']
            },
            'rice': {
                'patterns': [
                    r'\b(NERICA\s*\d+)\b',  # NERICA 3, NERICA 4
                    r'\b(WITA\s*\d+)\b',    # WITA varieties
                    r'\b(Kilombero)\b'
                ],
                'context_keywords': ['rice', 'paddy', 'upland']
            }
        }
    
    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def rule_based_extraction(self, text: str, crop_name: str, source_document: str) -> List[Dict[str, Any]]:
        """
        Extract varieties using rule-based patterns
        High precision, fast execution
        """
        varieties = []
        
        if crop_name not in self.variety_patterns:
            return varieties
        
        crop_config = self.variety_patterns[crop_name]
        text_lower = text.lower()
        
        # Check if text is relevant to this crop
        context_match = any(keyword in text_lower for keyword in crop_config['context_keywords'])
        if not context_match:
            return varieties
        
        # Extract varieties using patterns
        for pattern in crop_config['patterns']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                variety_name = match.group(1).strip()
                
                # Get surrounding context for validation
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                variety = {
                    'name': variety_name,
                    'crop': crop_name,
                    'extraction_method': 'rule_based',
                    'confidence': 0.9,  # High confidence for rule-based
                    'context': context,
                    'source_document': source_document,
                    'pattern_used': pattern
                }
                varieties.append(variety)
        
        return varieties
    
    def ai_fallback_extraction(self, text: str, crop_name: str, source_document: str, max_varieties: int = 10) -> List[Dict[str, Any]]:
        """
        Use AI extraction as fallback for complex cases
        Lower precision, but more comprehensive
        """
        try:
            # Prepare mock search result for AI parsing
            mock_search_result = [{
                'content': text,
                'source': source_document,
                'score': 1.0
            }]
            
            # Use existing AI parsing
            parsed_info = self.varieties_handler.parse_varieties_with_ai(
                mock_search_result, 
                crop_name, 
                max_varieties=max_varieties
            )
            
            varieties = []
            for variety in parsed_info.get('varieties', []):
                if variety.get('name'):
                    variety_data = {
                        'name': variety.get('name'),
                        'crop': crop_name,
                        'extraction_method': 'ai_fallback',
                        'confidence': 0.7,  # Medium confidence for AI
                        'context': text[:200] + "...",
                        'source_document': source_document,
                        'variety_type': variety.get('variety_type'),
                        'yield_potential': variety.get('yield_potential'),
                        'maturity_days': variety.get('maturity_days'),
                        'weather_requirements': variety.get('weather_requirements'),
                        'soil_requirements': variety.get('soil_requirements'),
                        'growing_areas': variety.get('growing_areas')
                    }
                    varieties.append(variety_data)
            
            return varieties
            
        except Exception as e:
            print(f"AI extraction error for {crop_name}: {e}")
            return []
    
    def validate_variety(self, variety: Dict[str, Any]) -> bool:
        """
        Validate extracted variety data
        """
        name = variety.get('name', '').strip()
        
        # Basic validation rules
        if not name or len(name) < 2:
            return False
        
        # Exclude generic terms
        generic_terms = [
            'variety', 'type', 'cultivar', 'hybrid', 'open pollinated', 
            'unknown', 'not specified', 'improved', 'local', 'traditional'
        ]
        
        if name.lower() in generic_terms:
            return False
        
        # Exclude very common words
        common_words = [
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'with', 'by', 'from', 'up', 'about', 'into', 'over', 'after'
        ]
        
        if name.lower() in common_words:
            return False
        
        return True
    
    def deduplicate_varieties(self, varieties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate varieties, preferring higher confidence extractions
        """
        unique_varieties = {}
        
        for variety in varieties:
            crop = variety.get('crop')
            name = variety.get('name', '').strip().lower()
            key = f"{crop}_{name}"
            
            if key not in unique_varieties:
                unique_varieties[key] = variety
            else:
                # Keep the one with higher confidence
                existing_confidence = unique_varieties[key].get('confidence', 0)
                new_confidence = variety.get('confidence', 0)
                
                if new_confidence > existing_confidence:
                    unique_varieties[key] = variety
        
        return list(unique_varieties.values())
    
    def extract_varieties_from_document(self, content: str, source_document: str, target_crops: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract varieties from a single document using the complete pipeline
        """
        if target_crops is None:
            target_crops = list(self.variety_patterns.keys())
        
        all_varieties = []
        extraction_stats = defaultdict(int)
        
        for crop_name in target_crops:
            print(f"  🔍 Extracting {crop_name} varieties...")
            
            # Step 1: Rule-based extraction (high precision)
            rule_varieties = self.rule_based_extraction(content, crop_name, source_document)
            extraction_stats[f'{crop_name}_rule_based'] = len(rule_varieties)
            all_varieties.extend(rule_varieties)
            
            # Step 2: AI fallback extraction (comprehensive coverage)
            # Only use AI if rule-based found few results
            if len(rule_varieties) < 3:
                ai_varieties = self.ai_fallback_extraction(content, crop_name, source_document)
                extraction_stats[f'{crop_name}_ai_fallback'] = len(ai_varieties)
                all_varieties.extend(ai_varieties)
            else:
                extraction_stats[f'{crop_name}_ai_fallback'] = 0
                print(f"    ℹ️  Skipped AI extraction (rule-based found {len(rule_varieties)} varieties)")
        
        # Step 3: Validation
        valid_varieties = [v for v in all_varieties if self.validate_variety(v)]
        extraction_stats['validation_passed'] = len(valid_varieties)
        extraction_stats['validation_failed'] = len(all_varieties) - len(valid_varieties)
        
        # Step 4: Deduplication
        final_varieties = self.deduplicate_varieties(valid_varieties)
        extraction_stats['final_unique'] = len(final_varieties)
        
        # Group by crop
        varieties_by_crop = defaultdict(list)
        for variety in final_varieties:
            varieties_by_crop[variety['crop']].append(variety)
        
        return {
            'varieties_by_crop': dict(varieties_by_crop),
            'extraction_stats': dict(extraction_stats),
            'total_varieties': len(final_varieties)
        }
    
    def extract_varieties_from_all_documents(self, target_crops: List[str] = None) -> Dict[str, Any]:
        """
        Extract varieties from all documents in the database
        """
        print(f"🔍 Starting variety extraction pipeline...")
        
        # Get all documents
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content, source FROM documents")
        documents = cursor.fetchall()
        conn.close()
        
        print(f"📚 Processing {len(documents)} documents")
        
        all_varieties_by_crop = defaultdict(list)
        total_stats = defaultdict(int)
        
        for doc_idx, (content, source) in enumerate(documents):
            print(f"\n📄 Document {doc_idx + 1}/{len(documents)}: {source}")
            
            # Extract from this document
            result = self.extract_varieties_from_document(content, source, target_crops)
            
            # Accumulate results
            for crop, varieties in result['varieties_by_crop'].items():
                all_varieties_by_crop[crop].extend(varieties)
            
            # Accumulate stats
            for key, value in result['extraction_stats'].items():
                total_stats[key] += value
            
            print(f"  📊 Found {result['total_varieties']} varieties")
        
        # Final deduplication across all documents
        final_varieties_by_crop = {}
        total_final_varieties = 0
        
        for crop, varieties in all_varieties_by_crop.items():
            deduplicated = self.deduplicate_varieties(varieties)
            final_varieties_by_crop[crop] = deduplicated
            total_final_varieties += len(deduplicated)
            print(f"  🌱 {crop}: {len(deduplicated)} unique varieties")
        
        return {
            'varieties_by_crop': final_varieties_by_crop,
            'extraction_stats': dict(total_stats),
            'total_varieties': total_final_varieties,
            'total_documents': len(documents)
        }

# Test function
def test_extraction_pipeline():
    """Test the variety extraction pipeline"""
    pipeline = VarietyExtractionPipeline()
    
    # Test with specific crops
    print("Testing variety extraction pipeline...")
    result = pipeline.extract_varieties_from_all_documents(['groundnut', 'maize'])
    
    print(f"\n📊 PIPELINE RESULTS:")
    print(f"Total varieties extracted: {result['total_varieties']}")
    print(f"Documents processed: {result['total_documents']}")
    
    print(f"\n🌱 Varieties by crop:")
    for crop, varieties in result['varieties_by_crop'].items():
        print(f"  - {crop}: {len(varieties)} varieties")
        for variety in varieties[:3]:  # Show first 3
            print(f"    • {variety['name']} (method: {variety['extraction_method']}, confidence: {variety['confidence']})")
    
    return result

if __name__ == "__main__":
    test_extraction_pipeline()
