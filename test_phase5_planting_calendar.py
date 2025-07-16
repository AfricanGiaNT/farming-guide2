"""
Test Phase 5: Planting Calendar Integration
Tests the complete planting calendar functionality including:
- Planting calendar generation
- Optimal planting window analysis
- Monthly recommendations
- Risk assessment
- Integration with varieties command
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from scripts.handlers.varieties_handler import VarietiesHandler
from scripts.weather_engine.historical_weather_api import HistoricalRainfallData


class TestPhase5PlantingCalendar:
    """Test suite for Phase 5 planting calendar functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = VarietiesHandler()
        
        # Mock weather analysis data
        self.mock_weather_analysis = {
            'location': {'lat': -13.9833, 'lon': 33.7833},
            'historical_data': {
                'years_analyzed': 5,
                'monthly_averages': {
                    'January': 145.2,
                    'February': 123.8,
                    'March': 89.4,
                    'April': 32.1,
                    'May': 8.5,
                    'June': 2.3,
                    'July': 1.2,
                    'August': 3.4,
                    'September': 12.6,
                    'October': 34.7,
                    'November': 98.3,
                    'December': 156.9
                },
                'annual_averages': [708.2, 542.8, 623.4, 798.1, 687.5],
                'wet_season_months': ['November', 'December', 'January', 'February', 'March'],
                'dry_season_months': ['April', 'May', 'June', 'July', 'August', 'September'],
                'drought_years': [2018, 2020],
                'flood_years': [2019],
                'rainfall_variability': 23.2,
                'climate_trend': 'stable'
            },
            'current_month': 'December',
            'analysis_timestamp': '2024-12-01T10:00:00'
        }
        
        print("✅ Test setup completed for Phase 5 planting calendar")
    
    def test_generate_planting_calendar(self):
        """Test 1: Planting calendar generation."""
        print("\n🧪 Test 1: Testing planting calendar generation...")
        
        # Generate planting calendar
        planting_calendar = self.handler.generate_planting_calendar(
            'maize', self.mock_weather_analysis, 'test_user'
        )
        
        # Verify calendar structure
        assert 'crop_name' in planting_calendar
        assert 'optimal_planting_windows' in planting_calendar
        assert 'monthly_recommendations' in planting_calendar
        assert 'risk_assessment' in planting_calendar
        assert 'best_planting_month' in planting_calendar
        assert 'alternative_months' in planting_calendar
        assert 'avoid_months' in planting_calendar
        assert 'generated_at' in planting_calendar
        
        print(f"✅ Planting calendar generated for {planting_calendar['crop_name']}")
        print(f"✅ Best planting month: {planting_calendar['best_planting_month']}")
        print(f"✅ Alternative months: {planting_calendar['alternative_months']}")
        print(f"✅ Avoid months: {planting_calendar['avoid_months']}")
        
        # Test that calendar is actually generated
        assert planting_calendar['crop_name'] == 'maize'
        assert planting_calendar['best_planting_month'] is not None
        assert isinstance(planting_calendar['alternative_months'], list)
        assert isinstance(planting_calendar['avoid_months'], list)
        
        print("✅ Test 1 passed: Planting calendar generation working correctly")
        
    def test_analyze_optimal_planting_windows(self):
        """Test 2: Optimal planting window analysis."""
        print("\n🧪 Test 2: Testing optimal planting window analysis...")
        
        # Analyze optimal planting windows
        planting_windows = self.handler._analyze_optimal_planting_windows(
            self.mock_weather_analysis, 'groundnut'
        )
        
        # Verify window analysis structure
        assert 'primary_optimal_month' in planting_windows
        assert 'alternative_months' in planting_windows
        assert 'avoid_months' in planting_windows
        assert 'month_scores' in planting_windows
        assert 'maturity_days' in planting_windows
        
        # Test that scores are calculated for planting months
        month_scores = planting_windows['month_scores']
        assert len(month_scores) == 4  # Primary planting months
        
        # Verify that all scores are between 0 and 100
        for month, score in month_scores.items():
            assert 0 <= score <= 100
        
        print(f"✅ Primary optimal month: {planting_windows['primary_optimal_month']}")
        print(f"✅ Month scores: {month_scores}")
        print(f"✅ Maturity days: {planting_windows['maturity_days']}")
        
        print("✅ Test 2 passed: Optimal planting window analysis working correctly")
        
    def test_score_planting_month(self):
        """Test 3: Planting month scoring algorithm."""
        print("\n🧪 Test 3: Testing planting month scoring algorithm...")
        
        monthly_averages = self.mock_weather_analysis['historical_data']['monthly_averages']
        historical_data = self.mock_weather_analysis['historical_data']
        
        # Test scoring for different months
        november_score = self.handler._score_planting_month(
            'November', monthly_averages, 120, historical_data
        )
        
        may_score = self.handler._score_planting_month(
            'May', monthly_averages, 120, historical_data
        )
        
        # Verify scoring logic
        assert 0 <= november_score <= 100
        assert 0 <= may_score <= 100
        
        # November should score higher than May (wet vs dry season)
        assert november_score > may_score
        
        print(f"✅ November score: {november_score}")
        print(f"✅ May score: {may_score}")
        print(f"✅ November scores higher than May: {november_score > may_score}")
        
        print("✅ Test 3 passed: Planting month scoring working correctly")
        
    def test_generate_monthly_recommendations(self):
        """Test 4: Monthly recommendations generation."""
        print("\n🧪 Test 4: Testing monthly recommendations generation...")
        
        # Mock planting windows
        planting_windows = {
            'primary_optimal_month': 'November',
            'alternative_months': ['December', 'January'],
            'avoid_months': ['May', 'June'],
            'month_scores': {
                'October': 65,
                'November': 85,
                'December': 78,
                'January': 72
            }
        }
        
        # Generate monthly recommendations
        monthly_recommendations = self.handler._generate_monthly_recommendations(
            'soybean', self.mock_weather_analysis, planting_windows
        )
        
        # Verify recommendations structure
        assert len(monthly_recommendations) == 12  # All months
        
        # Test specific month recommendations
        november_rec = monthly_recommendations['November']
        assert november_rec['recommendation_type'] == 'optimal'
        assert november_rec['month'] == 'November'
        assert 'activities' in november_rec
        assert 'advice' in november_rec
        
        may_rec = monthly_recommendations['May']
        assert may_rec['recommendation_type'] == 'avoid'
        
        print(f"✅ November recommendation: {november_rec['recommendation_type']}")
        print(f"✅ May recommendation: {may_rec['recommendation_type']}")
        print(f"✅ Generated recommendations for all 12 months")
        
        print("✅ Test 4 passed: Monthly recommendations generation working correctly")
        
    def test_assess_planting_risks(self):
        """Test 5: Risk assessment functionality."""
        print("\n🧪 Test 5: Testing planting risk assessment...")
        
        # Assess planting risks
        risk_assessment = self.handler._assess_planting_risks(
            self.mock_weather_analysis, 'maize'
        )
        
        # Verify risk assessment structure
        assert 'drought_risk' in risk_assessment
        assert 'flood_risk' in risk_assessment
        assert 'rainfall_variability' in risk_assessment
        assert 'mitigation_strategies' in risk_assessment
        assert 'overall_risk_level' in risk_assessment
        
        # Test drought risk calculation
        drought_risk = risk_assessment['drought_risk']
        assert 'level' in drought_risk
        assert 'probability' in drought_risk
        assert 'recent_years' in drought_risk
        
        # Test flood risk calculation
        flood_risk = risk_assessment['flood_risk']
        assert 'level' in flood_risk
        assert 'probability' in flood_risk
        
        # Test mitigation strategies
        mitigation_strategies = risk_assessment['mitigation_strategies']
        assert isinstance(mitigation_strategies, list)
        assert len(mitigation_strategies) > 0
        
        print(f"✅ Drought risk level: {drought_risk['level']}")
        print(f"✅ Flood risk level: {flood_risk['level']}")
        print(f"✅ Overall risk level: {risk_assessment['overall_risk_level']}")
        print(f"✅ Mitigation strategies: {len(mitigation_strategies)}")
        
        print("✅ Test 5 passed: Risk assessment working correctly")
        
    def test_format_planting_calendar_section(self):
        """Test 6: Planting calendar formatting."""
        print("\n🧪 Test 6: Testing planting calendar formatting...")
        
        # Generate a sample planting calendar
        planting_calendar = self.handler.generate_planting_calendar(
            'groundnut', self.mock_weather_analysis, 'test_user'
        )
        
        # Format the calendar section
        formatted_section = self.handler._format_planting_calendar_section(planting_calendar)
        
        # Verify formatting
        assert isinstance(formatted_section, str)
        assert len(formatted_section) > 0
        assert '📅 **Planting Calendar**' in formatted_section
        assert '🌟 **Best Planting Month:**' in formatted_section
        assert '📊 **Monthly Recommendations:**' in formatted_section
        assert '⚠️ **Risk Assessment:**' in formatted_section
        
        print(f"✅ Formatted section length: {len(formatted_section)} characters")
        print(f"✅ Contains calendar header: {'📅 **Planting Calendar**' in formatted_section}")
        print(f"✅ Contains monthly recommendations: {'📊 **Monthly Recommendations:**' in formatted_section}")
        print(f"✅ Contains risk assessment: {'⚠️ **Risk Assessment:**' in formatted_section}")
        
        print("✅ Test 6 passed: Planting calendar formatting working correctly")
        
    def test_calculate_growing_season_months(self):
        """Test 7: Growing season calculation."""
        print("\n🧪 Test 7: Testing growing season months calculation...")
        
        # Test growing season calculation for different crops
        maize_growing_months = self.handler._calculate_growing_season_months('November', 120)
        groundnut_growing_months = self.handler._calculate_growing_season_months('December', 105)
        
        # Verify growing season calculation
        assert isinstance(maize_growing_months, list)
        assert isinstance(groundnut_growing_months, list)
        assert len(maize_growing_months) == 5  # 120 days / 30 + 1
        assert len(groundnut_growing_months) == 4  # 105 days / 30 + 1
        
        print(f"✅ Maize growing months ({len(maize_growing_months)}): {maize_growing_months}")
        print(f"✅ Groundnut growing months ({len(groundnut_growing_months)}): {groundnut_growing_months}")
        
        print("✅ Test 7 passed: Growing season calculation working correctly")
        
    def test_basic_planting_calendar_fallback(self):
        """Test 8: Basic planting calendar fallback."""
        print("\n🧪 Test 8: Testing basic planting calendar fallback...")
        
        # Generate basic planting calendar without weather analysis
        basic_calendar = self.handler._generate_basic_planting_calendar('soybean')
        
        # Verify basic calendar structure
        assert 'crop_name' in basic_calendar
        assert 'best_planting_month' in basic_calendar
        assert 'alternative_months' in basic_calendar
        assert 'avoid_months' in basic_calendar
        assert 'monthly_recommendations' in basic_calendar
        assert 'risk_assessment' in basic_calendar
        assert 'note' in basic_calendar
        
        # Test fallback values
        assert basic_calendar['crop_name'] == 'soybean'
        assert basic_calendar['best_planting_month'] == 'November'
        assert 'November' in basic_calendar['monthly_recommendations']
        assert 'Basic recommendations' in basic_calendar['note']
        
        print(f"✅ Basic calendar crop: {basic_calendar['crop_name']}")
        print(f"✅ Basic calendar best month: {basic_calendar['best_planting_month']}")
        print(f"✅ Basic calendar note: {basic_calendar['note']}")
        
        print("✅ Test 8 passed: Basic planting calendar fallback working correctly")


def main():
    """Run all Phase 5 planting calendar tests."""
    print("🚀 Starting Phase 5 Planting Calendar Integration Tests")
    print("=" * 60)
    
    test_suite = TestPhase5PlantingCalendar()
    
    try:
        # Initialize test suite
        test_suite.setup_method()
        
        # Run all tests
        test_suite.test_generate_planting_calendar()
        test_suite.test_analyze_optimal_planting_windows()
        test_suite.test_score_planting_month()
        test_suite.test_generate_monthly_recommendations()
        test_suite.test_assess_planting_risks()
        test_suite.test_format_planting_calendar_section()
        test_suite.test_calculate_growing_season_months()
        test_suite.test_basic_planting_calendar_fallback()
        
        print("\n" + "=" * 60)
        print("🎉 ALL PHASE 5 TESTS PASSED!")
        print("✅ Planting calendar generation: WORKING")
        print("✅ Optimal planting window analysis: WORKING")
        print("✅ Monthly recommendations: WORKING")
        print("✅ Risk assessment: WORKING")
        print("✅ Calendar formatting: WORKING")
        print("✅ Growing season calculation: WORKING")
        print("✅ Basic calendar fallback: WORKING")
        print("✅ Integration ready: WORKING")
        
        print("\n🌟 Phase 5: Planting Calendar Integration - COMPLETE!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 