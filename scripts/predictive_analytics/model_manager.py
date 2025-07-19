"""
Model Manager Module for Predictive Analytics.

Handles training, saving, loading, and managing ML models for yield prediction.
Uses simple regression models initially, with plans for more complex models later.
"""
import pickle
import os
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

from scripts.utils.logger import logger


class ModelManager:
    """Manages ML models for yield prediction."""
    
    def __init__(self, models_dir: str = "data/models"):
        """
        Initialize the model manager.
        
        Args:
            models_dir: Directory to store trained models
        """
        self.models_dir = models_dir
        self.scaler = StandardScaler()
        self.models = {}
        self.model_metadata = {}
        
        # Ensure models directory exists
        os.makedirs(models_dir, exist_ok=True)
        
        # Load existing models
        self._load_existing_models()
    
    def train_yield_model(self, crop_id: str, training_data: List[Dict[str, Any]], 
                         model_type: str = "linear", user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Train a yield prediction model for a specific crop.
        
        Args:
            crop_id: Crop identifier
            training_data: List of historical yield data with weather features
            model_type: Type of model ('linear', 'ridge', 'random_forest', 'enhanced', 'ensemble')
            user_id: Optional user ID for logging
            
        Returns:
            Dictionary containing training results and model info
        """
        try:
            if not training_data:
                logger.warning(f"No training data provided for {crop_id}", user_id)
                return {'success': False, 'error': 'No training data'}
            
            # Prepare features and target
            X, y = self._prepare_training_data(training_data, model_type)
            
            if len(X) < 10:  # Need minimum data points
                logger.warning(f"Insufficient training data for {crop_id}: {len(X)} samples", user_id)
                return {'success': False, 'error': 'Insufficient training data'}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model based on type
            if model_type == "enhanced":
                model = self._create_enhanced_model()
            elif model_type == "ensemble":
                model = self._create_ensemble_model()
            else:
                model = self._create_model(model_type)
            
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            metrics = self._calculate_metrics(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=3, scoring='r2')
            
            # Save model
            model_info = {
                'crop_id': crop_id,
                'model_type': model_type,
                'training_date': datetime.now().isoformat(),
                'n_samples': len(X),
                'n_features': X.shape[1] if len(X.shape) > 1 else 1,
                'metrics': metrics,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'feature_names': self._get_feature_names(model_type),
                'model_path': self._save_model(model, crop_id, model_type)
            }
            
            # Store model and metadata
            self.models[f"{crop_id}_{model_type}"] = model
            self.model_metadata[f"{crop_id}_{model_type}"] = model_info
            
            logger.info(f"Model trained for {crop_id} ({model_type}): R²={metrics['r2']:.3f}", user_id)
            return {'success': True, 'model_info': model_info}
            
        except Exception as e:
            logger.error(f"Error training model for {crop_id}: {e}", user_id)
            return {'success': False, 'error': str(e)}
    
    def predict_yield(self, crop_id: str, features: Dict[str, float], 
                     model_type: str = "linear", user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Make yield prediction using trained model.
        
        Args:
            crop_id: Crop identifier
            features: Dictionary of weather and crop features
            model_type: Type of model to use
            user_id: Optional user ID for logging
            
        Returns:
            Dictionary containing prediction and confidence
        """
        try:
            model_key = f"{crop_id}_{model_type}"
            
            if model_key not in self.models:
                logger.warning(f"No trained model found for {crop_id} ({model_type})", user_id)
                return {'success': False, 'error': 'Model not found'}
            
            # Prepare features
            feature_vector = self._prepare_prediction_features(features, model_type)
            if feature_vector is None:
                return {'success': False, 'error': 'Invalid features'}
            
            # Scale features
            feature_vector_scaled = self.scaler.transform([feature_vector])
            
            # Make prediction
            model = self.models[model_key]
            prediction = model.predict(feature_vector_scaled)[0]
            
            # Calculate confidence interval (simple approach)
            confidence = self._calculate_confidence(model_key, feature_vector_scaled)
            
            result = {
                'success': True,
                'predicted_yield': round(prediction, 2),
                'confidence_interval': confidence,
                'model_type': model_type,
                'crop_id': crop_id,
                'prediction_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Yield prediction for {crop_id}: {prediction:.2f} tons/ha", user_id)
            return result
            
        except Exception as e:
            logger.error(f"Error making prediction for {crop_id}: {e}", user_id)
            return {'success': False, 'error': str(e)}
    
    def get_model_info(self, crop_id: str, model_type: str = "linear") -> Optional[Dict[str, Any]]:
        """Get information about a trained model."""
        model_key = f"{crop_id}_{model_type}"
        return self.model_metadata.get(model_key)
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available trained models."""
        return list(self.model_metadata.values())
    
    def compare_models(self, crop_id: str, test_data: List[Dict[str, Any]], 
                      user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare performance of different model types for a crop.
        
        Args:
            crop_id: Crop identifier
            test_data: Test data for comparison
            user_id: Optional user ID for logging
            
        Returns:
            Model comparison results
        """
        try:
            model_types = ['linear', 'ridge', 'random_forest', 'enhanced', 'ensemble']
            comparison_results = {}
            
            for model_type in model_types:
                # Check if model exists
                model_key = f"{crop_id}_{model_type}"
                if model_key in self.models:
                    # Test model performance
                    X, y = self._prepare_training_data(test_data, model_type)
                    if len(X) > 0:
                        X_scaled = self.scaler.transform(X)
                        model = self.models[model_key]
                        y_pred = model.predict(X_scaled)
                        metrics = self._calculate_metrics(y, y_pred)
                        
                        comparison_results[model_type] = {
                            'r2_score': metrics['r2'],
                            'rmse': metrics['rmse'],
                            'mae': metrics['mae'],
                            'available': True
                        }
                    else:
                        comparison_results[model_type] = {'available': False, 'error': 'No test data'}
                else:
                    comparison_results[model_type] = {'available': False, 'error': 'Model not trained'}
            
            # Find best model
            best_model = None
            best_r2 = -1
            
            for model_type, results in comparison_results.items():
                if results.get('available') and results.get('r2_score', -1) > best_r2:
                    best_r2 = results['r2_score']
                    best_model = model_type
            
            return {
                'comparison_results': comparison_results,
                'best_model': best_model,
                'best_r2_score': best_r2,
                'crop_id': crop_id,
                'comparison_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error comparing models for {crop_id}: {e}", user_id)
            return {'error': str(e)}
    
    def _prepare_training_data(self, training_data: List[Dict[str, Any]], model_type: str = "linear") -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data into features and target arrays."""
        features = []
        targets = []
        
        for entry in training_data:
            # Extract weather features
            weather = entry.get('weather_data', {})
            
            if model_type in ["enhanced", "ensemble"]:
                # Enhanced features for advanced models
                feature_vector = self._extract_enhanced_features(weather, entry)
            else:
                # Basic features for simple models
                feature_vector = [
                    weather.get('avg_temperature', 25),
                    weather.get('total_rainfall', 500),
                    weather.get('rainy_days', 45),
                    weather.get('humidity', 60),
                    # Add season encoding (0 for dry, 1 for rainy)
                    1 if entry.get('season') == 'rainy' else 0
                ]
            
            features.append(feature_vector)
            targets.append(entry.get('yield_tons_ha', 0))
        
        return np.array(features), np.array(targets)
    
    def _extract_enhanced_features(self, weather: Dict[str, Any], entry: Dict[str, Any]) -> List[float]:
        """Extract enhanced features for advanced models."""
        # Basic features
        basic_features = [
            weather.get('avg_temperature', 25),
            weather.get('total_rainfall', 500),
            weather.get('rainy_days', 45),
            weather.get('humidity', 60),
            1 if entry.get('season') == 'rainy' else 0
        ]
        
        # Enhanced features (if available)
        enhanced_features = [
            weather.get('historical_avg_rainfall', 500),
            weather.get('rainfall_deviation', 0),
            weather.get('rainfall_status', 2),  # normal
            weather.get('expected_seasonal_rainfall', 500),
            weather.get('season_confidence', 0.6),
            weather.get('drought_risk_level', 0),
            weather.get('drought_indicators', 0),
            weather.get('climate_trend', 0),
            weather.get('anomaly_score', 0)
        ]
        
        return basic_features + enhanced_features
    
    def _prepare_prediction_features(self, features: Dict[str, float], model_type: str = "linear") -> Optional[np.ndarray]:
        """Prepare features for prediction."""
        try:
            if model_type in ["enhanced", "ensemble"]:
                # Enhanced features
                feature_vector = [
                    features.get('avg_temperature', 25),
                    features.get('total_rainfall', 500),
                    features.get('rainy_days', 45),
                    features.get('humidity', 60),
                    features.get('season_rainy', 0),
                    features.get('historical_avg_rainfall', 500),
                    features.get('rainfall_deviation', 0),
                    features.get('rainfall_status', 2),
                    features.get('expected_seasonal_rainfall', 500),
                    features.get('season_confidence', 0.6),
                    features.get('drought_risk_level', 0),
                    features.get('drought_indicators', 0),
                    features.get('climate_trend', 0),
                    features.get('anomaly_score', 0)
                ]
            else:
                # Basic features
                feature_vector = [
                    features.get('avg_temperature', 25),
                    features.get('total_rainfall', 500),
                    features.get('rainy_days', 45),
                    features.get('humidity', 60),
                    features.get('season_rainy', 0)  # 1 if rainy season, 0 if dry
                ]
            
            return np.array(feature_vector)
        except Exception as e:
            logger.error(f"Error preparing prediction features: {e}")
            return None
    
    def _create_model(self, model_type: str):
        """Create model instance based on type."""
        if model_type == "linear":
            return LinearRegression()
        elif model_type == "ridge":
            return Ridge(alpha=1.0)
        elif model_type == "random_forest":
            return RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            logger.warning(f"Unknown model type: {model_type}, using linear regression")
            return LinearRegression()
    
    def _create_enhanced_model(self):
        """Create enhanced model with better hyperparameters."""
        return RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
    
    def _create_ensemble_model(self):
        """Create ensemble model combining multiple algorithms."""
        models = [
            ('linear', LinearRegression()),
            ('ridge', Ridge(alpha=1.0)),
            ('random_forest', RandomForestRegressor(n_estimators=100, random_state=42))
        ]
        
        return VotingRegressor(estimators=models, weights=[0.2, 0.3, 0.5])
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate model performance metrics."""
        return {
            'mae': mean_absolute_error(y_true, y_pred),
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'r2': r2_score(y_true, y_pred)
        }
    
    def _calculate_confidence(self, model_key: str, features_scaled: np.ndarray) -> Dict[str, float]:
        """Calculate confidence interval for prediction."""
        try:
            # Simple confidence calculation based on model performance
            model_info = self.model_metadata.get(model_key, {})
            rmse = model_info.get('metrics', {}).get('rmse', 0.5)
            
            # 95% confidence interval (±2 * RMSE)
            margin = 2 * rmse
            
            return {
                'lower_bound': max(0, -margin),  # Yield can't be negative
                'upper_bound': margin,
                'confidence_level': 0.95
            }
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return {'lower_bound': 0, 'upper_bound': 1, 'confidence_level': 0.5}
    
    def _get_feature_names(self, model_type: str = "linear") -> List[str]:
        """Get list of feature names based on model type."""
        basic_features = ['avg_temperature', 'total_rainfall', 'rainy_days', 'humidity', 'season_rainy']
        
        if model_type in ["enhanced", "ensemble"]:
            enhanced_features = [
                'historical_avg_rainfall', 'rainfall_deviation', 'rainfall_status',
                'expected_seasonal_rainfall', 'season_confidence', 'drought_risk_level',
                'drought_indicators', 'climate_trend', 'anomaly_score'
            ]
            return basic_features + enhanced_features
        else:
            return basic_features
    
    def _save_model(self, model, crop_id: str, model_type: str) -> str:
        """Save trained model to file."""
        filename = f"{crop_id}_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        filepath = os.path.join(self.models_dir, filename)
        
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)
        
        return filepath
    
    def _load_existing_models(self) -> None:
        """Load existing trained models from disk."""
        try:
            for filename in os.listdir(self.models_dir):
                if filename.endswith('.pkl'):
                    filepath = os.path.join(self.models_dir, filename)
                    
                    with open(filepath, 'rb') as f:
                        model = pickle.load(f)
                    
                    # Extract model info from filename
                    parts = filename.replace('.pkl', '').split('_')
                    if len(parts) >= 2:
                        crop_id = parts[0]
                        model_type = parts[1]
                        model_key = f"{crop_id}_{model_type}"
                        
                        self.models[model_key] = model
                        
                        # Create basic metadata
                        self.model_metadata[model_key] = {
                            'crop_id': crop_id,
                            'model_type': model_type,
                            'model_path': filepath,
                            'loaded_date': datetime.now().isoformat()
                        }
            
            logger.info(f"Loaded {len(self.models)} existing models")
            
        except Exception as e:
            logger.error(f"Error loading existing models: {e}")
    
    def retrain_model(self, crop_id: str, new_data: List[Dict[str, Any]], 
                     model_type: str = "linear", user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrain model with new data.
        
        Args:
            crop_id: Crop identifier
            new_data: New training data
            model_type: Type of model to retrain
            user_id: Optional user ID for logging
            
        Returns:
            Training results
        """
        # Load existing training data
        existing_data = self._load_training_data(crop_id)
        
        # Combine with new data
        combined_data = existing_data + new_data
        
        # Retrain model
        return self.train_yield_model(crop_id, combined_data, model_type, user_id)
    
    def _load_training_data(self, crop_id: str) -> List[Dict[str, Any]]:
        """Load existing training data for a crop."""
        # This would typically load from a database or file
        # For now, return empty list
        return [] 