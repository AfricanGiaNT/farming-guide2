#!/usr/bin/env python3
"""
Phase 1 Critical Fixes Test Suite
Tests the fixes for AI parsing slice error, hardcoded limits, and field mapping.
"""

import requests
import json
import time

def test_api_endpoint(endpoint, expected_fields=None):
    """Test an API endpoint and return the response."""
    try:
        response = requests.get(f"http://localhost:8000{endpoint}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {endpoint} - Status: {response.status_code}")
            return data
        else:
            print(f"❌ {endpoint} - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ {endpoint} - Error: {e}")
        return None

def test_varieties_endpoint(crop_name):
    """Test the varieties endpoint for a specific crop."""
    print(f"\n🧪 Testing varieties endpoint for {crop_name}")
    print("=" * 50)
    
    data = test_api_endpoint(f"/api/varieties/{crop_name}")
    if not data:
        return False
    
    # Check required fields
    required_fields = ['crop', 'real_data', 'timestamp', 'total_found', 'varieties']
    for field in required_fields:
        if field not in data:
            print(f"❌ Missing required field: {field}")
            return False
        else:
            print(f"✅ Has required field: {field}")
    
    # Check varieties structure
    varieties = data.get('varieties', [])
    print(f"✅ Found {len(varieties)} varieties")
    
    if len(varieties) > 0:
        # Check first variety structure
        first_variety = varieties[0]
        variety_fields = ['name', 'maturity_days', 'yield_potential', 'drought_tolerance', 
                         'disease_resistance', 'planting_time', 'description', 
                         'weather_requirements', 'soil_requirements', 'growing_areas']
        
        for field in variety_fields:
            if field in first_variety:
                print(f"✅ Variety has field: {field}")
            else:
                print(f"❌ Variety missing field: {field}")
        
        # Check that variety name is not generic
        variety_name = first_variety.get('name', '')
        generic_terms = ['variety', 'type', 'cultivar', 'not specified', 'hybrid']
        if any(term in variety_name.lower() for term in generic_terms):
            print(f"⚠️  Variety name might be generic: {variety_name}")
        else:
            print(f"✅ Variety name looks specific: {variety_name}")
    
    return True

def test_search_endpoint():
    """Test the search endpoint."""
    print(f"\n🧪 Testing search endpoint")
    print("=" * 50)
    
    data = test_api_endpoint("/api/search?q=groundnut%20varieties")
    if not data:
        return False
    
    # Check required fields
    required_fields = ['query', 'results', 'count', 'timestamp']
    for field in required_fields:
        if field not in data:
            print(f"❌ Missing required field: {field}")
            return False
        else:
            print(f"✅ Has required field: {field}")
    
    # Check results
    results = data.get('results', [])
    print(f"✅ Found {len(results)} search results")
    
    if len(results) > 0:
        first_result = results[0]
        if 'content' in first_result and 'score' in first_result:
            print("✅ Search result has required fields")
        else:
            print("❌ Search result missing required fields")
    
    return True

def test_no_slice_errors():
    """Test that no slice errors occur."""
    print(f"\n🧪 Testing for slice errors")
    print("=" * 50)
    
    # Test multiple crops to ensure no slice errors
    crops = ['groundnut', 'maize', 'soybean', 'bean']
    success_count = 0
    
    for crop in crops:
        print(f"Testing {crop}...")
        data = test_api_endpoint(f"/api/varieties/{crop}")
        if data and 'varieties' in data:
            success_count += 1
            print(f"✅ {crop} processed without slice errors")
        else:
            print(f"❌ {crop} failed or returned no varieties")
    
    print(f"✅ {success_count}/{len(crops)} crops processed successfully")
    return success_count == len(crops)

def main():
    """Run all Phase 1 tests."""
    print("🚀 Phase 1 Critical Fixes Test Suite")
    print("=" * 60)
    
    # Wait for API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(2)
    
    # Test health endpoint
    print("\n🧪 Testing health endpoint")
    print("=" * 50)
    health_data = test_api_endpoint("/api/health")
    if health_data and health_data.get('components', {}).get('varieties_handler'):
        print("✅ VarietiesHandler is available")
    else:
        print("❌ VarietiesHandler is not available")
        return
    
    # Test varieties endpoints
    test_varieties_endpoint("groundnut")
    test_varieties_endpoint("maize")
    
    # Test search endpoint
    test_search_endpoint()
    
    # Test for slice errors
    test_no_slice_errors()
    
    print("\n🎉 Phase 1 tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
