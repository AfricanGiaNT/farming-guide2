#!/usr/bin/env python3
"""
Test script for Week 3 AI integration.
Tests the GPT-3.5-turbo integration and response synthesis.
"""
import sys
import os
import asyncio
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.utils.config_loader import config
from scripts.utils.logger import logger

def test_config_loading():
    """Test configuration loading."""
    print("🧪 Testing configuration loading...")
    
    try:
        # Test creating template files
        config.create_template_env_files()
        print("✅ Template env files created/verified")
        
        # Test loading required keys (will fail if not set, which is expected)
        try:
            telegram_token = config.get_required("TELEGRAM_BOT_TOKEN")
            print("✅ Telegram token loaded")
        except ValueError:
            print("⚠️  Telegram token not set (expected for testing)")
        
        try:
            openai_key = config.get_required("OPENAI_API_KEY")
            print("✅ OpenAI key loaded")
        except ValueError:
            print("⚠️  OpenAI key not set (expected for testing)")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_ai_agent_imports():
    """Test AI agent module imports."""
    print("\n🧪 Testing AI agent imports...")
    
    try:
        from scripts.ai_agent import gpt_integration, prompt_formatter, response_synthesizer
        print("✅ AI agent modules imported successfully")
        
        # Test basic functionality
        print(f"✅ GPT integration model: {gpt_integration.model}")
        print(f"✅ Prompt formatter max length: {prompt_formatter.max_prompt_length}")
        print(f"✅ Response synthesizer AI enabled: {response_synthesizer.enable_ai_enhancement}")
        
        return True
    except Exception as e:
        print(f"❌ AI agent import test failed: {e}")
        return False

def test_prompt_formatting():
    """Test prompt formatting functionality."""
    print("\n🧪 Testing prompt formatting...")
    
    try:
        from scripts.ai_agent.prompt_formatter import prompt_formatter
        
        # Test crop analysis prompt
        sample_crop_data = {
            'recommendations': [
                {
                    'crop_data': {'name': 'Maize'},
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
        
        sample_weather_data = {
            'temperature': 24,
            'humidity': 65,
            'rainfall': 25
        }
        
        prompt = prompt_formatter.format_crop_analysis_prompt(
            sample_crop_data, sample_weather_data, "Lilongwe"
        )
        
        print(f"✅ Crop analysis prompt generated ({len(prompt)} chars)")
        print(f"✅ Prompt validation: {prompt_formatter.validate_prompt(prompt)}")
        
        return True
    except Exception as e:
        print(f"❌ Prompt formatting test failed: {e}")
        return False

def test_response_synthesizer():
    """Test response synthesizer (without AI calls)."""
    print("\n🧪 Testing response synthesizer...")
    
    try:
        from scripts.ai_agent.response_synthesizer import response_synthesizer
        
        # Disable AI enhancement for testing
        response_synthesizer.set_ai_enhancement(False)
        
        # Test basic response formatting
        sample_recommendations = {
            'recommendations': [
                {
                    'crop_data': {'name': 'Maize'},
                    'total_score': 85,
                    'suitability_level': 'excellent',
                    'recommended_varieties': [
                        {'variety_data': {'name': 'DK 8053'}}
                    ]
                }
            ],
            'environmental_summary': {
                'total_7day_rainfall': 25,
                'current_temperature': 24,
                'current_season': 'rainy_season'
            },
            'planting_calendar': [
                {
                    'crop_name': 'Maize',
                    'season_match': True
                }
            ]
        }
        
        sample_weather = {
            'temperature': 24,
            'humidity': 65
        }
        
        response = response_synthesizer._format_basic_response(
            sample_recommendations, sample_weather, "Lilongwe"
        )
        
        print(f"✅ Basic response generated ({len(response)} chars)")
        print("✅ Response synthesizer working correctly")
        
        # Test advice generation
        advice = response_synthesizer._generate_basic_advice(sample_recommendations)
        print(f"✅ Basic advice generated ({len(advice)} items)")
        
        return True
    except Exception as e:
        print(f"❌ Response synthesizer test failed: {e}")
        return False

def test_logger_enhancements():
    """Test logger enhancements for AI integration."""
    print("\n🧪 Testing logger enhancements...")
    
    try:
        from scripts.utils.logger import logger
        
        # Test timestamp method
        timestamp = logger.get_timestamp()
        print(f"✅ Timestamp generated: {timestamp}")
        
        # Test logging methods
        logger.info("Test info message", "test_user")
        logger.debug("Test debug message", "test_user")
        print("✅ Logger methods working correctly")
        
        return True
    except Exception as e:
        print(f"❌ Logger test failed: {e}")
        return False

async def test_integration_pipeline():
    """Test the complete integration pipeline (without actual API calls)."""
    print("\n🧪 Testing integration pipeline...")
    
    try:
        from scripts.ai_agent.response_synthesizer import response_synthesizer
        
        # Mock data similar to what crop_handler would pass
        mock_recommendations = {
            'recommendations': [
                {
                    'crop_data': {'name': 'Maize'},
                    'total_score': 85,
                    'suitability_level': 'excellent',
                    'recommended_varieties': [
                        {'variety_data': {'name': 'DK 8053'}}
                    ]
                }
            ],
            'environmental_summary': {
                'total_7day_rainfall': 25,
                'current_temperature': 24,
                'current_season': 'rainy_season'
            }
        }
        
        mock_weather = {
            'temperature': 24,
            'humidity': 65
        }
        
        # Disable AI for testing (avoids API calls)
        response_synthesizer.set_ai_enhancement(False)
        
        # Test the synthesis pipeline
        result = await response_synthesizer.synthesize_crop_recommendations(
            mock_recommendations, mock_weather, "Lilongwe", "test_user"
        )
        
        print(f"✅ Integration pipeline completed ({len(result)} chars)")
        print("✅ Week 3 integration working correctly")
        
        return True
    except Exception as e:
        print(f"❌ Integration pipeline test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🌾 Agricultural Advisor Bot - Week 3 Integration Test\n")
    
    tests = [
        ("Config Loading", test_config_loading),
        ("AI Agent Imports", test_ai_agent_imports),
        ("Prompt Formatting", test_prompt_formatting),
        ("Response Synthesizer", test_response_synthesizer),
        ("Logger Enhancements", test_logger_enhancements),
        ("Integration Pipeline", test_integration_pipeline)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = asyncio.run(test_func())
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Week 3 AI integration is ready.")
        
        print("\n📝 Next Steps:")
        print("1. Set up your OpenAI API key in config/openai_key.env")
        print("2. Test the bot with `/crops Lilongwe` command")
        print("3. Monitor costs and AI response quality")
        print("4. Adjust AI enhancement settings if needed")
        
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 