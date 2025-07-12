"""
Confidence Scoring System for Agricultural Advisor Bot.
Week 5 implementation - Provides confidence metrics for crop recommendations.
"""

import datetime
from typing import Dict, List, Any, Optional
from scripts.utils.logger import logger


class ConfidenceScorer:
    """
    Confidence scoring system for crop recommendations.
    Assesses data quality and recommendation reliability.
    """
    
    def __init__(self):
        """Initialize the confidence scorer."""
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
        # Data quality weights
        self.quality_weights = {
            'weather_data_freshness': 0.3,
            'rainfall_data_completeness': 0.25,
            'scoring_completeness': 0.2,
            'pdf_sources_available': 0.15,
            'coordinate_accuracy': 0.1
        }
        
        logger.info("Confidence scorer initialized")
    
    def calculate_confidence(self, recommendation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate confidence score for a recommendation.
        
        Args:
            recommendation_data: Dictionary containing recommendation and data quality info
            
        Returns:
            Confidence analysis with score and level
        """
        try:
            # Extract components
            crop_data = recommendation_data.get('crop_data', {})
            weather_data = recommendation_data.get('weather_data', {})
            rainfall_data = recommendation_data.get('rainfall_data', {})
            data_age = recommendation_data.get('data_age', 24)  # hours
            
            # Calculate individual confidence components
            confidence_components = {}
            
            # 1. Score completeness confidence (0-1)
            confidence_components['score_completeness'] = self._calculate_score_completeness_confidence(crop_data)
            
            # 2. Data freshness confidence (0-1)
            confidence_components['data_freshness'] = self._calculate_data_freshness_confidence(data_age)
            
            # 3. Weather data confidence (0-1)
            confidence_components['weather_data'] = self._calculate_weather_data_confidence(weather_data)
            
            # 4. Rainfall data confidence (0-1)
            confidence_components['rainfall_data'] = self._calculate_rainfall_data_confidence(rainfall_data)
            
            # 5. Recommendation strength confidence (0-1)
            confidence_components['recommendation_strength'] = self._calculate_recommendation_strength_confidence(crop_data)
            
            # Calculate overall confidence score
            overall_confidence = self._calculate_overall_confidence(confidence_components)
            
            # Determine confidence level
            confidence_level = self.get_confidence_level(overall_confidence)
            
            # Calculate data quality score
            data_quality = self.get_data_quality_score({
                'weather_data_age': data_age,
                'rainfall_data_completeness': confidence_components['rainfall_data'],
                'temperature_accuracy': confidence_components['weather_data'],
                'forecast_reliability': confidence_components['weather_data'] * 0.9
            })
            
            return {
                'confidence_score': overall_confidence,
                'confidence_level': confidence_level,
                'confidence_components': confidence_components,
                'data_quality': data_quality,
                'recommendations': self._generate_confidence_recommendations(
                    overall_confidence, confidence_components
                )
            }
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return {
                'confidence_score': 0.5,
                'confidence_level': 'medium',
                'confidence_components': {},
                'data_quality': 0.5,
                'recommendations': ['Unable to calculate confidence accurately']
            }
    
    def get_data_quality_score(self, data_quality_info: Dict[str, Any]) -> float:
        """
        Calculate data quality score based on various factors.
        
        Args:
            data_quality_info: Dictionary with data quality metrics
            
        Returns:
            Data quality score (0-1)
        """
        try:
            quality_score = 0.0
            
            # Weather data age scoring
            weather_age = data_quality_info.get('weather_data_age', 24)
            if weather_age <= 2:
                age_score = 1.0
            elif weather_age <= 6:
                age_score = 0.8
            elif weather_age <= 12:
                age_score = 0.6
            elif weather_age <= 24:
                age_score = 0.4
            else:
                age_score = 0.2
            
            quality_score += age_score * self.quality_weights['weather_data_freshness']
            
            # Rainfall data completeness
            rainfall_completeness = data_quality_info.get('rainfall_data_completeness', 0.8)
            quality_score += rainfall_completeness * self.quality_weights['rainfall_data_completeness']
            
            # Temperature accuracy
            temp_accuracy = data_quality_info.get('temperature_accuracy', 0.9)
            quality_score += temp_accuracy * self.quality_weights['scoring_completeness']
            
            # Forecast reliability
            forecast_reliability = data_quality_info.get('forecast_reliability', 0.8)
            quality_score += forecast_reliability * self.quality_weights['pdf_sources_available']
            
            # Coordinate accuracy (default good)
            coordinate_accuracy = data_quality_info.get('coordinate_accuracy', 0.95)
            quality_score += coordinate_accuracy * self.quality_weights['coordinate_accuracy']
            
            return min(max(quality_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating data quality score: {str(e)}")
            return 0.5
    
    def get_confidence_level(self, confidence_score: float) -> str:
        """
        Convert confidence score to categorical level.
        
        Args:
            confidence_score: Numerical confidence score (0-1)
            
        Returns:
            Confidence level string
        """
        if confidence_score >= self.confidence_thresholds['high']:
            return 'high'
        elif confidence_score >= self.confidence_thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_score_completeness_confidence(self, crop_data: Dict[str, Any]) -> float:
        """
        Calculate confidence based on completeness of scoring data.
        
        Args:
            crop_data: Crop scoring data
            
        Returns:
            Score completeness confidence (0-1)
        """
        try:
            score_components = crop_data.get('score_components', {})
            
            # Expected score components for enhanced scoring
            expected_components = [
                'rainfall_score', 'temperature_score', 'seasonal_score',
                'humidity_score', 'timing_score', 'drought_tolerance_score',
                'soil_suitability_score', 'market_demand_score',
                'input_availability_score', 'climate_trend_score'
            ]
            
            # Calculate completeness
            present_components = sum(1 for comp in expected_components if comp in score_components)
            completeness_ratio = present_components / len(expected_components)
            
            # Check if scores are meaningful (not just defaults)
            meaningful_scores = 0
            for comp in expected_components:
                if comp in score_components and score_components[comp] > 0:
                    meaningful_scores += 1
            
            meaningful_ratio = meaningful_scores / len(expected_components)
            
            # Combine completeness and meaningfulness
            return (completeness_ratio * 0.6) + (meaningful_ratio * 0.4)
            
        except Exception as e:
            logger.error(f"Error calculating score completeness confidence: {str(e)}")
            return 0.5
    
    def _calculate_data_freshness_confidence(self, data_age_hours: float) -> float:
        """
        Calculate confidence based on data freshness.
        
        Args:
            data_age_hours: Age of data in hours
            
        Returns:
            Data freshness confidence (0-1)
        """
        if data_age_hours <= 1:
            return 1.0
        elif data_age_hours <= 3:
            return 0.9
        elif data_age_hours <= 6:
            return 0.8
        elif data_age_hours <= 12:
            return 0.6
        elif data_age_hours <= 24:
            return 0.4
        else:
            return 0.2
    
    def _calculate_weather_data_confidence(self, weather_data: Dict[str, Any]) -> float:
        """
        Calculate confidence based on weather data quality.
        
        Args:
            weather_data: Weather data dictionary
            
        Returns:
            Weather data confidence (0-1)
        """
        try:
            confidence = 0.0
            
            # Required weather parameters
            required_params = ['temperature', 'humidity', 'pressure']
            optional_params = ['wind_speed', 'visibility', 'cloud_cover']
            
            # Check required parameters
            required_present = sum(1 for param in required_params if param in weather_data)
            required_ratio = required_present / len(required_params)
            
            # Check optional parameters
            optional_present = sum(1 for param in optional_params if param in weather_data)
            optional_ratio = optional_present / len(optional_params)
            
            # Check data reasonableness
            reasonable_data = 0
            total_checks = 0
            
            if 'temperature' in weather_data:
                temp = weather_data['temperature']
                if 0 <= temp <= 50:  # Reasonable temperature range
                    reasonable_data += 1
                total_checks += 1
            
            if 'humidity' in weather_data:
                humidity = weather_data['humidity']
                if 0 <= humidity <= 100:  # Valid humidity range
                    reasonable_data += 1
                total_checks += 1
            
            reasonableness_ratio = reasonable_data / total_checks if total_checks > 0 else 0.5
            
            # Combine factors
            confidence = (required_ratio * 0.6) + (optional_ratio * 0.2) + (reasonableness_ratio * 0.2)
            
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating weather data confidence: {str(e)}")
            return 0.5
    
    def _calculate_rainfall_data_confidence(self, rainfall_data: Dict[str, Any]) -> float:
        """
        Calculate confidence based on rainfall data quality.
        
        Args:
            rainfall_data: Rainfall data dictionary
            
        Returns:
            Rainfall data confidence (0-1)
        """
        try:
            confidence = 0.0
            
            # Required rainfall parameters
            required_params = ['total_7day_rainfall', 'forecast_7day_rainfall']
            optional_params = ['rainy_days_forecast', 'rainfall_intensity']
            
            # Check required parameters
            required_present = sum(1 for param in required_params if param in rainfall_data)
            required_ratio = required_present / len(required_params)
            
            # Check optional parameters
            optional_present = sum(1 for param in optional_params if param in rainfall_data)
            optional_ratio = optional_present / len(optional_params)
            
            # Check data consistency
            consistency_score = 0.8  # Default good consistency
            
            if 'total_7day_rainfall' in rainfall_data and 'forecast_7day_rainfall' in rainfall_data:
                historical = rainfall_data['total_7day_rainfall']
                forecast = rainfall_data['forecast_7day_rainfall']
                
                # Check if forecast is reasonable compared to historical
                if historical > 0:
                    ratio = forecast / historical
                    if 0.1 <= ratio <= 10:  # Reasonable range
                        consistency_score = 1.0
                    else:
                        consistency_score = 0.6
            
            # Combine factors
            confidence = (required_ratio * 0.6) + (optional_ratio * 0.2) + (consistency_score * 0.2)
            
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating rainfall data confidence: {str(e)}")
            return 0.5
    
    def _calculate_recommendation_strength_confidence(self, crop_data: Dict[str, Any]) -> float:
        """
        Calculate confidence based on recommendation strength.
        
        Args:
            crop_data: Crop recommendation data
            
        Returns:
            Recommendation strength confidence (0-1)
        """
        try:
            total_score = crop_data.get('total_score', 0)
            suitability_level = crop_data.get('suitability_level', 'poor')
            
            # Score-based confidence
            max_possible_score = 125  # Enhanced scoring max
            score_ratio = total_score / max_possible_score
            
            # Suitability level confidence mapping
            suitability_confidence = {
                'excellent': 1.0,
                'very_good': 0.9,
                'good': 0.8,
                'fair': 0.6,
                'poor': 0.3
            }
            
            level_confidence = suitability_confidence.get(suitability_level, 0.5)
            
            # Combine score and level confidence
            return (score_ratio * 0.6) + (level_confidence * 0.4)
            
        except Exception as e:
            logger.error(f"Error calculating recommendation strength confidence: {str(e)}")
            return 0.5
    
    def _calculate_overall_confidence(self, confidence_components: Dict[str, float]) -> float:
        """
        Calculate overall confidence from individual components.
        
        Args:
            confidence_components: Individual confidence component scores
            
        Returns:
            Overall confidence score (0-1)
        """
        try:
            # Component weights
            weights = {
                'score_completeness': 0.25,
                'data_freshness': 0.20,
                'weather_data': 0.20,
                'rainfall_data': 0.20,
                'recommendation_strength': 0.15
            }
            
            overall_confidence = 0.0
            
            for component, weight in weights.items():
                component_score = confidence_components.get(component, 0.5)
                overall_confidence += component_score * weight
            
            return min(max(overall_confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating overall confidence: {str(e)}")
            return 0.5
    
    def _generate_confidence_recommendations(self, 
                                           overall_confidence: float,
                                           confidence_components: Dict[str, float]) -> List[str]:
        """
        Generate recommendations to improve confidence.
        
        Args:
            overall_confidence: Overall confidence score
            confidence_components: Individual component scores
            
        Returns:
            List of improvement recommendations
        """
        recommendations = []
        
        # Overall confidence recommendations
        if overall_confidence < 0.6:
            recommendations.append("Consider multiple data sources for better accuracy")
        
        # Component-specific recommendations
        if confidence_components.get('data_freshness', 0.5) < 0.6:
            recommendations.append("Update weather data more frequently")
        
        if confidence_components.get('weather_data', 0.5) < 0.6:
            recommendations.append("Improve weather data completeness")
        
        if confidence_components.get('rainfall_data', 0.5) < 0.6:
            recommendations.append("Verify rainfall data accuracy")
        
        if confidence_components.get('score_completeness', 0.5) < 0.6:
            recommendations.append("Collect more environmental data for comprehensive scoring")
        
        if confidence_components.get('recommendation_strength', 0.5) < 0.6:
            recommendations.append("Consider additional crop options or timing")
        
        # If no specific issues, provide general advice
        if not recommendations:
            if overall_confidence >= 0.8:
                recommendations.append("High confidence - recommendations are reliable")
            else:
                recommendations.append("Moderate confidence - consider local expertise")
        
        return recommendations


# Global instance
confidence_scorer = ConfidenceScorer() 