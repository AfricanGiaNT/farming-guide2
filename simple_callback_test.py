#!/usr/bin/env python3
"""
Simple callback test to verify the fix works.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/telegram_token.env')

async def test_fix():
    """Test if callbacks work after the fix."""
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("❌ No bot token found!")
            return
        
        print("🎯 Testing callback fix...")
        
        # Create application
        application = Application.builder().token(bot_token).build()
        
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Start command with test button."""
            keyboard = [[InlineKeyboardButton("✅ Test Fix", callback_data="test_fix")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🔧 **Callback Fix Test**\n\nClick the button to test if callbacks work now!",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            print("📤 Sent test message with button")
        
        async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Handle callback to verify fix."""
            query = update.callback_query
            print(f"🎉 CALLBACK SUCCESS! Data: {query.data}")
            
            await query.answer("✅ Fix confirmed!")
            await query.edit_message_text(
                "🎉 **SUCCESS!**\n\nCallbacks are now working! The issue has been resolved.",
                parse_mode='Markdown'
            )
        
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(callback))
        
        print("📱 Send /start to test the fix")
        
        # Start with proper configuration
        application.run_polling(
            allowed_updates=['message', 'callback_query', 'edited_message'],
            drop_pending_updates=True,
            poll_interval=1.0
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fix()) 