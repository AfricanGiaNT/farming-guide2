"""
Main entry point for the Agricultural Advisor Bot.
Initializes the bot and registers all command handlers.
"""
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Import configuration and utilities
from scripts.utils.config_loader import config
from scripts.utils.logger import logger

# Import handlers
from scripts.handlers.start_handler import start_command, help_command, about_command
from scripts.handlers.weather_handler import weather_command, rain_command
from scripts.handlers.crop_handler import crops_command, seasonal_callback, weather_callback, rainfall_callback, alternatives_callback
from scripts.handlers.historical_rain_handler import historical_rain_handler
from scripts.handlers.varieties_handler import varieties_command


async def error_handler(update, context):
    """Handle errors in bot operations."""
    logger.error(f"Update {update} caused error {context.error}")


async def unknown_command(update, context):
    """Handle unknown commands."""
    user_id = str(update.effective_user.id)
    command = update.message.text
    
    logger.log_user_query(user_id, command, "unknown_command")
    
    await update.message.reply_text(
        "❓ Unknown command. Use `/help` to see available commands.\n\n"
        "**Available commands:**\n"
        "• `/start` - Welcome message\n"
        "• `/help` - Show help\n"
        "• `/weather [location]` - Get weather info\n"
        "• `/rain [location]` - Analyze rainfall\n"
        "• `/crops [location]` - Get crop recommendations\n"
        "• `/varieties [crop]` - Get variety information\n"
        "• `/rain_history [location] [years]` - Historical rainfall analysis\n"
        "• `/rain_compare [location] [rainfall] [years]` - Compare with historical data\n"
        "• `/drought_risk [location] [years]` - Assess drought risk\n"
        "• `/about` - About this bot",
        parse_mode='Markdown'
    )


async def text_message_handler(update, context):
    """Handle regular text messages."""
    user_id = str(update.effective_user.id)
    message_text = update.message.text
    
    logger.log_user_query(user_id, message_text, "text_message")
    
    # Simple response for text messages
    await update.message.reply_text(
        "👋 Hello! I'm an agricultural advisor bot.\n\n"
        "I can help you with:\n"
        "• Weather information (`/weather [location]`)\n"
        "• Rainfall analysis (`/rain [location]`)\n"
        "• Crop recommendations (`/crops [location]`)\n"
        "• Variety information (`/varieties [crop]`)\n"
        "• Historical rainfall analysis (`/rain_history [location] [years]`)\n"
        "• Rainfall comparison (`/rain_compare [location] [rainfall] [years]`)\n"
        "• Drought risk assessment (`/drought_risk [location] [years]`)\n\n"
        "Try sending a command like `/weather Lilongwe` or `/varieties groundnut` or use `/help` for more options!"
    )


def main():
    """Main function to start the bot."""
    # Create environment templates if they don't exist
    config.create_template_env_files()
    
    # Get bot token
    try:
        bot_token = config.get_required("TELEGRAM_BOT_TOKEN")
    except ValueError as e:
        logger.error(f"Bot token not found: {e}")
        logger.error("Please add your Telegram bot token to config/telegram_token.env")
        return
    
    # Verify weather API key
    try:
        weather_key = config.get_required("OPENWEATHERMAP_API_KEY")
        logger.info("Weather API key loaded successfully")
    except ValueError as e:
        logger.error(f"Weather API key not found: {e}")
        logger.error("Please add your OpenWeatherMap API key to config/weather_api.env")
        return
    
    logger.info("Starting Agricultural Advisor Bot...")
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("rain", rain_command))
    application.add_handler(CommandHandler("crops", crops_command))
    application.add_handler(CommandHandler("varieties", varieties_command))
    
    # Register callback query handlers
    from telegram.ext import CallbackQueryHandler
    
    # Add comprehensive callback handler for debugging
    async def comprehensive_callback(update, context):
        """Handle any callback queries with comprehensive logging."""
        query = update.callback_query
        user_id = str(query.from_user.id)
        callback_data = query.data
        
        # Log everything about the callback
        print(f"🔔 CALLBACK RECEIVED: {callback_data} from user {user_id}")
        logger.info(f"🔔 CALLBACK RECEIVED: {callback_data} from user {user_id}")
        
        # Log the full update object for debugging
        logger.info(f"Full update object: {update}")
        logger.info(f"Callback query object: {query}")
        
        try:
            # Try to handle specific callbacks
            if callback_data.startswith('s:'):
                logger.info("Routing to seasonal_callback")
                await seasonal_callback(update, context)
            elif callback_data.startswith('w:'):
                logger.info("Routing to weather_callback")
                await weather_callback(update, context)
            elif callback_data.startswith('r:'):
                logger.info("Routing to rainfall_callback")
                await rainfall_callback(update, context)
            elif callback_data.startswith('alt:'):
                logger.info("Routing to alternatives_callback")
                await alternatives_callback(update, context)
            elif callback_data == 'help':
                logger.info("Handling help callback")
                await query.answer("Help information")
                await query.edit_message_text("❓ **Help**\n\nUse the buttons to navigate between different seasons and get weather information.")
            else:
                logger.info(f"Unhandled callback: {callback_data}")
                await query.answer(f"Unhandled callback: {callback_data}")
                
        except Exception as e:
            logger.error(f"Error in callback handler: {e}")
            await query.answer(f"Error: {str(e)}")
    
    # Register the comprehensive callback handler
    application.add_handler(CallbackQueryHandler(comprehensive_callback))
    
    # Register historical rainfall commands
    application.add_handler(CommandHandler("rain_history", historical_rain_handler.handle_rain_history))
    application.add_handler(CommandHandler("rain_compare", historical_rain_handler.handle_rain_compare))
    application.add_handler(CommandHandler("drought_risk", historical_rain_handler.handle_drought_risk))
    
    # Register message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    logger.info("Bot handlers registered successfully")
    
    # Start the bot
    try:
        logger.info("Bot starting up...")
        # Configure polling with proper allowed updates
        application.run_polling(
            poll_interval=1.0,
            allowed_updates=['message', 'callback_query', 'edited_message'],
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    main() 