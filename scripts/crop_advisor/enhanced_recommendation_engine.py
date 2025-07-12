"""
Enhanced Crop Recommendation Engine for the Agricultural Advisor Bot.
Week 5 implementation with 10-factor scoring system and comprehensive analysis.
"""

import datetime
from typing import Dict, List, Any, Optional, Tuple
from scripts.crop_advisor.crop_database import crop_database
from scripts.crop_advisor.recommendation_engine import CropRecommendationEngine
from scripts.crop_advisor.confidence_scorer import ConfidenceScorer
from scripts.crop_advisor.planting_calendar import PlantingCalendar
from scripts.crop_advisor.pdf_enhanced_varieties import PDFEnhancedVarieties
from scripts.utils.logger import logger


class EnhancedRecommendationEngine(CropRecommendationEngine):
    """Enhanced crop recommendation engine with 10-factor analysis and confidence scoring."""
    
    def __init__(self):
        """Initialize the enhanced recommendation engine."""
        super().__init__()
        self.confidence_scorer = ConfidenceScorer()
        self.planting_calendar = PlantingCalendar()
        self.pdf_varieties = PDFEnhancedVarieties()
        
        # Market demand scoring data (simplified for MVP)
        self.market_demand_scores = {
            'maize': 5,  # High demand
            'beans': 4,  # Good demand
            'groundnuts': 4,  # Good demand
            'sorghum': 3,  # Moderate demand
            'cassava': 3,  # Moderate demand
            'sweet_potato': 2  # Lower demand
        }
        
        # Input availability scoring (simplified)
        self.input_availability_scores = {
            'maize': 5,  # High availability
            'beans': 4,  # Good availability
            'groundnuts': 4,  # Good availability
            'sorghum': 3,  # Moderate availability
            'cassava': 5,  # High availability
            'sweet_potato': 5  # High availability
        }
        
        logger.info("Enhanced recommendation engine initialized with 10-factor scoring")
    
    def generate_recommendations(self, 
                               rainfall_data: Dict[str, Any], 
                               weather_data: Dict[str, Any],
                               lat: float, 
                               lon: float,
                               user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate enhanced crop recommendations with 10-factor scoring.
        
        Args:
            rainfall_data: Rainfall analysis data
            weather_data: Current weather data
            lat: Latitude
            lon: Longitude
            user_preferences: Optional user preferences
            
        Returns:
            Enhanced recommendation results with confidence scoring
        """
        logger.info(f"Generating enhanced recommendations for coordinates: {lat}, {lon}")
        
        # Validate inputs
        if not self._validate_inputs(rainfall_data, weather_data, lat, lon):
            return {'error': 'Invalid input data provided'}
        
        # Extract environmental data
        total_rainfall = rainfall_data.get('total_7day_rainfall', 0)
        forecast_rainfall = rainfall_data.get('forecast_7day_rainfall', 0)
        current_temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 50)
        rainy_days = rainfall_data.get('rainy_days_forecast', 0)
        
        # Calculate seasonal rainfall estimate
        seasonal_rainfall = self._estimate_seasonal_rainfall(total_rainfall, forecast_rainfall)
        
        # Get current season
        current_season = self.crop_db.get_current_season(self.current_month)
        
        # Generate enhanced recommendations for each crop
        enhanced_crop_scores = []
        all_crops = self.crop_db.get_all_crops()
        
        for crop_id, crop_data in all_crops.items():
            enhanced_score_data = self._calculate_enhanced_crop_score(
                crop_id, crop_data, seasonal_rainfall, current_temp, 
                humidity, rainy_days, current_season, lat, lon
            )
            enhanced_crop_scores.append(enhanced_score_data)
        
        # Sort by total score
        enhanced_crop_scores.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Add confidence scoring to each recommendation
        scored_recommendations = []
        for crop_score in enhanced_crop_scores:
            confidence_data = self.confidence_scorer.calculate_confidence({
                'crop_data': crop_score,
                'weather_data': weather_data,
                'rainfall_data': rainfall_data,
                'data_age': 1  # Assuming 1 hour old data
            })
            
            crop_score['confidence_score'] = confidence_data['confidence_score']
            crop_score['confidence_level'] = confidence_data['confidence_level']
            crop_score['data_quality'] = confidence_data['data_quality']
            
            scored_recommendations.append(crop_score)
        
        # Get top recommendations with varieties
        top_recommendations = self._add_enhanced_variety_recommendations(
            scored_recommendations[:5], seasonal_rainfall, current_temp, lat, lon
        )
        
        # Generate enhanced planting calendar
        planting_calendar = self._generate_enhanced_planting_calendar(
            scored_recommendations[:3], self.current_month, lat, lon
        )
        
        # Generate seasonal advice
        seasonal_advice = self._generate_seasonal_advice(
            current_season, seasonal_rainfall, current_temp
        )
        
        return {
            'recommendations': top_recommendations,
            'planting_calendar': planting_calendar,
            'seasonal_advice': seasonal_advice,
            'environmental_summary': {
                'total_7day_rainfall': total_rainfall,
                'forecast_7day_rainfall': forecast_rainfall,
                'estimated_seasonal_rainfall': seasonal_rainfall,
                'current_temperature': current_temp,
                'humidity': humidity,
                'rainy_days_forecast': rainy_days,
                'current_season': current_season,
                'current_month': self.current_month
            },
            'analysis_timestamp': datetime.datetime.now().isoformat()
        }
    
    def generate_comprehensive_recommendations(self, 
                                            rainfall_data: Dict[str, Any], 
                                            weather_data: Dict[str, Any],
                                            lat: float, 
                                            lon: float,
                                            user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive recommendations with all enhanced components.
        
        Args:
            rainfall_data: Rainfall analysis data
            weather_data: Current weather data
            lat: Latitude
            lon: Longitude
            user_preferences: Optional user preferences
            
        Returns:
            Comprehensive recommendation results
        """
        # Get basic enhanced recommendations
        basic_recommendations = self.generate_recommendations(
            rainfall_data, weather_data, lat, lon, user_preferences
        )
        
        if 'error' in basic_recommendations:
            return basic_recommendations
        
        # Add PDF-enhanced varieties
        pdf_enhanced_varieties = self.pdf_varieties.get_pdf_enhanced_varieties(
            basic_recommendations['recommendations'][:3],
            location='Lilongwe',
            conditions={'rainfall': rainfall_data.get('total_7day_rainfall', 0)}
        )
        
        # Get detailed planting calendar
        detailed_calendar = self.planting_calendar.get_monthly_recommendations(
            month=self.current_month,
            location=(lat, lon),
            weather_forecast=weather_data
        )
        
        return {
            'enhanced_recommendations': basic_recommendations['recommendations'],
            'confidence_scores': [r['confidence_score'] for r in basic_recommendations['recommendations']],
            'planting_calendar': detailed_calendar,
            'pdf_enhanced_varieties': pdf_enhanced_varieties,
            'environmental_summary': basic_recommendations['environmental_summary'],
            'seasonal_advice': basic_recommendations['seasonal_advice'],
            'analysis_timestamp': datetime.datetime.now().isoformat()
        }
    
    def _calculate_enhanced_crop_score(self, 
                                     crop_id: str, 
                                     crop_data: Dict[str, Any], 
                                     seasonal_rainfall: float,
                                     current_temp: float,
                                     humidity: float,
                                     rainy_days: int,
                                     current_season: str,
                                     lat: float,
                                     lon: float) -> Dict[str, Any]:
        """
        Calculate enhanced crop score with 10 factors (max 125 points).
        
        Args:
            crop_id: Crop identifier
            crop_data: Crop data from database
            seasonal_rainfall: Estimated seasonal rainfall
            current_temp: Current temperature
            humidity: Current humidity
            rainy_days: Number of rainy days in forecast
            current_season: Current season
            lat: Latitude
            lon: Longitude
            
        Returns:
            Enhanced crop score data with 10 factors
        """
        # Start with base scoring (original 6 factors)
        base_score = self._calculate_crop_score(
            crop_id, crop_data, seasonal_rainfall, current_temp, 
            humidity, rainy_days, current_season
        )
        
        # Add 4 new factors
        enhanced_components = base_score['score_components'].copy()
        
        # Factor 7: Soil suitability scoring (10 points)
        soil_score = self._calculate_soil_suitability_score(crop_data, lat, lon)
        enhanced_components['soil_suitability_score'] = soil_score
        
        # Factor 8: Market demand scoring (5 points)
        market_score = self._calculate_market_demand_score(crop_id)
        enhanced_components['market_demand_score'] = market_score
        
        # Factor 9: Input availability scoring (5 points)
        input_score = self._calculate_input_availability_score(crop_id)
        enhanced_components['input_availability_score'] = input_score
        
        # Factor 10: Climate trend scoring (5 points)
        climate_score = self._calculate_climate_trend_score(crop_id, seasonal_rainfall)
        enhanced_components['climate_trend_score'] = climate_score
        
        # Calculate new total score (max 125 points)
        total_score = sum(enhanced_components.values())
        
        # Generate enhanced reasons
        enhanced_reasons = self._generate_enhanced_score_reasons(
            enhanced_components, crop_data, seasonal_rainfall, current_temp
        )
        
        return {
            'crop_id': crop_id,
            'crop_data': crop_data,
            'total_score': total_score,
            'score_components': enhanced_components,
            'reasons': enhanced_reasons,
            'suitability_level': self._get_enhanced_suitability_level(total_score)
        }
    
    def _calculate_soil_suitability_score(self, crop_data: Dict[str, Any], lat: float, lon: float) -> float:
        """
        Calculate soil suitability score based on crop requirements.
        
        Args:
            crop_data: Crop data from database
            lat: Latitude
            lon: Longitude
            
        Returns:
            Soil suitability score (0-10)
        """
        # Get soil data (mock implementation for now)
        soil_data = self._get_soil_data(lat, lon)
        
        soil_requirements = crop_data.get('soil_requirements', {})
        
        score = 0
        
        # pH suitability (4 points)
        if soil_data and 'ph' in soil_data:
            soil_ph = soil_data['ph']
            ph_range = soil_requirements.get('ph_range', [6.0, 7.0])
            
            if ph_range[0] <= soil_ph <= ph_range[1]:
                score += 4
            elif abs(soil_ph - ph_range[0]) <= 0.5 or abs(soil_ph - ph_range[1]) <= 0.5:
                score += 2
            else:
                score += 1
        else:
            score += 2  # Default moderate score when no data
        
        # Fertility matching (3 points)
        if soil_data and 'fertility' in soil_data:
            soil_fertility = soil_data['fertility']
            required_fertility = soil_requirements.get('fertility', 'medium')
            
            if soil_fertility == required_fertility:
                score += 3
            elif (soil_fertility == 'high' and required_fertility == 'medium') or \
                 (soil_fertility == 'medium' and required_fertility == 'low'):
                score += 2
            else:
                score += 1
        else:
            score += 2
        
        # Drainage suitability (3 points)
        if soil_data and 'drainage' in soil_data:
            soil_drainage = soil_data['drainage']
            required_drainage = soil_requirements.get('drainage', 'well_drained')
            
            if soil_drainage == required_drainage:
                score += 3
            else:
                score += 1
        else:
            score += 2
        
        return min(score, 10)
    
    def _calculate_market_demand_score(self, crop_id: str) -> float:
        """
        Calculate market demand score for the crop.
        
        Args:
            crop_id: Crop identifier
            
        Returns:
            Market demand score (0-5)
        """
        return self.market_demand_scores.get(crop_id, 3)
    
    def _calculate_input_availability_score(self, crop_id: str) -> float:
        """
        Calculate input availability score for the crop.
        
        Args:
            crop_id: Crop identifier
            
        Returns:
            Input availability score (0-5)
        """
        return self.input_availability_scores.get(crop_id, 3)
    
    def _calculate_climate_trend_score(self, crop_id: str, seasonal_rainfall: float) -> float:
        """
        Calculate climate trend score based on long-term patterns.
        
        Args:
            crop_id: Crop identifier
            seasonal_rainfall: Estimated seasonal rainfall
            
        Returns:
            Climate trend score (0-5)
        """
        # Simple implementation based on rainfall trends
        if seasonal_rainfall < 300:
            # Low rainfall - favor drought-tolerant crops
            drought_tolerant_crops = ['sorghum', 'cassava', 'sweet_potato']
            return 5 if crop_id in drought_tolerant_crops else 2
        elif seasonal_rainfall > 800:
            # High rainfall - favor water-loving crops
            water_loving_crops = ['maize', 'beans']
            return 5 if crop_id in water_loving_crops else 3
        else:
            # Moderate rainfall - all crops suitable
            return 4
    
    def _get_soil_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get soil data for the location (mock implementation).
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Soil data dictionary
        """
        # Mock soil data for Lilongwe region
        # In production, this would call a soil API or database
        return {
            'ph': 6.2,
            'fertility': 'medium',
            'drainage': 'well_drained',
            'organic_matter': 'medium',
            'texture': 'clay_loam'
        }
    
    def _add_enhanced_variety_recommendations(self, 
                                           top_crops: List[Dict[str, Any]], 
                                           seasonal_rainfall: float,
                                           current_temp: float,
                                           lat: float,
                                           lon: float) -> List[Dict[str, Any]]:
        """
        Add enhanced variety recommendations with PDF integration.
        
        Args:
            top_crops: List of top-scoring crops
            seasonal_rainfall: Estimated seasonal rainfall
            current_temp: Current temperature
            lat: Latitude
            lon: Longitude
            
        Returns:
            Enhanced crops with variety recommendations
        """
        enhanced_crops = []
        
        for crop_score in top_crops:
            # Get basic variety recommendations
            basic_enhanced = self._add_variety_recommendations(
                [crop_score], seasonal_rainfall, current_temp
            )[0]
            
            # Add PDF-enhanced variety data
            pdf_enhanced_data = self.pdf_varieties.search_variety_information(
                crop=crop_score['crop_id'],
                location='Lilongwe',
                conditions={'rainfall': seasonal_rainfall, 'temperature': current_temp}
            )
            
            basic_enhanced['pdf_enhanced_varieties'] = pdf_enhanced_data
            enhanced_crops.append(basic_enhanced)
        
        return enhanced_crops
    
    def _generate_enhanced_planting_calendar(self, 
                                           top_crops: List[Dict[str, Any]], 
                                           current_month: str,
                                           lat: float,
                                           lon: float) -> List[Dict[str, Any]]:
        """
        Generate enhanced planting calendar with detailed timing.
        
        Args:
            top_crops: Top-scoring crops
            current_month: Current month
            lat: Latitude
            lon: Longitude
            
        Returns:
            Enhanced planting calendar recommendations
        """
        enhanced_calendar = []
        
        for crop_score in top_crops:
            crop_id = crop_score['crop_id']
            
            # Get basic planting recommendations
            basic_recommendations = self.crop_db.get_planting_recommendations(crop_id, current_month)
            
            # Add enhanced timing information
            enhanced_timing = self.planting_calendar.get_critical_timing_alerts(
                crops=[crop_id],
                current_month=current_month,
                location=(lat, lon)
            )
            
            if basic_recommendations:
                basic_recommendations['enhanced_timing'] = enhanced_timing
                enhanced_calendar.append(basic_recommendations)
        
        return enhanced_calendar
    
    def _generate_enhanced_score_reasons(self, 
                                       score_components: Dict[str, float], 
                                       crop_data: Dict[str, Any], 
                                       seasonal_rainfall: float, 
                                       current_temp: float) -> List[str]:
        """
        Generate enhanced human-readable reasons for crop scoring.
        
        Args:
            score_components: All 10 score components
            crop_data: Crop data
            seasonal_rainfall: Seasonal rainfall estimate
            current_temp: Current temperature
            
        Returns:
            List of enhanced reason strings
        """
        reasons = []
        
        # Original reasons
        base_reasons = self._generate_score_reasons(
            score_components, crop_data, seasonal_rainfall, current_temp
        )
        reasons.extend(base_reasons)
        
        # Enhanced reasons for new factors
        if score_components.get('soil_suitability_score', 0) >= 8:
            reasons.append("Excellent soil suitability match")
        elif score_components.get('soil_suitability_score', 0) >= 6:
            reasons.append("Good soil conditions")
        
        if score_components.get('market_demand_score', 0) >= 4:
            reasons.append("Strong market demand")
        elif score_components.get('market_demand_score', 0) >= 3:
            reasons.append("Moderate market demand")
        
        if score_components.get('input_availability_score', 0) >= 4:
            reasons.append("Good input availability")
        
        if score_components.get('climate_trend_score', 0) >= 4:
            reasons.append("Favorable climate trends")
        
        return reasons
    
    def _get_enhanced_suitability_level(self, total_score: float) -> str:
        """
        Convert enhanced numerical score to suitability level.
        
        Args:
            total_score: Total enhanced crop score (max 125)
            
        Returns:
            Enhanced suitability level string
        """
        if total_score >= 100:
            return 'excellent'
        elif total_score >= 80:
            return 'very_good'
        elif total_score >= 60:
            return 'good'
        elif total_score >= 40:
            return 'fair'
        else:
            return 'poor'
    
    def _validate_inputs(self, rainfall_data: Dict[str, Any], weather_data: Dict[str, Any], 
                        lat: float, lon: float) -> bool:
        """
        Validate input data for recommendations.
        
        Args:
            rainfall_data: Rainfall data
            weather_data: Weather data
            lat: Latitude
            lon: Longitude
            
        Returns:
            True if valid, False otherwise
        """
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            logger.warning(f"Invalid coordinates: lat={lat}, lon={lon}")
            return False
        
        # Validate data structures
        if not isinstance(rainfall_data, dict) or not isinstance(weather_data, dict):
            logger.warning("Invalid data structures provided")
            return False
        
        return True
    
    def assess_recommendation_reliability(self, recommendations_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess overall recommendation reliability.
        
        Args:
            recommendations_data: Data about the recommendations
            
        Returns:
            Reliability assessment
        """
        # Calculate component reliability scores
        component_scores = {}
        
        # Weather data reliability
        weather_age = recommendations_data.get('weather_data_age', 24)
        if weather_age <= 2:
            component_scores['weather_reliability'] = 1.0
        elif weather_age <= 6:
            component_scores['weather_reliability'] = 0.8
        elif weather_age <= 12:
            component_scores['weather_reliability'] = 0.6
        else:
            component_scores['weather_reliability'] = 0.4
        
        # PDF sources reliability
        pdf_count = recommendations_data.get('pdf_sources_count', 0)
        if pdf_count >= 3:
            component_scores['pdf_reliability'] = 1.0
        elif pdf_count >= 2:
            component_scores['pdf_reliability'] = 0.8
        elif pdf_count >= 1:
            component_scores['pdf_reliability'] = 0.6
        else:
            component_scores['pdf_reliability'] = 0.4
        
        # Scoring completeness
        scoring_completeness = recommendations_data.get('scoring_completeness', 0.8)
        component_scores['scoring_completeness'] = scoring_completeness
        
        # Overall reliability
        overall_reliability = sum(component_scores.values()) / len(component_scores)
        
        # Generate improvement suggestions
        suggestions = []
        if component_scores['weather_reliability'] < 0.8:
            suggestions.append("Update weather data for better accuracy")
        if component_scores['pdf_reliability'] < 0.8:
            suggestions.append("Add more PDF sources for comprehensive recommendations")
        if component_scores['scoring_completeness'] < 0.9:
            suggestions.append("Improve data completeness for better scoring")
        
        return {
            'overall_reliability': overall_reliability,
            'component_reliability': component_scores,
            'improvement_suggestions': suggestions
        }


# Global instance
enhanced_recommendation_engine = EnhancedRecommendationEngine() 