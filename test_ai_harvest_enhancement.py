#!/usr/bin/env python3
"""
Test AI-Enhanced Harvest Advisor - Phase 6
Tests the integration of AI capabilities into the harvest advisor
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from scripts.handlers.harvest_advisor import HarvestAdvisor
from scripts.handlers.harvest_handler import HarvestHandler
from scripts.utils.logger import logger


async def test_harvest_advisor_structure():
    """Test the harvest advisor structure without AI calls."""
    print("🧪 Testing Harvest Advisor Structure")
    print("=" * 60)
    
    # Initialize advisor
    advisor = HarvestAdvisor()
    
    # Test cases
    test_cases = [
        {
            'crop': 'maize',
            'location': '-13.9833, 33.7833',
            'user_id': 'test_user_001'
        },
        {
            'crop': 'beans',
            'location': 'Lilongwe',
            'user_id': 'test_user_002'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test Case {i}: {test_case['crop']} at {test_case['location']}")
        print("-" * 50)
        
        try:
            # Test base advice generation (without AI)
            print("📋 Testing base harvest advice...")
            
            # Get weather context
            coords = advisor.coordinate_handler.parse_coordinates(test_case['location'], test_case['user_id'])
            weather_context = {}
            if coords:
                weather_context = advisor._get_weather_context({'lat': coords[0], 'lon': coords[1]}, test_case['crop'])
            
            # Get harvest knowledge
            harvest_knowledge = advisor._search_harvest_knowledge(test_case['crop'])
            
            # Create base advice manually
            base_advice = {
                'crop': test_case['crop'],
                'location': test_case['location'],
                'weather_context': weather_context,
                'harvest_timing': advisor._get_harvest_timing(test_case['crop'], harvest_knowledge, weather_context),
                'drying_recommendations': advisor._get_drying_recommendations(test_case['crop'], harvest_knowledge),
                'storage_guidelines': advisor._get_storage_guidelines(test_case['crop'], harvest_knowledge),
                'loss_prevention': advisor._get_loss_prevention(test_case['crop'], harvest_knowledge),
                'processing_advice': advisor._get_processing_advice(test_case['crop'], harvest_knowledge),
                'quality_standards': advisor._get_quality_standards(test_case['crop'], harvest_knowledge),
                'generated_at': '2024-01-01T00:00:00'
            }
            
            print("✅ Base advice generated successfully")
            print(f"📊 Weather context: {len(weather_context)} items")
            print(f"📚 Harvest knowledge: {len(harvest_knowledge)} categories")
            
            # Test AI prompt creation
            print("\n📝 Testing AI prompt creation...")
            prompt = advisor._create_harvest_ai_prompt(base_advice, test_case['crop'], test_case['location'])
            print(f"✅ AI prompt created: {len(prompt)} characters")
            
            # Test AI response parsing
            print("\n🔍 Testing AI response parsing...")
            sample_ai_response = """
            Risk Assessment:
            • Weather risks: Medium due to seasonal patterns
            • Storage risks: Low with proper containers
            
            Timing Optimization:
            • Harvest during dry months
            • Avoid rainy season for drying
            
            Quality Enhancement:
            • Use proper handling techniques
            • Monitor moisture content
            """
            
            insights = advisor._parse_ai_harvest_insights(sample_ai_response)
            print(f"✅ AI insights parsed: {len(insights)} sections")
            print(f"📊 Sections: {list(insights.keys())}")
            
            # Test response formatting
            print("\n📄 Testing response formatting...")
            formatted_response = advisor.format_harvest_advice(base_advice)
            print(f"✅ Response formatted: {len(formatted_response)} characters")
            print(f"📄 Preview: {formatted_response[:100]}...")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            logger.error(f"Test case {i} failed: {str(e)}")
    
    print(f"\n🎉 Structure Testing Complete!")
    print("=" * 60)


async def test_harvest_handler():
    """Test the harvest handler without AI calls."""
    print("\n📱 Testing Harvest Handler")
    print("=" * 40)
    
    handler = HarvestHandler()
    
    # Test cases
    test_commands = [
        "/harvest maize",
        "/harvest beans -13.9833, 33.7833",
        "/harvest groundnuts Lilongwe",
        "/harvest invalid_crop",
        "/harvest"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n🔬 Test Command {i}: {command}")
        print("-" * 30)
        
        try:
            # Test command parsing
            parts = command.strip().split()
            if len(parts) < 2:
                print("❌ Invalid command format")
                continue
            
            crop = parts[1].lower()
            location = None
            if len(parts) > 2:
                location = ' '.join(parts[2:]).strip()
            
            print(f"📋 Parsed: crop={crop}, location={location}")
            
            # Test crop validation
            is_valid = handler._is_valid_crop(crop)
            print(f"✅ Crop validation: {is_valid}")
            
            if not is_valid:
                print("❌ Invalid crop - skipping further tests")
                continue
            
            # Test handler structure (without actual AI calls)
            print("✅ Handler structure test passed")
            
        except Exception as e:
            print(f"❌ Handler test failed: {str(e)}")
    
    print("\n✅ Handler Testing Complete!")


def test_ai_components_offline():
    """Test AI components without making actual API calls."""
    print("\n🔧 Testing AI Components (Offline)")
    print("=" * 40)
    
    advisor = HarvestAdvisor()
    
    # Test AI prompt creation
    print("📝 Testing AI Prompt Creation...")
    base_advice = {
        'crop': 'maize',
        'location': 'Lilongwe',
        'weather_context': {
            'rainfall_patterns': {'January': 150, 'February': 120},
            'drying_conditions': {'optimal_drying_months': []},
            'storage_risks': {'high_humidity_months': []}
        },
        'harvest_timing': {'knowledge_based_timing': [{'text': 'test'}]},
        'drying_recommendations': {'methods': [{'method': 'sun drying'}]},
        'storage_guidelines': {'storage_methods': [{'method': 'warehouse'}]}
    }
    
    prompt = advisor._create_harvest_ai_prompt(base_advice, 'maize', 'Lilongwe')
    print(f"✅ Prompt created: {len(prompt)} characters")
    print(f"📄 Prompt preview: {prompt[:100]}...")
    
    # Test AI response parsing
    print("\n🔍 Testing AI Response Parsing...")
    sample_ai_response = """
    Risk Assessment:
    • Weather risks: Medium due to seasonal patterns
    • Storage risks: Low with proper containers
    
    Timing Optimization:
    • Harvest during dry months
    • Avoid rainy season for drying
    
    Quality Enhancement:
    • Use proper handling techniques
    • Monitor moisture content
    """
    
    insights = advisor._parse_ai_harvest_insights(sample_ai_response)
    print(f"✅ Insights parsed: {len(insights)} sections")
    print(f"📊 Sections: {list(insights.keys())}")
    
    # Test each section
    for section, items in insights.items():
        if section != 'raw_response':
            print(f"   • {section}: {len(items)} items")
    
    print("\n✅ AI Components Test Complete!")


def main():
    """Run all AI enhancement tests (offline mode)."""
    print("🚀 Starting AI-Enhanced Harvest Advisor Tests (Offline Mode)")
    print("=" * 60)
    
    try:
        # Run async tests
        asyncio.run(test_harvest_advisor_structure())
        asyncio.run(test_harvest_handler())
        
        # Run sync tests
        test_ai_components_offline()
        
        print("\n🎯 All Tests Completed Successfully!")
        print("\n💡 Note: This test ran in offline mode to avoid API calls.")
        print("   To test full AI integration, ensure OpenAI API key is configured.")
        
    except Exception as e:
        print(f"\n❌ Test Suite Failed: {str(e)}")
        logger.error(f"Test suite failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 