# Configuration Setup

This directory contains configuration files for the Agricultural Advisor Bot. 

## Setup Instructions

1. **Copy template files to create your configuration:**
   ```bash
   cp config/openai_key.env.example config/openai_key.env
   cp config/telegram_token.env.example config/telegram_token.env
   cp config/weather_api.env.example config/weather_api.env
   cp config/google_keys.env.example config/google_keys.env
   cp config/database.env.example config/database.env
   ```

2. **Edit each file with your actual API keys:**
   - `openai_key.env`: Add your OpenAI API key
   - `telegram_token.env`: Add your Telegram bot token
   - `weather_api.env`: Add your weather API key
   - `google_keys.env`: Add your Google API key
   - `database.env`: Configure your database connection

## Security Note

⚠️ **Never commit the actual `.env` files to version control!**

The `.env` files contain sensitive information and are excluded from git via `.gitignore`. 
Only the `.env.example` template files should be committed.

## Required APIs

- **OpenAI API**: For AI-powered agricultural recommendations
- **Telegram Bot**: For user interactions
- **Weather API**: For weather data integration
- **Google API**: For additional data sources

## Environment Variables

Each configuration file follows the format:
```
VARIABLE_NAME=your_value_here
```

Make sure to replace `your_value_here` with your actual API keys and configuration values. 