"""
Data Quality Validation System for Crop Recommendations.
Ensures data quality and consistency across all components.
"""
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from scripts.utils.logger import logger


class DataQualityValidator:
    """
    Data quality validation system for crop recommendations.
    Ensures data quality and consistency across all components.
    """
    
    def __init__(self):
        """Initialize the data quality validator."""
        self.validation_rules = self._setup_validation_rules()
        self.quality_metrics = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            'quality_score': 0.0
        }
        
        logger.info("Data Quality Validator initialized")
    
    def _setup_validation_rules(self) -> Dict[str, Any]:
        """Setup data quality validation rules."""
        return {
            'crop_recommendations': {
                'required_fields': [
                    'crop_id', 'crop_name', 'suitability_score', 'confidence',
                    'recommendation_level', 'top_varieties', 'yield_projections',
                    'input_recommendations', 'planting_guidelines', 'data_sources'
                ],
                'score_ranges': {
                    'suitability_score': (0.0, 1.0),
                    'confidence': (0.0, 1.0)
                },
                'min_varieties': 1,
                'max_varieties': 3
            },
            'yield_projections': {
                'required_fields': ['conservative', 'realistic', 'potential', 'optimal'],
                'value_ranges': {
                    'conservative': (0.0, 50.0),
                    'realistic': (0.0, 50.0),
                    'potential': (0.0, 50.0),
                    'optimal': (0.0, 50.0)
                },
                'progression_order': ['conservative', 'realistic', 'potential', 'optimal']
            },
            'input_recommendations': {
                'required_sections': [
                    'fertilizer_recommendations', 'seed_recommendations',
                    'pest_control_recommendations', 'total_input_costs'
                ],
                'cost_validation': {
                    'min_cost': 0,
                    'max_cost': 1000000  # 1M MK
                }
            },
            'varieties': {
                'required_fields': ['name', 'suitability_score', 'source'],
                'score_range': (0.0, 1.0),
                'source_validation': 'real_crop_varieties_database'
            },
            'data_sources': {
                'required_sources': [
                    'real_crop_varieties_database',
                    'real_historical_weather_data',
                    'advanced_crop_algorithm',
                    'advanced_yield_calculator',
                    'advanced_input_system'
                ],
                'forbidden_sources': [
                    'mock_data', 'sample_data', 'test_data', 'dummy_data'
                ]
            }
        }
    
    def validate_crop_recommendations(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate crop recommendations data quality.
        
        Args:
            recommendations: List of crop recommendations to validate
            
        Returns:
            Validation result with quality metrics
        """
        logger.info(f"Validating {len(recommendations)} crop recommendations")
        
        validation_results = {
            'total_recommendations': len(recommendations),
            'valid_recommendations': 0,
            'invalid_recommendations': 0,
            'validation_errors': [],
            'quality_score': 0.0
        }
        
        rules = self.validation_rules['crop_recommendations']
        
        for i, rec in enumerate(recommendations):
            rec_validation = self._validate_single_recommendation(rec, rules)
            
            if rec_validation['valid']:
                validation_results['valid_recommendations'] += 1
            else:
                validation_results['invalid_recommendations'] += 1
                validation_results['validation_errors'].extend([
                    f"Recommendation {i}: {error}" for error in rec_validation['errors']
                ])
        
        # Calculate quality score
        if validation_results['total_recommendations'] > 0:
            validation_results['quality_score'] = (
                validation_results['valid_recommendations'] / 
                validation_results['total_recommendations']
            )
        
        # Update global metrics
        self._update_quality_metrics(validation_results)
        
        return validation_results
    
    def _validate_single_recommendation(self, rec: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single crop recommendation."""
        errors = []
        
        # Check required fields
        for field in rules['required_fields']:
            if field not in rec:
                errors.append(f"Missing required field: {field}")
        
        # Validate score ranges
        for score_field, (min_val, max_val) in rules['score_ranges'].items():
            if score_field in rec:
                score = rec[score_field]
                if not isinstance(score, (int, float)) or not (min_val <= score <= max_val):
                    errors.append(f"Invalid {score_field}: {score} (expected {min_val}-{max_val})")
        
        # Validate varieties
        if 'top_varieties' in rec:
            varieties = rec['top_varieties']
            if not isinstance(varieties, list):
                errors.append("top_varieties must be a list")
            else:
                if len(varieties) < rules['min_varieties']:
                    errors.append(f"Too few varieties: {len(varieties)} (minimum: {rules['min_varieties']})")
                if len(varieties) > rules['max_varieties']:
                    errors.append(f"Too many varieties: {len(varieties)} (maximum: {rules['max_varieties']})")
                
                # Validate each variety
                for j, variety in enumerate(varieties):
                    variety_errors = self._validate_variety(variety)
                    if variety_errors:
                        errors.extend([f"Variety {j}: {error}" for error in variety_errors])
        
        # Validate yield projections
        if 'yield_projections' in rec:
            yield_errors = self._validate_yield_projections(rec['yield_projections'])
            if yield_errors:
                errors.extend([f"Yield projections: {error}" for error in yield_errors])
        
        # Validate input recommendations
        if 'input_recommendations' in rec:
            input_errors = self._validate_input_recommendations(rec['input_recommendations'])
            if input_errors:
                errors.extend([f"Input recommendations: {error}" for error in input_errors])
        
        # Validate data sources
        if 'data_sources' in rec:
            source_errors = self._validate_data_sources(rec['data_sources'])
            if source_errors:
                errors.extend([f"Data sources: {error}" for error in source_errors])
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _validate_variety(self, variety: Dict[str, Any]) -> List[str]:
        """Validate a single variety."""
        errors = []
        rules = self.validation_rules['varieties']
        
        # Check required fields
        for field in rules['required_fields']:
            if field not in variety:
                errors.append(f"Missing required field: {field}")
        
        # Validate suitability score
        if 'suitability_score' in variety:
            score = variety['suitability_score']
            min_val, max_val = rules['score_range']
            if not isinstance(score, (int, float)) or not (min_val <= score <= max_val):
                errors.append(f"Invalid suitability_score: {score} (expected {min_val}-{max_val})")
        
        # Validate source
        if 'source' in variety:
            if variety['source'] != rules['source_validation']:
                errors.append(f"Invalid source: {variety['source']} (expected: {rules['source_validation']})")
        
        return errors
    
    def _validate_yield_projections(self, projections: Dict[str, Any]) -> List[str]:
        """Validate yield projections."""
        errors = []
        rules = self.validation_rules['yield_projections']
        
        # Check required fields
        for field in rules['required_fields']:
            if field not in projections:
                errors.append(f"Missing required field: {field}")
        
        # Validate value ranges
        for field, (min_val, max_val) in rules['value_ranges'].items():
            if field in projections:
                value = projections[field]
                if not isinstance(value, (int, float)) or not (min_val <= value <= max_val):
                    errors.append(f"Invalid {field}: {value} (expected {min_val}-{max_val})")
        
        # Validate progression order
        progression = rules['progression_order']
        for i in range(len(progression) - 1):
            current_field = progression[i]
            next_field = progression[i + 1]
            
            if current_field in projections and next_field in projections:
                current_val = projections[current_field]
                next_val = projections[next_field]
                
                if current_val > next_val:
                    errors.append(f"Invalid progression: {current_field} ({current_val}) > {next_field} ({next_val})")
        
        return errors
    
    def _validate_input_recommendations(self, input_recs: Dict[str, Any]) -> List[str]:
        """Validate input recommendations."""
        errors = []
        rules = self.validation_rules['input_recommendations']
        
        # Check required sections
        for section in rules['required_sections']:
            if section not in input_recs:
                errors.append(f"Missing required section: {section}")
        
        # Validate costs
        if 'total_input_costs' in input_recs:
            costs = input_recs['total_input_costs']
            if isinstance(costs, dict) and 'total_cost' in costs:
                cost_str = costs['total_cost']
                # Extract numeric value from cost string
                try:
                    cost_value = float(cost_str.replace('MK ', '').replace(',', '').split('/')[0])
                    min_cost, max_cost = rules['cost_validation']['min_cost'], rules['cost_validation']['max_cost']
                    if not (min_cost <= cost_value <= max_cost):
                        errors.append(f"Invalid total cost: {cost_value} (expected {min_cost}-{max_cost})")
                except (ValueError, IndexError):
                    errors.append(f"Invalid cost format: {cost_str}")
        
        return errors
    
    def _validate_data_sources(self, sources: List[str]) -> List[str]:
        """Validate data sources."""
        errors = []
        rules = self.validation_rules['data_sources']
        
        # Check required sources
        for required_source in rules['required_sources']:
            if required_source not in sources:
                errors.append(f"Missing required data source: {required_source}")
        
        # Check forbidden sources
        for forbidden_source in rules['forbidden_sources']:
            if forbidden_source in sources:
                errors.append(f"Forbidden data source found: {forbidden_source}")
        
        return errors
    
    def _update_quality_metrics(self, validation_results: Dict[str, Any]):
        """Update global quality metrics."""
        self.quality_metrics['total_validations'] += 1
        
        if validation_results['quality_score'] >= 0.9:
            self.quality_metrics['passed_validations'] += 1
        else:
            self.quality_metrics['failed_validations'] += 1
        
        # Update overall quality score
        if self.quality_metrics['total_validations'] > 0:
            self.quality_metrics['quality_score'] = (
                self.quality_metrics['passed_validations'] / 
                self.quality_metrics['total_validations']
            )
    
    def validate_data_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data consistency across the entire system.
        
        Args:
            data: Complete system data to validate
            
        Returns:
            Consistency validation result
        """
        logger.info("Validating data consistency across system")
        
        consistency_results = {
            'consistent': True,
            'inconsistencies': [],
            'consistency_score': 0.0
        }
        
        # Check algorithm version consistency
        if 'data' in data and 'recommendations' in data['data']:
            recommendations = data['data']['recommendations']
            algorithm_versions = set()
            
            for rec in recommendations:
                if 'algorithm_version' in rec:
                    algorithm_versions.add(rec['algorithm_version'])
            
            if len(algorithm_versions) > 1:
                consistency_results['inconsistencies'].append(
                    f"Multiple algorithm versions found: {list(algorithm_versions)}"
                )
                consistency_results['consistent'] = False
        
        # Check data source consistency
        if 'data' in data and 'data_sources' in data['data']:
            main_sources = set(data['data']['data_sources'])
            
            for rec in recommendations:
                if 'data_sources' in rec:
                    rec_sources = set(rec['data_sources'])
                    if not rec_sources.issubset(main_sources):
                        missing_sources = rec_sources - main_sources
                        consistency_results['inconsistencies'].append(
                            f"Recommendation has additional data sources: {list(missing_sources)}"
                        )
                        consistency_results['consistent'] = False
        
        # Calculate consistency score
        if consistency_results['inconsistencies']:
            consistency_results['consistency_score'] = max(0, 1.0 - len(consistency_results['inconsistencies']) * 0.2)
        else:
            consistency_results['consistency_score'] = 1.0
        
        return consistency_results
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive data quality report."""
        return {
            'quality_metrics': self.quality_metrics,
            'validation_rules': self.validation_rules,
            'quality_status': self._get_quality_status(),
            'recommendations': self._get_quality_recommendations()
        }
    
    def _get_quality_status(self) -> str:
        """Get overall quality status."""
        quality_score = self.quality_metrics['quality_score']
        
        if quality_score >= 0.95:
            return 'excellent'
        elif quality_score >= 0.9:
            return 'good'
        elif quality_score >= 0.8:
            return 'fair'
        elif quality_score >= 0.7:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def _get_quality_recommendations(self) -> List[str]:
        """Get quality improvement recommendations."""
        recommendations = []
        quality_score = self.quality_metrics['quality_score']
        
        if quality_score < 0.9:
            recommendations.append("Improve data validation rules")
        
        if quality_score < 0.8:
            recommendations.append("Enhance error handling in data processing")
        
        if quality_score < 0.7:
            recommendations.append("Review data sources for consistency")
        
        return recommendations


# Create global instance
data_quality_validator = DataQualityValidator()
