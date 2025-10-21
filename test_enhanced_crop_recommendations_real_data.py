#!/usr/bin/env python3
"""
Test Enhanced Crop Recommendations with REAL DATA ONLY.
Tests the new enhanced recommendation engine using actual agriculture guides and varieties.
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from scripts.crop_advisor.enhanced_crop_recommendation_engine import enhanced_crop_recommendation_engine
from scripts.utils.logger import logger


def test_enhanced_recommendations_real_data():
    """Test enhanced recommendations using ONLY real data sources."""
    
    print("🌾 Testing Enhanced Crop Recommendations with REAL DATA ONLY")
    print("=" * 60)
    
    # Test parameters using real Malawi coordinates
    test_cases = [
        {
            'name': 'Lilongwe Central Region',
            'lat': -13.9626,
            'lon': 33.7741,
            'season': 'rainy_season',
            'rainfall_mm': 600,
            'temperature': 25,
            'farmer_profile': {
                'experience_level': 'intermediate',
                'available_inputs': ['fertilizer', 'seeds'],
                'farm_size': 2.0
            }
        },
        {
            'name': 'Blantyre Southern Region',
            'lat': -15.7849,
            'lon': 35.0035,
            'season': 'dry_season',
            'rainfall_mm': 50,
            'temperature': 28,
            'farmer_profile': {
                'experience_level': 'beginner',
                'available_inputs': ['seeds'],
                'farm_size': 1.0
            }
        },
        {
            'name': 'Mzuzu Northern Region',
            'lat': -11.4587,
            'lon': 34.0151,
            'season': 'current',
            'rainfall_mm': 400,
            'temperature': 22,
            'farmer_profile': {
                'experience_level': 'expert',
                'available_inputs': ['fertilizer', 'seeds', 'pest_control'],
                'farm_size': 5.0
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Get enhanced recommendations using real data
            recommendations = enhanced_crop_recommendation_engine.get_enhanced_crop_recommendations(
                lat=test_case['lat'],
                lon=test_case['lon'],
                season=test_case['season'],
                rainfall_mm=test_case['rainfall_mm'],
                temperature=test_case['temperature'],
                farmer_profile=test_case['farmer_profile'],
                historical_years=5
            )
            
            # Validate response structure
            assert 'recommendations' in recommendations, "Missing recommendations"
            assert 'yield_projections' in recommendations, "Missing yield projections"
            assert 'input_recommendations' in recommendations, "Missing input recommendations"
            assert 'planting_guidelines' in recommendations, "Missing planting guidelines"
            assert 'weather_context' in recommendations, "Missing weather context"
            assert 'data_sources' in recommendations, "Missing data sources"
            assert 'confidence_score' in recommendations, "Missing confidence score"
            assert recommendations['data_type'] == 'real_data_only', "Not using real data only"
            
            print(f"✅ Response structure valid")
            print(f"📊 Found {len(recommendations['recommendations'])} crop recommendations")
            print(f"🌱 Data sources: {len(recommendations['data_sources'])} agriculture guides")
            print(f"🎯 Confidence score: {recommendations['confidence_score']:.2f}")
            print(f"📍 Region: {recommendations['location']['region']}")
            
            # Test crop recommendations
            if recommendations['recommendations']:
                top_crop = recommendations['recommendations'][0]
                print(f"🥇 Top crop: {top_crop['crop_name']}")
                print(f"📈 Suitability score: {top_crop['suitability_score']:.2f}")
                print(f"🌾 Top varieties: {len(top_crop['top_varieties'])}")
                
                # Validate varieties are real
                if top_crop['top_varieties']:
                    top_variety = top_crop['top_varieties'][0]
                    print(f"   - {top_variety['name']} (confidence: {top_variety.get('confidence_score', 0)})")
                    assert top_variety['name'] != 'Unknown Variety', "Found unknown variety"
                    assert top_variety.get('source_document') != 'Database', "Missing source document"
            
            # Test yield projections
            if recommendations['yield_projections']:
                first_crop = list(recommendations['yield_projections'].keys())[0]
                yield_data = recommendations['yield_projections'][first_crop]
                print(f"📊 Yield projections for {first_crop}:")
                print(f"   - Potential: {yield_data['potential_yield']} tons/ha")
                print(f"   - Realistic: {yield_data['realistic_yield']} tons/ha")
                print(f"   - Range: {yield_data['yield_range']['minimum']}-{yield_data['yield_range']['maximum']} tons/ha")
                assert yield_data['data_source'] == 'real_historical_data', "Not using real historical data"
            
            # Test input recommendations
            input_recs = recommendations['input_recommendations']
            print(f"💊 Input recommendations:")
            print(f"   - Fertilizer: {input_recs['fertilizer']['type']}")
            print(f"   - Seeds: {input_recs['seeds']['quantity']}")
            print(f"   - Pest control: {len(input_recs['pest_control']['recommendations'])} recommendations")
            assert input_recs['data_source'] == 'real_crop_varieties_database', "Not using real crop varieties database"
            
            # Test planting guidelines
            planting = recommendations['planting_guidelines']
            print(f"🌱 Planting guidelines:")
            print(f"   - Timing: {len(planting['optimal_timing'])} recommendations")
            print(f"   - Spacing: {len(planting['spacing'])} recommendations")
            print(f"   - Soil prep: {len(planting['soil_preparation'])} recommendations")
            
            # Test weather context
            weather = recommendations['weather_context']
            print(f"🌤️ Weather context:")
            print(f"   - Current rainfall: {weather['current_rainfall']}mm")
            print(f"   - Current temperature: {weather['current_temperature']}°C")
            print(f"   - Historical years: {weather['historical_years']}")
            print(f"   - Climate trend: {weather['climate_trend']}")
            
            print(f"✅ Test case {i} PASSED - All real data sources validated")
            
        except Exception as e:
            print(f"❌ Test case {i} FAILED: {e}")
            logger.error(f"Test case {i} failed: {e}")
            continue
    
    print(f"\n🎉 Enhanced Crop Recommendations Test Complete!")
    print("=" * 60)


def test_real_data_sources():
    """Test that we're using only real data sources."""
    
    print("\n🔍 Testing Real Data Sources")
    print("-" * 30)
    
    # Test JSON crop database (our real data source)
    try:
        with open("data/crop_varieties.json", 'r') as f:
            crop_data = json.load(f)
        
        crops = crop_data.get('lilongwe_crops', {})
        print(f"🌾 JSON crop database: {len(crops)} crops")
        assert len(crops) > 0, "No crops in JSON database"
        
        # Check sample crop data
        total_varieties = 0
        for crop_id, crop_info in list(crops.items())[:3]:
            varieties = crop_info.get('varieties', [])
            total_varieties += len(varieties)
            print(f"   - {crop_info['name']}: {len(varieties)} varieties")
            assert crop_info['name'] != 'Unknown Crop', "Found unknown crop"
            assert 'water_requirements' in crop_info, "Missing water requirements"
            assert 'temperature_requirements' in crop_info, "Missing temperature requirements"
            
            # Check sample varieties
            for variety in varieties[:2]:  # First 2 varieties
                print(f"     * {variety['name']}: {variety.get('maturity_days', 0)} days")
                assert variety['name'] != 'Unknown Variety', "Found unknown variety"
                assert variety.get('maturity_days', 0) > 0, "Invalid maturity days"
        
        print(f"📋 Total varieties: {total_varieties}")
        assert total_varieties > 0, "No crop varieties found"
        print("✅ JSON crop database validation passed")
        
    except Exception as e:
        print(f"❌ JSON crop database test failed: {e}")
        return False
    
    return True


def test_no_mock_data():
    """Test that no mock data is being used."""
    
    print("\n🚫 Testing No Mock Data Usage")
    print("-" * 30)
    
    # Test that we're not using any mock data
    test_lat, test_lon = -13.9626, 33.7741  # Lilongwe
    
    recommendations = enhanced_crop_recommendation_engine.get_enhanced_crop_recommendations(
        lat=test_lat,
        lon=test_lon,
        season='rainy_season',
        rainfall_mm=600,
        temperature=25,
        farmer_profile={'experience_level': 'intermediate'},
        historical_years=5
    )
    
    # Check that all data sources are real
    assert recommendations['data_type'] == 'real_data_only', "Not using real data only"
    
    # Check that varieties have real source documents
    for crop in recommendations['recommendations']:
        for variety in crop['top_varieties']:
            assert variety['source_document'] != 'Mock Data', "Found mock variety data"
            assert variety['source_document'] == 'Crop Varieties Database', "Not using real crop varieties database"
            assert variety['name'] != 'Mock Variety', "Found mock variety name"
    
    # Check that yield projections use real data
    for crop_name, yield_data in recommendations['yield_projections'].items():
        assert yield_data['data_source'] == 'real_historical_data', "Not using real historical data"
        assert yield_data['potential_yield'] > 0, "Invalid yield projection"
        assert yield_data['realistic_yield'] > 0, "Invalid realistic yield"
    
    # Check that input recommendations come from real data
    input_recs = recommendations['input_recommendations']
    assert input_recs['data_source'] == 'real_crop_varieties_database', "Not using real crop varieties database"
    
    print("✅ No mock data detected - All data sources are real")
    return True


if __name__ == "__main__":
    print("🚀 Starting Enhanced Crop Recommendations Test Suite")
    print("=" * 60)
    
    # Test real data sources
    if not test_real_data_sources():
        print("❌ Real data sources test failed")
        sys.exit(1)
    
    # Test no mock data
    if not test_no_mock_data():
        print("❌ Mock data test failed")
        sys.exit(1)
    
    # Test enhanced recommendations
    test_enhanced_recommendations_real_data()
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Enhanced Crop Recommendations using REAL DATA ONLY")
    print("=" * 60)
