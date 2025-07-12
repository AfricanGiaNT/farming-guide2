"""
Crop Database Module for the Agricultural Advisor Bot.
Handles loading and managing crop varieties data for Lilongwe region.
"""
import json
import os
from typing import Dict, List, Optional, Any
from scripts.utils.logger import logger


class CropDatabase:
    """Manages crop varieties database and provides query functionality."""
    
    def __init__(self, data_file: str = "data/crop_varieties.json"):
        """
        Initialize the crop database.
        
        Args:
            data_file: Path to the crop varieties JSON file
        """
        self.data_file = data_file
        self.crops_data = None
        self.seasonal_calendar = None
        self.load_database()
    
    def load_database(self) -> bool:
        """
        Load crop varieties database from JSON file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.crops_data = data.get('lilongwe_crops', {})
                self.seasonal_calendar = data.get('seasonal_calendar', {})
                logger.info(f"Loaded {len(self.crops_data)} crop types from database")
                return True
        except FileNotFoundError:
            logger.error(f"Crop database file not found: {self.data_file}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in crop database: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading crop database: {e}")
            return False
    
    def get_all_crops(self) -> Dict[str, Any]:
        """
        Get all crops data.
        
        Returns:
            Dictionary of all crops data
        """
        return self.crops_data or {}
    
    def get_crop(self, crop_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific crop data by ID.
        
        Args:
            crop_id: Crop identifier (e.g., 'maize', 'beans')
            
        Returns:
            Crop data dictionary or None if not found
        """
        return self.crops_data.get(crop_id) if self.crops_data else None
    
    def get_crop_varieties(self, crop_id: str) -> List[Dict[str, Any]]:
        """
        Get varieties for a specific crop.
        
        Args:
            crop_id: Crop identifier
            
        Returns:
            List of variety dictionaries
        """
        crop = self.get_crop(crop_id)
        return crop.get('varieties', []) if crop else []
    
    def get_crops_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get crops by category (cereal, legume, root_tuber).
        
        Args:
            category: Crop category
            
        Returns:
            Dictionary of crops in the specified category
        """
        if not self.crops_data:
            return {}
        
        filtered_crops = {}
        for crop_id, crop_data in self.crops_data.items():
            if crop_data.get('category') == category:
                filtered_crops[crop_id] = crop_data
        
        return filtered_crops
    
    def get_drought_tolerant_crops(self, tolerance_level: str = "good") -> List[str]:
        """
        Get crops with specified drought tolerance level.
        
        Args:
            tolerance_level: Minimum drought tolerance level
            
        Returns:
            List of crop IDs with matching tolerance
        """
        if not self.crops_data:
            return []
        
        tolerance_hierarchy = {
            "excellent": 3,
            "good": 2,
            "moderate": 1,
            "poor": 0
        }
        
        min_tolerance = tolerance_hierarchy.get(tolerance_level, 1)
        drought_tolerant = []
        
        for crop_id, crop_data in self.crops_data.items():
            varieties = crop_data.get('varieties', [])
            for variety in varieties:
                variety_tolerance = variety.get('drought_tolerance', 'moderate')
                if tolerance_hierarchy.get(variety_tolerance, 1) >= min_tolerance:
                    if crop_id not in drought_tolerant:
                        drought_tolerant.append(crop_id)
                    break
        
        return drought_tolerant
    
    def get_crops_for_rainfall(self, rainfall_mm: float) -> List[Dict[str, Any]]:
        """
        Get crops suitable for given rainfall amount.
        
        Args:
            rainfall_mm: Rainfall amount in millimeters
            
        Returns:
            List of suitable crop data with suitability scores
        """
        if not self.crops_data:
            return []
        
        suitable_crops = []
        
        for crop_id, crop_data in self.crops_data.items():
            water_req = crop_data.get('water_requirements', {})
            min_rainfall = water_req.get('minimum_rainfall', 0)
            optimal_rainfall = water_req.get('optimal_rainfall', 0)
            max_rainfall = water_req.get('maximum_rainfall', 2000)
            
            # Calculate suitability score
            if rainfall_mm < min_rainfall:
                suitability = max(0, (rainfall_mm / min_rainfall) * 0.5)
            elif rainfall_mm <= optimal_rainfall:
                suitability = 0.5 + (rainfall_mm - min_rainfall) / (optimal_rainfall - min_rainfall) * 0.5
            elif rainfall_mm <= max_rainfall:
                suitability = 1.0 - (rainfall_mm - optimal_rainfall) / (max_rainfall - optimal_rainfall) * 0.3
            else:
                suitability = 0.7 - min(0.5, (rainfall_mm - max_rainfall) / 500)
            
            suitable_crops.append({
                'crop_id': crop_id,
                'crop_data': crop_data,
                'suitability_score': max(0, suitability),
                'rainfall_match': 'excellent' if suitability >= 0.8 else 
                                'good' if suitability >= 0.6 else 
                                'fair' if suitability >= 0.4 else 'poor'
            })
        
        # Sort by suitability score
        suitable_crops.sort(key=lambda x: x['suitability_score'], reverse=True)
        return suitable_crops
    
    def get_seasonal_calendar(self) -> Dict[str, Any]:
        """
        Get seasonal calendar information.
        
        Returns:
            Seasonal calendar data
        """
        return self.seasonal_calendar or {}
    
    def get_current_season(self, month: str) -> str:
        """
        Determine current season based on month.
        
        Args:
            month: Month name (e.g., 'January', 'July')
            
        Returns:
            Season name ('rainy_season' or 'dry_season')
        """
        if not self.seasonal_calendar:
            return 'unknown'
        
        rainy_season = self.seasonal_calendar.get('rainy_season', {})
        dry_season = self.seasonal_calendar.get('dry_season', {})
        
        rainy_months = ['November', 'December', 'January', 'February', 'March', 'April']
        dry_months = ['May', 'June', 'July', 'August', 'September', 'October']
        
        if month in rainy_months:
            return 'rainy_season'
        elif month in dry_months:
            return 'dry_season'
        else:
            return 'unknown'
    
    def get_planting_recommendations(self, crop_id: str, current_month: str) -> Dict[str, Any]:
        """
        Get planting recommendations for a specific crop and month.
        
        Args:
            crop_id: Crop identifier
            current_month: Current month name
            
        Returns:
            Planting recommendations dictionary
        """
        crop = self.get_crop(crop_id)
        if not crop:
            return {}
        
        planting_calendar = crop.get('planting_calendar', {})
        current_season = self.get_current_season(current_month)
        
        recommendations = {
            'crop_id': crop_id,
            'crop_name': crop.get('name', crop_id),
            'current_month': current_month,
            'current_season': current_season,
            'planting_windows': [],
            'optimal_timing': None,
            'season_match': False
        }
        
        # Check each planting window
        for window_name, window_data in planting_calendar.items():
            start_month = window_data.get('start')
            end_month = window_data.get('end')
            rainfall_needed = window_data.get('rainfall_needed', 0)
            irrigation_required = window_data.get('irrigation_required', False)
            
            # Simple month matching (could be improved with date ranges)
            month_list = self._get_month_range(start_month, end_month)
            is_current_window = current_month in month_list
            
            window_info = {
                'window_name': window_name,
                'start_month': start_month,
                'end_month': end_month,
                'rainfall_needed': rainfall_needed,
                'irrigation_required': irrigation_required,
                'is_current_window': is_current_window,
                'months': month_list
            }
            
            recommendations['planting_windows'].append(window_info)
            
            if is_current_window:
                recommendations['optimal_timing'] = window_info
                recommendations['season_match'] = True
        
        return recommendations
    
    def _get_month_range(self, start_month: str, end_month: str) -> List[str]:
        """
        Get list of months between start and end month.
        
        Args:
            start_month: Starting month name
            end_month: Ending month name
            
        Returns:
            List of month names in range
        """
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        try:
            start_idx = months.index(start_month)
            end_idx = months.index(end_month)
            
            if start_idx <= end_idx:
                return months[start_idx:end_idx + 1]
            else:
                # Cross year boundary
                return months[start_idx:] + months[:end_idx + 1]
        except ValueError:
            return []


# Global instance
crop_database = CropDatabase() 