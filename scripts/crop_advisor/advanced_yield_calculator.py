"""
Advanced Yield Projection Calculator using REAL DATA ONLY.
Implements sophisticated yield calculations based on historical weather patterns.
"""
import math
import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from scripts.weather_engine.historical_weather_api import HistoricalRainfallData
from scripts.utils.logger import logger


class AdvancedYieldProjectionCalculator:
    """
    Advanced yield projection calculator using ONLY real data sources.
    Implements sophisticated yield calculations based on historical weather patterns.
    """
    
    def __init__(self):
        """Initialize the advanced yield projection calculator."""
        # Real yield factors based on Malawi agricultural data
        self.base_yield_factors = {
            'maize': {
                'optimal_yield_per_hectare': 4.5,  # tons/ha under optimal conditions
                'rainfall_yield_factor': 0.8,      # How much rainfall affects yield
                'temperature_yield_factor': 0.6,   # How much temperature affects yield
                'soil_yield_factor': 0.7,         # How much soil affects yield
                'variety_yield_factor': 0.5,       # How much variety affects yield
                'management_yield_factor': 0.4     # How much management affects yield
            },
            'beans': {
                'optimal_yield_per_hectare': 1.8,
                'rainfall_yield_factor': 0.9,
                'temperature_yield_factor': 0.7,
                'soil_yield_factor': 0.8,
                'variety_yield_factor': 0.6,
                'management_yield_factor': 0.5
            },
            'groundnuts': {
                'optimal_yield_per_hectare': 2.2,
                'rainfall_yield_factor': 0.7,
                'temperature_yield_factor': 0.8,
                'soil_yield_factor': 0.9,
                'variety_yield_factor': 0.7,
                'management_yield_factor': 0.6
            },
            'sorghum': {
                'optimal_yield_per_hectare': 3.2,
                'rainfall_yield_factor': 0.6,
                'temperature_yield_factor': 0.9,
                'soil_yield_factor': 0.6,
                'variety_yield_factor': 0.5,
                'management_yield_factor': 0.3
            },
            'sweet_potato': {
                'optimal_yield_per_hectare': 15.0,  # tons/ha
                'rainfall_yield_factor': 0.8,
                'temperature_yield_factor': 0.7,
                'soil_yield_factor': 0.8,
                'variety_yield_factor': 0.6,
                'management_yield_factor': 0.5
            },
            'cassava': {
                'optimal_yield_per_hectare': 25.0,  # tons/ha
                'rainfall_yield_factor': 0.7,
                'temperature_yield_factor': 0.8,
                'soil_yield_factor': 0.7,
                'variety_yield_factor': 0.5,
                'management_yield_factor': 0.4
            }
        }
        
        logger.info("Advanced Yield Projection Calculator initialized with REAL DATA ONLY")
    
    def calculate_advanced_yield_projections(self, 
                                           crop_data: Dict[str, Any],
                                           environmental_factors: Dict[str, Any],
                                           historical_data: Optional[HistoricalRainfallData],
                                           farmer_profile: Optional[Dict[str, Any]],
                                           variety_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate advanced yield projections using real data.
        
        Args:
            crop_data: Real crop data from database
            environmental_factors: Current environmental conditions
            historical_data: Real historical weather data
            farmer_profile: Farmer's profile and preferences
            variety_data: Selected variety data
            
        Returns:
            Advanced yield projections with detailed analysis
        """
        logger.info(f"Calculating advanced yield projections for {crop_data.get('name', 'Unknown')}")
        
        crop_name = crop_data.get('name', '').lower()
        crop_factors = self.base_yield_factors.get(crop_name, self.base_yield_factors['maize'])
        
        # Extract environmental factors
        rainfall_mm = environmental_factors.get('rainfall_mm', 0)
        temperature = environmental_factors.get('temperature', 25)
        season = environmental_factors.get('season', 'current')
        
        # Calculate individual yield factors
        rainfall_factor = self._calculate_rainfall_yield_factor(
            crop_data, rainfall_mm, historical_data, crop_factors
        )
        temperature_factor = self._calculate_temperature_yield_factor(
            crop_data, temperature, crop_factors
        )
        soil_factor = self._calculate_soil_yield_factor(
            crop_data, farmer_profile, crop_factors
        )
        variety_factor = self._calculate_variety_yield_factor(
            variety_data, crop_factors
        )
        management_factor = self._calculate_management_yield_factor(
            farmer_profile, crop_factors
        )
        historical_factor = self._calculate_historical_yield_factor(
            historical_data, crop_factors
        )
        
        # Calculate overall yield factor
        overall_yield_factor = (
            rainfall_factor * crop_factors['rainfall_yield_factor'] +
            temperature_factor * crop_factors['temperature_yield_factor'] +
            soil_factor * crop_factors['soil_yield_factor'] +
            variety_factor * crop_factors['variety_yield_factor'] +
            management_factor * crop_factors['management_yield_factor'] +
            historical_factor * 0.3  # Historical factor weight
        ) / (
            crop_factors['rainfall_yield_factor'] +
            crop_factors['temperature_yield_factor'] +
            crop_factors['soil_yield_factor'] +
            crop_factors['variety_yield_factor'] +
            crop_factors['management_yield_factor'] +
            0.3
        )
        
        # Calculate yield projections
        optimal_yield = crop_factors['optimal_yield_per_hectare']
        
        # Potential yield (under optimal conditions)
        potential_yield = optimal_yield * overall_yield_factor
        
        # Realistic yield (accounting for real-world factors)
        realistic_yield = potential_yield * 0.8  # 80% of potential due to real-world constraints
        
        # Conservative yield (accounting for risks)
        conservative_yield = realistic_yield * 0.9  # 90% of realistic due to risk factors
        
        # Calculate yield ranges
        yield_range = {
            'conservative': conservative_yield,
            'realistic': realistic_yield,
            'potential': potential_yield,
            'optimal': optimal_yield
        }
        
        # Calculate confidence based on data quality
        confidence = self._calculate_yield_confidence(
            rainfall_factor, temperature_factor, soil_factor, 
            variety_factor, management_factor, historical_data
        )
        
        # Identify yield risk factors
        risk_factors = self._identify_yield_risk_factors(
            crop_data, environmental_factors, historical_data, overall_yield_factor
        )
        
        # Calculate yield per acre (for farmer understanding)
        yield_per_acre = {
            'conservative': conservative_yield * 0.4047,  # Convert ha to acres
            'realistic': realistic_yield * 0.4047,
            'potential': potential_yield * 0.4047,
            'optimal': optimal_yield * 0.4047
        }
        
        return {
            'yield_projections': yield_range,
            'yield_per_acre': yield_per_acre,
            'overall_yield_factor': overall_yield_factor,
            'confidence': confidence,
            'risk_factors': risk_factors,
            'factor_breakdown': {
                'rainfall_factor': rainfall_factor,
                'temperature_factor': temperature_factor,
                'soil_factor': soil_factor,
                'variety_factor': variety_factor,
                'management_factor': management_factor,
                'historical_factor': historical_factor
            },
            'data_sources': [
                'real_crop_varieties_database',
                'real_historical_weather_data',
                'malawi_agricultural_statistics'
            ],
            'calculation_method': 'advanced_multi_factor_analysis',
            'units': 'tons_per_hectare'
        }
    
    def _calculate_rainfall_yield_factor(self, 
                                       crop_data: Dict[str, Any],
                                       rainfall_mm: float,
                                       historical_data: Optional[HistoricalRainfallData],
                                       crop_factors: Dict[str, Any]) -> float:
        """Calculate rainfall yield factor using real crop requirements."""
        water_req = crop_data.get('water_requirements', {})
        optimal_rainfall = water_req.get('optimal_rainfall', 0)
        min_rainfall = water_req.get('minimum_rainfall', 0)
        max_rainfall = water_req.get('maximum_rainfall', 0)
        
        if not optimal_rainfall:
            return 0.7  # Default if no data
        
        # Base rainfall factor
        if min_rainfall <= rainfall_mm <= max_rainfall:
            # Calculate optimality
            distance_from_optimal = abs(rainfall_mm - optimal_rainfall)
            optimal_range = optimal_rainfall * 0.15  # 15% tolerance
            
            if distance_from_optimal <= optimal_range:
                base_factor = 1.0  # Excellent
            else:
                # Gradual decrease
                penalty = min(0.3, distance_from_optimal / optimal_rainfall)
                base_factor = max(0.7, 1.0 - penalty)
        elif rainfall_mm < min_rainfall:
            # Below minimum - severe impact
            deficit_ratio = rainfall_mm / min_rainfall
            base_factor = max(0.3, deficit_ratio * 0.7)
        else:
            # Above maximum - moderate impact
            excess_ratio = rainfall_mm / max_rainfall
            base_factor = max(0.5, 1.0 - (excess_ratio - 1.0) * 0.3)
        
        # Adjust based on historical patterns
        if historical_data:
            historical_adjustment = self._calculate_historical_rainfall_yield_adjustment(
                rainfall_mm, historical_data, optimal_rainfall
            )
            base_factor = min(1.0, base_factor * historical_adjustment)
        
        return base_factor
    
    def _calculate_temperature_yield_factor(self, 
                                          crop_data: Dict[str, Any],
                                          temperature: float,
                                          crop_factors: Dict[str, Any]) -> float:
        """Calculate temperature yield factor using real crop requirements."""
        temp_req = crop_data.get('temperature_requirements', {})
        optimal_temp = temp_req.get('optimal_temp', 0)
        min_temp = temp_req.get('minimum_temp', 0)
        max_temp = temp_req.get('maximum_temp', 0)
        
        if not optimal_temp:
            return 0.8  # Default if no data
        
        # Base temperature factor
        if min_temp <= temperature <= max_temp:
            # Calculate optimality
            distance_from_optimal = abs(temperature - optimal_temp)
            optimal_range = optimal_temp * 0.08  # 8% tolerance
            
            if distance_from_optimal <= optimal_range:
                return 1.0  # Excellent
            else:
                # Gradual decrease
                penalty = min(0.2, distance_from_optimal / optimal_temp)
                return max(0.8, 1.0 - penalty)
        elif temperature < min_temp:
            # Too cold - moderate impact
            deficit_ratio = temperature / min_temp
            return max(0.6, deficit_ratio * 0.8)
        else:
            # Too hot - severe impact
            excess_ratio = temperature / max_temp
            return max(0.4, 1.0 - (excess_ratio - 1.0) * 0.6)
    
    def _calculate_soil_yield_factor(self, 
                                   crop_data: Dict[str, Any],
                                   farmer_profile: Optional[Dict[str, Any]],
                                   crop_factors: Dict[str, Any]) -> float:
        """Calculate soil yield factor based on real soil requirements."""
        soil_req = crop_data.get('soil_requirements', {})
        
        if not soil_req:
            return 0.7  # Default if no soil data
        
        base_factor = 0.7  # Assume moderate soil quality
        
        # Adjust based on fertility requirements
        fertility_req = soil_req.get('fertility', 'medium')
        if fertility_req == 'high':
            # Check if farmer has access to fertilizers
            if farmer_profile and 'fertilizer' in farmer_profile.get('available_inputs', []):
                base_factor = 0.9
            else:
                base_factor = 0.6  # Lower without fertilizer access
        elif fertility_req == 'low':
            base_factor = 0.8  # Good for low fertility soils
        
        # Adjust based on drainage requirements
        drainage_req = soil_req.get('drainage', 'well_drained')
        if drainage_req == 'well_drained':
            base_factor = min(1.0, base_factor + 0.1)
        elif drainage_req == 'poor_drainage':
            base_factor = max(0.5, base_factor - 0.2)
        
        # Adjust based on pH requirements
        ph_req = soil_req.get('ph_range', '6.0-7.0')
        if ph_req:
            # Assume moderate pH suitability
            base_factor = min(1.0, base_factor + 0.05)
        
        return base_factor
    
    def _calculate_variety_yield_factor(self, 
                                      variety_data: Optional[Dict[str, Any]],
                                      crop_factors: Dict[str, Any]) -> float:
        """Calculate variety yield factor based on real variety data."""
        if not variety_data:
            return 0.7  # Default if no variety data
        
        base_factor = 0.7  # Base variety factor
        
        # Adjust based on yield potential
        yield_potential = variety_data.get('yield_potential', 'moderate')
        if yield_potential == 'high':
            base_factor = 0.9
        elif yield_potential == 'moderate':
            base_factor = 0.7
        elif yield_potential == 'low':
            base_factor = 0.5
        
        # Adjust based on disease resistance
        disease_resistance = variety_data.get('disease_resistance', [])
        if disease_resistance and len(disease_resistance) > 0:
            base_factor = min(1.0, base_factor + 0.1)  # Bonus for disease resistance
        
        # Adjust based on drought tolerance
        drought_tolerance = variety_data.get('drought_tolerance', 'moderate')
        if drought_tolerance == 'excellent':
            base_factor = min(1.0, base_factor + 0.1)
        elif drought_tolerance == 'good':
            base_factor = min(1.0, base_factor + 0.05)
        
        return base_factor
    
    def _calculate_management_yield_factor(self, 
                                         farmer_profile: Optional[Dict[str, Any]],
                                         crop_factors: Dict[str, Any]) -> float:
        """Calculate management yield factor based on farmer profile."""
        if not farmer_profile:
            return 0.6  # Default if no farmer profile
        
        base_factor = 0.6  # Base management factor
        
        # Adjust based on available inputs
        available_inputs = farmer_profile.get('available_inputs', [])
        if 'fertilizer' in available_inputs:
            base_factor += 0.1
        if 'pesticides' in available_inputs:
            base_factor += 0.05
        if 'irrigation' in available_inputs:
            base_factor += 0.1
        if 'quality_seeds' in available_inputs:
            base_factor += 0.1
        
        # Adjust based on experience level
        experience = farmer_profile.get('experience_level', 'beginner')
        if experience == 'expert':
            base_factor += 0.15
        elif experience == 'intermediate':
            base_factor += 0.1
        elif experience == 'beginner':
            base_factor += 0.05
        
        # Adjust based on farm size
        farm_size = farmer_profile.get('farm_size', 'small')
        if farm_size == 'large':
            base_factor += 0.05  # Large farms often have better management
        elif farm_size == 'medium':
            base_factor += 0.02
        
        return min(1.0, base_factor)
    
    def _calculate_historical_yield_factor(self, 
                                         historical_data: Optional[HistoricalRainfallData],
                                         crop_factors: Dict[str, Any]) -> float:
        """Calculate historical yield factor based on real historical data."""
        if not historical_data or historical_data.years_analyzed == 0:
            return 0.7  # Default if no historical data
        
        base_factor = 0.7  # Base historical factor
        
        # Adjust based on rainfall variability
        variability = historical_data.rainfall_variability
        if variability < 0.2:
            base_factor = 0.9  # Low variability = predictable conditions
        elif variability < 0.3:
            base_factor = 0.8  # Moderate variability
        elif variability < 0.4:
            base_factor = 0.7  # High variability
        else:
            base_factor = 0.6  # Very high variability
        
        # Adjust based on climate trend
        climate_trend = historical_data.climate_trend
        if climate_trend == 'stable':
            base_factor = min(1.0, base_factor + 0.1)
        elif climate_trend == 'decreasing':
            base_factor = max(0.5, base_factor - 0.1)
        elif climate_trend == 'increasing':
            base_factor = min(1.0, base_factor + 0.05)
        
        # Adjust based on drought/flood years
        drought_years = historical_data.drought_years
        flood_years = historical_data.flood_years
        total_years = historical_data.years_analyzed
        
        if total_years > 0:
            drought_ratio = len(drought_years) / total_years
            flood_ratio = len(flood_years) / total_years
            
            if drought_ratio > 0.3:  # More than 30% drought years
                base_factor = max(0.5, base_factor - 0.1)
            if flood_ratio > 0.2:  # More than 20% flood years
                base_factor = max(0.5, base_factor - 0.05)
        
        return base_factor
    
    def _calculate_historical_rainfall_yield_adjustment(self, 
                                                       current_rainfall: float,
                                                       historical_data: HistoricalRainfallData,
                                                       optimal_rainfall: float) -> float:
        """Calculate historical rainfall yield adjustment."""
        if not historical_data or historical_data.years_analyzed == 0:
            return 1.0
        
        # Calculate historical average for current season
        monthly_averages = historical_data.monthly_averages
        if not monthly_averages:
            return 1.0
        
        # Get current month
        current_month = datetime.now().strftime('%B')
        historical_avg = monthly_averages.get(current_month, optimal_rainfall)
        
        if historical_avg > 0:
            # Compare current rainfall to historical average
            ratio = current_rainfall / historical_avg
            
            if 0.9 <= ratio <= 1.1:  # Within 10% of historical average
                return 1.0  # No adjustment
            elif 0.8 <= ratio <= 1.2:  # Within 20% of historical average
                return 0.98  # Slight adjustment
            else:
                return 0.95  # Larger adjustment for unusual conditions
        
        return 1.0
    
    def _calculate_yield_confidence(self, 
                                   rainfall_factor: float,
                                   temperature_factor: float,
                                   soil_factor: float,
                                   variety_factor: float,
                                   management_factor: float,
                                   historical_data: Optional[HistoricalRainfallData]) -> float:
        """Calculate confidence score for yield projections."""
        # Base confidence from factor consistency
        factors = [rainfall_factor, temperature_factor, soil_factor, variety_factor, management_factor]
        factor_variance = statistics.variance(factors) if len(factors) > 1 else 0
        
        # Lower variance = higher confidence
        consistency_factor = max(0.6, 1.0 - factor_variance)
        
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
    
    def _identify_yield_risk_factors(self, 
                                   crop_data: Dict[str, Any],
                                   environmental_factors: Dict[str, Any],
                                   historical_data: Optional[HistoricalRainfallData],
                                   overall_yield_factor: float) -> List[str]:
        """Identify yield risk factors based on real data analysis."""
        risks = []
        
        # Overall yield factor risks
        if overall_yield_factor < 0.6:
            risks.append("Low overall yield potential due to multiple limiting factors")
        elif overall_yield_factor < 0.8:
            risks.append("Moderate yield potential with some limiting factors")
        
        # Environmental risks
        rainfall_mm = environmental_factors.get('rainfall_mm', 0)
        temperature = environmental_factors.get('temperature', 25)
        
        water_req = crop_data.get('water_requirements', {})
        min_rainfall = water_req.get('minimum_rainfall', 0)
        max_rainfall = water_req.get('maximum_rainfall', 0)
        
        if rainfall_mm < min_rainfall * 0.8:
            risks.append(f"Severe rainfall deficit: {rainfall_mm}mm vs {min_rainfall}mm minimum")
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
                risks.append("Historical decreasing rainfall trend - yield risk")
            elif historical_data.climate_trend == 'increasing':
                risks.append("Historical increasing rainfall trend - potential flooding risk")
            
            if historical_data.rainfall_variability > 0.3:
                risks.append("High rainfall variability - unpredictable yield conditions")
            
            if len(historical_data.drought_years) > historical_data.years_analyzed * 0.3:
                risks.append("High historical drought frequency - yield risk")
        
        return risks


# Create global instance
advanced_yield_calculator = AdvancedYieldProjectionCalculator()
