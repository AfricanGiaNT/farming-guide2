"""
Unit tests for agricultural crop recommendations system
Tests seasonal analysis, crop matching, and agricultural advisory generation
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.crop_advisor.seasonal_analyzer import SeasonalAnalyzer
from scripts.crop_advisor.crop_matcher import CropMatcher


class TestSeasonalAnalyzer:
    """Test suite for SeasonalAnalyzer class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = SeasonalAnalyzer()
        
        # Mock monthly averages data
        self.monthly_avg_wet_dominant = {
            'January': 250.0, 'February': 200.0, 'March': 150.0,
            'April': 80.0, 'May': 20.0, 'June': 5.0,
            'July': 0.0, 'August': 0.0, 'September': 10.0,
            'October': 50.0, 'November': 150.0, 'December': 220.0
        }
        
        self.monthly_avg_balanced = {
            'January': 120.0, 'February': 110.0, 'March': 105.0,
            'April': 95.0, 'May': 80.0, 'June': 70.0,
            'July': 75.0, 'August': 85.0, 'September': 90.0,
            'October': 100.0, 'November': 115.0, 'December': 125.0
        }
    
    def test_detect_wet_season(self):
        """Test wet season detection with >100mm threshold"""
        result = self.analyzer.detect_seasons(self.monthly_avg_wet_dominant)
        
        assert 'wet_season_months' in result
        assert 'January' in result['wet_season_months']
        assert 'February' in result['wet_season_months']
        assert 'March' in result['wet_season_months']
        assert 'November' in result['wet_season_months']
        assert 'December' in result['wet_season_months']
        
        # Dry season months
        assert 'July' in result['dry_season_months']
        assert 'August' in result['dry_season_months']
        
    def test_seasonal_rainfall_averages(self):
        """Test calculation of seasonal rainfall averages"""
        result = self.analyzer.detect_seasons(self.monthly_avg_wet_dominant)
        
        assert result['wet_season_average_rainfall_mm'] > 100
        assert result['dry_season_average_rainfall_mm'] < 100
        assert result['wet_season_total_rainfall_mm'] > 0
        assert result['dry_season_total_rainfall_mm'] >= 0
    
    def test_calculate_variability_low(self):
        """Test variability calculation with low variation"""
        annual_totals = [800, 820, 790, 810, 805]  # Low variability
        result = self.analyzer.calculate_variability(annual_totals)
        
        assert result['level'] == 'Low'
        assert result['percentage'] < 20
        assert 'coefficient_of_variation' in result
        assert result['coefficient_of_variation'] < 0.2
    
    def test_calculate_variability_high(self):
        """Test variability calculation with high variation"""
        annual_totals = [400, 900, 500, 850, 450]  # High variability
        result = self.analyzer.calculate_variability(annual_totals)
        
        assert result['level'] == 'High'
        assert result['percentage'] > 30
    
    def test_calculate_variability_medium(self):
        """Test variability calculation with medium variation"""
        annual_totals = [700, 850, 750, 820, 680]  # Medium variability
        result = self.analyzer.calculate_variability(annual_totals)
        
        assert result['level'] in ['Medium', 'Low', 'High']  # Should be categorized
        assert 0 <= result['percentage'] <= 100
    
    def test_count_drought_years(self):
        """Test drought year detection (<400mm threshold)"""
        per_year_data = [
            {'year': 2025, 'annual_rainfall': 350, 'monthly': {}},
            {'year': 2024, 'annual_rainfall': 380, 'monthly': {}},
            {'year': 2023, 'annual_rainfall': 700, 'monthly': {}}
        ]
        
        result = self.analyzer.count_extreme_events(per_year_data)
        
        assert result['drought_years'] == 2
        assert 2025 in result['drought_year_list']
        assert 2024 in result['drought_year_list']
        assert result['drought_threshold_mm'] == 400
    
    def test_count_flood_years(self):
        """Test flood year detection (>1200mm threshold)"""
        per_year_data = [
            {'year': 2025, 'annual_rainfall': 1300, 'monthly': {}},
            {'year': 2024, 'annual_rainfall': 800, 'monthly': {}},
            {'year': 2023, 'annual_rainfall': 1250, 'monthly': {}}
        ]
        
        result = self.analyzer.count_extreme_events(per_year_data)
        
        assert result['flood_years'] == 2
        assert 2025 in result['flood_year_list']
        assert 2023 in result['flood_year_list']
        assert result['flood_threshold_mm'] == 1200
    
    def test_extreme_month_detection(self):
        """Test detection of extreme monthly rainfall events"""
        per_year_data = [
            {'year': 2025, 'annual_rainfall': 800, 'monthly': {'January': 350}},
            {'year': 2024, 'annual_rainfall': 750, 'monthly': {'February': 280}}
        ]
        
        result = self.analyzer.count_extreme_events(per_year_data)
        
        # 350mm in January should trigger flood detection
        assert result['flood_years'] >= 1
        assert len(result['flood_month_events']) > 0
    
    def test_generate_warnings_high_variability(self):
        """Test warning generation for high variability"""
        variability = {'level': 'High', 'percentage': 35.0}
        extreme_events = {'drought_years': 1, 'flood_years': 0, 'total_years_analyzed': 3}
        seasonal_data = {'wet_season_months': ['Jan', 'Feb'], 'dry_season_count': 10, 'dry_season_months': []}
        
        warnings, advice = self.analyzer.generate_warnings_and_advice(
            variability, extreme_events, seasonal_data
        )
        
        assert len(warnings) > 0
        assert any('variability' in w.lower() for w in warnings)
        assert len(advice) > 0
        assert any('drought' in a.lower() for a in advice)
    
    def test_generate_warnings_frequent_droughts(self):
        """Test warning generation for frequent droughts"""
        variability = {'level': 'Low', 'percentage': 15.0}
        extreme_events = {'drought_years': 2, 'flood_years': 0, 'total_years_analyzed': 3}
        seasonal_data = {'wet_season_months': ['Jan'], 'dry_season_count': 11, 'dry_season_months': []}
        
        warnings, advice = self.analyzer.generate_warnings_and_advice(
            variability, extreme_events, seasonal_data
        )
        
        assert any('drought' in w.lower() for w in warnings)
        assert any('cassava' in a.lower() or 'sorghum' in a.lower() or 'millet' in a.lower() for a in advice)
    
    def test_full_analysis_pipeline(self):
        """Test complete weather pattern analysis"""
        historical_data = {
            'monthly_averages': {
                'January': {'average_rainfall': 250.0},
                'February': {'average_rainfall': 200.0},
                'March': {'average_rainfall': 150.0},
                'April': {'average_rainfall': 80.0},
                'May': {'average_rainfall': 20.0},
                'June': {'average_rainfall': 5.0},
                'July': {'average_rainfall': 0.0},
                'August': {'average_rainfall': 0.0},
                'September': {'average_rainfall': 10.0},
                'October': {'average_rainfall': 50.0},
                'November': {'average_rainfall': 150.0},
                'December': {'average_rainfall': 220.0}
            },
            'per_year': [
                {'year': 2025, 'annual_rainfall': 600, 'monthly': {}},
                {'year': 2024, 'annual_rainfall': 750, 'monthly': {}},
                {'year': 2023, 'annual_rainfall': 650, 'monthly': {}}
            ]
        }
        
        result = self.analyzer.analyze_weather_patterns(historical_data)
        
        assert 'wet_season' in result
        assert 'dry_season' in result
        assert 'variability' in result
        assert 'extreme_events' in result
        assert 'warnings' in result
        assert 'advice' in result
        assert result['years_analyzed'] == 3


class TestCropMatcher:
    """Test suite for CropMatcher class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.matcher = CropMatcher()
    
    def test_crop_data_loaded(self):
        """Test that crop data loads successfully"""
        assert self.matcher.crops_data is not None
        assert len(self.matcher.crops_data) > 0
        assert 'maize' in self.matcher.crops_data
    
    def test_chichewa_names_available(self):
        """Test Chichewa translations are available"""
        assert 'Chimanga' in self.matcher.CHICHEWA_NAMES.values()
        assert 'Nyemba' in self.matcher.CHICHEWA_NAMES.values()
        assert 'Mtedza' in self.matcher.CHICHEWA_NAMES.values()
    
    def test_match_wet_season_crops(self):
        """Test matching crops to wet season conditions"""
        wet_crops = self.matcher.match_crops_to_season(
            season_type='wet',
            season_avg_rainfall=200.0,  # Good rainfall
            season_months=['November', 'December', 'January', 'February', 'March'],
            variability_level='Low'
        )
        
        assert len(wet_crops) > 0
        # Maize should be suitable for wet season
        assert any(crop['crop_id'] == 'maize' for crop in wet_crops)
    
    def test_match_dry_season_crops(self):
        """Test matching crops to dry season conditions"""
        dry_crops = self.matcher.match_crops_to_season(
            season_type='dry',
            season_avg_rainfall=15.0,  # Low rainfall
            season_months=['May', 'June', 'July', 'August', 'September'],
            variability_level='Low'
        )
        
        # Dry season crops should have low water requirements
        for crop in dry_crops:
            assert crop['water_requirement'] in ['low', 'medium']
    
    def test_match_score_calculation(self):
        """Test crop match score calculation"""
        # Perfect match: actual = optimal
        score1 = self.matcher._calculate_match_score(
            actual_rainfall=600, optimal=600, minimum=450, maximum=1200
        )
        assert score1 == 100
        
        # Good match: actual between optimal and minimum
        score2 = self.matcher._calculate_match_score(
            actual_rainfall=500, optimal=600, minimum=450, maximum=1200
        )
        assert 70 <= score2 < 100
        
        # No match: below minimum
        score3 = self.matcher._calculate_match_score(
            actual_rainfall=300, optimal=600, minimum=450, maximum=1200
        )
        assert score3 == 0
    
    def test_water_requirement_classification(self):
        """Test classification of water requirements"""
        # Low water requirement
        low_req = {'minimum_rainfall': 300, 'optimal_rainfall': 400}
        assert self.matcher._classify_water_requirement(low_req) == 'low'
        
        # Medium water requirement
        med_req = {'minimum_rainfall': 450, 'optimal_rainfall': 600}
        assert self.matcher._classify_water_requirement(med_req) == 'medium'
        
        # High water requirement
        high_req = {'minimum_rainfall': 600, 'optimal_rainfall': 900}
        assert self.matcher._classify_water_requirement(high_req) == 'high'
    
    def test_high_variability_recommendations(self):
        """Test that high variability generates drought-tolerant advice"""
        crops = self.matcher.match_crops_to_season(
            season_type='wet',
            season_avg_rainfall=150.0,
            season_months=['November', 'December', 'January'],
            variability_level='High'
        )
        
        # Should include drought tolerance notes
        crops_with_notes = [c for c in crops if c.get('notes')]
        assert len(crops_with_notes) > 0
    
    def test_full_recommendations_pipeline(self):
        """Test complete agricultural recommendations generation"""
        seasonal_analysis = {
            'wet_season': {
                'months': ['November', 'December', 'January', 'February', 'March'],
                'average_monthly_rainfall_mm': 200.0,
                'total_season_rainfall_mm': 1000.0
            },
            'dry_season': {
                'months': ['May', 'June', 'July', 'August', 'September', 'October'],
                'average_monthly_rainfall_mm': 20.0,
                'total_season_rainfall_mm': 120.0
            },
            'variability': {'level': 'Low', 'percentage': 15.0},
            'extreme_events': {'drought_years': 0, 'flood_years': 0},
            'warnings': [],
            'advice': [],
            'years_analyzed': 3
        }
        
        recommendations = self.matcher.get_agricultural_recommendations(seasonal_analysis)
        
        assert 'wet_season' in recommendations
        assert 'dry_season' in recommendations
        assert 'suitable_crops' in recommendations['wet_season']
        assert 'suitable_crops' in recommendations['dry_season']
        assert len(recommendations['wet_season']['suitable_crops']) > 0


class TestIntegration:
    """Integration tests for complete recommendation system"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from weather data to crop recommendations"""
        # Simulate historical weather data
        historical_data = {
            'monthly_averages': {
                month: {'average_rainfall': rainfall}
                for month, rainfall in {
                    'January': 250, 'February': 200, 'March': 150, 'April': 80,
                    'May': 20, 'June': 5, 'July': 0, 'August': 0, 'September': 10,
                    'October': 50, 'November': 150, 'December': 220
                }.items()
            },
            'per_year': [
                {'year': 2025, 'annual_rainfall': 600, 'monthly': {}},
                {'year': 2024, 'annual_rainfall': 750, 'monthly': {}},
                {'year': 2023, 'annual_rainfall': 650, 'monthly': {}}
            ]
        }
        
        # Analyze weather patterns
        analyzer = SeasonalAnalyzer()
        analysis = analyzer.analyze_weather_patterns(historical_data)
        
        # Generate crop recommendations
        matcher = CropMatcher()
        recommendations = matcher.get_agricultural_recommendations(analysis)
        
        # Verify complete output structure
        assert recommendations is not None
        assert 'wet_season' in recommendations
        assert 'dry_season' in recommendations
        assert 'variability' in recommendations
        assert 'extreme_events' in recommendations
        
        # Verify crop recommendations exist
        wet_crops = recommendations['wet_season']['suitable_crops']
        assert len(wet_crops) > 0
        
        # Verify crop data structure
        for crop in wet_crops[:1]:  # Check first crop
            assert 'crop_name' in crop
            assert 'local_name' in crop
            assert 'water_requirement' in crop
            assert 'planting_months' in crop
            assert 'days_to_harvest' in crop
            assert 'match_score' in crop


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

