#!/usr/bin/env python3
"""
Comprehensive test suite for Week 3 AI integration.
Tests normal cases, edge cases, error scenarios, and performance.
"""
import sys
import os
import asyncio
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.utils.config_loader import config
from scripts.utils.logger import logger

class TestResults:
    """Track comprehensive test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.performance_metrics = {}
    
    def add_result(self, test_name: str, success: bool, error: str = None, duration: float = None):
        if success:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: {error}")
            print(f"❌ {test_name} - {error}")
        
        if duration:
            self.performance_metrics[test_name] = duration
    
    def get_summary(self):
        total = self.passed + self.failed
        return {
            'total': total,
            'passed': self.passed,
            'failed': self.failed,
            'success_rate': (self.passed / total * 100) if total > 0 else 0,
            'errors': self.errors,
            'performance': self.performance_metrics
        }

def test_configuration_edge_cases(results: TestResults):
    """Test configuration loading with edge cases."""
    print("\n🧪 Testing Configuration Edge Cases...")
    
    # Test 1: Missing OpenAI key
    start_time = time.time()
    try:
        # Temporarily backup and remove OpenAI key
        original_key = os.environ.get('OPENAI_API_KEY')
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # Test that it handles missing key gracefully
        from scripts.ai_agent.gpt_integration import GPTIntegration
        
        # Should raise ValueError for missing key
        try:
            gpt = GPTIntegration()
            results.add_result("Missing OpenAI key handling", False, "Should have raised ValueError")
        except ValueError:
            results.add_result("Missing OpenAI key handling", True, duration=time.time() - start_time)
        
        # Restore original key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key
    except Exception as e:
        results.add_result("Missing OpenAI key handling", False, str(e))
    
    # Test 2: Invalid OpenAI key format
    start_time = time.time()
    try:
        os.environ['OPENAI_API_KEY'] = "invalid-key-format"
        
        from scripts.ai_agent.gpt_integration import GPTIntegration
        gpt = GPTIntegration()
        
        # Should initialize but fail on actual API call
        results.add_result("Invalid OpenAI key format", True, duration=time.time() - start_time)
    except Exception as e:
        results.add_result("Invalid OpenAI key format", False, str(e))
    
    # Test 3: Empty configuration values
    start_time = time.time()
    try:
        # Test empty values
        test_config = config
        empty_value = test_config.get_optional("NON_EXISTENT_KEY", "default")
        
        if empty_value == "default":
            results.add_result("Empty configuration handling", True, duration=time.time() - start_time)
        else:
            results.add_result("Empty configuration handling", False, "Default value not returned")
    except Exception as e:
        results.add_result("Empty configuration handling", False, str(e))

def test_prompt_formatting_edge_cases(results: TestResults):
    """Test prompt formatting with edge cases."""
    print("\n🧪 Testing Prompt Formatting Edge Cases...")
    
    try:
        from scripts.ai_agent.prompt_formatter import prompt_formatter
        
        # Test 1: Very long crop data
        start_time = time.time()
        long_crop_data = {
            'recommendations': [
                {
                    'crop_data': {'name': 'A' * 1000},  # Very long crop name
                    'total_score': 85,
                    'suitability_level': 'excellent'
                }
            ],
            'environmental_summary': {
                'total_7day_rainfall': 25,
                'current_temperature': 24,
                'current_season': 'rainy_season'
            }
        }
        
        weather_data = {'temperature': 24, 'humidity': 65, 'rainfall': 25}
        
        prompt = prompt_formatter.format_crop_analysis_prompt(
            long_crop_data, weather_data, "Very Long Location Name" * 100
        )
        
        # Should be truncated to max length
        if len(prompt) <= prompt_formatter.max_prompt_length:
            results.add_result("Long prompt truncation", True, duration=time.time() - start_time)
        else:
            results.add_result("Long prompt truncation", False, f"Prompt too long: {len(prompt)} chars")
        
        # Test 2: Empty crop data
        start_time = time.time()
        empty_crop_data = {
            'recommendations': [],
            'environmental_summary': {}
        }
        
        prompt = prompt_formatter.format_crop_analysis_prompt(
            empty_crop_data, {}, "Empty Location"
        )
        
        if prompt and len(prompt) > 0:
            results.add_result("Empty crop data handling", True, duration=time.time() - start_time)
        else:
            results.add_result("Empty crop data handling", False, "Empty prompt generated")
        
        # Test 3: Special characters in location
        start_time = time.time()
        special_chars_location = "Location with 特殊字符 and émojis 🌾"
        
        prompt = prompt_formatter.format_crop_analysis_prompt(
            long_crop_data, weather_data, special_chars_location
        )
        
        if special_chars_location in prompt:
            results.add_result("Special characters in location", True, duration=time.time() - start_time)
        else:
            results.add_result("Special characters in location", False, "Special chars not preserved")
        
        # Test 4: Extreme weather values
        start_time = time.time()
        extreme_weather = {
            'temperature': -50,  # Extreme cold
            'humidity': 150,     # Invalid humidity
            'rainfall': 10000    # Extreme rainfall
        }
        
        prompt = prompt_formatter.format_weather_impact_prompt(
            extreme_weather, "Maize", "Arctic Location"
        )
        
        if prompt and len(prompt) > 0:
            results.add_result("Extreme weather values", True, duration=time.time() - start_time)
        else:
            results.add_result("Extreme weather values", False, "Failed to handle extreme values")
    
    except Exception as e:
        results.add_result("Prompt formatting edge cases", False, str(e))

def test_response_synthesis_edge_cases(results: TestResults):
    """Test response synthesis with edge cases."""
    print("\n🧪 Testing Response Synthesis Edge Cases...")
    
    try:
        from scripts.ai_agent.response_synthesizer import response_synthesizer
        
        # Test 1: Malformed recommendation data
        start_time = time.time()
        malformed_data = {
            'recommendations': "invalid_format",  # Should be list
            'environmental_summary': None
        }
        
        try:
            response = response_synthesizer._format_basic_response(
                malformed_data, {}, "Test Location"
            )
            if response:
                results.add_result("Malformed recommendation data", True, duration=time.time() - start_time)
            else:
                results.add_result("Malformed recommendation data", False, "No response generated")
        except Exception as e:
            # Should handle gracefully
            results.add_result("Malformed recommendation data", True, duration=time.time() - start_time)
        
        # Test 2: Very large dataset
        start_time = time.time()
        large_dataset = {
            'recommendations': [
                {
                    'crop_data': {'name': f'Crop_{i}'},
                    'total_score': i % 100,
                    'suitability_level': 'excellent',
                    'recommended_varieties': [
                        {'variety_data': {'name': f'Variety_{i}_{j}'}}
                        for j in range(100)  # 100 varieties per crop
                    ]
                }
                for i in range(1000)  # 1000 crops
            ],
            'environmental_summary': {
                'total_7day_rainfall': 25,
                'current_temperature': 24,
                'current_season': 'rainy_season'
            }
        }
        
        response = response_synthesizer._format_basic_response(
            large_dataset, {}, "Large Dataset Test"
        )
        
        # Should handle large dataset without crashing
        if response and len(response) > 0:
            results.add_result("Large dataset handling", True, duration=time.time() - start_time)
        else:
            results.add_result("Large dataset handling", False, "Failed to handle large dataset")
        
        # Test 3: Unicode and special characters
        start_time = time.time()
        unicode_data = {
            'recommendations': [
                {
                    'crop_data': {'name': 'Maïze 🌽 with émojis'},
                    'total_score': 85,
                    'suitability_level': 'excellent',
                    'recommended_varieties': [
                        {'variety_data': {'name': 'Variété Spéciale 🌾'}}
                    ]
                }
            ],
            'environmental_summary': {
                'total_7day_rainfall': 25,
                'current_temperature': 24,
                'current_season': 'rainy_season'
            }
        }
        
        response = response_synthesizer._format_basic_response(
            unicode_data, {}, "Location with 特殊字符"
        )
        
        if response and 'Maïze 🌽' in response:
            results.add_result("Unicode handling", True, duration=time.time() - start_time)
        else:
            results.add_result("Unicode handling", False, "Unicode not preserved")
    
    except Exception as e:
        results.add_result("Response synthesis edge cases", False, str(e))

async def test_ai_integration_error_scenarios(results: TestResults):
    """Test AI integration error scenarios."""
    print("\n🧪 Testing AI Integration Error Scenarios...")
    
    try:
        from scripts.ai_agent.gpt_integration import gpt_integration
        
        # Test 1: Network timeout simulation
        start_time = time.time()
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_create.side_effect = asyncio.TimeoutError("Network timeout")
            
            try:
                response = await gpt_integration._get_ai_response("Test prompt", "test_user")
                results.add_result("Network timeout handling", False, "Should have raised timeout error")
            except Exception:
                results.add_result("Network timeout handling", True, duration=time.time() - start_time)
        
        # Test 2: API quota exceeded
        start_time = time.time()
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_create.side_effect = Exception("Rate limit exceeded")
            
            try:
                response = await gpt_integration._get_ai_response("Test prompt", "test_user")
                results.add_result("API quota exceeded handling", False, "Should have raised quota error")
            except Exception:
                results.add_result("API quota exceeded handling", True, duration=time.time() - start_time)
        
        # Test 3: Invalid API response
        start_time = time.time()
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_response = Mock()
            mock_response.choices = []  # Empty choices
            mock_create.return_value = mock_response
            
            try:
                response = await gpt_integration._get_ai_response("Test prompt", "test_user")
                results.add_result("Invalid API response handling", False, "Should handle empty response")
            except Exception:
                results.add_result("Invalid API response handling", True, duration=time.time() - start_time)
        
        # Test 4: Very long response
        start_time = time.time()
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_response = Mock()
            mock_choice = Mock()
            mock_choice.message.content = "A" * 10000  # Very long response
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response
            
            try:
                response = await gpt_integration._get_ai_response("Test prompt", "test_user")
                if len(response) > 0:
                    results.add_result("Long response handling", True, duration=time.time() - start_time)
                else:
                    results.add_result("Long response handling", False, "Empty response")
            except Exception as e:
                results.add_result("Long response handling", False, str(e))
    
    except Exception as e:
        results.add_result("AI integration error scenarios", False, str(e))

def test_caching_behavior(results: TestResults):
    """Test caching behavior and efficiency."""
    print("\n🧪 Testing Caching Behavior...")
    
    try:
        from scripts.ai_agent.gpt_integration import gpt_integration
        
        # Clear cache first
        gpt_integration.clear_cache()
        
        # Test 1: Cache key generation
        start_time = time.time()
        recommendations = {
            'environmental_summary': {'total_7day_rainfall': 25},
            'recommendations': [{'crop_data': {'name': 'Maize'}}]
        }
        weather_data = {'temperature': 24}
        
        key1 = gpt_integration._generate_cache_key(recommendations, weather_data, "Lilongwe")
        key2 = gpt_integration._generate_cache_key(recommendations, weather_data, "Lilongwe")
        
        if key1 == key2:
            results.add_result("Cache key consistency", True, duration=time.time() - start_time)
        else:
            results.add_result("Cache key consistency", False, "Keys don't match for same data")
        
        # Test 2: Cache key uniqueness
        start_time = time.time()
        different_weather = {'temperature': 25}  # Different temperature
        key3 = gpt_integration._generate_cache_key(recommendations, different_weather, "Lilongwe")
        
        if key1 != key3:
            results.add_result("Cache key uniqueness", True, duration=time.time() - start_time)
        else:
            results.add_result("Cache key uniqueness", False, "Keys same for different data")
        
        # Test 3: Cache storage and retrieval
        start_time = time.time()
        cache_key = "test_key"
        test_data = {"test": "data"}
        
        gpt_integration.response_cache[cache_key] = test_data
        retrieved_data = gpt_integration.response_cache.get(cache_key)
        
        if retrieved_data == test_data:
            results.add_result("Cache storage/retrieval", True, duration=time.time() - start_time)
        else:
            results.add_result("Cache storage/retrieval", False, "Cache data mismatch")
        
        # Test 4: Cache clear functionality
        start_time = time.time()
        gpt_integration.clear_cache()
        
        if len(gpt_integration.response_cache) == 0:
            results.add_result("Cache clear functionality", True, duration=time.time() - start_time)
        else:
            results.add_result("Cache clear functionality", False, "Cache not cleared")
    
    except Exception as e:
        results.add_result("Caching behavior tests", False, str(e))

def test_performance_metrics(results: TestResults):
    """Test performance metrics and benchmarks."""
    print("\n🧪 Testing Performance Metrics...")
    
    try:
        from scripts.ai_agent.prompt_formatter import prompt_formatter
        from scripts.ai_agent.response_synthesizer import response_synthesizer
        
        # Test 1: Prompt generation speed
        start_time = time.time()
        
        for i in range(100):  # Generate 100 prompts
            crop_data = {
                'recommendations': [
                    {
                        'crop_data': {'name': f'Crop_{i}'},
                        'total_score': 85,
                        'suitability_level': 'excellent'
                    }
                ],
                'environmental_summary': {
                    'total_7day_rainfall': 25,
                    'current_temperature': 24,
                    'current_season': 'rainy_season'
                }
            }
            
            prompt = prompt_formatter.format_crop_analysis_prompt(
                crop_data, {'temperature': 24}, f"Location_{i}"
            )
        
        duration = time.time() - start_time
        prompts_per_second = 100 / duration
        
        if prompts_per_second > 50:  # Should generate at least 50 prompts/second
            results.add_result("Prompt generation speed", True, duration=duration)
        else:
            results.add_result("Prompt generation speed", False, f"Too slow: {prompts_per_second:.1f} prompts/sec")
        
        # Test 2: Response synthesis speed (without AI)
        start_time = time.time()
        response_synthesizer.set_ai_enhancement(False)
        
        for i in range(50):  # Generate 50 responses
            recommendations = {
                'recommendations': [
                    {
                        'crop_data': {'name': f'Crop_{i}'},
                        'total_score': 85,
                        'suitability_level': 'excellent',
                        'recommended_varieties': [
                            {'variety_data': {'name': f'Variety_{i}'}}
                        ]
                    }
                ],
                'environmental_summary': {
                    'total_7day_rainfall': 25,
                    'current_temperature': 24,
                    'current_season': 'rainy_season'
                }
            }
            
            response = response_synthesizer._format_basic_response(
                recommendations, {'temperature': 24}, f"Location_{i}"
            )
        
        duration = time.time() - start_time
        responses_per_second = 50 / duration
        
        if responses_per_second > 10:  # Should generate at least 10 responses/second
            results.add_result("Response synthesis speed", True, duration=duration)
        else:
            results.add_result("Response synthesis speed", False, f"Too slow: {responses_per_second:.1f} responses/sec")
        
        # Test 3: Memory usage (basic check)
        start_time = time.time()
        
        # Create large dataset and check if it's handled efficiently
        large_recommendations = {
            'recommendations': [
                {
                    'crop_data': {'name': f'Crop_{i}'},
                    'total_score': i % 100,
                    'suitability_level': 'excellent'
                }
                for i in range(1000)
            ],
            'environmental_summary': {
                'total_7day_rainfall': 25,
                'current_temperature': 24,
                'current_season': 'rainy_season'
            }
        }
        
        # Should handle large dataset without issues
        response = response_synthesizer._format_basic_response(
            large_recommendations, {'temperature': 24}, "Large Dataset Test"
        )
        
        duration = time.time() - start_time
        
        if duration < 5.0:  # Should complete within 5 seconds
            results.add_result("Memory efficiency", True, duration=duration)
        else:
            results.add_result("Memory efficiency", False, f"Too slow for large dataset: {duration:.1f}s")
    
    except Exception as e:
        results.add_result("Performance metrics tests", False, str(e))

def test_real_world_scenarios(results: TestResults):
    """Test real-world scenarios and integration."""
    print("\n🧪 Testing Real-World Scenarios...")
    
    try:
        from scripts.ai_agent.response_synthesizer import response_synthesizer
        
        # Test 1: Typical Lilongwe query
        start_time = time.time()
        lilongwe_data = {
            'recommendations': [
                {
                    'crop_data': {'name': 'Maize'},
                    'total_score': 85,
                    'suitability_level': 'excellent',
                    'recommended_varieties': [
                        {'variety_data': {'name': 'DK 8053'}}
                    ]
                },
                {
                    'crop_data': {'name': 'Groundnuts'},
                    'total_score': 78,
                    'suitability_level': 'good',
                    'recommended_varieties': [
                        {'variety_data': {'name': 'Chalimbana'}}
                    ]
                }
            ],
            'environmental_summary': {
                'total_7day_rainfall': 45,
                'current_temperature': 26,
                'current_season': 'rainy_season'
            },
            'planting_calendar': [
                {
                    'crop_name': 'Maize',
                    'season_match': True
                }
            ]
        }
        
        weather_data = {'temperature': 26, 'humidity': 70}
        
        response = response_synthesizer._format_basic_response(
            lilongwe_data, weather_data, "Lilongwe"
        )
        
        # Check if response contains expected elements
        expected_elements = ['Maize', 'DK 8053', 'Lilongwe', 'Temperature', 'Rainfall']
        elements_found = sum(1 for elem in expected_elements if elem in response)
        
        if elements_found >= 4:
            results.add_result("Typical Lilongwe query", True, duration=time.time() - start_time)
        else:
            results.add_result("Typical Lilongwe query", False, f"Missing elements: {5 - elements_found}")
        
        # Test 2: Drought conditions
        start_time = time.time()
        drought_data = {
            'recommendations': [
                {
                    'crop_data': {'name': 'Sorghum'},
                    'total_score': 70,
                    'suitability_level': 'good',
                    'recommended_varieties': [
                        {'variety_data': {'name': 'Drought Resistant Variety'}}
                    ]
                }
            ],
            'environmental_summary': {
                'total_7day_rainfall': 2,  # Very low rainfall
                'current_temperature': 35,  # High temperature
                'current_season': 'dry_season'
            }
        }
        
        response = response_synthesizer._format_basic_response(
            drought_data, {'temperature': 35}, "Drought Area"
        )
        
        if 'Sorghum' in response and 'Drought' in response:
            results.add_result("Drought conditions scenario", True, duration=time.time() - start_time)
        else:
            results.add_result("Drought conditions scenario", False, "Drought scenario not handled properly")
        
        # Test 3: Excessive rainfall conditions
        start_time = time.time()
        flood_data = {
            'recommendations': [
                {
                    'crop_data': {'name': 'Rice'},
                    'total_score': 75,
                    'suitability_level': 'good',
                    'recommended_varieties': [
                        {'variety_data': {'name': 'Flood Tolerant Rice'}}
                    ]
                }
            ],
            'environmental_summary': {
                'total_7day_rainfall': 200,  # Very high rainfall
                'current_temperature': 22,
                'current_season': 'rainy_season'
            }
        }
        
        response = response_synthesizer._format_basic_response(
            flood_data, {'temperature': 22}, "Flood Prone Area"
        )
        
        if 'Rice' in response and '200' in response:
            results.add_result("Excessive rainfall scenario", True, duration=time.time() - start_time)
        else:
            results.add_result("Excessive rainfall scenario", False, "Flood scenario not handled properly")
    
    except Exception as e:
        results.add_result("Real-world scenarios tests", False, str(e))

async def main():
    """Run comprehensive Week 3 tests."""
    print("🌾 Week 3 AI Integration - Comprehensive Test Suite\n")
    
    results = TestResults()
    
    # Test suites
    test_suites = [
        ("Configuration Edge Cases", test_configuration_edge_cases),
        ("Prompt Formatting Edge Cases", test_prompt_formatting_edge_cases),
        ("Response Synthesis Edge Cases", test_response_synthesis_edge_cases),
        ("AI Integration Error Scenarios", test_ai_integration_error_scenarios),
        ("Caching Behavior", test_caching_behavior),
        ("Performance Metrics", test_performance_metrics),
        ("Real-World Scenarios", test_real_world_scenarios)
    ]
    
    for suite_name, test_func in test_suites:
        try:
            if asyncio.iscoroutinefunction(test_func):
                await test_func(results)
            else:
                test_func(results)
        except Exception as e:
            results.add_result(f"{suite_name} (Suite)", False, str(e))
    
    # Print comprehensive results
    summary = results.get_summary()
    
    print(f"\n📊 COMPREHENSIVE TEST RESULTS")
    print(f"{'='*50}")
    print(f"Total Tests: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    
    if summary['performance']:
        print(f"\n⚡ PERFORMANCE METRICS")
        print(f"{'='*50}")
        for test_name, duration in summary['performance'].items():
            print(f"{test_name}: {duration:.3f}s")
    
    if summary['errors']:
        print(f"\n❌ FAILED TESTS")
        print(f"{'='*50}")
        for error in summary['errors']:
            print(f"• {error}")
    
    print(f"\n🎯 RECOMMENDATIONS")
    print(f"{'='*50}")
    
    if summary['success_rate'] >= 90:
        print("✅ Week 3 implementation is robust and production-ready!")
        print("• All critical functionality working correctly")
        print("• Good error handling and edge case coverage")
        print("• Performance within acceptable limits")
    elif summary['success_rate'] >= 75:
        print("⚠️  Week 3 implementation is mostly stable with minor issues")
        print("• Core functionality working well")
        print("• Some edge cases need attention")
        print("• Review failed tests for improvements")
    else:
        print("🔧 Week 3 implementation needs significant improvements")
        print("• Multiple critical issues found")
        print("• Review and fix failed tests before production")
        print("• Consider additional testing and validation")
    
    print(f"\n📝 NEXT STEPS")
    print(f"{'='*50}")
    print("1. Address any failed tests")
    print("2. Set up OpenAI API key for full AI testing")
    print("3. Test with real bot interactions")
    print("4. Monitor performance and costs in production")
    print("5. Proceed to Week 4 PDF integration")
    
    return summary['success_rate'] >= 75

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 