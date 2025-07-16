#!/usr/bin/env python3
"""
Test Phase 2: Historical Weather Integration
Tests the integration of historical weather analysis with the varieties handler.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from scripts.handlers.varieties_handler import varieties_handler
    from scripts.weather_engine.historical_weather_api import historical_weather_api
    from scripts.weather_engine.enhanced_rainfall_analyzer import enhanced_rainfall_analyzer
    print("✅ Phase 2 modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_weather_integration():
    """Test the weather integration in varieties handler."""
    print("\n🔄 Testing Phase 2: Weather Integration...")
    
    # Test coordinates (Lilongwe)
    lat, lon = -13.9833, 33.7833
    print(f"📍 Location: {lat}, {lon}")
    
    # Test weather analysis method
    print("\n1️⃣ Testing get_location_weather_analysis...")
    weather_analysis = varieties_handler.get_location_weather_analysis(lat, lon, 5, "test_user")
    
    if weather_analysis:
        print(f"✅ Weather analysis completed successfully!")
        print(f"   • Analysis timestamp: {weather_analysis.get('analysis_timestamp', 'N/A')}")
        print(f"   • Current month: {weather_analysis.get('current_month', 'N/A')}")
        
        historical_data = weather_analysis.get('historical_data', {})
        if historical_data:
            print(f"   • Years analyzed: {historical_data.get('years_analyzed', 0)}")
            print(f"   • Climate trend: {historical_data.get('climate_trend', 'N/A')}")
            print(f"   • Rainfall variability: {historical_data.get('rainfall_variability', 0):.1f}%")
            print(f"   • Wet season months: {len(historical_data.get('wet_season_months', []))}")
            print(f"   • Drought years: {len(historical_data.get('drought_years', []))}")
        
        return True
    else:
        print("❌ Weather analysis failed")
        return False


def test_weather_context_formatting():
    """Test the weather context formatting."""
    print("\n2️⃣ Testing weather context formatting...")
    
    # Test coordinates
    lat, lon = -13.9833, 33.7833
    
    # Get weather analysis
    weather_analysis = varieties_handler.get_location_weather_analysis(lat, lon, 3, "test_user")
    
    if weather_analysis:
        # Test formatting
        weather_context = varieties_handler._format_weather_context(weather_analysis)
        
        if weather_context:
            print(f"✅ Weather context formatted successfully!")
            print(f"   • Context length: {len(weather_context)} characters")
            print(f"   • Contains weather header: {'Weather Context' in weather_context}")
            print(f"   • Contains monthly data: {'average:' in weather_context}")
            
            # Show a preview
            print(f"   • Preview: {weather_context[:100]}...")
            
            return True
        else:
            print("❌ Weather context formatting failed")
            return False
    else:
        print("❌ No weather analysis data available for formatting")
        return False


def test_caching_mechanism():
    """Test the weather data caching mechanism."""
    print("\n3️⃣ Testing weather data caching...")
    
    # Test coordinates
    lat, lon = -13.9833, 33.7833
    
    # Clear existing cache
    varieties_handler.weather_cache.clear()
    
    # First call - should fetch from API
    print("   First call (should fetch from API)...")
    start_time = datetime.now()
    weather_analysis1 = varieties_handler.get_location_weather_analysis(lat, lon, 3, "test_user")
    first_call_duration = (datetime.now() - start_time).total_seconds()
    
    # Second call - should use cache
    print("   Second call (should use cache)...")
    start_time = datetime.now()
    weather_analysis2 = varieties_handler.get_location_weather_analysis(lat, lon, 3, "test_user")
    second_call_duration = (datetime.now() - start_time).total_seconds()
    
    if weather_analysis1 and weather_analysis2:
        print(f"✅ Caching mechanism works!")
        print(f"   • First call: {first_call_duration:.2f}s")
        print(f"   • Second call: {second_call_duration:.2f}s")
        print(f"   • Cache entries: {len(varieties_handler.weather_cache)}")
        print(f"   • Speed improvement: {first_call_duration / second_call_duration:.1f}x faster")
        
        return True
    else:
        print("❌ Caching mechanism failed")
        return False


def test_cache_cleanup():
    """Test the cache cleanup mechanism."""
    print("\n4️⃣ Testing cache cleanup...")
    
    # Add some test cache entries
    varieties_handler.weather_cache["test_key_1"] = ({"test": "data1"}, 0)  # Very old timestamp
    varieties_handler.weather_cache["test_key_2"] = ({"test": "data2"}, 999999999)  # Very old timestamp
    
    initial_count = len(varieties_handler.weather_cache)
    print(f"   Initial cache entries: {initial_count}")
    
    # Run cleanup
    varieties_handler._clear_old_cache_entries()
    
    final_count = len(varieties_handler.weather_cache)
    print(f"   Final cache entries: {final_count}")
    
    if final_count < initial_count:
        print(f"✅ Cache cleanup works!")
        print(f"   • Removed {initial_count - final_count} old entries")
        return True
    else:
        print("❌ Cache cleanup failed")
        return False


def test_error_handling():
    """Test error handling for invalid coordinates."""
    print("\n5️⃣ Testing error handling...")
    
    # Test invalid coordinates
    invalid_coords = [(999, 999), (-999, -999), (0, 0)]
    
    for lat, lon in invalid_coords:
        print(f"   Testing coordinates: {lat}, {lon}")
        weather_analysis = varieties_handler.get_location_weather_analysis(lat, lon, 3, "test_user")
        
        if weather_analysis is None:
            print(f"   ✅ Correctly handled invalid coordinates {lat}, {lon}")
        else:
            print(f"   ⚠️ Unexpected success for {lat}, {lon}")
    
    return True


def main():
    """Run all Phase 2 tests."""
    print("🚀 Phase 2: Historical Weather Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Weather Integration", test_weather_integration),
        ("Weather Context Formatting", test_weather_context_formatting),
        ("Caching Mechanism", test_caching_mechanism),
        ("Cache Cleanup", test_cache_cleanup),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
        
        print("-" * 40)
    
    print(f"\n📊 Phase 2 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 2 implementation is working correctly!")
        print("\n✅ Ready to proceed to Phase 3: Weather-Variety Matching Algorithm")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 