"""
Crop Matching Module
Matches crops to seasonal rainfall patterns based on water requirements
"""
import json
import os
from typing import Dict, List, Optional


class CropMatcher:
    """Matches crops to seasonal patterns based on water requirements"""
    
    # Chichewa translations for common crops
    CHICHEWA_NAMES = {
        'maize': 'Chimanga',
        'beans': 'Nyemba',
        'groundnuts': 'Mtedza',
        'sorghum': 'Mapira',
        'sweet_potato': 'Mbatata',
        'cassava': 'Chinangwa',
        'rice': 'Mpunga',
        'pigeon_pea': 'Nandolo',
        'cowpea': 'Khobwe',
        'millet': 'Mawere',
        'tomato': 'Tomato',
        'cabbage': 'Kabichi',
        'onion': 'Anyezi'
    }
    
    def __init__(self, crop_data_file: str = "data/crop_varieties.json"):
        """
        Initialize crop matcher with crop database.
        
        Args:
            crop_data_file: Path to crop varieties JSON file
        """
        self.crop_data_file = crop_data_file
        self.crops_data = self._load_crop_data()
    
    def _load_crop_data(self) -> Dict:
        """Load crop data from JSON file"""
        try:
            with open(self.crop_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('lilongwe_crops', {})
        except Exception as e:
            print(f"Error loading crop data: {e}")
            return {}
    
    def _get_planting_months(self, planting_calendar: Dict) -> List[str]:
        """Extract planting months from planting calendar"""
        months = []
        for season_data in planting_calendar.values():
            if isinstance(season_data, dict):
                start = season_data.get('start')
                end = season_data.get('end')
                if start:
                    months.append(start)
                if end and end != start:
                    months.append(end)
        return list(set(months))  # Remove duplicates
    
    def _determine_suitable_season(
        self, 
        water_reqs: Dict, 
        planting_calendar: Dict,
        wet_season_avg: float,
        dry_season_avg: float
    ) -> str:
        """
        Determine if crop is suitable for wet, dry, or year-round planting.
        
        Args:
            water_reqs: Crop water requirements
            planting_calendar: Crop planting calendar
            wet_season_avg: Average rainfall in wet season
            dry_season_avg: Average rainfall in dry season
            
        Returns:
            'wet', 'dry', or 'year-round'
        """
        min_rainfall = water_reqs.get('minimum_rainfall', 0)
        optimal_rainfall = water_reqs.get('optimal_rainfall', 0)
        
        # Check planting calendar for season indicators
        has_dry_season_planting = False
        for key, val in planting_calendar.items():
            if isinstance(val, dict):
                if 'dry' in str(key).lower():
                    has_dry_season_planting = True
                    break
                # Check for irrigation requirement
                if val.get('irrigation_required', False):
                    has_dry_season_planting = True
                    break
        
        # Determine based on water needs and seasonal rainfall
        if min_rainfall <= dry_season_avg * 6:  # Can survive on dry season rainfall
            if has_dry_season_planting:
                return 'dry'
            else:
                return 'year-round'
        elif min_rainfall <= wet_season_avg * 6:  # Needs wet season rainfall
            return 'wet'
        else:
            return 'wet'  # High water needs = wet season
    
    def _classify_water_requirement(self, water_reqs: Dict) -> str:
        """
        Classify water requirement as low, medium, or high.
        
        Args:
            water_reqs: Crop water requirements dictionary
            
        Returns:
            'low', 'medium', or 'high'
        """
        min_rainfall = water_reqs.get('minimum_rainfall', 0)
        optimal_rainfall = water_reqs.get('optimal_rainfall', 0)
        
        # Classification based on minimum rainfall needs
        if min_rainfall < 350:
            return 'low'
        elif min_rainfall < 500:
            return 'medium'
        else:
            return 'high'
    
    def match_crops_to_season(
        self, 
        season_type: str,
        season_avg_rainfall: float,
        season_months: List[str],
        variability_level: str = 'Low'
    ) -> List[Dict]:
        """
        Find suitable crops for a given season.
        
        Args:
            season_type: 'wet' or 'dry'
            season_avg_rainfall: Average monthly rainfall in the season
            season_months: List of months in the season
            variability_level: Rainfall variability level
            
        Returns:
            List of suitable crop recommendations
        """
        suitable_crops = []
        
        # Calculate total season rainfall (approximate)
        season_total_rainfall = season_avg_rainfall * len(season_months)
        
        for crop_id, crop_data in self.crops_data.items():
            water_reqs = crop_data.get('water_requirements', {})
            planting_calendar = crop_data.get('planting_calendar', {})
            
            min_rainfall = water_reqs.get('minimum_rainfall', 0)
            max_rainfall = water_reqs.get('maximum_rainfall', 999999)
            optimal_rainfall = water_reqs.get('optimal_rainfall', 0)
            
            # Check if crop's water needs match the season's rainfall
            if season_total_rainfall < min_rainfall:
                continue  # Not enough rain
            
            if season_total_rainfall > max_rainfall:
                # Too much rain, but might still be suitable with proper drainage
                if season_type == 'dry':
                    continue  # Skip if claiming to be dry season but has excess rain
            
            # Get planting months
            planting_months = self._get_planting_months(planting_calendar)
            
            # Check if any planting months overlap with season months
            if planting_months and season_months:
                has_overlap = any(month in season_months for month in planting_months)
                if not has_overlap and season_type == 'wet':
                    # For wet season, be lenient if crop needs high water
                    if min_rainfall > 500:
                        pass  # Allow high-water crops even if planting month doesn't perfectly match
                    else:
                        continue
            
            # Determine suitable season for this crop
            suitable_season = self._determine_suitable_season(
                water_reqs, planting_calendar, season_avg_rainfall, 0
            )
            
            # Match season type
            if season_type == 'wet' and suitable_season == 'dry':
                continue  # Don't recommend dry-season crops for wet season
            elif season_type == 'dry' and suitable_season == 'wet':
                continue  # Don't recommend wet-season crops for dry season
            
            # Build crop recommendation
            crop_name = crop_data.get('name', crop_id.replace('_', ' ').title())
            local_name = self.CHICHEWA_NAMES.get(crop_id, '')
            
            # Get representative variety (first one or best one)
            varieties = crop_data.get('varieties', [])
            days_to_harvest = varieties[0].get('maturity_days', 0) if varieties else 0
            
            # Add drought tolerance note if high variability
            notes = []
            if variability_level == 'High' and varieties:
                # Find drought-tolerant varieties
                drought_tolerant = [
                    v['name'] for v in varieties 
                    if v.get('drought_tolerance') in ['excellent', 'good']
                ]
                if drought_tolerant:
                    notes.append(f"Choose drought-tolerant varieties: {', '.join(drought_tolerant[:2])}")
                else:
                    notes.append("Consider drought-resistant varieties if available")
            
            # Add water management notes
            if season_total_rainfall > optimal_rainfall * 1.5:
                notes.append("Ensure proper drainage. Consider ridging or raised beds.")
            elif season_total_rainfall < optimal_rainfall:
                notes.append("Rainfall below optimal. Monitor soil moisture closely.")
            
            suitable_crops.append({
                'crop_name': crop_name,
                'local_name': local_name,
                'crop_id': crop_id,
                'water_requirement': self._classify_water_requirement(water_reqs),
                'planting_months': planting_months,
                'days_to_harvest': days_to_harvest,
                'min_rainfall_mm': min_rainfall,
                'max_rainfall_mm': max_rainfall,
                'optimal_rainfall_mm': optimal_rainfall,
                'notes': ' '.join(notes) if notes else None,
                'match_score': self._calculate_match_score(
                    season_total_rainfall, optimal_rainfall, min_rainfall, max_rainfall
                )
            })
        
        # Sort by match score (best matches first)
        suitable_crops.sort(key=lambda x: x['match_score'], reverse=True)
        
        return suitable_crops
    
    def _calculate_match_score(
        self, 
        actual_rainfall: float, 
        optimal: float, 
        minimum: float, 
        maximum: float
    ) -> float:
        """
        Calculate how well the actual rainfall matches crop requirements.
        
        Args:
            actual_rainfall: Actual seasonal rainfall
            optimal: Optimal rainfall for crop
            minimum: Minimum rainfall required
            maximum: Maximum rainfall tolerated
            
        Returns:
            Match score (0-100, higher is better)
        """
        if actual_rainfall < minimum:
            return 0  # Not viable
        
        if actual_rainfall > maximum:
            # Over maximum, but give some score
            excess = actual_rainfall - maximum
            penalty = min(excess / maximum, 0.5)  # Max 50% penalty
            return 50 * (1 - penalty)
        
        if actual_rainfall == optimal:
            return 100  # Perfect match
        
        # Calculate distance from optimal
        if actual_rainfall < optimal:
            # Between minimum and optimal
            range_span = optimal - minimum
            distance_from_optimal = optimal - actual_rainfall
            score = 100 - (distance_from_optimal / range_span * 30)  # Max 30 points deduction
        else:
            # Between optimal and maximum
            range_span = maximum - optimal
            distance_from_optimal = actual_rainfall - optimal
            score = 100 - (distance_from_optimal / range_span * 20)  # Max 20 points deduction
        
        return max(50, min(100, score))  # Clamp between 50-100 for viable crops
    
    def get_agricultural_recommendations(
        self, 
        seasonal_analysis: Dict
    ) -> Dict:
        """
        Generate complete agricultural recommendations based on seasonal analysis.
        
        Args:
            seasonal_analysis: Complete seasonal analysis from SeasonalAnalyzer
            
        Returns:
            Agricultural recommendations with crops for each season
        """
        wet_season_data = seasonal_analysis.get('wet_season', {})
        dry_season_data = seasonal_analysis.get('dry_season', {})
        variability = seasonal_analysis.get('variability', {})
        
        # Match crops for wet season
        wet_crops = self.match_crops_to_season(
            'wet',
            wet_season_data.get('average_monthly_rainfall_mm', 0),
            wet_season_data.get('months', []),
            variability.get('level', 'Low')
        )
        
        # Match crops for dry season
        dry_crops = self.match_crops_to_season(
            'dry',
            dry_season_data.get('average_monthly_rainfall_mm', 0),
            dry_season_data.get('months', []),
            variability.get('level', 'Low')
        )
        
        return {
            'wet_season': {
                **wet_season_data,
                'suitable_crops': wet_crops[:6]  # Top 6 matches
            },
            'dry_season': {
                **dry_season_data,
                'suitable_crops': dry_crops[:6]  # Top 6 matches
            },
            'variability': variability,
            'extreme_events': seasonal_analysis.get('extreme_events', {}),
            'warnings': seasonal_analysis.get('warnings', []),
            'advice': seasonal_analysis.get('advice', []),
            'years_analyzed': seasonal_analysis.get('years_analyzed', 0)
        }

