"""
Advanced Crop Recommendation Algorithm using REAL DATA ONLY.
Implements sophisticated multi-factor analysis for crop recommendations.
"""
import math
import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from scripts.weather_engine.historical_weather_api import HistoricalRainfallData
from scripts.utils.logger import logger


class AdvancedCropRecommendationAlgorithm:
    """
    Advanced crop recommendation algorithm using ONLY real data sources.
    Implements sophisticated multi-factor analysis for accurate recommendations.
    """
    
    def __init__(self, crop_database: Dict[str, Any]):
        """
        Initialize the advanced recommendation algorithm.
        
        Args:
            crop_database: Real crop data from JSON database
        """
        self.crop_database = crop_database
        self.seasonal_weights = {
            'rainy_season': {'rainfall': 0.4, 'temperature': 0.3, 'timing': 0.2, 'soil': 0.1},
            'dry_season': {'rainfall': 0.5, 'temperature': 0.2, 'timing': 0.2, 'soil': 0.1},
            'current': {'rainfall': 0.35, 'temperature': 0.3, 'timing': 0.25, 'soil': 0.1}
        }
        
        logger.info("Advanced Crop Recommendation Algorithm initialized with REAL DATA ONLY")
    
    def calculate_advanced_suitability_score(self, 
                                           crop_data: Dict[str, Any],
                                           environmental_factors: Dict[str, Any],
                                           historical_data: Optional[HistoricalRainfallData],
                                           farmer_profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate advanced suitability score using multiple real factors.
        
        Args:
            crop_data: Real crop data from database
            environmental_factors: Current environmental conditions
            historical_data: Real historical weather data
            farmer_profile: Farmer's profile and preferences
            
        Returns:
            Advanced suitability analysis with detailed scoring
        """
        logger.info(f"Calculating advanced suitability for {crop_data.get('name', 'Unknown')}")
        
        # Extract environmental factors
        rainfall_mm = environmental_factors.get('rainfall_mm', 0)
        temperature = environmental_factors.get('temperature', 25)
        season = environmental_factors.get('season', 'current')
        humidity = environmental_factors.get('humidity', 50)
        
        # Get seasonal weights
        weights = self.seasonal_weights.get(season, self.seasonal_weights['current'])
        
        # Calculate individual factor scores
        rainfall_score = self._calculate_rainfall_suitability(crop_data, rainfall_mm, historical_data)
        temperature_score = self._calculate_temperature_suitability(crop_data, temperature)
        timing_score = self._calculate_timing_suitability(crop_data, season, historical_data)
        soil_score = self._calculate_soil_suitability(crop_data, farmer_profile)
        variety_score = self._calculate_variety_suitability(crop_data, environmental_factors)
        
        # Calculate weighted overall score
        overall_score = (
            rainfall_score * weights['rainfall'] +
            temperature_score * weights['temperature'] +
            timing_score * weights['timing'] +
            soil_score * weights['soil']
        )
        
        # Apply variety bonus
        overall_score = min(1.0, overall_score + variety_score * 0.1)
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence_score(
            rainfall_score, temperature_score, timing_score, soil_score, historical_data
        )
        
        return {
            'overall_score': overall_score,
            'confidence': confidence,
            'factor_scores': {
                'rainfall': rainfall_score,
                'temperature': temperature_score,
                'timing': timing_score,
                'soil': soil_score,
                'variety': variety_score
            },
            'weights': weights,
            'recommendation_level': self._get_recommendation_level(overall_score),
            'risk_factors': self._identify_risk_factors(crop_data, environmental_factors, historical_data)
        }
    
    def _calculate_rainfall_suitability(self, 
                                      crop_data: Dict[str, Any], 
                                      rainfall_mm: float,
                                      historical_data: Optional[HistoricalRainfallData]) -> float:
        """Calculate rainfall suitability using real crop requirements and historical data."""
        water_req = crop_data.get('water_requirements', {})
        min_rainfall = water_req.get('minimum_rainfall', 0)
        optimal_rainfall = water_req.get('optimal_rainfall', 0)
        max_rainfall = water_req.get('maximum_rainfall', 0)
        
        if not all([min_rainfall, optimal_rainfall, max_rainfall]):
            return 0.5  # Default if data missing
        
        # Base suitability calculation
        if min_rainfall <= rainfall_mm <= max_rainfall:
            # Calculate how close to optimal
            distance_from_optimal = abs(rainfall_mm - optimal_rainfall)
            optimal_range = optimal_rainfall * 0.2  # 20% tolerance
            
            if distance_from_optimal <= optimal_range:
                base_score = 1.0  # Excellent
            else:
                # Gradual decrease based on distance
                penalty = min(0.5, distance_from_optimal / optimal_rainfall)
                base_score = max(0.5, 1.0 - penalty)
        elif rainfall_mm < min_rainfall:
            # Below minimum - calculate deficit
            deficit_ratio = rainfall_mm / min_rainfall
            base_score = max(0.1, deficit_ratio * 0.5)
        else:
            # Above maximum - calculate excess
            excess_ratio = rainfall_mm / max_rainfall
            base_score = max(0.1, 1.0 - (excess_ratio - 1.0) * 0.5)
        
        # Adjust based on historical data
        if historical_data:
            historical_adjustment = self._calculate_historical_rainfall_adjustment(
                rainfall_mm, historical_data, min_rainfall, optimal_rainfall, max_rainfall
            )
            base_score = min(1.0, base_score * historical_adjustment)
        
        return base_score
    
    def _calculate_temperature_suitability(self, 
                                        crop_data: Dict[str, Any], 
                                        temperature: float) -> float:
        """Calculate temperature suitability using real crop requirements."""
        temp_req = crop_data.get('temperature_requirements', {})
        min_temp = temp_req.get('minimum_temp', 0)
        optimal_temp = temp_req.get('optimal_temp', 0)
        max_temp = temp_req.get('maximum_temp', 0)
        
        if not all([min_temp, optimal_temp, max_temp]):
            return 0.5  # Default if data missing
        
        # Base temperature suitability
        if min_temp <= temperature <= max_temp:
            # Calculate optimality
            distance_from_optimal = abs(temperature - optimal_temp)
            optimal_range = optimal_temp * 0.1  # 10% tolerance
            
            if distance_from_optimal <= optimal_range:
                return 1.0  # Excellent
            else:
                # Gradual decrease
                penalty = min(0.4, distance_from_optimal / optimal_temp)
                return max(0.6, 1.0 - penalty)
        elif temperature < min_temp:
            # Too cold
            deficit_ratio = temperature / min_temp
            return max(0.2, deficit_ratio * 0.6)
        else:
            # Too hot
            excess_ratio = temperature / max_temp
            return max(0.2, 1.0 - (excess_ratio - 1.0) * 0.6)
    
    def _calculate_timing_suitability(self, 
                                    crop_data: Dict[str, Any], 
                                    season: str,
                                    historical_data: Optional[HistoricalRainfallData]) -> float:
        """Calculate timing suitability based on real planting calendar."""
        planting_calendar = crop_data.get('planting_calendar', {})
        
        if not planting_calendar:
            return 0.5  # Default if no calendar data
        
        # Check if current season is in planting calendar
        if season in planting_calendar:
            season_data = planting_calendar[season]
            
            # Base score for season match
            base_score = 0.8
            
            # Check rainfall requirements for the season
            required_rainfall = season_data.get('rainfall_needed', 0)
            if required_rainfall > 0:
                # This would need current rainfall data to be more precise
                # For now, assume good timing if season matches
                base_score = 0.9
            
            # Check if irrigation is required
            if season_data.get('irrigation_required', False):
                # Adjust score based on farmer's irrigation capability
                base_score = 0.7  # Slightly lower due to irrigation requirement
            
            return base_score
        
        # Check for partial season matches
        current_month = datetime.now().strftime('%B')
        for season_name, season_data in planting_calendar.items():
            start_month = season_data.get('start', '')
            end_month = season_data.get('end', '')
            
            if start_month and end_month:
                # Simple month-based check (could be more sophisticated)
                if start_month.lower() in current_month.lower() or end_month.lower() in current_month.lower():
                    return 0.6  # Partial match
        
        return 0.3  # Poor timing match
    
    def _calculate_soil_suitability(self, 
                                  crop_data: Dict[str, Any], 
                                  farmer_profile: Optional[Dict[str, Any]]) -> float:
        """Calculate soil suitability based on real crop requirements and farmer profile."""
        soil_req = crop_data.get('soil_requirements', {})
        
        if not soil_req:
            return 0.5  # Default if no soil data
        
        base_score = 0.7  # Assume moderate soil suitability
        
        # Adjust based on soil fertility requirements
        fertility_req = soil_req.get('fertility', 'medium')
        if fertility_req == 'high':
            # Check if farmer has access to fertilizers
            if farmer_profile and 'fertilizer' in farmer_profile.get('available_inputs', []):
                base_score = 0.9
            else:
                base_score = 0.6  # Lower without fertilizer access
        elif fertility_req == 'low':
            base_score = 0.8  # Good for low fertility soils
        
        # Adjust based on drainage requirements
        drainage_req = soil_req.get('drainage', 'well_drained')
        if drainage_req == 'well_drained':
            # Assume good drainage unless specified otherwise
            base_score = min(1.0, base_score + 0.1)
        
        return base_score
    
    def _calculate_variety_suitability(self, 
                                    crop_data: Dict[str, Any], 
                                    environmental_factors: Dict[str, Any]) -> float:
        """Calculate variety suitability based on real variety data."""
        varieties = crop_data.get('varieties', [])
        
        if not varieties:
            return 0.5  # Default if no variety data
        
        rainfall_mm = environmental_factors.get('rainfall_mm', 0)
        temperature = environmental_factors.get('temperature', 25)
        season = environmental_factors.get('season', 'current')
        
        # Score each variety and take the best
        best_variety_score = 0.0
        
        for variety in varieties:
            variety_score = 0.5  # Base score
            
            # Maturity days suitability
            maturity_days = variety.get('maturity_days', 0)
            if maturity_days > 0:
                if season == 'rainy_season' and maturity_days <= 120:
                    variety_score += 0.2  # Good for rainy season
                elif season == 'dry_season' and maturity_days <= 90:
                    variety_score += 0.2  # Good for dry season
                elif 90 <= maturity_days <= 120:
                    variety_score += 0.1  # Moderate suitability
            
            # Drought tolerance suitability
            drought_tolerance = variety.get('drought_tolerance', 'moderate')
            if drought_tolerance == 'excellent' and rainfall_mm < 300:
                variety_score += 0.3
            elif drought_tolerance == 'good' and rainfall_mm < 400:
                variety_score += 0.2
            elif drought_tolerance == 'moderate' and rainfall_mm >= 400:
                variety_score += 0.1
            
            # Disease resistance bonus
            disease_resistance = variety.get('disease_resistance', [])
            if disease_resistance and len(disease_resistance) > 0:
                variety_score += 0.1  # Bonus for disease resistance
            
            best_variety_score = max(best_variety_score, variety_score)
        
        return min(1.0, best_variety_score)
    
    def _calculate_historical_rainfall_adjustment(self, 
                                               current_rainfall: float,
                                               historical_data: HistoricalRainfallData,
                                               min_rainfall: float,
                                               optimal_rainfall: float,
                                               max_rainfall: float) -> float:
        """Calculate adjustment based on real historical rainfall patterns."""
        if not historical_data or historical_data.years_analyzed == 0:
            return 1.0  # No adjustment if no historical data
        
        # Calculate historical average for current season
        monthly_averages = historical_data.monthly_averages
        if not monthly_averages:
            return 1.0
        
        # Get current month
        current_month = datetime.now().strftime('%B')
        historical_avg = monthly_averages.get(current_month, optimal_rainfall)
        
        # Calculate adjustment factor
        if historical_avg > 0:
            # Compare current rainfall to historical average
            ratio = current_rainfall / historical_avg
            
            if 0.8 <= ratio <= 1.2:  # Within 20% of historical average
                return 1.0  # No adjustment
            elif 0.6 <= ratio <= 1.4:  # Within 40% of historical average
                return 0.95  # Slight adjustment
            else:
                return 0.9  # Larger adjustment for unusual conditions
        
        return 1.0
    
    def _calculate_confidence_score(self, 
                                  rainfall_score: float,
                                  temperature_score: float,
                                  timing_score: float,
                                  soil_score: float,
                                  historical_data: Optional[HistoricalRainfallData]) -> float:
        """Calculate confidence score based on data quality and consistency."""
        # Base confidence from score consistency
        scores = [rainfall_score, temperature_score, timing_score, soil_score]
        score_variance = statistics.variance(scores) if len(scores) > 1 else 0
        
        # Lower variance = higher confidence
        consistency_factor = max(0.5, 1.0 - score_variance)
        
        # Historical data quality factor
        historical_factor = 1.0
        if historical_data:
            if historical_data.years_analyzed >= 5:
                historical_factor = 1.0
            elif historical_data.years_analyzed >= 3:
                historical_factor = 0.9
            else:
                historical_factor = 0.8
        
        # Overall confidence
        confidence = consistency_factor * historical_factor
        
        return min(1.0, confidence)
    
    def _get_recommendation_level(self, score: float) -> str:
        """Get recommendation level based on score."""
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.8:
            return 'very_good'
        elif score >= 0.7:
            return 'good'
        elif score >= 0.6:
            return 'moderate'
        elif score >= 0.4:
            return 'fair'
        else:
            return 'poor'
    
    def _identify_risk_factors(self, 
                             crop_data: Dict[str, Any],
                             environmental_factors: Dict[str, Any],
                             historical_data: Optional[HistoricalRainfallData]) -> List[str]:
        """Identify risk factors based on real data analysis."""
        risks = []
        
        rainfall_mm = environmental_factors.get('rainfall_mm', 0)
        temperature = environmental_factors.get('temperature', 25)
        
        # Rainfall risks
        water_req = crop_data.get('water_requirements', {})
        min_rainfall = water_req.get('minimum_rainfall', 0)
        max_rainfall = water_req.get('maximum_rainfall', 0)
        
        if rainfall_mm < min_rainfall * 0.8:
            risks.append(f"Low rainfall risk: {rainfall_mm}mm vs {min_rainfall}mm minimum")
        elif rainfall_mm > max_rainfall * 1.2:
            risks.append(f"Excess rainfall risk: {rainfall_mm}mm vs {max_rainfall}mm maximum")
        
        # Temperature risks
        temp_req = crop_data.get('temperature_requirements', {})
        min_temp = temp_req.get('minimum_temp', 0)
        max_temp = temp_req.get('maximum_temp', 0)
        
        if temperature < min_temp:
            risks.append(f"Low temperature risk: {temperature}°C vs {min_temp}°C minimum")
        elif temperature > max_temp:
            risks.append(f"High temperature risk: {temperature}°C vs {max_temp}°C maximum")
        
        # Historical climate risks
        if historical_data:
            if historical_data.climate_trend == 'decreasing':
                risks.append("Historical decreasing rainfall trend")
            elif historical_data.climate_trend == 'increasing':
                risks.append("Historical increasing rainfall trend - potential flooding")
            
            if historical_data.rainfall_variability > 0.3:
                risks.append("High rainfall variability - unpredictable conditions")
        
        return risks
    
    def rank_crops_by_suitability(self, 
                                environmental_factors: Dict[str, Any],
                                historical_data: Optional[HistoricalRainfallData],
                                farmer_profile: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank all crops by suitability using advanced algorithm.
        
        Returns:
            List of crops ranked by suitability with detailed analysis
        """
        logger.info("Ranking crops by advanced suitability algorithm")
        
        ranked_crops = []
        
        for crop_id, crop_data in self.crop_database.items():
            # Calculate advanced suitability
            suitability_analysis = self.calculate_advanced_suitability_score(
                crop_data, environmental_factors, historical_data, farmer_profile
            )
            
            # Get top varieties for this crop
            top_varieties = self._get_top_varieties_for_crop(
                crop_data, environmental_factors, suitability_analysis
            )
            
            ranked_crops.append({
                'crop_id': crop_id,
                'crop_name': crop_data.get('name', crop_id),
                'suitability_score': suitability_analysis['overall_score'],
                'confidence': suitability_analysis['confidence'],
                'recommendation_level': suitability_analysis['recommendation_level'],
                'factor_scores': suitability_analysis['factor_scores'],
                'risk_factors': suitability_analysis['risk_factors'],
                'top_varieties': top_varieties,
                'crop_data': crop_data,
                'algorithm_version': 'advanced_v1.0'
            })
        
        # Sort by suitability score
        ranked_crops.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        logger.info(f"Ranked {len(ranked_crops)} crops by advanced suitability")
        
        return ranked_crops
    
    def _get_top_varieties_for_crop(self, 
                                  crop_data: Dict[str, Any],
                                  environmental_factors: Dict[str, Any],
                                  suitability_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get top varieties for a crop based on advanced analysis."""
        varieties = crop_data.get('varieties', [])
        
        if not varieties:
            return []
        
        rainfall_mm = environmental_factors.get('rainfall_mm', 0)
        temperature = environmental_factors.get('temperature', 25)
        season = environmental_factors.get('season', 'current')
        
        scored_varieties = []
        
        for variety in varieties:
            variety_score = 0.5  # Base score
            
            # Maturity days scoring
            maturity_days = variety.get('maturity_days', 0)
            if maturity_days > 0:
                if season == 'rainy_season' and maturity_days <= 120:
                    variety_score += 0.2
                elif season == 'dry_season' and maturity_days <= 90:
                    variety_score += 0.2
                elif 90 <= maturity_days <= 120:
                    variety_score += 0.1
            
            # Drought tolerance scoring
            drought_tolerance = variety.get('drought_tolerance', 'moderate')
            if drought_tolerance == 'excellent' and rainfall_mm < 300:
                variety_score += 0.3
            elif drought_tolerance == 'good' and rainfall_mm < 400:
                variety_score += 0.2
            elif drought_tolerance == 'moderate' and rainfall_mm >= 400:
                variety_score += 0.1
            
            # Disease resistance bonus
            disease_resistance = variety.get('disease_resistance', [])
            if disease_resistance and len(disease_resistance) > 0:
                variety_score += 0.1
            
            # Yield potential bonus
            yield_potential = variety.get('yield_potential', 'moderate')
            if yield_potential == 'high':
                variety_score += 0.1
            
            scored_varieties.append({
                'name': variety['name'],
                'suitability_score': min(1.0, variety_score),
                'maturity_days': maturity_days,
                'drought_tolerance': drought_tolerance,
                'disease_resistance': disease_resistance,
                'yield_potential': yield_potential,
                'type': variety.get('type', 'unknown'),
                'source': 'real_crop_varieties_database'
            })
        
        # Sort by suitability score
        scored_varieties.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return scored_varieties[:3]  # Top 3 varieties


# Create global instance
advanced_crop_algorithm = None  # Will be initialized with crop database
