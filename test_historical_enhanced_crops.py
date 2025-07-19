#!/usr/bin/env python3
"""
Test script for historical-enhanced crop recommendations.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/telegram_token.env')

async def test_historical_enhanced_crops():
    """Test the historical-enhanced crop recommendation engine."""
    try:
        from scripts.weather_engine.weather_api import weather_api
        from scripts.weather_engine.coordinate_handler import coordinate_handler
        from scripts.crop_advisor.historical_enhanced_engine import historical_enhanced_engine
        
        print("🧪 Testing Historical-Enhanced Crop Recommendations")
        print("=" * 50)
        
        # Test location (Lilongwe coordinates)
        test_location = "Lilongwe"
        lat, lon = -13.9833, 33.7833
        
        print(f"📍 Test Location: {test_location} ({lat}, {lon})")
        
        # Get weather and rainfall data
        print("\n🌦️ Fetching weather data...")
        rainfall_data = weather_api.get_rainfall_data(lat, lon, "test_user")
        weather_data = weather_api.get_current_weather(lat, lon, "test_user")
        
        if not rainfall_data or not weather_data:
            print("❌ Failed to fetch weather data")
            return
        
        print("✅ Weather data fetched successfully")
        print(f"   • Temperature: {weather_data.get('temperature', 'N/A')}°C")
        print(f"   • Humidity: {weather_data.get('humidity', 'N/A')}%")
        print(f"   • 7-day rainfall: {rainfall_data.get('total_7day_rainfall', 'N/A')}mm")
        
        # Test historical-enhanced recommendations
        print("\n🌱 Generating historical-enhanced recommendations...")
        recommendations = historical_enhanced_engine.generate_historical_enhanced_recommendations(
            rainfall_data, weather_data, lat, lon, historical_years=5
        )
        
        if not recommendations:
            print("❌ Failed to generate recommendations")
            return
        
        print("✅ Historical-enhanced recommendations generated")
        
        # Display results
        print("\n📊 Results Summary:")
        print("-" * 30)
        
        # Historical summary
        historical_summary = recommendations.get('historical_summary', {})
        if historical_summary:
            print(f"📈 Historical Analysis:")
            print(f"   • Years analyzed: {historical_summary.get('years_analyzed', 'N/A')}")
            print(f"   • Climate trend: {historical_summary.get('climate_trend', 'N/A')}")
            print(f"   • Rainfall variability: {historical_summary.get('rainfall_variability', 0):.1%}")
            print(f"   • Drought frequency: {historical_summary.get('drought_frequency', 0)}")
            print(f"   • Flood frequency: {historical_summary.get('flood_frequency', 0)}")
        
        # Top recommendations
        top_crops = recommendations.get('recommendations', [])
        if top_crops:
            print(f"\n🥇 Top Crop Recommendations:")
            for i, crop in enumerate(top_crops[:3], 1):
                crop_name = crop.get('crop_name', crop.get('crop_id', 'Unknown'))
                total_score = crop.get('total_score', 0)
                reliability_score = crop.get('reliability_score', 0)
                risk_score = crop.get('risk_score', 0)
                
                print(f"   {i}. {crop_name}")
                print(f"      • Score: {total_score:.1f}")
                print(f"      • Reliability: {reliability_score:.1%}")
                print(f"      • Risk: {risk_score:.1%}")
                
                # Show top variety
                top_varieties = crop.get('top_varieties', [])
                if top_varieties:
                    best_variety = top_varieties[0]
                    variety_name = best_variety.get('name', 'Unknown')
                    print(f"      • Best variety: {variety_name}")
        
        # Climate analysis
        climate_analysis = recommendations.get('climate_analysis', {})
        if climate_analysis:
            print(f"\n📈 Climate Trend Analysis:")
            print(f"   • Trend: {climate_analysis.get('trend', 'N/A')}")
            print(f"   • Description: {climate_analysis.get('trend_description', 'N/A')}")
            
            recommendations_list = climate_analysis.get('recommendations', [])
            if recommendations_list:
                print(f"   • Recommendations:")
                for rec in recommendations_list[:2]:
                    print(f"     - {rec}")
        
        # Planting calendar
        planting_calendar = recommendations.get('planting_calendar', [])
        if planting_calendar:
            print(f"\n📅 Planting Calendar:")
            for crop_timing in planting_calendar[:2]:
                crop_name = crop_timing.get('crop_name', 'Unknown')
                original_window = crop_timing.get('original_window', [])
                adjusted_window = crop_timing.get('adjusted_window', [])
                reliability = crop_timing.get('historical_reliability', 0)
                
                print(f"   • {crop_name}")
                print(f"     • Original window: {', '.join(original_window)}")
                print(f"     • Adjusted window: {', '.join(adjusted_window)}")
                print(f"     • Reliability: {reliability:.1%}")
        
        print("\n✅ Historical-enhanced crop recommendations test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_historical_enhanced_crops()) 