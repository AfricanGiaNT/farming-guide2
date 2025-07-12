"""
Enhanced Planting Calendar System for Agricultural Advisor Bot.
Week 5 implementation - Comprehensive planting calendar with timing alerts and weather integration.
"""

import datetime
from typing import Dict, List, Any, Optional, Tuple
from scripts.crop_advisor.crop_database import crop_database
from scripts.utils.logger import logger


class PlantingCalendar:
    """
    Enhanced planting calendar system with comprehensive timing recommendations.
    Provides month-by-month guidance, critical alerts, and weather-based adjustments.
    """
    
    def __init__(self):
        """Initialize the planting calendar."""
        self.crop_db = crop_database
        self.current_month = datetime.datetime.now().strftime('%B')
        self.current_date = datetime.datetime.now()
        
        # Activity timing mappings (days after planting)
        self.activity_schedules = {
            'maize': {
                'planting': 0,
                'first_weeding': 14,
                'fertilizer_application': 21,
                'second_weeding': 35,
                'top_dressing': 42,
                'tasseling_care': 70,
                'harvest': 120
            },
            'beans': {
                'planting': 0,
                'first_weeding': 10,
                'fertilizer_application': 14,
                'second_weeding': 28,
                'flowering_care': 45,
                'harvest': 90
            },
            'groundnuts': {
                'planting': 0,
                'first_weeding': 14,
                'fertilizer_application': 21,
                'second_weeding': 35,
                'earthing_up': 42,
                'harvest': 105
            },
            'sorghum': {
                'planting': 0,
                'first_weeding': 14,
                'fertilizer_application': 21,
                'second_weeding': 35,
                'head_emergence': 80,
                'harvest': 120
            }
        }
        
        # Critical timing windows
        self.critical_windows = {
            'planting_delay_risk': 7,  # days
            'weeding_delay_risk': 5,   # days
            'fertilizer_delay_risk': 3, # days
            'harvest_delay_risk': 10   # days
        }
        
        logger.info("Enhanced planting calendar initialized")
    
    def get_monthly_recommendations(self, 
                                  month: str,
                                  location: Tuple[float, float],
                                  weather_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive monthly planting recommendations.
        
        Args:
            month: Month name (e.g., 'January')
            location: Latitude, longitude tuple
            weather_forecast: Weather forecast data
            
        Returns:
            Monthly recommendations dictionary
        """
        logger.info(f"Getting monthly recommendations for {month}")
        
        try:
            # Get basic seasonal information
            current_season = self.crop_db.get_current_season(month)
            
            # Get crops suitable for planting this month
            plantable_crops = self._get_plantable_crops_for_month(month, weather_forecast)
            
            # Get critical activities for this month
            critical_activities = self._get_critical_activities_for_month(month, location)
            
            # Get timing alerts
            timing_alerts = self._get_monthly_timing_alerts(month, weather_forecast)
            
            # Get weather-based adjustments
            weather_adjustments = self._get_weather_based_monthly_adjustments(
                month, weather_forecast
            )
            
            # Generate month-specific advice
            monthly_advice = self._generate_monthly_advice(month, current_season, weather_forecast)
            
            return {
                'month': month,
                'season': current_season,
                'plantable_crops': plantable_crops,
                'critical_activities': critical_activities,
                'timing_alerts': timing_alerts,
                'weather_adjustments': weather_adjustments,
                'monthly_advice': monthly_advice,
                'location': location,
                'generated_at': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly recommendations: {str(e)}")
            return {
                'month': month,
                'error': 'Unable to generate monthly recommendations',
                'plantable_crops': [],
                'critical_activities': [],
                'timing_alerts': []
            }
    
    def get_critical_timing_alerts(self, 
                                 crops: List[str],
                                 current_month: str,
                                 location: Tuple[float, float]) -> List[Dict[str, Any]]:
        """
        Get critical timing alerts for specific crops.
        
        Args:
            crops: List of crop identifiers
            current_month: Current month name
            location: Latitude, longitude tuple
            
        Returns:
            List of critical timing alerts
        """
        alerts = []
        
        try:
            for crop in crops:
                crop_data = self.crop_db.get_crop(crop)
                if not crop_data:
                    continue
                
                # Get planting windows for this crop
                planting_calendar = crop_data.get('planting_calendar', {})
                
                for window_name, window_data in planting_calendar.items():
                    alert = self._check_timing_window_alert(
                        crop, window_name, window_data, current_month, location
                    )
                    if alert:
                        alerts.append(alert)
                
                # Check for activity-based alerts
                activity_alerts = self._check_activity_timing_alerts(crop, current_month)
                alerts.extend(activity_alerts)
            
            # Sort by urgency
            alerts.sort(key=lambda x: self._get_urgency_score(x['urgency']), reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating timing alerts: {str(e)}")
            return []
    
    def get_activity_schedule(self, 
                            crops: List[str],
                            planting_date: str,
                            location: Tuple[float, float]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get comprehensive activity schedule for crops.
        
        Args:
            crops: List of crop identifiers
            planting_date: Planting date in YYYY-MM-DD format
            location: Latitude, longitude tuple
            
        Returns:
            Activity schedule dictionary
        """
        try:
            planting_datetime = datetime.datetime.strptime(planting_date, '%Y-%m-%d')
            
            schedule = {
                'planting_activities': [],
                'maintenance_activities': [],
                'harvest_activities': []
            }
            
            for crop in crops:
                if crop not in self.activity_schedules:
                    continue
                
                crop_schedule = self.activity_schedules[crop]
                
                for activity, days_offset in crop_schedule.items():
                    activity_date = planting_datetime + datetime.timedelta(days=days_offset)
                    
                    activity_info = {
                        'crop': crop,
                        'activity': activity,
                        'date': activity_date.strftime('%Y-%m-%d'),
                        'days_after_planting': days_offset,
                        'month': activity_date.strftime('%B'),
                        'description': self._get_activity_description(crop, activity)
                    }
                    
                    # Categorize activities
                    if activity == 'planting':
                        schedule['planting_activities'].append(activity_info)
                    elif activity == 'harvest':
                        schedule['harvest_activities'].append(activity_info)
                    else:
                        schedule['maintenance_activities'].append(activity_info)
            
            # Sort each category by date
            for category in schedule.values():
                category.sort(key=lambda x: x['date'])
            
            return schedule
            
        except Exception as e:
            logger.error(f"Error generating activity schedule: {str(e)}")
            return {
                'planting_activities': [],
                'maintenance_activities': [],
                'harvest_activities': []
            }
    
    def get_weather_adjustments(self, 
                               planned_activities: List[Dict[str, Any]],
                               weather_forecast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get weather-based timing adjustments for planned activities.
        
        Args:
            planned_activities: List of planned activities
            weather_forecast: Weather forecast data
            
        Returns:
            List of adjustment recommendations
        """
        adjustments = []
        
        try:
            # Extract weather conditions
            rainfall_forecast = weather_forecast.get('rainfall_forecast', 0)
            temperature_forecast = weather_forecast.get('temperature_forecast', 25)
            wind_forecast = weather_forecast.get('wind_forecast', 0)
            
            for activity in planned_activities:
                adjustment = self._calculate_weather_adjustment(
                    activity, rainfall_forecast, temperature_forecast, wind_forecast
                )
                if adjustment:
                    adjustments.append(adjustment)
            
            return adjustments
            
        except Exception as e:
            logger.error(f"Error calculating weather adjustments: {str(e)}")
            return []
    
    def _get_plantable_crops_for_month(self, month: str, weather_forecast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get crops suitable for planting in the specified month.
        
        Args:
            month: Month name
            weather_forecast: Weather forecast data
            
        Returns:
            List of plantable crops with suitability info
        """
        plantable_crops = []
        all_crops = self.crop_db.get_all_crops()
        
        for crop_id, crop_data in all_crops.items():
            planting_calendar = crop_data.get('planting_calendar', {})
            
            for window_name, window_data in planting_calendar.items():
                start_month = window_data.get('start')
                end_month = window_data.get('end')
                months_in_window = self.crop_db._get_month_range(start_month, end_month)
                
                if month in months_in_window:
                    # Calculate suitability based on weather
                    suitability = self._calculate_planting_suitability(
                        crop_data, weather_forecast, window_data
                    )
                    
                    plantable_crops.append({
                        'crop_id': crop_id,
                        'crop_name': crop_data.get('name', crop_id),
                        'window_name': window_name,
                        'start_month': start_month,
                        'end_month': end_month,
                        'suitability_score': suitability,
                        'rainfall_needed': window_data.get('rainfall_needed', 0),
                        'irrigation_required': window_data.get('irrigation_required', False),
                        'planting_advice': self._get_planting_advice(crop_id, month, weather_forecast)
                    })
        
        # Sort by suitability score
        plantable_crops.sort(key=lambda x: x['suitability_score'], reverse=True)
        return plantable_crops
    
    def _get_critical_activities_for_month(self, month: str, location: Tuple[float, float]) -> List[Dict[str, Any]]:
        """
        Get critical activities that should be done in the specified month.
        
        Args:
            month: Month name
            location: Latitude, longitude tuple
            
        Returns:
            List of critical activities
        """
        critical_activities = []
        
        # Month-specific activity mapping
        monthly_activities = {
            'January': [
                {'activity': 'weeding', 'priority': 'high', 'crops': ['maize', 'beans']},
                {'activity': 'fertilizer_application', 'priority': 'high', 'crops': ['maize']},
                {'activity': 'pest_monitoring', 'priority': 'medium', 'crops': ['all']}
            ],
            'February': [
                {'activity': 'second_weeding', 'priority': 'high', 'crops': ['maize', 'beans']},
                {'activity': 'top_dressing', 'priority': 'high', 'crops': ['maize']},
                {'activity': 'disease_monitoring', 'priority': 'medium', 'crops': ['all']}
            ],
            'March': [
                {'activity': 'harvest_preparation', 'priority': 'high', 'crops': ['beans']},
                {'activity': 'storage_preparation', 'priority': 'medium', 'crops': ['all']},
                {'activity': 'field_cleanup', 'priority': 'low', 'crops': ['all']}
            ],
            'April': [
                {'activity': 'harvesting', 'priority': 'high', 'crops': ['beans', 'maize']},
                {'activity': 'drying_process', 'priority': 'high', 'crops': ['all']},
                {'activity': 'post_harvest_handling', 'priority': 'medium', 'crops': ['all']}
            ],
            'November': [
                {'activity': 'land_preparation', 'priority': 'high', 'crops': ['all']},
                {'activity': 'planting', 'priority': 'high', 'crops': ['maize', 'beans']},
                {'activity': 'seed_treatment', 'priority': 'medium', 'crops': ['all']}
            ],
            'December': [
                {'activity': 'continued_planting', 'priority': 'high', 'crops': ['maize', 'beans']},
                {'activity': 'first_weeding', 'priority': 'high', 'crops': ['early_planted']},
                {'activity': 'fertilizer_application', 'priority': 'medium', 'crops': ['maize']}
            ]
        }
        
        # Add default activities for other months
        default_activities = {
            'May': [{'activity': 'land_preparation', 'priority': 'medium', 'crops': ['all']}],
            'June': [{'activity': 'equipment_maintenance', 'priority': 'medium', 'crops': ['all']}],
            'July': [{'activity': 'planning_next_season', 'priority': 'medium', 'crops': ['all']}],
            'August': [{'activity': 'seed_procurement', 'priority': 'medium', 'crops': ['all']}],
            'September': [{'activity': 'land_preparation', 'priority': 'high', 'crops': ['all']}],
            'October': [{'activity': 'early_planting_prep', 'priority': 'high', 'crops': ['all']}]
        }
        
        # Get activities for the month
        month_activities = monthly_activities.get(month, default_activities.get(month, []))
        
        for activity_info in month_activities:
            critical_activities.append({
                'activity': activity_info['activity'],
                'priority': activity_info['priority'],
                'applicable_crops': activity_info['crops'],
                'description': self._get_activity_description('general', activity_info['activity']),
                'timing_window': 'full_month',
                'weather_dependent': self._is_weather_dependent(activity_info['activity'])
            })
        
        return critical_activities
    
    def _get_monthly_timing_alerts(self, month: str, weather_forecast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get timing alerts specific to the month.
        
        Args:
            month: Month name
            weather_forecast: Weather forecast data
            
        Returns:
            List of timing alerts
        """
        alerts = []
        
        # Season-specific alerts
        current_season = self.crop_db.get_current_season(month)
        
        if current_season == 'rainy_season':
            # Rainy season timing alerts
            if month in ['November', 'December']:
                alerts.append({
                    'alert_type': 'planting_window',
                    'message': 'Optimal planting window for main season crops',
                    'urgency': 'high',
                    'recommended_action': 'Complete planting activities as soon as possible'
                })
            
            if month in ['January', 'February']:
                alerts.append({
                    'alert_type': 'maintenance_critical',
                    'message': 'Critical period for weeding and fertilizer application',
                    'urgency': 'high',
                    'recommended_action': 'Prioritize weeding and crop maintenance'
                })
        
        elif current_season == 'dry_season':
            # Dry season timing alerts
            if month in ['March', 'April']:
                alerts.append({
                    'alert_type': 'harvest_window',
                    'message': 'Main harvest period - timing is critical',
                    'urgency': 'high',
                    'recommended_action': 'Harvest crops at optimal maturity'
                })
            
            if month in ['May', 'June']:
                alerts.append({
                    'alert_type': 'post_harvest',
                    'message': 'Focus on proper storage and land preparation',
                    'urgency': 'medium',
                    'recommended_action': 'Ensure proper drying and storage'
                })
        
        # Weather-based alerts
        rainfall_forecast = weather_forecast.get('rainfall_forecast', 0)
        temperature_forecast = weather_forecast.get('temperature_forecast', 25)
        
        if rainfall_forecast > 50 and month in ['November', 'December', 'January']:
            alerts.append({
                'alert_type': 'weather_opportunity',
                'message': 'Excellent rainfall forecast - optimal for planting',
                'urgency': 'medium',
                'recommended_action': 'Take advantage of favorable weather conditions'
            })
        
        if temperature_forecast > 35:
            alerts.append({
                'alert_type': 'weather_caution',
                'message': 'High temperature forecast - protect sensitive crops',
                'urgency': 'medium',
                'recommended_action': 'Ensure adequate water supply and shade'
            })
        
        return alerts
    
    def _get_weather_based_monthly_adjustments(self, month: str, weather_forecast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get weather-based adjustments for monthly activities.
        
        Args:
            month: Month name
            weather_forecast: Weather forecast data
            
        Returns:
            List of weather-based adjustments
        """
        adjustments = []
        
        rainfall_forecast = weather_forecast.get('rainfall_forecast', 0)
        temperature_forecast = weather_forecast.get('temperature_forecast', 25)
        
        # Rainfall-based adjustments
        if rainfall_forecast < 10 and month in ['November', 'December', 'January']:
            adjustments.append({
                'adjustment_type': 'low_rainfall',
                'original_plan': 'Regular planting schedule',
                'recommended_adjustment': 'Delay planting until adequate rainfall',
                'reason': 'Insufficient rainfall for successful germination'
            })
        
        if rainfall_forecast > 100:
            adjustments.append({
                'adjustment_type': 'high_rainfall',
                'original_plan': 'Normal field activities',
                'recommended_adjustment': 'Ensure proper drainage and delay harvesting',
                'reason': 'Excessive rainfall may cause waterlogging'
            })
        
        # Temperature-based adjustments
        if temperature_forecast > 35:
            adjustments.append({
                'adjustment_type': 'high_temperature',
                'original_plan': 'Standard planting/maintenance',
                'recommended_adjustment': 'Increase irrigation and provide shade',
                'reason': 'High temperatures may stress crops'
            })
        
        if temperature_forecast < 18:
            adjustments.append({
                'adjustment_type': 'low_temperature',
                'original_plan': 'Normal growth expectations',
                'recommended_adjustment': 'Expect slower growth and delayed maturity',
                'reason': 'Cool temperatures slow crop development'
            })
        
        return adjustments
    
    def _generate_monthly_advice(self, month: str, season: str, weather_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive monthly advice.
        
        Args:
            month: Month name
            season: Current season
            weather_forecast: Weather forecast data
            
        Returns:
            Monthly advice dictionary
        """
        advice = {
            'priority_focus': '',
            'key_activities': [],
            'weather_considerations': [],
            'planning_ahead': []
        }
        
        # Season-specific advice
        if season == 'rainy_season':
            if month in ['November', 'December']:
                advice['priority_focus'] = 'Planting and establishment'
                advice['key_activities'] = [
                    'Complete land preparation',
                    'Plant main season crops',
                    'Apply basal fertilizer',
                    'Begin pest monitoring'
                ]
            elif month in ['January', 'February']:
                advice['priority_focus'] = 'Crop maintenance'
                advice['key_activities'] = [
                    'Intensive weeding',
                    'Top-dress fertilizer',
                    'Monitor for pests and diseases',
                    'Manage water drainage'
                ]
        
        elif season == 'dry_season':
            if month in ['March', 'April']:
                advice['priority_focus'] = 'Harvesting and storage'
                advice['key_activities'] = [
                    'Harvest at optimal maturity',
                    'Proper drying processes',
                    'Safe storage practices',
                    'Field cleanup'
                ]
            elif month in ['May', 'June', 'July']:
                advice['priority_focus'] = 'Planning and preparation'
                advice['key_activities'] = [
                    'Land preparation',
                    'Equipment maintenance',
                    'Seed procurement',
                    'Skill development'
                ]
        
        # Weather-based considerations
        rainfall_forecast = weather_forecast.get('rainfall_forecast', 0)
        if rainfall_forecast > 30:
            advice['weather_considerations'].append('Take advantage of good rainfall')
        elif rainfall_forecast < 10:
            advice['weather_considerations'].append('Prepare for dry conditions')
        
        # Planning ahead
        next_month = self._get_next_month(month)
        advice['planning_ahead'] = [
            f'Prepare for {next_month} activities',
            'Monitor weather forecasts',
            'Plan resource allocation'
        ]
        
        return advice
    
    def _calculate_planting_suitability(self, crop_data: Dict[str, Any], 
                                      weather_forecast: Dict[str, Any],
                                      window_data: Dict[str, Any]) -> float:
        """
        Calculate planting suitability score.
        
        Args:
            crop_data: Crop data
            weather_forecast: Weather forecast data
            window_data: Planting window data
            
        Returns:
            Suitability score (0-1)
        """
        score = 0.5  # Base score
        
        # Weather suitability
        rainfall_forecast = weather_forecast.get('rainfall_forecast', 0)
        rainfall_needed = window_data.get('rainfall_needed', 0)
        
        if rainfall_forecast >= rainfall_needed:
            score += 0.3
        elif rainfall_forecast >= rainfall_needed * 0.7:
            score += 0.2
        else:
            score += 0.1
        
        # Temperature suitability
        temp_forecast = weather_forecast.get('temperature_forecast', 25)
        temp_req = crop_data.get('temperature_requirements', {})
        optimal_temp = temp_req.get('optimal_temp', 25)
        
        if abs(temp_forecast - optimal_temp) <= 3:
            score += 0.2
        elif abs(temp_forecast - optimal_temp) <= 6:
            score += 0.1
        
        return min(score, 1.0)
    
    def _check_timing_window_alert(self, crop: str, window_name: str, 
                                  window_data: Dict[str, Any], current_month: str,
                                  location: Tuple[float, float]) -> Optional[Dict[str, Any]]:
        """
        Check if there's a timing alert for a planting window.
        
        Args:
            crop: Crop identifier
            window_name: Planting window name
            window_data: Window data
            current_month: Current month
            location: Location coordinates
            
        Returns:
            Alert dictionary if applicable, None otherwise
        """
        start_month = window_data.get('start')
        end_month = window_data.get('end')
        
        if current_month == start_month:
            return {
                'crop': crop,
                'alert_type': 'planting_window_start',
                'message': f'{crop.title()} planting window begins - {window_name}',
                'urgency': 'high',
                'recommended_action': 'Begin planting preparations'
            }
        
        if current_month == end_month:
            return {
                'crop': crop,
                'alert_type': 'planting_window_end',
                'message': f'{crop.title()} planting window ending - {window_name}',
                'urgency': 'high',
                'recommended_action': 'Complete planting immediately'
            }
        
        return None
    
    def _check_activity_timing_alerts(self, crop: str, current_month: str) -> List[Dict[str, Any]]:
        """
        Check for activity timing alerts.
        
        Args:
            crop: Crop identifier
            current_month: Current month
            
        Returns:
            List of activity alerts
        """
        alerts = []
        
        # This is a simplified implementation
        # In practice, you'd track actual planting dates and calculate timing
        
        if current_month in ['January', 'February']:
            alerts.append({
                'crop': crop,
                'alert_type': 'maintenance_critical',
                'message': f'{crop.title()} requires weeding and fertilizer application',
                'urgency': 'high',
                'recommended_action': 'Schedule weeding and fertilizer application'
            })
        
        return alerts
    
    def _calculate_weather_adjustment(self, activity: Dict[str, Any], 
                                    rainfall: float, temperature: float, 
                                    wind: float) -> Optional[Dict[str, Any]]:
        """
        Calculate weather-based adjustment for an activity.
        
        Args:
            activity: Activity information
            rainfall: Rainfall forecast
            temperature: Temperature forecast
            wind: Wind forecast
            
        Returns:
            Adjustment recommendation if needed
        """
        activity_type = activity.get('activity', '')
        planned_date = activity.get('planned_date', '')
        
        # Weather-sensitive activities
        if activity_type in ['planting', 'fertilizer_application', 'spraying']:
            if rainfall > 20:
                return {
                    'original_date': planned_date,
                    'recommended_date': 'Delay until after rain',
                    'reason': 'High rainfall forecast unsuitable for field activities',
                    'activity': activity_type
                }
        
        if activity_type == 'harvesting':
            if rainfall > 10:
                return {
                    'original_date': planned_date,
                    'recommended_date': 'Delay until dry weather',
                    'reason': 'Rain will affect harvest quality',
                    'activity': activity_type
                }
        
        if temperature > 35:
            return {
                'original_date': planned_date,
                'recommended_date': 'Early morning or evening',
                'reason': 'High temperature - avoid midday activities',
                'activity': activity_type
            }
        
        return None
    
    def _get_activity_description(self, crop: str, activity: str) -> str:
        """
        Get description for an activity.
        
        Args:
            crop: Crop identifier
            activity: Activity name
            
        Returns:
            Activity description
        """
        descriptions = {
            'planting': 'Plant seeds at recommended spacing and depth',
            'first_weeding': 'Remove weeds and loosen soil around plants',
            'fertilizer_application': 'Apply basal fertilizer as recommended',
            'second_weeding': 'Second weeding and earthing up',
            'top_dressing': 'Apply top-dress fertilizer',
            'harvest': 'Harvest at optimal maturity',
            'land_preparation': 'Prepare land for planting',
            'pest_monitoring': 'Monitor and control pests',
            'equipment_maintenance': 'Maintain farming equipment'
        }
        
        return descriptions.get(activity, f'Perform {activity} for {crop}')
    
    def _is_weather_dependent(self, activity: str) -> bool:
        """
        Check if activity is weather dependent.
        
        Args:
            activity: Activity name
            
        Returns:
            True if weather dependent
        """
        weather_dependent = [
            'planting', 'weeding', 'fertilizer_application', 
            'harvesting', 'spraying', 'land_preparation'
        ]
        
        return activity in weather_dependent
    
    def _get_urgency_score(self, urgency: str) -> int:
        """
        Get numerical urgency score.
        
        Args:
            urgency: Urgency level
            
        Returns:
            Numerical score
        """
        urgency_scores = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        return urgency_scores.get(urgency, 1)
    
    def _get_next_month(self, current_month: str) -> str:
        """
        Get next month name.
        
        Args:
            current_month: Current month name
            
        Returns:
            Next month name
        """
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        try:
            current_index = months.index(current_month)
            next_index = (current_index + 1) % 12
            return months[next_index]
        except ValueError:
            return 'Unknown'
    
    def _get_planting_advice(self, crop_id: str, month: str, weather_forecast: Dict[str, Any]) -> List[str]:
        """
        Get specific planting advice for a crop in a given month.
        
        Args:
            crop_id: Crop identifier
            month: Month name
            weather_forecast: Weather forecast data
            
        Returns:
            List of planting advice strings
        """
        advice = []
        
        # Get crop data
        crop_data = self.crop_db.get_crop(crop_id)
        if not crop_data:
            return advice
        
        # General planting advice
        advice.append(f"Ensure proper land preparation before planting {crop_id}")
        
        # Weather-based advice
        rainfall_forecast = weather_forecast.get('rainfall_forecast', 0)
        temperature_forecast = weather_forecast.get('temperature_forecast', 25)
        
        if rainfall_forecast < 20:
            advice.append("Consider irrigation or wait for better rainfall")
        elif rainfall_forecast > 80:
            advice.append("Ensure good drainage to prevent waterlogging")
        else:
            advice.append("Good rainfall conditions for planting")
        
        if temperature_forecast > 30:
            advice.append("Plant early morning or late afternoon to avoid heat stress")
        
        # Crop-specific advice
        if crop_id == 'maize':
            advice.append("Plant at recommended spacing of 75cm x 25cm")
            advice.append("Apply basal fertilizer at planting")
        elif crop_id == 'beans':
            advice.append("Treat seeds with appropriate fungicide")
            advice.append("Plant at depth of 3-4cm")
        elif crop_id == 'groundnuts':
            advice.append("Remove shells carefully to avoid damage")
            advice.append("Plant in well-drained soil")
        
        # Season-specific advice
        current_season = self.crop_db.get_current_season(month)
        if current_season == 'rainy_season':
            advice.append("Take advantage of rainy season for optimal growth")
        elif current_season == 'dry_season':
            advice.append("Ensure adequate irrigation for dry season planting")
        
        return advice


# Global instance
planting_calendar = PlantingCalendar() 