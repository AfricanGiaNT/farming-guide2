"""
Advanced Error Handling and Fallback System for Crop Recommendations.
Provides comprehensive error handling, fallbacks, and graceful degradation.
"""
import traceback
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime
from scripts.utils.logger import logger


class AdvancedErrorHandler:
    """
    Advanced error handling system for crop recommendations.
    Provides comprehensive error handling, fallbacks, and graceful degradation.
    """
    
    def __init__(self):
        """Initialize the advanced error handler."""
        self.error_counts = {}
        self.fallback_strategies = {}
        
        # Define fallback strategies
        self._setup_fallback_strategies()
        
        logger.info("Advanced Error Handler initialized")
    
    def _setup_fallback_strategies(self):
        """Setup fallback strategies for different error types."""
        self.fallback_strategies = {
            'weather_api_error': self._fallback_weather_data,
            'historical_data_error': self._fallback_historical_data,
            'crop_database_error': self._fallback_crop_database,
            'algorithm_error': self._fallback_algorithm,
            'cache_error': self._fallback_cache,
            'general_error': self._fallback_general
        }
    
    def handle_error(self, 
                    error: Exception, 
                    error_type: str, 
                    context: Dict[str, Any],
                    fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle errors with appropriate fallback strategies.
        
        Args:
            error: The exception that occurred
            error_type: Type of error for fallback strategy selection
            context: Context information about the request
            fallback_data: Optional fallback data to use
            
        Returns:
            Error response with fallback data if available
        """
        # Log the error
        self._log_error(error, error_type, context)
        
        # Track error counts
        self._track_error(error_type)
        
        # Get fallback strategy
        fallback_strategy = self.fallback_strategies.get(error_type, self.fallback_strategies['general_error'])
        
        # Execute fallback strategy
        try:
            fallback_result = fallback_strategy(context, fallback_data)
            return self._create_error_response(error, error_type, context, fallback_result)
        except Exception as fallback_error:
            logger.error(f"Fallback strategy failed: {fallback_error}")
            return self._create_critical_error_response(error, error_type, context)
    
    def _log_error(self, error: Exception, error_type: str, context: Dict[str, Any]):
        """Log error with context information."""
        error_id = f"{error_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.error(f"Error {error_id}: {error_type}")
        logger.error(f"Error message: {str(error)}")
        logger.error(f"Context: {context}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Store error ID in context for tracking
        context['error_id'] = error_id
    
    def _track_error(self, error_type: str):
        """Track error counts by type."""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
    
    def _fallback_weather_data(self, context: Dict[str, Any], fallback_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback strategy for weather API errors."""
        logger.info("Using fallback weather data")
        
        # Use default weather values
        fallback_weather = {
            'rainfall_mm': 400,  # Average rainfall for Malawi
            'temperature': 25,   # Average temperature for Malawi
            'humidity': 60,      # Average humidity
            'data_source': 'fallback_default_values',
            'fallback_reason': 'Weather API unavailable'
        }
        
        return fallback_weather
    
    def _fallback_historical_data(self, context: Dict[str, Any], fallback_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback strategy for historical data errors."""
        logger.info("Using fallback historical data")
        
        # Use default historical data
        fallback_historical = {
            'years_analyzed': 0,
            'average_annual_rainfall': 400,
            'rainfall_variability': 0.3,
            'climate_trend': 'stable',
            'drought_years': 0,
            'flood_years': 0,
            'data_quality': 'fallback',
            'data_source': 'fallback_default_values',
            'fallback_reason': 'Historical data API unavailable'
        }
        
        return fallback_historical
    
    def _fallback_crop_database(self, context: Dict[str, Any], fallback_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback strategy for crop database errors."""
        logger.info("Using fallback crop database")
        
        # Use basic crop recommendations
        fallback_crops = [
            {
                'crop_id': 'maize',
                'crop_name': 'Maize',
                'suitability_score': 0.8,
                'confidence': 0.6,
                'recommendation_level': 'good',
                'data_source': 'fallback_basic_recommendations',
                'fallback_reason': 'Crop database unavailable'
            },
            {
                'crop_id': 'beans',
                'crop_name': 'Beans',
                'suitability_score': 0.7,
                'confidence': 0.6,
                'recommendation_level': 'good',
                'data_source': 'fallback_basic_recommendations',
                'fallback_reason': 'Crop database unavailable'
            }
        ]
        
        return {
            'recommendations': fallback_crops,
            'data_source': 'fallback_basic_recommendations',
            'fallback_reason': 'Crop database unavailable'
        }
    
    def _fallback_algorithm(self, context: Dict[str, Any], fallback_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback strategy for algorithm errors."""
        logger.info("Using fallback algorithm")
        
        # Use simple scoring based on basic factors
        lat = context.get('lat', -13.9626)
        lon = context.get('lon', 33.7741)
        season = context.get('season', 'current')
        rainfall_mm = context.get('rainfall_mm', 400)
        temperature = context.get('temperature', 25)
        
        # Simple scoring logic
        basic_crops = [
            {'name': 'Maize', 'score': 0.8},
            {'name': 'Beans', 'score': 0.7},
            {'name': 'Groundnuts', 'score': 0.6}
        ]
        
        # Adjust scores based on basic factors
        for crop in basic_crops:
            if rainfall_mm < 300:
                crop['score'] *= 0.8  # Reduce score for low rainfall
            elif rainfall_mm > 600:
                crop['score'] *= 0.9  # Slight reduction for high rainfall
            
            if temperature < 20 or temperature > 35:
                crop['score'] *= 0.8  # Reduce score for extreme temperatures
        
        return {
            'recommendations': basic_crops,
            'data_source': 'fallback_simple_algorithm',
            'fallback_reason': 'Advanced algorithm unavailable'
        }
    
    def _fallback_cache(self, context: Dict[str, Any], fallback_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback strategy for cache errors."""
        logger.info("Using fallback cache strategy")
        
        # Return None to indicate cache is not available
        return {
            'cache_available': False,
            'data_source': 'fallback_no_cache',
            'fallback_reason': 'Cache system unavailable'
        }
    
    def _fallback_general(self, context: Dict[str, Any], fallback_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """General fallback strategy for unknown errors."""
        logger.info("Using general fallback strategy")
        
        return {
            'status': 'error',
            'message': 'Service temporarily unavailable',
            'data_source': 'fallback_general',
            'fallback_reason': 'General system error'
        }
    
    def _create_error_response(self, 
                              error: Exception, 
                              error_type: str, 
                              context: Dict[str, Any],
                              fallback_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create error response with fallback data."""
        return {
            'status': 200,  # Still return 200 but with error information
            'data': fallback_result,
            'errors': [
                {
                    'type': error_type,
                    'message': str(error),
                    'error_id': context.get('error_id', 'unknown'),
                    'fallback_used': True,
                    'fallback_reason': fallback_result.get('fallback_reason', 'Unknown')
                }
            ],
            'warning': f'Service degraded due to {error_type}. Using fallback data.',
            'data_sources': fallback_result.get('data_source', 'fallback_unknown')
        }
    
    def _create_critical_error_response(self, 
                                      error: Exception, 
                                      error_type: str, 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Create critical error response when fallback also fails."""
        return {
            'status': 500,
            'error': {
                'type': error_type,
                'message': 'Service temporarily unavailable',
                'error_id': context.get('error_id', 'unknown'),
                'fallback_failed': True
            },
            'data': None,
            'errors': [
                {
                    'type': 'critical_error',
                    'message': 'Service unavailable - all systems down',
                    'error_id': context.get('error_id', 'unknown'),
                    'fallback_used': False
                }
            ]
        }
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        total_errors = sum(self.error_counts.values())
        
        return {
            'total_errors': total_errors,
            'error_counts': self.error_counts,
            'error_rate': total_errors / max(1, total_errors),  # Placeholder calculation
            'fallback_strategies_available': list(self.fallback_strategies.keys())
        }
    
    def reset_error_stats(self):
        """Reset error statistics."""
        self.error_counts = {}
        logger.info("Error statistics reset")


# Create global instance
advanced_error_handler = AdvancedErrorHandler()
