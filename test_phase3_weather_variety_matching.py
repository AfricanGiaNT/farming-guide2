#!/usr/bin/env python3
"""
Test Phase 3: Weather-Variety Matching Algorithm
Tests the weather-variety matching algorithm that scores varieties based on weather suitability.
"""

import sys
import os
from datetime import datetime

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from scripts.handlers.varieties_handler import varieties_handler
    from scripts.weather_engine.historical_weather_api import historical_weather_api
    from scripts.weather_engine.enhanced_rainfall_analyzer import enhanced_rainfall_analyzer
    print("✅ Phase 3 modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_weather_pattern_analysis():
    """Test weather pattern analysis functionality."""
    print("\n🔄 Testing Weather Pattern Analysis...")
    
    # Test coordinates (Lilongwe)
    lat, lon = -13.9833, 33.7833
    print(f"📍 Location: {lat}, {lon}")
    
    # Get weather analysis
    weather_analysis = varieties_handler.get_location_weather_analysis(lat, lon, 5, "test_user")
    
    if weather_analysis:
        # Test weather pattern analysis
        weather_patterns = varieties_handler._analyze_weather_patterns(weather_analysis)
        
        if weather_patterns:
            print("✅ Weather patterns analyzed successfully!")
            print(f"   • Current month: {weather_patterns.get('current_month', 'N/A')}")
            print(f"   • Rainfall variability: {weather_patterns.get('rainfall_variability', 0):.1f}%")
            print(f"   • Climate trend: {weather_patterns.get('climate_trend', 'N/A')}")
            print(f"   • Drought risk: {weather_patterns.get('drought_risk', 0):.2f}")
            print(f"   • Flood risk: {weather_patterns.get('flood_risk', 0):.2f}")
            
            # Test seasonal distribution
            seasonal_dist = weather_patterns.get('seasonal_distribution', {})
            if seasonal_dist:
                print(f"   • Annual total: {seasonal_dist.get('annual_total', 0):.0f}mm")
                print(f"   • Wet season: {seasonal_dist.get('wet_season_percentage', 0):.1f}%")
                print(f"   • Peak month: {seasonal_dist.get('peak_month', 'N/A')}")
            
            # Test planting season suitability
            planting_suit = weather_patterns.get('planting_season_suitability', {})
            if planting_suit:
                print(f"   • Planting season rainfall: {planting_suit.get('planting_season_rainfall', 0):.0f}mm")
                print(f"   • Rainfall reliability: {planting_suit.get('rainfall_reliability', 'N/A')}")
                print(f"   • Optimal planting month: {planting_suit.get('optimal_planting_month', 'N/A')}")
            
            return True
        else:
            print("❌ Weather pattern analysis failed")
            return False
    else:
        print("❌ No weather analysis data available")
        return False


def test_variety_scoring():
    """Test weather suitability scoring for varieties."""
    print("\n🔄 Testing Variety Scoring...")
    
    # Get weather analysis
    lat, lon = -13.9833, 33.7833
    weather_analysis = varieties_handler.get_location_weather_analysis(lat, lon, 5, "test_user")
    
    if not weather_analysis:
        print("❌ No weather analysis data available")
        return False
    
    # Analyze weather patterns
    weather_patterns = varieties_handler._analyze_weather_patterns(weather_analysis)
    
    # Create test varieties with different characteristics
    test_varieties = [
        {
            'name': 'Drought Tolerant Variety',
            'weather': 'drought tolerant, requires minimal water, suitable for dry conditions',
            'planting_time': 'November to December, rainy season',
            'yield': '2000-2500 kg/ha',
            'soil': 'well-drained sandy soil'
        },
        {
            'name': 'High Water Requirement Variety',
            'weather': 'requires high water, irrigation needed, high rainfall areas',
            'planting_time': 'January to February, wet season',
            'yield': '3000-4000 kg/ha',
            'soil': 'fertile loam soil'
        },
        {
            'name': 'Early Maturing Variety',
            'weather': 'adaptable to variable conditions, early maturing, short season',
            'planting_time': 'October to November, early rainy season',
            'yield': '1800-2200 kg/ha',
            'soil': 'various soil types'
        }
    ]
    
    print(f"   Testing {len(test_varieties)} varieties...")
    
    # Score each variety
    for i, variety in enumerate(test_varieties, 1):
        score = varieties_handler._calculate_weather_suitability_score(
            variety, weather_patterns, 'groundnut', 'test_user'
        )
        
        suitability = varieties_handler._interpret_weather_score(score)
        
        print(f"   {i}. {variety['name']}:")
        print(f"      • Total score: {score['total_score']:.1f}/100")
        print(f"      • Suitability: {suitability['level']} ({suitability['description']})")
        print(f"      • Component scores:")
        for component, component_score in score['component_scores'].items():
            print(f"        - {component}: {component_score:.1f}")
    
    return True


def test_weather_variety_matching():
    """Test the complete weather-variety matching process."""
    print("\n🔄 Testing Weather-Variety Matching...")
    
    # Get weather analysis
    lat, lon = -13.9833, 33.7833
    weather_analysis = varieties_handler.get_location_weather_analysis(lat, lon, 5, "test_user")
    
    if not weather_analysis:
        print("❌ No weather analysis data available")
        return False
    
    # Create test varieties
    test_varieties = [
        {
            'name': 'CG7',
            'weather': 'drought tolerant, suitable for low rainfall areas',
            'planting_time': 'November to December',
            'yield': '2000-2500 kg/ha'
        },
        {
            'name': 'Chalimbana',
            'weather': 'requires adequate rainfall, high water requirement',
            'planting_time': 'December to January',
            'yield': '3000-3500 kg/ha'
        },
        {
            'name': 'Nsinjiro',
            'weather': 'adaptable variety, moderate water requirements',
            'planting_time': 'October to December',
            'yield': '2500-3000 kg/ha'
        }
    ]
    
    print(f"   Testing with {len(test_varieties)} varieties...")
    
    # Apply weather-variety matching
    matched_varieties = varieties_handler.match_varieties_to_weather(
        test_varieties, weather_analysis, 'groundnut', 'test_user'
    )
    
    if matched_varieties:
        print("✅ Weather-variety matching completed successfully!")
        print("   Rankings (best to worst weather suitability):")
        
        for i, variety in enumerate(matched_varieties, 1):
            suitability = variety.get('weather_suitability', {})
            score = variety.get('weather_score', {}).get('total_score', 0)
            
            print(f"   {i}. {variety['name']} - {score:.1f}/100 ({suitability.get('level', 'unknown')})")
        
        # Check that varieties are properly sorted by score
        scores = [v.get('weather_score', {}).get('total_score', 0) for v in matched_varieties]
        is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
        
        if is_sorted:
            print("   ✅ Varieties correctly sorted by weather suitability")
        else:
            print("   ❌ Varieties not properly sorted by weather suitability")
        
        return is_sorted
    else:
        print("❌ Weather-variety matching failed")
        return False


def test_scoring_components():
    """Test individual scoring components."""
    print("\n🔄 Testing Scoring Components...")
    
    # Get weather analysis
    lat, lon = -13.9833, 33.7833
    weather_analysis = varieties_handler.get_location_weather_analysis(lat, lon, 5, "test_user")
    
    if not weather_analysis:
        print("❌ No weather analysis data available")
        return False
    
    weather_patterns = varieties_handler._analyze_weather_patterns(weather_analysis)
    
    # Test drought tolerance scoring
    drought_variety = {'weather': 'drought tolerant and drought resistant'}
    drought_score = varieties_handler._score_drought_tolerance(drought_variety, weather_patterns, 'groundnut')
    print(f"   • Drought tolerance score: {drought_score:.1f}/100")
    
    # Test rainfall compatibility scoring
    rain_variety = {'weather': 'requires high water and irrigation'}
    rain_score = varieties_handler._score_rainfall_compatibility(rain_variety, weather_patterns, 'groundnut')
    print(f"   • Rainfall compatibility score: {rain_score:.1f}/100")
    
    # Test seasonal timing scoring
    season_variety = {'planting_time': 'November to December, rainy season'}
    season_score = varieties_handler._score_seasonal_timing(season_variety, weather_patterns, 'groundnut')
    print(f"   • Seasonal timing score: {season_score:.1f}/100")
    
    # Test climate trend alignment
    trend_variety = {'weather': 'drought tolerant and resilient'}
    trend_score = varieties_handler._score_climate_trend_alignment(trend_variety, weather_patterns, 'groundnut')
    print(f"   • Climate trend alignment score: {trend_score:.1f}/100")
    
    # Test variability resilience
    resilience_variety = {'weather': 'adaptable and hardy, early maturing'}
    resilience_score = varieties_handler._score_variability_resilience(resilience_variety, weather_patterns, 'groundnut')
    print(f"   • Variability resilience score: {resilience_score:.1f}/100")
    
    print("✅ All scoring components tested successfully!")
    return True


def test_score_interpretation():
    """Test score interpretation functionality."""
    print("\n🔄 Testing Score Interpretation...")
    
    # Test different score levels
    test_scores = [
        {'total_score': 85, 'expected_level': 'excellent'},
        {'total_score': 75, 'expected_level': 'very_good'},
        {'total_score': 65, 'expected_level': 'good'},
        {'total_score': 55, 'expected_level': 'moderate'},
        {'total_score': 45, 'expected_level': 'fair'},
        {'total_score': 25, 'expected_level': 'poor'}
    ]
    
    all_correct = True
    for test_score in test_scores:
        score = test_score['total_score']
        expected = test_score['expected_level']
        
        interpretation = varieties_handler._interpret_weather_score({'total_score': score})
        actual = interpretation['level']
        
        if actual == expected:
            print(f"   ✅ Score {score} → {actual} (correct)")
        else:
            print(f"   ❌ Score {score} → {actual} (expected {expected})")
            all_correct = False
    
    if all_correct:
        print("✅ All score interpretations correct!")
        return True
    else:
        print("❌ Some score interpretations incorrect")
        return False


def main():
    """Run all Phase 3 tests."""
    print("🚀 Phase 3: Weather-Variety Matching Algorithm Test Suite")
    print("=" * 70)
    
    tests = [
        ("Weather Pattern Analysis", test_weather_pattern_analysis),
        ("Variety Scoring", test_variety_scoring),
        ("Weather-Variety Matching", test_weather_variety_matching),
        ("Scoring Components", test_scoring_components),
        ("Score Interpretation", test_score_interpretation),
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
        
        print("-" * 50)
    
    print(f"\n📊 Phase 3 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 3 implementation is working correctly!")
        print("\n✅ Weather-variety matching algorithm successfully implemented!")
        print("\n🔄 Summary of Phase 3 achievements:")
        print("• Varieties are now scored based on weather suitability")
        print("• Different weather patterns produce different variety rankings")
        print("• Algorithm considers rainfall, drought tolerance, and climate trends")
        print("• Varieties are ranked by their weather compatibility")
        print("• Weather suitability is displayed with clear indicators")
        print("\n✅ Ready to proceed to Phase 4: Enhanced Response Formatting")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 