"""
PDF-Enhanced Varieties System for Agricultural Advisor Bot.
Week 5 implementation - Integrates PDF knowledge with variety recommendations.
"""

import datetime
from typing import Dict, List, Any, Optional
from scripts.data_pipeline.semantic_search import SemanticSearch
from scripts.utils.logger import logger


class PDFEnhancedVarieties:
    """
    PDF-enhanced variety recommendation system.
    Uses semantic search to find variety-specific information from agricultural documents.
    """
    
    def __init__(self):
        """Initialize the PDF enhanced varieties system."""
        try:
            self.semantic_search = SemanticSearch()
            self.variety_cache = {}  # Cache for variety information
            
            # Common variety search terms
            self.variety_search_terms = {
                'drought_tolerance': ['drought tolerant', 'dry conditions', 'water stress resistant'],
                'disease_resistance': ['disease resistant', 'pest resistant', 'immune'],
                'yield_potential': ['high yield', 'productive', 'good yield'],
                'maturity': ['early maturity', 'late maturity', 'days to maturity'],
                'climate_adaptation': ['adapted to', 'suitable for', 'climate']
            }
            
            logger.info("PDF enhanced varieties system initialized")
            
        except Exception as e:
            logger.error(f"Error initializing PDF enhanced varieties: {str(e)}")
            self.semantic_search = None
    
    def get_pdf_enhanced_varieties(self, 
                                 crop_recommendations: List[Dict[str, Any]],
                                 location: str,
                                 conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get PDF-enhanced variety recommendations for top crop recommendations.
        
        Args:
            crop_recommendations: List of top crop recommendations
            location: Location name (e.g., 'Lilongwe')
            conditions: Environmental conditions
            
        Returns:
            Enhanced variety recommendations with PDF data
        """
        if not self.semantic_search:
            logger.warning("Semantic search not available")
            return {'varieties': [], 'pdf_sources': [], 'enhanced_recommendations': []}
        
        try:
            enhanced_varieties = []
            all_pdf_sources = set()
            
            for crop_rec in crop_recommendations:
                crop_id = crop_rec.get('crop_id', '')
                
                # Get PDF-enhanced variety information
                pdf_variety_info = self.search_variety_information(
                    crop=crop_id,
                    location=location,
                    conditions=conditions
                )
                
                # Combine with existing variety recommendations
                enhanced_crop = crop_rec.copy()
                enhanced_crop['pdf_enhanced_varieties'] = pdf_variety_info
                enhanced_varieties.append(enhanced_crop)
                
                # Collect PDF sources
                pdf_sources = pdf_variety_info.get('pdf_sources', [])
                all_pdf_sources.update(pdf_sources)
            
            return {
                'varieties': enhanced_varieties,
                'pdf_sources': list(all_pdf_sources),
                'enhanced_recommendations': self._generate_enhanced_recommendations(
                    enhanced_varieties, conditions
                ),
                'generated_at': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting PDF enhanced varieties: {str(e)}")
            return {'varieties': [], 'pdf_sources': [], 'enhanced_recommendations': []}
    
    def search_variety_information(self, 
                                 crop: str,
                                 location: str,
                                 conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for variety-specific information in PDF documents.
        
        Args:
            crop: Crop identifier
            location: Location name
            conditions: Environmental conditions
            
        Returns:
            Variety information from PDF sources
        """
        if not self.semantic_search:
            return {'varieties': [], 'pdf_sources': [], 'enhanced_recommendations': []}
        
        try:
            # Create cache key
            cache_key = f"{crop}_{location}_{hash(str(conditions))}"
            
            # Check cache first
            if cache_key in self.variety_cache:
                logger.info(f"Using cached variety information for {crop}")
                return self.variety_cache[cache_key]
            
            # Build search queries based on conditions
            search_queries = self._build_variety_search_queries(crop, location, conditions)
            
            # Search for variety information
            variety_results = []
            pdf_sources = set()
            
            for query in search_queries:
                logger.info(f"Searching for: {query}")
                
                search_results = self.semantic_search.search_documents(
                    query=query,
                    top_k=3,
                    threshold=0.7
                )
                
                for result in search_results:
                    variety_results.append(result)
                    pdf_sources.add(result.get('source_document', ''))
            
            # Process and enhance results
            enhanced_varieties = self._process_variety_search_results(
                variety_results, crop, conditions
            )
            
            # Generate recommendations
            recommendations = self._generate_variety_recommendations(
                enhanced_varieties, conditions
            )
            
            result = {
                'varieties': enhanced_varieties,
                'pdf_sources': list(pdf_sources),
                'enhanced_recommendations': recommendations,
                'search_queries': search_queries,
                'result_count': len(variety_results)
            }
            
            # Cache the result
            self.variety_cache[cache_key] = result
            
            logger.info(f"Found {len(enhanced_varieties)} PDF-enhanced varieties for {crop}")
            return result
            
        except Exception as e:
            logger.error(f"Error searching variety information: {str(e)}")
            return {'varieties': [], 'pdf_sources': [], 'enhanced_recommendations': []}
    
    def get_variety_performance_data(self, 
                                   variety_name: str,
                                   location: str) -> Dict[str, Any]:
        """
        Get performance data for a specific variety.
        
        Args:
            variety_name: Name of the variety
            location: Location name
            
        Returns:
            Performance data from PDF sources
        """
        if not self.semantic_search:
            return {'yield_data': {}, 'climate_adaptation': {}, 'pdf_sources': []}
        
        try:
            # Search for variety performance data
            performance_queries = [
                f"{variety_name} yield performance {location}",
                f"{variety_name} productivity {location}",
                f"{variety_name} adaptation {location}",
                f"{variety_name} field trials {location}"
            ]
            
            performance_results = []
            pdf_sources = set()
            
            for query in performance_queries:
                search_results = self.semantic_search.search_documents(
                    query=query,
                    top_k=2,
                    threshold=0.75
                )
                
                for result in search_results:
                    performance_results.append(result)
                    pdf_sources.add(result.get('source_document', ''))
            
            # Extract performance data
            yield_data = self._extract_yield_data(performance_results, variety_name)
            climate_adaptation = self._extract_climate_adaptation(performance_results, variety_name)
            
            return {
                'yield_data': yield_data,
                'climate_adaptation': climate_adaptation,
                'pdf_sources': list(pdf_sources),
                'variety_name': variety_name,
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Error getting variety performance data: {str(e)}")
            return {'yield_data': {}, 'climate_adaptation': {}, 'pdf_sources': []}
    
    def get_disease_resistance_info(self, 
                                  crop: str,
                                  location: str) -> Dict[str, Any]:
        """
        Get disease resistance information for crop varieties.
        
        Args:
            crop: Crop identifier
            location: Location name
            
        Returns:
            Disease resistance information from PDF sources
        """
        if not self.semantic_search:
            return {'common_diseases': [], 'resistant_varieties': [], 'pdf_sources': []}
        
        try:
            # Search for disease resistance information
            disease_queries = [
                f"{crop} disease resistance {location}",
                f"{crop} pest resistant varieties {location}",
                f"{crop} disease management {location}",
                f"{crop} common diseases {location}"
            ]
            
            disease_results = []
            pdf_sources = set()
            
            for query in disease_queries:
                search_results = self.semantic_search.search_documents(
                    query=query,
                    top_k=3,
                    threshold=0.7
                )
                
                for result in search_results:
                    disease_results.append(result)
                    pdf_sources.add(result.get('source_document', ''))
            
            # Extract disease information
            common_diseases = self._extract_common_diseases(disease_results, crop)
            resistant_varieties = self._extract_resistant_varieties(disease_results, crop)
            
            return {
                'common_diseases': common_diseases,
                'resistant_varieties': resistant_varieties,
                'pdf_sources': list(pdf_sources),
                'crop': crop,
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Error getting disease resistance info: {str(e)}")
            return {'common_diseases': [], 'resistant_varieties': [], 'pdf_sources': []}
    
    def _build_variety_search_queries(self, 
                                    crop: str,
                                    location: str,
                                    conditions: Dict[str, Any]) -> List[str]:
        """
        Build search queries based on crop, location, and conditions.
        
        Args:
            crop: Crop identifier
            location: Location name
            conditions: Environmental conditions
            
        Returns:
            List of search queries
        """
        queries = []
        
        # Base queries
        queries.append(f"{crop} varieties {location}")
        queries.append(f"{crop} cultivars {location}")
        queries.append(f"best {crop} varieties {location}")
        
        # Condition-specific queries
        if conditions.get('drought_stress', False) or conditions.get('rainfall', 0) < 400:
            queries.append(f"{crop} drought tolerant varieties {location}")
            queries.append(f"{crop} drought resistant {location}")
        
        if conditions.get('low_rainfall', False):
            queries.append(f"{crop} low rainfall varieties {location}")
            queries.append(f"{crop} water stress resistant {location}")
        
        if conditions.get('temperature') and conditions['temperature'] > 30:
            queries.append(f"{crop} heat tolerant varieties {location}")
            queries.append(f"{crop} high temperature resistant {location}")
        
        # Performance-based queries
        queries.append(f"{crop} high yield varieties {location}")
        queries.append(f"{crop} improved varieties {location}")
        queries.append(f"{crop} variety recommendations {location}")
        
        return queries
    
    def _process_variety_search_results(self, 
                                      search_results: List[Dict[str, Any]],
                                      crop: str,
                                      conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process search results to extract variety information.
        
        Args:
            search_results: Search results from semantic search
            crop: Crop identifier
            conditions: Environmental conditions
            
        Returns:
            Processed variety information
        """
        processed_varieties = []
        
        for result in search_results:
            text = result.get('text', '')
            score = result.get('score', 0)
            source = result.get('source_document', '')
            
            # Extract variety names from text
            variety_names = self._extract_variety_names(text, crop)
            
            # Extract performance characteristics
            characteristics = self._extract_characteristics(text, conditions)
            
            # Create variety entries
            for variety_name in variety_names:
                variety_info = {
                    'variety_name': variety_name,
                    'crop': crop,
                    'pdf_enhanced_data': {
                        'source_document': source,
                        'relevance_score': score,
                        'characteristics': characteristics,
                        'text_excerpt': text[:300] + '...' if len(text) > 300 else text
                    },
                    'conditions_match': self._calculate_conditions_match(characteristics, conditions)
                }
                
                processed_varieties.append(variety_info)
        
        # Remove duplicates and sort by relevance
        unique_varieties = {}
        for variety in processed_varieties:
            name = variety['variety_name']
            if name not in unique_varieties or \
               variety['pdf_enhanced_data']['relevance_score'] > unique_varieties[name]['pdf_enhanced_data']['relevance_score']:
                unique_varieties[name] = variety
        
        # Sort by conditions match and relevance
        sorted_varieties = sorted(
            unique_varieties.values(),
            key=lambda x: (x['conditions_match'], x['pdf_enhanced_data']['relevance_score']),
            reverse=True
        )
        
        return sorted_varieties[:5]  # Return top 5 varieties
    
    def _generate_variety_recommendations(self, 
                                        varieties: List[Dict[str, Any]],
                                        conditions: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on variety information.
        
        Args:
            varieties: List of variety information
            conditions: Environmental conditions
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if not varieties:
            recommendations.append("No specific variety information found in agricultural documents")
            return recommendations
        
        # Top variety recommendation
        if varieties:
            top_variety = varieties[0]
            recommendations.append(
                f"Based on agricultural documents, {top_variety['variety_name']} "
                f"shows good adaptation to local conditions"
            )
        
        # Condition-specific recommendations
        drought_tolerant = [v for v in varieties if 'drought' in str(v['pdf_enhanced_data']['characteristics']).lower()]
        if drought_tolerant and (conditions.get('drought_stress') or conditions.get('rainfall', 0) < 400):
            recommendations.append(
                f"For dry conditions, consider {drought_tolerant[0]['variety_name']} "
                f"which shows drought tolerance in field studies"
            )
        
        # Disease resistance recommendations
        disease_resistant = [v for v in varieties if 'resistance' in str(v['pdf_enhanced_data']['characteristics']).lower()]
        if disease_resistant:
            recommendations.append(
                f"{disease_resistant[0]['variety_name']} shows disease resistance "
                f"which is important for local conditions"
            )
        
        # General recommendations
        if len(varieties) > 1:
            recommendations.append(
                f"Consider diversifying with multiple varieties: "
                f"{', '.join([v['variety_name'] for v in varieties[:3]])}"
            )
        
        return recommendations
    
    def _generate_enhanced_recommendations(self, 
                                         enhanced_varieties: List[Dict[str, Any]],
                                         conditions: Dict[str, Any]) -> List[str]:
        """
        Generate overall enhanced recommendations.
        
        Args:
            enhanced_varieties: List of enhanced variety data
            conditions: Environmental conditions
            
        Returns:
            List of enhanced recommendation strings
        """
        recommendations = []
        
        # Count varieties with PDF data
        pdf_enhanced_count = sum(1 for crop in enhanced_varieties 
                               if crop.get('pdf_enhanced_varieties', {}).get('varieties', []))
        
        if pdf_enhanced_count > 0:
            recommendations.append(
                f"Found specific variety information for {pdf_enhanced_count} crops "
                f"in agricultural documents"
            )
        
        # Environmental adaptation recommendations
        if conditions.get('rainfall', 0) < 400:
            recommendations.append(
                "Focus on drought-tolerant varieties given low rainfall conditions"
            )
        
        if conditions.get('temperature', 0) > 30:
            recommendations.append(
                "Consider heat-tolerant varieties for high temperature conditions"
            )
        
        # Source quality recommendations
        recommendations.append(
            "Variety recommendations are based on agricultural research documents "
            "and field trial results"
        )
        
        return recommendations
    
    def _extract_variety_names(self, text: str, crop: str) -> List[str]:
        """
        Extract variety names from text.
        
        Args:
            text: Text to search
            crop: Crop identifier
            
        Returns:
            List of variety names
        """
        variety_names = []
        
        # Common variety naming patterns
        patterns = [
            r'variety\s+(\w+)',
            r'cultivar\s+(\w+)',
            r'(\w+\s*\d+)',  # Names with numbers like SC403
            r'(\w+\s+\w+)',  # Two-word names
        ]
        
        import re
        text_lower = text.lower()
        
        # Look for crop-specific patterns
        if crop == 'maize':
            # Look for common maize variety patterns
            maize_patterns = [
                r'(SC\d+)', r'(DK\d+)', r'(PHB\d+)', r'(Local\s+\w+)'
            ]
            for pattern in maize_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                variety_names.extend(matches)
        
        elif crop == 'beans':
            # Look for common bean variety patterns
            bean_patterns = [
                r'(Navy\s+Bean)', r'(Pinto\s+Bean)', r'(Climbing\s+Bean)'
            ]
            for pattern in bean_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                variety_names.extend(matches)
        
        # Generic variety extraction
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            variety_names.extend(matches)
        
        # Clean and filter results
        cleaned_names = []
        for name in variety_names:
            if isinstance(name, tuple):
                name = name[0]
            name = name.strip()
            if len(name) > 2 and name.lower() not in ['the', 'and', 'for', 'with']:
                cleaned_names.append(name)
        
        return list(set(cleaned_names))[:5]  # Return unique names, max 5
    
    def _extract_characteristics(self, text: str, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract variety characteristics from text.
        
        Args:
            text: Text to analyze
            conditions: Environmental conditions
            
        Returns:
            Dictionary of characteristics
        """
        characteristics = {}
        text_lower = text.lower()
        
        # Drought tolerance
        if any(term in text_lower for term in ['drought', 'dry', 'water stress', 'moisture stress']):
            characteristics['drought_tolerance'] = True
        
        # Disease resistance
        if any(term in text_lower for term in ['resistance', 'resistant', 'immune', 'tolerant']):
            characteristics['disease_resistance'] = True
        
        # Yield potential
        if any(term in text_lower for term in ['high yield', 'productive', 'good yield']):
            characteristics['high_yield'] = True
        
        # Maturity
        if any(term in text_lower for term in ['early', 'quick', 'fast']):
            characteristics['early_maturity'] = True
        elif any(term in text_lower for term in ['late', 'long', 'extended']):
            characteristics['late_maturity'] = True
        
        # Climate adaptation
        if any(term in text_lower for term in ['adapted', 'suitable', 'climate']):
            characteristics['climate_adapted'] = True
        
        return characteristics
    
    def _calculate_conditions_match(self, characteristics: Dict[str, Any], conditions: Dict[str, Any]) -> float:
        """
        Calculate how well variety characteristics match conditions.
        
        Args:
            characteristics: Variety characteristics
            conditions: Environmental conditions
            
        Returns:
            Match score (0-1)
        """
        score = 0.0
        total_conditions = 0
        
        # Drought conditions
        if conditions.get('drought_stress') or conditions.get('rainfall', 0) < 400:
            total_conditions += 1
            if characteristics.get('drought_tolerance'):
                score += 1.0
        
        # Temperature conditions
        if conditions.get('temperature', 0) > 30:
            total_conditions += 1
            if characteristics.get('climate_adapted'):
                score += 0.5
        
        # General suitability
        if characteristics.get('disease_resistance'):
            score += 0.3
        
        if characteristics.get('high_yield'):
            score += 0.2
        
        # Normalize score
        return min(score / max(total_conditions, 1), 1.0)
    
    def _extract_yield_data(self, results: List[Dict[str, Any]], variety_name: str) -> Dict[str, Any]:
        """
        Extract yield data from search results.
        
        Args:
            results: Search results
            variety_name: Variety name
            
        Returns:
            Yield data dictionary
        """
        yield_data = {}
        
        for result in results:
            text = result.get('text', '')
            if variety_name.lower() in text.lower():
                # Look for yield numbers (simplified extraction)
                import re
                yield_patterns = [
                    r'(\d+\.?\d*)\s*(?:tons?|kg|t)\s*(?:per|/)\s*(?:hectare|ha)',
                    r'yield\s*(?:of|:)?\s*(\d+\.?\d*)',
                    r'(\d+\.?\d*)\s*t/ha'
                ]
                
                for pattern in yield_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        yield_data['yield_estimate'] = matches[0]
                        yield_data['source'] = result.get('source_document', '')
                        break
        
        return yield_data
    
    def _extract_climate_adaptation(self, results: List[Dict[str, Any]], variety_name: str) -> Dict[str, Any]:
        """
        Extract climate adaptation information.
        
        Args:
            results: Search results
            variety_name: Variety name
            
        Returns:
            Climate adaptation data
        """
        adaptation_data = {}
        
        for result in results:
            text = result.get('text', '')
            if variety_name.lower() in text.lower():
                text_lower = text.lower()
                
                if 'drought' in text_lower:
                    adaptation_data['drought_adaptation'] = True
                if 'heat' in text_lower:
                    adaptation_data['heat_tolerance'] = True
                if 'rainfall' in text_lower:
                    adaptation_data['rainfall_adaptation'] = True
                
                adaptation_data['source'] = result.get('source_document', '')
        
        return adaptation_data
    
    def _extract_common_diseases(self, results: List[Dict[str, Any]], crop: str) -> List[Dict[str, Any]]:
        """
        Extract common diseases from search results.
        
        Args:
            results: Search results
            crop: Crop identifier
            
        Returns:
            List of common diseases
        """
        diseases = []
        
        # Common disease patterns by crop
        disease_patterns = {
            'maize': ['streak virus', 'grey leaf spot', 'borer', 'rust'],
            'beans': ['rust', 'anthracnose', 'mosaic virus', 'blight'],
            'groundnuts': ['rosette', 'leaf spot', 'rust', 'wilt']
        }
        
        crop_diseases = disease_patterns.get(crop, [])
        
        for result in results:
            text = result.get('text', '').lower()
            for disease in crop_diseases:
                if disease in text:
                    diseases.append({
                        'disease_name': disease,
                        'source': result.get('source_document', '')
                    })
        
        return diseases
    
    def _extract_resistant_varieties(self, results: List[Dict[str, Any]], crop: str) -> List[Dict[str, Any]]:
        """
        Extract resistant varieties from search results.
        
        Args:
            results: Search results
            crop: Crop identifier
            
        Returns:
            List of resistant varieties
        """
        resistant_varieties = []
        
        for result in results:
            text = result.get('text', '')
            if 'resistant' in text.lower() or 'resistance' in text.lower():
                # Extract variety names from resistant variety context
                variety_names = self._extract_variety_names(text, crop)
                
                for variety_name in variety_names:
                    resistant_varieties.append({
                        'variety_name': variety_name,
                        'resistance_level': 'moderate',  # Default level
                        'source': result.get('source_document', '')
                    })
        
        return resistant_varieties


# Global instance
pdf_enhanced_varieties = PDFEnhancedVarieties() 