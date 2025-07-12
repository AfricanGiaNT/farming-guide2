"""
Historical Weather API integration for the Agricultural Advisor Bot.
Provides multi-year historical weather and rainfall data for improved recommendations.
"""

import requests
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta, date
import json
import statistics
from dataclasses import dataclass
from scripts.utils.config_loader import config
from scripts.utils.logger import logger


@dataclass
class HistoricalRainfallData:
    """Data class for historical rainfall analysis."""
    years_analyzed: int
    monthly_averages: Dict[str, float]
    annual_averages: List[float]
    dry_season_months: List[str]
    wet_season_months: List[str]
    drought_years: List[int]
    flood_years: List[int]
    rainfall_variability: float
    climate_trend: str  # 'increasing', 'decreasing', 'stable'


class HistoricalWeatherAPI:
    """Historical weather API client for multi-year climate analysis."""
    
    def __init__(self):
        """Initialize historical weather API."""
        # Using Open-Meteo (free) and Visual Crossing as backup
        self.open_meteo_url = "https://archive-api.open-meteo.com/v1/archive"
        self.visual_crossing_key = config.get("VISUAL_CROSSING_API_KEY", None)  # Optional
        self.timeout = 15  # seconds for historical data requests
        
        logger.info("Historical weather API initialized")
    
    def get_historical_rainfall(self, 
                              lat: float, 
                              lon: float, 
                              years: int = 5,
                              user_id: Optional[str] = None) -> Optional[HistoricalRainfallData]:
        """
        Get historical rainfall data for the specified number of years.
        
        Args:
            lat: Latitude
            lon: Longitude  
            years: Number of years of historical data (1-10)
            user_id: Optional user ID for logging
            
        Returns:
            Historical rainfall analysis or None if failed
        """
        years = min(max(years, 1), 10)  # Ensure 1-10 year range
        
        logger.info(f"Fetching {years} years of historical rainfall for {lat}, {lon}", user_id)
        
        try:
            # Get data from Open-Meteo (free service)
            historical_data = self._get_open_meteo_historical_data(lat, lon, years)
            
            if not historical_data:
                # Fallback to Visual Crossing if available
                historical_data = self._get_visual_crossing_historical_data(lat, lon, years)
            
            if not historical_data:
                logger.error("Failed to fetch historical weather data from all sources", user_id)
                return None
            
            # Analyze the historical data
            rainfall_analysis = self._analyze_historical_rainfall(historical_data, years)
            
            logger.info(f"Historical rainfall analysis complete for {years} years", user_id)
            return rainfall_analysis
            
        except Exception as e:
            logger.error(f"Error fetching historical rainfall data: {e}", user_id)
            return None
    
    def get_monthly_historical_average(self, 
                                     lat: float, 
                                     lon: float, 
                                     month: str,
                                     years: int = 5,
                                     user_id: Optional[str] = None) -> Optional[float]:
        """
        Get historical average rainfall for a specific month.
        
        Args:
            lat: Latitude
            lon: Longitude
            month: Month name (e.g., 'January')
            years: Number of years to analyze
            user_id: Optional user ID for logging
            
        Returns:
            Average rainfall for the month in mm, or None if failed
        """
        historical_data = self.get_historical_rainfall(lat, lon, years, user_id)
        
        if historical_data and month in historical_data.monthly_averages:
            return historical_data.monthly_averages[month]
        
        return None
    
    def compare_current_with_historical(self,
                                      lat: float,
                                      lon: float,
                                      current_rainfall: float,
                                      month: str,
                                      years: int = 5,
                                      user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Compare current rainfall with historical averages.
        
        Args:
            lat: Latitude
            lon: Longitude
            current_rainfall: Current month's rainfall so far
            month: Current month name
            years: Number of years for historical comparison
            user_id: Optional user ID for logging
            
        Returns:
            Comparison analysis or None if failed
        """
        historical_data = self.get_historical_rainfall(lat, lon, years, user_id)
        
        if not historical_data:
            return None
        
        try:
            historical_avg = historical_data.monthly_averages.get(month, 0)
            
            if historical_avg == 0:
                return None
            
            percentage_of_normal = (current_rainfall / historical_avg) * 100
            
            # Determine status
            if percentage_of_normal >= 120:
                status = "above_normal"
                description = "Above normal rainfall"
            elif percentage_of_normal >= 80:
                status = "normal"
                description = "Normal rainfall"
            elif percentage_of_normal >= 50:
                status = "below_normal"
                description = "Below normal rainfall"
            else:
                status = "drought_conditions"
                description = "Drought conditions"
            
            return {
                'current_rainfall': current_rainfall,
                'historical_average': historical_avg,
                'percentage_of_normal': percentage_of_normal,
                'status': status,
                'description': description,
                'years_analyzed': years,
                'month': month
            }
            
        except Exception as e:
            logger.error(f"Error comparing rainfall with historical data: {e}", user_id)
            return None
    
    def _get_open_meteo_historical_data(self, lat: float, lon: float, years: int) -> Optional[List[Dict]]:
        """Get historical data from Open-Meteo API."""
        try:
            current_date = date.today()
            start_date = date(current_date.year - years, 1, 1)
            end_date = date(current_date.year - 1, 12, 31)
            
            params = {
                'latitude': lat,
                'longitude': lon,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'daily': 'precipitation_sum,temperature_2m_mean',
                'timezone': 'auto'
            }
            
            response = requests.get(self.open_meteo_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_open_meteo_data(data)
            else:
                logger.warning(f"Open-Meteo API returned status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching Open-Meteo historical data: {e}")
            return None
    
    def _get_visual_crossing_historical_data(self, lat: float, lon: float, years: int) -> Optional[List[Dict]]:
        """Get historical data from Visual Crossing API (if API key available)."""
        if not self.visual_crossing_key:
            return None
        
        try:
            current_date = date.today()
            start_date = date(current_date.year - years, 1, 1)
            end_date = date(current_date.year - 1, 12, 31)
            
            url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/{start_date}/{end_date}"
            
            params = {
                'key': self.visual_crossing_key,
                'include': 'days',
                'elements': 'precip,temp',
                'unitGroup': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_visual_crossing_data(data)
            else:
                logger.warning(f"Visual Crossing API returned status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching Visual Crossing historical data: {e}")
            return None
    
    def _parse_open_meteo_data(self, data: Dict) -> List[Dict]:
        """Parse Open-Meteo API response."""
        try:
            daily_data = data.get('daily', {})
            dates = daily_data.get('time', [])
            precipitation = daily_data.get('precipitation_sum', [])
            temperatures = daily_data.get('temperature_2m_mean', [])
            
            parsed_data = []
            for i, date_str in enumerate(dates):
                if i < len(precipitation) and i < len(temperatures):
                    parsed_data.append({
                        'date': date_str,
                        'rainfall_mm': precipitation[i] or 0,
                        'temperature_c': temperatures[i] or 20
                    })
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing Open-Meteo data: {e}")
            return []
    
    def _parse_visual_crossing_data(self, data: Dict) -> List[Dict]:
        """Parse Visual Crossing API response."""
        try:
            days = data.get('days', [])
            parsed_data = []
            
            for day in days:
                parsed_data.append({
                    'date': day.get('datetime'),
                    'rainfall_mm': day.get('precip', 0) or 0,
                    'temperature_c': day.get('temp', 20) or 20
                })
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing Visual Crossing data: {e}")
            return []
    
    def _analyze_historical_rainfall(self, historical_data: List[Dict], years: int) -> HistoricalRainfallData:
        """Analyze historical rainfall data."""
        try:
            # Group data by month and year
            monthly_data = {}
            annual_data = {}
            
            for entry in historical_data:
                entry_date = datetime.fromisoformat(entry['date'])
                month_name = entry_date.strftime('%B')
                year = entry_date.year
                rainfall = entry['rainfall_mm']
                
                # Monthly grouping
                if month_name not in monthly_data:
                    monthly_data[month_name] = []
                monthly_data[month_name].append(rainfall)
                
                # Annual grouping
                if year not in annual_data:
                    annual_data[year] = 0
                annual_data[year] += rainfall
            
            # Calculate monthly averages
            monthly_averages = {}
            for month, values in monthly_data.items():
                monthly_averages[month] = sum(values)
            
            # Calculate annual totals
            annual_totals = list(annual_data.values())
            
            # Identify seasons
            wet_season_months = []
            dry_season_months = []
            
            for month, total_rainfall in monthly_averages.items():
                avg_daily = total_rainfall / 30  # Approximate days per month
                if avg_daily > 3:  # More than 3mm per day on average
                    wet_season_months.append(month)
                else:
                    dry_season_months.append(month)
            
            # Identify extreme years
            if annual_totals:
                mean_annual = statistics.mean(annual_totals)
                std_annual = statistics.stdev(annual_totals) if len(annual_totals) > 1 else 0
                
                drought_threshold = mean_annual - std_annual
                flood_threshold = mean_annual + std_annual
                
                drought_years = [year for year, total in annual_data.items() if total < drought_threshold]
                flood_years = [year for year, total in annual_data.items() if total > flood_threshold]
                
                # Calculate variability
                variability = (std_annual / mean_annual) * 100 if mean_annual > 0 else 0
                
                # Determine climate trend
                if len(annual_totals) >= 3:
                    first_half_avg = statistics.mean(annual_totals[:len(annual_totals)//2])
                    second_half_avg = statistics.mean(annual_totals[len(annual_totals)//2:])
                    
                    if second_half_avg > first_half_avg * 1.1:
                        climate_trend = "increasing"
                    elif second_half_avg < first_half_avg * 0.9:
                        climate_trend = "decreasing"
                    else:
                        climate_trend = "stable"
                else:
                    climate_trend = "insufficient_data"
            else:
                drought_years = []
                flood_years = []
                variability = 0
                climate_trend = "no_data"
            
            return HistoricalRainfallData(
                years_analyzed=years,
                monthly_averages=monthly_averages,
                annual_averages=annual_totals,
                dry_season_months=dry_season_months,
                wet_season_months=wet_season_months,
                drought_years=drought_years,
                flood_years=flood_years,
                rainfall_variability=variability,
                climate_trend=climate_trend
            )
            
        except Exception as e:
            logger.error(f"Error analyzing historical rainfall data: {e}")
            return HistoricalRainfallData(
                years_analyzed=0,
                monthly_averages={},
                annual_averages=[],
                dry_season_months=[],
                wet_season_months=[],
                drought_years=[],
                flood_years=[],
                rainfall_variability=0,
                climate_trend="error"
            )


# Global historical weather API instance
historical_weather_api = HistoricalWeatherAPI() 