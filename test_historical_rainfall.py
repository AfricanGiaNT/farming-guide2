#!/usr/bin/env python3
"""
Test Historical Rainfall Functionality
Demonstrates the new historical weather analysis capabilities.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from scripts.weather_engine.historical_weather_api import historical_weather_api
    from scripts.weather_engine.enhanced_rainfall_analyzer import enhanced_rainfall_analyzer
    print("✅ Historical weather modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_historical_api():
    """Test the historical weather API."""
    print("\n🔄 Testing Historical Weather API...")
    
    # Test coordinates (Lilongwe)
    lat, lon = -13.9833, 33.7833
    years = 3
    
    print(f"📍 Location: {lat}, {lon}")
    print(f"📅 Years: {years}")
    
    # Test historical rainfall data
    print("\n1️⃣ Testing historical rainfall data...")
    historical_data = historical_weather_api.get_historical_rainfall(lat, lon, years)
    
    if historical_data:
        print(f"✅ Historical data retrieved successfully!")
        print(f"   • Years analyzed: {historical_data.years_analyzed}")
        print(f"   • Climate trend: {historical_data.climate_trend}")
        print(f"   • Rainfall variability: {historical_data.rainfall_variability:.1f}%")
        print(f"   • Wet season months: {len(historical_data.wet_season_months)}")
        print(f"   • Dry season months: {len(historical_data.dry_season_months)}")
        
        if historical_data.drought_years:
            print(f"   • Recent drought years: {historical_data.drought_years[-3:]}")
        if historical_data.flood_years:
            print(f"   • Recent flood years: {historical_data.flood_years[-3:]}")
            
        return True
    else:
        print("❌ Failed to retrieve historical data")
        return False


def test_enhanced_analyzer():
    """Test the enhanced rainfall analyzer."""
    print("\n🔄 Testing Enhanced Rainfall Analyzer...")
    
    # Test coordinates
    lat, lon = -13.9833, 33.7833
    current_rainfall = 15.0
    forecast_rainfall = 8.0
    
    print(f"📍 Location: {lat}, {lon}")
    print(f"🌧️ Current rainfall: {current_rainfall}mm")
    print(f"🔮 Forecast rainfall: {forecast_rainfall}mm")
    
    # Test comprehensive analysis
    print("\n2️⃣ Testing comprehensive rainfall analysis...")
    analysis = enhanced_rainfall_analyzer.analyze_comprehensive_rainfall(
        lat, lon, current_rainfall, forecast_rainfall, 3
    )
    
    if analysis and 'error' not in analysis:
        print(f"✅ Comprehensive analysis completed!")
        print(f"   • Analysis type: {analysis.get('analysis_type', 'unknown')}")
        print(f"   • Current month: {analysis.get('current_month', 'unknown')}")
        print(f"   • Enhanced seasonal estimate: {analysis.get('enhanced_seasonal_estimate', 0):.1f}mm")
        
        rainfall_status = analysis.get('rainfall_status', {})
        print(f"   • Rainfall status: {rainfall_status.get('description', 'unknown')}")
        
        if 'percentage_of_normal' in rainfall_status and rainfall_status['percentage_of_normal']:
            print(f"   • Percentage of normal: {rainfall_status['percentage_of_normal']:.1f}%")
        
        return True
    else:
        print("❌ Comprehensive analysis failed")
        return False


def test_drought_risk():
    """Test drought risk assessment."""
    print("\n🔄 Testing Drought Risk Assessment...")
    
    lat, lon = -13.9833, 33.7833
    current_conditions = {
        'total_7day_rainfall': 5.0,
        'temperature': 32,
        'humidity': 35
    }
    
    print(f"📍 Location: {lat}, {lon}")
    print(f"🌧️ Current conditions: {current_conditions['total_7day_rainfall']}mm rainfall, {current_conditions['temperature']}°C, {current_conditions['humidity']}% humidity")
    
    # Test drought risk
    print("\n3️⃣ Testing drought risk assessment...")
    risk_assessment = enhanced_rainfall_analyzer.get_drought_risk_assessment(
        lat, lon, current_conditions, 3
    )
    
    if risk_assessment and 'error' not in risk_assessment:
        print(f"✅ Drought risk assessment completed!")
        print(f"   • Risk level: {risk_assessment.get('drought_risk_level', 'unknown')}")
        
        indicators = risk_assessment.get('drought_indicators', {})
        if 'rainfall_deficit_ratio' in indicators:
            deficit = indicators['rainfall_deficit_ratio'] * 100
            print(f"   • Rainfall deficit: {deficit:.1f}% below normal")
        
        if 'rainfall_variability' in indicators:
            print(f"   • Rainfall variability: {indicators['rainfall_variability']:.1f}%")
        
        recommendations = risk_assessment.get('recommendations', [])
        if recommendations:
            print(f"   • Recommendations: {len(recommendations)} provided")
            print(f"     - {recommendations[0]}")
        
        return True
    else:
        print("❌ Drought risk assessment failed")
        return False


def test_comparison():
    """Test rainfall comparison."""
    print("\n🔄 Testing Rainfall Comparison...")
    
    lat, lon = -13.9833, 33.7833
    current_rainfall = 20.0
    current_month = datetime.now().strftime('%B')
    
    print(f"📍 Location: {lat}, {lon}")
    print(f"🌧️ Current rainfall: {current_rainfall}mm")
    print(f"📅 Month: {current_month}")
    
    # Test comparison
    print("\n4️⃣ Testing rainfall comparison...")
    comparison = enhanced_rainfall_analyzer.compare_with_historical_patterns(
        lat, lon, current_rainfall, current_month, 3
    )
    
    if comparison and 'error' not in comparison:
        print(f"✅ Rainfall comparison completed!")
        print(f"   • Status: {comparison.get('status', 'unknown')}")
        print(f"   • Description: {comparison.get('description', 'unknown')}")
        
        if 'historical_average' in comparison:
            print(f"   • Historical average: {comparison['historical_average']:.1f}mm")
        
        if 'percentage_of_normal' in comparison:
            print(f"   • Percentage of normal: {comparison['percentage_of_normal']:.1f}%")
        
        implications = comparison.get('agricultural_implications', [])
        if implications:
            print(f"   • Agricultural implications: {len(implications)} provided")
            print(f"     - {implications[0]}")
        
        return True
    else:
        print("❌ Rainfall comparison failed")
        return False


def main():
    """Main test function."""
    print("🧪 Testing Historical Rainfall Functionality")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(("Historical API", test_historical_api()))
    test_results.append(("Enhanced Analyzer", test_enhanced_analyzer()))
    test_results.append(("Drought Risk", test_drought_risk()))
    test_results.append(("Rainfall Comparison", test_comparison()))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("-" * 30)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("\n🎉 All tests passed! Historical rainfall functionality is working.")
        print("\n📱 New Bot Commands Available:")
        print("• /rain_history <location> [years] - Historical rainfall analysis")
        print("• /rain_compare <location> <rainfall_mm> [years] - Compare with historical")
        print("• /drought_risk <location> [years] - Drought risk assessment")
        print("\nExamples:")
        print("• /rain_history Lilongwe 5")
        print("• /rain_compare -13.9833, 33.7833 25")
        print("• /drought_risk Area 1 7")
    else:
        print(f"\n⚠️ {len(test_results) - passed} tests failed. Check the API keys and network connectivity.")
        print("\nNote: Some failures may be due to:")
        print("• Missing API keys (Open-Meteo should work without keys)")
        print("• Network connectivity issues")
        print("• Rate limiting on free APIs")
    
    return passed == len(test_results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 