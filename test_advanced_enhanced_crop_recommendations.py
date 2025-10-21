"""
Comprehensive test for Advanced Enhanced Crop Recommendation Engine.
Tests all advanced components: algorithm, yield calculator, and input system.
"""
import unittest
import json
from scripts.crop_advisor.advanced_enhanced_crop_recommendation_engine import AdvancedEnhancedCropRecommendationEngine
from scripts.crop_advisor.advanced_crop_algorithm import AdvancedCropRecommendationAlgorithm
from scripts.crop_advisor.advanced_yield_calculator import AdvancedYieldProjectionCalculator
from scripts.crop_advisor.advanced_input_system import AdvancedInputRecommendationSystem


class TestAdvancedEnhancedCropRecommendationEngine(unittest.TestCase):
    """Test the advanced enhanced crop recommendation engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = AdvancedEnhancedCropRecommendationEngine()
        self.algorithm = AdvancedCropRecommendationAlgorithm(self.engine.crop_database)
        self.yield_calculator = AdvancedYieldProjectionCalculator()
        self.input_system = AdvancedInputRecommendationSystem()
        
        # Test data
        self.test_crop_data = {
            'name': 'Maize',
            'water_requirements': {
                'minimum_rainfall': 300,
                'optimal_rainfall': 500,
                'maximum_rainfall': 800
            },
            'temperature_requirements': {
                'minimum_temp': 18,
                'optimal_temp': 25,
                'maximum_temp': 35
            },
            'varieties': [
                {
                    'name': 'SC 403',
                    'maturity_days': 110,
                    'drought_tolerance': 'good',
                    'disease_resistance': ['Maize streak virus'],
                    'yield_potential': 'high',
                    'type': 'hybrid'
                }
            ]
        }
        
        self.test_environmental_factors = {
            'rainfall_mm': 450,
            'temperature': 26,
            'season': 'rainy_season',
            'humidity': 60
        }
        
        self.test_farmer_profile = {
            'budget_level': 'medium',
            'available_inputs': ['fertilizer', 'pesticides'],
            'experience_level': 'intermediate',
            'farm_size': 'medium'
        }
    
    def test_advanced_algorithm_initialization(self):
        """Test advanced algorithm initialization."""
        self.assertIsNotNone(self.algorithm)
        self.assertIsNotNone(self.algorithm.crop_database)
        self.assertIsNotNone(self.algorithm.seasonal_weights)
        
        print("✅ Advanced algorithm initialized successfully")
    
    def test_advanced_algorithm_suitability_calculation(self):
        """Test advanced suitability score calculation."""
        suitability_analysis = self.algorithm.calculate_advanced_suitability_score(
            self.test_crop_data,
            self.test_environmental_factors,
            None,  # No historical data for this test
            self.test_farmer_profile
        )
        
        # Verify structure
        self.assertIn('overall_score', suitability_analysis)
        self.assertIn('confidence', suitability_analysis)
        self.assertIn('factor_scores', suitability_analysis)
        self.assertIn('recommendation_level', suitability_analysis)
        self.assertIn('risk_factors', suitability_analysis)
        
        # Verify score range
        self.assertGreaterEqual(suitability_analysis['overall_score'], 0.0)
        self.assertLessEqual(suitability_analysis['overall_score'], 1.0)
        
        # Verify factor scores
        factor_scores = suitability_analysis['factor_scores']
        self.assertIn('rainfall', factor_scores)
        self.assertIn('temperature', factor_scores)
        self.assertIn('timing', factor_scores)
        self.assertIn('soil', factor_scores)
        self.assertIn('variety', factor_scores)
        
        print("✅ Advanced suitability calculation working correctly")
        print(f"   Overall Score: {suitability_analysis['overall_score']:.3f}")
        print(f"   Confidence: {suitability_analysis['confidence']:.3f}")
        print(f"   Recommendation Level: {suitability_analysis['recommendation_level']}")
    
    def test_advanced_yield_calculator_initialization(self):
        """Test advanced yield calculator initialization."""
        self.assertIsNotNone(self.yield_calculator)
        self.assertIsNotNone(self.yield_calculator.base_yield_factors)
        
        # Verify crop factors exist
        self.assertIn('maize', self.yield_calculator.base_yield_factors)
        self.assertIn('beans', self.yield_calculator.base_yield_factors)
        
        print("✅ Advanced yield calculator initialized successfully")
    
    def test_advanced_yield_projections(self):
        """Test advanced yield projections calculation."""
        yield_projections = self.yield_calculator.calculate_advanced_yield_projections(
            self.test_crop_data,
            self.test_environmental_factors,
            None,  # No historical data for this test
            self.test_farmer_profile,
            self.test_crop_data['varieties'][0]
        )
        
        # Verify structure
        self.assertIn('yield_projections', yield_projections)
        self.assertIn('yield_per_acre', yield_projections)
        self.assertIn('overall_yield_factor', yield_projections)
        self.assertIn('confidence', yield_projections)
        self.assertIn('risk_factors', yield_projections)
        self.assertIn('factor_breakdown', yield_projections)
        
        # Verify yield projections
        yield_proj = yield_projections['yield_projections']
        self.assertIn('conservative', yield_proj)
        self.assertIn('realistic', yield_proj)
        self.assertIn('potential', yield_proj)
        self.assertIn('optimal', yield_proj)
        
        # Verify yield progression
        self.assertLessEqual(yield_proj['conservative'], yield_proj['realistic'])
        self.assertLessEqual(yield_proj['realistic'], yield_proj['potential'])
        self.assertLessEqual(yield_proj['potential'], yield_proj['optimal'])
        
        print("✅ Advanced yield projections calculated successfully")
        print(f"   Conservative: {yield_proj['conservative']:.2f} tons/ha")
        print(f"   Realistic: {yield_proj['realistic']:.2f} tons/ha")
        print(f"   Potential: {yield_proj['potential']:.2f} tons/ha")
        print(f"   Overall Factor: {yield_projections['overall_yield_factor']:.3f}")
    
    def test_advanced_input_system_initialization(self):
        """Test advanced input system initialization."""
        self.assertIsNotNone(self.input_system)
        self.assertIsNotNone(self.input_system.fertilizer_recommendations)
        self.assertIsNotNone(self.input_system.pest_disease_info)
        
        # Verify crop data exists
        self.assertIn('maize', self.input_system.fertilizer_recommendations)
        self.assertIn('maize', self.input_system.pest_disease_info)
        
        print("✅ Advanced input system initialized successfully")
    
    def test_comprehensive_input_recommendations(self):
        """Test comprehensive input recommendations generation."""
        input_recommendations = self.input_system.generate_comprehensive_input_recommendations(
            self.test_crop_data,
            self.test_environmental_factors,
            None,  # No historical data for this test
            self.test_farmer_profile,
            self.test_crop_data['varieties'][0]
        )
        
        # Verify structure
        self.assertIn('fertilizer_recommendations', input_recommendations)
        self.assertIn('seed_recommendations', input_recommendations)
        self.assertIn('pest_control_recommendations', input_recommendations)
        self.assertIn('irrigation_recommendations', input_recommendations)
        self.assertIn('soil_management_recommendations', input_recommendations)
        self.assertIn('total_input_costs', input_recommendations)
        self.assertIn('implementation_timeline', input_recommendations)
        
        # Verify fertilizer recommendations
        fert_recs = input_recommendations['fertilizer_recommendations']
        self.assertIn('npk_ratio', fert_recs)
        self.assertIn('application_rate', fert_recs)
        self.assertIn('timing', fert_recs)
        self.assertIn('recommended_options', fert_recs)
        self.assertIn('cost_per_hectare', fert_recs)
        
        # Verify seed recommendations
        seed_recs = input_recommendations['seed_recommendations']
        self.assertIn('seed_rate', seed_recs)
        self.assertIn('seed_cost', seed_recs)
        self.assertIn('recommended_varieties', seed_recs)
        
        # Verify pest control recommendations
        pest_recs = input_recommendations['pest_control_recommendations']
        self.assertIn('common_pests', pest_recs)
        self.assertIn('common_diseases', pest_recs)
        self.assertIn('control_methods', pest_recs)
        self.assertIn('cost_per_hectare', pest_recs)
        
        print("✅ Comprehensive input recommendations generated successfully")
        print(f"   Fertilizer Cost: {fert_recs['cost_per_hectare']}")
        print(f"   Seed Cost: {seed_recs['seed_cost']}")
        print(f"   Pest Control Cost: {pest_recs['cost_per_hectare']}")
    
    def test_advanced_enhanced_engine_initialization(self):
        """Test advanced enhanced engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.crop_database)
        self.assertIsNotNone(self.engine.advanced_algorithm)
        self.assertIsNotNone(self.engine.yield_calculator)
        self.assertIsNotNone(self.engine.input_system)
        
        print("✅ Advanced enhanced engine initialized successfully")
    
    def test_enhanced_crop_recommendations_structure(self):
        """Test enhanced crop recommendations structure."""
        recommendations = self.engine.get_enhanced_crop_recommendations(
            lat=-13.9626,  # Lilongwe
            lon=33.7741,
            season='rainy_season',
            rainfall_mm=450,
            temperature=26,
            farmer_profile=self.test_farmer_profile,
            historical_years=3
        )
        
        # Verify main structure
        self.assertIn('status', recommendations)
        self.assertIn('recommendations', recommendations)
        self.assertIn('environmental_factors', recommendations)
        self.assertIn('historical_data_summary', recommendations)
        self.assertIn('region', recommendations)
        self.assertIn('data_sources', recommendations)
        self.assertIn('algorithm_version', recommendations)
        
        # Verify status
        self.assertEqual(recommendations['status'], 200)
        
        # Verify recommendations
        recs = recommendations['recommendations']
        self.assertIsInstance(recs, list)
        self.assertGreater(len(recs), 0)
        self.assertLessEqual(len(recs), 3)  # Top 3 crops
        
        # Verify first recommendation structure
        if recs:
            first_rec = recs[0]
            self.assertIn('crop_id', first_rec)
            self.assertIn('crop_name', first_rec)
            self.assertIn('suitability_score', first_rec)
            self.assertIn('confidence', first_rec)
            self.assertIn('recommendation_level', first_rec)
            self.assertIn('factor_scores', first_rec)
            self.assertIn('risk_factors', first_rec)
            self.assertIn('top_varieties', first_rec)
            self.assertIn('yield_projections', first_rec)
            self.assertIn('input_recommendations', first_rec)
            self.assertIn('planting_guidelines', first_rec)
            self.assertIn('data_sources', first_rec)
            self.assertIn('algorithm_version', first_rec)
        
        print("✅ Enhanced crop recommendations structure verified")
        print(f"   Number of recommendations: {len(recs)}")
        if recs:
            print(f"   Top crop: {recs[0]['crop_name']}")
            print(f"   Suitability score: {recs[0]['suitability_score']:.3f}")
            print(f"   Confidence: {recs[0]['confidence']:.3f}")
    
    def test_real_data_sources_only(self):
        """Test that only real data sources are used."""
        recommendations = self.engine.get_enhanced_crop_recommendations(
            lat=-13.9626,  # Lilongwe
            lon=33.7741,
            season='rainy_season',
            rainfall_mm=450,
            temperature=26,
            farmer_profile=self.test_farmer_profile,
            historical_years=3
        )
        
        # Verify data sources
        data_sources = recommendations['data_sources']
        expected_sources = [
            'real_crop_varieties_database',
            'real_historical_weather_data',
            'advanced_crop_algorithm',
            'advanced_yield_calculator',
            'advanced_input_system'
        ]
        
        for expected_source in expected_sources:
            self.assertIn(expected_source, data_sources)
        
        # Verify no mock data sources
        mock_sources = ['mock_data', 'sample_data', 'test_data', 'dummy_data']
        for mock_source in mock_sources:
            self.assertNotIn(mock_source, data_sources)
        
        # Verify individual recommendation data sources
        for rec in recommendations['recommendations']:
            rec_sources = rec['data_sources']
            for expected_source in expected_sources:
                self.assertIn(expected_source, rec_sources)
        
        print("✅ Real data sources verified - no mock data used")
    
    def test_algorithm_version(self):
        """Test algorithm version is correct."""
        recommendations = self.engine.get_enhanced_crop_recommendations(
            lat=-13.9626,  # Lilongwe
            lon=33.7741,
            season='rainy_season',
            rainfall_mm=450,
            temperature=26,
            farmer_profile=self.test_farmer_profile,
            historical_years=3
        )
        
        # Verify algorithm version
        self.assertEqual(recommendations['algorithm_version'], 'advanced_enhanced_v2.0')
        
        # Verify individual recommendation algorithm versions
        for rec in recommendations['recommendations']:
            self.assertEqual(rec['algorithm_version'], 'advanced_enhanced_v2.0')
        
        print("✅ Algorithm version verified: advanced_enhanced_v2.0")


def run_advanced_enhanced_tests():
    """Run all advanced enhanced tests."""
    print("🧪 Testing Advanced Enhanced Crop Recommendation Engine")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestAdvancedEnhancedCropRecommendationEngine)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Advanced Enhanced Test Summary")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests) * 100
    
    print(f"Total Tests: {total_tests}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failures > 0:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if errors > 0:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if failures == 0 and errors == 0:
        print("\n🎉 All Advanced Enhanced tests passed!")
        print("✅ Advanced Enhanced Crop Recommendation Engine is working correctly")
        print("✅ All components integrated successfully")
        print("✅ Real data sources verified")
        print("✅ Advanced algorithms functioning")
    else:
        print(f"\n⚠️  {failures + errors} test(s) failed")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_advanced_enhanced_tests()
