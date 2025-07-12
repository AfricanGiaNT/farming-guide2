"""
Start handler for the Agricultural Advisor Bot.
Handles the /start command and provides welcome message.
"""
from telegram import Update
from telegram.ext import ContextTypes
from scripts.utils.logger import logger


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    username = update.effective_user.first_name or "Farmer"
    
    logger.log_user_query(user_id, "/start", "command")
    
    welcome_message = f"""
🌾 **Welcome to the Agricultural Advisor Bot, {username}!**

I'm your personal farming assistant, specialized in Lilongwe's climate and agricultural conditions. I can help you with:

🌧️ **Weather & Rainfall Analysis**
• Current weather conditions
• Rainfall patterns and forecasts
• Agricultural weather insights

🌱 **Crop Recommendations**
• Best crops for current conditions
• Variety-specific advice
• Planting timing recommendations

📍 **Location-Based Advice**
• Tailored for Lilongwe area
• Coordinate-based analysis
• Local farming practices

**Quick Start Commands:**
• `/weather [location]` - Get weather info
• `/rain [location]` - Analyze rainfall patterns
• `/crops [location]` - Get crop recommendations
• `/help` - Show detailed help

**Example Usage:**
• `/weather Lilongwe`
• `/rain -13.9833, 33.7833`
• `/crops Area 1`

Ready to help you make better farming decisions! 🚜
"""
    
    try:
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.log_bot_response(user_id, "start_welcome", True)
    except Exception as e:
        logger.error(f"Error sending start message: {e}", user_id)
        await update.message.reply_text("Welcome to the Agricultural Advisor Bot! Use /help for more information.")
        logger.log_bot_response(user_id, "start_welcome", False)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    
    logger.log_user_query(user_id, "/help", "command")
    
    help_message = """
🌾 **Agricultural Advisor Bot - Help Guide**

**Main Commands:**

🌦️ **Weather Commands:**
• `/weather [location]` - Current weather conditions
• `/rain [location]` - Detailed rainfall analysis
• `/forecast [location]` - 7-day weather forecast

🌱 **Crop Commands:**
• `/crops [location]` - Crop recommendations based on conditions
• `/varieties [crop_name]` - Specific variety recommendations
• `/planting [location]` - Optimal planting timing

📍 **Location Formats:**
• Coordinates: `-13.9833, 33.7833`
• Named locations: `Lilongwe`, `Area 1`, `Kawale`
• Directional: `13.9833S, 33.7833E`

**Examples:**
• `/weather Lilongwe` - Weather for Lilongwe
• `/rain -13.98, 33.78` - Rainfall analysis for coordinates
• `/crops Area 1` - Crop recommendations for Area 1

**Other Commands:**
• `/start` - Welcome message
• `/help` - This help message
• `/about` - About the bot

**Tips:**
• Use specific coordinates for best results
• Check weather before planting decisions
• Consider seasonal timing for crops

Need more help? Just ask a question about farming in Lilongwe! 🚜
"""
    
    try:
        await update.message.reply_text(help_message, parse_mode='Markdown')
        logger.log_bot_response(user_id, "help_message", True)
    except Exception as e:
        logger.error(f"Error sending help message: {e}", user_id)
        await update.message.reply_text("Help information is temporarily unavailable. Please try again later.")
        logger.log_bot_response(user_id, "help_message", False)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /about command.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    
    logger.log_user_query(user_id, "/about", "command")
    
    about_message = """
🌾 **Agricultural Advisor Bot**

**Mission:** 
Provide intelligent, location-specific agricultural advice for farmers in Lilongwe, Malawi.

**Key Features:**
• Real-time weather data integration
• Rainfall pattern analysis
• Crop recommendation system
• Variety-specific advice
• Seasonal timing guidance

**Data Sources:**
• OpenWeatherMap API for weather data
• Local agricultural knowledge base
• Lilongwe-specific farming practices
• AI-powered analysis and recommendations

**Focus Area:**
Optimized for Lilongwe's climate conditions and common crops including maize, beans, groundnuts, and vegetables.

**Version:** 1.0.0 (Week 1 MVP)
**Developer:** Agricultural Advisory System
**Contact:** For feedback and suggestions

Built with ❤️ for Malawi's farming community 🇲🇼
"""
    
    try:
        await update.message.reply_text(about_message, parse_mode='Markdown')
        logger.log_bot_response(user_id, "about_message", True)
    except Exception as e:
        logger.error(f"Error sending about message: {e}", user_id)
        await update.message.reply_text("About information is temporarily unavailable. Please try again later.")
        logger.log_bot_response(user_id, "about_message", False) 