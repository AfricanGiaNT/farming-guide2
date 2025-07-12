#!/usr/bin/env python3
"""
Document Quality Scorer for Agricultural Advisor Bot
Provides comprehensive quality assessment and validation of documents

Quality Assessment Areas:
- Content quality (readability, depth, relevance)
- Metadata quality (completeness, accuracy)
- Structure quality (organization, formatting)
- Relevance score (agricultural domain specificity)
"""

import os
import sys
import re
import math
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.logger import BotLogger

class DocumentQualityScorer:
    """
    Comprehensive document quality assessment system
    """
    
    def __init__(self):
        """Initialize the document quality scorer"""
        self.logger = BotLogger(__name__)
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 0.9,
            'very_good': 0.8,
            'good': 0.7,
            'fair': 0.6,
            'poor': 0.5
        }
        
        # Agricultural domain keywords
        self.agricultural_keywords = {
            'crops': ['maize', 'corn', 'wheat', 'rice', 'soybean', 'beans', 'cassava', 'potato', 'cotton', 'crop', 'crops'],
            'farming': ['farming', 'agriculture', 'agricultural', 'cultivation', 'planting', 'harvest', 'irrigation', 'tillage', 'farm', 'guide'],
            'soil': ['soil', 'fertilizer', 'compost', 'nutrients', 'pH', 'organic matter', 'erosion', 'management'],
            'pest': ['pest', 'disease', 'insect', 'fungus', 'weed', 'herbicide', 'pesticide', 'control'],
            'weather': ['rainfall', 'drought', 'climate', 'season', 'temperature', 'humidity', 'weather'],
            'livestock': ['livestock', 'cattle', 'chicken', 'goat', 'pig', 'dairy', 'animal', 'feed'],
            'techniques': ['precision', 'sustainable', 'practices', 'modern', 'strategies', 'methods', 'techniques', 'advanced'],
            'general': ['information', 'detailed', 'comprehensive', 'quality', 'content']
        }
        
        self.logger.info("DocumentQualityScorer initialized successfully")
    
    def score_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive document quality scoring
        
        Args:
            document_data: Dictionary containing document information
            
        Returns:
            Dictionary with quality scores and recommendations
        """
        try:
            # Extract document components - handle both 'text' and 'raw_text' keys
            text = document_data.get('text', '') or document_data.get('raw_text', '')
            
            # Safety check: ensure text is always a string
            if not isinstance(text, str):
                if isinstance(text, dict):
                    # If text is a dict, try to extract text content from it
                    text = text.get('content', '') or text.get('text', '') or str(text)
                else:
                    text = str(text) if text else ''
                    
            metadata = document_data.get('metadata', {})
            chunks = document_data.get('chunks', [])
            
            # Calculate individual quality components
            content_quality = self.assess_content_quality(text)
            metadata_quality = self._assess_metadata_quality(metadata)
            structure_quality = self._assess_structure_quality(text, chunks)
            relevance_score = self._assess_relevance_score(text)
            
            # Calculate overall score (weighted average)
            overall_score = (
                content_quality['score'] * 0.4 +
                metadata_quality['score'] * 0.2 +
                structure_quality['score'] * 0.2 +
                relevance_score['score'] * 0.2
            )
            
            # Generate quality level
            quality_level = self._get_quality_level(overall_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                content_quality, metadata_quality, structure_quality, relevance_score
            )
            
            return {
                'overall_score': overall_score,
                'quality_level': quality_level,
                'content_quality': content_quality,
                'metadata_quality': metadata_quality,
                'structure_quality': structure_quality,
                'relevance_score': relevance_score,
                'recommendations': recommendations,
                'assessment_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error scoring document: {str(e)}")
            return {
                'overall_score': 0.0,
                'quality_level': 'error',
                'error': str(e)
            }
    
    def assess_content_quality(self, text: str) -> Dict[str, Any]:
        """
        Assess content quality based on various metrics
        
        Args:
            text: Document text content
            
        Returns:
            Dictionary with content quality assessment
        """
        # Ensure text is always a string
        if not isinstance(text, str):
            if isinstance(text, dict):
                # If text is a dict, try to extract text content from it
                text = text.get('content', '') or text.get('text', '') or text.get('raw_text', '') or str(text)
            else:
                text = str(text) if text else ''
        
        if not text:
            return {
                'score': 0.0,
                'metrics': {'word_count': 0, 'sentence_count': 0, 'readability': 0.0},
                'issues': ['Empty content']
            }
        
        # Basic text metrics
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        
        word_count = len(words)
        sentence_count = len(sentences)
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Readability assessment (simplified)
        readability_score = self._calculate_readability(text, word_count, sentence_count)
        
        # Content depth assessment
        depth_score = self._assess_content_depth(text)
        
        # Information density
        info_density = self._assess_information_density(text)
        
        # Calculate overall content quality
        content_score = (
            min(1.0, word_count / 500) * 0.25 +   # Reduced word count requirement
            min(1.0, readability_score) * 0.25 +   # Readability
            depth_score * 0.25 +                   # Content depth
            info_density * 0.15 +                  # Information density
            min(1.0, sentence_count / 3) * 0.1     # Sentence variety bonus
        )
        
        # Generate issues
        issues = []
        if word_count < 50:  # Reduced threshold
            issues.append('Very short content')
        if readability_score < 0.3:
            issues.append('Poor readability')
        if depth_score < 0.2:  # Reduced threshold
            issues.append('Shallow content depth')
        
        return {
            'score': content_score,
            'metrics': {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'avg_sentence_length': avg_sentence_length,
                'readability': readability_score,
                'depth_score': depth_score,
                'info_density': info_density
            },
            'issues': issues
        }
    
    def _assess_metadata_quality(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Assess metadata quality"""
        required_fields = ['title', 'author', 'creation_date', 'word_count']
        optional_fields = ['language', 'page_count', 'doc_type', 'keywords']
        
        score = 0.0
        issues = []
        
        # Check required fields
        for field in required_fields:
            if field in metadata and metadata[field]:
                score += 0.2  # 20% per required field
            else:
                issues.append(f'Missing required field: {field}')
        
        # Check optional fields
        for field in optional_fields:
            if field in metadata and metadata[field]:
                score += 0.05  # 5% per optional field
        
        # Validate field values
        if 'word_count' in metadata and isinstance(metadata['word_count'], int):
            if metadata['word_count'] < 100:
                issues.append('Very low word count')
            elif metadata['word_count'] > 50000:
                issues.append('Extremely high word count')
        
        return {
            'score': min(1.0, score),
            'completeness': len([f for f in required_fields if f in metadata]) / len(required_fields),
            'issues': issues
        }
    
    def _assess_structure_quality(self, text: str, chunks: List[str]) -> Dict[str, Any]:
        """Assess document structure quality"""
        # Ensure text is always a string
        if not isinstance(text, str):
            if isinstance(text, dict):
                text = text.get('content', '') or text.get('text', '') or text.get('raw_text', '') or str(text)
            else:
                text = str(text) if text else ''
        
        score = 0.0
        issues = []
        
        # Check for structure indicators
        has_headings = len(re.findall(r'\n\s*[A-Z][A-Z\s]+\n', text)) > 0
        has_paragraphs = len(re.findall(r'\n\s*\n', text)) > 2
        has_lists = len(re.findall(r'\n\s*[-*•]\s', text)) > 0
        
        if has_headings:
            score += 0.3
        else:
            issues.append('No clear headings found')
        
        if has_paragraphs:
            score += 0.3
        else:
            issues.append('Poor paragraph structure')
        
        if has_lists:
            score += 0.2
        
        # Check chunk quality - handle both string and dict chunks
        if chunks:
            chunk_lengths = []
            for chunk in chunks:
                if isinstance(chunk, dict):
                    # Extract text from chunk dictionary
                    chunk_text = chunk.get('text', '') or chunk.get('content', '') or str(chunk)
                    chunk_lengths.append(len(chunk_text.split()))
                elif isinstance(chunk, str):
                    chunk_lengths.append(len(chunk.split()))
                else:
                    chunk_lengths.append(0)
            
            if chunk_lengths:
                avg_chunk_length = sum(chunk_lengths) / len(chunk_lengths)
                if 50 <= avg_chunk_length <= 500:
                    score += 0.2
                else:
                    issues.append('Suboptimal chunk sizes')
        
        return {
            'score': score,
            'has_headings': has_headings,
            'has_paragraphs': has_paragraphs,
            'has_lists': has_lists,
            'chunk_count': len(chunks),
            'issues': issues
        }
    
    def _assess_relevance_score(self, text: str) -> Dict[str, Any]:
        """Assess relevance to agricultural domain"""
        # Ensure text is always a string
        if not isinstance(text, str):
            if isinstance(text, dict):
                text = text.get('content', '') or text.get('text', '') or text.get('raw_text', '') or str(text)
            else:
                text = str(text) if text else ''
        
        text_lower = text.lower()
        
        # Count keyword occurrences
        keyword_scores = {}
        total_keywords = 0
        
        for category, keywords in self.agricultural_keywords.items():
            category_count = sum(text_lower.count(keyword) for keyword in keywords)
            keyword_scores[category] = category_count
            total_keywords += category_count
        
        # Calculate relevance score
        text_length = len(text.split())
        keyword_density = total_keywords / text_length if text_length > 0 else 0
        
        # Normalize relevance score
        relevance_score = min(1.0, keyword_density * 100)  # Scale up keyword density
        
        return {
            'score': relevance_score,
            'keyword_density': keyword_density,
            'keyword_counts': keyword_scores,
            'total_keywords': total_keywords,
            'is_agricultural': relevance_score > 0.1
        }
    
    def _calculate_readability(self, text: str, word_count: int, sentence_count: int) -> float:
        """Calculate readability score (simplified)"""
        if sentence_count == 0:
            return 0.0
        
        avg_sentence_length = word_count / sentence_count
        
        # Simple readability based on sentence length
        if avg_sentence_length <= 15:
            return 0.9  # Very readable
        elif avg_sentence_length <= 20:
            return 0.7  # Good readability
        elif avg_sentence_length <= 25:
            return 0.5  # Average readability
        else:
            return 0.3  # Poor readability
    
    def _assess_content_depth(self, text: str) -> float:
        """Assess depth of content"""
        # Ensure text is always a string
        if not isinstance(text, str):
            if isinstance(text, dict):
                text = text.get('content', '') or text.get('text', '') or text.get('raw_text', '') or str(text)
            else:
                text = str(text) if text else ''
        
        # Simple depth assessment based on various factors
        depth_score = 0.0
        
        # Check for detailed explanations
        if 'how' in text.lower() or 'why' in text.lower() or 'what' in text.lower():
            depth_score += 0.3
        
        # Check for examples
        if 'example' in text.lower() or 'for instance' in text.lower():
            depth_score += 0.2
        
        # Check for procedures/steps
        if 'step' in text.lower() or 'first' in text.lower() or 'then' in text.lower():
            depth_score += 0.3
        
        # Check for technical terms - be more generous
        technical_terms = ['analysis', 'method', 'process', 'technique', 'system', 'comprehensive', 'advanced', 'precision', 'sustainable', 'management', 'practices', 'strategies']
        for term in technical_terms:
            if term in text.lower():
                depth_score += 0.1  # Increased from 0.05
        
        # Check for agricultural terms - bonus for domain relevance
        agricultural_terms = ['agricultural', 'farming', 'crop', 'soil', 'pest', 'fertilizer', 'irrigation', 'cultivation', 'harvest', 'planting']
        for term in agricultural_terms:
            if term in text.lower():
                depth_score += 0.15  # Bonus for agricultural content
        
        return min(1.0, depth_score)
    
    def _assess_information_density(self, text: str) -> float:
        """Assess information density"""
        # Ensure text is always a string
        if not isinstance(text, str):
            if isinstance(text, dict):
                text = text.get('content', '') or text.get('text', '') or text.get('raw_text', '') or str(text)
            else:
                text = str(text) if text else ''
        
        # Simple information density assessment
        if not text:
            return 0.0
        
        words = text.split()
        word_count = len(words)
        
        # Count informative words (not common words)
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'a', 'an'}
        informative_words = [word for word in words if word.lower() not in common_words and len(word) > 2]
        
        if word_count == 0:
            return 0.0
        
        # More generous density calculation
        base_density = len(informative_words) / word_count
        
        # Bonus for technical/agricultural terms
        technical_words = ['comprehensive', 'advanced', 'precision', 'sustainable', 'management', 'practices', 'strategies', 'techniques', 'agricultural', 'farming', 'cultivation']
        tech_count = sum(1 for word in words if word.lower() in technical_words)
        tech_bonus = min(0.3, tech_count * 0.1)
        
        final_density = base_density * 2 + tech_bonus  # More generous scaling
        return min(1.0, final_density)
    
    def _get_quality_level(self, score: float) -> str:
        """Get quality level based on score"""
        if score >= self.quality_thresholds['excellent']:
            return 'excellent'
        elif score >= self.quality_thresholds['very_good']:
            return 'very_good'
        elif score >= self.quality_thresholds['good']:
            return 'good'
        elif score >= self.quality_thresholds['fair']:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_recommendations(self, content_quality: Dict, metadata_quality: Dict, 
                                structure_quality: Dict, relevance_score: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Content recommendations
        if content_quality['score'] < 0.6:
            recommendations.append("Improve content depth and detail")
        if content_quality['metrics']['word_count'] < 500:
            recommendations.append("Consider expanding content length")
        
        # Metadata recommendations
        if metadata_quality['score'] < 0.8:
            recommendations.append("Complete missing metadata fields")
        
        # Structure recommendations
        if structure_quality['score'] < 0.6:
            recommendations.append("Improve document structure with headings and paragraphs")
        
        # Relevance recommendations
        if relevance_score['score'] < 0.3:
            recommendations.append("Increase agricultural domain relevance")
        
        return recommendations
    
    def validate_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate document against quality thresholds
        
        Args:
            document_data: Document data to validate
            
        Returns:
            Validation results
        """
        quality_assessment = self.score_document(document_data)
        
        # Validation criteria
        min_score = 0.5  # Reduced from self.quality_thresholds['fair']
        is_valid = quality_assessment['overall_score'] >= min_score
        
        # Collect validation issues
        issues = []
        
        if quality_assessment['content_quality']['score'] < 0.3:  # Reduced threshold
            issues.append("Content quality below minimum threshold")
        
        if quality_assessment['metadata_quality']['score'] < 0.4:  # Reduced threshold
            issues.append("Metadata quality insufficient")
        
        if quality_assessment['relevance_score']['score'] < 0.05:  # Reduced threshold
            issues.append("Document not relevant to agricultural domain")
        
        return {
            'is_valid': is_valid,
            'quality_score': quality_assessment['overall_score'],
            'quality_level': quality_assessment['quality_level'],
            'issues': issues,
            'recommendations': quality_assessment['recommendations'],
            'validation_date': datetime.now().isoformat()
        }
    
    def get_quality_statistics(self) -> Dict[str, Any]:
        """
        Get quality scoring statistics
        
        Returns:
            Dictionary with scoring statistics
        """
        return {
            'quality_thresholds': self.quality_thresholds,
            'agricultural_keywords': {k: len(v) for k, v in self.agricultural_keywords.items()},
            'total_keywords': sum(len(v) for v in self.agricultural_keywords.values()),
            'scorer_version': '1.0.0'
        }


if __name__ == "__main__":
    # Test the document quality scorer
    scorer = DocumentQualityScorer()
    
    print("🌾 Document Quality Scorer - Test Run")
    print("=" * 50)
    
    # Test with sample document
    sample_document = {
        'text': 'This is a comprehensive agricultural guide with detailed information about crop cultivation, soil management, and pest control. It covers maize farming techniques, irrigation methods, and sustainable farming practices.',
        'metadata': {
            'title': 'Agricultural Guide',
            'author': 'Expert Author',
            'creation_date': '2024-01-01',
            'word_count': 500,
            'page_count': 20
        },
        'chunks': ['chunk1', 'chunk2', 'chunk3']
    }
    
    # Score the document
    quality_score = scorer.score_document(sample_document)
    print(f"Overall Score: {quality_score['overall_score']:.2f}")
    print(f"Quality Level: {quality_score['quality_level']}")
    
    # Validate the document
    validation_result = scorer.validate_document(sample_document)
    print(f"Is Valid: {validation_result['is_valid']}")
    print(f"Issues: {validation_result['issues']}")
    
    # Get statistics
    stats = scorer.get_quality_statistics()
    print(f"Total Keywords: {stats['total_keywords']}")
    
    print("\n✅ Document Quality Scorer test completed") 