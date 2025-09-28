# Agricultural Advisor Bot

A smart, region-specific Telegram bot that provides agricultural advice for Lilongwe, Malawi. The bot analyzes weather patterns and rainfall data to recommend suitable crops and varieties.

## Features

🌧️ **Weather & Rainfall Analysis**
- Current weather conditions
- 7-day rainfall forecasts
- Agricultural weather insights

🌱 **Crop Recommendations**
- Location-based crop suggestions
- Rainfall-optimized varieties
- Seasonal planting advice
- AI-enhanced summaries and insights
- Intelligent data processing and validation

🌿 **Variety Information**
- Specific variety names and types
- Planting times and seasons
- Expected yields per hectare
- Weather and soil requirements
- Growing areas and districts

📍 **Location Support**
- Coordinate-based analysis
- Named Lilongwe locations
- Flexible input formats

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- OpenWeatherMap API Key (from [OpenWeatherMap](https://openweathermap.org/api))

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd farming-guide2

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

The bot will automatically create template configuration files in the `config/` directory:

**Edit `config/telegram_token.env`:**
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

**Edit `config/weather_api.env`:**
```
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
```

### 4. Run the Bot

```bash
python main.py
```

## Usage Examples

### Weather Commands

```
/weather Lilongwe
/weather -13.9833, 33.7833
/weather Area 1
```

### Rainfall Analysis

```
/rain Lilongwe
/rain -13.98, 33.78
/rain Kawale
```

### Crop Recommendations

```
/crops Lilongwe
/crops -13.9833, 33.7833
/crops Area 1
```

### Variety Information

```
/varieties groundnut
/varieties maize
/varieties common bean
/varieties soybean
```

## Supported Locations

### Coordinate Formats
- Decimal degrees: `-13.9833, 33.7833`
- With direction: `13.9833S, 33.7833E`
- Labeled: `lat: -13.9833, lon: 33.7833`

### Named Locations
- Lilongwe, Lilongwe City, Lilongwe Central
- Area 1, Area 2, Area 3
- Kawale, Mgona, Kanengo

## Project Structure

```
farming-guide2/
├── main.py                 # Main bot entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── scripts/               # Core bot logic
│   ├── handlers/          # Command handlers
│   ├── weather_engine/    # Weather API integration
│   ├── crop_advisor/      # Crop recommendation system
│   ├── ai_agent/          # AI integration (future)
│   └── utils/             # Shared utilities
├── config/                # Configuration files
├── data/                  # Local data storage
├── logs/                  # Bot logs
└── docs/                  # Documentation
```

## Development

### Week 1 MVP Features ✅
- Basic Telegram bot with commands
- Weather API integration
- Rainfall analysis
- Simple crop recommendations
- Coordinate parsing
- Logging system

### Upcoming Features (Week 2-3)
- AI-powered response generation
- PDF knowledge base integration
- Enhanced crop variety database
- Historical weather analysis

## API Keys Setup

### Telegram Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Use `/newbot` command
3. Follow instructions to create your bot
4. Copy the token to `config/telegram_token.env`

### OpenWeatherMap API Key
1. Register at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Add it to `config/weather_api.env`

## Contributing

This is a personal agricultural advisor bot project. The code is structured for easy extension and modification.

## License

Private project for agricultural advisory purposes.

## Support

For issues or questions, check the logs in the `logs/` directory or review the error messages in the console.

---

**Built with ❤️ for Malawi's farming community 🇲🇼** 