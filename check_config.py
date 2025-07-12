#!/usr/bin/env python3
"""
Configuration Checker for Agricultural Advisor Bot
Validates all API keys and configurations before running the bot.
"""

import os
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from scripts.utils.config_loader import config
    from scripts.utils.logger import logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this script from the project root directory")
    sys.exit(1)


def check_configuration():
    """Check all configuration files and API keys."""
    print("🔧 Agricultural Advisor Bot - Configuration Checker")
    print("=" * 60)
    
    config_status = {
        "telegram_bot_token": False,
        "openweathermap_api_key": False,
        "openai_api_key": False,
        "database_configured": False,
        "directories_created": False
    }
    
    # Check Telegram Bot Token
    try:
        telegram_token = config.get_required("TELEGRAM_BOT_TOKEN")
        if telegram_token and len(telegram_token) > 20:
            print("✅ Telegram Bot Token: Valid")
            config_status["telegram_bot_token"] = True
        else:
            print("❌ Telegram Bot Token: Invalid or too short")
    except Exception as e:
        print(f"❌ Telegram Bot Token: Not found ({e})")
        print("   💡 Add your token to config/telegram_token.env")
    
    # Check OpenWeatherMap API Key
    try:
        weather_key = config.get_required("OPENWEATHERMAP_API_KEY")
        if weather_key and len(weather_key) > 20:
            print("✅ OpenWeatherMap API Key: Valid")
            config_status["openweathermap_api_key"] = True
        else:
            print("❌ OpenWeatherMap API Key: Invalid or too short")
    except Exception as e:
        print(f"❌ OpenWeatherMap API Key: Not found ({e})")
        print("   💡 Add your key to config/weather_api.env")
    
    # Check OpenAI API Key
    try:
        openai_key = config.get_required("OPENAI_API_KEY")
        if openai_key and len(openai_key) > 20:
            print("✅ OpenAI API Key: Valid")
            config_status["openai_api_key"] = True
        else:
            print("❌ OpenAI API Key: Invalid or too short")
    except Exception as e:
        print(f"❌ OpenAI API Key: Not found ({e})")
        print("   💡 Add your key to config/openai_key.env")
    
    # Check Database Configuration
    try:
        db_url = config.get_required("DATABASE_URL")
        if db_url:
            print("✅ Database URL: Configured")
            config_status["database_configured"] = True
        else:
            print("❌ Database URL: Not configured")
    except Exception as e:
        print(f"⚠️  Database URL: Using default ({e})")
        print("   💡 Add DATABASE_URL to config/database.env if using external DB")
        config_status["database_configured"] = True  # Default is acceptable
    
    # Check Directories
    required_dirs = [
        "data/pdfs",
        "data/vector_db",
        "logs",
        "config"
    ]
    
    all_dirs_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory {dir_path}: Exists")
        else:
            print(f"❌ Directory {dir_path}: Missing")
            all_dirs_exist = False
    
    if all_dirs_exist:
        config_status["directories_created"] = True
    
    # Overall Status
    print("\n📊 Configuration Summary:")
    print("-" * 30)
    
    ready_count = sum(config_status.values())
    total_count = len(config_status)
    
    if ready_count == total_count:
        print("🎉 All configurations are ready!")
        print("✅ Bot is ready to run")
        return True
    else:
        print(f"⚠️  {ready_count}/{total_count} configurations are ready")
        print("❌ Bot needs additional configuration")
        
        # Show what's missing
        missing_configs = [k for k, v in config_status.items() if not v]
        print(f"\n🔧 Missing configurations: {', '.join(missing_configs)}")
        
        return False


def create_sample_env_files():
    """Create sample environment files if they don't exist."""
    print("\n🔧 Creating sample environment files...")
    
    env_files = {
        "config/telegram_token.env": "TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here",
        "config/openai_key.env": "OPENAI_API_KEY=your_openai_api_key_here",
        "config/weather_api.env": "OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here",
        "config/database.env": "DATABASE_URL=sqlite:///data/agricultural_bot.db",
        "config/google_keys.env": "GOOGLE_SEARCH_API_KEY=your_google_api_key_here\nGOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here"
    }
    
    for file_path, content in env_files.items():
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Created: {file_path}")
        else:
            print(f"⚠️  Already exists: {file_path}")


def create_directories():
    """Create all required directories."""
    print("\n📁 Creating required directories...")
    
    directories = [
        "data/pdfs",
        "data/vector_db",
        "logs",
        "config",
        "content/dev_journal"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")


def main():
    """Main function to check configuration."""
    # Create directories first
    create_directories()
    
    # Create sample env files
    create_sample_env_files()
    
    # Check configuration
    is_ready = check_configuration()
    
    if is_ready:
        print("\n🚀 Ready to run the bot!")
        print("Next steps:")
        print("1. Add your PDFs to data/pdfs/")
        print("2. Run: python setup_knowledge_base.py")
        print("3. Start the bot: python main.py")
    else:
        print("\n🔧 Configuration needed:")
        print("1. Edit the config/*.env files with your API keys")
        print("2. Run this script again to verify")
        print("3. Then proceed with PDF setup and bot launch")


if __name__ == "__main__":
    main() 