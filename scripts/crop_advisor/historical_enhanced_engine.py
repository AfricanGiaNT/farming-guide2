"""
Historical-Enhanced Crop Recommendation Engine.
Integrates historical rainfall data and climate trends for improved crop recommendations.
"""
import datetime
from typing import Dict, List, Any, Optional, Tuple
from scripts.crop_advisor.crop_database import crop_database
from scripts.crop_advisor.recommendation_engine import CropRecommendationEngine
from scripts.weather_engine.historical_weather_api import HistoricalWeatherAPI, HistoricalRainfallData
from scripts.utils.logger import logger


class HistoricalEnhancedEngine(CropRecommendationEngine):
    """Enhanced recommendation engine with historical data integration."""
    
    def __init__(self):
        """Initialize the historical-enhanced engine."""
        super().__init__()
        self.historical_api = HistoricalWeatherAPI()
        self.current_month = datetime.datetime.now().strftime('%B')
        
    def generate_historical_enhanced_recommendations(self, 
                                                   rainfall_data: Dict[str, Any], 
                                                   weather_data: Dict[str, Any],
                                                   lat: float, 
                                                   lon: float,
                                                   user_preferences: Optional[Dict[str, Any]] = None,
                                                   historical_years: int = 5) -> Dict[str, Any]:
        """
        Generate crop recommendations enhanced with historical data analysis.
        
        Args:
            rainfall_data: Current rainfall analysis data
            weather_data: Current weather data
            lat: Latitude
            lon: Longitude
            user_preferences: Optional user preferences
            historical_years: Number of years of historical data to analyze
            
        Returns:
            Historical-enhanced recommendation results
        """
        logger.info(f"Generating historical-enhanced recommendations for {lat}, {lon} with {historical_years} years of data")
        
        # Get historical rainfall data
        historical_data = self.historical_api.get_historical_rainfall(
            lat, lon, historical_years
        )
        
        if not historical_data:
            logger.warning("Historical data unavailable, falling back to basic recommendations")
            return super().generate_recommendations(rainfall_data, weather_data, lat, lon, user_preferences)
        
        # Extract current environmental data
        total_rainfall = rainfall_data.get('total_7day_rainfall', 0)
        forecast_rainfall = rainfall_data.get('forecast_7day_rainfall', 0)
        current_temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 50)
        rainy_days = rainfall_data.get('rainy_days_forecast', 0)
        
        # Calculate historical-enhanced seasonal rainfall estimate
        seasonal_rainfall = self._estimate_historical_seasonal_rainfall(
            total_rainfall, forecast_rainfall, historical_data, self.current_month
        )
        
        # Get current season
        current_season = self.crop_db.get_current_season(self.current_month)
        
        # Generate historical-enhanced recommendations for each crop
        crop_scores = []
        all_crops = self.crop_db.get_all_crops()
        
        for crop_id, crop_data in all_crops.items():
            score_data = self._calculate_historical_crop_score(
                crop_id, crop_data, seasonal_rainfall, current_temp, 
                humidity, rainy_days, current_season, historical_data
            )
            crop_scores.append(score_data)
        
        # Sort by total score
        crop_scores.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Generate variety recommendations for top crops
        top_crops_with_varieties = self._add_historical_variety_recommendations(
            crop_scores[:5], seasonal_rainfall, current_temp, historical_data
        )
        
        # Generate historical-enhanced planting calendar
        planting_recommendations = self._generate_historical_planting_calendar(
            crop_scores[:3], self.current_month, historical_data
        )
        
        # Generate historical-enhanced seasonal advice
        seasonal_advice = self._generate_historical_seasonal_advice(
            current_season, seasonal_rainfall, current_temp, historical_data
        )
        
        # Generate climate trend analysis
        climate_analysis = self._analyze_climate_trends(historical_data)
        
        return {
            'recommendations': top_crops_with_varieties,
            'planting_calendar': planting_recommendations,
            'seasonal_advice': seasonal_advice,
            'climate_analysis': climate_analysis,
            'historical_summary': {
                'years_analyzed': historical_data.years_analyzed,
                'rainfall_variability': historical_data.rainfall_variability,
                'climate_trend': historical_data.climate_trend,
                'drought_frequency': len(historical_data.drought_years),
                'flood_frequency': len(historical_data.flood_years),
                'monthly_averages': historical_data.monthly_averages,
                'current_month_historical_avg': historical_data.monthly_averages.get(self.current_month, 0)
            },
            'environmental_summary': {
                'total_7day_rainfall': total_rainfall,
                'forecast_7day_rainfall': forecast_rainfall,
                'estimated_seasonal_rainfall': seasonal_rainfall,
                'current_temperature': current_temp,
                'humidity': humidity,
                'rainy_days_forecast': rainy_days,
                'current_season': current_season,
                'current_month': self.current_month
            },
            'analysis_timestamp': datetime.datetime.now().isoformat()
        }
    
    def generate_historical_enhanced_rainy_season_recommendations(self, 
                                                                rainfall_data: Dict[str, Any], 
                                                                weather_data: Dict[str, Any],
                                                                lat: float, 
                                                                lon: float,
                                                                historical_years: int = 5) -> Dict[str, Any]:
        """
        Generate historical-enhanced rainy season recommendations.
        
        Args:
            rainfall_data: Current rainfall analysis data
            weather_data: Current weather data
            lat: Latitude
            lon: Longitude
            historical_years: Number of years of historical data to analyze
            
        Returns:
            Historical-enhanced rainy season recommendations
        """
        logger.info(f"Generating historical-enhanced rainy season recommendations for {lat}, {lon} with {historical_years} years of data")
        
        # Get historical rainfall data
        historical_data = self.historical_api.get_historical_rainfall(
            lat, lon, historical_years
        )
        
        if not historical_data:
            logger.warning("Historical data unavailable, falling back to basic rainy season recommendations")
            return super().generate_rainy_season_recommendations(rainfall_data, weather_data, lat, lon)
        
        # Calculate historical rainy season rainfall
        rainy_season_rainfall = self._estimate_historical_rainy_season_rainfall(historical_data)
        
        # Use optimal rainy season conditions with historical adjustments
        rainy_temp = 25  # Optimal rainy season temperature
        rainy_humidity = 70  # High humidity during rainy season
        rainy_days = 15  # Typical rainy days per month
        
        # Generate historical-enhanced recommendations for each crop
        crop_scores = []
        all_crops = self.crop_db.get_all_crops()
        
        for crop_id, crop_data in all_crops.items():
            score_data = self._calculate_historical_rainy_season_score(
                crop_id, crop_data, rainy_season_rainfall, rainy_temp, 
                rainy_humidity, rainy_days, historical_data
            )
            crop_scores.append(score_data)
        
        # Sort by total score
        crop_scores.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Generate variety recommendations for top crops
        top_crops_with_varieties = self._add_historical_variety_recommendations(
            crop_scores[:5], rainy_season_rainfall, rainy_temp, historical_data
        )
        
        # Generate historical-enhanced seasonal advice
        seasonal_advice = self._generate_historical_rainy_season_advice(
            rainy_season_rainfall, rainy_temp, historical_data
        )
        
        # Generate climate trend analysis
        climate_analysis = self._analyze_climate_trends(historical_data)
        
        return {
            'recommendations': top_crops_with_varieties,
            'seasonal_advice': seasonal_advice,
            'climate_analysis': climate_analysis,
            'historical_summary': {
                'years_analyzed': historical_data.years_analyzed,
                'rainfall_variability': historical_data.rainfall_variability,
                'climate_trend': historical_data.climate_trend,
                'drought_frequency': len(historical_data.drought_years),
                'flood_frequency': len(historical_data.flood_years),
                'rainy_season_historical_avg': rainy_season_rainfall,
                'rainy_season_months': ['November', 'December', 'January', 'February', 'March', 'April']
            },
            'environmental_summary': {
                'estimated_rainy_season_rainfall': rainy_season_rainfall,
                'rainy_season_temperature': rainy_temp,
                'rainy_season_humidity': rainy_humidity,
                'rainy_days_per_month': rainy_days,
                'season': 'rainy_season'
            },
            'analysis_timestamp': datetime.datetime.now().isoformat()
        }
    
    def generate_historical_enhanced_dry_season_recommendations(self, 
                                                              rainfall_data: Dict[str, Any], 
                                                              weather_data: Dict[str, Any],
                                                              lat: float, 
                                                              lon: float,
                                                              historical_years: int = 5) -> Dict[str, Any]:
        """
        Generate historical-enhanced dry season recommendations.
        
        Args:
            rainfall_data: Current rainfall analysis data
            weather_data: Current weather data
            lat: Latitude
            lon: Longitude
            historical_years: Number of years of historical data to analyze
            
        Returns:
            Historical-enhanced dry season recommendations
        """
        logger.info(f"Generating historical-enhanced dry season recommendations for {lat}, {lon} with {historical_years} years of data")
        
        # Get historical rainfall data
        historical_data = self.historical_api.get_historical_rainfall(
            lat, lon, historical_years
        )
        
        if not historical_data:
            logger.warning("Historical data unavailable, falling back to basic dry season recommendations")
            return super().generate_dry_season_recommendations(rainfall_data, weather_data, lat, lon)
        
        # Calculate historical dry season rainfall
        dry_season_rainfall = self._estimate_historical_dry_season_rainfall(historical_data)
        
        # Use typical dry season conditions with historical adjustments
        dry_temp = 22  # Typical dry season temperature
        dry_humidity = 40  # Low humidity during dry season
        dry_days = 3  # Few rainy days per month
        
        # Generate historical-enhanced recommendations for each crop
        crop_scores = []
        all_crops = self.crop_db.get_all_crops()
        
        for crop_id, crop_data in all_crops.items():
            score_data = self._calculate_historical_dry_season_score(
                crop_id, crop_data, dry_season_rainfall, dry_temp, 
                dry_humidity, dry_days, historical_data
            )
            crop_scores.append(score_data)
        
        # Sort by total score
        crop_scores.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Generate variety recommendations for top crops
        top_crops_with_varieties = self._add_historical_variety_recommendations(
            crop_scores[:5], dry_season_rainfall, dry_temp, historical_data
        )
        
        # Generate historical-enhanced seasonal advice
        seasonal_advice = self._generate_historical_dry_season_advice(
            dry_season_rainfall, dry_temp, historical_data
        )
        
        # Generate climate trend analysis
        climate_analysis = self._analyze_climate_trends(historical_data)
        
        return {
            'recommendations': top_crops_with_varieties,
            'seasonal_advice': seasonal_advice,
            'climate_analysis': climate_analysis,
            'historical_summary': {
                'years_analyzed': historical_data.years_analyzed,
                'rainfall_variability': historical_data.rainfall_variability,
                'climate_trend': historical_data.climate_trend,
                'drought_frequency': len(historical_data.drought_years),
                'flood_frequency': len(historical_data.flood_years),
                'dry_season_historical_avg': dry_season_rainfall,
                'dry_season_months': ['May', 'June', 'July', 'August', 'September', 'October']
            },
            'environmental_summary': {
                'estimated_dry_season_rainfall': dry_season_rainfall,
                'dry_season_temperature': dry_temp,
                'dry_season_humidity': dry_humidity,
                'rainy_days_per_month': dry_days,
                'season': 'dry_season'
            },
            'analysis_timestamp': datetime.datetime.now().isoformat()
        }
    
    def generate_historical_enhanced_all_seasons_comparison(self, 
                                                           rainfall_data: Dict[str, Any], 
                                                           weather_data: Dict[str, Any],
                                                           lat: float, 
                                                           lon: float,
                                                           historical_years: int = 5) -> Dict[str, Any]:
        """
        Generate historical-enhanced all seasons comparison.
        
        Args:
            rainfall_data: Current rainfall analysis data
            weather_data: Current weather data
            lat: Latitude
            lon: Longitude
            historical_years: Number of years of historical data to analyze
            
        Returns:
            Historical-enhanced all seasons comparison
        """
        logger.info(f"Generating historical-enhanced all seasons comparison for {lat}, {lon} with {historical_years} years of data")
        
        # Get historical rainfall data
        historical_data = self.historical_api.get_historical_rainfall(
            lat, lon, historical_years
        )
        
        if not historical_data:
            logger.warning("Historical data unavailable, falling back to basic all seasons comparison")
            return super().generate_all_seasons_comparison(rainfall_data, weather_data, lat, lon)
        
        # Calculate historical rainfall for each season
        rainy_season_rainfall = self._estimate_historical_rainy_season_rainfall(historical_data)
        dry_season_rainfall = self._estimate_historical_dry_season_rainfall(historical_data)
        
        # Generate recommendations for each season
        rainy_recommendations = self.generate_historical_enhanced_rainy_season_recommendations(
            rainfall_data, weather_data, lat, lon, historical_years
        )
        
        dry_recommendations = self.generate_historical_enhanced_dry_season_recommendations(
            rainfall_data, weather_data, lat, lon, historical_years
        )
        
        # Find crops that perform well across seasons
        year_round_crops = self._identify_year_round_crops(
            rainy_recommendations['recommendations'],
            dry_recommendations['recommendations'],
            historical_data
        )
        
        # Generate comprehensive seasonal advice
        seasonal_advice = self._generate_historical_all_seasons_advice(
            rainy_season_rainfall, dry_season_rainfall, historical_data
        )
        
        # Generate climate trend analysis
        climate_analysis = self._analyze_climate_trends(historical_data)
        
        return {
            'rainy_season': rainy_recommendations,
            'dry_season': dry_recommendations,
            'year_round_crops': year_round_crops,
            'seasonal_advice': seasonal_advice,
            'climate_analysis': climate_analysis,
            'historical_summary': {
                'years_analyzed': historical_data.years_analyzed,
                'rainfall_variability': historical_data.rainfall_variability,
                'climate_trend': historical_data.climate_trend,
                'drought_frequency': len(historical_data.drought_years),
                'flood_frequency': len(historical_data.flood_years),
                'rainy_season_historical_avg': rainy_season_rainfall,
                'dry_season_historical_avg': dry_season_rainfall
            },
            'environmental_summary': {
                'rainy_season_rainfall': rainy_season_rainfall,
                'dry_season_rainfall': dry_season_rainfall,
                'season_comparison': 'all_seasons'
            },
            'analysis_timestamp': datetime.datetime.now().isoformat()
        }
    
    def _estimate_historical_seasonal_rainfall(self, 
                                             recent_rainfall: float, 
                                             forecast_rainfall: float,
                                             historical_data: HistoricalRainfallData,
                                             current_month: str) -> float:
        """
        Estimate seasonal rainfall using historical data and current conditions.
        
        Args:
            recent_rainfall: Recent 7-day rainfall
            forecast_rainfall: Forecasted 7-day rainfall
            historical_data: Historical rainfall analysis
            current_month: Current month
            
        Returns:
            Estimated seasonal rainfall in mm
        """
        # Get historical average for current month
        historical_monthly_avg = historical_data.monthly_averages.get(current_month, 0)
        
        # Calculate trend adjustment
        trend_adjustment = self._calculate_trend_adjustment(historical_data)
        
        # Weight current conditions vs historical average
        current_weight = 0.3  # 30% weight to current conditions
        historical_weight = 0.7  # 70% weight to historical average
        
        # Estimate based on current conditions and historical patterns
        current_estimate = (recent_rainfall + forecast_rainfall) * 4  # Rough monthly estimate
        historical_estimate = historical_monthly_avg * (1 + trend_adjustment)
        
        # Combine estimates
        seasonal_estimate = (current_estimate * current_weight + 
                           historical_estimate * historical_weight)
        
        # Apply variability adjustment
        variability_factor = 1 + (historical_data.rainfall_variability - 0.5) * 0.2
        seasonal_estimate *= variability_factor
        
        return max(0, seasonal_estimate)
    
    def _estimate_historical_rainy_season_rainfall(self, historical_data: HistoricalRainfallData) -> float:
        """
        Estimate historical rainy season rainfall.
        
        Args:
            historical_data: Historical rainfall analysis
            
        Returns:
            Estimated rainy season rainfall in mm
        """
        rainy_months = ['November', 'December', 'January', 'February', 'March', 'April']
        rainy_rainfall = sum(historical_data.monthly_averages.get(month, 0) for month in rainy_months)
        
        # Apply variability adjustment
        variability_factor = 1 + (historical_data.rainfall_variability - 0.5) * 0.2
        rainy_rainfall *= variability_factor
        
        return max(0, rainy_rainfall)
    
    def _estimate_historical_dry_season_rainfall(self, historical_data: HistoricalRainfallData) -> float:
        """
        Estimate historical dry season rainfall.
        
        Args:
            historical_data: Historical rainfall analysis
            
        Returns:
            Estimated dry season rainfall in mm
        """
        dry_months = ['May', 'June', 'July', 'August', 'September', 'October']
        dry_rainfall = sum(historical_data.monthly_averages.get(month, 0) for month in dry_months)
        
        # Apply variability adjustment
        variability_factor = 1 + (historical_data.rainfall_variability - 0.5) * 0.2
        dry_rainfall *= variability_factor
        
        return max(0, dry_rainfall)
    
    def _calculate_trend_adjustment(self, historical_data: HistoricalRainfallData) -> float:
        """
        Calculate trend adjustment based on climate trends.
        
        Args:
            historical_data: Historical rainfall analysis
            
        Returns:
            Trend adjustment factor (-0.2 to 0.2)
        """
        if historical_data.climate_trend == 'increasing':
            return 0.1  # 10% increase
        elif historical_data.climate_trend == 'decreasing':
            return -0.1  # 10% decrease
        else:
            return 0.0  # Stable
    
    def _calculate_historical_crop_score(self, 
                                       crop_id: str, 
                                       crop_data: Dict[str, Any], 
                                       seasonal_rainfall: float,
                                       current_temp: float,
                                       humidity: float,
                                       rainy_days: int,
                                       current_season: str,
                                       historical_data: HistoricalRainfallData) -> Dict[str, Any]:
        """
        Calculate crop score with historical data integration.
        
        Args:
            crop_id: Crop identifier
            crop_data: Crop data from database
            seasonal_rainfall: Estimated seasonal rainfall
            current_temp: Current temperature
            humidity: Current humidity
            rainy_days: Number of rainy days forecast
            current_season: Current season
            historical_data: Historical rainfall analysis
            
        Returns:
            Enhanced crop score data
        """
        # Get base score from parent class
        base_score_data = self._calculate_crop_score(
            crop_id, crop_data, seasonal_rainfall, current_temp, 
            humidity, rainy_days, current_season
        )
        
        # Calculate historical enhancement factors
        historical_factors = self._calculate_historical_factors(
            crop_data, historical_data, current_season
        )
        
        # Apply historical adjustments
        adjusted_score = base_score_data['total_score'] * historical_factors['reliability_multiplier']
        
        # Add historical risk assessment
        risk_score = self._calculate_historical_risk_score(
            crop_data, historical_data, current_season
        )
        
        # Combine scores
        final_score = adjusted_score * (1 - risk_score * 0.3)  # Risk reduces score by up to 30%
        
        # Update score data
        enhanced_score_data = base_score_data.copy()
        enhanced_score_data.update({
            'total_score': final_score,
            'historical_factors': historical_factors,
            'risk_score': risk_score,
            'reliability_score': historical_factors['reliability_score'],
            'trend_adjustment': historical_factors['trend_adjustment']
        })
        
        return enhanced_score_data
    
    def _calculate_historical_rainy_season_score(self, 
                                                crop_id: str, 
                                                crop_data: Dict[str, Any], 
                                                rainy_season_rainfall: float,
                                                rainy_temp: float,
                                                rainy_humidity: float,
                                                rainy_days: int,
                                                historical_data: HistoricalRainfallData) -> Dict[str, Any]:
        """
        Calculate historical-enhanced score for rainy season.
        
        Args:
            crop_id: Crop identifier
            crop_data: Crop data
            rainy_season_rainfall: Estimated rainy season rainfall
            rainy_temp: Estimated rainy season temperature
            rainy_humidity: Estimated rainy season humidity
            rainy_days: Estimated rainy days per month
            historical_data: Historical rainfall analysis
            
        Returns:
            Enhanced score data for rainy season
        """
        # Get base score from parent class
        base_score_data = self._calculate_crop_score(
            crop_id, crop_data, rainy_season_rainfall, rainy_temp, 
            rainy_humidity, rainy_days, 'rainy_season'
        )
        
        # Calculate historical enhancement factors
        historical_factors = self._calculate_historical_factors(
            crop_data, historical_data, 'rainy_season'
        )
        
        # Apply historical adjustments
        adjusted_score = base_score_data['total_score'] * historical_factors['reliability_multiplier']
        
        # Add historical risk assessment
        risk_score = self._calculate_historical_risk_score(
            crop_data, historical_data, 'rainy_season'
        )
        
        # Combine scores
        final_score = adjusted_score * (1 - risk_score * 0.3)  # Risk reduces score by up to 30%
        
        # Update score data
        enhanced_score_data = base_score_data.copy()
        enhanced_score_data.update({
            'total_score': final_score,
            'historical_factors': historical_factors,
            'risk_score': risk_score,
            'reliability_score': historical_factors['reliability_score'],
            'trend_adjustment': historical_factors['trend_adjustment']
        })
        
        return enhanced_score_data
    
    def _calculate_historical_dry_season_score(self, 
                                              crop_id: str, 
                                              crop_data: Dict[str, Any], 
                                              dry_season_rainfall: float,
                                              dry_temp: float,
                                              dry_humidity: float,
                                              dry_days: int,
                                              historical_data: HistoricalRainfallData) -> Dict[str, Any]:
        """
        Calculate historical-enhanced score for dry season.
        
        Args:
            crop_id: Crop identifier
            crop_data: Crop data
            dry_season_rainfall: Estimated dry season rainfall
            dry_temp: Estimated dry season temperature
            dry_humidity: Estimated dry season humidity
            dry_days: Estimated rainy days per month
            historical_data: Historical rainfall analysis
            
        Returns:
            Enhanced score data for dry season
        """
        # Get base score from parent class
        base_score_data = self._calculate_crop_score(
            crop_id, crop_data, dry_season_rainfall, dry_temp, 
            dry_humidity, dry_days, 'dry_season'
        )
        
        # Calculate historical enhancement factors
        historical_factors = self._calculate_historical_factors(
            crop_data, historical_data, 'dry_season'
        )
        
        # Apply historical adjustments
        adjusted_score = base_score_data['total_score'] * historical_factors['reliability_multiplier']
        
        # Add historical risk assessment
        risk_score = self._calculate_historical_risk_score(
            crop_data, historical_data, 'dry_season'
        )
        
        # Combine scores
        final_score = adjusted_score * (1 - risk_score * 0.3)  # Risk reduces score by up to 30%
        
        # Update score data
        enhanced_score_data = base_score_data.copy()
        enhanced_score_data.update({
            'total_score': final_score,
            'historical_factors': historical_factors,
            'risk_score': risk_score,
            'reliability_score': historical_factors['reliability_score'],
            'trend_adjustment': historical_factors['trend_adjustment']
        })
        
        return enhanced_score_data
    
    def _calculate_historical_factors(self, 
                                    crop_data: Dict[str, Any],
                                    historical_data: HistoricalRainfallData,
                                    current_season: str) -> Dict[str, float]:
        """
        Calculate historical factors affecting crop suitability.
        
        Args:
            crop_data: Crop data
            historical_data: Historical rainfall analysis
            current_season: Current season
            
        Returns:
            Historical factors dictionary
        """
        # Calculate rainfall reliability for crop's growing season
        growing_months = crop_data.get('growing_months', [])
        if not growing_months:
            growing_months = self._get_default_growing_months(current_season)
        
        # Calculate reliability based on historical variability
        reliability_score = self._calculate_rainfall_reliability(
            growing_months, historical_data
        )
        
        # Calculate trend adjustment
        trend_adjustment = self._calculate_trend_adjustment(historical_data)
        
        # Calculate drought risk
        drought_risk = len(historical_data.drought_years) / historical_data.years_analyzed
        
        # Calculate flood risk
        flood_risk = len(historical_data.flood_years) / historical_data.years_analyzed
        
        # Determine reliability multiplier
        reliability_multiplier = 0.8 + (reliability_score * 0.4)  # 0.8 to 1.2 range
        
        return {
            'reliability_score': reliability_score,
            'reliability_multiplier': reliability_multiplier,
            'trend_adjustment': trend_adjustment,
            'drought_risk': drought_risk,
            'flood_risk': flood_risk,
            'rainfall_variability': historical_data.rainfall_variability
        }
    
    def _calculate_rainfall_reliability(self, 
                                      growing_months: List[str],
                                      historical_data: HistoricalRainfallData) -> float:
        """
        Calculate rainfall reliability for crop growing months.
        
        Args:
            growing_months: List of months when crop grows
            historical_data: Historical rainfall analysis
            
        Returns:
            Reliability score (0.0 to 1.0)
        """
        if not growing_months:
            return 0.5  # Default reliability
        
        # Calculate average rainfall for growing months
        growing_month_rainfall = []
        for month in growing_months:
            if month in historical_data.monthly_averages:
                growing_month_rainfall.append(historical_data.monthly_averages[month])
        
        if not growing_month_rainfall:
            return 0.5
        
        # Calculate reliability based on consistency
        avg_rainfall = sum(growing_month_rainfall) / len(growing_month_rainfall)
        
        # Higher reliability for consistent, adequate rainfall
        if avg_rainfall >= 100:  # Adequate rainfall
            reliability = 0.8
        elif avg_rainfall >= 50:
            reliability = 0.6
        else:
            reliability = 0.4
        
        # Adjust for variability (lower variability = higher reliability)
        variability_penalty = historical_data.rainfall_variability * 0.3
        reliability = max(0.1, reliability - variability_penalty)
        
        return reliability
    
    def _calculate_historical_risk_score(self, 
                                       crop_data: Dict[str, Any],
                                       historical_data: HistoricalRainfallData,
                                       current_season: str) -> float:
        """
        Calculate historical risk score for crop.
        
        Args:
            crop_data: Crop data
            historical_data: Historical rainfall analysis
            current_season: Current season
            
        Returns:
            Risk score (0.0 to 1.0)
        """
        # Base risk from drought and flood frequency
        drought_risk = len(historical_data.drought_years) / historical_data.years_analyzed
        flood_risk = len(historical_data.flood_years) / historical_data.years_analyzed
        
        # Crop-specific risk factors
        drought_tolerance = crop_data.get('drought_tolerance', 'medium')
        flood_tolerance = crop_data.get('flood_tolerance', 'medium')
        
        # Adjust risk based on crop tolerance
        drought_multiplier = self._get_tolerance_multiplier(drought_tolerance)
        flood_multiplier = self._get_tolerance_multiplier(flood_tolerance)
        
        # Calculate weighted risk
        weighted_drought_risk = drought_risk * drought_multiplier
        weighted_flood_risk = flood_risk * flood_multiplier
        
        # Combine risks
        total_risk = (weighted_drought_risk + weighted_flood_risk) / 2
        
        # Add variability risk
        variability_risk = historical_data.rainfall_variability * 0.5
        
        final_risk = min(1.0, (total_risk + variability_risk) / 2)
        
        return final_risk
    
    def _get_tolerance_multiplier(self, tolerance: str) -> float:
        """Get risk multiplier based on crop tolerance."""
        tolerance_map = {
            'high': 0.5,    # High tolerance = lower risk
            'medium': 1.0,  # Medium tolerance = normal risk
            'low': 2.0      # Low tolerance = higher risk
        }
        return tolerance_map.get(tolerance, 1.0)
    
    def _get_default_growing_months(self, season: str) -> List[str]:
        """Get default growing months for a season."""
        if season == 'rainy_season':
            return ['November', 'December', 'January', 'February', 'March', 'April']
        elif season == 'dry_season':
            return ['May', 'June', 'July', 'August', 'September', 'October']
        else:
            return ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    def _add_historical_variety_recommendations(self, 
                                              top_crops: List[Dict[str, Any]], 
                                              seasonal_rainfall: float,
                                              current_temp: float,
                                              historical_data: HistoricalRainfallData) -> List[Dict[str, Any]]:
        """
        Add historical-enhanced variety recommendations.
        
        Args:
            top_crops: Top crop recommendations
            seasonal_rainfall: Estimated seasonal rainfall
            current_temp: Current temperature
            historical_data: Historical rainfall analysis
            
        Returns:
            Enhanced crop recommendations with varieties
        """
        enhanced_crops = []
        
        for crop in top_crops:
            crop_id = crop['crop_id']
            crop_data = self.crop_db.get_crop(crop_id)
            
            if not crop_data or 'varieties' not in crop_data:
                enhanced_crops.append(crop)
                continue
            
            # Score varieties with historical data
            scored_varieties = []
            for variety in crop_data['varieties']:
                variety_score = self._score_historical_variety(
                    variety, seasonal_rainfall, current_temp, historical_data
                )
                scored_varieties.append(variety_score)
            
            # Sort varieties by score
            scored_varieties.sort(key=lambda x: x['score'], reverse=True)
            
            # Add top varieties to crop
            enhanced_crop = crop.copy()
            enhanced_crop['top_varieties'] = scored_varieties[:3]  # Top 3 varieties
            enhanced_crops.append(enhanced_crop)
        
        return enhanced_crops
    
    def _score_historical_variety(self, 
                                variety: Dict[str, Any], 
                                seasonal_rainfall: float, 
                                current_temp: float,
                                historical_data: HistoricalRainfallData) -> Dict[str, Any]:
        """
        Score variety with historical data integration.
        
        Args:
            variety: Variety data
            seasonal_rainfall: Estimated seasonal rainfall
            current_temp: Current temperature
            historical_data: Historical rainfall analysis
            
        Returns:
            Scored variety data
        """
        # Get base variety score
        base_score = self._score_variety(variety, seasonal_rainfall, current_temp)
        
        # Add historical reliability factor
        reliability_score = self._calculate_rainfall_reliability(
            variety.get('growing_months', []), historical_data
        )
        
        # Calculate historical risk
        risk_score = self._calculate_historical_risk_score(
            variety, historical_data, 'current'
        )
        
        # Adjust score
        adjusted_score = base_score['score'] * (0.8 + reliability_score * 0.4) * (1 - risk_score * 0.2)
        
        enhanced_variety = base_score.copy()
        enhanced_variety.update({
            'score': adjusted_score,
            'reliability_score': reliability_score,
            'risk_score': risk_score,
            'historical_adjustment': adjusted_score - base_score['score']
        })
        
        return enhanced_variety
    
    def _generate_historical_planting_calendar(self, 
                                             top_crops: List[Dict[str, Any]], 
                                             current_month: str,
                                             historical_data: HistoricalRainfallData) -> List[Dict[str, Any]]:
        """
        Generate historical-enhanced planting calendar.
        
        Args:
            top_crops: Top crop recommendations
            current_month: Current month
            historical_data: Historical rainfall analysis
            
        Returns:
            Enhanced planting calendar
        """
        calendar = []
        
        for crop in top_crops:
            crop_id = crop['crop_id']
            crop_data = self.crop_db.get_crop(crop_id)
            
            if not crop_data:
                continue
            
            # Get optimal planting window
            planting_window = crop_data.get('planting_window', [])
            
            # Adjust based on historical data
            adjusted_window = self._adjust_planting_window(
                planting_window, historical_data, current_month
            )
            
            calendar.append({
                'crop_id': crop_id,
                'crop_name': crop_data.get('name', crop_id),
                'original_window': planting_window,
                'adjusted_window': adjusted_window,
                'historical_reliability': crop.get('reliability_score', 0.5),
                'risk_level': crop.get('risk_score', 0.5)
            })
        
        return calendar
    
    def _adjust_planting_window(self, 
                              planting_window: List[str],
                              historical_data: HistoricalRainfallData,
                              current_month: str) -> List[str]:
        """
        Adjust planting window based on historical data.
        
        Args:
            planting_window: Original planting window
            historical_data: Historical rainfall analysis
            current_month: Current month
            
        Returns:
            Adjusted planting window
        """
        if not planting_window:
            return planting_window
        
        # Adjust based on climate trend
        if historical_data.climate_trend == 'increasing':
            # Earlier planting for increasing rainfall
            adjusted_window = self._shift_window_earlier(planting_window)
        elif historical_data.climate_trend == 'decreasing':
            # Later planting for decreasing rainfall
            adjusted_window = self._shift_window_later(planting_window)
        else:
            adjusted_window = planting_window
        
        return adjusted_window
    
    def _shift_window_earlier(self, window: List[str]) -> List[str]:
        """Shift planting window earlier by one month."""
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        adjusted_window = []
        for month in window:
            try:
                current_index = months.index(month)
                new_index = max(0, current_index - 1)
                adjusted_window.append(months[new_index])
            except ValueError:
                adjusted_window.append(month)
        
        return adjusted_window
    
    def _shift_window_later(self, window: List[str]) -> List[str]:
        """Shift planting window later by one month."""
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        adjusted_window = []
        for month in window:
            try:
                current_index = months.index(month)
                new_index = min(11, current_index + 1)
                adjusted_window.append(months[new_index])
            except ValueError:
                adjusted_window.append(month)
        
        return adjusted_window
    
    def _generate_historical_seasonal_advice(self, 
                                           current_season: str, 
                                           seasonal_rainfall: float, 
                                           current_temp: float,
                                           historical_data: HistoricalRainfallData) -> Dict[str, Any]:
        """
        Generate historical-enhanced seasonal advice.
        
        Args:
            current_season: Current season
            seasonal_rainfall: Estimated seasonal rainfall
            current_temp: Current temperature
            historical_data: Historical rainfall analysis
            
        Returns:
            Enhanced seasonal advice
        """
        base_advice = self._generate_seasonal_advice(current_season, seasonal_rainfall, current_temp)
        
        # Ensure base_advice has the required structure
        if not isinstance(base_advice, dict):
            base_advice = {'advice': str(base_advice)}
        elif 'advice' not in base_advice:
            base_advice['advice'] = "Seasonal advice for current conditions."
        
        # Add historical insights
        historical_insights = []
        
        # Climate trend advice
        if historical_data.climate_trend == 'increasing':
            historical_insights.append("🌧️ **Historical Trend**: Rainfall has been increasing over the past years. Consider early planting to take advantage of longer growing seasons.")
        elif historical_data.climate_trend == 'decreasing':
            historical_insights.append("🌤️ **Historical Trend**: Rainfall has been decreasing. Consider drought-resistant crops and water conservation techniques.")
        
        # Variability advice
        if historical_data.rainfall_variability > 0.7:
            historical_insights.append("⚠️ **High Variability**: Rainfall patterns are highly variable. Consider flexible planting strategies and multiple crop options.")
        elif historical_data.rainfall_variability < 0.3:
            historical_insights.append("✅ **Stable Patterns**: Rainfall patterns are relatively stable. You can plan with more confidence.")
        
        # Drought/flood frequency advice
        drought_freq = len(historical_data.drought_years) / historical_data.years_analyzed
        if drought_freq > 0.3:
            historical_insights.append("🌵 **Drought Risk**: Historical data shows frequent drought conditions. Prioritize drought-tolerant crops and irrigation planning.")
        
        flood_freq = len(historical_data.flood_years) / historical_data.years_analyzed
        if flood_freq > 0.2:
            historical_insights.append("🌊 **Flood Risk**: Historical data shows occasional flooding. Consider elevated planting areas and flood-resistant varieties.")
        
        # Combine advice
        enhanced_advice = base_advice.copy()
        if historical_insights:
            enhanced_advice['historical_insights'] = historical_insights
            enhanced_advice['advice'] += "\n\n**Historical Analysis:**\n" + "\n".join(historical_insights)
        
        return enhanced_advice
    
    def _generate_historical_rainy_season_advice(self, 
                                               rainy_season_rainfall: float, 
                                               rainy_temp: float,
                                               historical_data: HistoricalRainfallData) -> Dict[str, Any]:
        """
        Generate historical-enhanced seasonal advice for rainy season.
        
        Args:
            rainy_season_rainfall: Estimated rainy season rainfall
            rainy_temp: Estimated rainy season temperature
            historical_data: Historical rainfall analysis
            
        Returns:
            Enhanced seasonal advice for rainy season
        """
        base_advice = self._generate_seasonal_advice('rainy_season', rainy_season_rainfall, rainy_temp)
        
        if not isinstance(base_advice, dict):
            base_advice = {'advice': str(base_advice)}
        elif 'advice' not in base_advice:
            base_advice['advice'] = "Seasonal advice for rainy season conditions."
        
        historical_insights = []
        
        # Climate trend advice
        if historical_data.climate_trend == 'increasing':
            historical_insights.append("🌧️ **Historical Trend**: Rainfall has been increasing over the past years. Consider early planting to take advantage of longer growing seasons.")
        elif historical_data.climate_trend == 'decreasing':
            historical_insights.append("🌤️ **Historical Trend**: Rainfall has been decreasing. Consider drought-resistant crops and water conservation techniques.")
        
        # Variability advice
        if historical_data.rainfall_variability > 0.7:
            historical_insights.append("⚠️ **High Variability**: Rainfall patterns are highly variable. Consider flexible planting strategies and multiple crop options.")
        elif historical_data.rainfall_variability < 0.3:
            historical_insights.append("✅ **Stable Patterns**: Rainfall patterns are relatively stable. You can plan with more confidence.")
        
        # Drought/flood frequency advice
        drought_freq = len(historical_data.drought_years) / historical_data.years_analyzed
        if drought_freq > 0.3:
            historical_insights.append("🌵 **Drought Risk**: Historical data shows frequent drought conditions. Prioritize drought-tolerant crops and irrigation planning.")
        
        flood_freq = len(historical_data.flood_years) / historical_data.years_analyzed
        if flood_freq > 0.2:
            historical_insights.append("🌊 **Flood Risk**: Historical data shows occasional flooding. Consider elevated planting areas and flood-resistant varieties.")
        
        enhanced_advice = base_advice.copy()
        if historical_insights:
            enhanced_advice['historical_insights'] = historical_insights
            enhanced_advice['advice'] += "\n\n**Historical Analysis:**\n" + "\n".join(historical_insights)
        
        return enhanced_advice
    
    def _generate_historical_dry_season_advice(self, 
                                             dry_season_rainfall: float, 
                                             dry_temp: float,
                                             historical_data: HistoricalRainfallData) -> Dict[str, Any]:
        """
        Generate historical-enhanced seasonal advice for dry season.
        
        Args:
            dry_season_rainfall: Estimated dry season rainfall
            dry_temp: Estimated dry season temperature
            historical_data: Historical rainfall analysis
            
        Returns:
            Enhanced seasonal advice for dry season
        """
        base_advice = self._generate_seasonal_advice('dry_season', dry_season_rainfall, dry_temp)
        
        if not isinstance(base_advice, dict):
            base_advice = {'advice': str(base_advice)}
        elif 'advice' not in base_advice:
            base_advice['advice'] = "Seasonal advice for dry season conditions."
        
        historical_insights = []
        
        # Climate trend advice
        if historical_data.climate_trend == 'increasing':
            historical_insights.append("🌧️ **Historical Trend**: Rainfall has been increasing over the past years. Consider early planting to take advantage of longer growing seasons.")
        elif historical_data.climate_trend == 'decreasing':
            historical_insights.append("🌤️ **Historical Trend**: Rainfall has been decreasing. Consider drought-resistant crops and water conservation techniques.")
        
        # Variability advice
        if historical_data.rainfall_variability > 0.7:
            historical_insights.append("⚠️ **High Variability**: Rainfall patterns are highly variable. Consider flexible planting strategies and multiple crop options.")
        elif historical_data.rainfall_variability < 0.3:
            historical_insights.append("✅ **Stable Patterns**: Rainfall patterns are relatively stable. You can plan with more confidence.")
        
        # Drought/flood frequency advice
        drought_freq = len(historical_data.drought_years) / historical_data.years_analyzed
        if drought_freq > 0.3:
            historical_insights.append("🌵 **Drought Risk**: Historical data shows frequent drought conditions. Prioritize drought-tolerant crops and irrigation planning.")
        
        flood_freq = len(historical_data.flood_years) / historical_data.years_analyzed
        if flood_freq > 0.2:
            historical_insights.append("🌊 **Flood Risk**: Historical data shows occasional flooding. Consider elevated planting areas and flood-resistant varieties.")
        
        enhanced_advice = base_advice.copy()
        if historical_insights:
            enhanced_advice['historical_insights'] = historical_insights
            enhanced_advice['advice'] += "\n\n**Historical Analysis:**\n" + "\n".join(historical_insights)
        
        return enhanced_advice
    
    def _generate_historical_all_seasons_advice(self, 
                                               rainy_season_rainfall: float, 
                                               dry_season_rainfall: float,
                                               historical_data: HistoricalRainfallData) -> Dict[str, Any]:
        """
        Generate historical-enhanced comprehensive seasonal advice.
        
        Args:
            rainy_season_rainfall: Estimated rainy season rainfall
            dry_season_rainfall: Estimated dry season rainfall
            historical_data: Historical rainfall analysis
            
        Returns:
            Enhanced comprehensive seasonal advice
        """
        base_advice = self._generate_seasonal_advice('all_seasons', (rainy_season_rainfall + dry_season_rainfall) / 2, (25 + 22) / 2)
        
        if not isinstance(base_advice, dict):
            base_advice = {'advice': str(base_advice)}
        elif 'advice' not in base_advice:
            base_advice['advice'] = "Seasonal advice for all seasons."
        
        historical_insights = []
        
        # Climate trend advice
        if historical_data.climate_trend == 'increasing':
            historical_insights.append("🌧️ **Historical Trend**: Rainfall has been increasing over the past years. Consider early planting to take advantage of longer growing seasons.")
        elif historical_data.climate_trend == 'decreasing':
            historical_insights.append("🌤️ **Historical Trend**: Rainfall has been decreasing. Consider drought-resistant crops and water conservation techniques.")
        
        # Variability advice
        if historical_data.rainfall_variability > 0.7:
            historical_insights.append("⚠️ **High Variability**: Rainfall patterns are highly variable. Consider flexible planting strategies and multiple crop options.")
        elif historical_data.rainfall_variability < 0.3:
            historical_insights.append("✅ **Stable Patterns**: Rainfall patterns are relatively stable. You can plan with more confidence.")
        
        # Drought/flood frequency advice
        drought_freq = len(historical_data.drought_years) / historical_data.years_analyzed
        if drought_freq > 0.3:
            historical_insights.append("🌵 **Drought Risk**: Historical data shows frequent drought conditions. Prioritize drought-tolerant crops and irrigation planning.")
        
        flood_freq = len(historical_data.flood_years) / historical_data.years_analyzed
        if flood_freq > 0.2:
            historical_insights.append("🌊 **Flood Risk**: Historical data shows occasional flooding. Consider elevated planting areas and flood-resistant varieties.")
        
        enhanced_advice = base_advice.copy()
        if historical_insights:
            enhanced_advice['historical_insights'] = historical_insights
            enhanced_advice['advice'] += "\n\n**Historical Analysis:**\n" + "\n".join(historical_insights)
        
        return enhanced_advice
    
    def _analyze_climate_trends(self, historical_data: HistoricalRainfallData) -> Dict[str, Any]:
        """
        Analyze climate trends from historical data.
        
        Args:
            historical_data: Historical rainfall analysis
            
        Returns:
            Climate trend analysis
        """
        return {
            'trend': historical_data.climate_trend,
            'variability': historical_data.rainfall_variability,
            'drought_frequency': len(historical_data.drought_years) / historical_data.years_analyzed,
            'flood_frequency': len(historical_data.flood_years) / historical_data.years_analyzed,
            'years_analyzed': historical_data.years_analyzed,
            'trend_description': self._get_trend_description(historical_data),
            'recommendations': self._get_trend_recommendations(historical_data)
        }
    
    def _get_trend_description(self, historical_data: HistoricalRainfallData) -> str:
        """Get human-readable trend description."""
        if historical_data.climate_trend == 'increasing':
            return "Rainfall has been increasing over the analyzed period"
        elif historical_data.climate_trend == 'decreasing':
            return "Rainfall has been decreasing over the analyzed period"
        else:
            return "Rainfall patterns have remained relatively stable"
    
    def _get_trend_recommendations(self, historical_data: HistoricalRainfallData) -> List[str]:
        """Get recommendations based on climate trends."""
        recommendations = []
        
        if historical_data.climate_trend == 'increasing':
            recommendations.extend([
                "Consider early planting to take advantage of longer growing seasons",
                "Monitor for potential flooding and prepare drainage systems",
                "High-yield crops may perform better with increased rainfall"
            ])
        elif historical_data.climate_trend == 'decreasing':
            recommendations.extend([
                "Prioritize drought-resistant crop varieties",
                "Implement water conservation and irrigation systems",
                "Consider shorter-season crops to reduce water requirements"
            ])
        
        if historical_data.rainfall_variability > 0.6:
            recommendations.append("Maintain flexible planting strategies due to high rainfall variability")
        
        return recommendations

    def _identify_year_round_crops(self, 
                                  rainy_recommendations: List[Dict[str, Any]], 
                                  dry_recommendations: List[Dict[str, Any]],
                                  historical_data: HistoricalRainfallData) -> List[Dict[str, Any]]:
        """
        Identify crops that perform well across both seasons.
        
        Args:
            rainy_recommendations: Rainy season crop recommendations
            dry_recommendations: Dry season crop recommendations
            historical_data: Historical rainfall analysis
            
        Returns:
            List of year-round crop recommendations
        """
        year_round_crops = []
        
        # Create sets of crop IDs for each season
        rainy_crop_ids = {crop['crop_id'] for crop in rainy_recommendations}
        dry_crop_ids = {crop['crop_id'] for crop in dry_recommendations}
        
        # Find crops that appear in both seasons
        common_crop_ids = rainy_crop_ids.intersection(dry_crop_ids)
        
        for crop_id in common_crop_ids:
            # Get recommendations for both seasons
            rainy_crop = next(crop for crop in rainy_recommendations if crop['crop_id'] == crop_id)
            dry_crop = next(crop for crop in dry_recommendations if crop['crop_id'] == crop_id)
            
            # Calculate year-round score (average of both seasons)
            year_round_score = (rainy_crop['total_score'] + dry_crop['total_score']) / 2
            
            # Calculate year-round reliability (average of both seasons)
            rainy_reliability = rainy_crop.get('reliability_score', 0.5)
            dry_reliability = dry_crop.get('reliability_score', 0.5)
            year_round_reliability = (rainy_reliability + dry_reliability) / 2
            
            # Calculate year-round risk (average of both seasons)
            rainy_risk = rainy_crop.get('risk_score', 0.5)
            dry_risk = dry_crop.get('risk_score', 0.5)
            year_round_risk = (rainy_risk + dry_risk) / 2
            
            # Create year-round crop recommendation
            year_round_crop = {
                'crop_id': crop_id,
                'crop_name': rainy_crop.get('crop_name', crop_id),
                'total_score': year_round_score,
                'reliability_score': year_round_reliability,
                'risk_score': year_round_risk,
                'rainy_season_score': rainy_crop['total_score'],
                'dry_season_score': dry_crop['total_score'],
                'suitability_level': self._get_year_round_suitability_level(year_round_score),
                'historical_factors': {
                    'rainfall_variability': historical_data.rainfall_variability,
                    'climate_trend': historical_data.climate_trend,
                    'drought_frequency': len(historical_data.drought_years) / historical_data.years_analyzed,
                    'flood_frequency': len(historical_data.flood_years) / historical_data.years_analyzed
                }
            }
            
            year_round_crops.append(year_round_crop)
        
        # Sort by year-round score
        year_round_crops.sort(key=lambda x: x['total_score'], reverse=True)
        
        return year_round_crops[:5]  # Return top 5 year-round crops
    
    def _get_year_round_suitability_level(self, score: float) -> str:
        """Get suitability level for year-round crops."""
        if score >= 8.0:
            return "excellent"
        elif score >= 6.0:
            return "good"
        elif score >= 4.0:
            return "fair"
        else:
            return "poor"


# Create global instance
historical_enhanced_engine = HistoricalEnhancedEngine() 