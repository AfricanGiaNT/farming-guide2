"""
Seasonal Analysis Module for Agricultural Recommendations
Analyzes historical weather patterns to identify wet/dry seasons and extreme events
"""
import math
from typing import Dict, List, Tuple
from datetime import datetime


class SeasonalAnalyzer:
    """Analyzes weather patterns to identify agricultural seasons and risks"""
    
    # Thresholds based on Malawi agricultural practices
    WET_SEASON_THRESHOLD_MM = 100  # Months with >100mm are wet season
    DROUGHT_ANNUAL_THRESHOLD_MM = 400  # Years with <400mm are drought years
    FLOOD_ANNUAL_THRESHOLD_MM = 1200  # Years with >1200mm are flood years
    FLOOD_MONTHLY_THRESHOLD_MM = 300  # Single month with >300mm indicates flood risk
    
    MONTH_ORDER = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    def __init__(self):
        """Initialize the seasonal analyzer"""
        pass
    
    def detect_seasons(self, monthly_averages: Dict[str, float]) -> Dict:
        """
        Identify wet and dry seasons based on monthly rainfall averages.
        
        Args:
            monthly_averages: Dict with month names as keys and average rainfall as values
            
        Returns:
            Dict with wet_season_months, dry_season_months, and related statistics
        """
        wet_months = []
        dry_months = []
        
        for month in self.MONTH_ORDER:
            rainfall = monthly_averages.get(month, 0)
            if rainfall > self.WET_SEASON_THRESHOLD_MM:
                wet_months.append(month)
            else:
                dry_months.append(month)
        
        # Calculate season averages
        wet_season_total = sum(monthly_averages.get(m, 0) for m in wet_months)
        dry_season_total = sum(monthly_averages.get(m, 0) for m in dry_months)
        
        wet_season_avg = wet_season_total / len(wet_months) if wet_months else 0
        dry_season_avg = dry_season_total / len(dry_months) if dry_months else 0
        
        return {
            'wet_season_months': wet_months,
            'dry_season_months': dry_months,
            'wet_season_average_rainfall_mm': round(wet_season_avg, 1),
            'dry_season_average_rainfall_mm': round(dry_season_avg, 1),
            'wet_season_total_rainfall_mm': round(wet_season_total, 1),
            'dry_season_total_rainfall_mm': round(dry_season_total, 1),
            'wet_season_count': len(wet_months),
            'dry_season_count': len(dry_months)
        }
    
    def calculate_variability(self, annual_totals: List[float]) -> Dict:
        """
        Calculate rainfall variability using coefficient of variation.
        
        Args:
            annual_totals: List of annual rainfall totals across multiple years
            
        Returns:
            Dict with percentage, level, and interpretation
        """
        if not annual_totals or len(annual_totals) < 2:
            return {
                'percentage': 0.0,
                'level': 'Unknown',
                'interpretation': 'Insufficient data for variability analysis',
                'coefficient_of_variation': 0.0
            }
        
        mean_rainfall = sum(annual_totals) / len(annual_totals)
        
        # Calculate standard deviation
        variance = sum((x - mean_rainfall) ** 2 for x in annual_totals) / len(annual_totals)
        std_dev = math.sqrt(variance)
        
        # Coefficient of variation (CV)
        cv = (std_dev / mean_rainfall) if mean_rainfall > 0 else 0
        percentage = cv * 100
        
        # Classify variability level
        if percentage < 20:
            level = 'Low'
            interpretation = 'Rainfall is relatively predictable across years.'
        elif percentage < 30:
            level = 'Medium'
            interpretation = 'Moderate rainfall variability. Some years differ significantly.'
        else:
            level = 'High'
            interpretation = 'High rainfall variability. Plan for both drought and excess water scenarios.'
        
        return {
            'percentage': round(percentage, 1),
            'level': level,
            'interpretation': interpretation,
            'coefficient_of_variation': round(cv, 3)
        }
    
    def count_extreme_events(self, per_year_data: List[Dict]) -> Dict:
        """
        Count drought and flood years based on annual rainfall.
        
        Args:
            per_year_data: List of year dictionaries with annual_rainfall
            
        Returns:
            Dict with drought_years, flood_years, and event details
        """
        drought_years = []
        flood_years = []
        flood_month_events = []
        
        for year_data in per_year_data:
            year = year_data.get('year')
            annual_rainfall = year_data.get('annual_rainfall', 0)
            monthly_data = year_data.get('monthly', {})
            
            # Check for drought
            if annual_rainfall < self.DROUGHT_ANNUAL_THRESHOLD_MM:
                drought_years.append(year)
            
            # Check for flood (by annual total or single extreme month)
            if annual_rainfall > self.FLOOD_ANNUAL_THRESHOLD_MM:
                flood_years.append(year)
            else:
                # Check for extreme single-month rainfall
                for month, rainfall in monthly_data.items():
                    if rainfall > self.FLOOD_MONTHLY_THRESHOLD_MM:
                        if year not in flood_years:
                            flood_years.append(year)
                        flood_month_events.append({
                            'year': year,
                            'month': month,
                            'rainfall_mm': rainfall
                        })
        
        return {
            'drought_years': len(drought_years),
            'drought_year_list': sorted(drought_years),
            'flood_years': len(flood_years),
            'flood_year_list': sorted(flood_years),
            'flood_month_events': flood_month_events,
            'total_years_analyzed': len(per_year_data),
            'drought_threshold_mm': self.DROUGHT_ANNUAL_THRESHOLD_MM,
            'flood_threshold_mm': self.FLOOD_ANNUAL_THRESHOLD_MM
        }
    
    def generate_warnings_and_advice(
        self, 
        variability: Dict, 
        extreme_events: Dict,
        seasonal_data: Dict
    ) -> Tuple[List[str], List[str]]:
        """
        Generate contextual warnings and advice based on analysis.
        
        Args:
            variability: Variability analysis results
            extreme_events: Extreme event counts
            seasonal_data: Seasonal detection results
            
        Returns:
            Tuple of (warnings, advice) as lists of strings
        """
        warnings = []
        advice = []
        
        # Variability warnings
        if variability['level'] == 'High':
            warnings.append('[WARNING] High rainfall variability detected. Expect unpredictable seasons.')
            advice.append('Plant drought-resistant crop varieties')
            advice.append('Consider crop insurance or diversification strategies')
        elif variability['level'] == 'Medium':
            warnings.append('[WARNING] Moderate rainfall variability. Some years may differ significantly.')
            advice.append('Prepare contingency plans for both wet and dry conditions')
        
        # Drought warnings
        drought_pct = (extreme_events['drought_years'] / extreme_events['total_years_analyzed'] * 100) if extreme_events['total_years_analyzed'] > 0 else 0
        if drought_pct > 30:
            warnings.append(f'[WARNING] Frequent droughts: {extreme_events["drought_years"]} of {extreme_events["total_years_analyzed"]} years analyzed.')
            advice.append('Prioritize drought-tolerant crops like cassava, sorghum, or millet')
            advice.append('Invest in water conservation techniques (mulching, water harvesting)')
        
        # Flood warnings
        flood_pct = (extreme_events['flood_years'] / extreme_events['total_years_analyzed'] * 100) if extreme_events['total_years_analyzed'] > 0 else 0
        if flood_pct > 20:
            warnings.append(f'[WARNING] Flood risk detected in {extreme_events["flood_years"]} of {extreme_events["total_years_analyzed"]} years.')
            advice.append('Ensure proper drainage in planting areas')
            advice.append('Consider planting on ridges or raised beds')
        
        # Extreme month warnings
        if extreme_events.get('flood_month_events'):
            warnings.append('[WARNING] Extreme rainfall months detected. Risk of waterlogging.')
            advice.append('Monitor weather forecasts during wet season')
        
        # Dry season length
        if seasonal_data['dry_season_count'] > 6:
            advice.append('Long dry season detected. Plan for dry-season cropping or irrigation')
        
        # If no wet season detected
        if not seasonal_data['wet_season_months']:
            warnings.append('[WARNING] No clear wet season identified. Consult local extension officer.')
        
        # General advice if conditions are stable
        if variability['level'] == 'Low' and drought_pct < 20 and flood_pct < 20:
            advice.append('Stable rainfall patterns detected. Good conditions for planning')
            advice.append('Consider both early and late-season plantings')
        
        return warnings, advice
    
    def analyze_weather_patterns(self, historical_data: Dict) -> Dict:
        """
        Comprehensive weather pattern analysis for agricultural recommendations.
        
        Args:
            historical_data: Complete historical weather data from API
            
        Returns:
            Complete agricultural analysis including seasons, variability, and events
        """
        # Extract required data
        monthly_averages_raw = historical_data.get('monthly_averages', {})
        monthly_averages = {}
        for month, data in monthly_averages_raw.items():
            if isinstance(data, dict):
                monthly_averages[month] = data.get('average_rainfall', 0)
            elif isinstance(data, (int, float)):
                monthly_averages[month] = data
            else:
                monthly_averages[month] = 0
        
        per_year_data = historical_data.get('per_year', [])
        annual_totals = [year['annual_rainfall'] for year in per_year_data if 'annual_rainfall' in year]
        
        # Perform analyses
        seasonal_data = self.detect_seasons(monthly_averages)
        variability = self.calculate_variability(annual_totals)
        extreme_events = self.count_extreme_events(per_year_data)
        warnings, advice = self.generate_warnings_and_advice(variability, extreme_events, seasonal_data)
        
        return {
            'wet_season': {
                'months': seasonal_data['wet_season_months'],
                'average_monthly_rainfall_mm': seasonal_data['wet_season_average_rainfall_mm'],
                'total_season_rainfall_mm': seasonal_data['wet_season_total_rainfall_mm'],
            },
            'dry_season': {
                'months': seasonal_data['dry_season_months'],
                'average_monthly_rainfall_mm': seasonal_data['dry_season_average_rainfall_mm'],
                'total_season_rainfall_mm': seasonal_data['dry_season_total_rainfall_mm'],
            },
            'variability': variability,
            'extreme_events': extreme_events,
            'warnings': warnings,
            'advice': advice,
            'years_analyzed': len(per_year_data)
        }

