"""
Yield Predictor Module for Predictive Analytics.

Core yield prediction engine that uses weather data and ML models
to predict crop yields for agricultural planning.
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np

from .data_collector import DataCollector
from .model_manager import ModelManager
from scripts.utils.logger import logger


class YieldPredictor:
    """Core yield prediction engine for agricultural planning."""
    
    def __init__(self):
        """Initialize the yield predictor with required components."""
        self.data_collector = DataCollector()
        self.model_manager = ModelManager()
        
    def predict_yield(self, crop_id: str, location: Dict[str, float], 
                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Predict crop yield for a specific location and crop.
        
        Args:
            crop_id: Crop identifier (e.g., 'maize', 'beans')
            location: Dictionary with lat/lon coordinates
            user_id: Optional user ID for logging
            
        Returns:
            Dictionary containing yield prediction and confidence
        """
        try:
            logger.info(f"Starting yield prediction for {crop_id} at {location}", user_id)
            
            # Step 1: Collect all relevant data
            combined_data = self.data_collector.get_combined_data(crop_id, location, user_id)
            
            if not combined_data:
                return {
                    'success': False,
                    'error': 'Failed to collect required data',
                    'crop_id': crop_id,
                    'location': location
                }
            
            # Step 2: Check if we have a trained model
            model_info = self.model_manager.get_model_info(crop_id)
            
            if not model_info:
                # Step 3: Train model if not available
                logger.info(f"No trained model found for {crop_id}, training new model", user_id)
                training_result = self._train_model_for_crop(crop_id, combined_data, user_id)
                
                if not training_result['success']:
                    return {
                        'success': False,
                        'error': f"Failed to train model: {training_result.get('error', 'Unknown error')}",
                        'crop_id': crop_id,
                        'location': location
                    }
            
            # Step 4: Prepare features for prediction
            prediction_features = self._extract_prediction_features(combined_data)
            
            if not prediction_features:
                return {
                    'success': False,
                    'error': 'Failed to extract prediction features',
                    'crop_id': crop_id,
                    'location': location
                }
            
            # Step 5: Make prediction
            prediction_result = self.model_manager.predict_yield(
                crop_id, prediction_features, user_id=user_id
            )
            
            if not prediction_result['success']:
                return {
                    'success': False,
                    'error': f"Prediction failed: {prediction_result.get('error', 'Unknown error')}",
                    'crop_id': crop_id,
                    'location': location
                }
            
            # Step 6: Enhance prediction with additional insights
            enhanced_result = self._enhance_prediction_result(
                prediction_result, combined_data, crop_id, location
            )
            
            logger.info(f"Yield prediction completed for {crop_id}: {enhanced_result['predicted_yield']} tons/ha", user_id)
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in yield prediction for {crop_id}: {e}", user_id)
            return {
                'success': False,
                'error': str(e),
                'crop_id': crop_id,
                'location': location
            }
    
    def predict_yield_with_confidence(self, crop_id: str, location: Dict[str, float],
                                    confidence_level: float = 0.95, 
                                    user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Predict yield with detailed confidence analysis.
        
        Args:
            crop_id: Crop identifier
            location: Dictionary with lat/lon coordinates
            confidence_level: Desired confidence level (0.90, 0.95, 0.99)
            user_id: Optional user ID for logging
            
        Returns:
            Dictionary with prediction and detailed confidence analysis
        """
        try:
            # Get base prediction
            base_prediction = self.predict_yield(crop_id, location, user_id)
            
            if not base_prediction['success']:
                return base_prediction
            
            # Enhance with confidence analysis
            confidence_analysis = self._analyze_prediction_confidence(
                base_prediction, confidence_level
            )
            
            # Add confidence analysis to result
            base_prediction['confidence_analysis'] = confidence_analysis
            base_prediction['confidence_level'] = confidence_level
            
            return base_prediction
            
        except Exception as e:
            logger.error(f"Error in confidence analysis for {crop_id}: {e}", user_id)
            return {
                'success': False,
                'error': str(e),
                'crop_id': crop_id,
                'location': location
            }
    
    def get_yield_trends(self, crop_id: str, location: Dict[str, float], 
                        years: int = 5, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze yield trends over multiple years.
        
        Args:
            crop_id: Crop identifier
            location: Dictionary with lat/lon coordinates
            years: Number of years to analyze
            user_id: Optional user ID for logging
            
        Returns:
            Dictionary with yield trend analysis
        """
        try:
            # Get historical data
            historical_data = self.data_collector.load_mock_data(crop_id)
            
            if not historical_data:
                return {
                    'success': False,
                    'error': 'No historical data available',
                    'crop_id': crop_id
                }
            
            # Filter by location and years
            filtered_data = self._filter_historical_data(historical_data, location, years)
            
            if not filtered_data:
                return {
                    'success': False,
                    'error': 'No historical data for specified location and period',
                    'crop_id': crop_id,
                    'location': location
                }
            
            # Calculate trends
            trend_analysis = self._calculate_yield_trends(filtered_data)
            
            return {
                'success': True,
                'crop_id': crop_id,
                'location': location,
                'trend_analysis': trend_analysis,
                'historical_data': filtered_data
            }
            
        except Exception as e:
            logger.error(f"Error analyzing yield trends for {crop_id}: {e}", user_id)
            return {
                'success': False,
                'error': str(e),
                'crop_id': crop_id,
                'location': location
            }
    
    def _train_model_for_crop(self, crop_id: str, combined_data: Dict[str, Any], 
                             user_id: Optional[str] = None) -> Dict[str, Any]:
        """Train a model for a specific crop using available data."""
        try:
            historical_data = combined_data.get('historical_yields', [])
            
            if not historical_data:
                logger.warning(f"No historical data available for {crop_id}", user_id)
                return {'success': False, 'error': 'No historical data available'}
            
            # Train model
            training_result = self.model_manager.train_yield_model(
                crop_id, historical_data, model_type="linear", user_id=user_id
            )
            
            return training_result
            
        except Exception as e:
            logger.error(f"Error training model for {crop_id}: {e}", user_id)
            return {'success': False, 'error': str(e)}
    
    def _extract_prediction_features(self, combined_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Extract features from combined data for prediction."""
        try:
            weather_data = combined_data.get('weather', {})
            current_weather = weather_data.get('current', {})
            rainfall_data = weather_data.get('rainfall', {})
            
            # Extract current weather features
            features = {
                'avg_temperature': current_weather.get('temperature', 25),
                'total_rainfall': rainfall_data.get('total_7day_rainfall', 500),
                'rainy_days': rainfall_data.get('rainy_days_forecast', 45),
                'humidity': current_weather.get('humidity', 60),
                'season_rainy': self._determine_season_encoding()
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting prediction features: {e}")
            return None
    
    def _determine_season_encoding(self) -> int:
        """Determine if current period is rainy season (1) or dry season (0)."""
        current_month = datetime.now().month
        
        # Simple season determination for Malawi
        # Rainy season: November to April (months 11, 12, 1, 2, 3, 4)
        # Dry season: May to October (months 5, 6, 7, 8, 9, 10)
        rainy_months = [11, 12, 1, 2, 3, 4]
        
        return 1 if current_month in rainy_months else 0
    
    def _enhance_prediction_result(self, prediction_result: Dict[str, Any], 
                                 combined_data: Dict[str, Any], crop_id: str, 
                                 location: Dict[str, float]) -> Dict[str, Any]:
        """Enhance prediction result with additional insights."""
        try:
            # Get crop information
            crop_data = combined_data.get('crop', {})
            crop_info = crop_data.get('crop_info', {})
            
            # Calculate additional metrics
            predicted_yield = prediction_result['predicted_yield']
            base_yield = crop_info.get('yield_characteristics', {}).get('average_yield_ha', 2.5)
            
            # Calculate yield performance relative to average
            yield_performance = (predicted_yield / base_yield) if base_yield > 0 else 1.0
            
            # Determine yield category
            if yield_performance >= 1.2:
                yield_category = "excellent"
            elif yield_performance >= 1.0:
                yield_category = "good"
            elif yield_performance >= 0.8:
                yield_category = "fair"
            else:
                yield_category = "poor"
            
            # Add enhancements to result
            enhanced_result = prediction_result.copy()
            enhanced_result.update({
                'yield_performance': round(yield_performance, 2),
                'yield_category': yield_category,
                'base_yield': base_yield,
                'crop_name': crop_info.get('name', crop_id),
                'location_name': combined_data.get('weather', {}).get('current', {}).get('location', f"{location['lat']}, {location['lon']}"),
                'prediction_date': datetime.now().isoformat()
            })
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error enhancing prediction result: {e}")
            return prediction_result
    
    def _analyze_prediction_confidence(self, prediction_result: Dict[str, Any], 
                                     confidence_level: float) -> Dict[str, Any]:
        """Analyze prediction confidence in detail."""
        try:
            confidence_interval = prediction_result.get('confidence_interval', {})
            predicted_yield = prediction_result.get('predicted_yield', 0)
            
            # Calculate confidence bounds
            lower_bound = predicted_yield - confidence_interval.get('lower_bound', 0)
            upper_bound = predicted_yield + confidence_interval.get('upper_bound', 0)
            
            # Calculate confidence range
            confidence_range = upper_bound - lower_bound
            
            # Determine confidence quality
            if confidence_range < predicted_yield * 0.1:
                confidence_quality = "high"
            elif confidence_range < predicted_yield * 0.2:
                confidence_quality = "medium"
            else:
                confidence_quality = "low"
            
            return {
                'confidence_level': confidence_level,
                'lower_bound': round(lower_bound, 2),
                'upper_bound': round(upper_bound, 2),
                'confidence_range': round(confidence_range, 2),
                'confidence_quality': confidence_quality,
                'prediction_accuracy': confidence_interval.get('confidence_level', 0.95)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing prediction confidence: {e}")
            return {
                'confidence_level': confidence_level,
                'confidence_quality': 'unknown',
                'error': str(e)
            }
    
    def _filter_historical_data(self, historical_data: List[Dict[str, Any]], 
                               location: Dict[str, float], years: int) -> List[Dict[str, Any]]:
        """Filter historical data by location and time period."""
        try:
            current_year = datetime.now().year
            cutoff_year = current_year - years
            
            filtered_data = []
            
            for entry in historical_data:
                entry_location = entry.get('location', {})
                entry_year = entry.get('year', 0)
                
                # Check location match (simple coordinate comparison)
                lat_match = abs(entry_location.get('lat', 0) - location['lat']) < 0.1
                lon_match = abs(entry_location.get('lon', 0) - location['lon']) < 0.1
                
                # Check year range
                year_match = entry_year >= cutoff_year
                
                if lat_match and lon_match and year_match:
                    filtered_data.append(entry)
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error filtering historical data: {e}")
            return []
    
    def _calculate_yield_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate yield trends from historical data."""
        try:
            if not historical_data:
                return {'error': 'No data available'}
            
            # Sort by year
            sorted_data = sorted(historical_data, key=lambda x: x.get('year', 0))
            
            years = [entry.get('year', 0) for entry in sorted_data]
            yields = [entry.get('yield_tons_ha', 0) for entry in sorted_data]
            
            if len(yields) < 2:
                return {'error': 'Insufficient data for trend analysis'}
            
            # Calculate basic statistics
            avg_yield = np.mean(yields)
            std_yield = np.std(yields)
            min_yield = min(yields)
            max_yield = max(yields)
            
            # Calculate trend (simple linear regression)
            if len(years) > 1:
                trend_coefficient = np.polyfit(years, yields, 1)[0]
                trend_direction = "increasing" if trend_coefficient > 0 else "decreasing"
                trend_strength = abs(trend_coefficient)
            else:
                trend_coefficient = 0
                trend_direction = "stable"
                trend_strength = 0
            
            return {
                'years_analyzed': len(years),
                'average_yield': round(avg_yield, 2),
                'yield_std': round(std_yield, 2),
                'min_yield': round(min_yield, 2),
                'max_yield': round(max_yield, 2),
                'trend_coefficient': round(trend_coefficient, 3),
                'trend_direction': trend_direction,
                'trend_strength': round(trend_strength, 3),
                'data_points': len(yields)
            }
            
        except Exception as e:
            logger.error(f"Error calculating yield trends: {e}")
            return {'error': str(e)} 