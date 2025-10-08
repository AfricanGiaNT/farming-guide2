#!/usr/bin/env python3
"""
Malawi-Specific Variety Data Extraction Pipeline
Enhanced to identify varieties suitable for Malawi and filter by crop relevance
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

class MalawiVarietyExtractionPipeline:
    """Enhanced pipeline for extracting Malawi-specific variety data"""
    
    def __init__(self, db_path: str = "data/agricultural_documents.db"):
        self.db_path = db_path
        if not os.path.isabs(self.db_path):
            self.db_path = os.path.join(project_root, self.db_path)
        
        # Initialize AI handler for fallback
        self.varieties_handler = VarietiesHandler()
        
        # Malawi-specific variety patterns and context
        self.malawi_variety_patterns = {
            'maize': {
                'patterns': [
                    r'\b(SC\s*\d+[A-Z]*)\b',  # SC 301, SC403, SC719, etc.
                    r'\b(PAN\s*\d+[A-Z]*)\b',  # PAN 12, PAN53, etc.
                    r'\b(MH\s*\d+[A-Z]*)\b',  # MH 18, MH26, etc.
                    r'\b(ZM\s*\d+)\b',  # ZM 309, etc.
                    r'\b(DK\s*\d+)\b',  # DK varieties
                    r'\b(Chitedze\s*\d*)\b',  # Chitedze varieties
                    r'\b(Chitala|Kakoma|Baka)\b'  # Common Malawi names
                ],
                'context_keywords': [
                    'maize', 'corn', 'hybrid', 'malawi', 'chitedze', 
                    'seed co', 'panar', 'mh', 'zm', 'dk'
                ],
                'malawi_indicators': [
                    'malawi', 'chitedze', 'seed co', 'panar', 'mh', 'zm', 'dk',
                    'lilongwe', 'blantyre', 'mzuzu', 'zomba', 'kasungu'
                ]
            },
            'groundnut': {
                'patterns': [
                    r'\b(CG\s*\d+)\b',  # CG 7, CG8, etc.
                    r'\b(Chalimbana\s*\d*)\b',  # Chalimbana 2005
                    r'\b(Nsinjiro|Kakoma|Chitala|Baka)\b',
                    r'\b(ICGV-SM\s*\d+)\b'  # ICGV-SM codes
                ],
                'context_keywords': [
                    'groundnut', 'peanut', 'virginia', 'spanish', 'malawi',
                    'confectionery', 'oil', 'cg', 'chalimbana', 'nsinjiro'
                ],
                'malawi_indicators': [
                    'malawi', 'cg', 'chalimbana', 'nsinjiro', 'icgv-sm',
                    'virginia', 'spanish', 'confectionery'
                ]
            },
            'soybean': {
                'patterns': [
                    r'\b(SB\s*\d+)\b',  # SB varieties
                    r'\b(TGx\s*\d+)\b',  # TGx varieties
                    r'\b(Makwacha|Nasaka|Baka)\b'
                ],
                'context_keywords': [
                    'soybean', 'soya', 'malawi', 'sb', 'tgx', 'makwacha', 'nasaka'
                ],
                'malawi_indicators': [
                    'malawi', 'sb', 'tgx', 'makwacha', 'nasaka', 'baka'
                ]
            },
            'rice': {
                'patterns': [
                    r'\b(IR\s*\d+)\b',  # IR varieties
                    r'\b(NERICA\s*\d+)\b',  # NERICA varieties
                    r'\b(Faya|Kilombero|Baka)\b'
                ],
                'context_keywords': [
                    'rice', 'paddy', 'malawi', 'ir', 'nerica', 'faya', 'kilombero'
                ],
                'malawi_indicators': [
                    'malawi', 'ir', 'nerica', 'faya', 'kilombero', 'baka'
                ]
            },
            'cassava': {
                'patterns': [
                    r'\b(Sauti|Mkondezi|Baka)\b',
                    r'\b(Chitembwere|Mkondezi)\b'
                ],
                'context_keywords': [
                    'cassava', 'malawi', 'sauti', 'mkondezi', 'chitembwere'
                ],
                'malawi_indicators': [
                    'malawi', 'sauti', 'mkondezi', 'chitembwere', 'baka'
                ]
            },
            'tomato': {
                'patterns': [
                    r'\b(Roma|Money Maker|Baka)\b',
                    r'\b(Heinz|Ponderosa)\b'
                ],
                'context_keywords': [
                    'tomato', 'malawi', 'roma', 'money maker', 'heinz', 'ponderosa'
                ],
                'malawi_indicators': [
                    'malawi', 'roma', 'money maker', 'heinz', 'ponderosa', 'baka'
                ]
            }
        }
        
        # Common Malawi agricultural terms and locations
        self.malawi_terms = [
            'malawi', 'lilongwe', 'blantyre', 'mzuzu', 'zomba', 'kasungu',
            'chitedze', 'bunda', 'makoka', 'chitedze research station',
            'ministry of agriculture', 'malawi government', 'agriculture extension'
        ]
        
        # Crop-specific context validation
        self.crop_context_validation = {
            'maize': ['grain', 'cereal', 'staple', 'food security', 'hybrid', 'open pollinated'],
            'groundnut': ['legume', 'oil', 'confectionery', 'nitrogen fixation', 'rotation'],
            'soybean': ['legume', 'protein', 'oil', 'nitrogen fixation', 'rotation'],
            'rice': ['paddy', 'irrigated', 'upland', 'lowland', 'cereal'],
            'cassava': ['tuber', 'root crop', 'staple', 'drought tolerant'],
            'tomato': ['vegetable', 'horticulture', 'fresh market', 'processing']
        }

    def is_malawi_relevant(self, text: str, crop: str) -> bool:
        """Check if text contains Malawi-specific indicators for the given crop"""
        text_lower = text.lower()
        
        # Check for general Malawi indicators
        malawi_indicators = self.malawi_variety_patterns.get(crop, {}).get('malawi_indicators', [])
        if any(indicator in text_lower for indicator in malawi_indicators):
            return True
        
        # Check for general Malawi terms
        if any(term in text_lower for term in self.malawi_terms):
            return True
        
        # Check for crop-specific context
        crop_context = self.crop_context_validation.get(crop, [])
        if any(context in text_lower for context in crop_context):
            return True
        
        return False

    def extract_varieties_with_context(self, content: str, crop: str, source_document: str) -> List[Dict[str, Any]]:
        """Extract varieties with enhanced context validation"""
        patterns = self.malawi_variety_patterns.get(crop, {}).get('patterns', [])
        context_keywords = self.malawi_variety_patterns.get(crop, {}).get('context_keywords', [])
        
        varieties = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                variety_name = match.group(1).strip()
                
                # Get context around the match
                start = max(0, match.start() - 200)
                end = min(len(content), match.end() + 200)
                context = content[start:end]
                
                # Check if context is Malawi-relevant
                if not self.is_malawi_relevant(context, crop):
                    continue
                
                # Check if context contains crop-specific keywords
                context_lower = context.lower()
                if not any(keyword in context_lower for keyword in context_keywords):
                    continue
                
                # Extract additional information from context
                variety_info = self.extract_variety_info_from_context(context, variety_name, crop)
                
                varieties.append({
                    'variety_name': variety_name,
                    'crop_name': crop,
                    'source_document': source_document,
                    'context': context,
                    **variety_info
                })
        
        return varieties

    def extract_variety_info_from_context(self, context: str, variety_name: str, crop: str) -> Dict[str, Any]:
        """Extract additional variety information from context"""
        info = {
            'variety_type': 'Not specified',
            'yield_potential': 'Not specified',
            'maturity_days': None,
            'weather_requirements': 'Not specified',
            'soil_requirements': 'Not specified',
            'growing_areas': 'Not specified',
            'disease_resistance': 'Not specified',
            'planting_time': 'Not specified'
        }
        
        context_lower = context.lower()
        
        # Extract variety type
        if crop == 'groundnut':
            if 'virginia' in context_lower:
                info['variety_type'] = 'Virginia'
            elif 'spanish' in context_lower:
                info['variety_type'] = 'Spanish'
        
        # Extract maturity days
        maturity_match = re.search(r'(\d+)\s*to\s*(\d+)\s*days?', context_lower)
        if maturity_match:
            days = int(maturity_match.group(1))
            info['maturity_days'] = days
        else:
            maturity_match = re.search(r'(\d+)\s*days?', context_lower)
            if maturity_match:
                info['maturity_days'] = int(maturity_match.group(1))
        
        # Extract yield potential
        yield_match = re.search(r'(\d+(?:,\d+)*)\s*kg\s*(?:per\s*hectare|ha)', context_lower)
        if yield_match:
            info['yield_potential'] = f"{yield_match.group(1)} kg/ha"
        
        # Extract growing areas
        if 'all' in context_lower and ('area' in context_lower or 'region' in context_lower):
            info['growing_areas'] = 'All growing areas of Malawi'
        elif 'plateau' in context_lower:
            info['growing_areas'] = 'Plateau areas of Malawi'
        elif 'lowland' in context_lower:
            info['growing_areas'] = 'Lowland areas of Malawi'
        
        # Extract soil requirements
        if 'well-drained' in context_lower:
            info['soil_requirements'] = 'Well-drained soils'
        elif 'clay' in context_lower:
            info['soil_requirements'] = 'Clay soils'
        elif 'sandy' in context_lower:
            info['soil_requirements'] = 'Sandy soils'
        
        # Extract planting time
        if 'december' in context_lower and 'january' in context_lower:
            info['planting_time'] = 'December-January'
        elif 'november' in context_lower:
            info['planting_time'] = 'November'
        elif 'october' in context_lower:
            info['planting_time'] = 'October'
        
        # Extract disease resistance
        if 'drought' in context_lower and 'tolerant' in context_lower:
            info['disease_resistance'] = 'Drought tolerant'
        elif 'rosette' in context_lower and 'tolerant' in context_lower:
            info['disease_resistance'] = 'Groundnut rosette tolerant'
        
        return info

    def ai_fallback_extraction(self, content: str, crop: str, source_document: str) -> List[Dict[str, Any]]:
        """AI fallback extraction with Malawi-specific filtering"""
        try:
            # Use the existing AI handler but with enhanced prompting
            prompt = f"""
            Extract ONLY varieties that are specifically mentioned as suitable for Malawi agriculture for {crop}.
            Focus on varieties that are:
            1. Recommended for Malawi
            2. Commonly grown in Malawi
            3. Mentioned in the context of Malawi agriculture
            4. From recognized seed companies in Malawi (Seed Co, PANAR, etc.)
            
            Document content: {content[:2000]}...
            
            Return only varieties that are clearly Malawi-specific for {crop}.
            """
            
            # This would use the existing AI handler but with enhanced filtering
            # For now, return empty list as we're focusing on rule-based extraction
            return []
            
        except Exception as e:
            print(f"AI extraction failed: {e}")
            return []

    def extract_varieties_from_document(self, content: str, source_document: str, target_crops: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Extract Malawi-specific varieties from a single document"""
        if target_crops is None:
            target_crops = list(self.malawi_variety_patterns.keys())
        
        all_varieties = []
        extraction_stats = defaultdict(int)
        
        for crop_name in target_crops:
            print(f"  🔍 Extracting {crop_name} varieties (Malawi-specific)...")
            
            # Rule-based extraction with Malawi filtering
            rule_varieties = self.extract_varieties_with_context(content, crop_name, source_document)
            
            # Limit varieties per document to prevent over-extraction
            max_varieties_per_document = 10
            if len(rule_varieties) > max_varieties_per_document:
                print(f"    ⚠️  Limiting to {max_varieties_per_document} varieties from this document")
                rule_varieties = rule_varieties[:max_varieties_per_document]
            
            extraction_stats[f'{crop_name}_rule_based'] = len(rule_varieties)
            all_varieties.extend(rule_varieties)
            
            # AI fallback only if rule-based found very few results
            if len(rule_varieties) < 1:
                ai_varieties = self.ai_fallback_extraction(content, crop_name, source_document)
                extraction_stats[f'{crop_name}_ai_fallback'] = len(ai_varieties)
                all_varieties.extend(ai_varieties)
            else:
                extraction_stats[f'{crop_name}_ai_fallback'] = 0
                print(f"    ℹ️  Skipped AI extraction (rule-based found {len(rule_varieties)} varieties)")
        
        # Validation and deduplication
        valid_varieties = [v for v in all_varieties if self.validate_variety(v)]
        extraction_stats['validation_passed'] = len(valid_varieties)
        extraction_stats['validation_failed'] = len(all_varieties) - len(valid_varieties)
        
        # Deduplicate
        final_varieties = self.deduplicate_varieties(valid_varieties)
        extraction_stats['final_unique'] = len(final_varieties)

        for variety in final_varieties:
            self.calculate_confidence_score(variety)

        # Group by crop
        varieties_by_crop = defaultdict(list)
        for variety in final_varieties:
            varieties_by_crop[variety['crop_name']].append(variety)
        
        return {
            'varieties_by_crop': dict(varieties_by_crop),
            'extraction_stats': dict(extraction_stats),
            'total_varieties': len(final_varieties)
        }

    def validate_variety(self, variety: Dict[str, Any]) -> bool:
        """Validate variety data with stricter criteria"""
        required_fields = ['variety_name', 'crop_name', 'source_document']
        
        # Check required fields
        if not all(field in variety and variety[field] for field in required_fields):
            return False
        
        variety_name = variety['variety_name'].strip()
        
        # Reject empty or very short names
        if len(variety_name) < 2:
            return False
        
        # Reject generic terms
        generic_terms = ['variety', 'type', 'cultivar', 'strain', 'line', 'baka', 'unknown']
        if variety_name.lower() in generic_terms:
            return False
        
        # Reject names that are just numbers
        if variety_name.isdigit():
            return False
        
        # Reject names that are too generic (like just "CG" or "SC")
        if len(variety_name) <= 3 and variety_name.isalpha():
            return False
        
        return True

    def deduplicate_varieties(self, varieties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate varieties with improved normalization"""
        unique_varieties = {}
        
        for variety in varieties:
            # Normalize variety name (remove extra spaces, standardize format)
            normalized_name = self.normalize_variety_name(variety['variety_name'])
            
            # Create a more robust key that ignores source document for true deduplication
            key = f"{normalized_name.lower()}_{variety['crop_name']}"
            
            if key not in unique_varieties:
                # Keep the variety with the most complete information
                variety['variety_name'] = normalized_name
                unique_varieties[key] = variety
            else:
                # Merge information if the new variety has more complete data
                existing = unique_varieties[key]
                if self.is_more_complete(variety, existing):
                    variety['variety_name'] = normalized_name
                    unique_varieties[key] = variety
        
        return list(unique_varieties.values())
    
    def normalize_variety_name(self, name: str) -> str:
        """Normalize variety name to handle variations like 'SC 403' vs 'SC403'"""
        if not name:
            return name

        # Remove extra spaces and standardize spacing
        normalized = re.sub(r'\s+', ' ', name.strip())
        
        # Standardize common patterns
        # SC 403 -> SC403, MH 18 -> MH18, etc.
        normalized = re.sub(r'\b([A-Z]{2})\s+(\d+)', r'\1\2', normalized)
        
        # ZM 309 -> ZM309, DK 123 -> DK123, etc.
        normalized = re.sub(r'\b([A-Z]{2})\s+(\d+)', r'\1\2', normalized)
        
        return normalized

    def _value_is_present(self, value: Any) -> bool:
        """Check if a value contains meaningful information."""
        if value is None:
            return False
        if isinstance(value, str):
            normalized = value.strip().lower()
            return bool(normalized) and normalized not in {'not specified', 'unknown', 'n/a'}
        return True

    def calculate_confidence_score(self, variety: Dict[str, Any]) -> int:
        """Calculate a 0-100 confidence score for an extracted variety."""
        completeness_fields = [
            'variety_type',
            'yield_potential',
            'maturity_days',
            'weather_requirements',
            'soil_requirements',
            'growing_areas',
            'disease_resistance',
            'planting_time'
        ]

        filled_fields = sum(1 for field in completeness_fields if self._value_is_present(variety.get(field)))
        completeness_score = (filled_fields / len(completeness_fields)) * 40 if completeness_fields else 0

        source_score = 0
        source = (variety.get('source_document') or '').lower()
        if source:
            high_quality_keywords = ['gov', 'ministry', 'department', 'agriculture', 'research', 'pdf']
            medium_quality_keywords = ['extension', 'training', 'manual', 'guide']
            if any(keyword in source for keyword in high_quality_keywords):
                source_score = 30
            elif any(keyword in source for keyword in medium_quality_keywords):
                source_score = 20
            else:
                source_score = 10

        pattern_score = 0
        crop = (variety.get('crop_name') or variety.get('crop') or '').lower()
        name = variety.get('variety_name') or ''
        patterns = self.malawi_variety_patterns.get(crop, {}).get('patterns', [])
        if name and patterns:
            if any(re.search(pattern, name, re.IGNORECASE) for pattern in patterns):
                pattern_score = 20
        if pattern_score == 0 and name:
            if re.search(r'\b[A-Z]{2,}\s*\d+', name):
                pattern_score = 15
            elif len(name) > 3:
                pattern_score = 10

        context_score = 0
        context = variety.get('context') or ''
        if context:
            context_score = 10 if self.is_malawi_relevant(context, crop) else 5

        total_score = int(round(min(100, completeness_score + source_score + pattern_score + context_score)))
        variety['confidence_score'] = total_score
        return total_score
    
    def is_more_complete(self, new_variety: Dict[str, Any], existing_variety: Dict[str, Any]) -> bool:
        """Check if new variety has more complete information than existing"""
        new_fields = sum(1 for v in new_variety.values() if v and v != 'Not specified')
        existing_fields = sum(1 for v in existing_variety.values() if v and v != 'Not specified')
        return new_fields > existing_fields

    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
