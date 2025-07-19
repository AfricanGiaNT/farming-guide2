#!/usr/bin/env python3
"""
Specialized processor for 2025 National Agriculture Extension Policy
Extracts harvest advice, farm planning, and community knowledge information
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scripts.data_pipeline.pdf_processor import PDFProcessor
from scripts.data_pipeline.text_chunker import TextChunker
from scripts.utils.logger import logger


class ExtensionPolicyProcessor:
    """
    Specialized processor for the 2025 National Agriculture Extension Policy
    Extracts structured information for harvest advice, farm planning, and community knowledge
    """
    
    def __init__(self):
        """Initialize the extension policy processor."""
        self.pdf_processor = PDFProcessor()
        self.text_chunker = TextChunker(chunk_size=800, overlap=100)
        
        # Define key sections to extract
        self.harvest_sections = [
            'harvest', 'post-harvest', 'storage', 'drying', 'processing',
            'value addition', 'market preparation', 'quality standards'
        ]
        
        self.planning_sections = [
            'farm planning', 'crop rotation', 'resource allocation',
            'seasonal planning', 'land management', 'irrigation planning'
        ]
        
        self.community_sections = [
            'extension services', 'farmer groups', 'knowledge sharing',
            'community participation', 'local knowledge', 'success stories'
        ]
        
        self.predictive_sections = [
            'climate adaptation', 'yield prediction', 'risk assessment',
            'long-term planning', 'trends analysis', 'forecasting'
        ]
        
        logger.info("ExtensionPolicyProcessor initialized")
    
    def process_extension_policy(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process the 2025 National Agriculture Extension Policy document.
        
        Args:
            pdf_path: Path to the PDF document
            
        Returns:
            Dictionary with extracted structured information
        """
        try:
            logger.info(f"Processing extension policy: {pdf_path}")
            
            # Extract text from PDF
            text = self.pdf_processor.extract_text_from_pdf(pdf_path)
            if not text:
                raise ValueError("No text extracted from PDF")
            
            logger.info(f"Extracted {len(text):,} characters from extension policy")
            
            # Extract structured information
            extracted_data = {
                'document_info': self._extract_document_info(pdf_path, text),
                'harvest_advice': self._extract_harvest_advice(text),
                'farm_planning': self._extract_farm_planning(text),
                'community_knowledge': self._extract_community_knowledge(text),
                'predictive_insights': self._extract_predictive_insights(text),
                'processed_date': datetime.now().isoformat()
            }
            
            # Create specialized chunks for vector database
            chunks = self._create_specialized_chunks(text, extracted_data)
            extracted_data['chunks'] = chunks
            
            logger.info(f"Successfully processed extension policy with {len(chunks)} chunks")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error processing extension policy: {str(e)}")
            raise
    
    def _extract_document_info(self, pdf_path: str, text: str) -> Dict[str, Any]:
        """Extract basic document information."""
        return {
            'filename': os.path.basename(pdf_path),
            'file_size': os.path.getsize(pdf_path),
            'text_length': len(text),
            'document_type': 'national_extension_policy',
            'year': '2025',
            'country': 'Malawi',
            'language': 'English'
        }
    
    def _extract_harvest_advice(self, text: str) -> Dict[str, Any]:
        """Extract harvest and post-harvest advice information."""
        harvest_info = {
            'optimal_harvest_timing': [],
            'drying_recommendations': [],
            'storage_guidelines': [],
            'post_harvest_loss_prevention': [],
            'quality_standards': [],
            'market_preparation': []
        }
        
        # Extract harvest timing information
        harvest_patterns = [
            r'harvest.*timing.*?[.!]',
            r'optimal.*harvest.*?[.!]',
            r'when.*harvest.*?[.!]',
            r'harvest.*season.*?[.!]'
        ]
        
        for pattern in harvest_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            harvest_info['optimal_harvest_timing'].extend(matches)
        
        # Extract drying recommendations
        drying_patterns = [
            r'drying.*?[.!]',
            r'sun.*dry.*?[.!]',
            r'artificial.*dry.*?[.!]',
            r'moisture.*content.*?[.!]'
        ]
        
        for pattern in drying_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            harvest_info['drying_recommendations'].extend(matches)
        
        # Extract storage guidelines
        storage_patterns = [
            r'storage.*?[.!]',
            r'warehouse.*?[.!]',
            r'preservation.*?[.!]',
            r'container.*?[.!]'
        ]
        
        for pattern in storage_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            harvest_info['storage_guidelines'].extend(matches)
        
        # Clean and deduplicate results
        for key in harvest_info:
            harvest_info[key] = list(set([item.strip() for item in harvest_info[key] if len(item.strip()) > 20]))
        
        return harvest_info
    
    def _extract_farm_planning(self, text: str) -> Dict[str, Any]:
        """Extract farm planning and resource allocation information."""
        planning_info = {
            'crop_rotation_guidelines': [],
            'resource_allocation': [],
            'seasonal_planning': [],
            'land_management': [],
            'irrigation_planning': []
        }
        
        # Extract crop rotation information
        rotation_patterns = [
            r'crop.*rotation.*?[.!]',
            r'rotation.*plan.*?[.!]',
            r'intercropping.*?[.!]',
            r'crop.*sequence.*?[.!]'
        ]
        
        for pattern in rotation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            planning_info['crop_rotation_guidelines'].extend(matches)
        
        # Extract resource allocation
        resource_patterns = [
            r'resource.*allocation.*?[.!]',
            r'land.*use.*?[.!]',
            r'labor.*planning.*?[.!]',
            r'input.*management.*?[.!]'
        ]
        
        for pattern in resource_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            planning_info['resource_allocation'].extend(matches)
        
        # Clean and deduplicate results
        for key in planning_info:
            planning_info[key] = list(set([item.strip() for item in planning_info[key] if len(item.strip()) > 20]))
        
        return planning_info
    
    def _extract_community_knowledge(self, text: str) -> Dict[str, Any]:
        """Extract community knowledge sharing and extension information."""
        community_info = {
            'extension_services': [],
            'farmer_groups': [],
            'knowledge_sharing': [],
            'local_practices': [],
            'success_stories': []
        }
        
        # Extract extension services information
        extension_patterns = [
            r'extension.*service.*?[.!]',
            r'advisory.*service.*?[.!]',
            r'farmer.*education.*?[.!]',
            r'training.*program.*?[.!]'
        ]
        
        for pattern in extension_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            community_info['extension_services'].extend(matches)
        
        # Extract farmer groups information
        groups_patterns = [
            r'farmer.*group.*?[.!]',
            r'cooperative.*?[.!]',
            r'association.*?[.!]',
            r'community.*organization.*?[.!]'
        ]
        
        for pattern in groups_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            community_info['farmer_groups'].extend(matches)
        
        # Clean and deduplicate results
        for key in community_info:
            community_info[key] = list(set([item.strip() for item in community_info[key] if len(item.strip()) > 20]))
        
        return community_info
    
    def _extract_predictive_insights(self, text: str) -> Dict[str, Any]:
        """Extract predictive analytics and climate adaptation information."""
        predictive_info = {
            'climate_adaptation': [],
            'yield_prediction': [],
            'risk_assessment': [],
            'long_term_planning': [],
            'trends_analysis': []
        }
        
        # Extract climate adaptation information
        climate_patterns = [
            r'climate.*adaptation.*?[.!]',
            r'climate.*change.*?[.!]',
            r'weather.*pattern.*?[.!]',
            r'seasonal.*variation.*?[.!]'
        ]
        
        for pattern in climate_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            predictive_info['climate_adaptation'].extend(matches)
        
        # Extract yield prediction information
        yield_patterns = [
            r'yield.*prediction.*?[.!]',
            r'production.*forecast.*?[.!]',
            r'expected.*yield.*?[.!]',
            r'productivity.*projection.*?[.!]'
        ]
        
        for pattern in yield_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            predictive_info['yield_prediction'].extend(matches)
        
        # Clean and deduplicate results
        for key in predictive_info:
            predictive_info[key] = list(set([item.strip() for item in predictive_info[key] if len(item.strip()) > 20]))
        
        return predictive_info
    
    def _create_specialized_chunks(self, text: str, extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create specialized chunks for vector database with enhanced metadata."""
        # Create regular chunks first
        metadata = {
            'source_document': '2025_National_Agriculture_Extension_Policy',
            'document_type': 'national_extension_policy',
            'year': '2025',
            'country': 'Malawi',
            'processed_date': datetime.now().isoformat()
        }
        
        chunks = self.text_chunker.chunk_text(text, metadata)
        
        # Enhance chunks with specialized categorization
        enhanced_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_text = chunk.get('text', '')
            
            # Determine chunk category based on content
            category = self._categorize_chunk(chunk_text)
            
            # Add specialized metadata
            enhanced_chunk = {
                **chunk,
                'chunk_id': f"extension_policy_{i:04d}",
                'category': category,
                'specialized_content': self._extract_specialized_content(chunk_text, category),
                'relevance_score': self._calculate_relevance_score(chunk_text, category)
            }
            
            enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks
    
    def _categorize_chunk(self, text: str) -> str:
        """Categorize chunk based on content keywords."""
        text_lower = text.lower()
        
        # Check for harvest-related content
        harvest_keywords = ['harvest', 'post-harvest', 'storage', 'drying', 'processing']
        if any(keyword in text_lower for keyword in harvest_keywords):
            return 'harvest_advice'
        
        # Check for planning-related content
        planning_keywords = ['planning', 'rotation', 'allocation', 'management', 'irrigation']
        if any(keyword in text_lower for keyword in planning_keywords):
            return 'farm_planning'
        
        # Check for community-related content
        community_keywords = ['extension', 'farmer', 'community', 'group', 'knowledge']
        if any(keyword in text_lower for keyword in community_keywords):
            return 'community_knowledge'
        
        # Check for predictive content
        predictive_keywords = ['climate', 'prediction', 'forecast', 'trend', 'adaptation']
        if any(keyword in text_lower for keyword in predictive_keywords):
            return 'predictive_analytics'
        
        return 'general_agriculture'
    
    def _extract_specialized_content(self, text: str, category: str) -> Dict[str, Any]:
        """Extract specialized content based on category."""
        specialized_content = {}
        
        if category == 'harvest_advice':
            # Extract timing information
            timing_matches = re.findall(r'(\d+)\s*(days?|weeks?|months?)\s*(?:after|before|during)', text, re.IGNORECASE)
            if timing_matches:
                specialized_content['timing_info'] = timing_matches
            
            # Extract moisture content
            moisture_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%?\s*moisture', text, re.IGNORECASE)
            if moisture_matches:
                specialized_content['moisture_content'] = moisture_matches
        
        elif category == 'farm_planning':
            # Extract crop names
            crop_matches = re.findall(r'\b(maize|beans|groundnuts?|soybeans?|sorghum|millet)\b', text, re.IGNORECASE)
            if crop_matches:
                specialized_content['crops_mentioned'] = list(set(crop_matches))
            
            # Extract time periods
            time_matches = re.findall(r'\b(season|month|year|period)\b', text, re.IGNORECASE)
            if time_matches:
                specialized_content['time_references'] = list(set(time_matches))
        
        elif category == 'community_knowledge':
            # Extract group sizes
            size_matches = re.findall(r'(\d+)\s*(?:farmers?|members?|participants?)', text, re.IGNORECASE)
            if size_matches:
                specialized_content['group_sizes'] = size_matches
            
            # Extract location references
            location_matches = re.findall(r'\b(district|village|area|region)\b', text, re.IGNORECASE)
            if location_matches:
                specialized_content['location_references'] = list(set(location_matches))
        
        return specialized_content
    
    def _calculate_relevance_score(self, text: str, category: str) -> float:
        """Calculate relevance score for chunk based on category and content."""
        base_score = 0.5
        
        # Add score based on category-specific keywords
        if category == 'harvest_advice':
            harvest_keywords = ['harvest', 'post-harvest', 'storage', 'drying', 'processing', 'moisture']
            keyword_count = sum(1 for keyword in harvest_keywords if keyword in text.lower())
            base_score += min(keyword_count * 0.1, 0.3)
        
        elif category == 'farm_planning':
            planning_keywords = ['planning', 'rotation', 'allocation', 'management', 'irrigation', 'seasonal']
            keyword_count = sum(1 for keyword in planning_keywords if keyword in text.lower())
            base_score += min(keyword_count * 0.1, 0.3)
        
        elif category == 'community_knowledge':
            community_keywords = ['extension', 'farmer', 'community', 'group', 'knowledge', 'training']
            keyword_count = sum(1 for keyword in community_keywords if keyword in text.lower())
            base_score += min(keyword_count * 0.1, 0.3)
        
        elif category == 'predictive_analytics':
            predictive_keywords = ['climate', 'prediction', 'forecast', 'trend', 'adaptation', 'risk']
            keyword_count = sum(1 for keyword in predictive_keywords if keyword in text.lower())
            base_score += min(keyword_count * 0.1, 0.3)
        
        # Add score based on text length (prefer substantial content)
        if len(text) > 100:
            base_score += 0.1
        if len(text) > 200:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def save_extracted_data(self, extracted_data: Dict[str, Any], output_path: str) -> bool:
        """Save extracted data to JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved extracted data to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving extracted data: {str(e)}")
            return False


def main():
    """Main function to process the extension policy document."""
    processor = ExtensionPolicyProcessor()
    
    # Path to the extension policy PDF
    pdf_path = "data/pdfs/2025 NATIONAL AGRICULTURE EXTENSION AND ADVISORY SERVICES POLICY Final.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    try:
        print(f"🔄 Processing extension policy document...")
        
        # Process the document
        extracted_data = processor.process_extension_policy(pdf_path)
        
        # Save extracted data
        output_path = "data/extension_policy_extracted.json"
        if processor.save_extracted_data(extracted_data, output_path):
            print(f"✅ Successfully processed extension policy")
            print(f"📊 Extracted {len(extracted_data.get('chunks', []))} specialized chunks")
            print(f"💾 Data saved to {output_path}")
            
            # Print summary
            print(f"\n📋 Extraction Summary:")
            print(f"   Harvest Advice: {len(extracted_data['harvest_advice']['optimal_harvest_timing'])} items")
            print(f"   Farm Planning: {len(extracted_data['farm_planning']['crop_rotation_guidelines'])} items")
            print(f"   Community Knowledge: {len(extracted_data['community_knowledge']['extension_services'])} items")
            print(f"   Predictive Insights: {len(extracted_data['predictive_insights']['climate_adaptation'])} items")
            
            return True
        else:
            print(f"❌ Failed to save extracted data")
            return False
            
    except Exception as e:
        print(f"❌ Error processing extension policy: {str(e)}")
        return False


if __name__ == "__main__":
    main() 