"""
SQLite-Based Crop Recommendation Engine.
Uses agriculture guide PDFs from SQLite database for location-specific recommendations.
"""
import sqlite3
import json
import datetime
from typing import Dict, List, Any, Optional, Tuple
from scripts.weather_engine.historical_weather_api import HistoricalWeatherAPI, HistoricalRainfallData
from scripts.utils.logger import logger
import re


class SQLiteBasedRecommendationEngine:
    """Recommendation engine using agriculture guide PDFs from SQLite database."""
    
    def __init__(self, db_path: str = "data/farming_guide_vectors.db"):
        """
        Initialize the SQLite-based recommendation engine.
        
        Args:
            db_path: Path to the SQLite database with PDF chunks
        """
        self.db_path = db_path
        self.historical_api = HistoricalWeatherAPI()
        self.current_month = datetime.datetime.now().strftime('%B')
        
    def get_crop_recommendations_from_guides(self, 
                                           lat: float, 
                                           lon: float, 
                                           season: str,
                                           rainfall_mm: float,
                                           temperature: float,
                                           historical_years: int = 5,
                                           limit: int = 10,  # Increased default from 5 to 10
                                           offset: int = 0,
                                           include_alternatives: bool = False) -> Dict[str, Any]:
        """
        Get crop recommendations from agriculture guide PDFs.
        
        Args:
            lat: Latitude
            lon: Longitude
            season: Season (rainy_season, dry_season, current)
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            historical_years: Number of years of historical data
            limit: Number of recommendations to return (default: 5)
            offset: Offset for pagination (default: 0)
            include_alternatives: Whether to include alternative crops (default: False)
            
        Returns:
            Recommendations based on agriculture guides
        """
        logger.info(f"Generating SQLite-based recommendations for {lat}, {lon} in {season} (limit: {limit}, offset: {offset})")
        
        # Get historical weather data
        historical_data = self.historical_api.get_historical_rainfall(
            lat, lon, historical_years
        )
        
        # Query agriculture guides for crop information
        crop_guides = self._query_crop_guides(lat, lon, season, rainfall_mm, temperature)
        
        # Generate recommendations based on guide content
        recommendations = self._generate_guide_based_recommendations(
            crop_guides, lat, lon, season, rainfall_mm, temperature, historical_data,
            limit=limit, offset=offset, include_alternatives=include_alternatives
        )
        
        return recommendations
    
    def get_specific_crop_recommendations(self, 
                                        crop_name: str,
                                        lat: float, 
                                        lon: float, 
                                        season: str,
                                        rainfall_mm: float,
                                        temperature: float,
                                        historical_years: int = 5) -> Dict[str, Any]:
        """
        Get recommendations for a specific crop only - Phase 4 implementation.
        
        Args:
            crop_name: Name of the specific crop to get recommendations for
            lat: Latitude
            lon: Longitude
            season: Season (rainy_season, dry_season, current)
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            historical_years: Number of years of historical data
            
        Returns:
            Specific crop recommendations with detailed analysis
        """
        logger.info(f"Generating specific crop recommendations for '{crop_name}' at {lat}, {lon} in {season}")
        
        # Get historical weather data
        historical_data = self.historical_api.get_historical_rainfall(
            lat, lon, historical_years
        )
        
        # Query agriculture guides specifically for the named crop
        crop_guides = self._query_specific_crop_guides(crop_name, lat, lon, season, rainfall_mm, temperature)
        
        # Generate specific crop recommendations
        recommendations = self._generate_specific_crop_recommendations(
            crop_name, crop_guides, lat, lon, season, rainfall_mm, temperature, historical_data
        )
        
        return recommendations
    
    def _query_specific_crop_guides(self, 
                                   crop_name: str,
                                   lat: float, 
                                   lon: float, 
                                   season: str,
                                   rainfall_mm: float,
                                   temperature: float) -> List[Dict[str, Any]]:
        """
        Query agriculture guide PDFs specifically for a named crop.
        
        Args:
            crop_name: Name of the specific crop
            lat: Latitude
            lon: Longitude
            season: Season
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            
        Returns:
            List of relevant guide content for the specific crop
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Search specifically for the named crop
                crop_search_terms = [
                    crop_name.lower(),
                    crop_name.title(),
                    crop_name.upper(),
                    f"{crop_name} cultivation",
                    f"{crop_name} farming",
                    f"{crop_name} planting",
                    f"{crop_name} varieties",
                    f"{crop_name} management"
                ]
                
                guide_content = []
                
                for term in crop_search_terms:
                    query = """
                        SELECT chunk_id, text, source_doc, metadata
                        FROM pdf_chunks 
                        WHERE text LIKE ? 
                        ORDER BY LENGTH(text) DESC
                        LIMIT 20
                    """
                    cursor.execute(query, (f'%{term}%',))
                    results = cursor.fetchall()
                    
                    for row in results:
                        chunk_id, text, source_doc, metadata = row
                        guide_content.append({
                            'chunk_id': chunk_id,
                            'text': text,
                            'source_doc': source_doc,
                            'metadata': json.loads(metadata) if metadata else {},
                            'search_term': term,
                            'relevance_score': self._calculate_crop_relevance(text, crop_name, season, rainfall_mm, temperature)
                        })
                
                # Remove duplicates and sort by relevance
                unique_content = {}
                for content in guide_content:
                    chunk_id = content['chunk_id']
                    if chunk_id not in unique_content or content['relevance_score'] > unique_content[chunk_id]['relevance_score']:
                        unique_content[chunk_id] = content
                
                sorted_content = sorted(unique_content.values(), key=lambda x: x['relevance_score'], reverse=True)
                
                logger.info(f"Found {len(sorted_content)} relevant chunks for '{crop_name}'")
                return sorted_content[:15]  # Limit to top 15 most relevant chunks
                
        except Exception as e:
            logger.error(f"Error querying specific crop guides for '{crop_name}': {e}")
            return []
    
    def _generate_specific_crop_recommendations(self, 
                                              crop_name: str,
                                              crop_guides: List[Dict[str, Any]], 
                                              lat: float, 
                                              lon: float, 
                                              season: str,
                                              rainfall_mm: float,
                                              temperature: float,
                                              historical_data: HistoricalRainfallData) -> Dict[str, Any]:
        """
        Generate recommendations specifically for the named crop.
        
        Args:
            crop_name: Name of the specific crop
            crop_guides: Guide content for the specific crop
            lat: Latitude
            lon: Longitude
            season: Season
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            historical_data: Historical rainfall data
            
        Returns:
            Specific crop recommendations with detailed analysis
        """
        if not crop_guides:
            # Return "not suitable" analysis if no guides found
            return self._generate_unsuitable_crop_analysis(crop_name, lat, lon, season, rainfall_mm, temperature)
        
        # Analyze crop suitability based on guides
        suitability_analysis = self._analyze_crop_suitability(crop_name, crop_guides, season, rainfall_mm, temperature)
        
        # Extract crop-specific information
        crop_info = self._extract_crop_information(crop_name, crop_guides)
        
        # Generate detailed recommendations
        recommendations = [{
            'crop_name': crop_name,
            'suitability_score': suitability_analysis['score'],
            'score': round(suitability_analysis['score'] * 100),
            'suitability_level': suitability_analysis['level'],
            'rainfall_match': suitability_analysis['rainfall_match'],
            'temperature_match': suitability_analysis['temperature_match'],
            'season_suitability': suitability_analysis['season_match'],
            'sources': crop_info['sources'],
            'guide_recommendations': crop_info['recommendations'],
            'varieties': crop_info['varieties'],
            'planting_time': crop_info['planting_time'],
            'yield_potential': crop_info['yield_potential'],
            'description': crop_info['description'],
            'management_tips': crop_info['management_tips'],
            'risk_assessment': crop_info['risk_assessment']
        }]
        
        return {
            'recommendations': recommendations,
            'planting_advice': crop_info['planting_advice'],
            'management_tips': crop_info['management_tips'],
            'risk_assessment': crop_info['risk_assessment'],
            'sources': crop_info['sources'],
            'historical_data': historical_data.years_analyzed,
            'location': {'lat': lat, 'lon': lon, 'region': self._get_region_name(lat, lon)},
            'search_mode': 'specific_crop',
            'crop_analyzed': crop_name
        }
    
    def _generate_unsuitable_crop_analysis(self, 
                                         crop_name: str,
                                         lat: float, 
                                         lon: float, 
                                         season: str,
                                         rainfall_mm: float,
                                         temperature: float) -> Dict[str, Any]:
        """
        Generate analysis for crops that are not suitable for current conditions.
        
        Args:
            crop_name: Name of the unsuitable crop
            lat: Latitude
            lon: Longitude
            season: Season
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            
        Returns:
            Analysis explaining why the crop is not suitable
        """
        # Basic suitability check based on common crop requirements
        rainfall_suitable = 200 <= rainfall_mm <= 1200  # General range for most crops
        temperature_suitable = 15 <= temperature <= 35   # General range for most crops
        
        suitability_score = 0.2  # Low score for unsuitable crops
        if rainfall_suitable and temperature_suitable:
            suitability_score = 0.4  # Slightly higher if basic conditions are met
        
        return {
            'recommendations': [{
                'crop_name': crop_name,
                'suitability_score': suitability_score,
                'score': round(suitability_score * 100),
                'suitability_level': 'poor',
                'rainfall_match': 'poor' if not rainfall_suitable else 'fair',
                'temperature_match': 'poor' if not temperature_suitable else 'fair',
                'season_suitability': 'poor',
                'sources': ['General agricultural knowledge'],
                'guide_recommendations': [
                    f'{crop_name.title()} may not be suitable for current conditions',
                    'Consider alternative crops better suited to your location and season',
                    'Consult local agricultural extension services for specific advice'
                ],
                'varieties': [],
                'planting_time': 'Not recommended',
                'yield_potential': 'Low',
                'description': f'{crop_name.title()} is not well-suited for current environmental conditions',
                'management_tips': [
                    'Consider soil and climate requirements for this crop',
                    'Evaluate alternative crops for your region',
                    'Consult with local agricultural experts'
                ],
                'risk_assessment': {
                    'weather_risks': [
                        f'Current rainfall ({rainfall_mm}mm) may not be optimal for {crop_name}',
                        f'Current temperature ({temperature}°C) may not be suitable for {crop_name}'
                    ],
                    'pest_risks': ['High risk due to unsuitable growing conditions'],
                    'disease_risks': ['High risk due to unsuitable growing conditions']
                }
            }],
            'planting_advice': {
                'optimal_planting_time': 'Not recommended',
                'soil_preparation': 'Not applicable',
                'spacing': 'Not applicable'
            },
            'management_tips': [
                f'{crop_name.title()} is not recommended for current conditions',
                'Consider crops better suited to your climate and soil',
                'Consult local agricultural extension services'
            ],
            'risk_assessment': {
                'weather_risks': [
                    f'Current conditions are not suitable for {crop_name}',
                    'Consider waiting for more favorable weather conditions'
                ],
                'pest_risks': ['High risk due to unsuitable conditions'],
                'disease_risks': ['High risk due to unsuitable conditions']
            },
            'sources': ['General agricultural knowledge'],
            'historical_data': 0,
            'location': {'lat': lat, 'lon': lon, 'region': self._get_region_name(lat, lon)},
            'search_mode': 'specific_crop',
            'crop_analyzed': crop_name,
            'unsuitable': True
        }
    
    def _query_crop_guides(self, 
                          lat: float, 
                          lon: float, 
                          season: str,
                          rainfall_mm: float,
                          temperature: float) -> List[Dict[str, Any]]:
        """
        Query agriculture guide PDFs for crop information.
        
        Args:
            lat: Latitude
            lon: Longitude
            season: Season
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            
        Returns:
            List of relevant guide content
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Search for crop-related content
                search_terms = self._generate_search_terms(season, rainfall_mm, temperature)
                guide_content = []
                
                for term in search_terms:
                    cursor.execute("""
                        SELECT id, content, source, metadata
                        FROM documents
                        WHERE content LIKE ?
                        ORDER BY id
                        LIMIT 20
                    """, (f'%{term}%',))
                    
                    for row in cursor.fetchall():
                        doc_id, content, source, metadata = row
                        guide_content.append({
                            'id': doc_id,
                            'content': content,
                            'source': source,
                            'metadata': metadata,
                            'search_term': term,
                            'relevance_score': self._calculate_content_relevance(
                                content, lat, lon, season, rainfall_mm, temperature
                            )
                        })
                
                # Sort by relevance and remove duplicates
                guide_content.sort(key=lambda x: x['relevance_score'], reverse=True)
                unique_content = self._remove_duplicate_content(guide_content)
                
                logger.info(f"Found {len(unique_content)} relevant guide chunks")
                return unique_content
                
        except Exception as e:
            logger.error(f"Error querying crop guides: {e}")
            return []
    
    def _generate_search_terms(self, season: str, rainfall_mm: float, temperature: float) -> List[str]:
        """Generate search terms based on conditions."""
        terms = []
        
        # Season-based terms
        if season == 'rainy_season':
            terms.extend(['rainy season', 'wet season', 'rainfall', 'irrigation'])
        elif season == 'dry_season':
            terms.extend(['dry season', 'drought', 'water conservation', 'irrigation'])
        
        # Rainfall-based terms
        if rainfall_mm < 100:
            terms.extend(['drought tolerant', 'low rainfall', 'water efficient'])
        elif rainfall_mm > 500:
            terms.extend(['high rainfall', 'flood resistant', 'drainage'])
        
        # Temperature-based terms
        if temperature < 20:
            terms.extend(['cool season', 'cold tolerant', 'early maturing'])
        elif temperature > 30:
            terms.extend(['heat tolerant', 'warm season', 'late maturing'])
        
        # General crop terms
        terms.extend([
            'maize', 'corn', 'beans', 'groundnuts', 'peanuts', 'sorghum',
            'cassava', 'sweet potato', 'soybeans', 'pigeon peas',
            'planting', 'cultivation', 'production', 'yield',
            'Malawi', 'Lilongwe', 'agriculture', 'farming'
        ])
        
        return list(set(terms))  # Remove duplicates
    
    def _calculate_content_relevance(self, 
                                   content: str, 
                                   lat: float, 
                                   lon: float, 
                                   season: str,
                                   rainfall_mm: float,
                                   temperature: float) -> float:
        """Calculate relevance score for guide content."""
        relevance = 0.0
        
        # Location relevance
        if 'Malawi' in content or 'Lilongwe' in content:
            relevance += 0.3
        
        # Season relevance
        if season == 'rainy_season' and ('rainy' in content.lower() or 'wet' in content.lower()):
            relevance += 0.2
        elif season == 'dry_season' and ('dry' in content.lower() or 'drought' in content.lower()):
            relevance += 0.2
        
        # Rainfall relevance
        if rainfall_mm < 100 and ('drought' in content.lower() or 'low rainfall' in content.lower()):
            relevance += 0.2
        elif rainfall_mm > 500 and ('high rainfall' in content.lower() or 'flood' in content.lower()):
            relevance += 0.2
        
        # Crop relevance
        crop_terms = ['maize', 'beans', 'groundnuts', 'cassava', 'sweet potato', 'sorghum']
        for crop in crop_terms:
            if crop in content.lower():
                relevance += 0.1
        
        return min(1.0, relevance)
    
    def _remove_duplicate_content(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate content based on source and similar content."""
        unique_content = []
        seen_sources = set()
        
        for item in content_list:
            source = item['source']
            if source not in seen_sources:
                unique_content.append(item)
                seen_sources.add(source)
        
        return unique_content[:30]  # Increased from 20 to 30 results
    
    def _generate_guide_based_recommendations(self, 
                                            guide_content: List[Dict[str, Any]],
                                            lat: float, 
                                            lon: float, 
                                            season: str,
                                            rainfall_mm: float,
                                            temperature: float,
                                            historical_data: Optional[HistoricalRainfallData],
                                            limit: int = 10,  # Increased default from 5 to 10
                                            offset: int = 0,
                                            include_alternatives: bool = False) -> Dict[str, Any]:
        """
        Generate recommendations based on agriculture guide content.
        
        Args:
            guide_content: Agriculture guide content
            lat: Latitude
            lon: Longitude
            season: Season
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            historical_data: Historical weather data
            limit: Number of recommendations to return (default: 5)
            offset: Offset for pagination (default: 0)
            include_alternatives: Whether to include alternative crops (default: False)
            
        Returns:
            Guide-based recommendations
        """
        # Extract crop recommendations from guide content
        crop_recommendations = self._extract_crop_recommendations(guide_content, season, rainfall_mm, temperature, limit, offset, include_alternatives)
        
        # Generate planting advice from guides
        planting_advice = self._extract_planting_advice(guide_content, season, historical_data)
        
        # Generate management tips from guides
        management_tips = self._extract_management_tips(guide_content, season, rainfall_mm, temperature)
        
        # Generate risk assessment from guides
        risk_assessment = self._extract_risk_assessment(guide_content, season, rainfall_mm, temperature, historical_data)
        
        return {
            'recommendations': crop_recommendations,
            'planting_advice': planting_advice,
            'management_tips': management_tips,
            'risk_assessment': risk_assessment,
            'sources': [item['source'] for item in guide_content[:5]],  # Top 5 sources
            'historical_data': historical_data.years_analyzed if historical_data else 0,
            'location': {
                'latitude': lat,
                'longitude': lon,
                'season': season,
                'rainfall_mm': rainfall_mm,
                'temperature': temperature
            },
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total_recommendations': len(crop_recommendations),
                'has_more': len(crop_recommendations) >= limit,
                'include_alternatives': include_alternatives
            },
            'analysis_timestamp': datetime.datetime.now().isoformat()
        }
    
    def _extract_crop_recommendations(self, 
                                    guide_content: List[Dict[str, Any]],
                                    season: str,
                                    rainfall_mm: float,
                                    temperature: float,
                                    limit: int = 10,  # Increased default from 5 to 10
                                    offset: int = 0,
                                    include_alternatives: bool = False) -> List[Dict[str, Any]]:
        """Extract crop recommendations from guide content."""
        recommendations = []
        
        # Define primary crops to look for (expanded list)
        primary_crops = [
            'maize', 'corn', 'beans', 'groundnuts', 'peanuts', 'sorghum',
            'cassava', 'sweet potato', 'soybeans', 'pigeon peas', 'cowpeas',
            'rice', 'millet', 'wheat', 'barley', 'oats', 'rye',
            'potato', 'yam', 'taro', 'plantain', 'banana',
            'tomato', 'onion', 'garlic', 'pepper', 'chili',
            'cabbage', 'lettuce', 'spinach', 'kale', 'collard greens',
            'carrot', 'beetroot', 'radish', 'turnip', 'parsnip',
            'pumpkin', 'squash', 'cucumber', 'melon', 'watermelon',
            'eggplant', 'okra', 'green beans', 'peas', 'lentils',
            'sunflower', 'sesame', 'flax', 'chia', 'quinoa',
            'cotton', 'tobacco', 'sugarcane', 'coffee', 'tea',
            'mango', 'papaya', 'guava', 'pineapple', 'citrus',
            'apple', 'pear', 'peach', 'plum', 'apricot',
            'grapes', 'fig', 'pomegranate', 'mulberry', 'strawberry'
        ]
        
        # Alternative crops for variety (expanded list)
        alternative_crops = [
            'amaranth', 'quinoa', 'buckwheat', 'teff', 'fonio',
            'bambara groundnuts', 'cowpeas', 'lablab beans', 'lima beans',
            'black beans', 'navy beans', 'kidney beans', 'pinto beans',
            'chickpeas', 'lentils', 'black-eyed peas', 'mung beans',
            'adzuki beans', 'fava beans', 'sword beans', 'winged beans',
            'yam bean', 'african potato', 'cocoyam', 'dasheen',
            'eddoe', 'malanga', 'tania', 'arrowroot',
            'jerusalem artichoke', 'chinese artichoke', 'oca', 'ulluco',
            'african eggplant', 'bitter melon', 'bottle gourd', 'ridge gourd',
            'snake gourd', 'sponge gourd', 'ash gourd', 'ivy gourd',
            'african cucumber', 'horned melon', 'chayote', 'winter squash',
            'patty pan squash', 'acorn squash', 'butternut squash',
            'delicata squash', 'hubbard squash', 'kabocha squash',
            'moringa', 'baobab', 'african potato', 'african spinach',
            'jute mallow', 'spider plant', 'nightshade', 'amaranth greens',
            'purslane', 'lamb\'s quarters', 'pigweed', 'goosefoot',
            'orach', 'saltbush', 'sea beet', 'chard',
            'mizuna', 'mustard greens', 'turnip greens', 'beet greens',
            'radish greens', 'carrot greens', 'fennel', 'endive',
            'radicchio', 'arugula', 'watercress', 'upland cress',
            'garden cress', 'winter cress', 'land cress', 'rocket',
            'corn salad', 'mache', 'winter purslane', 'claytonia',
            'new zealand spinach', 'tetragonia', 'ice plant', 'samphire',
            'sea beans', 'glasswort', 'salicornia', 'sea asparagus',
            'drumstick tree', 'horseradish tree', 'ben oil tree',
            'miracle tree', 'mother\'s best friend', 'never die',
            'west indian ben', 'drumstick', 'sahjan', 'murungai',
            'malunggay', 'kamunggay', 'sajina', 'sajna', 'munaga',
            'nuggekai', 'shevaga', 'shigru', 'sohanjna', 'saijhan',
            'shajna', 'sahijan', 'munaga', 'nugge', 'drumstick',
            'horseradish', 'tree radish', 'white radish', 'daikon',
            'chinese radish', 'winter radish', 'japanese radish',
            'black radish', 'red radish', 'cherry radish', 'easter egg radish',
            'french breakfast radish', 'icicle radish', 'watermelon radish',
            'rat tail radish', 'serpent radish', 'aerial radish',
            'dill', 'parsley', 'cilantro', 'chervil', 'lovage',
            'bay leaf', 'curry leaf', 'kaffir lime', 'lemongrass', 'ginger',
            'turmeric', 'galangal', 'cardamom', 'cinnamon', 'nutmeg',
            'clove', 'allspice', 'star anise', 'fennel seed', 'cumin',
            'coriander', 'mustard', 'poppy seed', 'nigella', 'fenugreek',
            'ajwain', 'caraway', 'dill seed', 'celery seed', 'anise'
        ]
        
        # Use alternative crops if requested, otherwise use primary crops
        crops_to_find = alternative_crops if include_alternatives else primary_crops
        
        # Also search for crops mentioned in the guide content that we might have missed
        content_crops = self._extract_crops_from_content(guide_content)
        crops_to_find.extend(content_crops)
        
        # Remove duplicates while preserving order and validate crop names
        seen_crops = set()
        unique_crops = []
        for crop in crops_to_find:
            # Validate crop name before adding
            if self._is_valid_crop_name(crop) and crop not in seen_crops:
                unique_crops.append(crop)
                seen_crops.add(crop)
        
        logger.info(f"Searching for {len(unique_crops)} unique crops in guides")
        
        for crop in unique_crops:
            crop_info = self._find_crop_in_guides(guide_content, crop, season, rainfall_mm, temperature)
            if crop_info:
                # Additional validation before adding to recommendations
                if self._is_valid_recommendation(crop_info):
                    recommendations.append(crop_info)
        
        # Sort by suitability score
        recommendations.sort(key=lambda x: x.get('suitability_score', 0), reverse=True)
        
        # Apply pagination
        start_index = offset
        end_index = start_index + limit
        paginated_recommendations = recommendations[start_index:end_index]
        
        # Add pagination metadata
        total_recommendations = len(recommendations)
        has_more = end_index < total_recommendations
        
        logger.info(f"Extracted {len(paginated_recommendations)} recommendations (showing {start_index+1}-{min(end_index, total_recommendations)} of {total_recommendations})")
        
        return paginated_recommendations
    
    def _is_valid_crop_name(self, crop_name: str) -> bool:
        """Validate if a crop name is legitimate."""
        if not crop_name or not isinstance(crop_name, str):
            return False
        
        crop_name = crop_name.strip().lower()
        
        # Basic validation rules
        if (len(crop_name) < 3 or                    # Too short
            crop_name.isdigit() or                   # Just numbers
            re.match(r'^[0-9]+$', crop_name) or      # Only digits
            crop_name in ['the', 'and', 'for', 'with', 'that', 'this', 'they', 'their', 'from', 'into', 'over', 'under', 'above', 'below'] or  # Common words
            len([c for c in crop_name if c.isalpha()]) < 2):  # Not enough letters
            logger.debug(f"Rejected invalid crop name: '{crop_name}'")
            return False
        
        return True
    
    def _is_valid_recommendation(self, crop_info: Dict[str, Any]) -> bool:
        """Validate if a crop recommendation is legitimate."""
        if not crop_info or not isinstance(crop_info, dict):
            logger.debug("Rejected recommendation: Invalid crop_info structure")
            return False
        
        # Get crop name from new structure (crop_data.name) or fallback to old structure
        crop_name = crop_info.get('crop_data', {}).get('name', '')
        if not crop_name:
            crop_name = crop_info.get('crop_name', '')  # Fallback for compatibility
        
        # Get scores - try multiple fields for compatibility
        suitability_score = crop_info.get('suitability_score', 0)
        total_score = crop_info.get('total_score', 0)
        score = crop_info.get('score', 0)
        
        # Use the highest available score
        best_score = max(suitability_score, total_score, score)
        
        # Validate crop name
        if not self._is_valid_crop_name(crop_name):
            logger.debug(f"Rejected recommendation with invalid crop name: '{crop_name}'")
            return False
        
        # Validate score - must be positive
        if best_score <= 0:
            logger.debug(f"Rejected recommendation with zero/negative score: '{crop_name}' (score: {best_score})")
            return False
        
        logger.debug(f"✅ Valid recommendation: '{crop_name}' (score: {best_score})")
        return True
    
    def _extract_crops_from_content(self, guide_content: List[Dict[str, Any]]) -> List[str]:
        """Extract additional crop names mentioned in the guide content."""
        crops_found = set()
        
        # Comprehensive Malawi crop database with common name variations
        malawi_crops = {
            # Cereals
            'maize', 'corn', 'white maize', 'yellow maize', 'dent corn', 'flint corn',
            'sorghum', 'millet', 'finger millet', 'pearl millet', 'rice', 'paddy rice',
            'wheat', 'barley', 'teff',
            
            # Legumes
            'beans', 'common beans', 'kidney beans', 'navy beans', 'black beans',
            'groundnuts', 'peanuts', 'bambara nuts', 'bambara groundnuts',
            'soybeans', 'soya beans', 'soja', 'pigeon peas', 'cajanus', 
            'cowpeas', 'black-eyed peas', 'vigna', 'chickpeas', 'lentils',
            
            # Root crops and tubers
            'cassava', 'manioc', 'tapioca', 'sweet potato', 'sweet potatoes',
            'irish potato', 'potato', 'potatoes', 'yam', 'yams', 'cocoyam',
            
            # Vegetables
            'tomato', 'tomatoes', 'onion', 'onions', 'cabbage', 'lettuce',
            'spinach', 'kale', 'collard greens', 'carrot', 'carrots',
            'beetroot', 'radish', 'turnip', 'okra', 'eggplant', 'brinjal',
            'pepper', 'chili', 'bell pepper', 'green pepper',
            
            # Cucurbits
            'pumpkin', 'squash', 'cucumber', 'watermelon', 'melon',
            'cantaloupe', 'honeydew', 'zucchini', 'gourd',
            
            # Cash crops
            'tobacco', 'cotton', 'sunflower', 'sesame', 'sugarcane',
            'coffee', 'tea', 'macadamia', 'cashew nuts',
            
            # Fruits
            'banana', 'bananas', 'plantain', 'mango', 'mangoes',
            'papaya', 'pawpaw', 'guava', 'pineapple', 'avocado',
            'citrus', 'orange', 'lemon', 'lime', 'grapefruit',
            'apple', 'pear', 'peach', 'grapes', 'fig',
            
            # Other important crops
            'moringa', 'baobab', 'indigenous vegetables', 'amaranth',
            'quinoa', 'chia', 'flax', 'mustard'
        }
        
        logger.info(f"Searching for {len(malawi_crops)} known Malawi crops in content")
        
        for item in guide_content:
            content = item['content'].lower()
            
            # Direct crop name matching with word boundaries
            for crop in malawi_crops:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(crop) + r'\b'
                if re.search(pattern, content):
                    crops_found.add(crop)
                    logger.debug(f"Found crop '{crop}' in content from {item.get('source', 'unknown')}")
            
            # Additional patterns for crop mentions in agricultural context
            agricultural_patterns = [
                # "cultivation of maize", "production of beans"
                r'(?:cultivation|production|growing|farming|planting)\s+of\s+(\w+(?:\s+\w+)?)',
                # "maize varieties", "bean cultivation"
                r'(\w+(?:\s+\w+)?)\s+(?:varieties|cultivation|production|farming|planting|seeds?|crops?)',
                # "grow maize", "plant beans"  
                r'(?:grow|plant|cultivate|harvest)\s+(\w+(?:\s+\w+)?)',
                # "maize is", "beans are"
                r'(\w+(?:\s+\w+)?)\s+(?:is|are)\s+(?:a\s+)?(?:crop|plant|grain|legume|vegetable|fruit)',
                # "recommended crops: maize, beans"
                r'(?:recommended|suitable|adapted)\s+crops?:?\s*([^.]+)',
            ]
            
            for pattern in agricultural_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    
                    # Split on commas and clean each potential crop
                    potential_crops = [crop.strip().lower() for crop in match.split(',')]
                    
                    for crop in potential_crops:
                        # Clean the crop name
                        crop = re.sub(r'[^\w\s]', '', crop).strip()
                        
                        # Only add if it's in our known crops list
                        if crop in malawi_crops and len(crop) > 2:
                            crops_found.add(crop)
                            logger.debug(f"Pattern-matched crop '{crop}' from agricultural context")
        
        # Filter and validate results
        valid_crops = []
        for crop in crops_found:
            # Additional validation - reject obvious non-crops
            if (len(crop) > 2 and 
                not crop.isdigit() and 
                crop not in ['the', 'and', 'for', 'with', 'that', 'this', 'they', 'their'] and
                not re.match(r'^[0-9]+$', crop)):
                valid_crops.append(crop)
        
        logger.info(f"Extracted {len(valid_crops)} valid crops from content: {valid_crops[:10]}...")
        return list(set(valid_crops))  # Remove duplicates
    
    def _find_crop_in_guides(self, 
                           guide_content: List[Dict[str, Any]],
                           crop_name: str,
                           season: str,
                           rainfall_mm: float,
                           temperature: float) -> Optional[Dict[str, Any]]:
        """Find specific crop information in guides."""
        crop_content = []
        
        for item in guide_content:
            content = item['content'].lower()
            if crop_name in content:
                crop_content.append(item)
        
        if not crop_content:
            logger.debug(f"No content found for crop: {crop_name}")
            return None
        
        # Calculate suitability based on guide content  
        suitability_score = self._calculate_crop_suitability_from_guides(
            crop_content, crop_name, season, rainfall_mm, temperature
        )
        
        # Convert suitability (0.0-1.0) to percentage (0-100)
        score_percentage = max(1, int(suitability_score * 100))  # Minimum 1% to avoid 0 scores
        
        # Extract crop details from guides
        crop_details = self._extract_crop_details_from_guides(crop_content, crop_name)
        
        # Get primary source (most relevant)
        primary_source = crop_content[0].get('source', 'Malawi Agriculture Guide') if crop_content else 'Malawi Agriculture Guide'
        
        # Format to match expected structure (compatible with rest of system)
        return {
            'crop_data': {
                'name': crop_name.title(),
                'description': f'{crop_name.title()} recommendations from agricultural guides',
                'category': self._determine_crop_category(crop_name),
                'water_requirements': self._estimate_water_requirements(crop_name),
                'temperature_requirements': self._estimate_temperature_requirements(crop_name)
            },
            'total_score': score_percentage,
            'suitability_score': suitability_score,  # Keep original for compatibility
            'score': score_percentage,  # Alternative score field
            'source': primary_source,
            'sources': [item['source'] for item in crop_content[:3]],  # Keep plural for compatibility
            'guide_recommendations': crop_details,
            'score_components': {
                'guide_relevance': suitability_score * 40,  # Weighted components
                'content_quality': min(40, len(crop_content) * 10), 
                'seasonal_match': 20 if season in ['rainy', 'current'] else 10
            },
            'reasons': [
                f'Found in {len(crop_content)} agricultural guide(s)',
                f'Suitability score: {suitability_score:.2f}',
                f'Seasonal match for {season} season'
            ],
            'suitability_level': self._get_suitability_level_from_score(score_percentage)
        }
    
    def _determine_crop_category(self, crop_name: str) -> str:
        """Determine crop category based on crop name."""
        crop_lower = crop_name.lower()
        
        cereals = ['maize', 'corn', 'sorghum', 'millet', 'rice', 'wheat', 'barley', 'teff']
        legumes = ['beans', 'groundnuts', 'peanuts', 'soybeans', 'pigeon peas', 'cowpeas', 'chickpeas', 'lentils']
        roots_tubers = ['cassava', 'sweet potato', 'potato', 'yam', 'cocoyam']
        vegetables = ['tomato', 'onion', 'cabbage', 'lettuce', 'spinach', 'kale', 'carrot', 'pepper']
        fruits = ['banana', 'mango', 'papaya', 'guava', 'pineapple', 'citrus', 'orange', 'lemon']
        cash_crops = ['tobacco', 'cotton', 'sunflower', 'sesame', 'sugarcane', 'coffee', 'tea']
        
        if any(cereal in crop_lower for cereal in cereals):
            return 'Cereals'
        elif any(legume in crop_lower for legume in legumes):
            return 'Legumes' 
        elif any(root in crop_lower for root in roots_tubers):
            return 'Root Crops & Tubers'
        elif any(veg in crop_lower for veg in vegetables):
            return 'Vegetables'
        elif any(fruit in crop_lower for fruit in fruits):
            return 'Fruits'
        elif any(cash in crop_lower for cash in cash_crops):
            return 'Cash Crops'
        else:
            return 'Other Crops'
    
    def _estimate_water_requirements(self, crop_name: str) -> Dict[str, int]:
        """Estimate water requirements based on crop type."""
        crop_lower = crop_name.lower()
        
        # High water requirement crops
        if any(crop in crop_lower for crop in ['rice', 'sugarcane', 'banana']):
            return {'minimum_rainfall': 800, 'optimal_rainfall': 1200, 'maximum_rainfall': 2000}
        
        # Medium-high water requirement crops  
        elif any(crop in crop_lower for crop in ['maize', 'corn', 'beans', 'tomato']):
            return {'minimum_rainfall': 500, 'optimal_rainfall': 800, 'maximum_rainfall': 1500}
        
        # Medium water requirement crops
        elif any(crop in crop_lower for crop in ['groundnuts', 'peanuts', 'sweet potato']):
            return {'minimum_rainfall': 400, 'optimal_rainfall': 600, 'maximum_rainfall': 1200}
        
        # Low water requirement crops
        elif any(crop in crop_lower for crop in ['sorghum', 'millet', 'cassava']):
            return {'minimum_rainfall': 250, 'optimal_rainfall': 500, 'maximum_rainfall': 1000}
        
        # Default medium requirements
        else:
            return {'minimum_rainfall': 400, 'optimal_rainfall': 700, 'maximum_rainfall': 1300}
    
    def _estimate_temperature_requirements(self, crop_name: str) -> Dict[str, int]:
        """Estimate temperature requirements based on crop type."""
        crop_lower = crop_name.lower()
        
        # Cool season crops
        if any(crop in crop_lower for crop in ['wheat', 'barley', 'peas']):
            return {'minimum_temp': 10, 'optimal_temp': 18, 'maximum_temp': 25}
        
        # Warm season crops
        elif any(crop in crop_lower for crop in ['maize', 'corn', 'sorghum', 'millet']):
            return {'minimum_temp': 15, 'optimal_temp': 25, 'maximum_temp': 35}
        
        # Hot season crops
        elif any(crop in crop_lower for crop in ['cassava', 'sweet potato', 'mango']):
            return {'minimum_temp': 18, 'optimal_temp': 28, 'maximum_temp': 38}
        
        # Default moderate requirements
        else:
            return {'minimum_temp': 15, 'optimal_temp': 22, 'maximum_temp': 30}
    
    def _get_suitability_level_from_score(self, score: int) -> str:
        """Get suitability level from percentage score."""
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Moderate'
        elif score >= 20:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def _calculate_crop_suitability_from_guides(self, 
                                              crop_content: List[Dict[str, Any]],
                                              crop_name: str,
                                              season: str,
                                              rainfall_mm: float,
                                              temperature: float) -> float:
        """Calculate crop suitability based on guide content."""
        suitability = 0.5  # Base score
        
        for item in crop_content:
            content = item['content'].lower()
            
            # Season suitability
            if season == 'rainy_season' and ('rainy' in content or 'wet' in content):
                suitability += 0.1
            elif season == 'dry_season' and ('dry' in content or 'drought' in content):
                suitability += 0.1
            
            # Rainfall suitability
            if rainfall_mm < 100 and ('drought' in content or 'low rainfall' in content):
                suitability += 0.1
            elif rainfall_mm > 500 and ('high rainfall' in content or 'flood' in content):
                suitability += 0.1
            
            # Temperature suitability
            if temperature < 20 and ('cool' in content or 'cold' in content):
                suitability += 0.1
            elif temperature > 30 and ('heat' in content or 'warm' in content):
                suitability += 0.1
        
        return min(1.0, suitability)
    
    def _extract_crop_details_from_guides(self, 
                                        crop_content: List[Dict[str, Any]],
                                        crop_name: str) -> List[str]:
        """Extract specific crop details from guide content."""
        details = []
        
        for item in crop_content:
            content = item['content']
            # Extract sentences containing crop information
            sentences = content.split('.')
            for sentence in sentences:
                if crop_name in sentence.lower() and len(sentence.strip()) > 20:
                    details.append(sentence.strip())
        
        return details[:5]  # Top 5 details
    
    def _extract_planting_advice(self, 
                               guide_content: List[Dict[str, Any]],
                               season: str,
                               historical_data: Optional[HistoricalRainfallData]) -> Dict[str, Any]:
        """Extract planting advice from guides."""
        planting_advice = {
            'timing': [],
            'methods': [],
            'considerations': []
        }
        
        for item in guide_content:
            content = item['content'].lower()
            
            # Extract planting timing advice
            if 'planting' in content and ('time' in content or 'season' in content):
                sentences = item['content'].split('.')
                for sentence in sentences:
                    if 'planting' in sentence.lower() and len(sentence.strip()) > 20:
                        planting_advice['timing'].append(sentence.strip())
            
            # Extract planting methods
            if 'planting' in content and ('method' in content or 'technique' in content):
                sentences = item['content'].split('.')
                for sentence in sentences:
                    if 'planting' in sentence.lower() and len(sentence.strip()) > 20:
                        planting_advice['methods'].append(sentence.strip())
        
        # Add historical data insights
        if historical_data:
            if historical_data.climate_trend == 'increasing':
                planting_advice['considerations'].append(
                    "Historical data shows increasing rainfall trends. Consider early planting to take advantage of longer growing seasons."
                )
            elif historical_data.climate_trend == 'decreasing':
                planting_advice['considerations'].append(
                    "Historical data shows decreasing rainfall trends. Consider drought-resistant varieties and water conservation techniques."
                )
        
        return planting_advice
    
    def _extract_management_tips(self, 
                               guide_content: List[Dict[str, Any]],
                               season: str,
                               rainfall_mm: float,
                               temperature: float) -> List[str]:
        """Extract management tips from guides."""
        tips = []
        
        for item in guide_content:
            content = item['content'].lower()
            
            # Look for management-related content
            management_keywords = ['management', 'care', 'maintenance', 'pest', 'disease', 'fertilizer']
            if any(keyword in content for keyword in management_keywords):
                sentences = item['content'].split('.')
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in management_keywords):
                        if len(sentence.strip()) > 20:
                            tips.append(sentence.strip())
        
        return tips[:10]  # Top 10 tips
    
    def _extract_risk_assessment(self, 
                               guide_content: List[Dict[str, Any]],
                               season: str,
                               rainfall_mm: float,
                               temperature: float,
                               historical_data: Optional[HistoricalRainfallData]) -> Dict[str, Any]:
        """Extract risk assessment from guides."""
        risks = {
            'weather_risks': [],
            'pest_risks': [],
            'disease_risks': [],
            'market_risks': [],
            'overall_risk_level': 'moderate'
        }
        
        for item in guide_content:
            content = item['content'].lower()
            
            # Weather risks
            if 'drought' in content or 'flood' in content or 'rainfall' in content:
                sentences = item['content'].split('.')
                for sentence in sentences:
                    if ('drought' in sentence.lower() or 'flood' in sentence.lower() or 'rainfall' in sentence.lower()):
                        if len(sentence.strip()) > 20:
                            risks['weather_risks'].append(sentence.strip())
            
            # Pest risks
            if 'pest' in content:
                sentences = item['content'].split('.')
                for sentence in sentences:
                    if 'pest' in sentence.lower() and len(sentence.strip()) > 20:
                        risks['pest_risks'].append(sentence.strip())
            
            # Disease risks
            if 'disease' in content:
                sentences = item['content'].split('.')
                for sentence in sentences:
                    if 'disease' in sentence.lower() and len(sentence.strip()) > 20:
                        risks['disease_risks'].append(sentence.strip())
        
        # Determine overall risk level
        total_risks = len(risks['weather_risks']) + len(risks['pest_risks']) + len(risks['disease_risks'])
        if total_risks > 10:
            risks['overall_risk_level'] = 'high'
        elif total_risks > 5:
            risks['overall_risk_level'] = 'moderate'
        else:
            risks['overall_risk_level'] = 'low'
        
        return risks

    def clear_ai_cache(self):
        """Clear the AI response cache to force fresh responses."""
        try:
            from scripts.ai_agent.gpt_integration import gpt_integration
            gpt_integration.clear_cache()
            logger.info("AI response cache cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to clear AI cache: {e}")
            return False
    
    def debug_database_content(self, limit: int = 5) -> Dict[str, Any]:
        """Debug method to inspect database content and crop extraction."""
        debug_info = {
            'database_stats': {},
            'sample_content': [],
            'crop_extraction_test': {},
            'recommendations': 0
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get database statistics
                cursor.execute("SELECT COUNT(*) as total FROM documents")
                total_docs = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT source) as unique_sources FROM documents")
                unique_sources = cursor.fetchone()[0]
                
                debug_info['database_stats'] = {
                    'total_documents': total_docs,
                    'unique_sources': unique_sources
                }
                
                # Get sample content
                cursor.execute("SELECT content, source FROM documents ORDER BY RANDOM() LIMIT ?", (limit,))
                for content, source in cursor.fetchall():
                    debug_info['sample_content'].append({
                        'source': source,
                        'content_preview': content[:200] + "..." if len(content) > 200 else content,
                        'content_length': len(content)
                    })
                
                # Test crop extraction on sample content
                sample_data = [{'content': row['content_preview'], 'source': row['source']} for row in debug_info['sample_content']]
                extracted_crops = self._extract_crops_from_content(sample_data)
                debug_info['crop_extraction_test'] = {
                    'extracted_crops': extracted_crops[:20],  # First 20 crops
                    'total_extracted': len(extracted_crops)
                }
                
                logger.info(f"Database debug completed - {total_docs} docs, {unique_sources} sources, {len(extracted_crops)} crops extracted")
                
        except Exception as e:
            logger.error(f"Database debug failed: {e}")
            debug_info['error'] = str(e)
        
        return debug_info
    
    def _calculate_crop_relevance(self, text: str, crop_name: str, season: str, rainfall_mm: float, temperature: float) -> float:
        """
        Calculate relevance score for crop-specific content.
        
        Args:
            text: Text content to analyze
            crop_name: Name of the specific crop
            season: Current season
            rainfall_mm: Current rainfall
            temperature: Current temperature
            
        Returns:
            Relevance score between 0 and 1
        """
        score = 0.0
        text_lower = text.lower()
        crop_lower = crop_name.lower()
        
        # Direct crop name mentions
        if crop_lower in text_lower:
            score += 0.4
        
        # Crop-specific terms
        crop_terms = [f"{crop_lower} cultivation", f"{crop_lower} farming", f"{crop_lower} planting", 
                      f"{crop_lower} varieties", f"{crop_lower} management", f"{crop_lower} yield"]
        for term in crop_terms:
            if term in text_lower:
                score += 0.1
        
        # Season relevance
        if season in text_lower:
            score += 0.1
        
        # Environmental conditions relevance
        if any(condition in text_lower for condition in ['rainfall', 'temperature', 'climate', 'weather']):
            score += 0.1
        
        # Management and cultivation terms
        if any(term in text_lower for term in ['planting', 'harvesting', 'fertilizer', 'irrigation', 'pest', 'disease']):
            score += 0.1
        
        # Length bonus (more detailed content)
        if len(text) > 200:
            score += 0.1
        
        return min(score, 1.0)
    
    def _analyze_crop_suitability(self, crop_name: str, crop_guides: List[Dict[str, Any]], season: str, rainfall_mm: float, temperature: float) -> Dict[str, Any]:
        """
        Analyze crop suitability based on guide content and environmental conditions.
        
        Args:
            crop_name: Name of the crop
            crop_guides: Guide content for the crop
            season: Current season
            rainfall_mm: Current rainfall
            temperature: Current temperature
            
        Returns:
            Suitability analysis results
        """
        # Get crop requirements
        water_req = self._estimate_water_requirements(crop_name)
        temp_req = self._estimate_temperature_requirements(crop_name)
        
        # Analyze rainfall suitability
        if rainfall_mm >= water_req['minimum_rainfall'] and rainfall_mm <= water_req['maximum_rainfall']:
            if rainfall_mm >= water_req['optimal_rainfall'] * 0.8 and rainfall_mm <= water_req['optimal_rainfall'] * 1.2:
                rainfall_match = 'excellent'
                rainfall_score = 1.0
            else:
                rainfall_match = 'good'
                rainfall_score = 0.8
        elif rainfall_mm >= water_req['minimum_rainfall'] * 0.7:
            rainfall_match = 'fair'
            rainfall_score = 0.6
        else:
            rainfall_match = 'poor'
            rainfall_score = 0.3
        
        # Analyze temperature suitability
        if temperature >= temp_req['minimum_temp'] and temperature <= temp_req['maximum_temp']:
            if temperature >= temp_req['optimal_temp'] * 0.9 and temperature <= temp_req['optimal_temp'] * 1.1:
                temperature_match = 'excellent'
                temperature_score = 1.0
            else:
                temperature_match = 'good'
                temperature_score = 0.8
        elif temperature >= temp_req['minimum_temp'] * 0.8:
            temperature_match = 'fair'
            temperature_score = 0.6
        else:
            temperature_match = 'poor'
            temperature_score = 0.3
        
        # Analyze season suitability
        season_score = 0.7  # Default moderate suitability
        season_match = 'good'
        
        # Check guide content for season-specific information
        for guide in crop_guides:
            text_lower = guide['text'].lower()
            if season in text_lower:
                season_score = 0.9
                season_match = 'excellent'
                break
            elif any(term in text_lower for term in ['planting', 'cultivation', 'growing']):
                season_score = 0.8
                season_match = 'good'
        
        # Calculate overall suitability score
        overall_score = (rainfall_score * 0.4 + temperature_score * 0.3 + season_score * 0.3)
        
        # Determine suitability level
        if overall_score >= 0.8:
            level = 'excellent'
        elif overall_score >= 0.6:
            level = 'good'
        elif overall_score >= 0.4:
            level = 'fair'
        else:
            level = 'poor'
        
        return {
            'score': overall_score,
            'level': level,
            'rainfall_match': rainfall_match,
            'temperature_match': temperature_match,
            'season_match': season_match
        }
    
    def _extract_crop_information(self, crop_name: str, crop_guides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract crop-specific information from guide content.
        
        Args:
            crop_name: Name of the crop
            crop_guides: Guide content for the crop
            
        Returns:
            Extracted crop information
        """
        sources = set()
        recommendations = []
        varieties = []
        management_tips = []
        risk_assessment = {'weather_risks': [], 'pest_risks': [], 'disease_risks': []}
        
        planting_time = 'Not specified'
        yield_potential = 'Not specified'
        description = f'{crop_name.title()} cultivation information'
        
        for guide in crop_guides:
            text = guide['text']
            source = guide['source_doc']
            sources.add(source)
            
            # Extract recommendations
            if any(term in text.lower() for term in ['recommend', 'suggest', 'advise', 'should', 'best practice']):
                recommendations.append(text[:200] + '...' if len(text) > 200 else text)
            
            # Extract varieties
            if 'variety' in text.lower() or 'cultivar' in text.lower():
                # Simple extraction of variety names
                import re
                variety_matches = re.findall(r'\b[A-Z]{2,}\d+\b|\b[A-Z]+\d+\b', text)
                varieties.extend(variety_matches[:3])  # Limit to 3 varieties
            
            # Extract management tips
            if any(term in text.lower() for term in ['management', 'care', 'maintenance', 'fertilizer', 'irrigation']):
                management_tips.append(text[:150] + '...' if len(text) > 150 else text)
            
            # Extract risk information
            if 'risk' in text.lower() or 'pest' in text.lower() or 'disease' in text.lower():
                if 'weather' in text.lower() or 'rainfall' in text.lower() or 'temperature' in text.lower():
                    risk_assessment['weather_risks'].append(text[:100] + '...' if len(text) > 100 else text)
                elif 'pest' in text.lower():
                    risk_assessment['pest_risks'].append(text[:100] + '...' if len(text) > 100 else text)
                elif 'disease' in text.lower():
                    risk_assessment['disease_risks'].append(text[:100] + '...' if len(text) > 100 else text)
            
            # Extract planting time
            if 'planting' in text.lower() and ('month' in text.lower() or 'season' in text.lower()):
                planting_time = 'See guide recommendations'
            
            # Extract yield information
            if 'yield' in text.lower() and ('ton' in text.lower() or 'kg' in text.lower()):
                yield_potential = 'See guide recommendations'
        
        # Limit lists to prevent overwhelming output
        recommendations = recommendations[:5]
        management_tips = management_tips[:5]
        varieties = list(set(varieties))[:5]  # Remove duplicates
        
        return {
            'sources': list(sources),
            'recommendations': recommendations,
            'varieties': varieties,
            'management_tips': management_tips,
            'risk_assessment': risk_assessment,
            'planting_time': planting_time,
            'yield_potential': yield_potential,
            'description': description,
            'planting_advice': {
                'optimal_planting_time': planting_time,
                'soil_preparation': 'See guide recommendations',
                'spacing': 'See guide recommendations'
            }
        }
    
    def _get_region_name(self, lat: float, lon: float) -> str:
        """
        Get region name based on coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Region name
        """
        # Malawi regions based on coordinates
        if -16.0 <= lat <= -13.0 and 32.0 <= lon <= 35.0:
            if lat >= -14.5:
                return 'Central Region'
            elif lat >= -15.5:
                return 'Southern Region'
            else:
                return 'Northern Region'
        else:
            return 'Unknown Region'


# Create global instance
sqlite_recommendation_engine = SQLiteBasedRecommendationEngine() 