#!/usr/bin/env python3
"""
Test suite for Week 5 Enhanced Recommendations
Agricultural Advisor Bot - Enhanced crop recommendation system
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from scripts.crop_advisor.enhanced_recommendation_engine import EnhancedRecommendationEngine
from scripts.crop_advisor.confidence_scorer import ConfidenceScorer
from scripts.crop_advisor.planting_calendar import PlantingCalendar
from scripts.crop_advisor.pdf_enhanced_varieties import PDFEnhancedVarieties


class TestEnhancedRecommendationEngine:
    """Test enhanced recommendation engine with 10-factor scoring"""
    
    def setup_method(self):
        """Set up test environment"""
        self.engine = EnhancedRecommendationEngine()
        self.sample_weather_data = {
            'temperature': 25,
            'humidity': 65,
            'pressure': 1013,
            'wind_speed': 10
        }
        self.sample_rainfall_data = {
            'total_7day_rainfall': 45,
            'forecast_7day_rainfall': 30,
            'rainy_days_forecast': 4
        }
    
    def test_enhanced_scoring_has_10_factors(self):
        """Test that enhanced scoring includes all 10 factors"""
        # This test will fail initially - we need to implement enhanced scoring
        recommendations = self.engine.generate_recommendations(
            self.sample_rainfall_data, 
            self.sample_weather_data, 
            -13.9833, 
            33.7833
        )
        
        # Check that recommendations include enhanced scoring
        assert 'recommendations' in recommendations
        assert len(recommendations['recommendations']) > 0
        
        # Check that scoring includes all 10 factors
        first_crop = recommendations['recommendations'][0]
        assert 'score_components' in first_crop
        
        expected_factors = [
            'rainfall_score', 'temperature_score', 'seasonal_score', 
            'humidity_score', 'timing_score', 'drought_tolerance_score',
            'soil_suitability_score', 'market_demand_score', 
            'input_availability_score', 'climate_trend_score'
        ]
        
        for factor in expected_factors:
            assert factor in first_crop['score_components']
    
    def test_enhanced_total_score_calculation(self):
        """Test that enhanced total score is calculated correctly"""
        recommendations = self.engine.generate_recommendations(
            self.sample_rainfall_data, 
            self.sample_weather_data, 
            -13.9833, 
            33.7833
        )
        
        first_crop = recommendations['recommendations'][0]
        score_components = first_crop['score_components']
        
        # Total score should be sum of all 10 factors (max 125 points)
        expected_total = sum(score_components.values())
        assert first_crop['total_score'] == expected_total
        assert first_crop['total_score'] <= 125  # Max possible score
    
    def test_soil_suitability_scoring(self):
        """Test soil suitability scoring based on crop requirements"""
        # Mock soil data - fix the method name with underscore
        with patch.object(self.engine, '_get_soil_data') as mock_soil:
            mock_soil.return_value = {
                'ph': 6.5,
                'fertility': 'medium',
                'drainage': 'well_drained'
            }
            
            recommendations = self.engine.generate_recommendations(
                self.sample_rainfall_data, 
                self.sample_weather_data, 
                -13.9833, 
                33.7833
            )
            
            # Should have soil suitability score
            first_crop = recommendations['recommendations'][0]
            assert 'soil_suitability_score' in first_crop['score_components']
            assert 0 <= first_crop['score_components']['soil_suitability_score'] <= 10
    
    def test_market_demand_scoring(self):
        """Test market demand scoring for different crops"""
        recommendations = self.engine.generate_recommendations(
            self.sample_rainfall_data, 
            self.sample_weather_data, 
            -13.9833, 
            33.7833
        )
        
        # Market demand should be included in scoring
        first_crop = recommendations['recommendations'][0]
        assert 'market_demand_score' in first_crop['score_components']
        assert 0 <= first_crop['score_components']['market_demand_score'] <= 5


class TestConfidenceScorer:
    """Test confidence scoring system for recommendations"""
    
    def setup_method(self):
        """Set up test environment"""
        self.scorer = ConfidenceScorer()
    
    def test_confidence_scoring_initialization(self):
        """Test confidence scorer initialization"""
        assert self.scorer is not None
        assert hasattr(self.scorer, 'calculate_confidence')
        assert hasattr(self.scorer, 'get_data_quality_score')
    
    def test_calculate_recommendation_confidence(self):
        """Test confidence calculation for recommendations"""
        # This test will fail initially - we need to implement confidence scoring
        sample_recommendation = {
            'crop_id': 'maize',
            'total_score': 85,
            'score_components': {
                'rainfall_score': 35,
                'temperature_score': 25,
                'seasonal_score': 15,
                'humidity_score': 10
            },
            'data_sources': ['weather_api', 'crop_database']
        }
        
        confidence_result = self.scorer.calculate_confidence(sample_recommendation)
        
        # Confidence result should be a dictionary
        assert isinstance(confidence_result, dict)
        assert 'confidence_score' in confidence_result
        assert 'confidence_level' in confidence_result
        
        # Confidence score should be between 0 and 1
        confidence_score = confidence_result['confidence_score']
        assert 0 <= confidence_score <= 1
        assert isinstance(confidence_score, float)
    
    def test_data_quality_scoring(self):
        """Test data quality assessment"""
        sample_data = {
            'weather_data_age': 2,  # hours
            'rainfall_data_completeness': 0.95,
            'temperature_accuracy': 0.98,
            'forecast_reliability': 0.87
        }
        
        quality_score = self.scorer.get_data_quality_score(sample_data)
        
        assert 0 <= quality_score <= 1
        assert isinstance(quality_score, float)
    
    def test_confidence_levels_assignment(self):
        """Test confidence level categorization"""
        # High confidence
        high_confidence = self.scorer.get_confidence_level(0.9)
        assert high_confidence == 'high'
        
        # Medium confidence
        medium_confidence = self.scorer.get_confidence_level(0.7)
        assert medium_confidence == 'medium'
        
        # Low confidence
        low_confidence = self.scorer.get_confidence_level(0.4)
        assert low_confidence == 'low'


class TestPlantingCalendar:
    """Test enhanced planting calendar integration"""
    
    def setup_method(self):
        """Set up test environment"""
        self.calendar = PlantingCalendar()
        self.sample_location = (-13.9833, 33.7833)  # Lilongwe coordinates
    
    def test_planting_calendar_initialization(self):
        """Test planting calendar initialization"""
        assert self.calendar is not None
        assert hasattr(self.calendar, 'get_monthly_recommendations')
        assert hasattr(self.calendar, 'get_critical_timing_alerts')
    
    def test_monthly_planting_recommendations(self):
        """Test month-by-month planting recommendations"""
        # This test will fail initially - we need to implement planting calendar
        recommendations = self.calendar.get_monthly_recommendations(
            month='January',
            location=self.sample_location,
            weather_forecast={'rainfall_forecast': 150}
        )
        
        assert 'month' in recommendations
        assert 'plantable_crops' in recommendations
        assert 'critical_activities' in recommendations
        assert 'timing_alerts' in recommendations
        
        # Should have specific crop recommendations
        assert len(recommendations['plantable_crops']) > 0
    
    def test_critical_timing_alerts(self):
        """Test critical timing alerts generation"""
        alerts = self.calendar.get_critical_timing_alerts(
            crops=['maize', 'beans'],
            current_month='December',
            location=self.sample_location
        )
        
        assert isinstance(alerts, list)
        
        # Should have alert structure
        if alerts:
            alert = alerts[0]
            assert 'crop' in alert
            assert 'alert_type' in alert
            assert 'message' in alert
            assert 'urgency' in alert
    
    def test_activity_scheduling(self):
        """Test agricultural activity scheduling"""
        schedule = self.calendar.get_activity_schedule(
            crops=['maize', 'beans'],
            planting_date='2024-12-15',
            location=self.sample_location
        )
        
        assert 'planting_activities' in schedule
        assert 'maintenance_activities' in schedule
        assert 'harvest_activities' in schedule
        
        # Should have dated activities
        for activity_type in schedule.values():
            if activity_type:
                assert 'date' in activity_type[0]
                assert 'activity' in activity_type[0]
    
    def test_weather_based_timing_adjustments(self):
        """Test weather-based timing adjustments"""
        adjustments = self.calendar.get_weather_adjustments(
            planned_activities=[
                {'crop': 'maize', 'activity': 'planting', 'planned_date': '2024-12-20'}
            ],
            weather_forecast={'rainfall_forecast': 5, 'temperature_forecast': 35}
        )
        
        assert isinstance(adjustments, list)
        
        # Should have adjustment recommendations
        if adjustments:
            adjustment = adjustments[0]
            assert 'original_date' in adjustment
            assert 'recommended_date' in adjustment
            assert 'reason' in adjustment


class TestPDFEnhancedVarieties:
    """Test PDF-enhanced variety recommendations"""
    
    def setup_method(self):
        """Set up test environment"""
        self.pdf_varieties = PDFEnhancedVarieties()
        self.sample_query = "drought tolerant maize varieties for Lilongwe"
    
    def test_pdf_varieties_initialization(self):
        """Test PDF enhanced varieties initialization"""
        assert self.pdf_varieties is not None
        assert hasattr(self.pdf_varieties, 'get_pdf_enhanced_varieties')
        assert hasattr(self.pdf_varieties, 'search_variety_information')
    
    def test_pdf_enhanced_variety_search(self):
        """Test PDF-based variety information search"""
        # This test will fail initially - we need to implement PDF variety enhancement
        variety_info = self.pdf_varieties.search_variety_information(
            crop='maize',
            location='Lilongwe',
            conditions={'drought_stress': True, 'low_rainfall': True}
        )
        
        assert 'varieties' in variety_info
        assert 'pdf_sources' in variety_info
        assert 'enhanced_recommendations' in variety_info
        
        # Should have PDF-sourced information
        if variety_info['varieties']:
            variety = variety_info['varieties'][0]
            assert 'pdf_enhanced_data' in variety
    
    def test_variety_performance_data_integration(self):
        """Test integration of PDF performance data"""
        performance_data = self.pdf_varieties.get_variety_performance_data(
            variety_name='SC403',
            location='Lilongwe'
        )
        
        assert 'yield_data' in performance_data
        assert 'climate_adaptation' in performance_data
        assert 'pdf_sources' in performance_data
        
        # Should have location-specific data
        if performance_data['yield_data']:
            assert 'location' in performance_data['yield_data']
    
    def test_disease_resistance_pdf_integration(self):
        """Test PDF-based disease resistance information"""
        disease_info = self.pdf_varieties.get_disease_resistance_info(
            crop='maize',
            location='Lilongwe'
        )
        
        assert 'common_diseases' in disease_info
        assert 'resistant_varieties' in disease_info
        assert 'pdf_sources' in disease_info
        
        # Should have actionable information
        if disease_info['resistant_varieties']:
            variety = disease_info['resistant_varieties'][0]
            assert 'variety_name' in variety
            assert 'resistance_level' in variety


class TestIntegrationEnhancedRecommendations:
    """Test integration of all enhanced recommendation components"""
    
    def setup_method(self):
        """Set up test environment"""
        self.engine = EnhancedRecommendationEngine()
        self.sample_coordinates = (-13.9833, 33.7833)
        
    def test_complete_enhanced_recommendation_flow(self):
        """Test complete enhanced recommendation with all components"""
        recommendations = self.engine.generate_comprehensive_recommendations(
            rainfall_data={
                'total_7day_rainfall': 45,
                'forecast_7day_rainfall': 30,
                'rainy_days_forecast': 4
            },
            weather_data={
                'temperature': 25,
                'humidity': 65,
                'pressure': 1013
            },
            lat=-13.9833,
            lon=33.7833,
            user_preferences={'focus': 'drought_resistance'}
        )
        
        # Should have all enhanced components
        assert 'enhanced_recommendations' in recommendations
        assert 'confidence_scores' in recommendations
        assert 'planting_calendar' in recommendations
        assert 'pdf_enhanced_varieties' in recommendations
        
        # Each recommendation should have confidence scoring
        for recommendation in recommendations['enhanced_recommendations']:
            assert 'confidence_score' in recommendation
            assert 'confidence_level' in recommendation
            assert 'data_quality' in recommendation
    
    def test_recommendation_reliability_assessment(self):
        """Test overall recommendation reliability assessment"""
        reliability = self.engine.assess_recommendation_reliability(
            recommendations_data={
                'weather_data_age': 1,
                'pdf_sources_count': 3,
                'scoring_completeness': 0.95
            }
        )
        
        assert 'overall_reliability' in reliability
        assert 'component_reliability' in reliability
        assert 'improvement_suggestions' in reliability
        
        # Should have reliability score
        assert 0 <= reliability['overall_reliability'] <= 1


# Test data validation and error handling
class TestEnhancedRecommendationValidation:
    """Test validation and error handling for enhanced recommendations"""
    
    def test_invalid_coordinates_handling(self):
        """Test handling of invalid coordinates"""
        engine = EnhancedRecommendationEngine()
        
        # Should handle invalid coordinates gracefully
        recommendations = engine.generate_recommendations(
            rainfall_data={'total_7day_rainfall': 45},
            weather_data={'temperature': 25},
            lat=999,  # Invalid latitude
            lon=999   # Invalid longitude
        )
        
        # Should return error information
        assert 'error' in recommendations or 'recommendations' in recommendations
    
    def test_missing_data_handling(self):
        """Test handling of missing data"""
        engine = EnhancedRecommendationEngine()
        
        # Should handle missing data gracefully
        recommendations = engine.generate_recommendations(
            rainfall_data={},  # Missing data
            weather_data={'temperature': 25},
            lat=-13.9833,
            lon=33.7833
        )
        
        # Should still provide recommendations with lower confidence
        assert 'recommendations' in recommendations
        
        # Confidence should be lower due to missing data
        if recommendations['recommendations']:
            assert recommendations['recommendations'][0]['confidence_score'] < 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 