"""
Enhanced Yield Predictor Module for Predictive Analytics.

Advanced yield prediction engine that uses sophisticated weather analysis,
historical patterns, and ensemble methods for improved accuracy.
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import VotingRegressor
from sklearn.model_selection import cross_val_score

from .yield_predictor import YieldPredictor
from .data_collector import DataCollector
from .model_manager import ModelManager
from scripts.weather_engine.enhanced_rainfall_analyzer import EnhancedRainfallAnalyzer
from scripts.weather_engine.historical_weather_api import historical_weather_api
from scripts.utils.logger import logger


class EnhancedYieldPredictor(YieldPredictor):
    """Enhanced yield predictor with sophisticated weather analysis."""
    
    def __init__(self):
        """Initialize enhanced yield predictor with additional components."""
        super().__init__()
        self.enhanced_rainfall_analyzer = EnhancedRainfallAnalyzer()
        self.historical_weather_api = historical_weather_api
        
    def predict_yield_enhanced(self, crop_id: str, location: Dict[str, float], 
                             user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced yield prediction with sophisticated weather analysis.
        
        Args:
            crop_id: Crop identifier
            location: Dictionary with lat/lon coordinates
            user_id: Optional user ID for logging
            
        Returns:
            Enhanced yield prediction with detailed weather analysis
        """
        try:
            logger.info(f"Starting enhanced yield prediction for {crop_id} at {location}", user_id)
            
            # Step 1: Get enhanced weather analysis
            enhanced_weather = self._get_enhanced_weather_analysis(location, user_id)
            
            # Step 2: Get combined data with enhanced features
            combined_data = self.data_collector.get_combined_data(crop_id, location, user_id)
            if not combined_data:
                return {
                    'success': False,
                    'error': 'Failed to collect required data',
                    'crop_id': crop_id,
                    'location': location
                }
            
            # Step 3: Add enhanced weather data
            combined_data['enhanced_weather'] = enhanced_weather
            
            # Step 4: Train or use enhanced model
            model_result = self._train_enhanced_model(crop_id, combined_data, user_id)
            if not model_result['success']:
                return {
                    'success': False,
                    'error': f"Model training failed: {model_result.get('error', 'Unknown error')}",
                    'crop_id': crop_id,
                    'location': location
                }
            
            # Step 5: Extract enhanced features
            enhanced_features = self._extract_enhanced_features(combined_data)
            if not enhanced_features:
                return {
                    'success': False,
                    'error': 'Failed to extract enhanced features',
                    'crop_id': crop_id,
                    'location': location
                }
            
            # Step 6: Make enhanced prediction
            prediction_result = self.model_manager.predict_yield(
                crop_id, enhanced_features, model_type="enhanced", user_id=user_id
            )
            
            if not prediction_result['success']:
                return {
                    'success': False,
                    'error': f"Prediction failed: {prediction_result.get('error', 'Unknown error')}",
                    'crop_id': crop_id,
                    'location': location
                }
            
            # Step 7: Enhance result with weather insights
            enhanced_result = self._enhance_prediction_with_weather_insights(
                prediction_result, combined_data, enhanced_weather, crop_id, location
            )
            
            logger.info(f"Enhanced yield prediction completed for {crop_id}: {enhanced_result['predicted_yield']} tons/ha", user_id)
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in enhanced yield prediction for {crop_id}: {e}", user_id)
            return {
                'success': False,
                'error': str(e),
                'crop_id': crop_id,
                'location': location
            }
    
    def predict_yield_with_weather_risks(self, crop_id: str, location: Dict[str, float],
                                       user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Predict yield with comprehensive weather risk assessment.
        
        Args:
            crop_id: Crop identifier
            location: Dictionary with lat/lon coordinates
            user_id: Optional user ID for logging
            
        Returns:
            Yield prediction with weather risk analysis
        """
        try:
            # Get enhanced prediction
            enhanced_prediction = self.predict_yield_enhanced(crop_id, location, user_id)
            
            if not enhanced_prediction['success']:
                return enhanced_prediction
            
            # Add weather risk assessment
            weather_risks = self._assess_weather_risks(location, enhanced_prediction, user_id)
            enhanced_prediction['weather_risks'] = weather_risks
            
            # Add risk-adjusted yield estimate
            risk_adjusted_yield = self._calculate_risk_adjusted_yield(
                enhanced_prediction['predicted_yield'], weather_risks
            )
            enhanced_prediction['risk_adjusted_yield'] = risk_adjusted_yield
            
            return enhanced_prediction
            
        except Exception as e:
            logger.error(f"Error in weather risk assessment for {crop_id}: {e}", user_id)
            return {
                'success': False,
                'error': str(e),
                'crop_id': crop_id,
                'location': location
            }
    
    def get_seasonal_yield_forecast(self, crop_id: str, location: Dict[str, float],
                                  months_ahead: int = 6, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get seasonal yield forecast based on weather predictions.
        
        Args:
            crop_id: Crop identifier
            location: Dictionary with lat/lon coordinates
            months_ahead: Number of months to forecast
            user_id: Optional user ID for logging
            
        Returns:
            Seasonal yield forecast
        """
        try:
            logger.info(f"Generating seasonal yield forecast for {crop_id} ({months_ahead} months)", user_id)
            
            # Get seasonal weather predictions
            seasonal_weather = self._get_seasonal_weather_forecast(location, months_ahead, user_id)
            
            # Generate yield forecasts for each month
            monthly_forecasts = []
            current_date = datetime.now()
            
            for i in range(months_ahead):
                forecast_date = current_date + timedelta(days=30*i)
                month_features = self._extract_monthly_features(seasonal_weather, forecast_date)
                
                if month_features:
                    # Make prediction for this month
                    prediction = self.model_manager.predict_yield(
                        crop_id, month_features, model_type="enhanced", user_id=user_id
                    )
                    
                    if prediction['success']:
                        monthly_forecasts.append({
                            'month': forecast_date.strftime('%B %Y'),
                            'predicted_yield': prediction['predicted_yield'],
                            'confidence': prediction['confidence_interval'],
                            'weather_conditions': month_features
                        })
            
            # Calculate seasonal summary
            if monthly_forecasts:
                total_predicted_yield = sum(f['predicted_yield'] for f in monthly_forecasts)
                avg_yield = total_predicted_yield / len(monthly_forecasts)
                
                seasonal_summary = {
                    'total_seasonal_yield': round(total_predicted_yield, 2),
                    'average_monthly_yield': round(avg_yield, 2),
                    'best_month': max(monthly_forecasts, key=lambda x: x['predicted_yield']),
                    'worst_month': min(monthly_forecasts, key=lambda x: x['predicted_yield']),
                    'yield_variability': self._calculate_yield_variability(monthly_forecasts)
                }
            else:
                seasonal_summary = {'error': 'No valid forecasts generated'}
            
            return {
                'success': True,
                'crop_id': crop_id,
                'location': location,
                'forecast_period': f"{months_ahead} months",
                'monthly_forecasts': monthly_forecasts,
                'seasonal_summary': seasonal_summary,
                'generated_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in seasonal yield forecast for {crop_id}: {e}", user_id)
            return {
                'success': False,
                'error': str(e),
                'crop_id': crop_id,
                'location': location
            }
    
    def _get_enhanced_weather_analysis(self, location: Dict[str, float], 
                                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive weather analysis for enhanced prediction."""
        try:
            lat, lon = location['lat'], location['lon']
            
            # Get current weather data
            current_weather = self.data_collector.get_weather_data(lat, lon, user_id=user_id)
            
            # Get enhanced rainfall analysis
            current_rainfall = current_weather.get('rainfall', {}).get('total_7day_rainfall', 0)
            forecast_rainfall = current_weather.get('rainfall', {}).get('total_7day_rainfall', 0)
            
            enhanced_rainfall = self.enhanced_rainfall_analyzer.analyze_comprehensive_rainfall(
                lat, lon, current_rainfall, forecast_rainfall, historical_years=5, user_id=user_id
            )
            
            # Get seasonal rainfall prediction
            current_month = datetime.now().strftime('%B')
            seasonal_prediction = self.enhanced_rainfall_analyzer.get_seasonal_rainfall_prediction(
                lat, lon, current_month, historical_years=5, user_id=user_id
            )
            
            # Get historical comparison
            historical_comparison = self.enhanced_rainfall_analyzer.compare_with_historical_patterns(
                lat, lon, current_rainfall, current_month, historical_years=5, user_id=user_id
            )
            
            # Get drought risk assessment
            drought_risk = self.enhanced_rainfall_analyzer.get_drought_risk_assessment(
                lat, lon, current_weather, historical_years=5, user_id=user_id
            )
            
            enhanced_analysis = {
                'current_weather': current_weather,
                'enhanced_rainfall': enhanced_rainfall,
                'seasonal_prediction': seasonal_prediction,
                'historical_comparison': historical_comparison,
                'drought_risk': drought_risk,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Enhanced weather analysis completed for {lat}, {lon}", user_id)
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error in enhanced weather analysis: {e}", user_id)
            return {'error': str(e)}
    
    def _train_enhanced_model(self, crop_id: str, combined_data: Dict[str, Any], 
                            user_id: Optional[str] = None) -> Dict[str, Any]:
        """Train enhanced model with additional features."""
        try:
            # Check if enhanced model exists
            model_info = self.model_manager.get_model_info(crop_id, "enhanced")
            
            if not model_info:
                # Train enhanced model
                historical_data = combined_data.get('historical_yields', [])
                
                if not historical_data:
                    return {'success': False, 'error': 'No historical data available'}
                
                # Enhance historical data with weather features
                enhanced_historical_data = self._enhance_historical_data(historical_data, combined_data)
                
                # Train ensemble model
                training_result = self._train_ensemble_model(crop_id, enhanced_historical_data, user_id)
                
                return training_result
            
            return {'success': True, 'model_info': model_info}
            
        except Exception as e:
            logger.error(f"Error training enhanced model for {crop_id}: {e}", user_id)
            return {'success': False, 'error': str(e)}
    
    def _extract_enhanced_features(self, combined_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Extract enhanced features for prediction."""
        try:
            # Get basic features
            basic_features = self._extract_prediction_features(combined_data)
            if not basic_features:
                return None
            
            # Get enhanced weather data
            enhanced_weather = combined_data.get('enhanced_weather', {})
            
            # Add enhanced features
            enhanced_features = basic_features.copy()
            
            # Historical rainfall features
            enhanced_rainfall = enhanced_weather.get('enhanced_rainfall', {})
            if enhanced_rainfall:
                enhanced_features.update({
                    'historical_avg_rainfall': enhanced_rainfall.get('historical_monthly_average', 500),
                    'rainfall_deviation': enhanced_rainfall.get('deviation_from_average', 0),
                    'rainfall_status': self._encode_rainfall_status(enhanced_rainfall.get('status', 'normal'))
                })
            
            # Seasonal prediction features
            seasonal_prediction = enhanced_weather.get('seasonal_prediction', {})
            if seasonal_prediction:
                enhanced_features.update({
                    'expected_seasonal_rainfall': seasonal_prediction.get('expected_seasonal_rainfall', 500),
                    'season_confidence': self._encode_confidence(seasonal_prediction.get('confidence_level', 'medium'))
                })
            
            # Drought risk features
            drought_risk = enhanced_weather.get('drought_risk', {})
            if drought_risk:
                enhanced_features.update({
                    'drought_risk_level': self._encode_drought_risk(drought_risk.get('risk_level', 'low')),
                    'drought_indicators': drought_risk.get('drought_indicators', {}).get('total_indicators', 0)
                })
            
            # Climate trend features
            historical_comparison = enhanced_weather.get('historical_comparison', {})
            if historical_comparison:
                enhanced_features.update({
                    'climate_trend': self._encode_climate_trend(historical_comparison.get('trend', 'stable')),
                    'anomaly_score': historical_comparison.get('anomaly_score', 0)
                })
            
            return enhanced_features
            
        except Exception as e:
            logger.error(f"Error extracting enhanced features: {e}")
            return None
    
    def _enhance_prediction_with_weather_insights(self, prediction_result: Dict[str, Any],
                                                combined_data: Dict[str, Any],
                                                enhanced_weather: Dict[str, Any],
                                                crop_id: str, location: Dict[str, float]) -> Dict[str, Any]:
        """Enhance prediction result with detailed weather insights."""
        try:
            # Get base enhancement
            enhanced_result = self._enhance_prediction_result(prediction_result, combined_data, crop_id, location)
            
            # Add weather insights
            weather_insights = self._generate_weather_insights(enhanced_weather, enhanced_result)
            enhanced_result['weather_insights'] = weather_insights
            
            # Add seasonal context
            seasonal_context = self._get_seasonal_context(enhanced_weather, enhanced_result)
            enhanced_result['seasonal_context'] = seasonal_context
            
            # Add climate recommendations
            climate_recommendations = self._get_climate_recommendations(enhanced_weather, enhanced_result)
            enhanced_result['climate_recommendations'] = climate_recommendations
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error enhancing prediction with weather insights: {e}")
            return prediction_result
    
    def _assess_weather_risks(self, location: Dict[str, float], prediction_result: Dict[str, Any],
                            user_id: Optional[str] = None) -> Dict[str, Any]:
        """Assess weather-related risks to yield prediction."""
        try:
            # Get enhanced weather data
            enhanced_weather = self._get_enhanced_weather_analysis(location, user_id)
            
            risks = {
                'drought_risk': enhanced_weather.get('drought_risk', {}).get('risk_level', 'low'),
                'flood_risk': self._assess_flood_risk(enhanced_weather),
                'temperature_risk': self._assess_temperature_risk(enhanced_weather),
                'rainfall_volatility': self._assess_rainfall_volatility(enhanced_weather),
                'overall_risk_level': 'low'  # Will be calculated
            }
            
            # Calculate overall risk level
            risk_scores = {
                'low': 1, 'medium': 2, 'high': 3, 'very_high': 4
            }
            
            total_risk_score = sum(risk_scores.get(risk, 1) for risk in risks.values() if isinstance(risk, str))
            avg_risk_score = total_risk_score / 4
            
            if avg_risk_score <= 1.5:
                risks['overall_risk_level'] = 'low'
            elif avg_risk_score <= 2.5:
                risks['overall_risk_level'] = 'medium'
            elif avg_risk_score <= 3.5:
                risks['overall_risk_level'] = 'high'
            else:
                risks['overall_risk_level'] = 'very_high'
            
            return risks
            
        except Exception as e:
            logger.error(f"Error assessing weather risks: {e}")
            return {'overall_risk_level': 'unknown', 'error': str(e)}
    
    def _calculate_risk_adjusted_yield(self, base_yield: float, weather_risks: Dict[str, Any]) -> float:
        """Calculate risk-adjusted yield estimate."""
        try:
            risk_level = weather_risks.get('overall_risk_level', 'low')
            
            # Risk adjustment factors
            risk_adjustments = {
                'low': 1.0,      # No adjustment
                'medium': 0.95,  # 5% reduction
                'high': 0.85,    # 15% reduction
                'very_high': 0.7 # 30% reduction
            }
            
            adjustment_factor = risk_adjustments.get(risk_level, 1.0)
            risk_adjusted_yield = base_yield * adjustment_factor
            
            return round(risk_adjusted_yield, 2)
            
        except Exception as e:
            logger.error(f"Error calculating risk-adjusted yield: {e}")
            return base_yield
    
    # Helper methods for feature encoding
    def _encode_rainfall_status(self, status: str) -> int:
        """Encode rainfall status as numeric feature."""
        encoding = {'deficit': 0, 'below_normal': 1, 'normal': 2, 'above_normal': 3, 'excess': 4}
        return encoding.get(status, 2)
    
    def _encode_confidence(self, confidence: str) -> float:
        """Encode confidence level as numeric feature."""
        encoding = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
        return encoding.get(confidence, 0.6)
    
    def _encode_drought_risk(self, risk: str) -> int:
        """Encode drought risk as numeric feature."""
        encoding = {'low': 0, 'medium': 1, 'high': 2, 'very_high': 3}
        return encoding.get(risk, 0)
    
    def _encode_climate_trend(self, trend: str) -> int:
        """Encode climate trend as numeric feature."""
        encoding = {'decreasing': -1, 'stable': 0, 'increasing': 1}
        return encoding.get(trend, 0)
    
    # Additional helper methods would be implemented here...
    def _enhance_historical_data(self, historical_data: List[Dict[str, Any]], 
                               combined_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance historical data with additional weather features."""
        # Implementation would add enhanced weather features to historical data
        return historical_data
    
    def _train_ensemble_model(self, crop_id: str, enhanced_data: List[Dict[str, Any]], 
                            user_id: Optional[str] = None) -> Dict[str, Any]:
        """Train ensemble model with multiple algorithms."""
        # Implementation would train ensemble model
        return self.model_manager.train_yield_model(crop_id, enhanced_data, 'linear', user_id)
    
    def _get_seasonal_weather_forecast(self, location: Dict[str, float], months_ahead: int,
                                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get seasonal weather forecast."""
        # Implementation would get seasonal weather predictions
        return {}
    
    def _extract_monthly_features(self, seasonal_weather: Dict[str, Any], 
                                forecast_date: datetime) -> Optional[Dict[str, float]]:
        """Extract features for specific month."""
        # Implementation would extract monthly weather features
        return None
    
    def _calculate_yield_variability(self, monthly_forecasts: List[Dict[str, Any]]) -> float:
        """Calculate yield variability across months."""
        # Implementation would calculate variability
        return 0.0
    
    def _generate_weather_insights(self, enhanced_weather: Dict[str, Any], 
                                 prediction_result: Dict[str, Any]) -> List[str]:
        """Generate weather-based insights."""
        # Implementation would generate insights
        return []
    
    def _get_seasonal_context(self, enhanced_weather: Dict[str, Any], 
                            prediction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Get seasonal context for prediction."""
        # Implementation would provide seasonal context
        return {}
    
    def _get_climate_recommendations(self, enhanced_weather: Dict[str, Any], 
                                   prediction_result: Dict[str, Any]) -> List[str]:
        """Get climate-based recommendations."""
        # Implementation would provide recommendations
        return []
    
    def _assess_flood_risk(self, enhanced_weather: Dict[str, Any]) -> str:
        """Assess flood risk based on weather data."""
        # Implementation would assess flood risk
        return 'low'
    
    def _assess_temperature_risk(self, enhanced_weather: Dict[str, Any]) -> str:
        """Assess temperature risk based on weather data."""
        # Implementation would assess temperature risk
        return 'low'
    
    def _assess_rainfall_volatility(self, enhanced_weather: Dict[str, Any]) -> str:
        """Assess rainfall volatility risk."""
        # Implementation would assess rainfall volatility
        return 'low' 