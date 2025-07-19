#!/usr/bin/env python3
"""
Test script for enhanced /crops command with seasonal filtering.
Tests the new seasonal recommendation functionality.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.handlers.crop_handler import crops_command, seasonal_callback, weather_callback, rainfall_callback
from scripts.crop_advisor.recommendation_engine import recommendation_engine
from scripts.utils.logger import logger
from telegram import Update
from telegram.ext import ContextTypes
from unittest.mock import Mock, AsyncMock


class MockUpdate:
    """Mock Telegram Update object for testing."""
    
    def __init__(self, message_text: str, user_id: str = "test_user"):
        self.message = Mock()
        self.message.text = message_text
        self.message.reply_text = AsyncMock()
        self.message.reply_chat_action = AsyncMock()
        
        self.effective_user = Mock()
        self.effective_user.id = user_id
        self.effective_user.first_name = "TestUser"
        
        # Add callback query support for interactive navigation
        self.callback_query = None


class MockCallbackQuery:
    """Mock Telegram CallbackQuery object for testing."""
    
    def __init__(self, data: str = ""):
        self.data = data
        self.edit_message_text = AsyncMock()
        self.answer = AsyncMock()
        
        # Add from_user attribute that callback handlers expect
        self.from_user = Mock()
        self.from_user.id = "test_user"
        self.from_user.first_name = "TestUser"


class MockContext:
    """Mock Telegram Context object for testing."""
    
    def __init__(self, args: list):
        self.args = args


async def test_enhanced_crops_command():
    """Test the enhanced crops command with seasonal filtering."""
    
    print("🧪 Testing Enhanced /crops Command with Seasonal Filtering")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "name": "Current Season (Default)",
            "command": "/crops Lilongwe",
            "expected_season": "current"
        },
        {
            "name": "Rainy Season",
            "command": "/crops Lilongwe rainy",
            "expected_season": "rainy"
        },
        {
            "name": "Dry Season",
            "command": "/crops -13.98, 33.78 dry",
            "expected_season": "dry"
        },
        {
            "name": "All Seasons Comparison",
            "command": "/crops Area 1 all",
            "expected_season": "all"
        },
        {
            "name": "Rainy Season (Alternative)",
            "command": "/crops Lilongwe rain",
            "expected_season": "rain"
        },
        {
            "name": "No Location (Should show help)",
            "command": "/crops",
            "expected_season": "current"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Command: {test_case['command']}")
        print(f"Expected Season: {test_case['expected_season']}")
        
        # Parse command arguments
        parts = test_case['command'].split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Create mock objects
        update = MockUpdate(test_case['command'])
        context = MockContext(args)
        
        try:
            # Call the crops command
            await crops_command(update, context)
            
            # Check if reply_text was called
            if update.message.reply_text.called:
                print("✅ Command executed successfully")
                
                # Get the response text
                response_text = update.message.reply_text.call_args[0][0]
                
                # Check for seasonal indicators in response
                if test_case['expected_season'] in ['rainy', 'rain', 'wet']:
                    if 'Rainy Season' in response_text or 'rainy' in response_text.lower():
                        print("✅ Rainy season context detected")
                    else:
                        print("⚠️  Rainy season context not found")
                        
                elif test_case['expected_season'] == 'dry':
                    if 'Dry Season' in response_text or 'dry' in response_text.lower():
                        print("✅ Dry season context detected")
                    else:
                        print("⚠️  Dry season context not found")
                        
                elif test_case['expected_season'] == 'all':
                    if 'All Seasons' in response_text or 'Multi-Season' in response_text:
                        print("✅ All seasons comparison detected")
                    else:
                        print("⚠️  All seasons comparison not found")
                        
                elif test_case['expected_season'] == 'current':
                    if 'Current Season' in response_text or 'Traditional Analysis' in response_text:
                        print("✅ Current season analysis detected")
                    else:
                        print("⚠️  Current season analysis not found")
                
                # Check for seasonal navigation hints
                if 'TRY OTHER SEASONS' in response_text:
                    print("✅ Seasonal navigation hints found")
                else:
                    print("⚠️  Seasonal navigation hints not found")
                    
            else:
                print("❌ No response generated")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)


async def test_recommendation_engine_methods():
    """Test the new recommendation engine methods."""
    
    print("\n🔧 Testing Recommendation Engine Methods")
    print("=" * 60)
    
    # Mock data
    mock_rainfall_data = {
        'total_7day_rainfall': 25.5,
        'forecast_7day_rainfall': 15.2,
        'rainy_days_forecast': 3
    }
    
    mock_weather_data = {
        'temperature': 24.5,
        'humidity': 65
    }
    
    test_coordinates = (-13.9833, 33.7833)
    
    # Test methods
    test_methods = [
        {
            "name": "Rainy Season Recommendations",
            "method": recommendation_engine.generate_rainy_season_recommendations,
            "expected_season": "rainy_season"
        },
        {
            "name": "Dry Season Recommendations", 
            "method": recommendation_engine.generate_dry_season_recommendations,
            "expected_season": "dry_season"
        },
        {
            "name": "All Seasons Comparison",
            "method": recommendation_engine.generate_all_seasons_comparison,
            "expected_season": "mixed"
        }
    ]
    
    for test_method in test_methods:
        print(f"\n📊 Testing: {test_method['name']}")
        
        try:
            # Call the method
            result = test_method['method'](
                mock_rainfall_data, 
                mock_weather_data, 
                test_coordinates[0], 
                test_coordinates[1]
            )
            
            # Verify result structure
            if 'recommendations' in result:
                print(f"✅ Recommendations generated: {len(result['recommendations'])} crops")
                
                # Check environmental summary
                env_summary = result.get('environmental_summary', {})
                if env_summary:
                    print(f"✅ Environmental summary: {env_summary.get('current_season', 'unknown')}")
                    
                    # Verify season-specific data
                    if test_method['expected_season'] == 'rainy_season':
                        if env_summary.get('current_season') == 'rainy_season':
                            print("✅ Rainy season data confirmed")
                        else:
                            print("⚠️  Rainy season data mismatch")
                            
                    elif test_method['expected_season'] == 'dry_season':
                        if env_summary.get('current_season') == 'dry_season':
                            print("✅ Dry season data confirmed")
                        else:
                            print("⚠️  Dry season data mismatch")
                            
                    elif test_method['expected_season'] == 'mixed':
                        if 'season_comparison' in result:
                            print("✅ Season comparison data found")
                        else:
                            print("⚠️  Season comparison data missing")
                
            else:
                print("❌ No recommendations in result")
                
        except Exception as e:
            print(f"❌ Error: {e}")


async def test_interactive_seasonal_navigation():
    """Test the interactive seasonal navigation callbacks."""
    
    print("\n🎮 Testing Interactive Seasonal Navigation")
    print("=" * 60)
    
    # Test cases for callback queries
    test_cases = [
        {
            "name": "Seasonal Navigation - Rainy Season",
            "callback_data": "season:Lilongwe:rainy",
            "callback_type": "seasonal"
        },
        {
            "name": "Seasonal Navigation - Dry Season", 
            "callback_data": "season:Lilongwe:dry",
            "callback_type": "seasonal"
        },
        {
            "name": "Weather Quick Access",
            "callback_data": "weather:Lilongwe",
            "callback_type": "weather"
        },
        {
            "name": "Rainfall Quick Access",
            "callback_data": "rainfall:Lilongwe",
            "callback_type": "rainfall"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📱 Test {i}: {test_case['name']}")
        print(f"Callback Data: {test_case['callback_data']}")
        
        # Create mock objects
        mock_update = MockUpdate("")
        mock_update.callback_query = MockCallbackQuery(test_case['callback_data'])
        mock_context = MockContext([])
        
        try:
            # Call the appropriate callback based on type
            if test_case['callback_type'] == 'seasonal':
                await seasonal_callback(mock_update, mock_context)
            elif test_case['callback_type'] == 'weather':
                await weather_callback(mock_update, mock_context)
            elif test_case['callback_type'] == 'rainfall':
                await rainfall_callback(mock_update, mock_context)
            
            # Check if edit_message_text was called (for callback responses)
            if mock_update.callback_query.edit_message_text.called:
                print("✅ Callback response generated successfully")
                
                # Get the response text
                response_text = mock_update.callback_query.edit_message_text.call_args[0][0]
                
                # Check for appropriate content based on callback type
                if test_case['callback_type'] == 'seasonal':
                    if 'Season' in response_text or 'Crop' in response_text:
                        print("✅ Seasonal recommendations found")
                    else:
                        print("⚠️  Seasonal recommendations not found")
                        
                elif test_case['callback_type'] == 'weather':
                    if 'Weather' in response_text or '°C' in response_text:
                        print("✅ Weather information found")
                    else:
                        print("⚠️  Weather information not found")
                        
                elif test_case['callback_type'] == 'rainfall':
                    if 'Rainfall' in response_text or 'mm' in response_text:
                        print("✅ Rainfall information found")
                    else:
                        print("⚠️  Rainfall information not found")
                
                # Check for interactive keyboard
                if 'reply_markup' in mock_update.callback_query.edit_message_text.call_args[1]:
                    print("✅ Interactive keyboard included")
                else:
                    print("⚠️  Interactive keyboard missing")
                    
            else:
                print("❌ No callback response generated")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)


async def main():
    """Main test function."""
    
    print("🚀 Enhanced /crops Command Testing Suite")
    print("=" * 60)
    
    # Test the command handler
    await test_enhanced_crops_command()
    
    # Test the recommendation engine methods
    await test_recommendation_engine_methods()
    
    # Test the interactive seasonal navigation callbacks
    await test_interactive_seasonal_navigation()
    
    print("\n🎉 Testing Complete!")
    print("\n📝 Summary:")
    print("• Enhanced /crops command with seasonal filtering")
    print("• Rainy season recommendations (Nov-Apr)")
    print("• Dry season recommendations (May-Oct)")
    print("• All seasons comparison")
    print("• Interactive seasonal navigation buttons")
    print("• Quick access to weather and rainfall data")
    print("• Seasonal navigation hints")
    print("• Updated help documentation")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(main()) 
 