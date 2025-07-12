"""
Weather handler for the Agricultural Advisor Bot.
Handles weather-related commands including /weather and /rain.
"""
from telegram import Update
from telegram.ext import ContextTypes
from scripts.utils.logger import logger
from scripts.weather_engine.weather_api import weather_api
from scripts.weather_engine.coordinate_handler import coordinate_handler


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /weather command.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    
    # Extract location from command arguments
    location_text = ' '.join(context.args) if context.args else ""
    
    logger.log_user_query(user_id, f"/weather {location_text}", "command")
    
    if not location_text:
        await update.message.reply_text(
            "🌦️ Please provide a location!\n\n"
            "**Examples:**\n"
            "• `/weather Lilongwe`\n"
            "• `/weather -13.9833, 33.7833`\n"
            "• `/weather Area 1`\n\n"
            "Use `/help` for more coordinate formats.",
            parse_mode='Markdown'
        )
        logger.log_bot_response(user_id, "weather_error", False)
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
        logger.log_bot_response(user_id, "weather_parse_error", False)
        return
    
    lat, lon = coordinates
    
    # Send "typing" indicator
    await update.message.reply_chat_action("typing")
    
    # Get weather data
    weather_data = weather_api.get_current_weather(lat, lon, user_id)
    
    if not weather_data:
        await update.message.reply_text(
            "❌ Unable to fetch weather data at the moment.\n"
            "Please try again later or check your location."
        )
        logger.log_bot_response(user_id, "weather_api_error", False)
        return
    
    # Format weather response
    weather_message = _format_weather_response(weather_data, lat, lon)
    
    try:
        await update.message.reply_text(weather_message, parse_mode='Markdown')
        logger.log_bot_response(user_id, "weather_success", True)
    except Exception as e:
        logger.error(f"Error sending weather message: {e}", user_id)
        await update.message.reply_text("Weather data retrieved but there was an error formatting the response.")
        logger.log_bot_response(user_id, "weather_format_error", False)


async def rain_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /rain command for detailed rainfall analysis.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    
    # Extract location from command arguments
    location_text = ' '.join(context.args) if context.args else ""
    
    logger.log_user_query(user_id, f"/rain {location_text}", "command")
    
    if not location_text:
        await update.message.reply_text(
            "🌧️ Please provide a location for rainfall analysis!\n\n"
            "**Examples:**\n"
            "• `/rain Lilongwe`\n"
            "• `/rain -13.9833, 33.7833`\n"
            "• `/rain Area 1`\n\n"
            "Use `/help` for more coordinate formats.",
            parse_mode='Markdown'
        )
        logger.log_bot_response(user_id, "rain_error", False)
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
        logger.log_bot_response(user_id, "rain_parse_error", False)
        return
    
    lat, lon = coordinates
    
    # Send "typing" indicator
    await update.message.reply_chat_action("typing")
    
    # Get rainfall data
    rainfall_data = weather_api.get_rainfall_data(lat, lon, user_id)
    
    if not rainfall_data:
        await update.message.reply_text(
            "❌ Unable to fetch rainfall data at the moment.\n"
            "Please try again later or check your location."
        )
        logger.log_bot_response(user_id, "rain_api_error", False)
        return
    
    # Format rainfall response
    rainfall_message = _format_rainfall_response(rainfall_data, lat, lon)
    
    try:
        await update.message.reply_text(rainfall_message, parse_mode='Markdown')
        logger.log_bot_response(user_id, "rain_success", True)
    except Exception as e:
        logger.error(f"Error sending rainfall message: {e}", user_id)
        await update.message.reply_text("Rainfall data retrieved but there was an error formatting the response.")
        logger.log_bot_response(user_id, "rain_format_error", False)


def _format_weather_response(weather_data: dict, lat: float, lon: float) -> str:
    """
    Format weather data into a user-friendly message.
    
    Args:
        weather_data: Weather data dictionary
        lat: Latitude
        lon: Longitude
        
    Returns:
        Formatted weather message
    """
    location = weather_data.get('location', 'Unknown')
    country = weather_data.get('country', '')
    temp = weather_data.get('temperature', 0)
    feels_like = weather_data.get('feels_like', 0)
    humidity = weather_data.get('humidity', 0)
    weather_desc = weather_data.get('weather', 'Unknown')
    wind_speed = weather_data.get('wind_speed', 0)
    rainfall = weather_data.get('rainfall', 0)
    
    # Format coordinates
    coord_str = coordinate_handler.format_coordinates(lat, lon)
    
    # Check if it's in Lilongwe area
    is_lilongwe = coordinate_handler.is_lilongwe_area(lat, lon)
    area_note = "🎯 *Lilongwe area detected*" if is_lilongwe else ""
    
    message = f"""
🌦️ **Current Weather Report**

📍 **Location:** {location}, {country}
🗺️ **Coordinates:** {coord_str}
{area_note}

🌡️ **Temperature:** {temp:.1f}°C (feels like {feels_like:.1f}°C)
☁️ **Conditions:** {weather_desc.title()}
💧 **Humidity:** {humidity}%
💨 **Wind Speed:** {wind_speed:.1f} m/s
"""
    
    if rainfall > 0:
        message += f"🌧️ **Current Rainfall:** {rainfall:.1f} mm/hour\n"
    else:
        message += "☀️ **No current rainfall**\n"
    
    # Add agricultural context
    message += "\n🌾 **Agricultural Context:**\n"
    
    if humidity > 70:
        message += "• High humidity - good for most crops\n"
    elif humidity < 40:
        message += "• Low humidity - consider irrigation\n"
    else:
        message += "• Moderate humidity - favorable conditions\n"
    
    if temp > 30:
        message += "• Hot weather - ensure adequate watering\n"
    elif temp < 15:
        message += "• Cool weather - monitor frost-sensitive crops\n"
    else:
        message += "• Favorable temperature for most crops\n"
    
    if rainfall > 0:
        message += "• Current rainfall - good for crop growth\n"
    
    message += "\n💡 *Use `/rain` for detailed rainfall analysis*"
    
    return message


def _format_rainfall_response(rainfall_data: dict, lat: float, lon: float) -> str:
    """
    Format rainfall data into a user-friendly message.
    
    Args:
        rainfall_data: Rainfall data dictionary
        lat: Latitude
        lon: Longitude
        
    Returns:
        Formatted rainfall message
    """
    location = rainfall_data.get('location', 'Unknown')
    current_rainfall = rainfall_data.get('current_rainfall', 0)
    humidity = rainfall_data.get('humidity', 0)
    total_7day = rainfall_data.get('total_7day_rainfall', 0)
    rainy_days = rainfall_data.get('rainy_days_forecast', 0)
    forecast_rainfall = rainfall_data.get('forecast_rainfall', [])
    
    # Format coordinates
    coord_str = coordinate_handler.format_coordinates(lat, lon)
    
    # Check if it's in Lilongwe area
    is_lilongwe = coordinate_handler.is_lilongwe_area(lat, lon)
    area_note = "🎯 *Lilongwe area detected*" if is_lilongwe else ""
    
    message = f"""
🌧️ **Rainfall Analysis Report**

📍 **Location:** {location}
🗺️ **Coordinates:** {coord_str}
{area_note}

**Current Conditions:**
• **Current Rainfall:** {current_rainfall:.1f} mm/hour
• **Humidity:** {humidity}%

**7-Day Forecast:**
• **Total Expected Rainfall:** {total_7day:.1f} mm
• **Rainy Days Expected:** {rainy_days} days
"""
    
    # Add rainfall forecast details
    if forecast_rainfall:
        message += "\n**Upcoming Rainfall:**\n"
        for rain_event in forecast_rainfall[:3]:  # Show first 3 events
            datetime_str = rain_event['datetime']
            rainfall_mm = rain_event['rainfall_mm']
            weather = rain_event['weather']
            
            # Format datetime
            try:
                from datetime import datetime
                dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                date_str = dt.strftime('%a %d %b, %H:%M')
            except:
                date_str = datetime_str
            
            message += f"• {date_str}: {rainfall_mm:.1f}mm ({weather})\n"
    
    # Add agricultural recommendations
    message += "\n🌾 **Agricultural Recommendations:**\n"
    
    if total_7day > 50:
        message += "• Excellent rainfall expected - perfect for planting\n"
        message += "• Consider planting rain-fed crops\n"
    elif total_7day > 20:
        message += "• Good rainfall expected - suitable for most crops\n"
        message += "• Monitor soil moisture levels\n"
    elif total_7day > 5:
        message += "• Light rainfall expected - may need supplemental irrigation\n"
        message += "• Choose drought-resistant varieties\n"
    else:
        message += "• Little rainfall expected - irrigation highly recommended\n"
        message += "• Focus on drought-tolerant crops\n"
    
    if rainy_days >= 4:
        message += "• Multiple rainy days - good for crop establishment\n"
    elif rainy_days >= 2:
        message += "• Moderate rainy days - plan field activities accordingly\n"
    else:
        message += "• Few rainy days - prepare for dry conditions\n"
    
    message += "\n💡 *Use `/crops` for specific crop recommendations*"
    
    return message 