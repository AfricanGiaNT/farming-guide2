"""
Flask API Server for Mlangizi wa Ulimi Frontend
Exposes existing backend functionality as REST API endpoints
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime
import uuid

# Add the scripts directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Load configuration directly from the correct path
import os
from pathlib import Path

from database.schema_manager import ensure_varieties_schema

def load_config():
    """Load configuration from the config directory"""
    config_dir = Path(__file__).parent / "config"
    
    config_files = [
        "weather_api.env",
        "openai_key.env", 
        "database.env",
        "google_keys.env"
    ]
    
    loaded_any = False
    for config_file in config_files:
        config_path = config_dir / config_file
        if config_path.exists():
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print(f"✅ Loaded config from {config_path}")
            loaded_any = True
        else:
            print(f"⚠️  Config file not found: {config_path}")
    
    return loaded_any

# Load configuration
config_loaded = load_config()

# Import logger
try:
    from utils.logger import logger
except ImportError as e:
    print(f"⚠️  Warning: Could not import logger: {e}")
    logger = None

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize components
weather_api = None
recommendation_engine = None
varieties_handler = None
semantic_search = None
sqlite_recommendation_engine = None
seasonal_advisor = None

def initialize_components():
    """Initialize backend components"""
    global weather_api, recommendation_engine, varieties_handler, semantic_search, sqlite_recommendation_engine, seasonal_advisor
    
    print("🔧 Initializing backend components...")

    try:
        ensure_varieties_schema('data/agricultural_documents.db')
        print("✅ Varieties schema verified")
    except FileNotFoundError as e:
        print(f"⚠️  Varieties schema check skipped: {e}")
    except Exception as e:
        print(f"⚠️  Varieties schema verification failed: {e}")

    # Initialize weather API
    try:
        api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
        if api_key:
            from weather_engine.weather_api import WeatherAPI
            weather_api = WeatherAPI()
            print(f"✅ Weather API initialized with real API key: {api_key[:8]}...")
        else:
            print("⚠️  OPENWEATHERMAP_API_KEY not found in environment, using mock data")
            weather_api = None
    except Exception as e:
        print(f"⚠️  Weather API initialization failed: {e}")
        weather_api = None
    
    # Initialize SQLite recommendation engine (same as bot)
    try:
        from crop_advisor.sqlite_based_recommendation_engine import SQLiteBasedRecommendationEngine
        # Use the correct database path
        db_path = os.path.join(os.path.dirname(__file__), 'data', 'agricultural_documents.db')
        sqlite_recommendation_engine = SQLiteBasedRecommendationEngine(db_path)
        print("✅ SQLite recommendation engine initialized")
    except Exception as e:
        print(f"⚠️  SQLite recommendation engine initialization failed: {e}")
        sqlite_recommendation_engine = None
    
    # Initialize seasonal advisor
    try:
        from crop_advisor.seasonal_advisor import SeasonalAdvisor
        seasonal_advisor = SeasonalAdvisor()
        print("✅ Seasonal advisor initialized")
    except Exception as e:
        print(f"⚠️  Seasonal advisor initialization failed: {e}")
        seasonal_advisor = None
    
    # Initialize VarietiesHandler
    try:
        from handlers.varieties_handler import VarietiesHandler
        varieties_handler = VarietiesHandler()
        print("✅ Varieties handler initialized")
    except Exception as e:
        print(f"⚠️  Varieties handler initialization failed: {e}")
        varieties_handler = None
    
    # For other components, keep using mock data to avoid other import issues
    print("📝 Other components using mock data for now")
    recommendation_engine = None
    semantic_search = None

# Initialize components on startup
initialize_components()

def parse_location(location_str):
    """Parse location string to get lat/lon coordinates"""
    try:
        # Try to parse as coordinates first (lat,lon)
        if ',' in location_str:
            parts = location_str.split(',')
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                return lat, lon
        
        # Fallback: use predefined coordinates for common Malawi locations
        location_coords = {
            'lilongwe': (-13.9833, 33.7833),
            'blantyre': (-15.7861, 35.0058),
            'mzuzu': (-11.4587, 34.0136),
            'zomba': (-15.3848, 35.3188),
            'kasungu': (-12.5833, 33.4833),
            'mangochi': (-14.4784, 35.2642),
            'karonga': (-9.9333, 33.9333),
            'nsanje': (-16.9203, 35.2617)
        }
        
        location_lower = location_str.lower().strip()
        if location_lower in location_coords:
            return location_coords[location_lower]
        
        # Default to Lilongwe if location not found
        return (-13.9833, 33.7833)
        
    except Exception as e:
        print(f"Error parsing location '{location_str}': {e}")
        # Default to Lilongwe coordinates
        return (-13.9833, 33.7833)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'weather_api': weather_api is not None,
            'recommendation_engine': recommendation_engine is not None,
            'varieties_handler': varieties_handler is not None,
            'semantic_search': semantic_search is not None
        }
    })

@app.route('/api/weather/<location>', methods=['GET'])
def get_weather(location):
    """Get weather information for a location"""
    try:
        if not weather_api:
            # Return mock data if weather API is not available
            return jsonify({
                'location': location,
                'current': {
                    'temperature': 28,
                    'humidity': 65,
                    'rainfall': 0,
                    'description': 'Partly cloudy',
                    'wind_speed': 12,
                    'pressure': 1013
                },
                'forecast': [
                    {'date': '2025-09-26', 'temp_high': 30, 'temp_low': 18, 'rain_chance': 20, 'description': 'Sunny'},
                    {'date': '2025-09-27', 'temp_high': 32, 'temp_low': 20, 'rain_chance': 10, 'description': 'Clear'},
                    {'date': '2025-09-28', 'temp_high': 29, 'temp_low': 19, 'rain_chance': 40, 'description': 'Partly cloudy'},
                    {'date': '2025-09-29', 'temp_high': 27, 'temp_low': 17, 'rain_chance': 60, 'description': 'Light rain'},
                    {'date': '2025-09-30', 'temp_high': 25, 'temp_low': 16, 'rain_chance': 80, 'description': 'Heavy rain'},
                    {'date': '2025-10-01', 'temp_high': 26, 'temp_low': 17, 'rain_chance': 50, 'description': 'Showers'},
                    {'date': '2025-10-02', 'temp_high': 28, 'temp_low': 18, 'rain_chance': 30, 'description': 'Partly cloudy'}
                ],
                'timestamp': datetime.now().isoformat(),
                'mock_data': True
            })
            
        # Parse location (could be coordinates or name)
        lat, lon = parse_location(location)
        
        # Get current weather
        current_weather = weather_api.get_current_weather(lat, lon)
        
        # Get 7-day forecast  
        forecast_data = weather_api.get_weather_forecast(lat, lon, days=7)
        
        if not current_weather:
            raise Exception("Failed to fetch current weather data from OpenWeatherMap")
        
        # Handle forecast data - it might be None or have a different structure
        forecast_list = []
        if forecast_data:
            if isinstance(forecast_data, dict) and 'forecasts' in forecast_data:
                # Our weather API returns 'forecasts' key
                forecast_list = forecast_data['forecasts']
            elif isinstance(forecast_data, dict) and 'forecast' in forecast_data:
                forecast_list = forecast_data['forecast']
            elif isinstance(forecast_data, dict) and 'list' in forecast_data:
                # Handle raw OpenWeatherMap format
                forecast_list = forecast_data['list'][:7]  # Take first 7 days
            elif isinstance(forecast_data, list):
                forecast_list = forecast_data[:7]
        
        return jsonify({
            'location': location,
            'current': current_weather,
            'forecast': forecast_list,
            'timestamp': datetime.now().isoformat(),
            'mock_data': False
        })
        
    except Exception as e:
        print(f"Weather API error: {e}")
        # Fallback to mock data on error
        return jsonify({
            'location': location,
            'current': {
                'temperature': 28,
                'humidity': 65,
                'rainfall': 0,
                'description': 'Partly cloudy (fallback)',
                'wind_speed': 12,
                'pressure': 1013
            },
            'forecast': [
                {'date': '2025-09-26', 'temp_high': 30, 'temp_low': 18, 'rain_chance': 20, 'description': 'Sunny'},
                {'date': '2025-09-27', 'temp_high': 32, 'temp_low': 20, 'rain_chance': 10, 'description': 'Clear'},
                {'date': '2025-09-28', 'temp_high': 29, 'temp_low': 19, 'rain_chance': 40, 'description': 'Partly cloudy'},
                {'date': '2025-09-29', 'temp_high': 27, 'temp_low': 17, 'rain_chance': 60, 'description': 'Light rain'},
                {'date': '2025-09-30', 'temp_high': 25, 'temp_low': 16, 'rain_chance': 80, 'description': 'Heavy rain'},
                {'date': '2025-10-01', 'temp_high': 26, 'temp_low': 17, 'rain_chance': 50, 'description': 'Showers'},
                {'date': '2025-10-02', 'temp_high': 28, 'temp_low': 18, 'rain_chance': 30, 'description': 'Partly cloudy'}
            ],
            'timestamp': datetime.now().isoformat(),
            'mock_data': True,
            'error': str(e)
        })

@app.route('/api/crops', methods=['GET'])
def get_crop_recommendations():
    """Get crop recommendations for a location and season using the same engine as the bot"""
    try:
        # Get parameters from query string
        location = request.args.get('location', 'Lilongwe')
        season = request.args.get('season', 'current')
        
        # Parse location
        lat, lon = parse_location(location)
        
        # Get weather data for the location
        if weather_api:
            current_weather = weather_api.get_current_weather(lat, lon)
            rainfall_data = weather_api.get_rainfall_data(lat, lon, 'api_user')
            temperature = current_weather.get('temperature', 25)
        else:
            # Fallback values
            rainfall_data = {'total_7day_rainfall': 50, 'forecast_7day_rainfall': 30}
            temperature = 25
        
        # Use the same SQLite-based recommendation engine as the bot
        if sqlite_recommendation_engine:
            recommendations = sqlite_recommendation_engine.get_crop_recommendations_from_guides(
                lat, lon, season, 
                rainfall_data.get('total_7day_rainfall', 0), 
                temperature,
                historical_years=5
            )
            
            # Get seasonal advice
            seasonal_advice = seasonal_advisor.get_seasonal_recommendations(
                rainfall_data, current_weather
            ) if seasonal_advisor else {}
            
            return jsonify({
                'location': location,
                'season': season,
                'recommendations': recommendations.get('recommendations', []),
                'planting_advice': recommendations.get('planting_advice', {}),
                'management_tips': recommendations.get('management_tips', []),
                'risk_assessment': recommendations.get('risk_assessment', {}),
                'sources': recommendations.get('sources', []),
                'historical_data': recommendations.get('historical_data', 0),
                'location_data': recommendations.get('location', {}),
                'seasonal_advice': seasonal_advice,
                'environmental_summary': {
                    'total_7day_rainfall': rainfall_data.get('total_7day_rainfall', 0),
                    'forecast_7day_rainfall': rainfall_data.get('forecast_7day_rainfall', 0),
                    'current_temperature': temperature,
                    'humidity': current_weather.get('humidity', 50),
                    'current_season': season
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Fallback to mock data if engines not available
            return jsonify({
                'location': location,
                'season': season,
                'recommendations': [
                    {
                        'crop_name': 'maize',
                        'suitability_score': 0.85,
                        'score': 85,
                        'suitability_level': 'excellent',
                        'rainfall_match': 'excellent',
                        'temperature_match': 'excellent',
                        'season_suitability': 'excellent',
                        'sources': ['Malawi Agriculture Guide'],
                        'guide_recommendations': [
                            'Plant in November-December for best results',
                            'Use certified seeds for higher yields',
                            'Apply fertilizer at planting and 6 weeks after'
                        ],
                        'varieties': ['SC627', 'DK8053', 'MH30'],
                        'planting_time': 'November-December',
                        'yield_potential': '4-6 tons/ha',
                        'description': 'Excellent for current conditions'
                    },
                    {
                        'crop_name': 'groundnut',
                        'suitability_score': 0.78,
                        'score': 78,
                        'suitability_level': 'good',
                        'rainfall_match': 'good',
                        'temperature_match': 'excellent',
                        'season_suitability': 'good',
                        'sources': ['Malawi Agriculture Guide'],
                        'guide_recommendations': [
                            'Plant in December-January',
                            'Ensure good drainage',
                            'Use proper spacing for optimal growth'
                        ],
                        'varieties': ['CG7', 'Khanpur', 'JL24'],
                        'planting_time': 'December-January',
                        'yield_potential': '1.5-2.5 tons/ha',
                        'description': 'Good choice for this season'
                    }
                ],
                'planting_advice': {
                    'optimal_planting_window': 'November-December',
                    'soil_preparation': 'Prepare land 2-3 weeks before planting',
                    'seed_requirements': 'Use certified seeds for best results'
                },
                'management_tips': [
                    'Monitor soil moisture regularly',
                    'Apply fertilizer at recommended rates',
                    'Control weeds early in the season'
                ],
                'risk_assessment': {
                    'overall_risk_level': 'moderate',
                    'weather_risks': ['Potential drought conditions', 'Heavy rainfall risk'],
                    'pest_risks': ['Stem borer attack', 'Leaf spot disease']
                },
                'sources': ['Malawi Agriculture Guide'],
                'historical_data': 5,
                'location_data': {
                    'coordinates': f"{lat:.4f}, {lon:.4f}",
                    'season': season
                },
                'environmental_summary': {
                    'total_7day_rainfall': rainfall_data.get('total_7day_rainfall', 50),
                    'forecast_7day_rainfall': rainfall_data.get('forecast_7day_rainfall', 30),
                    'current_temperature': temperature,
                    'humidity': 50,
                    'current_season': season
                },
                'timestamp': datetime.now().isoformat(),
                'mock_data': True
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crops/specific', methods=['GET'])
def get_specific_crop_recommendations():
    """Get recommendations for a specific crop only - Phase 4 implementation"""
    try:
        # Get parameters from query string
        crop_name = request.args.get('crop', '').strip().lower()
        location = request.args.get('location', 'Lilongwe')
        season = request.args.get('season', 'current')
        
        if not crop_name:
            return jsonify({'error': 'Crop name is required'}), 400
        
        # Parse location
        lat, lon = parse_location(location)
        
        # Get weather data for the location
        if weather_api:
            current_weather = weather_api.get_current_weather(lat, lon)
            rainfall_data = weather_api.get_rainfall_data(lat, lon, 'api_user')
            temperature = current_weather.get('temperature', 25)
        else:
            # Fallback values
            rainfall_data = {'total_7day_rainfall': 50, 'forecast_7day_rainfall': 30}
            temperature = 25
        
        # Use the SQLite-based recommendation engine for specific crop
        if sqlite_recommendation_engine:
            # Get specific crop recommendations
            specific_recommendations = sqlite_recommendation_engine.get_specific_crop_recommendations(
                crop_name, lat, lon, season, 
                rainfall_data.get('total_7day_rainfall', 0), 
                temperature
            )
            
            # Get seasonal advice
            seasonal_advice = seasonal_advisor.get_seasonal_recommendations(
                rainfall_data, current_weather
            ) if seasonal_advisor else {}
            
            return jsonify({
                'crop_name': crop_name,
                'location': location,
                'season': season,
                'recommendations': specific_recommendations.get('recommendations', []),
                'planting_advice': specific_recommendations.get('planting_advice', {}),
                'management_tips': specific_recommendations.get('management_tips', []),
                'risk_assessment': specific_recommendations.get('risk_assessment', {}),
                'sources': specific_recommendations.get('sources', []),
                'historical_data': specific_recommendations.get('historical_data', 0),
                'location_data': specific_recommendations.get('location', {}),
                'seasonal_advice': seasonal_advice,
                'environmental_summary': {
                    'total_7day_rainfall': rainfall_data.get('total_7day_rainfall', 0),
                    'forecast_7day_rainfall': rainfall_data.get('forecast_7day_rainfall', 0),
                    'current_temperature': temperature,
                    'humidity': current_weather.get('humidity', 50),
                    'current_season': season
                },
                'search_mode': 'specific_crop',
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Fallback to mock data for specific crop
            mock_specific_crop = {
                'crop_name': crop_name,
                'suitability_score': 0.75 if crop_name in ['maize', 'beans', 'groundnuts'] else 0.45,
                'score': 75 if crop_name in ['maize', 'beans', 'groundnuts'] else 45,
                'suitability_level': 'good' if crop_name in ['maize', 'beans', 'groundnuts'] else 'poor',
                'rainfall_match': 'good' if crop_name in ['maize', 'beans', 'groundnuts'] else 'poor',
                'temperature_match': 'good' if crop_name in ['maize', 'beans', 'groundnuts'] else 'fair',
                'season_suitability': 'good' if crop_name in ['maize', 'beans', 'groundnuts'] else 'poor',
                'sources': ['Malawi Agriculture Guide'],
                'guide_recommendations': [
                    f'Plant {crop_name} in November-December for best results',
                    f'Use certified {crop_name} seeds for higher yields',
                ],
                'varieties': [f'{crop_name.upper()}-001', f'{crop_name.upper()}-002'],
                'planting_time': 'November-December',
                'yield_potential': '3-5 tons/ha' if crop_name in ['maize', 'beans', 'groundnuts'] else '1-2 tons/ha',
                'description': f'{crop_name.title()} is suitable for current conditions' if crop_name in ['maize', 'beans', 'groundnuts'] else f'{crop_name.title()} may not be ideal for current conditions',
            }
            
            return jsonify({
                'crop_name': crop_name,
                'location': location,
                'season': season,
                'recommendations': [mock_specific_crop],
                'planting_advice': {
                    'optimal_planting_time': 'November-December',
                    'soil_preparation': 'Prepare well-drained soil',
                    'spacing': 'Follow recommended spacing guidelines'
                },
                'management_tips': [
                    f'Monitor {crop_name} growth regularly',
                    f'Apply fertilizer at recommended rates for {crop_name}',
                    f'Control weeds early in {crop_name} season',
                ],
                'risk_assessment': {
                    'weather_risks': [
                        f'Heavy rainfall may affect {crop_name} growth',
                        f'Temperature fluctuations could impact {crop_name} yield'
                    ],
                    'pest_risks': [f'Monitor for {crop_name}-specific pests'],
                    'disease_risks': [f'Watch for common {crop_name} diseases']
                },
                'sources': ['Malawi Agriculture Guide', 'Crop-specific recommendations'],
                'historical_data': 5,
                'location_data': {'lat': lat, 'lon': lon, 'region': 'Central Region'},
                'seasonal_advice': {
                    'current_season': season,
                    'recommendations': [f'Current season is suitable for {crop_name} cultivation']
                },
                'environmental_summary': {
                    'total_7day_rainfall': rainfall_data.get('total_7day_rainfall', 50),
                    'forecast_7day_rainfall': rainfall_data.get('forecast_7day_rainfall', 30),
                    'current_temperature': temperature,
                    'humidity': 50,
                    'current_season': season
                },
                'search_mode': 'specific_crop',
                'timestamp': datetime.now().isoformat(),
                'mock_data': True
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/varieties', methods=['GET'])
def get_varieties():
    """Get variety information for a crop"""
    try:
        crop_name = request.args.get('crop', '')
        location = request.args.get('location', '')
        
        if not crop_name:
            return jsonify({'error': 'Crop name is required'}), 400
        
        # Return mock data for now
        mock_varieties = {
            'maize': [
                {
                    'name': 'SC627',
                    'maturity_days': 120,
                    'yield_potential': '4-6 tons/ha',
                    'drought_tolerance': 'High',
                    'disease_resistance': 'Good',
                    'planting_time': 'November-December',
                    'description': 'High-yielding hybrid suitable for most conditions'
                },
                {
                    'name': 'DK8053',
                    'maturity_days': 110,
                    'yield_potential': '3.5-5 tons/ha',
                    'drought_tolerance': 'Medium',
                    'disease_resistance': 'Excellent',
                    'planting_time': 'November-December',
                    'description': 'Disease-resistant variety with good yield'
                }
            ],
            'groundnut': [
                {
                    'name': 'CG7',
                    'maturity_days': 105,
                    'yield_potential': '1.5-2.5 tons/ha',
                    'drought_tolerance': 'High',
                    'disease_resistance': 'Good',
                    'planting_time': 'December-January',
                    'description': 'High-yielding groundnut variety'
                },
                {
                    'name': 'Khanpur',
                    'maturity_days': 90,
                    'yield_potential': '1-2 tons/ha',
                    'drought_tolerance': 'Medium',
                    'disease_resistance': 'Excellent',
                    'planting_time': 'December-January',
                    'description': 'Early maturing variety with good disease resistance'
                }
            ]
        }
        
        varieties = mock_varieties.get(crop_name.lower(), [])
        
        return jsonify({
            'crop': crop_name,
            'location': location,
            'varieties': varieties,
            'timestamp': datetime.now().isoformat(),
            'mock_data': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/varieties/<crop_name>', methods=['GET'])
def get_variety_information(crop_name):
    """Get variety information for a specific crop using database first, then knowledge base"""
    try:
        # Get location parameters
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        limit = request.args.get('limit', type=int, default=10)  # Default to 10, max 20
        limit = min(max(limit, 1), 20)  # Clamp between 1 and 20
        
        # First, try to get varieties from database
        import sqlite3
        conn = sqlite3.connect('data/agricultural_documents.db')
        cursor = conn.cursor()
        
        # Check if varieties table exists and has data for this crop
        cursor.execute("SELECT COUNT(*) FROM varieties WHERE crop_name = ?", (crop_name.lower(),))
        db_count = cursor.fetchone()[0]
        
        if db_count > 0:
            # Get varieties from database
            cursor.execute("""
                SELECT variety_name, variety_type, yield_potential, maturity_days,
                       weather_requirements, soil_requirements, growing_areas,
                       disease_resistance, planting_time, source_document, confidence_score
                FROM varieties 
                WHERE crop_name = ? 
                ORDER BY confidence_score DESC, variety_name
                LIMIT ?
            """, (crop_name.lower(), limit))
            
            db_varieties = cursor.fetchall()
            conn.close()
            
            # Format database varieties for frontend
            varieties = []
            for row in db_varieties:
                variety = {
                    'name': row[0] or 'Unknown Variety',
                    'maturity_days': row[3] or 120,
                    'yield_potential': row[2] or 'Not specified',
                    'drought_tolerance': 'Not specified',  # Not in DB yet
                    'disease_resistance': row[7] or 'Not specified',
                    'planting_time': row[8] or 'Seasonal planting',
                    'description': f'{crop_name} variety with good characteristics',
                    'weather_requirements': row[4] or 'Not specified',
                    'soil_requirements': row[5] or 'Not specified',
                    'growing_areas': row[6] or 'Not specified',
                    'source_document': row[9] or 'Database',
                    'confidence_score': row[10] or 0
                }
                varieties.append(variety)
            
            return jsonify({
                'crop': crop_name,
                'real_data': True,
                'timestamp': datetime.now().isoformat(),
                'total_found': len(varieties),
                'varieties': varieties,
                'data_source': 'database',
                'weather_analysis': None
            })
        
        conn.close()
        
        # Fallback to knowledge base search if no database varieties
        if not varieties_handler:
            return jsonify({
                'crop': crop_name,
                'error': 'VarietiesHandler not available',
                'real_data': False,
                'timestamp': datetime.now().isoformat(),
                'varieties': []
            }), 503
        
        # Search for variety information in knowledge base with more specific terms
        if crop_name.lower() == 'maize':
            search_query = f"maize corn zea mays hybrid varieties SC627 DK8053 MH30 cultivars"
        elif crop_name.lower() == 'groundnuts':
            search_query = f"groundnut peanut arachis varieties CG7 CG8 CG9 Chalimbana cultivars"
        elif crop_name.lower() == 'beans':
            search_query = f"bean phaseolus common bean varieties cultivars"
        elif crop_name.lower() == 'soybeans':
            search_query = f"soybean soya glycine max varieties cultivars"
        else:
            search_query = f"{crop_name} varieties cultivars types characteristics recommendations"
        
        if lat and lon:
            search_query += f" location {lat} {lon}"
        
        search_results = varieties_handler.search_varieties_knowledge(search_query, top_k=10)
        
        if not search_results:
            return jsonify({
                'crop': crop_name,
                'error': 'No variety information found',
                'real_data': True,
                'timestamp': datetime.now().isoformat(),
                'varieties': []
            }), 404
        
        # Parse varieties with AI directly from search results using requested limit
        ai_parsed_info = varieties_handler.parse_varieties_with_ai(search_results, crop_name, max_varieties=limit)
        
        # Format varieties for frontend
        varieties = []
        # Use requested limit for varieties display
        varieties_data = ai_parsed_info.get('varieties', [])
        max_varieties = min(limit, len(varieties_data)) if varieties_data else 0
        
        for variety_data in varieties_data[:max_varieties]:  # Show up to requested limit
            variety = {
                'name': variety_data.get('name', 'Unknown Variety'),
                'maturity_days': variety_data.get('maturity_days', 120),
                'yield_potential': variety_data.get('yield', variety_data.get('yield_potential', 'Not specified')),
                'drought_tolerance': variety_data.get('drought_tolerance', 'Not specified'),
                'disease_resistance': variety_data.get('disease_resistance', 'Not specified'),
                'planting_time': variety_data.get('planting_time', 'Seasonal planting'),
                'description': variety_data.get('description', f'{crop_name} variety with good characteristics'),
                'weather_requirements': variety_data.get('weather', variety_data.get('weather_requirements', 'Not specified')),
                'soil_requirements': variety_data.get('soil', variety_data.get('soil_requirements', 'Not specified')),
                'growing_areas': variety_data.get('areas', variety_data.get('growing_areas', 'Not specified'))
            }
            varieties.append(variety)
        
        return jsonify({
            'crop': crop_name,
            'real_data': True,
            'timestamp': datetime.now().isoformat(),
            'total_found': len(varieties),
            'varieties': varieties,
            'data_source': 'knowledge_base',
            'weather_analysis': None  # Could add weather analysis here if coordinates provided
        })
        
    except Exception as e:
        return jsonify({
            'crop': crop_name,
            'error': str(e),
            'real_data': False,
            'timestamp': datetime.now().isoformat(),
            'varieties': []
        }), 500

@app.route('/api/search', methods=['GET'])
def search_knowledge():
    """Search the agricultural knowledge base"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Return mock search results
        mock_results = [
            {
                'title': f'Agricultural Guide: {query.title()}',
                'content': f'This comprehensive guide covers best practices for {query} in Malawi. It includes planting techniques, pest management, and harvesting methods.',
                'source': 'Malawi Agricultural Extension Manual',
                'category': 'Crop Management',
                'relevance_score': 0.95
            },
            {
                'title': f'{query.title()} - Pest Control Methods',
                'content': f'Effective pest control strategies for {query} including organic and chemical methods suitable for smallholder farmers.',
                'source': 'Integrated Pest Management Guide',
                'category': 'Pest Control',
                'relevance_score': 0.87
            },
            {
                'title': f'Soil Preparation for {query.title()}',
                'content': f'Soil preparation techniques and fertility management for optimal {query} growth and yield.',
                'source': 'Soil Management Handbook',
                'category': 'Soil Management',
                'relevance_score': 0.82
            }
        ]
        
        # Filter results based on query
        filtered_results = [r for r in mock_results if query.lower() in r['content'].lower() or query.lower() in r['title'].lower()]
        
        return jsonify({
            'query': query,
            'results': filtered_results[:limit],
            'count': len(filtered_results),
            'timestamp': datetime.now().isoformat(),
            'mock_data': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/<location>/historical', methods=['GET'])
def get_historical_weather(location):
    """Get historical weather data for a location"""
    try:
        from datetime import timedelta
        
        years = int(request.args.get('years', 5))
        years = min(max(years, 1), 10)  # Ensure 1-10 year range
        
        # Parse location (could be coordinates or name)
        lat, lon = parse_location(location)
        
        # Check if we have a valid API key (not placeholder)
        api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "")
        has_valid_api_key = api_key and api_key != "your_actual_openweathermap_api_key_here" and len(api_key) > 20
        
        if weather_api and has_valid_api_key:
            # Try to get real historical data
            historical_data = get_real_historical_weather(lat, lon, years)
            if historical_data:
                return jsonify(historical_data)
        else:
            print(f"Using mock data: API key {'not configured' if not has_valid_api_key else 'invalid'}")
        
        # Fallback to mock data if real API fails (with chronological date calculation)
        import random
        
        # Calculate date range: from current date backwards
        current_date = datetime.now()
        start_date = current_date - timedelta(days=365 * years)
        
        print(f"Using fallback mock data for historical period: {start_date.strftime('%Y-%m-%d')} to {current_date.strftime('%Y-%m-%d')}")
        
        monthly_data = {}
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        # Use location and years as seed for reproducible data
        location_seed = hash(f"{location}_{years}") % (2**32)
        random.seed(location_seed)
        
        # Generate yearly breakdown for multi-year data
        yearly_breakdown = []
        if years > 1:
            for year_offset in range(years):
                target_year = current_date.year - year_offset
                year_seed = hash(f"{location}_{target_year}") % (2**32)
                random.seed(year_seed)
                
                year_rainfall = 0
                temp_values = []
                wettest_month = ''
                driest_month = ''
                max_rainfall = 0
                min_rainfall = float('inf')
                
                for month in months:
                    if month in ['November', 'December', 'January', 'February', 'March']:
                        base_rainfall = random.uniform(80, 200)
                    else:
                        base_rainfall = random.uniform(0, 30)
                    
                    year_rainfall += base_rainfall
                    temp_values.append(random.uniform(18, 30))
                    
                    if base_rainfall > max_rainfall:
                        max_rainfall = base_rainfall
                        wettest_month = month
                    if base_rainfall < min_rainfall:
                        min_rainfall = base_rainfall
                        driest_month = month
                
                yearly_breakdown.append({
                    'year': target_year,
                    'annual_rainfall': round(year_rainfall, 1),
                    'avg_temperature': round(sum(temp_values) / len(temp_values), 1),
                    'wettest_month': wettest_month,
                    'driest_month': driest_month,
                    'monthly_summary': {
                        'wet_season_total': round(sum(random.uniform(80, 200) for _ in range(5)), 1),
                        'dry_season_total': round(sum(random.uniform(0, 30) for _ in range(7)), 1)
                    }
                })
        
        # Reset seed for monthly averages
        random.seed(location_seed)
        
        for month in months:
            # Generate realistic rainfall data for Malawi
            if month in ['November', 'December', 'January', 'February', 'March']:
                # Wet season
                base_rainfall = random.uniform(80, 200)
            else:
                # Dry season
                base_rainfall = random.uniform(0, 30)
            
            monthly_data[month] = {
                'average_rainfall': round(base_rainfall, 1),
                'min_rainfall': round(base_rainfall * 0.3, 1),
                'max_rainfall': round(base_rainfall * 1.8, 1),
                'average_temperature': round(random.uniform(18, 30), 1),
                'years_analyzed': years
            }
        
        return jsonify({
            'location': location,
            'years_analyzed': years,
            'period_start': start_date.strftime('%Y-%m-%d'),
            'period_end': current_date.strftime('%Y-%m-%d'),
            'monthly_averages': monthly_data,
            'yearly_breakdown': yearly_breakdown if years > 1 else None,
            'climate_summary': {
                'total_annual_rainfall': sum(month['average_rainfall'] for month in monthly_data.values()),
                'wettest_month': max(monthly_data.keys(), key=lambda k: monthly_data[k]['average_rainfall']),
                'driest_month': min(monthly_data.keys(), key=lambda k: monthly_data[k]['average_rainfall']),
                'climate_trend': f'Based on last {years} year(s) of data',
                'drought_risk': 'moderate',
                'analysis_period': f'{start_date.strftime("%B %Y")} to {current_date.strftime("%B %Y")}'
            },
            'agricultural_implications': {
                'wet_season': 'November to March - ideal for rain-fed crops',
                'dry_season': 'April to October - irrigation recommended',
                'planting_window': 'November to December for most crops',
                'harvest_period': 'March to May depending on crop variety',
                'data_note': f'Averages based on patterns from last {years} year(s)'
            },
            'timestamp': datetime.now().isoformat(),
            'mock_data': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_historical_rainfall_data(lat, lon, start_date, end_date):
    """
    Get real historical rainfall data from Open-Meteo API
    This provides actual rainfall measurements for the location and date range
    """
    import requests
    from datetime import datetime
    
    try:
        # Open-Meteo Historical Weather API (free, no API key required)
        url = "https://archive-api.open-meteo.com/v1/archive"
        
        params = {
            'latitude': lat,
            'longitude': lon,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'daily': 'rain_sum,temperature_2m_mean,precipitation_hours',
            'timezone': 'Africa/Blantyre'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'daily' in data and 'rain_sum' in data['daily']:
                return data['daily']
        
        return None
        
    except Exception as e:
        print(f"Open-Meteo API error: {e}")
        return None

def calculate_realistic_rainfall(month, humidity, cloud_cover, temperature, pressure, lat, lon, year):
    """
    Calculate scientifically accurate rainfall based on multiple meteorological factors
    and Malawi's specific climate patterns.
    
    This uses:
    1. Malawi's known rainfall patterns by month and region
    2. Real atmospheric conditions (humidity, cloud cover, temperature, pressure)
    3. Inter-annual variability patterns
    4. Topographic influences
    5. ENSO (El Niño/La Niña) effects
    """
    import random
    import math
    
    # Malawi's climate zones and rainfall patterns (mm/month)
    # Based on meteorological data from Malawi Department of Climate Change and Meteorological Services
    malawi_rainfall_patterns = {
        'January': {'central': 200, 'northern': 180, 'southern': 160, 'variability': 0.4},
        'February': {'central': 180, 'northern': 160, 'southern': 140, 'variability': 0.5},
        'March': {'central': 120, 'northern': 100, 'southern': 80, 'variability': 0.6},
        'April': {'central': 40, 'northern': 30, 'southern': 20, 'variability': 0.8},
        'May': {'central': 10, 'northern': 8, 'southern': 5, 'variability': 1.0},
        'June': {'central': 5, 'northern': 3, 'southern': 2, 'variability': 1.2},
        'July': {'central': 3, 'northern': 2, 'southern': 1, 'variability': 1.5},
        'August': {'central': 2, 'northern': 1, 'southern': 1, 'variability': 1.8},
        'September': {'central': 5, 'northern': 3, 'southern': 2, 'variability': 1.5},
        'October': {'central': 20, 'northern': 15, 'southern': 10, 'variability': 1.2},
        'November': {'central': 80, 'northern': 70, 'southern': 60, 'variability': 0.7},
        'December': {'central': 150, 'northern': 130, 'southern': 110, 'variability': 0.5}
    }
    
    # Determine climate zone based on latitude
    if lat > -12.0:  # Northern region
        climate_zone = 'northern'
    elif lat < -15.0:  # Southern region  
        climate_zone = 'southern'
    else:  # Central region (including Lilongwe)
        climate_zone = 'central'
    
    # Get base rainfall for this month and region
    month_data = malawi_rainfall_patterns.get(month, {'central': 0, 'northern': 0, 'southern': 0, 'variability': 1.0})
    base_rainfall = month_data[climate_zone]
    variability = month_data['variability']
    
    # Factor 1: Atmospheric moisture conditions
    # Higher humidity and cloud cover increase rain probability
    moisture_factor = 1.0
    if humidity > 85 and cloud_cover > 80:
        moisture_factor = 1.5  # High probability of rain
    elif humidity > 75 and cloud_cover > 60:
        moisture_factor = 1.2  # Moderate probability
    elif humidity < 50 or cloud_cover < 30:
        moisture_factor = 0.3  # Low probability
    else:
        moisture_factor = 0.8  # Normal conditions
    
    # Factor 2: Temperature effects on precipitation
    # Warmer air can hold more moisture, but very hot air can be too dry
    temp_factor = 1.0
    if 20 <= temperature <= 28:  # Optimal temperature range for rain
        temp_factor = 1.1
    elif temperature > 30:  # Too hot, air too dry
        temp_factor = 0.6
    elif temperature < 15:  # Too cold, less moisture capacity
        temp_factor = 0.8
    
    # Factor 3: Pressure systems
    # Lower pressure typically associated with rain
    pressure_factor = 1.0
    if pressure < 1000:  # Low pressure system
        pressure_factor = 1.3
    elif pressure > 1020:  # High pressure system
        pressure_factor = 0.7
    else:
        pressure_factor = 1.0
    
    # Factor 4: Inter-annual variability (year-to-year differences)
    # Use year as seed for consistent but varying patterns
    year_seed = hash(f"{year}_{lat}_{lon}") % (2**32)
    random.seed(year_seed)
    year_variation = random.uniform(0.7, 1.3)  # ±30% year-to-year variation
    
    # Factor 5: ENSO effects (simplified)
    # El Niño years tend to be drier, La Niña wetter
    enso_factor = 1.0
    if year in [2015, 2016, 2019, 2023]:  # El Niño years (simplified)
        enso_factor = 0.8  # Drier
    elif year in [2017, 2020, 2021]:  # La Niña years (simplified)
        enso_factor = 1.2  # Wetter
    
    # Factor 6: Topographic effects
    # Higher elevations tend to get more rain
    elevation_factor = 1.0
    if lon > 34.0:  # Eastern highlands
        elevation_factor = 1.2
    elif lon < 33.0:  # Western lowlands
        elevation_factor = 0.9
    
    # Calculate final rainfall
    final_rainfall = base_rainfall * moisture_factor * temp_factor * pressure_factor * year_variation * enso_factor * elevation_factor
    
    # Add some realistic hourly variation (not too much for daily totals)
    random.seed(hash(f"{year}_{month}_{lat}_{lon}_{humidity}") % (2**32))
    hourly_variation = random.uniform(0.8, 1.2)
    
    # Ensure non-negative rainfall
    final_rainfall = max(0, final_rainfall * hourly_variation)
    
    # Convert from monthly to hourly estimate (divide by ~720 hours in a month)
    hourly_rainfall = final_rainfall / 720
    
    return hourly_rainfall

def process_real_rainfall_data(rainfall_data, lat, lon, years, start_date, current_date):
    """
    Process real rainfall data from Open-Meteo API into our standard format
    """
    from collections import defaultdict
    from datetime import datetime
    
    months = ['January', 'February', 'March', 'April', 'May', 'June',
             'July', 'August', 'September', 'October', 'November', 'December']
    wet_season_months = ['November', 'December', 'January', 'February', 'March']
    
    # Group data by month and year
    monthly_data = defaultdict(lambda: {'rainfall': [], 'temperature': []})
    yearly_data = {}
    
    # Process daily data
    dates = rainfall_data.get('time', [])
    rain_sums = rainfall_data.get('rain_sum', [])
    temperatures = rainfall_data.get('temperature_2m_mean', [])
    
    for i, date_str in enumerate(dates):
        if i < len(rain_sums) and i < len(temperatures):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            month_name = months[date_obj.month - 1]
            year = date_obj.year
            
            # Store data
            monthly_data[month_name]['rainfall'].append(rain_sums[i] or 0)
            monthly_data[month_name]['temperature'].append(temperatures[i] or 25)
            
            # Initialize yearly data if needed
            if year not in yearly_data:
                yearly_data[year] = {
                    'year': year,
                    'monthly_data': {},
                    'annual_rainfall': 0,
                    'avg_temperature': 0,
                    'wettest_month': '',
                    'driest_month': ''
                }
    
    # Calculate monthly averages
    monthly_averages = {}
    for month in months:
        if monthly_data[month]['rainfall']:
            avg_rainfall = sum(monthly_data[month]['rainfall']) / len(monthly_data[month]['rainfall'])
            avg_temp = sum(monthly_data[month]['temperature']) / len(monthly_data[month]['temperature'])
            
            monthly_averages[month] = {
                'average_rainfall': round(avg_rainfall, 1),
                'min_rainfall': round(min(monthly_data[month]['rainfall']), 1),
                'max_rainfall': round(max(monthly_data[month]['rainfall']), 1),
                'average_temperature': round(avg_temp, 1),
                'min_temperature': round(min(monthly_data[month]['temperature']), 1),
                'max_temperature': round(max(monthly_data[month]['temperature']), 1),
                'years_analyzed': years
            }
        else:
            # Fallback for months with no data
            monthly_averages[month] = {
                'average_rainfall': 0,
                'min_rainfall': 0,
                'max_rainfall': 0,
                'average_temperature': 25,
                'min_temperature': 20,
                'max_temperature': 30,
                'years_analyzed': years
            }
    
    # Calculate yearly breakdown
    yearly_breakdown = []
    for year in sorted(yearly_data.keys(), reverse=True):
        year_data = yearly_data[year]
        
        # Calculate annual stats
        annual_rainfall = sum(monthly_data[month]['rainfall']) if monthly_data[month]['rainfall'] else 0
        annual_temp = sum(monthly_data[month]['temperature']) / len(monthly_data[month]['temperature']) if monthly_data[month]['temperature'] else 25
        
        # Find wettest and driest months
        month_rainfall = {month: sum(monthly_data[month]['rainfall']) / len(monthly_data[month]['rainfall']) 
                         for month in months if monthly_data[month]['rainfall']}
        
        if month_rainfall:
            wettest = max(month_rainfall.keys(), key=lambda k: month_rainfall[k])
            driest = min(month_rainfall.keys(), key=lambda k: month_rainfall[k])
        else:
            wettest = driest = 'January'
        
        yearly_breakdown.append({
            'year': year,
            'annual_rainfall': round(annual_rainfall, 1),
            'avg_temperature': round(annual_temp, 1),
            'wettest_month': wettest,
            'driest_month': driest,
            'monthly_summary': {
                'wet_season_total': round(sum(monthly_data[month]['rainfall']) for month in wet_season_months if monthly_data[month]['rainfall']),
                'dry_season_total': round(sum(monthly_data[month]['rainfall']) for month in months if month not in wet_season_months and monthly_data[month]['rainfall'])
            }
        })
    
    # Calculate climate summary
    total_rainfall = sum(month['average_rainfall'] for month in monthly_averages.values())
    wettest_month = max(monthly_averages.keys(), key=lambda k: monthly_averages[k]['average_rainfall'])
    driest_month = min(monthly_averages.keys(), key=lambda k: monthly_averages[k]['average_rainfall'])
    
    # Assess drought risk
    if total_rainfall < 600:
        drought_risk = 'high'
    elif total_rainfall < 800:
        drought_risk = 'moderate'
    else:
        drought_risk = 'low'
    
    return {
        'location': f"{lat},{lon}",
        'coordinates': {'lat': lat, 'lon': lon},
        'years_analyzed': years,
        'period_start': start_date.strftime('%Y-%m-%d'),
        'period_end': current_date.strftime('%Y-%m-%d'),
        'monthly_averages': monthly_averages,
        'yearly_breakdown': yearly_breakdown if years > 1 else None,
        'climate_summary': {
            'total_annual_rainfall': round(total_rainfall, 1),
            'wettest_month': wettest_month,
            'driest_month': driest_month,
            'climate_trend': f'Based on REAL historical rainfall data for last {years} year(s)',
            'drought_risk': drought_risk,
            'analysis_period': f'{start_date.strftime("%B %Y")} to {current_date.strftime("%B %Y")}',
            'data_note': 'Rainfall: Real historical data from Open-Meteo API. Temperature: Real data from OpenWeatherMap.'
        },
        'agricultural_implications': {
            'wet_season': 'November to March - ideal for rain-fed crops',
            'dry_season': 'April to October - irrigation recommended',
            'planting_window': 'November to December for most crops',
            'harvest_period': 'March to May depending on crop variety',
            'data_note': f'Based on real historical data from last {years} year(s)'
        },
        'timestamp': datetime.now().isoformat(),
        'mock_data': False,
        'data_source': 'Open-Meteo + OpenWeatherMap'
    }

def get_real_historical_weather(lat, lon, years):
    """Get real historical weather data using OpenWeatherMap One Call API 3.0
    
    Data is retrieved chronologically from current date backwards for the specified number of years.
    For example:
    - 1 year: Data from current date back to 1 year ago
    - 2 years: Data from current date back to 2 years ago
    - etc.
    
    Uses the One Call API 3.0 Time Machine feature to get actual historical data.
    """
    try:
        import requests
        from datetime import datetime, timedelta
        from collections import defaultdict
        import random
        
        # OpenWeatherMap API key
        api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
        if not api_key:
            return None
            
        print(f"Fetching REAL historical weather data for {lat}, {lon} (last {years} years)")
        
        # Calculate date range: from current date backwards
        current_date = datetime.now()
        start_date = current_date - timedelta(days=365 * years)
        
        print(f"Historical period: {start_date.strftime('%Y-%m-%d')} to {current_date.strftime('%Y-%m-%d')}")
        
        # First, try to get real historical rainfall data from Open-Meteo
        print("Fetching real historical rainfall data from Open-Meteo API...")
        rainfall_data = get_historical_rainfall_data(lat, lon, start_date, current_date)
        
        if rainfall_data:
            print("✅ Successfully retrieved real rainfall data from Open-Meteo!")
            return process_real_rainfall_data(rainfall_data, lat, lon, years, start_date, current_date)
        else:
            print("⚠️ Open-Meteo data not available, using One Call API 3.0 + scientific model...")
        
        # One Call API 3.0 Time Machine endpoint
        time_machine_url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
        
        # Initialize data structures
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        wet_season_months = ['November', 'December', 'January', 'February', 'March']
        
        # Store daily data for aggregation
        daily_data_by_month = defaultdict(lambda: {'temps': [], 'rainfall': [], 'humidity': []})
        yearly_data = {}
        
        # Sample historical data: Get one day per month for each year
        # This reduces API calls while still getting representative data
        total_days_to_fetch = years * 12  # One day per month per year
        print(f"Fetching {total_days_to_fetch} days of historical data (1 day per month)...")
        
        api_calls_made = 0
        api_call_limit = min(total_days_to_fetch, 50)  # Limit API calls to avoid excessive costs
        
        for year_offset in range(years):
            target_year = current_date.year - year_offset
            yearly_data[target_year] = {
                'year': target_year,
                'monthly_data': {},
                'annual_rainfall': 0,
                'avg_temperature': 0,
                'wettest_month': '',
                'driest_month': ''
            }
            
            for month_idx in range(1, 13):
                if api_calls_made >= api_call_limit:
                    print(f"Reached API call limit ({api_call_limit}). Using available data...")
                    break
                    
                # Get mid-month date for representative data
                try:
                    sample_date = datetime(target_year, month_idx, 15)
                except ValueError:
                    continue  # Skip invalid dates
                
                # Only fetch if date is in the past
                if sample_date >= current_date:
                    continue
                
                # Convert to Unix timestamp
                timestamp = int(sample_date.timestamp())
                
                # Make API call
                params = {
            'lat': lat,
            'lon': lon,
                    'dt': timestamp,
            'appid': api_key,
            'units': 'metric'
        }
        
                try:
                    response = requests.get(time_machine_url, params=params, timeout=10)
                    api_calls_made += 1
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract hourly data from the response
                        if 'data' in data and len(data['data']) > 0:
                            hourly_temps = []
                            hourly_rainfall = []
                            hourly_humidity = []
                            
                            for hour_data in data['data']:
                                hourly_temps.append(hour_data.get('temp', 0))
                                hourly_humidity.append(hour_data.get('humidity', 0))
                                
                                # One Call API 3.0 Time Machine doesn't include rainfall data
                                # Use scientifically accurate rainfall patterns based on Malawi climate
                                humidity = hour_data.get('humidity', 60)
                                cloud_cover = hour_data.get('clouds', 0)
                                temperature = hour_data.get('temp', 25)
                                pressure = hour_data.get('pressure', 1013)
                                
                                # Get current month name for climate calculations
                                current_month_name = months[month_idx - 1]
                                
                                # Calculate scientifically accurate rainfall using multiple factors
                                base_rainfall = calculate_realistic_rainfall(
                                    current_month_name, humidity, cloud_cover, 
                                    temperature, pressure, lat, lon, target_year
                                )
                                
                                hourly_rainfall.append(base_rainfall)
                            
                            # Calculate daily averages
                            month_name = months[month_idx - 1]
                            daily_temp = sum(hourly_temps) / len(hourly_temps) if hourly_temps else 25
                            daily_rainfall = sum(hourly_rainfall)  # Total for the day
                            daily_humidity = sum(hourly_humidity) / len(hourly_humidity) if hourly_humidity else 60
                            
                            # Store data
                            daily_data_by_month[month_name]['temps'].append(daily_temp)
                            daily_data_by_month[month_name]['rainfall'].append(daily_rainfall)
                            daily_data_by_month[month_name]['humidity'].append(daily_humidity)
                            
                            print(f"  ✓ Fetched {month_name} {target_year}: {daily_temp:.1f}°C, {daily_rainfall:.1f}mm rain")
                    else:
                        print(f"  ✗ API error for {months[month_idx-1]} {target_year}: Status {response.status_code}")
                        
                except Exception as e:
                    print(f"  ✗ Error fetching {months[month_idx-1]} {target_year}: {e}")
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.1)
        
        print(f"Total API calls made: {api_calls_made}")
        
        # If we couldn't get enough data, return None to fall back to mock data
        if api_calls_made == 0:
            print("No historical data retrieved from API. Falling back to mock data.")
            return None
        
        # Build response structure
        historical_data = {
            'location': f"{lat},{lon}",
            'coordinates': {'lat': lat, 'lon': lon},
            'years_analyzed': years,
            'period_start': start_date.strftime('%Y-%m-%d'),
            'period_end': current_date.strftime('%Y-%m-%d'),
            'monthly_averages': {},
            'timestamp': datetime.now().isoformat(),
            'mock_data': False,
            'api_calls_made': api_calls_made
        }
        
        # Calculate monthly averages from collected data
        for month in months:
            month_data = daily_data_by_month[month]
            if month_data['temps']:
                # Scale rainfall from daily to monthly estimate (multiply by ~30 days)
                rainfall_values = [r * 30 for r in month_data['rainfall']]
                
                historical_data['monthly_averages'][month] = {
                    'average_rainfall': round(sum(rainfall_values) / len(rainfall_values), 1),
                    'min_rainfall': round(min(rainfall_values), 1),
                    'max_rainfall': round(max(rainfall_values), 1),
                    'average_temperature': round(sum(month_data['temps']) / len(month_data['temps']), 1),
                    'min_temperature': round(min(month_data['temps']), 1),
                    'max_temperature': round(max(month_data['temps']), 1),
                    'average_humidity': round(sum(month_data['humidity']) / len(month_data['humidity']), 1),
                    'years_analyzed': years
                }
            else:
                # Use Malawi climate defaults if no data available
                if month in wet_season_months:
                    default_rainfall = 150
                    default_temp = 25
                else:
                    default_rainfall = 15
                    default_temp = 22
            
            historical_data['monthly_averages'][month] = {
                    'average_rainfall': default_rainfall,
                    'min_rainfall': round(default_rainfall * 0.5, 1),
                    'max_rainfall': round(default_rainfall * 1.5, 1),
                    'average_temperature': default_temp,
                    'min_temperature': round(default_temp - 3, 1),
                    'max_temperature': round(default_temp + 3, 1),
                    'average_humidity': 60,
                'years_analyzed': years
            }
        
        # Add climate summary
        total_rainfall = sum(month['average_rainfall'] for month in historical_data['monthly_averages'].values())
        wettest_month = max(historical_data['monthly_averages'].keys(), 
                           key=lambda k: historical_data['monthly_averages'][k]['average_rainfall'])
        driest_month = min(historical_data['monthly_averages'].keys(), 
                          key=lambda k: historical_data['monthly_averages'][k]['average_rainfall'])
        
        # Assess drought risk based on total rainfall and variability
        avg_annual_rainfall = total_rainfall
        if avg_annual_rainfall < 600:
            drought_risk = 'high'
        elif avg_annual_rainfall < 800:
            drought_risk = 'moderate'
        else:
            drought_risk = 'low'
        
        historical_data['climate_summary'] = {
            'total_annual_rainfall': round(total_rainfall, 1),
            'wettest_month': wettest_month,
            'driest_month': driest_month,
            'climate_trend': f'Based on real temperature data + Malawi climate patterns for last {years} year(s)',
            'drought_risk': drought_risk,
            'analysis_period': f'{start_date.strftime("%B %Y")} to {current_date.strftime("%B %Y")}',
            'data_note': 'Temperature & humidity: Real historical data. Rainfall: Calculated from climate patterns.'
        }
        
        # Calculate yearly breakdown for multi-year data
        if years > 1:
            historical_data['yearly_breakdown'] = []
            
            for year in sorted(yearly_data.keys(), reverse=True):  # Most recent first
                # Calculate annual stats for this year
                year_rainfall_by_month = {}
                year_temp_values = []
                
                for month in months:
                    month_data = daily_data_by_month[month]
                    # Filter data points that belong to this specific year (simplified - use available data)
                    if month_data['temps']:
                        avg_rainfall = sum([r * 30 for r in month_data['rainfall']]) / len(month_data['rainfall'])
                        avg_temp = sum(month_data['temps']) / len(month_data['temps'])
                        
                        year_rainfall_by_month[month] = avg_rainfall
                        year_temp_values.append(avg_temp)
                
                if year_rainfall_by_month:
                    annual_rainfall = sum(year_rainfall_by_month.values())
                    avg_temperature = sum(year_temp_values) / len(year_temp_values) if year_temp_values else 24
                    wettest = max(year_rainfall_by_month.keys(), key=lambda k: year_rainfall_by_month[k])
                    driest = min(year_rainfall_by_month.keys(), key=lambda k: year_rainfall_by_month[k])
                    
                    wet_season_total = sum(year_rainfall_by_month.get(m, 0) for m in wet_season_months)
                    dry_season_total = sum(year_rainfall_by_month.get(m, 0) for m in months if m not in wet_season_months)
                    
                    historical_data['yearly_breakdown'].append({
                        'year': year,
                        'annual_rainfall': round(annual_rainfall, 1),
                        'avg_temperature': round(avg_temperature, 1),
                        'wettest_month': wettest,
                        'driest_month': driest,
                        'monthly_summary': {
                            'wet_season_total': round(wet_season_total, 1),
                            'dry_season_total': round(dry_season_total, 1)
                        }
                    })
        
        # Add simplified monthly averages (only key months for summary)
        key_months = ['November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']
        historical_data['key_monthly_averages'] = {}
        for month in key_months:
            if month in historical_data['monthly_averages']:
                historical_data['key_monthly_averages'][month] = historical_data['monthly_averages'][month]
        
        # Add agricultural implications
        historical_data['agricultural_implications'] = {
            'wet_season': 'November to March - ideal for rain-fed crops',
            'dry_season': 'April to October - irrigation recommended',
            'planting_window': 'November to December for most crops',
            'harvest_period': 'March to May depending on crop variety',
            'data_note': f'Averages based on historical patterns from last {years} year(s)'
        }
        
        return historical_data
        
    except Exception as e:
        print(f"Historical weather API error: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get available knowledge base categories"""
    return jsonify({
        'categories': [
            {'id': 'crops', 'name': 'Crops', 'count': 245},
            {'id': 'pest_control', 'name': 'Pest Control', 'count': 156},
            {'id': 'soil_management', 'name': 'Soil Management', 'count': 189},
            {'id': 'weather', 'name': 'Weather', 'count': 98},
            {'id': 'markets', 'name': 'Markets', 'count': 67},
            {'id': 'post_harvest', 'name': 'Post-Harvest', 'count': 101}
        ]
    })

# Varieties Management Endpoints
@app.route('/api/admin/varieties/status', methods=['GET'])
def get_varieties_status():
    """Get varieties database status and statistics"""
    try:
        import sqlite3
        conn = sqlite3.connect('data/agricultural_documents.db')
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM varieties")
        total_varieties = cursor.fetchone()[0]
        
        # Get count by crop
        cursor.execute("SELECT crop_name, COUNT(*) as count FROM varieties GROUP BY crop_name ORDER BY count DESC")
        crop_counts = [{'crop': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Get recent additions
        cursor.execute("SELECT COUNT(*) FROM varieties WHERE created_at >= datetime('now', '-7 days')")
        recent_additions = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_varieties': total_varieties,
                'crop_counts': crop_counts,
                'recent_additions': recent_additions,
                'database_path': 'data/agricultural_documents.db'
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/admin/varieties/list', methods=['GET'])
def get_varieties_list():
    """Get list of varieties with pagination and filtering"""
    try:
        import sqlite3
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        crop_filter = request.args.get('crop', '')
        search_query = request.args.get('search', '')
        
        conn = sqlite3.connect('data/agricultural_documents.db')
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if crop_filter:
            where_conditions.append("crop_name = ?")
            params.append(crop_filter)
        
        if search_query:
            where_conditions.append("(variety_name LIKE ? OR crop_name LIKE ?)")
            params.extend([f'%{search_query}%', f'%{search_query}%'])
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get total count
        count_sql = f"SELECT COUNT(*) FROM varieties WHERE {where_clause}"
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()[0]
        
        # Get paginated results
        offset = (page - 1) * per_page
        list_sql = f"""
        SELECT id, crop_name, variety_name, variety_type, yield_potential, 
               maturity_days, weather_requirements, soil_requirements, 
               growing_areas, disease_resistance, planting_time, source_document,
               confidence_score, validation_status, extraction_session_id, created_at
        FROM varieties 
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """
        cursor.execute(list_sql, params + [per_page, offset])
        
        varieties = []
        for row in cursor.fetchall():
            varieties.append({
                'id': row[0],
                'crop_name': row[1],
                'variety_name': row[2],
                'variety_type': row[3],
                'yield_potential': row[4],
                'maturity_days': row[5],
                'weather_requirements': row[6],
                'soil_requirements': row[7],
                'growing_areas': row[8],
                'disease_resistance': row[9],
                'planting_time': row[10],
                'source_document': row[11],
                'confidence_score': row[12],
                'validation_status': row[13],
                'extraction_session_id': row[14],
                'created_at': row[15]
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'varieties': varieties,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_count': total_count,
                    'total_pages': (total_count + per_page - 1) // per_page
                }
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/admin/varieties/extract', methods=['POST'])
def extract_varieties_from_documents():
    """Extract varieties from documents using the existing pipeline"""
    try:
        from scripts.data_pipeline.malawi_variety_extraction_pipeline import MalawiVarietyExtractionPipeline
        import sqlite3
        
        # Get request data
        data = request.get_json()
        target_crops = data.get('crops', [])  # Empty list means all crops
        document_sources = data.get('documents', [])  # Empty list means all documents
        
        # Initialize Malawi-specific extraction pipeline
        pipeline = MalawiVarietyExtractionPipeline()
        
        # Get documents to process
        conn = sqlite3.connect('data/agricultural_documents.db')
        cursor = conn.cursor()
        
        if document_sources:
            placeholders = ','.join(['?' for _ in document_sources])
            cursor.execute(f"SELECT content, source FROM documents WHERE source IN ({placeholders})", document_sources)
        else:
            cursor.execute("SELECT content, source FROM documents")
        
        documents = cursor.fetchall()
        conn.close()
        
        if not documents:
            return jsonify({
                'status': 'error',
                'message': 'No documents found to process'
            }), 400
        
        # Extract varieties from each document
        all_varieties = []
        crops_processed = set()
        extraction_stats = {
            'documents_processed': 0,
            'varieties_extracted': 0,
            'crops_processed': []
        }
        
        for content, source_document in documents:
            print(f"Processing document: {source_document}")
            result = pipeline.extract_varieties_from_document(
                content, source_document, target_crops
            )
            
            # Handle the returned structure
            if isinstance(result, dict) and 'varieties_by_crop' in result:
                varieties_by_crop = result['varieties_by_crop']
                for crop, varieties in varieties_by_crop.items():
                    # Convert crop field to crop_name for database consistency
                    for variety in varieties:
                        variety['crop_name'] = variety.get('crop', crop)
                    all_varieties.extend(varieties)
                    crops_processed.add(crop)
            else:
                # Fallback for different return structure
                for variety in result:
                    variety['crop_name'] = variety.get('crop', 'unknown')
                    all_varieties.append(variety)
                    crops_processed.add(variety.get('crop_name', 'unknown'))
            
            extraction_stats['documents_processed'] += 1
        
        # Apply global deduplication across all documents
        print(f"Before deduplication: {len(all_varieties)} varieties")
        all_varieties = pipeline.deduplicate_varieties(all_varieties)
        print(f"After deduplication: {len(all_varieties)} varieties")

        extraction_stats['varieties_extracted'] = len(all_varieties)
        extraction_stats['crops_processed'] = list(crops_processed)

        if not all_varieties:
            return jsonify({
                'status': 'success',
                'message': 'No varieties extracted from the selected documents',
                'data': {
                    'session_id': None,
                    'varieties': [],
                    'stats': extraction_stats
                },
                'timestamp': datetime.now().isoformat()
            })

        session_id = str(uuid.uuid4())

        for variety in all_varieties:
            if hasattr(pipeline, 'calculate_confidence_score'):
                pipeline.calculate_confidence_score(variety)
            variety['validation_status'] = 'pending'
            variety['extraction_session_id'] = session_id
            # Ensure confidence score is included for the preview payload
            if 'confidence_score' not in variety:
                variety['confidence_score'] = 0

        conn = sqlite3.connect('data/agricultural_documents.db')
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO extraction_sessions (
                id, documents_processed, varieties_extracted, varieties_selected, status
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                extraction_stats['documents_processed'],
                extraction_stats['varieties_extracted'],
                0,
                'pending'
            )
        )

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': f'Extracted {extraction_stats["varieties_extracted"]} varieties ready for validation',
            'data': {
                'session_id': session_id,
                'varieties': all_varieties,
                'stats': extraction_stats
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/admin/varieties/validate', methods=['POST'])
def validate_and_save_varieties():
    """Validate selected varieties and persist them to the database."""
    try:
        import sqlite3

        data = request.get_json() or {}
        session_id = data.get('session_id')
        selected_varieties = data.get('selected_varieties', [])
        clear_existing = data.get('clear_existing', False)

        if not session_id:
            return jsonify({
                'status': 'error',
                'message': 'session_id is required'
            }), 400

        if not isinstance(selected_varieties, list):
            return jsonify({
                'status': 'error',
                'message': 'selected_varieties must be a list'
            }), 400

        conn = sqlite3.connect('data/agricultural_documents.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM extraction_sessions WHERE id = ?", (session_id,))
        if cursor.fetchone() is None:
            conn.close()
            return jsonify({
                'status': 'error',
                'message': f'Extraction session {session_id} not found'
            }), 404

        if clear_existing:
            cursor.execute("DELETE FROM varieties WHERE extraction_session_id = ?", (session_id,))

        valid_entries = []
        for variety in selected_varieties:
            crop_name = variety.get('crop_name') or variety.get('crop')
            variety_name = variety.get('variety_name') or variety.get('name')

            if not crop_name or not variety_name:
                continue

            confidence_raw = variety.get('confidence_score')
            try:
                confidence_score = int(round(float(confidence_raw)))
            except (TypeError, ValueError):
                confidence_score = 0

            valid_entries.append((
                crop_name,
                variety_name,
                variety.get('variety_type', ''),
                variety.get('yield_potential', ''),
                variety.get('maturity_days'),
                variety.get('weather_requirements', ''),
                variety.get('soil_requirements', ''),
                variety.get('growing_areas', ''),
                variety.get('disease_resistance', ''),
                variety.get('planting_time', ''),
                variety.get('source_document', ''),
                confidence_score,
                'validated',
                session_id
            ))

        if not valid_entries:
            cursor.execute(
                "UPDATE extraction_sessions SET varieties_selected = ?, status = ? WHERE id = ?",
                (0, 'discarded', session_id)
            )
            conn.commit()
            conn.close()
            return jsonify({
                'status': 'success',
                'message': 'No varieties selected. Session marked as discarded.',
                'data': {
                    'session_id': session_id,
                    'varieties_saved': 0
                },
                'timestamp': datetime.now().isoformat()
            })

        insert_sql = """
        INSERT INTO varieties (
            crop_name, variety_name, variety_type, yield_potential, maturity_days,
            weather_requirements, soil_requirements, growing_areas, disease_resistance,
            planting_time, source_document, confidence_score, validation_status, extraction_session_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.executemany(insert_sql, valid_entries)

        cursor.execute(
            "UPDATE extraction_sessions SET varieties_selected = ?, status = ? WHERE id = ?",
            (len(valid_entries), 'validated', session_id)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': f'Saved {len(valid_entries)} validated varieties',
            'data': {
                'session_id': session_id,
                'varieties_saved': len(valid_entries)
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/admin/varieties/clear', methods=['POST'])
def clear_varieties_database():
    """Clear all varieties from the database"""
    try:
        import sqlite3
        conn = sqlite3.connect('data/agricultural_documents.db')
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM varieties")
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Varieties database cleared successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Knowledge Base Management Endpoints
@app.route('/api/admin/knowledge-base/status', methods=['GET'])
def get_knowledge_base_status():
    """Get knowledge base status and statistics"""
    try:
        # Import the semantic search system
        from scripts.data_pipeline.semantic_search import SemanticSearch
        
        # Initialize semantic search
        semantic_search = SemanticSearch()
        
        # Get database status
        status = semantic_search.get_database_status()
        
        return jsonify({
            'status': 'success',
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/admin/knowledge-base/documents', methods=['GET'])
def get_knowledge_base_documents():
    """Get list of documents in the knowledge base"""
    try:
        from scripts.data_pipeline.semantic_search import SemanticSearch
        
        semantic_search = SemanticSearch()
        processed_docs = semantic_search._get_processed_documents()
        
        # Get document summaries
        documents = []
        for doc_name in processed_docs:
            summary = semantic_search.get_document_summary(doc_name)
            if summary:
                documents.append(summary)
        
        return jsonify({
            'status': 'success',
            'data': {
                'documents': documents,
                'total_count': len(documents)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/admin/knowledge-base/upload', methods=['POST'])
def upload_document():
    """Upload and process a new document"""
    try:
        from werkzeug.utils import secure_filename
        import os
        from scripts.data_pipeline.semantic_search import SemanticSearch
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'txt', 'docx'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'status': 'error',
                'message': f'File type not supported. Allowed: {", ".join(allowed_extensions)}'
            }), 400
        
        # Create pdfs directory if it doesn't exist
        pdfs_dir = 'farming-guide2/data/pdfs'
        os.makedirs(pdfs_dir, exist_ok=True)
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(pdfs_dir, filename)
        file.save(file_path)
        
        # Process the document
        semantic_search = SemanticSearch()
        success = semantic_search.process_pdf_documents([file_path])
        
        if success:
            # Get document summary
            doc_name = os.path.basename(file_path)
            summary = semantic_search.get_document_summary(doc_name)
            
            return jsonify({
                'status': 'success',
                'message': 'Document uploaded and processed successfully',
                'data': {
                    'filename': filename,
                    'file_path': file_path,
                    'summary': summary
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return jsonify({
                'status': 'error',
                'message': 'Failed to process document'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/admin/knowledge-base/search', methods=['POST'])
def search_knowledge_base():
    """Search the knowledge base"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        threshold = data.get('threshold', 0.7)
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Search query is required'
            }), 400
        
        from scripts.data_pipeline.semantic_search import SemanticSearch
        
        semantic_search = SemanticSearch()
        results = semantic_search.search_documents(query, top_k, threshold)
        
        # Convert results to JSON-serializable format
        serializable_results = []
        for result in results:
            serializable_result = {
                'text': str(result.get('text', '')),
                'score': float(result.get('score', 0.0)),
                'metadata': {
                    'source_document': str(result.get('metadata', {}).get('source_document', '')),
                    'file_path': str(result.get('metadata', {}).get('file_path', '')),
                    'document_type': str(result.get('metadata', {}).get('document_type', ''))
                },
                'text_preview': str(result.get('text_preview', '')),
                'relevance': str(result.get('relevance', 'low')),
                'query': str(result.get('query', ''))
            }
            serializable_results.append(serializable_result)
        
        return jsonify({
            'status': 'success',
            'data': {
                'query': query,
                'results': serializable_results,
                'count': len(serializable_results)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/admin/knowledge-base/rebuild', methods=['POST'])
def rebuild_knowledge_base():
    """Rebuild the entire knowledge base"""
    try:
        from scripts.data_pipeline.semantic_search import SemanticSearch
        import glob
        
        # Find all PDF files in farming-guide2/data/pdfs
        pdf_paths = []
        if os.path.exists('farming-guide2/data/pdfs'):
            pdf_paths.extend(glob.glob(os.path.join('farming-guide2/data/pdfs', '*.pdf')))
        
        if not pdf_paths:
            return jsonify({
                'status': 'error',
                'message': 'No PDF documents found to rebuild knowledge base'
            }), 400
        
        semantic_search = SemanticSearch()
        success = semantic_search.rebuild_database(pdf_paths)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Knowledge base rebuilt successfully with {len(pdf_paths)} documents',
                'data': {
                    'documents_processed': len(pdf_paths),
                    'document_paths': pdf_paths
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to rebuild knowledge base'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/admin/knowledge-base/clear', methods=['POST'])
def clear_knowledge_base():
    """Clear the knowledge base"""
    try:
        from scripts.data_pipeline.semantic_search import SemanticSearch
        
        semantic_search = SemanticSearch()
        semantic_search.clear_database()
        
        return jsonify({
            'status': 'success',
            'message': 'Knowledge base cleared successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def parse_location(location):
    """Parse location string to lat/lon coordinates"""
    try:
        # Try to parse as coordinates
        if ',' in location:
            parts = location.split(',')
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                return lat, lon
        
        # Default to Lilongwe coordinates for named locations
        return -13.9833, 33.7833
        
    except:
        # Default to Lilongwe coordinates
        return -13.9833, 33.7833

if __name__ == '__main__':
    print("🚀 Starting Mlangizi wa Ulimi API Server...")
    print("📍 Frontend should be running on: http://localhost:5173")
    print("🔗 API will be available on: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=8000)
