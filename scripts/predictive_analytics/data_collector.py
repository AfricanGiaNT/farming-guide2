"""
Data Collector Module for Predictive Analytics.

Aggregates data from existing systems (weather engine, crop advisor) 
for use in yield prediction models.
"""
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np

from scripts.weather_engine.weather_api import weather_api
from scripts.crop_advisor.crop_database import CropDatabase
from scripts.utils.logger import logger


class DataCollector:
    """Collects and aggregates data from various sources for predictive analytics."""
    
    def __init__(self):
        """Initialize the data collector with required components."""
        self.crop_db = CropDatabase()
        self.weather_api = weather_api
        self.mock_data_file = "data/mock_yield_data.json"
        
    def get_weather_data(self, lat: float, lon: float, days: int = 30, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Collect weather data for a specific location.
        
        Args:
            lat: Latitude
            lon: Longitude  
            days: Number of days to collect
            user_id: Optional user ID for logging
            
        Returns:
            Dictionary containing weather data
        """
        try:
            # Get current weather
            current_weather = self.weather_api.get_current_weather(lat, lon, user_id)
            
            # Get forecast data
            forecast_data = self.weather_api.get_weather_forecast(lat, lon, min(days, 7), user_id)
            
            # Get rainfall data
            rainfall_data = self.weather_api.get_rainfall_data(lat, lon, user_id)
            
            weather_summary = {
                'current': current_weather,
                'forecast': forecast_data,
                'rainfall': rainfall_data,
                'location': {'lat': lat, 'lon': lon},
                'collection_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Weather data collected for {lat}, {lon}", user_id)
            return weather_summary
            
        except Exception as e:
            logger.error(f"Error collecting weather data: {e}", user_id)
            return {}
    
    def get_crop_data(self, crop_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Collect crop-specific data for prediction models.
        
        Args:
            crop_id: Crop identifier
            user_id: Optional user ID for logging
            
        Returns:
            Dictionary containing crop data
        """
        try:
            crop_data = self.crop_db.get_crop(crop_id)
            if not crop_data:
                logger.warning(f"Crop data not found for {crop_id}", user_id)
                return {}
            
            # Get crop varieties
            varieties = self.crop_db.get_crop_varieties(crop_id)
            
            # Get seasonal information
            seasonal_calendar = self.crop_db.get_seasonal_calendar()
            
            crop_summary = {
                'crop_info': crop_data,
                'varieties': varieties,
                'seasonal_calendar': seasonal_calendar,
                'water_requirements': crop_data.get('water_requirements', {}),
                'growth_characteristics': crop_data.get('growth_characteristics', {}),
                'collection_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Crop data collected for {crop_id}", user_id)
            return crop_summary
            
        except Exception as e:
            logger.error(f"Error collecting crop data: {e}", user_id)
            return {}
    
    def generate_mock_yield_data(self, crop_id: str, location: Dict[str, float], years: int = 5) -> List[Dict[str, Any]]:
        """
        Generate mock historical yield data for testing and validation.
        
        Args:
            crop_id: Crop identifier
            location: Dictionary with lat/lon coordinates
            years: Number of years of data to generate
            
        Returns:
            List of mock yield data entries
        """
        try:
            crop_data = self.crop_db.get_crop(crop_id)
            if not crop_data:
                logger.warning(f"Cannot generate mock data for unknown crop: {crop_id}")
                return []
            
            # Get base yield information
            base_yield = crop_data.get('yield_characteristics', {}).get('average_yield_ha', 2.5)  # tons/ha
            yield_variability = crop_data.get('yield_characteristics', {}).get('yield_variability', 0.3)
            
            mock_data = []
            current_date = datetime.now() - timedelta(days=years * 365)
            
            for year in range(years):
                for season in ['rainy', 'dry']:
                    # Generate realistic yield based on season
                    if season == 'rainy':
                        season_multiplier = np.random.normal(1.2, 0.2)  # Better yields in rainy season
                    else:
                        season_multiplier = np.random.normal(0.8, 0.3)  # Lower yields in dry season
                    
                    # Add some weather-based variation
                    weather_factor = np.random.normal(1.0, 0.15)
                    
                    # Calculate yield
                    actual_yield = base_yield * season_multiplier * weather_factor
                    actual_yield = max(0.1, actual_yield)  # Ensure positive yield
                    
                    # Generate weather data for this period
                    weather_data = self._generate_mock_weather(location, season)
                    
                    mock_entry = {
                        'year': current_date.year + year,
                        'season': season,
                        'crop_id': crop_id,
                        'location': location,
                        'yield_tons_ha': round(actual_yield, 2),
                        'weather_data': weather_data,
                        'planting_date': f"{current_date.year + year}-{self._get_planting_month(season)}-01",
                        'harvest_date': f"{current_date.year + year}-{self._get_harvest_month(season)}-01",
                        'data_type': 'mock'
                    }
                    
                    mock_data.append(mock_entry)
            
            # Save mock data to file
            self._save_mock_data(mock_data, crop_id)
            
            logger.info(f"Generated {len(mock_data)} mock yield entries for {crop_id}")
            return mock_data
            
        except Exception as e:
            logger.error(f"Error generating mock yield data: {e}")
            return []
    
    def get_combined_data(self, crop_id: str, location: Dict[str, float], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Collect all relevant data for yield prediction.
        
        Args:
            crop_id: Crop identifier
            location: Dictionary with lat/lon coordinates
            user_id: Optional user ID for logging
            
        Returns:
            Dictionary containing all collected data
        """
        try:
            # Collect weather data
            weather_data = self.get_weather_data(location['lat'], location['lon'], user_id=user_id)
            
            # Collect crop data
            crop_data = self.get_crop_data(crop_id, user_id=user_id)
            
            # Get mock historical data
            historical_data = self.generate_mock_yield_data(crop_id, location)
            
            combined_data = {
                'weather': weather_data,
                'crop': crop_data,
                'historical_yields': historical_data,
                'location': location,
                'collection_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Combined data collected for {crop_id} at {location}", user_id)
            return combined_data
            
        except Exception as e:
            logger.error(f"Error collecting combined data: {e}", user_id)
            return {}
    
    def _generate_mock_weather(self, location: Dict[str, float], season: str) -> Dict[str, Any]:
        """Generate realistic mock weather data for a season."""
        if season == 'rainy':
            return {
                'avg_temperature': np.random.normal(25, 3),
                'total_rainfall': np.random.normal(800, 150),
                'rainy_days': np.random.randint(60, 90),
                'humidity': np.random.normal(75, 10)
            }
        else:
            return {
                'avg_temperature': np.random.normal(30, 4),
                'total_rainfall': np.random.normal(200, 80),
                'rainy_days': np.random.randint(10, 30),
                'humidity': np.random.normal(50, 15)
            }
    
    def _get_planting_month(self, season: str) -> str:
        """Get planting month for season."""
        return "11" if season == "rainy" else "04"
    
    def _get_harvest_month(self, season: str) -> str:
        """Get harvest month for season."""
        return "04" if season == "rainy" else "08"
    
    def _save_mock_data(self, mock_data: List[Dict[str, Any]], crop_id: str) -> None:
        """Save mock data to JSON file."""
        try:
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            # Load existing data if any
            existing_data = {}
            if os.path.exists(self.mock_data_file):
                with open(self.mock_data_file, 'r') as f:
                    existing_data = json.load(f)
            
            # Add new mock data
            if crop_id not in existing_data:
                existing_data[crop_id] = []
            
            existing_data[crop_id].extend(mock_data)
            
            # Save updated data
            with open(self.mock_data_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving mock data: {e}")
    
    def load_mock_data(self, crop_id: str) -> List[Dict[str, Any]]:
        """Load mock yield data from file."""
        try:
            if not os.path.exists(self.mock_data_file):
                return []
            
            with open(self.mock_data_file, 'r') as f:
                data = json.load(f)
                return data.get(crop_id, [])
                
        except Exception as e:
            logger.error(f"Error loading mock data: {e}")
            return [] 