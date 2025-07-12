"""
Weather API integration for the Agricultural Advisor Bot.
Connects to OpenWeatherMap API to fetch current weather and forecast data.
"""
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from scripts.utils.config_loader import config
from scripts.utils.logger import logger


class WeatherAPI:
    """Weather API client for OpenWeatherMap."""
    
    def __init__(self):
        self.api_key = config.get_required("OPENWEATHERMAP_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.onecall_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.timeout = 10  # seconds
    
    def get_current_weather(self, lat: float, lon: float, user_id: Optional[str] = None) -> Optional[Dict]:
        """Get current weather for given coordinates."""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            logger.info(f"Fetching current weather for coordinates: {lat}, {lon}", user_id)
            response = requests.get(url, params=params, timeout=self.timeout)
            
            logger.log_api_call("OpenWeatherMap", "current_weather", response.status_code, user_id)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_current_weather(data)
            else:
                logger.error(f"Weather API error: {response.status_code} - {response.text}", user_id)
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request failed: {e}", user_id)
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_current_weather: {e}", user_id)
            return None
    
    def get_weather_forecast(self, lat: float, lon: float, days: int = 7, user_id: Optional[str] = None) -> Optional[Dict]:
        """Get weather forecast for given coordinates."""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            logger.info(f"Fetching {days}-day forecast for coordinates: {lat}, {lon}", user_id)
            response = requests.get(url, params=params, timeout=self.timeout)
            
            logger.log_api_call("OpenWeatherMap", "forecast", response.status_code, user_id)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_forecast_data(data, days)
            else:
                logger.error(f"Forecast API error: {response.status_code} - {response.text}", user_id)
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Forecast API request failed: {e}", user_id)
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_weather_forecast: {e}", user_id)
            return None
    
    def get_rainfall_data(self, lat: float, lon: float, user_id: Optional[str] = None) -> Optional[Dict]:
        """Get rainfall-specific data for agricultural planning."""
        weather_data = self.get_current_weather(lat, lon, user_id)
        forecast_data = self.get_weather_forecast(lat, lon, 7, user_id)
        
        if not weather_data or not forecast_data:
            return None
        
        try:
            rainfall_info = {
                'current_rainfall': weather_data.get('rainfall', 0),
                'humidity': weather_data.get('humidity', 0),
                'forecast_rainfall': self._extract_rainfall_forecast(forecast_data),
                'total_7day_rainfall': self._calculate_total_rainfall(forecast_data),
                'rainy_days_forecast': self._count_rainy_days(forecast_data),
                'coordinates': {'lat': lat, 'lon': lon},
                'location': weather_data.get('location', f"{lat}, {lon}"),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Rainfall data compiled for {lat}, {lon}", user_id)
            return rainfall_info
            
        except Exception as e:
            logger.error(f"Error processing rainfall data: {e}", user_id)
            return None
    
    def _parse_current_weather(self, data: Dict) -> Dict:
        """Parse current weather data from API response."""
        try:
            return {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'weather': data['weather'][0]['description'],
                'weather_main': data['weather'][0]['main'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'rainfall': data.get('rain', {}).get('1h', 0),  # mm in last hour
                'location': data['name'],
                'country': data['sys']['country'],
                'coordinates': {'lat': data['coord']['lat'], 'lon': data['coord']['lon']},
                'timestamp': datetime.now().isoformat()
            }
        except KeyError as e:
            logger.error(f"Missing key in weather data: {e}")
            return {}
    
    def _parse_forecast_data(self, data: Dict, days: int) -> Dict:
        """Parse forecast data from API response."""
        try:
            forecasts = []
            
            for item in data['list'][:days * 8]:  # Limit to requested days
                forecast = {
                    'datetime': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'weather': item['weather'][0]['description'],
                    'weather_main': item['weather'][0]['main'],
                    'rainfall': item.get('rain', {}).get('3h', 0),  # mm in 3 hours
                    'wind_speed': item['wind']['speed']
                }
                forecasts.append(forecast)
            
            return {
                'forecasts': forecasts,
                'location': data['city']['name'],
                'country': data['city']['country'],
                'coordinates': {'lat': data['city']['coord']['lat'], 'lon': data['city']['coord']['lon']},
                'timestamp': datetime.now().isoformat()
            }
            
        except KeyError as e:
            logger.error(f"Missing key in forecast data: {e}")
            return {}
    
    def _extract_rainfall_forecast(self, forecast_data: Dict) -> List[Dict]:
        """Extract rainfall information from forecast data."""
        rainfall_forecast = []
        
        for forecast in forecast_data.get('forecasts', []):
            if forecast['rainfall'] > 0:
                rainfall_forecast.append({
                    'datetime': forecast['datetime'],
                    'rainfall_mm': forecast['rainfall'],
                    'weather': forecast['weather']
                })
        
        return rainfall_forecast
    
    def _calculate_total_rainfall(self, forecast_data: Dict) -> float:
        """Calculate total expected rainfall over forecast period."""
        total = 0
        for forecast in forecast_data.get('forecasts', []):
            total += forecast['rainfall']
        return round(total, 2)
    
    def _count_rainy_days(self, forecast_data: Dict) -> int:
        """Count number of days with expected rainfall."""
        rainy_days = set()
        
        for forecast in forecast_data.get('forecasts', []):
            if forecast['rainfall'] > 0:
                date = forecast['datetime'].split()[0]  # Extract date part
                rainy_days.add(date)
        
        return len(rainy_days)
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """Validate if coordinates are within valid range."""
        return -90 <= lat <= 90 and -180 <= lon <= 180


# Global weather API instance
weather_api = WeatherAPI() 