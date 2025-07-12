"""
Advanced Crop Recommendation Engine for the Agricultural Advisor Bot.
Provides intelligent crop recommendations based on multiple environmental factors.
"""
import datetime
from typing import Dict, List, Any, Optional, Tuple
from scripts.crop_advisor.crop_database import crop_database
from scripts.utils.logger import logger


class CropRecommendationEngine:
    """Advanced crop recommendation engine with multi-factor analysis."""
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self.crop_db = crop_database
        self.current_month = datetime.datetime.now().strftime('%B')
        
    def generate_recommendations(self, 
                               rainfall_data: Dict[str, Any], 
                               weather_data: Dict[str, Any],
                               lat: float, 
                               lon: float,
                               user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive crop recommendations based on multiple factors.
        
        Args:
            rainfall_data: Rainfall analysis data
            weather_data: Current weather data
            lat: Latitude
            lon: Longitude
            user_preferences: Optional user preferences
            
        Returns:
            Comprehensive recommendation results
        """
        logger.info(f"Generating crop recommendations for coordinates: {lat}, {lon}")
        
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
        
        # Generate recommendations for each crop
        crop_scores = []
        all_crops = self.crop_db.get_all_crops()
        
        for crop_id, crop_data in all_crops.items():
            score_data = self._calculate_crop_score(
                crop_id, crop_data, seasonal_rainfall, current_temp, 
                humidity, rainy_days, current_season
            )
            crop_scores.append(score_data)
        
        # Sort by total score
        crop_scores.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Generate variety recommendations for top crops
        top_crops_with_varieties = self._add_variety_recommendations(
            crop_scores[:5], seasonal_rainfall, current_temp
        )
        
        # Generate planting calendar recommendations
        planting_recommendations = self._generate_planting_calendar(
            crop_scores[:3], self.current_month
        )
        
        # Generate season-specific advice
        seasonal_advice = self._generate_seasonal_advice(
            current_season, seasonal_rainfall, current_temp
        )
        
        return {
            'recommendations': top_crops_with_varieties,
            'planting_calendar': planting_recommendations,
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
    
    def _calculate_crop_score(self, 
                            crop_id: str, 
                            crop_data: Dict[str, Any], 
                            seasonal_rainfall: float,
                            current_temp: float,
                            humidity: float,
                            rainy_days: int,
                            current_season: str) -> Dict[str, Any]:
        """
        Calculate comprehensive score for a crop based on multiple factors.
        
        Args:
            crop_id: Crop identifier
            crop_data: Crop data from database
            seasonal_rainfall: Estimated seasonal rainfall
            current_temp: Current temperature
            humidity: Current humidity
            rainy_days: Number of rainy days in forecast
            current_season: Current season
            
        Returns:
            Comprehensive crop score data
        """
        score_components = {
            'rainfall_score': 0,
            'temperature_score': 0,
            'seasonal_score': 0,
            'humidity_score': 0,
            'timing_score': 0,
            'drought_tolerance_score': 0
        }
        
        # Rainfall scoring (40% weight)
        water_req = crop_data.get('water_requirements', {})
        min_rainfall = water_req.get('minimum_rainfall', 0)
        optimal_rainfall = water_req.get('optimal_rainfall', 0)
        max_rainfall = water_req.get('maximum_rainfall', 2000)
        
        if seasonal_rainfall >= optimal_rainfall:
            score_components['rainfall_score'] = 40
        elif seasonal_rainfall >= min_rainfall:
            score_components['rainfall_score'] = 20 + (seasonal_rainfall - min_rainfall) / (optimal_rainfall - min_rainfall) * 20
        else:
            score_components['rainfall_score'] = (seasonal_rainfall / min_rainfall) * 20
        
        # Temperature scoring (25% weight)
        temp_req = crop_data.get('temperature_requirements', {})
        min_temp = temp_req.get('minimum_temp', 0)
        optimal_temp = temp_req.get('optimal_temp', 25)
        max_temp = temp_req.get('maximum_temp', 40)
        
        if min_temp <= current_temp <= max_temp:
            if abs(current_temp - optimal_temp) <= 3:
                score_components['temperature_score'] = 25
            else:
                score_components['temperature_score'] = 20
        else:
            score_components['temperature_score'] = 10
        
        # Seasonal timing scoring (20% weight)
        planting_calendar = crop_data.get('planting_calendar', {})
        timing_score = 0
        for window_name, window_data in planting_calendar.items():
            start_month = window_data.get('start')
            end_month = window_data.get('end')
            months_in_window = self.crop_db._get_month_range(start_month, end_month)
            
            if self.current_month in months_in_window:
                timing_score = 20
                break
            # Check if close to planting window
            elif self._is_month_close_to_window(self.current_month, months_in_window):
                timing_score = 10
        
        score_components['timing_score'] = timing_score
        
        # Humidity scoring (10% weight)
        if humidity >= 60:
            score_components['humidity_score'] = 10
        elif humidity >= 40:
            score_components['humidity_score'] = 7
        else:
            score_components['humidity_score'] = 3
        
        # Drought tolerance bonus (5% weight)
        varieties = crop_data.get('varieties', [])
        max_drought_tolerance = 0
        for variety in varieties:
            tolerance = variety.get('drought_tolerance', 'moderate')
            tolerance_values = {'excellent': 5, 'good': 4, 'moderate': 3, 'poor': 1}
            max_drought_tolerance = max(max_drought_tolerance, tolerance_values.get(tolerance, 3))
        
        score_components['drought_tolerance_score'] = max_drought_tolerance
        
        # Calculate total score
        total_score = sum(score_components.values())
        
        # Generate reasons for recommendation
        reasons = self._generate_score_reasons(score_components, crop_data, seasonal_rainfall, current_temp)
        
        return {
            'crop_id': crop_id,
            'crop_data': crop_data,
            'total_score': total_score,
            'score_components': score_components,
            'reasons': reasons,
            'suitability_level': self._get_suitability_level(total_score)
        }
    
    def _add_variety_recommendations(self, 
                                   top_crops: List[Dict[str, Any]], 
                                   seasonal_rainfall: float,
                                   current_temp: float) -> List[Dict[str, Any]]:
        """
        Add specific variety recommendations for top crops.
        
        Args:
            top_crops: List of top-scoring crops
            seasonal_rainfall: Estimated seasonal rainfall
            current_temp: Current temperature
            
        Returns:
            Top crops with variety recommendations
        """
        enhanced_crops = []
        
        for crop_score in top_crops:
            crop_data = crop_score['crop_data']
            varieties = crop_data.get('varieties', [])
            
            # Score varieties based on current conditions
            variety_scores = []
            for variety in varieties:
                variety_score = self._score_variety(variety, seasonal_rainfall, current_temp)
                variety_scores.append(variety_score)
            
            # Sort varieties by score
            variety_scores.sort(key=lambda x: x['score'], reverse=True)
            
            # Add variety recommendations to crop data
            enhanced_crop = crop_score.copy()
            enhanced_crop['recommended_varieties'] = variety_scores[:3]  # Top 3 varieties
            enhanced_crops.append(enhanced_crop)
        
        return enhanced_crops
    
    def _score_variety(self, variety: Dict[str, Any], seasonal_rainfall: float, current_temp: float) -> Dict[str, Any]:
        """
        Score a specific variety based on environmental conditions.
        
        Args:
            variety: Variety data
            seasonal_rainfall: Seasonal rainfall estimate
            current_temp: Current temperature
            
        Returns:
            Variety score data
        """
        score = 0
        reasons = []
        
        # Drought tolerance scoring
        tolerance = variety.get('drought_tolerance', 'moderate')
        tolerance_scores = {'excellent': 40, 'good': 30, 'moderate': 20, 'poor': 10}
        drought_score = tolerance_scores.get(tolerance, 20)
        
        # Adjust score based on rainfall
        if seasonal_rainfall < 400:  # Low rainfall conditions
            score += drought_score
            reasons.append(f"Drought tolerance: {tolerance}")
        else:
            score += drought_score * 0.7  # Less emphasis on drought tolerance
        
        # Yield potential scoring
        yield_potential = variety.get('yield_potential', 'moderate')
        yield_scores = {'high': 30, 'moderate': 20, 'low': 10}
        score += yield_scores.get(yield_potential, 20)
        reasons.append(f"Yield potential: {yield_potential}")
        
        # Maturity period scoring (shorter is better for uncertain conditions)
        maturity_days = variety.get('maturity_days', 120)
        if maturity_days <= 100:
            score += 20
            reasons.append("Early maturity")
        elif maturity_days <= 120:
            score += 15
            reasons.append("Medium maturity")
        else:
            score += 10
            reasons.append("Late maturity")
        
        # Disease resistance bonus
        disease_resistance = variety.get('disease_resistance', [])
        if len(disease_resistance) > 1:
            score += 10
            reasons.append("Multiple disease resistance")
        elif len(disease_resistance) == 1:
            score += 5
            reasons.append("Disease resistance")
        
        return {
            'variety_data': variety,
            'score': score,
            'reasons': reasons
        }
    
    def _generate_planting_calendar(self, top_crops: List[Dict[str, Any]], current_month: str) -> List[Dict[str, Any]]:
        """
        Generate planting calendar recommendations for top crops.
        
        Args:
            top_crops: Top-scoring crops
            current_month: Current month
            
        Returns:
            Planting calendar recommendations
        """
        calendar_recommendations = []
        
        for crop_score in top_crops:
            crop_id = crop_score['crop_id']
            recommendations = self.crop_db.get_planting_recommendations(crop_id, current_month)
            
            if recommendations:
                calendar_recommendations.append(recommendations)
        
        return calendar_recommendations
    
    def _generate_seasonal_advice(self, current_season: str, seasonal_rainfall: float, current_temp: float) -> Dict[str, Any]:
        """
        Generate season-specific agricultural advice.
        
        Args:
            current_season: Current season
            seasonal_rainfall: Seasonal rainfall estimate
            current_temp: Current temperature
            
        Returns:
            Seasonal advice dictionary
        """
        advice = {
            'season': current_season,
            'primary_activities': [],
            'crop_management': [],
            'risk_factors': [],
            'opportunities': []
        }
        
        if current_season == 'rainy_season':
            advice['primary_activities'] = [
                'Land preparation and planting',
                'Weed management',
                'Fertilizer application',
                'Pest and disease monitoring'
            ]
            
            if seasonal_rainfall < 400:
                advice['risk_factors'].append('Below-average rainfall expected')
                advice['crop_management'].append('Choose drought-tolerant varieties')
                advice['crop_management'].append('Implement water conservation practices')
            elif seasonal_rainfall > 800:
                advice['risk_factors'].append('Above-average rainfall - flood risk')
                advice['crop_management'].append('Ensure proper drainage')
                advice['crop_management'].append('Monitor for waterlogging')
            else:
                advice['opportunities'].append('Favorable rainfall conditions')
                advice['crop_management'].append('Optimal conditions for most crops')
        
        elif current_season == 'dry_season':
            advice['primary_activities'] = [
                'Harvesting and post-harvest handling',
                'Land preparation for next season',
                'Irrigation farming where possible',
                'Soil conservation activities'
            ]
            
            advice['opportunities'].append('Good time for land preparation')
            advice['crop_management'].append('Focus on storage and preservation')
            advice['crop_management'].append('Consider dry-season vegetables with irrigation')
        
        return advice
    
    def _estimate_seasonal_rainfall(self, recent_rainfall: float, forecast_rainfall: float) -> float:
        """
        Estimate seasonal rainfall based on recent and forecast data.
        
        Args:
            recent_rainfall: Recent 7-day rainfall
            forecast_rainfall: Forecast 7-day rainfall
            
        Returns:
            Estimated seasonal rainfall
        """
        # Simple estimation - can be improved with historical data
        weekly_average = (recent_rainfall + forecast_rainfall) / 2
        
        # Estimate based on current season
        if self.crop_db.get_current_season(self.current_month) == 'rainy_season':
            # Rainy season: 20-24 weeks, extrapolate from 2-week data
            seasonal_estimate = weekly_average * 22  # 22 weeks average
        else:
            # Dry season: lower extrapolation
            seasonal_estimate = weekly_average * 8  # 8 weeks average
        
        return min(seasonal_estimate, 1500)  # Cap at reasonable maximum
    
    def _get_suitability_level(self, total_score: float) -> str:
        """
        Convert numerical score to suitability level.
        
        Args:
            total_score: Total crop score
            
        Returns:
            Suitability level string
        """
        if total_score >= 80:
            return 'excellent'
        elif total_score >= 60:
            return 'good'
        elif total_score >= 40:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_score_reasons(self, score_components: Dict[str, float], 
                              crop_data: Dict[str, Any], 
                              seasonal_rainfall: float, 
                              current_temp: float) -> List[str]:
        """
        Generate human-readable reasons for crop scoring.
        
        Args:
            score_components: Individual score components
            crop_data: Crop data
            seasonal_rainfall: Seasonal rainfall estimate
            current_temp: Current temperature
            
        Returns:
            List of reason strings
        """
        reasons = []
        
        # Rainfall reasoning
        if score_components['rainfall_score'] >= 35:
            reasons.append(f"Excellent rainfall conditions ({seasonal_rainfall:.0f}mm estimated)")
        elif score_components['rainfall_score'] >= 25:
            reasons.append(f"Good rainfall conditions ({seasonal_rainfall:.0f}mm estimated)")
        elif score_components['rainfall_score'] >= 15:
            reasons.append(f"Adequate rainfall ({seasonal_rainfall:.0f}mm estimated)")
        else:
            reasons.append(f"Low rainfall conditions ({seasonal_rainfall:.0f}mm estimated)")
        
        # Temperature reasoning
        if score_components['temperature_score'] >= 20:
            reasons.append(f"Suitable temperature ({current_temp:.1f}°C)")
        else:
            reasons.append(f"Challenging temperature ({current_temp:.1f}°C)")
        
        # Timing reasoning
        if score_components['timing_score'] >= 15:
            reasons.append("Optimal planting time")
        elif score_components['timing_score'] >= 8:
            reasons.append("Near planting window")
        else:
            reasons.append("Outside typical planting window")
        
        return reasons
    
    def _is_month_close_to_window(self, current_month: str, window_months: List[str]) -> bool:
        """
        Check if current month is close to planting window.
        
        Args:
            current_month: Current month
            window_months: Months in planting window
            
        Returns:
            True if close to window
        """
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        try:
            current_idx = months.index(current_month)
            window_indices = [months.index(month) for month in window_months if month in months]
            
            # Check if within 1-2 months of window
            for window_idx in window_indices:
                if abs(current_idx - window_idx) <= 2:
                    return True
                # Handle year boundary
                if abs(current_idx - window_idx) >= 10:  # Across year boundary
                    return True
            
            return False
        except ValueError:
            return False


# Global instance
recommendation_engine = CropRecommendationEngine() 