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
            # Use ASCII-friendly markers to avoid Windows console Unicode errors
            print(f"[OK] Loaded config from {config_path}")
            loaded_any = True
        else:
            print(f"[WARN] Config file not found: {config_path}")
    
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
    
    print("[INIT] Initializing backend components...")

    try:
        ensure_varieties_schema('data/agricultural_documents.db')
        print("[OK] Varieties schema verified")
    except FileNotFoundError as e:
        print(f"[WARN] Varieties schema check skipped: {e}")
    except Exception as e:
        print(f"[WARN] Varieties schema verification failed: {e}")

    # Initialize weather API
    try:
        api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
        if api_key:
            from weather_engine.weather_api import WeatherAPI
            weather_api = WeatherAPI()
            print(f"[OK] Weather API initialized with real API key: {api_key[:8]}...")
        else:
            print("[WARN] OPENWEATHERMAP_API_KEY not found in environment, using mock data")
            weather_api = None
    except Exception as e:
        print(f"[WARN] Weather API initialization failed: {e}")
        weather_api = None
    
    # Initialize SQLite recommendation engine (same as bot)
    try:
        from crop_advisor.sqlite_based_recommendation_engine import SQLiteBasedRecommendationEngine
        # Use the correct database path
        db_path = os.path.join(os.path.dirname(__file__), 'data', 'agricultural_documents.db')
        sqlite_recommendation_engine = SQLiteBasedRecommendationEngine(db_path)
        print("[OK] SQLite recommendation engine initialized")
    except Exception as e:
        print(f"[WARN] SQLite recommendation engine initialization failed: {e}")
        sqlite_recommendation_engine = None
    
    # Initialize seasonal advisor
    try:
        from crop_advisor.seasonal_advisor import SeasonalAdvisor
        seasonal_advisor = SeasonalAdvisor()
        print("[OK] Seasonal advisor initialized")
    except Exception as e:
        print(f"[WARN] Seasonal advisor initialization failed: {e}")
        seasonal_advisor = None
    
    # Initialize VarietiesHandler
    try:
        from handlers.varieties_handler import VarietiesHandler
        varieties_handler = VarietiesHandler()
        print("[OK] Varieties handler initialized")
    except Exception as e:
        print(f"[WARN] Varieties handler initialization failed: {e}")
        varieties_handler = None
    
    # For other components, keep using mock data to avoid other import issues
    print("[INFO] Other components using mock data for now")
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
            # Return error if weather API is not available - no mock data
            return jsonify({
                'error': 'Weather API is not available. Please check your API configuration.',
                'message': 'Real weather data cannot be fetched at this time.',
                'location': location,
                'timestamp': datetime.now().isoformat()
            }), 503
            
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
        # Return error instead of mock data
        return jsonify({
            'error': f'Failed to fetch weather data: {str(e)}',
            'message': 'Real weather data cannot be fetched at this time.',
            'location': location,
            'timestamp': datetime.now().isoformat()
        }), 500

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
        
        years_param = request.args.get('years')
        years_list_param = request.args.get('years_list')  # CSV of explicit years

        explicit_years = None
        if years_list_param:
            try:
                explicit_years = [int(y) for y in years_list_param.split(',') if y.strip().isdigit()]
                # Deduplicate and clamp to at most 10 entries
                explicit_years = sorted(list({y for y in explicit_years}), reverse=True)[:10]
            except Exception:
                explicit_years = None

        years = int(years_param or (len(explicit_years) if explicit_years else 5))
        years = min(max(years, 1), 10)  # Ensure 1-10 range when not explicit
        
        # Parse location (could be coordinates or name)
        lat, lon = parse_location(location)
        
        # Always try to get real historical data first (uses free Open-Meteo API)
        print("Attempting to fetch real historical weather data...")
        historical_data = get_real_historical_weather(lat, lon, years, explicit_years)
        if historical_data:
            print("✅ Using REAL historical weather data")
            return jsonify(historical_data)
        else:
            print("❌ Real data not available - returning error instead of mock data")
            return jsonify({
                'error': 'Real historical weather data is not available for this location and time period.',
                'message': 'Please check your internet connection and API configuration.',
                'coordinates': {'lat': lat, 'lon': lon},
                'years_requested': years,
                'timestamp': datetime.now().isoformat()
            }), 503
        
        # NO FALLBACK TO MOCK DATA - Real data only
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/<location>/agricultural-recommendations', methods=['GET'])
def get_agricultural_recommendations(location):
    """Get crop recommendations based on historical weather patterns"""
    try:
        from scripts.crop_advisor.seasonal_analyzer import SeasonalAnalyzer
        from scripts.crop_advisor.crop_matcher import CropMatcher
        
        years_param = request.args.get('years')
        years_list_param = request.args.get('years_list')
        
        # Parse years parameter (same logic as historical weather)
        explicit_years = None
        if years_list_param:
            try:
                explicit_years = [int(y) for y in years_list_param.split(',') if y.strip().isdigit()]
                explicit_years = sorted(list({y for y in explicit_years}), reverse=True)[:10]
            except Exception:
                explicit_years = None
        
        years = int(years_param or (len(explicit_years) if explicit_years else 3))
        years = min(max(years, 1), 10)
        
        # Parse location
        lat, lon = parse_location(location)
        
        # Get historical weather data first
        print(f"Fetching historical weather for agricultural recommendations: {lat}, {lon}")
        historical_data = get_real_historical_weather(lat, lon, years, explicit_years)
        
        if not historical_data:
            return jsonify({
                'error': 'Historical weather data not available',
                'message': 'Unable to generate crop recommendations without weather data'
            }), 503
        
        # Analyze weather patterns
        analyzer = SeasonalAnalyzer()
        seasonal_analysis = analyzer.analyze_weather_patterns(historical_data)
        
        # Match crops to patterns
        matcher = CropMatcher()
        recommendations = matcher.get_agricultural_recommendations(seasonal_analysis)
        
        print(f"✅ Generated agricultural recommendations for {lat}, {lon}")
        print(f"   Wet season crops: {len(recommendations['wet_season']['suitable_crops'])}")
        print(f"   Dry season crops: {len(recommendations['dry_season']['suitable_crops'])}")
        
        return jsonify({
            'years_analyzed': historical_data.get('years_analyzed', years),
            'agricultural_implications': recommendations,
            'coordinates': {'lat': lat, 'lon': lon},
            'analysis_date': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error generating agricultural recommendations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def get_historical_rainfall_data(lat, lon, start_date, end_date):
    """
    Get real historical rainfall data from Open-Meteo API
    This provides actual rainfall measurements for the location and date range
    """
    import requests
    from datetime import datetime
    
    try:
        # Simple on-disk cache to avoid repeated archive calls for same window
        import json as _json
        import time as _time
        cache_path = os.path.join('data', 'weather_cache.json')
        os.makedirs('data', exist_ok=True)
        cache = {}
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cache = _json.load(f) or {}
            except Exception:
                cache = {}

        cache_key = f"openmeteo:{lat:.4f},{lon:.4f}:{start_date.strftime('%Y-%m-%d')}:{end_date.strftime('%Y-%m-%d')}"
        cached = cache.get(cache_key)
        # TTL 24h for safety; historical ranges rarely change
        if cached and (int(_time.time()) - int(cached.get('ts', 0)) < 24 * 3600):
            return cached.get('daily')
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
                # Write to cache
                cache[cache_key] = {'ts': int(_time.time()), 'daily': data['daily']}
                try:
                    with open(cache_path, 'w') as f:
                        _json.dump(cache, f)
                except Exception:
                    pass
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

def process_real_rainfall_data(rainfall_data, lat, lon, years, start_date, current_date, allowed_years=None):
    """
    Process real rainfall data from Open-Meteo API into our standard format
    """
    from collections import defaultdict
    from datetime import datetime
    
    months = ['January', 'February', 'March', 'April', 'May', 'June',
             'July', 'August', 'September', 'October', 'November', 'December']
    wet_season_months = ['November', 'December', 'January', 'February', 'March']
    
    # Group data by month (across all years) and by year->month
    monthly_data = defaultdict(lambda: {'rainfall': [], 'temperature': []})
    yearly_data = {}
    per_year_monthly_totals = defaultdict(lambda: defaultdict(float))  # year -> month -> total_mm
    per_year_months_present = defaultdict(set)  # year -> set(month_index)
    
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
            daily_rain = rain_sums[i] or 0
            monthly_data[month_name]['rainfall'].append(daily_rain)
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
            # Accumulate per-year monthly totals and track month coverage
            per_year_monthly_totals[year][month_name] += float(daily_rain)
            per_year_months_present[year].add(date_obj.month)
    
    # Calculate monthly totals and averages
    monthly_averages = {}
    for month in months:
        if monthly_data[month]['rainfall']:
            # Sum all daily rainfall for the month (rain_sum is daily total, not average)
            total_monthly_rainfall = sum(monthly_data[month]['rainfall'])
            avg_temp = sum(monthly_data[month]['temperature']) / len(monthly_data[month]['temperature'])
            
            monthly_averages[month] = {
                'average_rainfall': round(total_monthly_rainfall, 1),
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
        all_rainfall = [r for month in months for r in monthly_data[month]['rainfall']]
        all_temps = [t for month in months for t in monthly_data[month]['temperature']]
        annual_rainfall = sum(all_rainfall) if all_rainfall else 0
        annual_temp = sum(all_temps) / len(all_temps) if all_temps else 25
        
        # Find wettest and driest months
        month_rainfall = {month: sum(monthly_data[month]['rainfall']) 
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
                'wet_season_total': round(sum(sum(monthly_data[month]['rainfall']) for month in wet_season_months if monthly_data[month]['rainfall'])),
                'dry_season_total': round(sum(sum(monthly_data[month]['rainfall']) for month in months if month not in wet_season_months and monthly_data[month]['rainfall']))
            }
        })
    
    # Build per-year breakdown with monthly totals and annual sums (for averaging)
    per_year_list = []
    candidate_years = sorted(per_year_monthly_totals.keys(), reverse=True)
    if allowed_years:
        candidate_years = [y for y in candidate_years if y in set(allowed_years)]
    for year in candidate_years:
        monthly_totals_map = {}
        for m in months:
            monthly_totals_map[m] = round(per_year_monthly_totals[year].get(m, 0.0), 1)
        annual_total = round(sum(monthly_totals_map.values()), 1)
        months_covered = len(per_year_months_present.get(year, set()))
        coverage = 'full' if months_covered == 12 else 'partial'
        per_year_list.append({
            'year': year,
            'monthly': monthly_totals_map,
            'annual_rainfall': annual_total,
            'months_covered': months_covered,
            'coverage': coverage,
        })

    # Compute multi-year averages when multiple years requested
    multi_year = None
    if per_year_list and len(per_year_list) >= 1:
        annuals = [y['annual_rainfall'] for y in per_year_list]
        # monthly mean across years per month
        monthly_avg_map = {}
        for m in months:
            vals = [y['monthly'].get(m, 0.0) for y in per_year_list]
            monthly_avg_map[m] = round((sum(vals) / len(vals)) if vals else 0.0, 1)
        multi_year = {
            'annual_average': round((sum(annuals) / len(annuals)) if annuals else 0.0, 1),
            'monthly_average': monthly_avg_map,
        }

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
        'years_analyzed': len(per_year_list) if allowed_years else years,
        'period_start': start_date.strftime('%Y-%m-%d'),
        'period_end': current_date.strftime('%Y-%m-%d'),
        'monthly_averages': monthly_averages,
        'yearly_breakdown': yearly_breakdown if years > 1 else None,
        # New additive fields for multi-year analysis and UI
        'per_year': per_year_list,
        'multi_year': multi_year,
        'climate_summary': {
            'total_annual_rainfall': round(total_rainfall, 1),
            'wettest_month': wettest_month,
            'driest_month': driest_month,
            'climate_trend': f'Based on REAL historical rainfall data for last {years} year(s)',
            'drought_risk': drought_risk,
            'analysis_period': f'{start_date.strftime("%B %Y")} to {current_date.strftime("%B %Y")}',
            'data_note': 'Rainfall & temperature from Open-Meteo Archive (ERA5/ERA5-Land).'
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
        'data_source': 'Open-Meteo (ERA5/ERA5-Land)'
    }

def get_real_historical_weather(lat, lon, years, explicit_years=None):
    """Get real historical weather data using Open-Meteo Archive only.

    Returns None if Open-Meteo is unavailable; the caller will 503 (no synthetic fallback).
    """
    try:
        from datetime import datetime, timedelta

        print(f"Fetching REAL historical weather data for {lat}, {lon} (last {years} years)")

        current_date = datetime.now()
        # If explicit years are provided, fetch each year separately to avoid gaps and partial windows
        if explicit_years:
            year_list = sorted(list({int(y) for y in explicit_years}), reverse=True)[:10]
            print(f"[OBSERVABILITY] Explicit years requested: {year_list}")
            aggregate = {'time': [], 'rain_sum': [], 'temperature_2m_mean': []}
            failed_years = []
            for y in year_list:
                y_start = datetime(y, 1, 1)
                y_end = datetime(y, 12, 31)
                if y == current_date.year:
                    y_end = current_date
                print(f"[OBSERVABILITY] Fetching year {y}: {y_start.strftime('%Y-%m-%d')} to {y_end.strftime('%Y-%m-%d')}")
                y_data = get_historical_rainfall_data(lat, lon, y_start, y_end)
                if not y_data:
                    print(f"[WARN] Year {y} fetch failed")
                    failed_years.append(y)
                    continue
                # Concatenate daily arrays
                aggregate['time'].extend(y_data.get('time', []))
                aggregate['rain_sum'].extend(y_data.get('rain_sum', []))
                aggregate['temperature_2m_mean'].extend(y_data.get('temperature_2m_mean', []))

            if not aggregate['time']:
                return None

            start_date = datetime(min(year_list), 1, 1)
            end_date = current_date if max(year_list) == current_date.year else datetime(max(year_list), 12, 31)
            print(f"[OBSERVABILITY] Historical period (explicit): {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            print(f"[OBSERVABILITY] Failed years: {failed_years if failed_years else 'None'}")
            print("[OK] Successfully retrieved per-year rainfall data from Open-Meteo!")
            result = process_real_rainfall_data(aggregate, lat, lon, len(year_list), start_date, end_date, year_list)
            if failed_years:
                result['meta'] = {'failed_years': failed_years}
            
            # Log clean summary of results
            print("\n" + "="*80)
            print(f"[RAINFALL DATA SUMMARY] Location: {lat}, {lon}")
            print("="*80)
            if result.get('per_year'):
                for yr in result['per_year']:
                    coverage_marker = "[PARTIAL]" if yr.get('coverage') == 'partial' else "[FULL]"
                    print(f"  Year {yr['year']} {coverage_marker}: {yr['annual_rainfall']} mm ({yr.get('months_covered', 0)}/12 months)")
            if result.get('multi_year'):
                print(f"\n  Multi-Year Average: {result['multi_year']['annual_average']} mm")
            print(f"  Period: {result.get('period_start')} to {result.get('period_end')}")
            print(f"  Source: Open-Meteo Archive (ERA5/ERA5-Land)")
            print("="*80 + "\n")
            
            return result
        else:
            start_date = current_date - timedelta(days=365 * years)
            end_date = current_date

            print(f"Historical period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            print("Fetching real historical rainfall data from Open-Meteo API...")

            rainfall_data = get_historical_rainfall_data(lat, lon, start_date, end_date)
            if not rainfall_data:
                return None

            print("[OK] Successfully retrieved real rainfall data from Open-Meteo!")
            result = process_real_rainfall_data(rainfall_data, lat, lon, years, start_date, end_date)
            
            # Log clean summary of results
            print("\n" + "="*80)
            print(f"[RAINFALL DATA SUMMARY] Location: {lat}, {lon}")
            print("="*80)
            if result.get('per_year'):
                for yr in result['per_year']:
                    coverage_marker = "[PARTIAL]" if yr.get('coverage') == 'partial' else "[FULL]"
                    print(f"  Year {yr['year']} {coverage_marker}: {yr['annual_rainfall']} mm ({yr.get('months_covered', 0)}/12 months)")
            if result.get('multi_year'):
                print(f"\n  Multi-Year Average: {result['multi_year']['annual_average']} mm")
            print(f"  Period: {result.get('period_start')} to {result.get('period_end')}")
            print(f"  Source: Open-Meteo Archive (ERA5/ERA5-Land)")
            print("="*80 + "\n")
            
            return result

    except Exception as e:
        print(f"Historical weather API error: {e}")
        return None

@app.route('/api/_debug/openmeteo-sum', methods=['GET'])
def debug_openmeteo_sum():
    """Debug endpoint: fetch year's rainfall from Open-Meteo and return raw sum for verification"""
    try:
        from datetime import datetime
        lat = float(request.args.get('lat', -13.9833))
        lon = float(request.args.get('lon', 33.7833))
        year = int(request.args.get('year', datetime.now().year))
        
        y_start = datetime(year, 1, 1)
        y_end = datetime(year, 12, 31)
        if year == datetime.now().year:
            y_end = datetime.now()
        
        rainfall_data = get_historical_rainfall_data(lat, lon, y_start, y_end)
        if not rainfall_data:
            return jsonify({'error': 'No data from Open-Meteo'}), 503
        
        rain_sums = rainfall_data.get('rain_sum', [])
        total = round(sum(r or 0 for r in rain_sums), 1)
        
        return jsonify({
            'year': year,
            'lat': lat,
            'lon': lon,
            'daily_count': len(rain_sums),
            'total_rainfall_mm': total,
            'source': 'Open-Meteo Archive (ERA5)',
            'note': 'Dev-only debug endpoint for data integrity checks'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    print("[START] Starting Mlangizi wa Ulimi API Server...")
    print("[INFO] Frontend should be running on: http://localhost:5173")
    print("[INFO] API will be available on: http://localhost:8000")
    print("[INFO] API Documentation: http://localhost:8000/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=8000)
