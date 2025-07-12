"""
Enhanced Rainfall Analyzer for the Agricultural Advisor Bot.
Integrates historical rainfall data with current/forecast data for comprehensive analysis.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import calendar
from scripts.weather_engine.historical_weather_api import historical_weather_api, HistoricalRainfallData
from scripts.utils.logger import logger


class EnhancedRainfallAnalyzer:
    """Enhanced rainfall analyzer with historical data integration."""
    
    def __init__(self):
        """Initialize enhanced rainfall analyzer."""
        self.historical_api = historical_weather_api
        logger.info("Enhanced rainfall analyzer initialized")
    
    def analyze_comprehensive_rainfall(self,
                                     lat: float,
                                     lon: float,
                                     current_rainfall: float,
                                     forecast_rainfall: float,
                                     historical_years: int = 5,
                                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive rainfall analysis with historical context.
        
        Args:
            lat: Latitude
            lon: Longitude
            current_rainfall: Current 7-day rainfall
            forecast_rainfall: Forecast 7-day rainfall
            historical_years: Years of historical data to analyze
            user_id: Optional user ID for logging
            
        Returns:
            Comprehensive rainfall analysis
        """
        logger.info(f"Starting comprehensive rainfall analysis for {lat}, {lon}", user_id)
        
        try:
            # Get current month
            current_month = datetime.now().strftime('%B')
            
            # Get historical data
            historical_data = self.historical_api.get_historical_rainfall(
                lat, lon, historical_years, user_id
            )
            
            # Basic current analysis
            basic_analysis = {
                'current_7day_rainfall': current_rainfall,
                'forecast_7day_rainfall': forecast_rainfall,
                'total_14day_estimate': current_rainfall + forecast_rainfall,
                'current_month': current_month
            }
            
            if not historical_data:
                logger.warning("Historical data unavailable, using basic analysis only", user_id)
                return self._create_fallback_analysis(basic_analysis)
            
            # Enhanced analysis with historical context
            enhanced_analysis = self._create_enhanced_analysis(
                basic_analysis, historical_data, current_month, user_id
            )
            
            logger.info("Comprehensive rainfall analysis completed", user_id)
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive rainfall analysis: {e}", user_id)
            return self._create_fallback_analysis({
                'current_7day_rainfall': current_rainfall,
                'forecast_7day_rainfall': forecast_rainfall,
                'error': 'Analysis failed'
            })
    
    def get_seasonal_rainfall_prediction(self,
                                       lat: float,
                                       lon: float,
                                       current_month: str,
                                       historical_years: int = 5,
                                       user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get seasonal rainfall prediction based on historical patterns.
        
        Args:
            lat: Latitude
            lon: Longitude
            current_month: Current month name
            historical_years: Years of historical data
            user_id: Optional user ID for logging
            
        Returns:
            Seasonal rainfall prediction
        """
        try:
            historical_data = self.historical_api.get_historical_rainfall(
                lat, lon, historical_years, user_id
            )
            
            if not historical_data:
                return {'error': 'Historical data unavailable'}
            
            # Get remaining months in current season
            remaining_months = self._get_remaining_season_months(current_month)
            
            # Calculate expected rainfall for remaining season
            expected_seasonal_rainfall = 0
            monthly_predictions = {}
            
            for month in remaining_months:
                if month in historical_data.monthly_averages:
                    monthly_avg = historical_data.monthly_averages[month]
                    monthly_predictions[month] = monthly_avg
                    expected_seasonal_rainfall += monthly_avg
            
            # Determine season type
            season_type = self._determine_season_type(historical_data, current_month)
            
            # Calculate seasonal outlook
            outlook = self._calculate_seasonal_outlook(
                historical_data, expected_seasonal_rainfall, current_month
            )
            
            return {
                'expected_seasonal_rainfall': expected_seasonal_rainfall,
                'monthly_predictions': monthly_predictions,
                'season_type': season_type,
                'outlook': outlook,
                'confidence_level': self._calculate_prediction_confidence(historical_data),
                'years_analyzed': historical_years
            }
            
        except Exception as e:
            logger.error(f"Error in seasonal rainfall prediction: {e}", user_id)
            return {'error': 'Prediction failed'}
    
    def compare_with_historical_patterns(self,
                                       lat: float,
                                       lon: float,
                                       current_rainfall: float,
                                       month: str,
                                       historical_years: int = 5,
                                       user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare current rainfall with historical patterns.
        
        Args:
            lat: Latitude
            lon: Longitude
            current_rainfall: Current month rainfall
            month: Month name
            historical_years: Years of historical data
            user_id: Optional user ID for logging
            
        Returns:
            Historical comparison analysis
        """
        try:
            comparison = self.historical_api.compare_current_with_historical(
                lat, lon, current_rainfall, month, historical_years, user_id
            )
            
            if not comparison:
                return {'error': 'Comparison data unavailable'}
            
            # Add agricultural implications
            agricultural_implications = self._get_agricultural_implications(comparison)
            comparison['agricultural_implications'] = agricultural_implications
            
            # Add recommendations
            recommendations = self._get_rainfall_recommendations(comparison)
            comparison['recommendations'] = recommendations
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing with historical patterns: {e}", user_id)
            return {'error': 'Comparison failed'}
    
    def get_drought_risk_assessment(self,
                                  lat: float,
                                  lon: float,
                                  current_conditions: Dict[str, Any],
                                  historical_years: int = 5,
                                  user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Assess drought risk based on current conditions and historical patterns.
        
        Args:
            lat: Latitude
            lon: Longitude
            current_conditions: Current weather/rainfall conditions
            historical_years: Years of historical data
            user_id: Optional user ID for logging
            
        Returns:
            Drought risk assessment
        """
        try:
            historical_data = self.historical_api.get_historical_rainfall(
                lat, lon, historical_years, user_id
            )
            
            if not historical_data:
                return {'error': 'Historical data unavailable for drought assessment'}
            
            current_month = datetime.now().strftime('%B')
            current_rainfall = current_conditions.get('total_7day_rainfall', 0)
            
            # Calculate drought indicators
            drought_indicators = self._calculate_drought_indicators(
                historical_data, current_rainfall, current_month
            )
            
            # Assess risk level
            risk_level = self._assess_drought_risk_level(drought_indicators)
            
            # Generate recommendations
            drought_recommendations = self._get_drought_recommendations(risk_level, historical_data)
            
            return {
                'drought_risk_level': risk_level,
                'drought_indicators': drought_indicators,
                'historical_drought_years': historical_data.drought_years,
                'rainfall_variability': historical_data.rainfall_variability,
                'recommendations': drought_recommendations,
                'monitoring_advice': self._get_drought_monitoring_advice(risk_level)
            }
            
        except Exception as e:
            logger.error(f"Error in drought risk assessment: {e}", user_id)
            return {'error': 'Drought assessment failed'}
    
    def _create_enhanced_analysis(self,
                                basic_analysis: Dict[str, Any],
                                historical_data: HistoricalRainfallData,
                                current_month: str,
                                user_id: Optional[str]) -> Dict[str, Any]:
        """Create enhanced analysis with historical context."""
        try:
            # Get historical average for current month
            historical_avg = historical_data.monthly_averages.get(current_month, 0)
            
            # Calculate seasonal estimate using historical patterns
            enhanced_seasonal_estimate = self._calculate_enhanced_seasonal_estimate(
                basic_analysis, historical_data, current_month
            )
            
            # Determine rainfall status
            current_total = basic_analysis['current_7day_rainfall']
            rainfall_status = self._determine_rainfall_status(current_total, historical_avg)
            
            # Climate context
            climate_context = {
                'rainfall_variability': historical_data.rainfall_variability,
                'climate_trend': historical_data.climate_trend,
                'wet_season_months': historical_data.wet_season_months,
                'dry_season_months': historical_data.dry_season_months,
                'recent_drought_years': historical_data.drought_years[-3:] if historical_data.drought_years else [],
                'recent_flood_years': historical_data.flood_years[-3:] if historical_data.flood_years else []
            }
            
            # Risk assessment
            risk_assessment = self._assess_climate_risks(historical_data, current_month, current_total)
            
            return {
                **basic_analysis,
                'enhanced_seasonal_estimate': enhanced_seasonal_estimate,
                'historical_monthly_average': historical_avg,
                'rainfall_status': rainfall_status,
                'climate_context': climate_context,
                'risk_assessment': risk_assessment,
                'historical_years_analyzed': historical_data.years_analyzed,
                'analysis_type': 'enhanced_with_historical_data'
            }
            
        except Exception as e:
            logger.error(f"Error creating enhanced analysis: {e}", user_id)
            return basic_analysis
    
    def _calculate_enhanced_seasonal_estimate(self,
                                            basic_analysis: Dict[str, Any],
                                            historical_data: HistoricalRainfallData,
                                            current_month: str) -> float:
        """Calculate enhanced seasonal rainfall estimate using historical patterns."""
        try:
            # Get remaining months in rainy season
            remaining_months = self._get_remaining_season_months(current_month)
            
            # Sum historical averages for remaining months
            remaining_seasonal_rainfall = 0
            for month in remaining_months:
                if month in historical_data.monthly_averages:
                    remaining_seasonal_rainfall += historical_data.monthly_averages[month]
            
            # Add current month's actual rainfall (use 7-day data extrapolated)
            current_month_estimate = basic_analysis['total_14day_estimate'] * 2  # Rough monthly estimate
            
            total_seasonal_estimate = current_month_estimate + remaining_seasonal_rainfall
            
            # Apply climate trend adjustment
            if historical_data.climate_trend == "increasing":
                total_seasonal_estimate *= 1.1
            elif historical_data.climate_trend == "decreasing":
                total_seasonal_estimate *= 0.9
            
            return round(total_seasonal_estimate, 1)
            
        except Exception as e:
            logger.error(f"Error calculating enhanced seasonal estimate: {e}")
            return basic_analysis.get('total_14day_estimate', 0) * 8  # Fallback
    
    def _determine_rainfall_status(self, current_rainfall: float, historical_avg: float) -> Dict[str, Any]:
        """Determine current rainfall status compared to historical average."""
        if historical_avg == 0:
            return {
                'status': 'no_historical_data',
                'description': 'No historical data available for comparison',
                'percentage_of_normal': None
            }
        
        percentage = (current_rainfall / historical_avg) * 100
        
        if percentage >= 150:
            status = 'well_above_normal'
            description = 'Well above normal rainfall'
        elif percentage >= 120:
            status = 'above_normal'
            description = 'Above normal rainfall'
        elif percentage >= 80:
            status = 'normal'
            description = 'Normal rainfall'
        elif percentage >= 50:
            status = 'below_normal'
            description = 'Below normal rainfall'
        elif percentage >= 25:
            status = 'well_below_normal'
            description = 'Well below normal rainfall'
        else:
            status = 'severe_deficit'
            description = 'Severe rainfall deficit'
        
        return {
            'status': status,
            'description': description,
            'percentage_of_normal': round(percentage, 1)
        }
    
    def _get_remaining_season_months(self, current_month: str) -> List[str]:
        """Get remaining months in the current rainy season."""
        # Define Malawi rainy season (November to April)
        rainy_season_months = [
            'November', 'December', 'January', 
            'February', 'March', 'April'
        ]
        
        try:
            current_index = rainy_season_months.index(current_month)
            return rainy_season_months[current_index + 1:]
        except ValueError:
            # Current month not in rainy season, return empty list
            return []
    
    def _determine_season_type(self, historical_data: HistoricalRainfallData, current_month: str) -> str:
        """Determine if current month is in wet or dry season."""
        if current_month in historical_data.wet_season_months:
            return 'wet_season'
        elif current_month in historical_data.dry_season_months:
            return 'dry_season'
        else:
            return 'transitional'
    
    def _calculate_seasonal_outlook(self,
                                  historical_data: HistoricalRainfallData,
                                  expected_rainfall: float,
                                  current_month: str) -> Dict[str, Any]:
        """Calculate seasonal outlook based on historical patterns."""
        if not historical_data.annual_averages:
            return {'outlook': 'unknown', 'confidence': 'low'}
        
        avg_annual_rainfall = sum(historical_data.annual_averages) / len(historical_data.annual_averages)
        
        if expected_rainfall >= avg_annual_rainfall * 1.2:
            outlook = 'above_normal'
            description = 'Above normal seasonal rainfall expected'
        elif expected_rainfall >= avg_annual_rainfall * 0.8:
            outlook = 'normal'
            description = 'Normal seasonal rainfall expected'
        else:
            outlook = 'below_normal'
            description = 'Below normal seasonal rainfall expected'
        
        return {
            'outlook': outlook,
            'description': description,
            'expected_percentage_of_normal': round((expected_rainfall / avg_annual_rainfall) * 100, 1)
        }
    
    def _calculate_prediction_confidence(self, historical_data: HistoricalRainfallData) -> str:
        """Calculate confidence level for predictions based on data quality."""
        if historical_data.years_analyzed >= 5:
            if historical_data.rainfall_variability < 30:  # Low variability
                return 'high'
            elif historical_data.rainfall_variability < 50:
                return 'medium'
            else:
                return 'low'
        elif historical_data.years_analyzed >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _create_fallback_analysis(self, basic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback analysis when historical data is unavailable."""
        return {
            **basic_data,
            'enhanced_seasonal_estimate': basic_data.get('total_14day_estimate', 0) * 8,
            'historical_monthly_average': None,
            'rainfall_status': {
                'status': 'no_historical_data',
                'description': 'Historical data not available',
                'percentage_of_normal': None
            },
            'climate_context': {
                'note': 'Historical climate data unavailable'
            },
            'analysis_type': 'basic_current_forecast_only'
        }
    
    def _assess_climate_risks(self,
                            historical_data: HistoricalRainfallData,
                            current_month: str,
                            current_rainfall: float) -> Dict[str, Any]:
        """Assess climate-related risks based on historical patterns."""
        risks = []
        opportunities = []
        
        # Drought risk
        if current_month in historical_data.wet_season_months:
            historical_avg = historical_data.monthly_averages.get(current_month, 0)
            if current_rainfall < historical_avg * 0.5:
                risks.append("High drought risk - rainfall well below normal")
            elif current_rainfall < historical_avg * 0.8:
                risks.append("Moderate drought risk - rainfall below normal")
        
        # Flood risk
        if historical_data.flood_years and len(historical_data.flood_years) > len(historical_data.drought_years):
            risks.append("Historical flood risk in this area")
        
        # Climate variability
        if historical_data.rainfall_variability > 40:
            risks.append("High rainfall variability - unpredictable conditions")
        
        # Climate trend implications
        if historical_data.climate_trend == "decreasing":
            risks.append("Long-term decreasing rainfall trend")
        elif historical_data.climate_trend == "increasing":
            opportunities.append("Long-term increasing rainfall trend")
        
        return {
            'risks': risks,
            'opportunities': opportunities,
            'overall_risk_level': 'high' if len(risks) >= 3 else 'medium' if len(risks) >= 1 else 'low'
        }
    
    def _get_agricultural_implications(self, comparison: Dict[str, Any]) -> List[str]:
        """Get agricultural implications of current rainfall status."""
        implications = []
        status = comparison.get('status', '')
        
        if status == 'above_normal':
            implications.extend([
                "Excellent conditions for crop establishment",
                "Monitor for waterlogging in low-lying areas",
                "Good opportunity for water-loving crops"
            ])
        elif status == 'normal':
            implications.extend([
                "Suitable conditions for most crops",
                "Continue with planned agricultural activities"
            ])
        elif status == 'below_normal':
            implications.extend([
                "Consider drought-tolerant crop varieties",
                "Implement water conservation practices",
                "Monitor soil moisture levels closely"
            ])
        elif status == 'drought_conditions':
            implications.extend([
                "High drought stress for crops",
                "Focus on drought-resistant varieties only",
                "Implement emergency water conservation",
                "Consider delaying planting if possible"
            ])
        
        return implications
    
    def _get_rainfall_recommendations(self, comparison: Dict[str, Any]) -> List[str]:
        """Get specific recommendations based on rainfall comparison."""
        recommendations = []
        status = comparison.get('status', '')
        
        if status in ['above_normal', 'normal']:
            recommendations.extend([
                "Proceed with normal planting schedule",
                "Ensure proper drainage systems are in place",
                "Take advantage of good soil moisture conditions"
            ])
        else:
            recommendations.extend([
                "Consider drought-tolerant crop varieties",
                "Implement mulching to conserve soil moisture",
                "Plan for supplementary irrigation if available"
            ])
        
        return recommendations
    
    def _calculate_drought_indicators(self,
                                    historical_data: HistoricalRainfallData,
                                    current_rainfall: float,
                                    current_month: str) -> Dict[str, Any]:
        """Calculate drought indicators based on current and historical data."""
        indicators = {}
        
        # Current rainfall vs historical average
        historical_avg = historical_data.monthly_averages.get(current_month, 0)
        if historical_avg > 0:
            rainfall_ratio = current_rainfall / historical_avg
            indicators['rainfall_deficit_ratio'] = round(1 - rainfall_ratio, 2)
        else:
            indicators['rainfall_deficit_ratio'] = 0
        
        # Rainfall variability (higher = more unpredictable)
        indicators['rainfall_variability'] = historical_data.rainfall_variability
        
        # Recent drought frequency
        total_years = historical_data.years_analyzed
        drought_frequency = len(historical_data.drought_years) / total_years if total_years > 0 else 0
        indicators['historical_drought_frequency'] = round(drought_frequency, 2)
        
        # Climate trend factor
        trend_factor = 0
        if historical_data.climate_trend == "decreasing":
            trend_factor = 0.2  # Increases drought risk
        elif historical_data.climate_trend == "increasing":
            trend_factor = -0.1  # Decreases drought risk
        indicators['climate_trend_factor'] = trend_factor
        
        return indicators
    
    def _assess_drought_risk_level(self, drought_indicators: Dict[str, Any]) -> str:
        """Assess overall drought risk level."""
        risk_score = 0
        
        # Rainfall deficit contribution
        deficit_ratio = drought_indicators.get('rainfall_deficit_ratio', 0)
        if deficit_ratio >= 0.5:  # 50% or more below normal
            risk_score += 3
        elif deficit_ratio >= 0.3:  # 30-50% below normal
            risk_score += 2
        elif deficit_ratio >= 0.1:  # 10-30% below normal
            risk_score += 1
        
        # Variability contribution
        variability = drought_indicators.get('rainfall_variability', 0)
        if variability >= 50:
            risk_score += 2
        elif variability >= 30:
            risk_score += 1
        
        # Historical frequency contribution
        drought_freq = drought_indicators.get('historical_drought_frequency', 0)
        if drought_freq >= 0.4:  # 40% or more years were drought years
            risk_score += 2
        elif drought_freq >= 0.2:  # 20-40% of years
            risk_score += 1
        
        # Climate trend contribution
        trend_factor = drought_indicators.get('climate_trend_factor', 0)
        if trend_factor > 0:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 6:
            return 'very_high'
        elif risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'moderate'
        else:
            return 'low'
    
    def _get_drought_recommendations(self, risk_level: str, historical_data: HistoricalRainfallData) -> List[str]:
        """Get drought-specific recommendations based on risk level."""
        recommendations = []
        
        if risk_level == 'very_high':
            recommendations.extend([
                "🚨 URGENT: Implement emergency drought response plan",
                "Focus exclusively on drought-resistant crop varieties",
                "Consider water harvesting and storage systems",
                "Reduce planted area to conserve water resources",
                "Activate community drought support networks"
            ])
        elif risk_level == 'high':
            recommendations.extend([
                "⚠️ HIGH PRIORITY: Prepare for drought conditions",
                "Select drought-tolerant varieties (sorghum, millet, cassava)",
                "Implement water conservation practices immediately",
                "Consider early-maturing crop varieties",
                "Plan supplementary irrigation if available"
            ])
        elif risk_level == 'moderate':
            recommendations.extend([
                "🔶 MODERATE: Monitor conditions closely",
                "Mix drought-tolerant and conventional varieties",
                "Implement basic water conservation (mulching)",
                "Have backup plans for irrigation",
                "Monitor weather forecasts regularly"
            ])
        else:  # low risk
            recommendations.extend([
                "✅ LOW RISK: Normal planting with precautions",
                "Include some drought-tolerant varieties as insurance",
                "Maintain basic water conservation practices",
                "Continue regular monitoring"
            ])
        
        # Add specific recommendations based on historical patterns
        if historical_data.climate_trend == "decreasing":
            recommendations.append("📉 Long-term trend: Plan for increasingly dry conditions")
        
        if historical_data.rainfall_variability > 40:
            recommendations.append("📊 High variability: Diversify crops to reduce risk")
        
        return recommendations
    
    def _get_drought_monitoring_advice(self, risk_level: str) -> List[str]:
        """Get drought monitoring advice based on risk level."""
        monitoring_advice = []
        
        if risk_level in ['very_high', 'high']:
            monitoring_advice.extend([
                "Check soil moisture daily",
                "Monitor crop stress indicators (wilting, leaf curl)",
                "Track local water reservoir levels",
                "Follow meteorological drought alerts",
                "Coordinate with agricultural extension services"
            ])
        elif risk_level == 'moderate':
            monitoring_advice.extend([
                "Check soil moisture 2-3 times per week",
                "Monitor weather forecasts for rainfall predictions",
                "Observe early signs of crop stress",
                "Stay informed about regional drought conditions"
            ])
        else:  # low risk
            monitoring_advice.extend([
                "Regular weekly soil moisture checks",
                "Monitor seasonal weather patterns",
                "Maintain awareness of drought indicators"
            ])
        
        return monitoring_advice


# Global enhanced rainfall analyzer instance
enhanced_rainfall_analyzer = EnhancedRainfallAnalyzer() 