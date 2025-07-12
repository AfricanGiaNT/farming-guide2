"""
Seasonal Advisor Module for the Agricultural Advisor Bot.
Provides season-specific recommendations and timing advice for Lilongwe region.
"""
import datetime
from typing import Dict, List, Any, Optional
from scripts.crop_advisor.crop_database import crop_database
from scripts.utils.logger import logger


class SeasonalAdvisor:
    """Provides seasonal agricultural advice and timing recommendations."""
    
    def __init__(self):
        """Initialize the seasonal advisor."""
        self.crop_db = crop_database
        self.current_month = datetime.datetime.now().strftime('%B')
        self.current_date = datetime.datetime.now()
        
    def get_seasonal_recommendations(self, rainfall_data: Dict[str, Any], weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive seasonal recommendations.
        
        Args:
            rainfall_data: Rainfall analysis data
            weather_data: Current weather data
            
        Returns:
            Seasonal recommendations dictionary
        """
        current_season = self.crop_db.get_current_season(self.current_month)
        seasonal_calendar = self.crop_db.get_seasonal_calendar()
        
        # Get seasonal context
        seasonal_context = self._get_seasonal_context(current_season, seasonal_calendar)
        
        # Generate month-specific advice
        monthly_advice = self._get_monthly_advice(self.current_month, rainfall_data, weather_data)
        
        # Get planting calendar for current period
        planting_calendar = self._get_current_planting_calendar(self.current_month)
        
        # Generate agricultural calendar
        agricultural_calendar = self._generate_agricultural_calendar(self.current_month)
        
        # Get weather-based recommendations
        weather_recommendations = self._get_weather_based_recommendations(rainfall_data, weather_data)
        
        return {
            'current_season': current_season,
            'current_month': self.current_month,
            'seasonal_context': seasonal_context,
            'monthly_advice': monthly_advice,
            'planting_calendar': planting_calendar,
            'agricultural_calendar': agricultural_calendar,
            'weather_recommendations': weather_recommendations,
            'timestamp': self.current_date.isoformat()
        }
    
    def _get_seasonal_context(self, current_season: str, seasonal_calendar: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get contextual information about the current season.
        
        Args:
            current_season: Current season identifier
            seasonal_calendar: Seasonal calendar data
            
        Returns:
            Seasonal context dictionary
        """
        context = {
            'season': current_season,
            'description': '',
            'typical_activities': [],
            'key_challenges': [],
            'opportunities': []
        }
        
        if current_season == 'rainy_season':
            season_data = seasonal_calendar.get('rainy_season', {})
            context.update({
                'description': 'Main agricultural season in Lilongwe with regular rainfall',
                'start_month': season_data.get('start_month', 'November'),
                'end_month': season_data.get('end_month', 'April'),
                'peak_months': season_data.get('peak_months', []),
                'typical_rainfall': season_data.get('typical_rainfall', 800),
                'typical_activities': [
                    'Land preparation',
                    'Planting major crops',
                    'Weeding and fertilization',
                    'Pest and disease management',
                    'Harvesting early crops'
                ],
                'key_challenges': [
                    'Timing of planting with rainfall',
                    'Weed management',
                    'Pest and disease pressure',
                    'Potential flooding in low areas'
                ],
                'opportunities': [
                    'Optimal growing conditions',
                    'Multiple cropping opportunities',
                    'Natural soil moisture replenishment',
                    'Good pasture growth'
                ]
            })
        
        elif current_season == 'dry_season':
            season_data = seasonal_calendar.get('dry_season', {})
            context.update({
                'description': 'Dry season with minimal rainfall, focus on harvesting and land preparation',
                'start_month': season_data.get('start_month', 'May'),
                'end_month': season_data.get('end_month', 'October'),
                'peak_months': season_data.get('peak_months', []),
                'typical_rainfall': season_data.get('typical_rainfall', 50),
                'typical_activities': [
                    'Harvesting main crops',
                    'Post-harvest processing',
                    'Land preparation for next season',
                    'Irrigation farming',
                    'Soil conservation activities'
                ],
                'key_challenges': [
                    'Water scarcity',
                    'Crop drying and storage',
                    'Soil moisture conservation',
                    'Fire management'
                ],
                'opportunities': [
                    'Good weather for harvesting',
                    'Ideal for land preparation',
                    'Dry-season vegetable production',
                    'Equipment maintenance'
                ]
            })
        
        return context
    
    def _get_monthly_advice(self, month: str, rainfall_data: Dict[str, Any], weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get specific advice for the current month.
        
        Args:
            month: Current month
            rainfall_data: Rainfall analysis data
            weather_data: Current weather data
            
        Returns:
            Monthly advice dictionary
        """
        advice = {
            'month': month,
            'priority_activities': [],
            'crop_activities': [],
            'management_focus': [],
            'weather_considerations': []
        }
        
        # Month-specific agricultural activities
        monthly_activities = {
            'January': {
                'priority_activities': ['Weeding', 'Top-dressing fertilizer', 'Pest monitoring'],
                'crop_activities': ['Maize tasseling care', 'Bean flowering management'],
                'management_focus': ['Water management', 'Disease prevention']
            },
            'February': {
                'priority_activities': ['Continued weeding', 'Harvest preparation', 'Storage preparation'],
                'crop_activities': ['Early maize harvesting', 'Bean pod monitoring'],
                'management_focus': ['Harvest timing', 'Post-harvest planning']
            },
            'March': {
                'priority_activities': ['Main harvest season', 'Drying and storage', 'Field cleaning'],
                'crop_activities': ['Maize harvesting', 'Bean harvesting', 'Root crop harvesting'],
                'management_focus': ['Proper drying', 'Storage pest prevention']
            },
            'April': {
                'priority_activities': ['Complete harvesting', 'Post-harvest processing', 'Field preparation'],
                'crop_activities': ['Late crop harvesting', 'Cassava harvesting'],
                'management_focus': ['Quality control', 'Market preparation']
            },
            'May': {
                'priority_activities': ['Storage management', 'Land preparation', 'Soil conservation'],
                'crop_activities': ['Dry-season vegetable planting', 'Sweet potato planting'],
                'management_focus': ['Irrigation setup', 'Soil improvement']
            },
            'June': {
                'priority_activities': ['Continued land preparation', 'Equipment maintenance', 'Training'],
                'crop_activities': ['Vegetable management', 'Tree planting'],
                'management_focus': ['Skill development', 'Planning for next season']
            },
            'July': {
                'priority_activities': ['Ridging and land preparation', 'Seed procurement', 'Planning'],
                'crop_activities': ['Dry-season crop management', 'Nursery preparation'],
                'management_focus': ['Input procurement', 'Financial planning']
            },
            'August': {
                'priority_activities': ['Final land preparation', 'Seed testing', 'Tool preparation'],
                'crop_activities': ['Continued dry-season farming', 'Seedbed preparation'],
                'management_focus': ['Readiness assessment', 'Resource allocation']
            },
            'September': {
                'priority_activities': ['Land preparation completion', 'Early planting prep', 'Water source prep'],
                'crop_activities': ['Dry-season harvest', 'Nursery management'],
                'management_focus': ['Timing optimization', 'Resource mobilization']
            },
            'October': {
                'priority_activities': ['Early season planting', 'Fertilizer application', 'Planting material prep'],
                'crop_activities': ['Early maize planting', 'Vegetable transplanting'],
                'management_focus': ['Timing with rainfall', 'Soil moisture management']
            },
            'November': {
                'priority_activities': ['Main season planting', 'Weed control', 'Fertilizer application'],
                'crop_activities': ['Maize planting', 'Bean planting', 'Groundnut planting'],
                'management_focus': ['Planting density', 'Spacing optimization']
            },
            'December': {
                'priority_activities': ['Planting completion', 'First weeding', 'Pest monitoring'],
                'crop_activities': ['Late planting', 'Crop establishment monitoring'],
                'management_focus': ['Stand establishment', 'Early pest management']
            }
        }
        
        # Get activities for current month
        current_activities = monthly_activities.get(month, {})
        advice.update(current_activities)
        
        # Add weather-based considerations
        total_rainfall = rainfall_data.get('total_7day_rainfall', 0)
        current_temp = weather_data.get('temperature', 25)
        
        if total_rainfall > 20:
            advice['weather_considerations'].append('Good rainfall - optimal for planting activities')
        elif total_rainfall > 10:
            advice['weather_considerations'].append('Moderate rainfall - monitor soil moisture')
        else:
            advice['weather_considerations'].append('Low rainfall - consider supplemental irrigation')
        
        if current_temp > 30:
            advice['weather_considerations'].append('High temperatures - ensure adequate water supply')
        elif current_temp < 20:
            advice['weather_considerations'].append('Cool temperatures - may slow crop growth')
        
        return advice
    
    def _get_current_planting_calendar(self, month: str) -> List[Dict[str, Any]]:
        """
        Get crops suitable for planting in the current month.
        
        Args:
            month: Current month
            
        Returns:
            List of crops suitable for planting
        """
        planting_calendar = []
        all_crops = self.crop_db.get_all_crops()
        
        for crop_id, crop_data in all_crops.items():
            planting_windows = crop_data.get('planting_calendar', {})
            
            for window_name, window_data in planting_windows.items():
                start_month = window_data.get('start')
                end_month = window_data.get('end')
                months_in_window = self.crop_db._get_month_range(start_month, end_month)
                
                if month in months_in_window:
                    planting_calendar.append({
                        'crop_id': crop_id,
                        'crop_name': crop_data.get('name', crop_id),
                        'window_name': window_name,
                        'start_month': start_month,
                        'end_month': end_month,
                        'rainfall_needed': window_data.get('rainfall_needed', 0),
                        'irrigation_required': window_data.get('irrigation_required', False),
                        'recommended_varieties': [v.get('name', 'Unknown') for v in crop_data.get('varieties', [])[:2]]
                    })
        
        return planting_calendar
    
    def _generate_agricultural_calendar(self, month: str) -> Dict[str, Any]:
        """
        Generate agricultural calendar for the next 3 months.
        
        Args:
            month: Current month
            
        Returns:
            Agricultural calendar dictionary
        """
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        try:
            current_idx = months.index(month)
            next_months = []
            
            for i in range(3):
                next_idx = (current_idx + i) % 12
                next_months.append(months[next_idx])
            
            calendar = {
                'forecast_period': f"{next_months[0]} - {next_months[-1]}",
                'months': []
            }
            
            for next_month in next_months:
                month_data = {
                    'month': next_month,
                    'season': self.crop_db.get_current_season(next_month),
                    'planting_opportunities': self._get_current_planting_calendar(next_month),
                    'key_activities': self._get_monthly_advice(next_month, {}, {})['priority_activities']
                }
                calendar['months'].append(month_data)
            
            return calendar
            
        except ValueError:
            return {'forecast_period': 'Unknown', 'months': []}
    
    def _get_weather_based_recommendations(self, rainfall_data: Dict[str, Any], weather_data: Dict[str, Any]) -> List[str]:
        """
        Get recommendations based on current weather conditions.
        
        Args:
            rainfall_data: Rainfall analysis data
            weather_data: Current weather data
            
        Returns:
            List of weather-based recommendations
        """
        recommendations = []
        
        total_rainfall = rainfall_data.get('total_7day_rainfall', 0)
        forecast_rainfall = rainfall_data.get('forecast_7day_rainfall', 0)
        current_temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 50)
        
        # Rainfall-based recommendations
        if total_rainfall > 30:
            recommendations.append("Excellent rainfall conditions - ideal for planting and crop establishment")
            if forecast_rainfall > 20:
                recommendations.append("Continued rainfall expected - ensure proper drainage in low-lying areas")
        elif total_rainfall > 15:
            recommendations.append("Good rainfall conditions - suitable for most agricultural activities")
        elif total_rainfall > 5:
            recommendations.append("Moderate rainfall - monitor soil moisture levels closely")
        else:
            recommendations.append("Low rainfall - consider drought-tolerant crops and water conservation")
        
        # Temperature-based recommendations
        if current_temp > 35:
            recommendations.append("High temperatures - ensure adequate water supply and consider shade for sensitive crops")
        elif current_temp < 18:
            recommendations.append("Cool temperatures - crop growth may be slower, consider cold-tolerant varieties")
        
        # Humidity-based recommendations
        if humidity > 80:
            recommendations.append("High humidity - monitor for fungal diseases and ensure good air circulation")
        elif humidity < 40:
            recommendations.append("Low humidity - plants may need additional watering")
        
        # Seasonal recommendations
        current_season = self.crop_db.get_current_season(self.current_month)
        if current_season == 'rainy_season':
            recommendations.append("Rainy season - focus on planting, weeding, and pest management")
        elif current_season == 'dry_season':
            recommendations.append("Dry season - focus on harvesting, storage, and land preparation")
        
        return recommendations
    
    def get_crop_timing_advice(self, crop_id: str) -> Dict[str, Any]:
        """
        Get specific timing advice for a particular crop.
        
        Args:
            crop_id: Crop identifier
            
        Returns:
            Crop timing advice dictionary
        """
        crop_data = self.crop_db.get_crop(crop_id)
        if not crop_data:
            return {'error': f'Crop {crop_id} not found'}
        
        planting_recommendations = self.crop_db.get_planting_recommendations(crop_id, self.current_month)
        
        # Generate timing advice
        timing_advice = {
            'crop_id': crop_id,
            'crop_name': crop_data.get('name', crop_id),
            'current_month': self.current_month,
            'planting_recommendations': planting_recommendations,
            'optimal_timing': None,
            'alternative_timings': [],
            'season_advice': ''
        }
        
        # Determine optimal timing
        if planting_recommendations.get('season_match'):
            timing_advice['optimal_timing'] = planting_recommendations.get('optimal_timing')
            timing_advice['season_advice'] = 'Current month is optimal for planting this crop'
        else:
            timing_advice['season_advice'] = 'Current month is not optimal for planting this crop'
            
            # Find alternative timings
            all_windows = planting_recommendations.get('planting_windows', [])
            for window in all_windows:
                if not window.get('is_current_window'):
                    timing_advice['alternative_timings'].append(window)
        
        return timing_advice


# Global instance
seasonal_advisor = SeasonalAdvisor() 