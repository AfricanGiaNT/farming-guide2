#!/usr/bin/env python3
"""
Check and clear webhook if needed.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/telegram_token.env')

async def fix_allowed_updates():
    """Fix the allowed_updates configuration to include callbacks."""
    try:
        from telegram import Bot
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("❌ No bot token found!")
            return
        
        print(f"🔧 Fixing allowed_updates configuration...")
        
        # Create bot instance
        bot = Bot(token=bot_token)
        
        # Set webhook with proper allowed_updates (even if URL is empty)
        success = await bot.set_webhook(
            url="",  # Empty URL for polling mode
            allowed_updates=['message', 'callback_query', 'edited_message']
        )
        
        if success:
            print("✅ Successfully configured allowed_updates!")
            print("📝 Allowed updates now include: message, callback_query, edited_message")
        else:
            print("❌ Failed to configure allowed_updates")
            
        # Verify the configuration
        webhook_info = await bot.get_webhook_info()
        print(f"✅ New allowed updates: {webhook_info.allowed_updates}")
        
        await bot.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def check_webhook():
    """Check if webhook is set and clear it if needed."""
    try:
        from telegram import Bot
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("❌ No bot token found!")
            return
        
        print(f"🔍 Checking webhook status...")
        
        # Create bot instance
        bot = Bot(token=bot_token)
        
        # Get webhook info
        webhook_info = await bot.get_webhook_info()
        
        print(f"📊 Webhook Info:")
        print(f"   URL: {webhook_info.url}")
        print(f"   Has custom certificate: {webhook_info.has_custom_certificate}")
        print(f"   Pending update count: {webhook_info.pending_update_count}")
        print(f"   Last error date: {webhook_info.last_error_date}")
        print(f"   Last error message: {webhook_info.last_error_message}")
        print(f"   Max connections: {webhook_info.max_connections}")
        print(f"   Allowed updates: {webhook_info.allowed_updates}")
        
        if webhook_info.url:
            print(f"⚠️  Webhook is set to: {webhook_info.url}")
            print(f"🔄 Clearing webhook...")
            
            # Delete webhook
            success = await bot.delete_webhook()
            if success:
                print("✅ Webhook cleared successfully!")
            else:
                print("❌ Failed to clear webhook")
        else:
            print("✅ No webhook is set - using polling mode")
        
        # Check if allowed_updates includes callback_query
        if webhook_info.allowed_updates and 'callback_query' not in webhook_info.allowed_updates:
            print("⚠️  callback_query not in allowed_updates!")
            print("🔧 This is likely why callbacks aren't working")
            await fix_allowed_updates()
        
        print("🔄 Getting updates to clear pending ones...")
        
        # Get pending updates
        updates = await bot.get_updates(limit=100, timeout=1)
        print(f"📨 Found {len(updates)} pending updates")
        
        if updates:
            # Clear pending updates by getting them with offset
            last_update_id = updates[-1].update_id
            await bot.get_updates(offset=last_update_id + 1, limit=1, timeout=1)
            print("🗑️ Cleared pending updates")
        
        await bot.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_webhook()) 