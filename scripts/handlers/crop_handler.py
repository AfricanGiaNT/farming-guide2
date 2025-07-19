"""
Crop handler for the Agricultural Advisor Bot.
Handles crop recommendation commands using the advanced recommendation system with AI enhancement and historical data integration.
"""
import re
import hashlib
from urllib.parse import quote, unquote
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from scripts.utils.logger import logger
from scripts.weather_engine.weather_api import weather_api
from scripts.weather_engine.coordinate_handler import coordinate_handler
from scripts.crop_advisor.recommendation_engine import recommendation_engine
from scripts.crop_advisor.sqlite_based_recommendation_engine import sqlite_recommendation_engine
from scripts.crop_advisor.historical_enhanced_engine import historical_enhanced_engine
from scripts.crop_advisor.seasonal_advisor import seasonal_advisor
# Week 3 Addition: AI integration
from scripts.ai_agent.response_synthesizer import response_synthesizer

# Location cache to map hashes back to original locations
_location_cache = {}


def _sanitize_markdown(text: str) -> str:
    """
    Sanitize Markdown text to prevent Telegram parsing errors.
    
    Args:
        text: Raw text that may contain problematic Markdown
        
    Returns:
        Sanitized text safe for Telegram
    """
    if not text:
        return text
        
    # Fix unclosed bold/italic markers
    # Count asterisks and ensure they're balanced
    asterisk_count = text.count('*')
    if asterisk_count % 2 != 0:
        # Remove the last unpaired asterisk
        text = text.rstrip('*')
        
    # Fix unclosed bold markers
    bold_count = text.count('**')
    if bold_count % 2 != 0:
        # Remove the last unpaired bold marker
        text = text.rstrip('*')
        
    # Escape special characters that might cause issues
    # Escape underscores that aren't part of bold/italic
    text = re.sub(r'(?<!\*)_(?!\*)', r'\\_', text)
    
    # Escape brackets that might be interpreted as entities
    text = re.sub(r'\[([^\]]*)\]', r'\\[\1\\]', text)
    
    # Remove any remaining problematic characters
    text = re.sub(r'[<>]', '', text)
    
    # Ensure proper spacing around Markdown elements
    text = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', text)
    text = re.sub(r'\*([^*]+)\*', r'*\1*', text)
    
    # Limit message length to prevent truncation
    if len(text) > 4000:
        # Truncate and add ellipsis
        text = text[:3997] + "..."
        
    return text


async def crops_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /crops command for advanced crop recommendations with AI enhancement and seasonal filtering.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    
    # Parse command arguments for location and season
    args = context.args if context.args else []
    
    # Extract season filter (last argument if it's a valid season)
    season_filter = 'current'  # Default to current season
    location_parts = args.copy()
    
    if args:
        last_arg = args[-1].lower()
        valid_seasons = ['current', 'rainy', 'dry', 'all', 'rain', 'wet']
        
        if last_arg in valid_seasons:
            season_filter = last_arg
            location_parts = args[:-1]  # Remove season from location parts
    
    # Join remaining parts as location
    location_text = ' '.join(location_parts) if location_parts else ""
    
    logger.log_user_query(user_id, f"/crops {location_text} {season_filter}", "command")
    
    if not location_text:
        await update.message.reply_text(
            "🌱 Please provide a location for crop recommendations!\n\n"
            "**Examples:**\n"
            "• `/crops Lilongwe` - Current season recommendations\n"
            "• `/crops -13.9833, 33.7833 rainy` - Rainy season recommendations\n"
            "• `/crops Area 1 dry` - Dry season recommendations\n"
            "• `/crops Lilongwe all` - All seasons comparison\n\n"
            "**Seasonal Options:**\n"
            "• `current` (default) - Current season recommendations\n"
            "• `rainy` or `rain` - Rainy season (Nov-Apr) recommendations\n"
            "• `dry` - Dry season (May-Oct) recommendations\n"
            "• `all` - Compare all seasons\n\n"
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
    
    # Generate advanced recommendations based on season filter
    try:
        # Send typing indicator for AI processing
        await update.message.reply_chat_action("typing")
        
        # Generate recommendations based on season filter using SQLite agriculture guides
        if season_filter in ['rainy', 'rain', 'wet']:
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'rainy_season', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5
            )
        elif season_filter == 'dry':
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'dry_season', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5
            )
        elif season_filter == 'all':
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'current', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5
            )
        else:  # current season - Use SQLite-based engine
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'current', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5
            )
        
        # Get seasonal advice
        seasonal_advice = seasonal_advisor.get_seasonal_recommendations(
            rainfall_data, weather_data
        )
        
        # Week 3 Enhancement: AI-synthesized response
        try:
            ai_enhanced_message = await response_synthesizer.synthesize_crop_recommendations(
                recommendations, weather_data, location_text, user_id, season_filter
            )
            
            # Add interactive keyboard for seasonal navigation
            keyboard = _create_seasonal_keyboard(location_text, season_filter)
            logger.info(f"Created keyboard for AI response with {len(keyboard.inline_keyboard)} rows")
            
            await update.message.reply_text(
                ai_enhanced_message, 
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            logger.log_bot_response(user_id, f"crops_success_ai_enhanced_{season_filter}", True)
            
        except Exception as ai_error:
            logger.error(f"AI enhancement failed, using fallback: {ai_error}", user_id)
            
            # Fallback to traditional comprehensive response
            fallback_message = _format_sqlite_guide_response(
                recommendations, seasonal_advice, lat, lon, location_text, season_filter
            )
            
            # Add interactive keyboard for seasonal navigation
            keyboard = _create_seasonal_keyboard(location_text, season_filter)
            logger.info(f"Created keyboard for fallback response with {len(keyboard.inline_keyboard)} rows")
            
            await update.message.reply_text(
                fallback_message, 
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            logger.log_bot_response(user_id, f"crops_success_fallback_{season_filter}", True)
        
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


async def seasonal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle seasonal navigation callback queries.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    # Parse callback data: "s:location_hash:season_filter" or "s:location_hash:season_filter:offset:limit"
    callback_data = query.data
    logger.info(f"Seasonal callback received: {callback_data} from user {user_id}")
    
    if not callback_data.startswith('s:'):
        logger.error(f"Invalid callback data format: {callback_data}")
        await query.answer("Invalid callback data")
        return
    
    try:
        parts = callback_data.split(':', 4)  # Allow up to 5 parts for pagination
        if len(parts) < 3:
            logger.error(f"Invalid callback data parts: {parts}")
            await query.answer("Invalid callback data format")
            return
            
        _, location_hash, season_filter = parts[:3]
        
        # Parse pagination parameters if present
        offset = int(parts[3]) if len(parts) > 3 else 0
        limit = int(parts[4]) if len(parts) > 4 else 10  # Increased default limit from 5 to 10
        
        logger.info(f"Parsed callback data - location_hash: '{location_hash}', season: '{season_filter}', offset: {offset}, limit: {limit}")
        
        # Get original location from cache
        location = _location_cache.get(location_hash)
        if not location:
            logger.error(f"Location not found in cache for hash: {location_hash}")
            await query.answer("Location not found")
            return
        
        logger.info(f"Retrieved location from cache: '{location}'")
        
        logger.log_user_query(user_id, f"season_callback:{location}:{season_filter}:{offset}:{limit}", "callback")
        
        # Answer the callback query
        await query.answer(f"Loading {season_filter} season recommendations...")
        
        # Parse coordinates from location
        coordinates = coordinate_handler.parse_coordinates(location, user_id)
        if not coordinates:
            logger.error(f"Could not parse coordinates from location: '{location}'")
            await query.edit_message_text(
                _sanitize_markdown("❌ Could not parse location coordinates. Please try the command again."),
                parse_mode='Markdown'
            )
            return
        
        lat, lon = coordinates
        logger.info(f"Parsed coordinates: {lat}, {lon}")
        
        # Get weather and rainfall data
        rainfall_data = weather_api.get_rainfall_data(lat, lon, user_id)
        weather_data = weather_api.get_current_weather(lat, lon, user_id)
        
        if not rainfall_data or not weather_data:
            logger.error(f"Could not fetch weather data for coordinates: {lat}, {lon}")
            await query.edit_message_text(
                _sanitize_markdown("❌ Unable to fetch weather data. Please try again later."),
                parse_mode='Markdown'
            )
            return
        
        # Generate recommendations based on season filter with pagination
        if season_filter in ['rainy', 'rain', 'wet']:
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'rainy_season', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5,
                limit=limit,
                offset=offset
            )
        elif season_filter == 'dry':
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'dry_season', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5,
                limit=limit,
                offset=offset
            )
        elif season_filter == 'all':
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'current', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5,
                limit=limit,
                offset=offset
            )
        else:  # current season - Use SQLite-based engine
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'current', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5,
                limit=limit,
                offset=offset
            )
        
        # Get seasonal advice
        seasonal_advice = seasonal_advisor.get_seasonal_recommendations(
            rainfall_data, weather_data
        )
        
        # Generate response with interactive buttons
        try:
            ai_enhanced_message = await response_synthesizer.synthesize_crop_recommendations(
                recommendations, weather_data, location, user_id, season_filter
            )
            
            # Add interactive buttons with pagination support
            keyboard = _create_seasonal_keyboard(location, season_filter, offset, limit)
            
            # Check if the message content would actually change
            current_text = query.message.text if query.message.text else ""
            normalized_current = re.sub(r'\s+', ' ', current_text.strip())
            normalized_new = re.sub(r'\s+', ' ', ai_enhanced_message.strip())
            
            if normalized_current == normalized_new:
                # Content is the same, just answer the callback without editing
                await query.answer(f"Already showing {season_filter} season recommendations")
                logger.log_bot_response(user_id, f"season_callback_no_change_{season_filter}", True)
            else:
                # Content is different, update the message
                await query.edit_message_text(
                    ai_enhanced_message,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                logger.log_bot_response(user_id, f"season_callback_success_{season_filter}", True)
            
        except Exception as ai_error:
            logger.error(f"AI enhancement failed in callback: {ai_error}", user_id)
            
            # Fallback to traditional response
            fallback_message = _format_sqlite_guide_response(
                recommendations, seasonal_advice, lat, lon, location, season_filter, offset, limit
            )
            
            # Add interactive buttons with pagination support
            keyboard = _create_seasonal_keyboard(location, season_filter, offset, limit)
            
            # Check if the message content would actually change
            current_text = query.message.text if query.message.text else ""
            normalized_current = re.sub(r'\s+', ' ', current_text.strip())
            normalized_new = re.sub(r'\s+', ' ', fallback_message.strip())
            
            if normalized_current == normalized_new:
                # Content is the same, just answer the callback without editing
                await query.answer(f"Already showing {season_filter} season recommendations")
                logger.log_bot_response(user_id, f"season_callback_fallback_no_change_{season_filter}", True)
            else:
                # Content is different, update the message
                await query.edit_message_text(
                    fallback_message,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                logger.log_bot_response(user_id, f"season_callback_fallback_{season_filter}", True)
        
    except Exception as e:
        logger.error(f"Error in seasonal callback: {e}", user_id)
        await query.edit_message_text(
            _sanitize_markdown("❌ Error processing seasonal request. Please try again."),
            parse_mode='Markdown'
        )


async def weather_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle weather callback queries.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    # Parse callback data: "w:location_hash"
    callback_data = query.data
    logger.info(f"Weather callback received: {callback_data} from user {user_id}")
    
    if not callback_data.startswith('w:'):
        logger.error(f"Invalid weather callback data format: {callback_data}")
        await query.answer("Invalid callback data")
        return
    
    try:
        parts = callback_data.split(':', 1)
        if len(parts) != 2:
            logger.error(f"Invalid weather callback data parts: {parts}")
            await query.answer("Invalid callback data format")
            return
            
        _, location_hash = parts
        logger.info(f"Parsed weather callback data - location_hash: '{location_hash}'")
        
        # Get original location from cache
        location = _location_cache.get(location_hash)
        if not location:
            logger.error(f"Location not found in cache for hash: {location_hash}")
            await query.answer("Location not found")
            return
        
        logger.info(f"Retrieved location from cache: '{location}'")
        
        logger.log_user_query(user_id, f"weather_callback:{location}", "callback")
        
        # Answer the callback query
        await query.answer("Loading weather information...")
        
        # Parse coordinates from location
        coordinates = coordinate_handler.parse_coordinates(location, user_id)
        if not coordinates:
            logger.error(f"Could not parse coordinates from location: '{location}'")
            await query.edit_message_text(
                _sanitize_markdown("❌ Could not parse location coordinates."),
                parse_mode='Markdown'
            )
            return
        
        lat, lon = coordinates
        logger.info(f"Parsed coordinates for weather: {lat}, {lon}")
        
        # Get weather data
        weather_data = weather_api.get_current_weather(lat, lon, user_id)
        
        if not weather_data:
            logger.error(f"Could not fetch weather data for coordinates: {lat}, {lon}")
            await query.edit_message_text(
                _sanitize_markdown("❌ Unable to fetch weather data. Please try again later."),
                parse_mode='Markdown'
            )
            return
        
        # Format weather response
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 50)
        description = weather_data.get('description', 'Unknown')
        
        weather_message = f"""🌦️ **Weather for {location}**

**Current Conditions:**
• Temperature: {temp}°C
• Humidity: {humidity}%
• Conditions: {description}

**Agricultural Impact:**
• {'🌡️ High temperature stress' if temp > 35 else '🌡️ Cool temperatures' if temp < 15 else '🌡️ Favorable temperature'}
• {'💧 High humidity - monitor for disease' if humidity > 70 else '💧 Low humidity - consider irrigation' if humidity < 30 else '💧 Moderate humidity'}

**Quick Actions:**
• Use buttons below to explore crop recommendations
• `/rain {location}` - Detailed rainfall analysis
• `/crops {location}` - Crop recommendations
"""
        
        # Add back button
        keyboard = _create_seasonal_keyboard(location, 'current')
        
        # Check if the message content would actually change
        current_text = query.message.text if query.message.text else ""
        # Normalize text for comparison by removing extra whitespace and formatting
        normalized_current = re.sub(r'\s+', ' ', current_text.strip())
        normalized_new = re.sub(r'\s+', ' ', weather_message.strip())
        
        if normalized_current == normalized_new:
            # Content is the same, just answer the callback without editing
            await query.answer("Already showing weather information")
            logger.log_bot_response(user_id, "weather_callback_no_change", True)
        else:
            # Content is different, update the message
            await query.edit_message_text(
                _sanitize_markdown(weather_message),
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            logger.log_bot_response(user_id, "weather_callback_success", True)
        
    except Exception as e:
        logger.error(f"Error in weather callback: {e}", user_id)
        await query.edit_message_text(
            _sanitize_markdown("❌ Error loading weather information. Please try again."),
            parse_mode='Markdown'
        )


async def rainfall_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle rainfall callback queries.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    # Parse callback data: "r:location_hash"
    callback_data = query.data
    logger.info(f"Rainfall callback received: {callback_data} from user {user_id}")
    
    if not callback_data.startswith('r:'):
        logger.error(f"Invalid rainfall callback data format: {callback_data}")
        await query.answer("Invalid callback data")
        return
    
    try:
        parts = callback_data.split(':', 1)
        if len(parts) != 2:
            logger.error(f"Invalid rainfall callback data parts: {parts}")
            await query.answer("Invalid callback data format")
            return
            
        _, location_hash = parts
        logger.info(f"Parsed rainfall callback data - location_hash: '{location_hash}'")
        
        # Get original location from cache
        location = _location_cache.get(location_hash)
        if not location:
            logger.error(f"Location not found in cache for hash: {location_hash}")
            await query.answer("Location not found")
            return
        
        logger.info(f"Retrieved location from cache: '{location}'")
        
        logger.log_user_query(user_id, f"rainfall_callback:{location}", "callback")
        
        # Answer the callback query
        await query.answer("Loading rainfall analysis...")
        
        # Parse coordinates from location
        coordinates = coordinate_handler.parse_coordinates(location, user_id)
        if not coordinates:
            logger.error(f"Could not parse coordinates from location: '{location}'")
            await query.edit_message_text(
                _sanitize_markdown("❌ Could not parse location coordinates."),
                parse_mode='Markdown'
            )
            return
        
        lat, lon = coordinates
        logger.info(f"Parsed coordinates for rainfall: {lat}, {lon}")
        
        # Get rainfall data
        rainfall_data = weather_api.get_rainfall_data(lat, lon, user_id)
        
        if not rainfall_data:
            logger.error(f"Could not fetch rainfall data for coordinates: {lat}, {lon}")
            await query.edit_message_text(
                _sanitize_markdown("❌ Unable to fetch rainfall data. Please try again later."),
                parse_mode='Markdown'
            )
            return
        
        # Format rainfall response
        recent_rainfall = rainfall_data.get('total_7day_rainfall', 0)
        forecast_rainfall = rainfall_data.get('forecast_7day_rainfall', 0)
        rainy_days = rainfall_data.get('rainy_days_forecast', 0)
        
        rainfall_message = f"""🌧️ **Rainfall Analysis for {location}**

**Recent Rainfall (7 days):**
• Total: {recent_rainfall:.1f}mm
• Rainy days: {rainy_days}

**Forecast (7 days):**
• Expected: {forecast_rainfall:.1f}mm

**Agricultural Assessment:**
• {'💧 Excellent rainfall conditions' if recent_rainfall > 50 else '💧 Adequate rainfall' if recent_rainfall > 20 else '💧 Low rainfall - consider irrigation'}
• {'🌱 Good planting conditions' if forecast_rainfall > 30 else '🌱 Monitor forecast for planting'}

**Quick Actions:**
• Use buttons below to explore crop recommendations
• `/weather {location}` - Current weather conditions
• `/crops {location}` - Crop recommendations
"""
        
        # Add back button
        keyboard = _create_seasonal_keyboard(location, 'current')
        
        # Check if the message content would actually change
        current_text = query.message.text if query.message.text else ""
        # Normalize text for comparison by removing extra whitespace and formatting
        normalized_current = re.sub(r'\s+', ' ', current_text.strip())
        normalized_new = re.sub(r'\s+', ' ', rainfall_message.strip())
        
        if normalized_current == normalized_new:
            # Content is the same, just answer the callback without editing
            await query.answer("Already showing rainfall information")
            logger.log_bot_response(user_id, "rainfall_callback_no_change", True)
        else:
            # Content is different, update the message
            await query.edit_message_text(
                _sanitize_markdown(rainfall_message),
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            logger.log_bot_response(user_id, "rainfall_callback_success", True)
        
    except Exception as e:
        logger.error(f"Error in rainfall callback: {e}", user_id)
        await query.edit_message_text(
            _sanitize_markdown("❌ Error loading rainfall information. Please try again."),
            parse_mode='Markdown'
        )


async def alternatives_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle alternatives callback queries to show alternative crop recommendations.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    # Parse callback data: "alt:location_hash:season_filter:offset:limit"
    callback_data = query.data
    logger.info(f"Alternatives callback received: {callback_data} from user {user_id}")
    
    if not callback_data.startswith('alt:'):
        logger.error(f"Invalid alternatives callback data format: {callback_data}")
        await query.answer("Invalid callback data")
        return
    
    try:
        parts = callback_data.split(':', 4)
        if len(parts) < 3:
            logger.error(f"Invalid alternatives callback data parts: {parts}")
            await query.answer("Invalid callback data format")
            return
            
        _, location_hash, season_filter = parts[:3]
        
        # Parse pagination parameters if present
        offset = int(parts[3]) if len(parts) > 3 else 0
        limit = int(parts[4]) if len(parts) > 4 else 10  # Increased default limit from 5 to 10
        
        logger.info(f"Parsed alternatives callback data - location_hash: '{location_hash}', season: '{season_filter}', offset: {offset}, limit: {limit}")
        
        # Get original location from cache
        location = _location_cache.get(location_hash)
        if not location:
            logger.error(f"Location not found in cache for hash: {location_hash}")
            await query.answer("Location not found")
            return
        
        logger.info(f"Retrieved location from cache: '{location}'")
        
        logger.log_user_query(user_id, f"alternatives_callback:{location}:{season_filter}:{offset}:{limit}", "callback")
        
        # Answer the callback query
        await query.answer("Loading alternative crop recommendations...")
        
        # Parse coordinates from location
        coordinates = coordinate_handler.parse_coordinates(location, user_id)
        if not coordinates:
            logger.error(f"Could not parse coordinates from location: '{location}'")
            await query.edit_message_text(
                _sanitize_markdown("❌ Could not parse location coordinates. Please try the command again."),
                parse_mode='Markdown'
            )
            return
        
        lat, lon = coordinates
        logger.info(f"Parsed coordinates: {lat}, {lon}")
        
        # Get weather and rainfall data
        rainfall_data = weather_api.get_rainfall_data(lat, lon, user_id)
        weather_data = weather_api.get_current_weather(lat, lon, user_id)
        
        if not rainfall_data or not weather_data:
            logger.error(f"Could not fetch weather data for coordinates: {lat}, {lon}")
            await query.edit_message_text(
                _sanitize_markdown("❌ Unable to fetch weather data. Please try again later."),
                parse_mode='Markdown'
            )
            return
        
        # Generate alternative recommendations based on season filter
        if season_filter in ['rainy', 'rain', 'wet']:
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'rainy_season', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5,
                limit=limit,
                offset=offset,
                include_alternatives=True
            )
        elif season_filter == 'dry':
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'dry_season', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5,
                limit=limit,
                offset=offset,
                include_alternatives=True
            )
        elif season_filter == 'all':
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'current', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5,
                limit=limit,
                offset=offset,
                include_alternatives=True
            )
        else:  # current season
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, 'current', 
                rainfall_data.get('total_7day_rainfall', 0), 
                weather_data.get('temperature', 25),
                historical_years=5,
                limit=limit,
                offset=offset,
                include_alternatives=True
            )
        
        # Get seasonal advice
        seasonal_advice = seasonal_advisor.get_seasonal_recommendations(
            rainfall_data, weather_data
        )
        
        # Generate response with interactive buttons
        try:
            ai_enhanced_message = await response_synthesizer.synthesize_crop_recommendations(
                recommendations, weather_data, location, user_id, season_filter
            )
            
            # Add interactive buttons with pagination support
            keyboard = _create_seasonal_keyboard(location, season_filter, offset, limit)
            
            # Check if the message content would actually change
            current_text = query.message.text if query.message.text else ""
            normalized_current = re.sub(r'\s+', ' ', current_text.strip())
            normalized_new = re.sub(r'\s+', ' ', ai_enhanced_message.strip())
            
            if normalized_current == normalized_new:
                # Content is the same, just answer the callback without editing
                await query.answer("Already showing alternative recommendations")
                logger.log_bot_response(user_id, f"alternatives_callback_no_change_{season_filter}", True)
            else:
                # Content is different, update the message
                await query.edit_message_text(
                    ai_enhanced_message,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                logger.log_bot_response(user_id, f"alternatives_callback_success_{season_filter}", True)
            
        except Exception as ai_error:
            logger.error(f"AI enhancement failed in alternatives callback: {ai_error}", user_id)
            
            # Fallback to traditional response
            fallback_message = _format_sqlite_guide_response(
                recommendations, seasonal_advice, lat, lon, location, season_filter, offset, limit
            )
            
            # Add interactive buttons with pagination support
            keyboard = _create_seasonal_keyboard(location, season_filter, offset, limit)
            
            # Check if the message content would actually change
            current_text = query.message.text if query.message.text else ""
            normalized_current = re.sub(r'\s+', ' ', current_text.strip())
            normalized_new = re.sub(r'\s+', ' ', fallback_message.strip())
            
            if normalized_current == normalized_new:
                # Content is the same, just answer the callback without editing
                await query.answer("Already showing alternative recommendations")
                logger.log_bot_response(user_id, f"alternatives_callback_fallback_no_change_{season_filter}", True)
            else:
                # Content is different, update the message
                await query.edit_message_text(
                    fallback_message,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                logger.log_bot_response(user_id, f"alternatives_callback_fallback_{season_filter}", True)
        
    except Exception as e:
        logger.error(f"Error in alternatives callback: {e}", user_id)
        await query.edit_message_text(
            _sanitize_markdown("❌ Error processing alternatives request. Please try again."),
            parse_mode='Markdown'
        )


def _format_sqlite_guide_response(recommendations: dict, seasonal_advice: dict, 
                                 lat: float, lon: float, location_text: str, season_filter: str,
                                 offset: int = 0, limit: int = 5) -> str:
    """
    Format SQLite-based crop recommendations response from agriculture guides.
    
    Args:
        recommendations: SQLite-based recommendations data
        seasonal_advice: Seasonal advice data
        lat: Latitude
        lon: Longitude
        location_text: Location text
        season_filter: Season filter used
        offset: Pagination offset
        limit: Number of recommendations shown
        
    Returns:
        Formatted response message
    """
    try:
        # Extract data from SQLite recommendations
        crop_recommendations = recommendations.get('recommendations', [])
        planting_advice = recommendations.get('planting_advice', {})
        management_tips = recommendations.get('management_tips', [])
        risk_assessment = recommendations.get('risk_assessment', {})
        sources = recommendations.get('sources', [])
        historical_data = recommendations.get('historical_data', 0)
        location_data = recommendations.get('location', {})
        pagination = recommendations.get('pagination', {})
        
        # Build response message
        response_parts = []
        
        # Header
        season_display = season_filter.replace('_', ' ').title()
        response_parts.append(f"🌱 **{season_display} Crop Recommendations**")
        response_parts.append(f"📍 **Location**: {location_text} ({lat:.4f}, {lon:.4f})")
        response_parts.append(f"📚 **Based on**: {len(sources)} Agriculture Guides")
        response_parts.append(f"📊 **Historical Data**: {historical_data} years analyzed")
        
        # Show pagination info if not on first page or showing alternatives
        if offset > 0 or pagination.get('include_alternatives', False):
            if pagination.get('include_alternatives', False):
                response_parts.append(f"🔄 **Showing**: Alternative crops (page {offset//limit + 1})")
            else:
                response_parts.append(f"📄 **Showing**: Page {offset//limit + 1} of recommendations")
        
        # Environmental conditions
        response_parts.append("\n🌦️ **Environmental Conditions**")
        response_parts.append(f"• **Temperature**: {location_data.get('temperature', 'N/A')}°C")
        response_parts.append(f"• **Rainfall**: {location_data.get('rainfall_mm', 'N/A')}mm")
        response_parts.append(f"• **Season**: {location_data.get('season', 'N/A').replace('_', ' ').title()}")
        
        # Top crop recommendations from guides
        if crop_recommendations:
            response_parts.append("\n🥇 **Top Crop Recommendations from Agriculture Guides**")
            
            for i, crop in enumerate(crop_recommendations, offset + 1):
                crop_name = crop.get('crop_name', 'Unknown')
                suitability_score = crop.get('suitability_score', 0)
                rainfall_match = crop.get('rainfall_match', 'unknown')
                temperature_match = crop.get('temperature_match', 'unknown')
                season_suitability = crop.get('season_suitability', 'unknown')
                guide_sources = crop.get('sources', [])
                
                # Format score as percentage
                score_percent = suitability_score * 100
                
                # Add match indicators
                rainfall_emoji = "🟢" if rainfall_match == 'excellent' else "🟡" if rainfall_match == 'good' else "🔴"
                temp_emoji = "🟢" if temperature_match == 'excellent' else "🟡" if temperature_match == 'good' else "🔴"
                season_emoji = "🟢" if season_suitability == 'excellent' else "🟡" if season_suitability == 'good' else "🔴"
                
                response_parts.append(f"{i}. **{crop_name}** ({score_percent:.0f}%)")
                response_parts.append(f"   • Rainfall Match: {rainfall_emoji} {rainfall_match}")
                response_parts.append(f"   • Temperature Match: {temp_emoji} {temperature_match}")
                response_parts.append(f"   • Season Suitability: {season_emoji} {season_suitability}")
                
                # Add guide sources
                if guide_sources:
                    source_names = [source.split('.')[0] for source in guide_sources[:2]]
                    response_parts.append(f"   • **Sources**: {', '.join(source_names)}")
                
                # Add guide recommendations if available
                guide_recs = crop.get('guide_recommendations', [])
                if guide_recs:
                    response_parts.append(f"   • **Guide Advice**: {guide_recs[0][:80]}...")
                
                response_parts.append("")  # Empty line between crops
        
        # Planting advice from guides
        if planting_advice:
            response_parts.append("📅 **Planting Advice from Agriculture Guides**")
            
            if planting_advice.get('timing'):
                response_parts.append("**Timing:**")
                for advice in planting_advice['timing'][:2]:
                    response_parts.append(f"• {advice[:100]}...")
            
            if planting_advice.get('methods'):
                response_parts.append("**Methods:**")
                for method in planting_advice['methods'][:2]:
                    response_parts.append(f"• {method[:100]}...")
            
            if planting_advice.get('considerations'):
                response_parts.append("**Historical Considerations:**")
                for consideration in planting_advice['considerations']:
                    response_parts.append(f"• {consideration}")
        
        # Management tips from guides
        if management_tips:
            response_parts.append("\n💡 **Management Tips from Agriculture Guides**")
            for tip in management_tips[:5]:
                response_parts.append(f"• {tip[:100]}...")
        
        # Risk assessment from guides
        if risk_assessment:
            response_parts.append("\n⚠️ **Risk Assessment from Agriculture Guides**")
            overall_risk = risk_assessment.get('overall_risk_level', 'moderate')
            risk_emoji = "🔴" if overall_risk == 'high' else "🟡" if overall_risk == 'moderate' else "🟢"
            response_parts.append(f"**Overall Risk Level**: {risk_emoji} {overall_risk.title()}")
            
            weather_risks = risk_assessment.get('weather_risks', [])
            if weather_risks:
                response_parts.append(f"**Weather Risks** ({len(weather_risks)} identified):")
                for risk in weather_risks[:2]:
                    response_parts.append(f"• {risk[:100]}...")
            
            pest_risks = risk_assessment.get('pest_risks', [])
            if pest_risks:
                response_parts.append(f"**Pest Risks** ({len(pest_risks)} identified):")
                for risk in pest_risks[:2]:
                    response_parts.append(f"• {risk[:100]}...")
        
        # Footer
        response_parts.append("\n💡 **Tips**")
        response_parts.append("• Use the buttons below to explore different seasons")
        response_parts.append("• Recommendations based on official agriculture guides")
        response_parts.append("• Consider local conditions and historical patterns")
        
        # Join all parts
        full_response = "\n".join(response_parts)
        
        # Sanitize and return
        return _sanitize_markdown(full_response)
        
    except Exception as e:
        logger.error(f"Error formatting SQLite guide response: {e}")
        return _sanitize_markdown(
            "❌ Error formatting recommendations. Please try again or contact support."
        )


def _format_comprehensive_response(recommendations: dict, seasonal_advice: dict, 
                                 lat: float, lon: float, location_text: str, season_filter: str) -> str:
    """
    Format comprehensive crop recommendations response with historical data integration.
    
    Args:
        recommendations: Crop recommendations data
        seasonal_advice: Seasonal advice data
        lat: Latitude
        lon: Longitude
        location_text: Location text
        season_filter: Season filter used
        
    Returns:
        Formatted response message
    """
    try:
        # Handle different recommendation structures based on season filter
        if season_filter == 'all':
            # All seasons comparison has a different structure
            return _format_all_seasons_response(recommendations, seasonal_advice, lat, lon, location_text)
        
        # Extract data from recommendations
        top_crops = recommendations.get('recommendations', [])
        environmental_summary = recommendations.get('environmental_summary', {})
        historical_summary = recommendations.get('historical_summary', {})
        climate_analysis = recommendations.get('climate_analysis', {})
        
        # Build response message
        response_parts = []
        
        # Header
        season_display = season_filter.replace('_', ' ').title()
        response_parts.append(f"🌱 **{season_display} Crop Recommendations**")
        response_parts.append(f"📍 **Location**: {location_text} ({lat:.4f}, {lon:.4f})")
        
        # Historical data insights (if available)
        if historical_summary:
            response_parts.append("\n📊 **Historical Analysis**")
            response_parts.append(f"• **Years Analyzed**: {historical_summary.get('years_analyzed', 'N/A')}")
            response_parts.append(f"• **Climate Trend**: {historical_summary.get('climate_trend', 'N/A').title()}")
            response_parts.append(f"• **Rainfall Variability**: {historical_summary.get('rainfall_variability', 0):.1%}")
            
            # Add season-specific historical data
            if season_filter in ['rainy', 'rain', 'wet']:
                rainy_avg = historical_summary.get('rainy_season_historical_avg', 0)
                response_parts.append(f"• **Rainy Season Average**: {rainy_avg:.1f}mm")
            elif season_filter == 'dry':
                dry_avg = historical_summary.get('dry_season_historical_avg', 0)
                response_parts.append(f"• **Dry Season Average**: {dry_avg:.1f}mm")
            
            if historical_summary.get('drought_frequency', 0) > 0:
                response_parts.append(f"• **Drought Years**: {historical_summary.get('drought_frequency', 0)} out of {historical_summary.get('years_analyzed', 0)}")
            
            if historical_summary.get('flood_frequency', 0) > 0:
                response_parts.append(f"• **Flood Years**: {historical_summary.get('flood_frequency', 0)} out of {historical_summary.get('years_analyzed', 0)}")
        
        # Environmental conditions
        response_parts.append("\n🌦️ **Environmental Conditions**")
        
        if season_filter in ['rainy', 'rain', 'wet']:
            response_parts.append(f"• **Estimated Rainfall**: {environmental_summary.get('estimated_rainy_season_rainfall', 'N/A')}mm")
            response_parts.append(f"• **Temperature**: {environmental_summary.get('rainy_season_temperature', 'N/A')}°C")
            response_parts.append(f"• **Humidity**: {environmental_summary.get('rainy_season_humidity', 'N/A')}%")
            response_parts.append(f"• **Rainy Days**: {environmental_summary.get('rainy_days_per_month', 'N/A')} per month")
        elif season_filter == 'dry':
            response_parts.append(f"• **Estimated Rainfall**: {environmental_summary.get('estimated_dry_season_rainfall', 'N/A')}mm")
            response_parts.append(f"• **Temperature**: {environmental_summary.get('dry_season_temperature', 'N/A')}°C")
            response_parts.append(f"• **Humidity**: {environmental_summary.get('dry_season_humidity', 'N/A')}%")
            response_parts.append(f"• **Rainy Days**: {environmental_summary.get('rainy_days_per_month', 'N/A')} per month")
        else:  # current season
            response_parts.append(f"• **Temperature**: {environmental_summary.get('current_temperature', 'N/A')}°C")
            response_parts.append(f"• **Humidity**: {environmental_summary.get('humidity', 'N/A')}%")
            response_parts.append(f"• **7-Day Rainfall**: {environmental_summary.get('total_7day_rainfall', 'N/A')}mm")
            response_parts.append(f"• **Forecast Rainfall**: {environmental_summary.get('forecast_7day_rainfall', 'N/A')}mm")
            response_parts.append(f"• **Estimated Seasonal**: {environmental_summary.get('estimated_seasonal_rainfall', 'N/A')}mm")
        
        # Top crop recommendations
        if top_crops:
            response_parts.append("\n🥇 **Top Crop Recommendations**")
            
            for i, crop in enumerate(top_crops[:5], 1):
                crop_name = crop.get('crop_name', crop.get('crop_id', 'Unknown'))
                total_score = crop.get('total_score', 0)
                suitability = crop.get('suitability_level', 'Unknown')
                reliability_score = crop.get('reliability_score', 0)
                risk_score = crop.get('risk_score', 0)
                
                # Format score as percentage
                score_percent = min(100, max(0, total_score * 10))  # Scale 0-10 to 0-100
                
                # Add reliability and risk indicators
                reliability_emoji = "🟢" if reliability_score > 0.7 else "🟡" if reliability_score > 0.4 else "🔴"
                risk_emoji = "🟢" if risk_score < 0.3 else "🟡" if risk_score < 0.6 else "🔴"
                
                response_parts.append(f"{i}. **{crop_name}** ({score_percent:.0f}%)")
                response_parts.append(f"   • Suitability: {suitability}")
                response_parts.append(f"   • Reliability: {reliability_emoji} {reliability_score:.1%}")
                response_parts.append(f"   • Risk Level: {risk_emoji} {risk_score:.1%}")
                
                # Add top variety if available
                top_varieties = crop.get('top_varieties', [])
                if top_varieties:
                    best_variety = top_varieties[0]
                    variety_name = best_variety.get('name', 'Unknown')
                    variety_score = best_variety.get('score', 0)
                    response_parts.append(f"   • **Best Variety**: {variety_name} ({variety_score:.1f})")
                
                response_parts.append("")  # Empty line between crops
        
        # Climate trend recommendations
        if climate_analysis and climate_analysis.get('recommendations'):
            response_parts.append("📈 **Climate Trend Recommendations**")
            for rec in climate_analysis['recommendations'][:3]:  # Top 3 recommendations
                response_parts.append(f"• {rec}")
        
        # Seasonal advice
        if seasonal_advice and seasonal_advice.get('advice'):
            response_parts.append("\n🌾 **Seasonal Advice**")
            response_parts.append(seasonal_advice['advice'])
        
        # Historical insights (if available)
        if historical_summary and climate_analysis:
            response_parts.append("\n📚 **Historical Insights**")
            trend_desc = climate_analysis.get('trend_description', '')
            if trend_desc:
                response_parts.append(f"• {trend_desc}")
            
            if historical_summary.get('rainfall_variability', 0) > 0.7:
                response_parts.append("• High rainfall variability detected - consider flexible planting strategies")
            elif historical_summary.get('rainfall_variability', 0) < 0.3:
                response_parts.append("• Stable rainfall patterns - you can plan with more confidence")
        
        # Footer
        response_parts.append("\n💡 **Tips**")
        response_parts.append("• Use the buttons below to explore different seasons")
        response_parts.append("• Check weather and rainfall for detailed analysis")
        response_parts.append("• Consider historical patterns for long-term planning")
        
        # Join all parts
        full_response = "\n".join(response_parts)
        
        # Sanitize and return
        return _sanitize_markdown(full_response)
        
    except Exception as e:
        logger.error(f"Error formatting comprehensive response: {e}")
        return _sanitize_markdown(
            "❌ Error formatting recommendations. Please try again or contact support."
        )


def _format_all_seasons_response(recommendations: dict, seasonal_advice: dict, 
                                lat: float, lon: float, location_text: str) -> str:
    """
    Format all seasons comparison response.
    
    Args:
        recommendations: All seasons comparison data
        seasonal_advice: Seasonal advice data
        lat: Latitude
        lon: Longitude
        location_text: Location text
        
    Returns:
        Formatted all seasons response
    """
    try:
        response_parts = []
        
        # Header
        response_parts.append(f"🌱 **All Seasons Crop Comparison**")
        response_parts.append(f"📍 **Location**: {location_text} ({lat:.4f}, {lon:.4f})")
        
        # Historical summary
        historical_summary = recommendations.get('historical_summary', {})
        if historical_summary:
            response_parts.append("\n📊 **Historical Analysis**")
            response_parts.append(f"• **Years Analyzed**: {historical_summary.get('years_analyzed', 'N/A')}")
            response_parts.append(f"• **Climate Trend**: {historical_summary.get('climate_trend', 'N/A').title()}")
            response_parts.append(f"• **Rainfall Variability**: {historical_summary.get('rainfall_variability', 0):.1%}")
            response_parts.append(f"• **Rainy Season Average**: {historical_summary.get('rainy_season_historical_avg', 0):.1f}mm")
            response_parts.append(f"• **Dry Season Average**: {historical_summary.get('dry_season_historical_avg', 0):.1f}mm")
        
        # Year-round crops
        year_round_crops = recommendations.get('year_round_crops', [])
        if year_round_crops:
            response_parts.append("\n🔄 **Year-Round Crops**")
            response_parts.append("These crops perform well across both seasons:")
            
            for i, crop in enumerate(year_round_crops[:3], 1):
                crop_name = crop.get('crop_name', crop.get('crop_id', 'Unknown'))
                total_score = crop.get('total_score', 0)
                rainy_score = crop.get('rainy_season_score', 0)
                dry_score = crop.get('dry_season_score', 0)
                reliability_score = crop.get('reliability_score', 0)
                risk_score = crop.get('risk_score', 0)
                
                # Format scores as percentages
                score_percent = min(100, max(0, total_score * 10))
                rainy_percent = min(100, max(0, rainy_score * 10))
                dry_percent = min(100, max(0, dry_score * 10))
                
                # Add reliability and risk indicators
                reliability_emoji = "🟢" if reliability_score > 0.7 else "🟡" if reliability_score > 0.4 else "🔴"
                risk_emoji = "🟢" if risk_score < 0.3 else "🟡" if risk_score < 0.6 else "🔴"
                
                response_parts.append(f"{i}. **{crop_name}** ({score_percent:.0f}%)")
                response_parts.append(f"   • Rainy Season: {rainy_percent:.0f}% | Dry Season: {dry_percent:.0f}%")
                response_parts.append(f"   • Reliability: {reliability_emoji} {reliability_score:.1%}")
                response_parts.append(f"   • Risk Level: {risk_emoji} {risk_score:.1%}")
                response_parts.append("")
        
        # Seasonal advice
        if seasonal_advice and seasonal_advice.get('advice'):
            response_parts.append("🌾 **Comprehensive Seasonal Advice**")
            response_parts.append(seasonal_advice['advice'])
        
        # Climate analysis
        climate_analysis = recommendations.get('climate_analysis', {})
        if climate_analysis and climate_analysis.get('recommendations'):
            response_parts.append("\n📈 **Climate Trend Recommendations**")
            for rec in climate_analysis['recommendations'][:3]:
                response_parts.append(f"• {rec}")
        
        # Footer
        response_parts.append("\n💡 **Tips**")
        response_parts.append("• Use the buttons below to explore specific seasons")
        response_parts.append("• Year-round crops provide consistent income")
        response_parts.append("• Consider crop rotation between seasons")
        
        # Join all parts
        full_response = "\n".join(response_parts)
        
        # Sanitize and return
        return _sanitize_markdown(full_response)
        
    except Exception as e:
        logger.error(f"Error formatting all seasons response: {e}")
        return _sanitize_markdown(
            "❌ Error formatting all seasons comparison. Please try again."
        )


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
            advanced_recommendations, seasonal_advice, lat, lon, "Requested Location", "current"
        )
    except Exception as e:
        logger.error(f"Error in legacy formatting function: {e}")
        return "❌ Error formatting crop recommendations. Please try again." 


def _create_seasonal_keyboard(location: str, current_season: str, offset: int = 0, limit: int = 10) -> InlineKeyboardMarkup:
    """
    Create inline keyboard for seasonal navigation.
    
    Args:
        location: Location string
        current_season: Current season filter
        offset: Pagination offset
        limit: Number of recommendations to show (default: 10)
        
    Returns:
        InlineKeyboardMarkup with seasonal navigation buttons
    """
    keyboard = []
    
    # Create a simple hash of the location for callback data
    location_hash = hashlib.md5(location.encode()).hexdigest()[:8]
    
    # Store the original location in the cache
    _location_cache[location_hash] = location
    
    # Season buttons row
    season_buttons = []
    
    # Current season button
    current_text = "🌤️ Current" if current_season == 'current' else "Current"
    current_callback = f"s:{location_hash}:current:{offset}:{limit}"
    logger.info(f"Creating Current button with callback: {current_callback}")
    season_buttons.append(InlineKeyboardButton(
        current_text, 
        callback_data=current_callback
    ))
    
    # Rainy season button
    rainy_text = "🌧️ Rainy" if current_season in ['rainy', 'rain', 'wet'] else "Rainy"
    rainy_callback = f"s:{location_hash}:rainy:{offset}:{limit}"
    logger.info(f"Creating Rainy button with callback: {rainy_callback}")
    season_buttons.append(InlineKeyboardButton(
        rainy_text, 
        callback_data=rainy_callback
    ))
    
    # Dry season button
    dry_text = "☀️ Dry" if current_season == 'dry' else "Dry"
    dry_callback = f"s:{location_hash}:dry:{offset}:{limit}"
    logger.info(f"Creating Dry button with callback: {dry_callback}")
    season_buttons.append(InlineKeyboardButton(
        dry_text, 
        callback_data=dry_callback
    ))
    
    # All seasons button
    all_text = "📊 All" if current_season == 'all' else "All"
    all_callback = f"s:{location_hash}:all:{offset}:{limit}"
    logger.info(f"Creating All button with callback: {all_callback}")
    season_buttons.append(InlineKeyboardButton(
        all_text, 
        callback_data=all_callback
    ))
    
    keyboard.append(season_buttons)
    
    # Action buttons row
    action_buttons = []
    
    # Weather button
    weather_callback = f"w:{location_hash}"
    logger.info(f"Creating Weather button with callback: {weather_callback}")
    action_buttons.append(InlineKeyboardButton(
        "🌦️ Weather", 
        callback_data=weather_callback
    ))
    
    # Rainfall button
    rainfall_callback = f"r:{location_hash}"
    logger.info(f"Creating Rainfall button with callback: {rainfall_callback}")
    action_buttons.append(InlineKeyboardButton(
        "🌧️ Rainfall", 
        callback_data=rainfall_callback
    ))
    
    # Help button
    help_callback = "help"
    logger.info(f"Creating Help button with callback: {help_callback}")
    action_buttons.append(InlineKeyboardButton(
        "❓ Help", 
        callback_data=help_callback
    ))
    
    keyboard.append(action_buttons)
    
    # Pagination and alternatives row
    pagination_buttons = []
    
    # Show More button (if there are more recommendations)
    if offset + limit < 50:  # Increased max from 20 to 50 recommendations
        show_more_callback = f"s:{location_hash}:{current_season}:{offset + limit}:{limit}"
        logger.info(f"Creating Show More button with callback: {show_more_callback}")
        pagination_buttons.append(InlineKeyboardButton(
            "📄 Show More", 
            callback_data=show_more_callback
        ))
    
    # Show Alternatives button
    alternatives_callback = f"alt:{location_hash}:{current_season}:0:10" # Increased default limit to 10
    logger.info(f"Creating Show Alternatives button with callback: {alternatives_callback}")
    pagination_buttons.append(InlineKeyboardButton(
        "🔄 Alternatives", 
        callback_data=alternatives_callback
    ))
    
    # Reset to first page button (if not on first page)
    if offset > 0:
        reset_callback = f"s:{location_hash}:{current_season}:0:{limit}"
        logger.info(f"Creating Reset button with callback: {reset_callback}")
        pagination_buttons.append(InlineKeyboardButton(
            "🏠 First Page", 
            callback_data=reset_callback
        ))
    
    if pagination_buttons:
        keyboard.append(pagination_buttons)
    
    logger.info(f"Created keyboard with {len(keyboard)} rows for location: {location} (hash: {location_hash})")
    return InlineKeyboardMarkup(keyboard) 