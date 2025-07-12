"""
Crop handler for the Agricultural Advisor Bot.
Handles crop recommendation commands using the advanced recommendation system with AI enhancement.
"""
from telegram import Update
from telegram.ext import ContextTypes
from scripts.utils.logger import logger
from scripts.weather_engine.weather_api import weather_api
from scripts.weather_engine.coordinate_handler import coordinate_handler
from scripts.crop_advisor.recommendation_engine import recommendation_engine
from scripts.crop_advisor.seasonal_advisor import seasonal_advisor
# Week 3 Addition: AI integration
from scripts.ai_agent.response_synthesizer import response_synthesizer


async def crops_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /crops command for advanced crop recommendations with AI enhancement.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    
    # Extract location from command arguments
    location_text = ' '.join(context.args) if context.args else ""
    
    logger.log_user_query(user_id, f"/crops {location_text}", "command")
    
    if not location_text:
        await update.message.reply_text(
            "🌱 Please provide a location for crop recommendations!\n\n"
            "**Examples:**\n"
            "• `/crops Lilongwe`\n"
            "• `/crops -13.9833, 33.7833`\n"
            "• `/crops Area 1`\n\n"
            "The AI-enhanced system provides:\n"
            "• Advanced multi-factor analysis\n"
            "• AI-generated actionable insights\n"
            "• Specific variety recommendations\n"
            "• Seasonal timing advice\n"
            "• Risk assessment and mitigation\n\n"
            "Use `/help` for more coordinate formats.",
            parse_mode='Markdown'
        )
        logger.log_bot_response(user_id, "crops_error", False)
        return
    
    # Parse coordinates
    coordinates = coordinate_handler.parse_coordinates(location_text, user_id)
    
    if not coordinates:
        await update.message.reply_text(
            "❌ Could not understand the location format.\n\n"
            f"You entered: `{location_text}`\n\n"
            "**Supported formats:**\n"
            "• Coordinates: `-13.9833, 33.7833`\n"
            "• Named locations: `Lilongwe`, `Area 1`\n"
            "• Use `/help` for more examples.",
            parse_mode='Markdown'
        )
        logger.log_bot_response(user_id, "crops_parse_error", False)
        return
    
    lat, lon = coordinates
    
    # Send "typing" indicator
    await update.message.reply_chat_action("typing")
    
    # Get weather and rainfall data
    rainfall_data = weather_api.get_rainfall_data(lat, lon, user_id)
    weather_data = weather_api.get_current_weather(lat, lon, user_id)
    
    if not rainfall_data or not weather_data:
        await update.message.reply_text(
            "❌ Unable to fetch weather data for crop recommendations.\n"
            "Please try again later or check your location.\n\n"
            "**Fallback Options:**\n"
            "• Try a nearby major city\n"
            "• Check your coordinates format\n"
            "• Use `/weather` to test location first"
        )
        logger.log_bot_response(user_id, "crops_api_error", False)
        return
    
    # Generate advanced recommendations
    try:
        # Send typing indicator for AI processing
        await update.message.reply_chat_action("typing")
        
        recommendations = recommendation_engine.generate_recommendations(
            rainfall_data, weather_data, lat, lon
        )
        
        # Get seasonal advice
        seasonal_advice = seasonal_advisor.get_seasonal_recommendations(
            rainfall_data, weather_data
        )
        
        # Week 3 Enhancement: AI-synthesized response
        try:
            ai_enhanced_message = await response_synthesizer.synthesize_crop_recommendations(
                recommendations, weather_data, location_text, user_id
            )
            
            await update.message.reply_text(ai_enhanced_message, parse_mode='Markdown')
            logger.log_bot_response(user_id, "crops_success_ai_enhanced", True)
            
        except Exception as ai_error:
            logger.error(f"AI enhancement failed, using fallback: {ai_error}", user_id)
            
            # Fallback to traditional comprehensive response
            fallback_message = _format_comprehensive_response(
                recommendations, seasonal_advice, lat, lon, location_text
            )
            
            await update.message.reply_text(fallback_message, parse_mode='Markdown')
            logger.log_bot_response(user_id, "crops_success_fallback", True)
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}", user_id)
        
        # Enhanced error handling with helpful guidance
        error_message = """❌ Error generating recommendations. 

**Possible Issues:**
• Weather service temporary unavailable
• Location coordinates invalid
• System processing overload

**Try These Solutions:**
• Wait 30 seconds and try again
• Use a nearby major city name
• Check coordinate format: `lat, lon`
• Use `/weather` first to test location

**Alternative Commands:**
• `/rain` - Rainfall analysis only
• `/weather` - Current conditions
• `/help` - All available commands

Please try again in a moment."""
        
        await update.message.reply_text(error_message, parse_mode='Markdown')
        logger.log_bot_response(user_id, "crops_processing_error", False)


def _format_comprehensive_response(recommendations: dict, seasonal_advice: dict, 
                                 lat: float, lon: float, location_text: str) -> str:
    """
    Format comprehensive crop recommendations into a user-friendly message.
    This is the fallback response when AI enhancement fails.
    
    Args:
        recommendations: Advanced recommendations data
        seasonal_advice: Seasonal advice data
        lat: Latitude
        lon: Longitude
        location_text: Original location text
        
    Returns:
        Formatted comprehensive recommendations message
    """
    # Get environmental summary
    env_summary = recommendations.get('environmental_summary', {})
    coord_str = coordinate_handler.format_coordinates(lat, lon)
    
    # Check if it's in Lilongwe area
    is_lilongwe = coordinate_handler.is_lilongwe_area(lat, lon)
    area_note = "🎯 *Lilongwe area detected*" if is_lilongwe else ""
    
    # Start building the message
    message = f"""
🌾 **Crop Recommendations Report** (Traditional Analysis)

📍 **Location:** {location_text}
🗺️ **Coordinates:** {coord_str}
{area_note}

🌤️ **Environmental Conditions:**
• **Recent Rainfall:** {env_summary.get('total_7day_rainfall', 0):.1f}mm (7 days)
• **Forecast Rainfall:** {env_summary.get('forecast_7day_rainfall', 0):.1f}mm (7 days)
• **Seasonal Estimate:** {env_summary.get('estimated_seasonal_rainfall', 0):.0f}mm
• **Temperature:** {env_summary.get('current_temperature', 25):.1f}°C
• **Humidity:** {env_summary.get('humidity', 50)}%
• **Season:** {env_summary.get('current_season', 'unknown').replace('_', ' ').title()}

"""
    
    # Add top recommendations
    top_recommendations = recommendations.get('recommendations', [])[:3]
    if top_recommendations:
        message += "🏆 **TOP CROP RECOMMENDATIONS:**\n"
        
        for i, rec in enumerate(top_recommendations, 1):
            crop_data = rec['crop_data']
            suitability = rec['suitability_level']
            total_score = rec['total_score']
            reasons = rec.get('reasons', [])
            
            # Suitability emoji
            suitability_emoji = {
                'excellent': '🟢',
                'good': '🟡',
                'fair': '🟠',
                'poor': '🔴'
            }.get(suitability, '⚪')
            
            message += f"\n**{i}. {crop_data['name']}** {suitability_emoji} {suitability.title()}\n"
            message += f"• **Score:** {total_score:.0f}/100\n"
            message += f"• **Category:** {crop_data.get('category', 'unknown').replace('_', ' ').title()}\n"
            
            # Add top reasons
            if reasons:
                message += f"• **Why recommended:** {', '.join(reasons[:2])}\n"
            
            # Add top varieties
            recommended_varieties = rec.get('recommended_varieties', [])
            if recommended_varieties:
                top_variety = recommended_varieties[0]
                variety_name = top_variety['variety_data'].get('name', 'Unknown')
                message += f"• **Best variety:** {variety_name}\n"
    
    # Add seasonal timing advice
    current_month = env_summary.get('current_month', 'Unknown')
    planting_calendar = recommendations.get('planting_calendar', [])
    
    if planting_calendar:
        message += f"\n📅 **PLANTING TIMING ({current_month}):**\n"
        
        # Check for current planting opportunities
        current_opportunities = []
        for crop_timing in planting_calendar:
            if crop_timing.get('season_match'):
                current_opportunities.append(crop_timing)
        
        if current_opportunities:
            message += "🟢 **Optimal planting time for:**\n"
            for timing in current_opportunities[:2]:
                crop_name = timing.get('crop_name', 'Unknown')
                window = timing.get('optimal_timing', {})
                message += f"• {crop_name} ({window.get('start_month', 'Unknown')} - {window.get('end_month', 'Unknown')})\n"
        else:
            message += "🟡 **Not optimal planting time currently**\n"
            message += "• Consider preparing for upcoming planting seasons\n"
    
    # Add seasonal advice
    seasonal_context = seasonal_advice.get('seasonal_context', {})
    monthly_advice = seasonal_advice.get('monthly_advice', {})
    
    if monthly_advice:
        message += f"\n🗓️ **THIS MONTH'S PRIORITIES:**\n"
        priority_activities = monthly_advice.get('priority_activities', [])
        for activity in priority_activities[:3]:
            message += f"• {activity}\n"
    
    # Add weather-based recommendations
    weather_recs = seasonal_advice.get('weather_recommendations', [])
    if weather_recs:
        message += f"\n🌦️ **WEATHER GUIDANCE:**\n"
        for rec in weather_recs[:2]:
            message += f"• {rec}\n"
    
    # Add action items
    message += "\n💡 **NEXT STEPS:**\n"
    
    # Determine next steps based on season and conditions
    current_season = env_summary.get('current_season', 'unknown')
    seasonal_rainfall = env_summary.get('estimated_seasonal_rainfall', 0)
    
    if current_season == 'rainy_season':
        if seasonal_rainfall > 400:
            message += "• Plan for main season crops\n"
            message += "• Ensure proper drainage systems\n"
        else:
            message += "• Focus on drought-tolerant varieties\n"
            message += "• Consider water conservation methods\n"
    else:
        message += "• Prepare for next planting season\n"
        message += "• Consider dry-season vegetables\n"
    
    message += "• Monitor weather forecasts regularly\n"
    
    # Add helpful commands
    message += "\n🔧 **MORE INFORMATION:**\n"
    message += "• `/rain` - Detailed rainfall analysis\n"
    message += "• `/weather` - Current weather conditions\n"
    message += "• `/help` - All available commands\n"
    
    # Note about AI enhancement
    message += "\n📝 *Note: AI enhancement temporarily unavailable - showing traditional analysis*"
    
    return message


# Backwards compatibility function (simplified)
def _generate_crop_recommendations(rainfall_data: dict, weather_data: dict, lat: float, lon: float) -> dict:
    """
    Legacy function for backwards compatibility.
    Now redirects to the advanced recommendation engine.
    
    Args:
        rainfall_data: Rainfall analysis data
        weather_data: Current weather data
        lat: Latitude
        lon: Longitude
        
    Returns:
        Basic recommendations dictionary for compatibility
    """
    try:
        advanced_recommendations = recommendation_engine.generate_recommendations(
            rainfall_data, weather_data, lat, lon
        )
        
        # Convert to legacy format for any existing code that depends on it
        legacy_recommendations = []
        for rec in advanced_recommendations.get('recommendations', []):
            legacy_recommendations.append({
                'crop_id': rec['crop_id'],
                'crop_data': rec['crop_data'],
                'score': rec['total_score'],
                'reasons': rec.get('reasons', [])
            })
        
        return {
            'recommendations': legacy_recommendations,
            'conditions': advanced_recommendations.get('environmental_summary', {})
        }
    except Exception as e:
        logger.error(f"Error in legacy recommendation function: {e}")
        return {'recommendations': [], 'conditions': {}}


def _format_crop_response(recommendations: dict, rainfall_data: dict, weather_data: dict, lat: float, lon: float) -> str:
    """
    Legacy formatting function for backwards compatibility.
    Now redirects to the comprehensive response formatter.
    
    Args:
        recommendations: Recommendations data
        rainfall_data: Rainfall data
        weather_data: Weather data
        lat: Latitude
        lon: Longitude
        
    Returns:
        Formatted legacy response
    """
    try:
        # Get fresh data using the new system
        advanced_recommendations = recommendation_engine.generate_recommendations(
            rainfall_data, weather_data, lat, lon
        )
        
        seasonal_advice = seasonal_advisor.get_seasonal_recommendations(
            rainfall_data, weather_data
        )
        
        # Use the new comprehensive formatter
        return _format_comprehensive_response(
            advanced_recommendations, seasonal_advice, lat, lon, "Requested Location"
        )
    except Exception as e:
        logger.error(f"Error in legacy formatting function: {e}")
        return "❌ Error formatting crop recommendations. Please try again." 