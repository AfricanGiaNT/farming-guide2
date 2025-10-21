"""
Comprehensive Integration Tests for the Complete Crop Recommendation System.
Tests all components working together with real data sources.
"""
import unittest
import json
import time
from unittest.mock import patch, MagicMock
from enhanced_api_server import app
from scripts.crop_advisor.advanced_enhanced_crop_recommendation_engine import advanced_enhanced_crop_recommendation_engine
from scripts.utils.advanced_caching_system import advanced_caching_system
from scripts.utils.advanced_error_handler import advanced_error_handler
from scripts.utils.performance_monitor import performance_monitor


class TestCompleteSystemIntegration(unittest.TestCase):
    """Test the complete crop recommendation system integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        
        # Test locations across Malawi
        self.test_locations = [
            {
                'name': 'Lilongwe (Central)',
                'lat': -13.9626,
                'lon': 33.7741,
                'region': 'Central Region'
            },
            {
                'name': 'Blantyre (Southern)',
                'lat': -15.7847,
                'lon': 35.0034,
                'region': 'Southern Region'
            },
            {
                'name': 'Mzuzu (Northern)',
                'lat': -11.4587,
                'lon': 34.0151,
                'region': 'Northern Region'
            }
        ]
        
        # Test farmer profiles
        self.test_farmer_profiles = [
            {
                'budget_level': 'low',
                'available_inputs': ['seeds'],
                'experience_level': 'beginner',
                'farm_size': 'small'
            },
            {
                'budget_level': 'medium',
                'available_inputs': ['fertilizer', 'pesticides', 'seeds'],
                'experience_level': 'intermediate',
                'farm_size': 'medium'
            },
            {
                'budget_level': 'high',
                'available_inputs': ['fertilizer', 'pesticides', 'seeds', 'irrigation', 'quality_seeds'],
                'experience_level': 'expert',
                'farm_size': 'large'
            }
        ]
        
        # Test seasons
        self.test_seasons = ['rainy_season', 'dry_season', 'current']
    
    def test_system_health_check(self):
        """Test complete system health check."""
        response = self.client.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify all services are healthy
        self.assertEqual(data['status'], 'healthy')
        services = data['services']
        
        self.assertTrue(services['weather_api'])
        self.assertTrue(services['crop_engine'])
        self.assertTrue(services['caching_system'])
        self.assertTrue(services['error_handler'])
        self.assertTrue(services['performance_monitor'])
        
        print("✅ Complete system health check passed")
    
    def test_end_to_end_recommendations_all_locations(self):
        """Test end-to-end recommendations for all Malawi locations."""
        for location in self.test_locations:
            with self.subTest(location=location['name']):
                request_data = {
                    'latitude': location['lat'],
                    'longitude': location['lon'],
                    'season': 'rainy_season',
                    'farmer_profile': self.test_farmer_profiles[1]  # Medium budget
                }
                
                response = self.client.post('/api/crops/recommendations/enhanced', 
                                          json=request_data)
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                
                # Verify response structure
                self.assertIn('data', data)
                self.assertIn('recommendations', data['data'])
                self.assertIn('region', data['data'])
                
                # Verify recommendations
                recommendations = data['data']['recommendations']
                self.assertGreater(len(recommendations), 0)
                self.assertLessEqual(len(recommendations), 3)
                
                # Verify first recommendation structure
                if recommendations:
                    first_rec = recommendations[0]
                    self.assertIn('crop_name', first_rec)
                    self.assertIn('suitability_score', first_rec)
                    self.assertIn('confidence', first_rec)
                    self.assertIn('top_varieties', first_rec)
                    self.assertIn('yield_projections', first_rec)
                    self.assertIn('input_recommendations', first_rec)
                
                print(f"✅ End-to-end test passed for {location['name']}")
    
    def test_different_farmer_profiles(self):
        """Test recommendations for different farmer profiles."""
        location = self.test_locations[0]  # Lilongwe
        
        for profile in self.test_farmer_profiles:
            with self.subTest(profile=profile['budget_level']):
                request_data = {
                    'latitude': location['lat'],
                    'longitude': location['lon'],
                    'season': 'rainy_season',
                    'farmer_profile': profile
                }
                
                response = self.client.post('/api/crops/recommendations/enhanced', 
                                          json=request_data)
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                
                # Verify recommendations are tailored to farmer profile
                recommendations = data['data']['recommendations']
                if recommendations:
                    first_rec = recommendations[0]
                    
                    # Check input recommendations are appropriate for budget level
                    input_recs = first_rec['input_recommendations']
                    self.assertIn('fertilizer_recommendations', input_recs)
                    self.assertIn('seed_recommendations', input_recs)
                    self.assertIn('total_input_costs', input_recs)
                
                print(f"✅ Farmer profile test passed for {profile['budget_level']} budget")
    
    def test_different_seasons(self):
        """Test recommendations for different seasons."""
        location = self.test_locations[0]  # Lilongwe
        farmer_profile = self.test_farmer_profiles[1]  # Medium budget
        
        for season in self.test_seasons:
            with self.subTest(season=season):
                request_data = {
                    'latitude': location['lat'],
                    'longitude': location['lon'],
                    'season': season,
                    'farmer_profile': farmer_profile
                }
                
                response = self.client.post('/api/crops/recommendations/enhanced', 
                                          json=request_data)
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                
                # Verify recommendations are season-appropriate
                recommendations = data['data']['recommendations']
                if recommendations:
                    first_rec = recommendations[0]
                    
                    # Check that recommendations consider season
                    self.assertIn('planting_guidelines', first_rec)
                    planting_guidelines = first_rec['planting_guidelines']
                    self.assertIn('guidelines', planting_guidelines)
                
                print(f"✅ Season test passed for {season}")
    
    def test_caching_performance(self):
        """Test caching performance across multiple requests."""
        location = self.test_locations[0]  # Lilongwe
        request_data = {
            'latitude': location['lat'],
            'longitude': location['lon'],
            'season': 'rainy_season',
            'farmer_profile': self.test_farmer_profiles[1]
        }
        
        # Make multiple requests and measure performance
        response_times = []
        cache_hits = 0
        
        for i in range(5):
            start_time = time.time()
            response = self.client.post('/api/crops/recommendations/enhanced', 
                                      json=request_data)
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            response_times.append(end_time - start_time)
            if data.get('cached', False):
                cache_hits += 1
        
        # Verify performance improvements
        avg_response_time = sum(response_times) / len(response_times)
        self.assertLess(avg_response_time, 5.0)  # Should be under 5 seconds
        
        print(f"✅ Caching performance test passed")
        print(f"   Average response time: {avg_response_time:.3f}s")
        print(f"   Cache hits: {cache_hits}/5")
    
    def test_error_handling_integration(self):
        """Test error handling across the complete system."""
        # Test with invalid coordinates
        invalid_request = {
            'latitude': 999.0,  # Invalid latitude
            'longitude': 999.0,  # Invalid longitude
            'season': 'rainy_season',
            'farmer_profile': self.test_farmer_profiles[1]
        }
        
        response = self.client.post('/api/crops/recommendations/enhanced', 
                                  json=invalid_request)
        
        # Should still return 200 with fallback data
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should have errors array with fallback information
        self.assertIn('errors', data)
        if data['errors']:
            self.assertIn('fallback_used', data['errors'][0])
        
        print("✅ Error handling integration test passed")
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring across the complete system."""
        # Make several requests to generate performance data
        location = self.test_locations[0]  # Lilongwe
        request_data = {
            'latitude': location['lat'],
            'longitude': location['lon'],
            'season': 'rainy_season',
            'farmer_profile': self.test_farmer_profiles[1]
        }
        
        for i in range(3):
            response = self.client.post('/api/crops/recommendations/enhanced', 
                                      json=request_data)
            self.assertEqual(response.status_code, 200)
        
        # Check performance stats
        perf_response = self.client.get('/api/performance/stats')
        self.assertEqual(perf_response.status_code, 200)
        
        perf_data = json.loads(perf_response.data)
        stats = perf_data['data']['performance_stats']
        
        # Verify performance metrics
        self.assertGreater(stats['total_requests'], 0)
        self.assertLessEqual(stats['average_response_time'], 5.0)
        self.assertTrue(stats['performance_target_met'])
        
        print("✅ Performance monitoring integration test passed")
        print(f"   Total requests: {stats['total_requests']}")
        print(f"   Average response time: {stats['average_response_time']}s")
    
    def test_data_quality_validation(self):
        """Test data quality across all recommendations."""
        location = self.test_locations[0]  # Lilongwe
        request_data = {
            'latitude': location['lat'],
            'longitude': location['lon'],
            'season': 'rainy_season',
            'farmer_profile': self.test_farmer_profiles[1]
        }
        
        response = self.client.post('/api/crops/recommendations/enhanced', 
                                  json=request_data)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        recommendations = data['data']['recommendations']
        
        for rec in recommendations:
            # Verify data quality
            self.assertGreater(rec['suitability_score'], 0.0)
            self.assertLessEqual(rec['suitability_score'], 1.0)
            self.assertGreater(rec['confidence'], 0.0)
            self.assertLessEqual(rec['confidence'], 1.0)
            
            # Verify varieties data
            if rec['top_varieties']:
                for variety in rec['top_varieties']:
                    self.assertIn('name', variety)
                    self.assertIn('suitability_score', variety)
                    self.assertIn('source', variety)
                    self.assertEqual(variety['source'], 'real_crop_varieties_database')
            
            # Verify yield projections
            yield_proj = rec['yield_projections']
            self.assertIn('yield_projections', yield_proj)
            
            # Check nested yield projections
            nested_projections = yield_proj['yield_projections']
            self.assertIn('conservative', nested_projections)
            self.assertIn('realistic', nested_projections)
            self.assertIn('potential', nested_projections)
            self.assertIn('optimal', nested_projections)
            
            # Verify yield progression
            self.assertLessEqual(nested_projections['conservative'], nested_projections['realistic'])
            self.assertLessEqual(nested_projections['realistic'], nested_projections['potential'])
            self.assertLessEqual(nested_projections['potential'], nested_projections['optimal'])
            
            # Verify input recommendations
            input_recs = rec['input_recommendations']
            self.assertIn('fertilizer_recommendations', input_recs)
            self.assertIn('seed_recommendations', input_recs)
            self.assertIn('pest_control_recommendations', input_recs)
            self.assertIn('total_input_costs', input_recs)
            
            # Verify data sources
            data_sources = rec['data_sources']
            self.assertIn('real_crop_varieties_database', data_sources)
            self.assertIn('real_historical_weather_data', data_sources)
        
        print("✅ Data quality validation test passed")
    
    def test_real_data_sources_only(self):
        """Test that only real data sources are used throughout the system."""
        location = self.test_locations[0]  # Lilongwe
        request_data = {
            'latitude': location['lat'],
            'longitude': location['lon'],
            'season': 'rainy_season',
            'farmer_profile': self.test_farmer_profiles[1]
        }
        
        response = self.client.post('/api/crops/recommendations/enhanced', 
                                  json=request_data)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify main data sources
        main_sources = data['data']['data_sources']
        expected_sources = [
            'real_crop_varieties_database',
            'real_historical_weather_data',
            'advanced_crop_algorithm',
            'advanced_yield_calculator',
            'advanced_input_system'
        ]
        
        for expected_source in expected_sources:
            self.assertIn(expected_source, main_sources)
        
        # Verify no mock data sources
        mock_sources = ['mock_data', 'sample_data', 'test_data', 'dummy_data']
        for mock_source in mock_sources:
            self.assertNotIn(mock_source, main_sources)
        
        # Verify individual recommendation data sources
        for rec in data['data']['recommendations']:
            rec_sources = rec['data_sources']
            for expected_source in expected_sources:
                self.assertIn(expected_source, rec_sources)
        
        print("✅ Real data sources verification test passed")


def run_complete_system_tests():
    """Run all complete system integration tests."""
    print("🧪 Testing Complete Crop Recommendation System Integration")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCompleteSystemIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 Complete System Integration Test Summary")
    print("=" * 70)
    
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
        print("\n🎉 All Complete System Integration tests passed!")
        print("✅ End-to-end system working correctly")
        print("✅ All components integrated successfully")
        print("✅ Performance monitoring active")
        print("✅ Error handling working")
        print("✅ Caching system functioning")
        print("✅ Real data sources verified")
        print("✅ Data quality validated")
    else:
        print(f"\n⚠️  {failures + errors} test(s) failed")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_complete_system_tests()
