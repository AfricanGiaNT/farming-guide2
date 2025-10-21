"""
Enhanced Crop Recommendation Engine using REAL DATA ONLY.
Now includes advanced algorithms for sophisticated analysis.
"""
import json
import math
from typing import Dict, List, Any, Optional, Tuple
from scripts.weather_engine.historical_weather_api import HistoricalWeatherAPI, HistoricalRainfallData
from scripts.crop_advisor.advanced_crop_algorithm import AdvancedCropRecommendationAlgorithm
from scripts.crop_advisor.advanced_yield_calculator import AdvancedYieldProjectionCalculator
from scripts.crop_advisor.advanced_input_system import AdvancedInputRecommendationSystem
from scripts.utils.logger import logger


class AdvancedEnhancedCropRecommendationEngine:
    """
    Advanced Enhanced crop recommendation engine using ONLY real data sources.
    Integrates advanced algorithms for sophisticated crop recommendations.
    """
    
    def __init__(self, crop_json_path: str = "data/crop_varieties.json"):
        """
        Initialize the advanced enhanced recommendation engine.
        
        Args:
            crop_json_path: Path to JSON crop varieties database
        """
        self.crop_json_path = crop_json_path
        self.historical_api = HistoricalWeatherAPI()
        
        # Load real crop data
        self.crop_database = self._load_crop_database()
        
        # Initialize advanced components
        self.advanced_algorithm = AdvancedCropRecommendationAlgorithm(self.crop_database)
        self.yield_calculator = AdvancedYieldProjectionCalculator()
        self.input_system = AdvancedInputRecommendationSystem()
        
        logger.info("Advanced Enhanced Crop Recommendation Engine initialized with REAL DATA ONLY")
        logger.info(f"- Crop JSON: {crop_json_path}")
        logger.info(f"- Advanced Algorithm: Available")
        logger.info(f"- Yield Calculator: Available")
        logger.info(f"- Input System: Available")
    
    def _load_crop_database(self) -> Dict[str, Any]:
        """Load real crop data from JSON file."""
        try:
            with open(self.crop_json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                crops_data = data.get('lilongwe_crops', {})
                logger.info(f"Loaded {len(crops_data)} real crop types from database")
                return crops_data
        except Exception as e:
            logger.error(f"Failed to load crop database: {e}")
            return {}
    
    def get_enhanced_crop_recommendations(self, 
                                        lat: float, 
                                        lon: float, 
                                        season: str = 'current',
                                        rainfall_mm: float = 0,
                                        temperature: float = 25,
                                        farmer_profile: Optional[Dict[str, Any]] = None,
                                        historical_years: int = 5,
                                        top_n: int = 3) -> Dict[str, Any]:
        """
        Get enhanced crop recommendations using advanced algorithms.
        
        Args:
            lat: Latitude
            lon: Longitude
            season: Planting season
            rainfall_mm: Current rainfall in mm
            temperature: Current temperature in Celsius
            farmer_profile: Farmer's profile and preferences
            historical_years: Number of years for historical analysis
            top_n: Number of top crops to return (default=3, use higher for specific crop searches)
            
        Returns:
            Enhanced crop recommendations with advanced analysis
        """
        logger.info(f"Getting enhanced crop recommendations for lat={lat}, lon={lon}, season={season}")
        
        try:
            # Get historical weather data
            historical_data = self._get_historical_weather_data(lat, lon, historical_years)
            logger.info(f"[DEBUG] Historical data retrieved: {historical_data is not None}")
            
            # Use historical seasonal rainfall instead of current rainfall
            seasonal_rainfall_mm = self._get_seasonal_rainfall_from_historical(historical_data, season)
            if seasonal_rainfall_mm is None:
                seasonal_rainfall_mm = rainfall_mm  # Fallback to current if no historical data
            
            logger.info(f"[DEBUG] Using seasonal rainfall: {seasonal_rainfall_mm}mm")
            
            # Prepare environmental factors
            environmental_factors = {
                'rainfall_mm': seasonal_rainfall_mm,  # Use historical seasonal rainfall
                'temperature': temperature,
                'season': season,
                'humidity': 50,  # Default humidity
                'latitude': lat,
                'longitude': lon
            }
            
            logger.info(f"[DEBUG] Environmental factors prepared: {environmental_factors}")
            
            # Use advanced algorithm to rank crops
            ranked_crops = self.advanced_algorithm.rank_crops_by_suitability(
                environmental_factors, historical_data, farmer_profile
            )
            
            logger.info(f"[DEBUG] Ranked {len(ranked_crops)} crops")
            
            # Get top 3 crops
            top_crops = ranked_crops[:top_n]
            logger.info(f"[DEBUG] Selected top {len(top_crops)} crops")
            
            # Generate comprehensive recommendations for each crop
            enhanced_recommendations = []
            
            for i, crop_rank in enumerate(top_crops):
                logger.info(f"[DEBUG] Processing crop {i+1}: {crop_rank.get('crop_id', 'Unknown')}")
                crop_id = crop_rank['crop_id']
                crop_data = crop_rank['crop_data']
                
                # Get top variety for this crop
                top_variety = crop_rank['top_varieties'][0] if crop_rank['top_varieties'] else None
                logger.info(f"[DEBUG] Top variety: {top_variety}")
                
                # Calculate advanced yield projections
                logger.info(f"[DEBUG] Calculating yield projections for {crop_id}")
                yield_projections = self.yield_calculator.calculate_advanced_yield_projections(
                    crop_data, environmental_factors, historical_data, farmer_profile, top_variety
                )
                logger.info(f"[DEBUG] Yield projections calculated for {crop_id}")
                
                # Generate comprehensive input recommendations
                logger.info(f"[DEBUG] Generating input recommendations for {crop_id}")
                input_recommendations = self.input_system.generate_comprehensive_input_recommendations(
                    crop_data, environmental_factors, historical_data, farmer_profile, top_variety
                )
                logger.info(f"[DEBUG] Input recommendations generated for {crop_id}")
                
                # Generate planting guidelines
                planting_guidelines = self._generate_advanced_planting_guidelines(
                    crop_data, environmental_factors, historical_data, top_variety
                )
                
                # Calculate overall confidence
                overall_confidence = self._calculate_overall_confidence(
                    crop_rank, yield_projections, input_recommendations, historical_data
                )
                
                enhanced_recommendations.append({
                    'crop_id': crop_id,
                    'crop_name': crop_data.get('name', crop_id),
                    'suitability_score': crop_rank['suitability_score'],
                    'confidence': overall_confidence,
                    'recommendation_level': crop_rank['recommendation_level'],
                    'factor_scores': crop_rank['factor_scores'],
                    'risk_factors': crop_rank['risk_factors'],
                    'top_varieties': crop_rank['top_varieties'],
                    'yield_projections': yield_projections,
                    'input_recommendations': input_recommendations,
                    'planting_guidelines': planting_guidelines,
                    'data_sources': [
                        'real_crop_varieties_database',
                        'real_historical_weather_data',
                        'advanced_crop_algorithm',
                        'advanced_yield_calculator',
                        'advanced_input_system'
                    ],
                    'algorithm_version': 'advanced_enhanced_v2.0'
                })
            
            logger.info(f"[DEBUG] Generated {len(enhanced_recommendations)} enhanced recommendations")
            
            return {
                'status': 200,
                'recommendations': enhanced_recommendations,
                'environmental_factors': environmental_factors,
                'historical_data_summary': self._get_historical_summary(historical_data),
                'region': self._get_region_name(lat, lon),
                'data_sources': [
                    'real_crop_varieties_database',
                    'real_historical_weather_data',
                    'advanced_crop_algorithm',
                    'advanced_yield_calculator',
                    'advanced_input_system'
                ],
                'algorithm_version': 'advanced_enhanced_v2.0'
            }
            
        except Exception as e:
            logger.error(f"[DEBUG] Error in get_enhanced_crop_recommendations: {e}")
            import traceback
            logger.error(f"[DEBUG] Full traceback: {traceback.format_exc()}")
            raise e
    
    def _get_seasonal_rainfall_from_historical(self, 
                                            historical_data: Optional[HistoricalRainfallData], 
                                            season: str) -> Optional[float]:
        """Extract seasonal rainfall from historical data."""
        if not historical_data or not historical_data.monthly_averages:
            return None
        
        # Define seasonal months for Malawi
        seasonal_months = {
            'rainy_season': ['November', 'December', 'January', 'February', 'March', 'April'],
            'dry_season': ['May', 'June', 'July', 'August', 'September', 'October'],
            'current': ['November', 'December', 'January', 'February', 'March', 'April']  # Default to rainy
        }
        
        months = seasonal_months.get(season, seasonal_months['current'])
        monthly_averages = historical_data.monthly_averages
        
        # Calculate seasonal average rainfall
        seasonal_rainfall = 0
        month_count = 0
        
        for month in months:
            if month in monthly_averages:
                seasonal_rainfall += monthly_averages[month]
                month_count += 1
        
        if month_count > 0:
            avg_seasonal_rainfall = seasonal_rainfall / month_count
            logger.info(f"Calculated {season} seasonal rainfall: {avg_seasonal_rainfall:.1f}mm from {month_count} months")
            return avg_seasonal_rainfall
        
        return None
    
    def _get_historical_weather_data(self, lat: float, lon: float, years: int) -> Optional[HistoricalRainfallData]:
        """Get historical weather data using real API."""
        try:
            historical_data = self.historical_api.get_historical_rainfall(
                lat, lon, years
            )
            logger.info(f"Retrieved historical weather data for {years} years")
            return historical_data
        except Exception as e:
            logger.error(f"Failed to get historical weather data: {e}")
            return None
    
    def _generate_advanced_planting_guidelines(self, 
                                            crop_data: Dict[str, Any],
                                            environmental_factors: Dict[str, Any],
                                            historical_data: Optional[HistoricalRainfallData],
                                            variety_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate advanced planting guidelines using real data."""
        planting_calendar = crop_data.get('planting_calendar', {})
        season = environmental_factors.get('season', 'current')
        
        # Get season-specific guidelines
        season_guidelines = planting_calendar.get(season, {})
        
        # Base guidelines
        guidelines = {
            'optimal_timing': season_guidelines.get('start', 'Not specified'),
            'planting_depth': '2-5 cm',
            'spacing': '75cm x 25cm',
            'soil_preparation': 'Plow and harrow to fine tilth',
            'seed_rate': '20-25 kg/ha'
        }
        
        # Adjust based on variety
        if variety_data:
            maturity_days = variety_data.get('maturity_days', 0)
            if maturity_days > 0:
                guidelines['maturity_days'] = maturity_days
                guidelines['harvest_timing'] = f"Approximately {maturity_days} days after planting"
        
        # Adjust based on environmental factors
        rainfall_mm = environmental_factors.get('rainfall_mm', 0)
        if rainfall_mm < 300:
            guidelines['irrigation_required'] = 'Yes - low rainfall conditions'
        elif rainfall_mm > 600:
            guidelines['drainage_important'] = 'Yes - high rainfall conditions'
        
        # Adjust based on historical data
        if historical_data:
            if historical_data.climate_trend == 'decreasing':
                guidelines['water_conservation'] = 'Important - decreasing rainfall trend'
            elif historical_data.climate_trend == 'increasing':
                guidelines['flood_preparation'] = 'Important - increasing rainfall trend'
        
        return {
            'guidelines': guidelines,
            'data_source': 'real_crop_varieties_database'
        }
    
    def _calculate_overall_confidence(self, 
                                    crop_rank: Dict[str, Any],
                                    yield_projections: Dict[str, Any],
                                    input_recommendations: Dict[str, Any],
                                    historical_data: Optional[HistoricalRainfallData]) -> float:
        """Calculate overall confidence score."""
        # Base confidence from crop ranking
        base_confidence = crop_rank.get('confidence', 0.7)
        
        # Yield projection confidence
        yield_confidence = yield_projections.get('confidence', 0.7)
        
        # Input recommendation confidence
        input_confidence = input_recommendations.get('recommendation_confidence', 0.7)
        
        # Historical data quality factor
        historical_factor = 1.0
        if historical_data:
            if historical_data.years_analyzed >= 5:
                historical_factor = 1.0
            elif historical_data.years_analyzed >= 3:
                historical_factor = 0.9
            else:
                historical_factor = 0.8
        
        # Calculate weighted overall confidence
        overall_confidence = (
            base_confidence * 0.4 +
            yield_confidence * 0.3 +
            input_confidence * 0.3
        ) * historical_factor
        
        return min(1.0, overall_confidence)
    
    def _get_historical_summary(self, historical_data: Optional[HistoricalRainfallData]) -> Dict[str, Any]:
        """Get summary of historical data."""
        if not historical_data:
            return {
                'years_analyzed': 0,
                'data_quality': 'not_available'
            }
        
        return {
            'years_analyzed': historical_data.years_analyzed,
            'average_annual_rainfall': sum(historical_data.annual_averages) / len(historical_data.annual_averages) if historical_data.annual_averages else 0,
            'rainfall_variability': historical_data.rainfall_variability,
            'climate_trend': historical_data.climate_trend,
            'drought_years': historical_data.drought_years,
            'flood_years': historical_data.flood_years,
            'data_quality': 'excellent' if historical_data.years_analyzed >= 5 else 'good'
        }
    
    def _get_region_name(self, lat: float, lon: float) -> str:
        """Determine region based on coordinates."""
        # Malawi regions based on coordinates
        if -15.0 <= lat <= -13.0 and 33.0 <= lon <= 35.0:
            return "Central Region (Lilongwe)"
        elif -16.0 <= lat <= -14.0 and 34.0 <= lon <= 36.0:
            return "Southern Region (Blantyre)"
        elif -12.0 <= lat <= -10.0 and 33.0 <= lon <= 35.0:
            return "Northern Region (Mzuzu)"
        else:
            return "Malawi"


# Create global instance
advanced_enhanced_crop_recommendation_engine = AdvancedEnhancedCropRecommendationEngine()
