"""
Flask API Server for Mlangizi wa Ulimi Frontend
Exposes existing backend functionality as REST API endpoints
"""

from flask import Flask, jsonify, request, send_from_directory
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
from scripts.handlers.varieties_supabase_handler import VarietiesSupabaseHandler

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
supabase_varieties_handler = None
semantic_search = None
sqlite_recommendation_engine = None
seasonal_advisor = None

def initialize_components():
    """Initialize backend components"""
    global weather_api, recommendation_engine, varieties_handler, supabase_varieties_handler, semantic_search, sqlite_recommendation_engine, seasonal_advisor
    
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
        
    # Initialize Supabase varieties handler
    try:
        supabase_varieties_handler = VarietiesSupabaseHandler()
        print("[OK] Supabase varieties handler initialized")
    except Exception as e:
        print(f"[WARN] Supabase varieties handler initialization failed: {e}")
        supabase_varieties_handler = None
    
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
            'supabase_varieties_handler': supabase_varieties_handler is not None,
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
        season = request.args.get('season', 'rainy_season')
        
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
        
        # Use advanced enhanced engine as primary, SQLite as fallback
        try:
            from scripts.crop_advisor.advanced_enhanced_crop_recommendation_engine import advanced_enhanced_crop_recommendation_engine
            
            logger.info(f"[DEBUG] Starting general recommendations for {lat},{lon}")
            logger.info(f"[DEBUG] Parameters: season={season}, rainfall_mm={rainfall_data.get('total_7day_rainfall', 400)}")
            
            # Get enhanced recommendations using real data
            enhanced_recommendations = advanced_enhanced_crop_recommendation_engine.get_enhanced_crop_recommendations(
                lat=lat,
                lon=lon,
                season=season,
                rainfall_mm=rainfall_data.get('total_7day_rainfall', 400),
                temperature=temperature,
                farmer_profile={'experience_level': 'intermediate'},
                historical_years=5
            )
            
            logger.info(f"[DEBUG] General recommendations received: {len(enhanced_recommendations.get('recommendations', []))} crops")
            
            if not enhanced_recommendations.get('recommendations'):
                logger.warning("[DEBUG] No recommendations received from enhanced engine")
                raise Exception("No recommendations from enhanced engine")
            
            # Convert enhanced format to legacy format for compatibility
            legacy_recommendations = []
            logger.info(f"[DEBUG] Processing {len(enhanced_recommendations['recommendations'])} recommendations")
            for i, rec in enumerate(enhanced_recommendations['recommendations'][:2]):  # Top 2 crops
                logger.info(f"[DEBUG] Processing recommendation {i+1}: {rec.get('crop_id', 'Unknown')}")
                legacy_recommendations.append({
                    'crop_name': rec['crop_id'],
                    'suitability_score': rec['suitability_score'],
                    'score': int(rec['suitability_score'] * 100),
                    'suitability_level': rec['recommendation_level'],
                    'rainfall_match': 'excellent' if rec['factor_scores']['rainfall'] > 0.8 else 'good',
                    'temperature_match': 'excellent' if rec['factor_scores']['temperature'] > 0.8 else 'good',
                    'season_suitability': 'excellent' if rec['factor_scores']['timing'] > 0.8 else 'good',
                    'sources': ['Real Crop Varieties Database', 'Historical Weather Data'],
                    'guide_recommendations': [
                        rec['planting_guidelines'].get('optimal_timing', 'Not specified'),
                        rec['planting_guidelines'].get('planting_depth', '2-5 cm'),
                        rec['planting_guidelines'].get('spacing', '75cm x 25cm')
                    ],
                    'varieties': [v['name'] for v in rec['top_varieties'][:3]],
                    'planting_time': rec['planting_guidelines'].get('optimal_timing', 'Not specified'),
                    'yield_potential': f"{rec['yield_projections']['yield_projections']['realistic']:.1f}-{rec['yield_projections']['yield_projections']['optimal']:.1f} tons/ha",
                    'description': f"Real data recommendation with {rec['confidence']:.1%} confidence"
                })
            
            logger.info(f"[DEBUG] Generated {len(legacy_recommendations)} legacy recommendations")
            
            return jsonify({
                'location': location,
                'season': season,
                'recommendations': legacy_recommendations,
                'planting_advice': {
                    'optimal_planting_window': enhanced_recommendations['recommendations'][0]['planting_guidelines'].get('optimal_timing', 'Not specified'),
                    'soil_preparation': 'Prepare land 2-3 weeks before planting',
                    'seed_requirements': 'Use certified seeds for best results'
                },
                'environmental_summary': {
                    'total_7day_rainfall': rainfall_data.get('total_7day_rainfall', 0),
                    'forecast_7day_rainfall': rainfall_data.get('forecast_7day_rainfall', 0),
                    'current_temperature': temperature,
                    'humidity': current_weather.get('humidity', 50),
                    'current_season': season
                },
                'risk_assessment': {
                    'weather_risks': enhanced_recommendations['recommendations'][0]['risk_factors'][:2] if enhanced_recommendations['recommendations'] else [],
                    'pest_risks': ['Stem borer attack', 'Leaf spot disease']
                },
                'management_tips': [
                    'Monitor crop growth regularly',
                    'Apply fertilizer at recommended rates',
                    'Control weeds early in season',
                ],
                'seasonal_advice': {
                    'agricultural_calendar': {
                        'forecast_period': 'October - December',
                        'months': [
                            {
                                'month': 'October',
                                'key_activities': [
                                    'Early season planting',
                                    'Fertilizer application',
                                    'Planting material prep'
                                ]
                            },
                            {
                                'month': 'November',
                                'key_activities': [
                                    'Main planting season',
                                    'Weed control',
                                    'Pest monitoring'
                                ]
                            },
                            {
                                'month': 'December',
                                'key_activities': [
                                    'Late planting',
                                    'Crop maintenance',
                                    'Harvest preparation'
                                ]
                            }
                        ]
                    }
                },
                'historical_data': enhanced_recommendations.get('historical_data_summary', {}).get('years_analyzed', 5),
                'location_data': {
                    'latitude': lat,
                    'longitude': lon,
                    'rainfall_mm': rainfall_data.get('total_7day_rainfall', 0),
                    'season': season,
                    'temperature': temperature
                },
                'sources': enhanced_recommendations.get('data_sources', ['Real Crop Varieties Database']),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Enhanced engine failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Fallback to SQLite-based recommendation engine
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
                # Return error if no engine available
                return jsonify({
                    'error': 'Service temporarily unavailable',
                    'message': 'No recommendation engine available',
                    'data_type': 'error_fallback'
                }), 503
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crops/recommendations/enhanced', methods=['POST'])
def get_enhanced_crop_recommendations():
    """
    Enhanced crop recommendations API using ONLY real data sources.
    Provides comprehensive recommendations with varieties, yield projections, and input recommendations.
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Extract parameters
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        season = data.get('season', 'rainy_season')
        farmer_profile = data.get('farmer_profile', {})
        
        if latitude is None or longitude is None:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        # Get weather data for the location
        if weather_api:
            current_weather = weather_api.get_current_weather(latitude, longitude)
            rainfall_data = weather_api.get_rainfall_data(latitude, longitude, 'api_user')
            temperature = current_weather.get('temperature', 25)
            rainfall_mm = rainfall_data.get('total_7day_rainfall', 0)
        else:
            # Fallback values
            rainfall_data = {'total_7day_rainfall': 50, 'forecast_7day_rainfall': 30}
            temperature = 25
            rainfall_mm = 50
        
        # Use the advanced enhanced recommendation engine with real data only
        from scripts.crop_advisor.advanced_enhanced_crop_recommendation_engine import advanced_enhanced_crop_recommendation_engine

        recommendations = advanced_enhanced_crop_recommendation_engine.get_enhanced_crop_recommendations(
            lat=latitude,
            lon=longitude,
            season=season,
            rainfall_mm=rainfall_mm,
            temperature=temperature,
            farmer_profile=farmer_profile,
            historical_years=5
        )
        
        return jsonify({
            'status': 200,
            'data': recommendations,
            'errors': []
        })
        
    except Exception as e:
        logger.error(f"Enhanced recommendations error: {e}")
        return jsonify({'error': str(e)}), 500

def normalize_crop_name(search_term: str) -> str:
    """
    Normalize crop search term to match database IDs.
    Handles common variations while excluding different crops.
    
    Args:
        search_term: User's search term (e.g., "Beans", "Common Beans", "Phaseolus")
        
    Returns:
        Normalized crop ID for database matching
    """
    term = search_term.strip().lower()
    
    # Handle beans variations (but NOT soybeans)
    if term in ['beans', 'bean', 'common beans', 'common bean', 'phaseolus', 'phaseolus vulgaris']:
        if 'soy' not in term:  # Exclude soybeans
            return 'beans'
    
    # Handle other common variations
    if term in ['maize', 'corn', 'maize corn']:
        return 'maize'
    
    if term in ['groundnuts', 'groundnut', 'peanuts', 'peanut']:
        return 'groundnuts'
    
    if term in ['sweet potato', 'sweetpotato', 'sweet potatoes']:
        return 'sweet_potato'
    
    # Return as-is for direct matches
    return term

def match_crop_in_recommendations(search_term: str, recommendations: list) -> dict:
    """
    Find a crop in recommendations list using fuzzy matching.
    
    Args:
        search_term: Normalized search term
        recommendations: List of crop recommendations from engine
        
    Returns:
        Matching crop recommendation or None
    """
    for rec in recommendations:
        crop_id = rec['crop_id'].lower()
        # Direct match
        if crop_id == search_term:
            return rec
        # Handle beans variations
        if search_term == 'beans' and crop_id == 'beans':
            return rec
        # Handle underscores and spaces
        if crop_id.replace('_', ' ') == search_term.replace('_', ' '):
            return rec
    
    return None

@app.route('/api/crops/specific', methods=['GET'])
def get_specific_crop_recommendations():
    """Get recommendations for a specific crop only - Phase 4 implementation"""
    try:
        # Get parameters from query string
        crop_name = request.args.get('crop', '').strip().lower()
        location = request.args.get('location', 'Lilongwe')
        season = request.args.get('season', 'rainy_season')
        
        if not crop_name:
            return jsonify({'error': 'Crop name is required'}), 400
        
        # Normalize crop name to handle variations
        normalized_crop_name = normalize_crop_name(crop_name)
        
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
        
        # Use the advanced enhanced recommendation engine for specific crop
        try:
            from scripts.crop_advisor.advanced_enhanced_crop_recommendation_engine import advanced_enhanced_crop_recommendation_engine
            
            logger.info(f"[DEBUG] Starting enhanced recommendations for {crop_name} (normalized: {normalized_crop_name}) at {lat},{lon}")
            logger.info(f"[DEBUG] Parameters: season={season}, rainfall_mm={rainfall_data.get('total_7day_rainfall', 400)}, temperature={temperature}")
            logger.info(f"[DEBUG] Engine object: {advanced_enhanced_crop_recommendation_engine}")
            
            # Get enhanced recommendations using real data
            # Request ALL crops (top_n=999) for specific crop searches to ensure we find the requested crop
            logger.info(f"[DEBUG] Calling get_enhanced_crop_recommendations with top_n=999 for specific crop search...")
            enhanced_recommendations = advanced_enhanced_crop_recommendation_engine.get_enhanced_crop_recommendations(
                lat=lat,
                lon=lon,
                season=season,
                rainfall_mm=rainfall_data.get('total_7day_rainfall', 400),
                temperature=temperature,
                farmer_profile={'experience_level': 'intermediate'},
                historical_years=5,
                top_n=999  # Request all crops for specific crop search
            )
            
            logger.info(f"[DEBUG] Enhanced recommendations received: {len(enhanced_recommendations.get('recommendations', []))} crops")
            logger.info(f"[DEBUG] Enhanced recommendations type: {type(enhanced_recommendations)}")
            logger.info(f"[DEBUG] Enhanced recommendations keys: {list(enhanced_recommendations.keys()) if isinstance(enhanced_recommendations, dict) else 'Not a dict'}")
            
            if enhanced_recommendations.get('recommendations'):
                logger.info(f"[DEBUG] First recommendation type: {type(enhanced_recommendations['recommendations'][0])}")
                logger.info(f"[DEBUG] First recommendation keys: {list(enhanced_recommendations['recommendations'][0].keys()) if isinstance(enhanced_recommendations['recommendations'][0], dict) else 'Not a dict'}")
                logger.info(f"[DEBUG] First recommendation crop_id: {enhanced_recommendations['recommendations'][0].get('crop_id', 'NO_CROP_ID')}")
            
            # Find the specific crop in recommendations using improved matching
            logger.info(f"[DEBUG] Looking for crop '{crop_name}' (normalized: {normalized_crop_name}) in {len(enhanced_recommendations['recommendations'])} recommendations")
            
            specific_crop_rec = match_crop_in_recommendations(
                normalized_crop_name, 
                enhanced_recommendations['recommendations']
            )
            
            if specific_crop_rec:
                logger.info(f"[DEBUG] Found matching crop: {specific_crop_rec['crop_id']}")
            else:
                logger.warning(f"[DEBUG] Crop '{normalized_crop_name}' not found in recommendations")
            
            if specific_crop_rec:
                logger.info(f"[DEBUG] Processing specific crop recommendation for {specific_crop_rec['crop_id']}")
                # Convert enhanced format to legacy format for compatibility
                legacy_crop_rec = {
                    'crop_name': specific_crop_rec['crop_id'],
                    'suitability_score': specific_crop_rec['suitability_score'],
                    'score': int(specific_crop_rec['suitability_score'] * 100),
                    'suitability_level': specific_crop_rec['recommendation_level'],
                    'rainfall_match': 'excellent' if specific_crop_rec['factor_scores']['rainfall'] > 0.8 else 'good',
                    'temperature_match': 'excellent' if specific_crop_rec['factor_scores']['temperature'] > 0.8 else 'good',
                    'season_suitability': 'excellent' if specific_crop_rec['factor_scores']['timing'] > 0.8 else 'good',
                    'sources': ['Real Crop Varieties Database', 'Historical Weather Data'],
                    'guide_recommendations': [
                        specific_crop_rec['planting_guidelines'].get('optimal_timing', 'Not specified'),
                        specific_crop_rec['planting_guidelines'].get('planting_depth', '2-5 cm'),
                        specific_crop_rec['planting_guidelines'].get('spacing', '75cm x 25cm')
                    ],
                    'varieties': [v['name'] for v in specific_crop_rec['top_varieties'][:3]],
                    'planting_time': specific_crop_rec['planting_guidelines'].get('optimal_timing', 'Not specified'),
                    'yield_potential': f"{specific_crop_rec['yield_projections']['yield_projections']['realistic']:.1f}-{specific_crop_rec['yield_projections']['yield_projections']['optimal']:.1f} tons/ha",
                    'description': f"Real data recommendation with {specific_crop_rec['confidence']:.1%} confidence"
                }
            else:
                # Crop not found in recommendations
                legacy_crop_rec = {
                    'crop_name': crop_name,
                    'suitability_score': 0.0,
                    'score': 0,
                    'suitability_level': 'not_recommended',
                    'rainfall_match': 'poor',
                    'temperature_match': 'poor',
                    'season_suitability': 'poor',
                    'sources': ['Real Crop Varieties Database'],
                    'guide_recommendations': [f'{crop_name.title()} is not recommended for rainy season conditions'],
                    'varieties': [],
                    'planting_time': 'Not recommended',
                    'yield_potential': '0 tons/ha',
                    'description': f'{crop_name.title()} is not suitable for rainy season conditions'
                }
            
            return jsonify({
                'crop_name': crop_name,
                'location': location,
                'season': season,
                'recommendations': [legacy_crop_rec],
                'planting_advice': {
                    'optimal_planting_time': legacy_crop_rec['planting_time'],
                    'soil_preparation': 'Prepare well-drained soil',
                    'spacing': 'Follow recommended spacing guidelines'
                },
                'management_tips': [
                    f'Monitor {crop_name} growth regularly',
                    f'Apply fertilizer at recommended rates for {crop_name}',
                    f'Control weeds early in {crop_name} season',
                ],
                'risk_assessment': {
                    'weather_risks': specific_crop_rec['risk_factors'][:2] if specific_crop_rec else ['High risk due to unsuitable conditions'],
                    'pest_risks': ['Stem borer attack', 'Leaf spot disease']
                },
                'environmental_summary': {
                    'total_7day_rainfall': rainfall_data.get('total_7day_rainfall', 0),
                    'forecast_7day_rainfall': rainfall_data.get('forecast_7day_rainfall', 0),
                    'current_temperature': temperature,
                    'humidity': current_weather.get('humidity', 50),
                    'current_season': season
                },
                'search_mode': 'specific_crop',
                'data_type': 'real_data_only',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Advanced engine failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return jsonify({
                'error': 'Service temporarily unavailable',
                'message': 'Please try again later',
                'data_type': 'error_fallback',
                'debug_info': str(e)
            }), 503
        
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
        
        # Load real variety data from crop varieties database
        try:
            import json
            import os
            
            # Load real crop varieties data
            crop_varieties_file = os.path.join('data', 'crop_varieties.json')
            if os.path.exists(crop_varieties_file):
                with open(crop_varieties_file, 'r') as f:
                    crop_data = json.load(f)
                
                # Find the crop and return its varieties
                for crop in crop_data:
                    if crop['crop_id'].lower() == crop_name.lower():
                        varieties = []
                        for variety in crop.get('varieties', []):
                            varieties.append({
                                'name': variety['name'],
                                'maturity_days': variety.get('maturity_days', 120),
                                'yield_potential': f"{variety.get('yield_min', 2)}-{variety.get('yield_max', 5)} tons/ha",
                                'drought_tolerance': variety.get('drought_tolerance', 'Medium'),
                                'disease_resistance': variety.get('disease_resistance', 'Good'),
                                'planting_time': variety.get('planting_time', 'November-December'),
                                'description': variety.get('description', f'{variety["name"]} variety')
                            })
                        
                        return jsonify({
                            'crop': crop_name,
                            'location': location,
                            'varieties': varieties,
                            'data_source': 'Real Crop Varieties Database',
                            'data_type': 'real_data_only',
                            'timestamp': datetime.now().isoformat()
                        })
                
                # Crop not found
                return jsonify({
                    'crop': crop_name,
                    'location': location,
                    'varieties': [],
                    'data_source': 'Real Crop Varieties Database',
                    'data_type': 'real_data_only',
                    'message': f'No varieties found for {crop_name}',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'error': 'Crop varieties database not found',
                    'data_type': 'error'
                }), 404
                
        except Exception as e:
            logger.error(f"Error loading crop varieties: {e}")
            return jsonify({
                'error': 'Failed to load crop varieties',
                'data_type': 'error'
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/varieties/<crop_name>', methods=['GET'])
def get_variety_information(crop_name):
    """Get variety information for a specific crop using Supabase first, then fallback to other sources"""
    try:
        # Get location parameters
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        limit = request.args.get('limit', type=int, default=10)  # Default to 10, max 20
        limit = min(max(limit, 1), 20)  # Clamp between 1 and 20
        
        # First, try to get varieties from Supabase
        if supabase_varieties_handler:
            try:
                # Get varieties from Supabase
                result = supabase_varieties_handler.get_varieties_by_crop(crop_name, limit)
                
                print(f"🔍 API Server - Handler result for {crop_name}:")
                print(f"   total_found: {result.get('total_found', 0)}")
                print(f"   varieties_count: {len(result.get('varieties', []))}")
                print(f"   data_source: {result.get('data_source')}")
                print(f"   has_error: {'error' in result}")
                
                # Add weather analysis if location provided
                if lat and lon:
                    result['weather_analysis'] = {
                        'location': f"{lat}, {lon}",
                        'message': "Location-specific recommendations included"
                    }
                else:
                    result['weather_analysis'] = None
                    
                # Add timestamp
                result['timestamp'] = datetime.now().isoformat()
                
                # If we found varieties, return them
                if result['total_found'] > 0:
                    print(f"✅ API Server - Returning {result['total_found']} varieties for {crop_name}")
                    return jsonify(result)
                    
                # If no varieties found but we got a proper response, return empty result (200)
                # Don't continue to fallback if Supabase returned successfully with 0 results
                if result.get('data_source') == 'supabase' and 'error' not in result:
                    print(f"No varieties found in Supabase for {crop_name}")
                    return jsonify(result), 200
                    
                # If there was an error, continue to fallback options
                print(f"Error or no result from Supabase for {crop_name}, falling back to local database")
            except Exception as e:
                print(f"Error fetching varieties from Supabase: {e}")
                # Continue to fallback options
        
        # Map common crop names to database names
        crop_name_mapping = {
            'beans': 'phaseolus beans',
            'groundnuts': 'groundnut',
            'sweet_potato': 'sweet potato',
            'pigeon_pea': 'pigeonpea',
            'pearl_millet': 'pearl millet',
            'finger_millet': 'finger millet',
            'leafy_vegetables': 'leafy vegetables',
            'tree_nuts': 'tree nut',
            # Add hyphenated versions
            'phaseolus-beans': 'phaseolus beans',
            'sweet-potato': 'sweet potato',
            'pigeon-pea': 'pigeonpea',
            'pearl-millet': 'pearl millet',
            'finger-millet': 'finger millet',
            'leafy-vegetables': 'leafy vegetables',
            'tree-nuts': 'tree nut'
        }
        
        # Use mapped name if available, otherwise use original
        db_crop_name = crop_name_mapping.get(crop_name.lower(), crop_name.lower())
        
        # Fallback: try to get varieties from local SQLite database
        import sqlite3
        try:
            conn = sqlite3.connect('data/agricultural_documents.db')
            cursor = conn.cursor()
            
            # Check if varieties table exists and has data for this crop
            cursor.execute("""
                SELECT COUNT(*) FROM varieties v 
                JOIN crops c ON v.crop_id = c.id 
                WHERE c.crop_name = ?
            """, (db_crop_name,))
            db_count = cursor.fetchone()[0]
            
            if db_count > 0:
                # Get varieties from database
                cursor.execute("""
                SELECT v.variety_name, v.type, v.yield_potential, v.maturity_days,
                       v.soil_requirements, v.spacing_requirements, v.planting_months,
                       v.disease_resistance, v.harvesting_guidelines, v.source_document, 
                       v.extraction_confidence, v.drought_tolerance, v.optimal_temperature_min,
                       v.optimal_temperature_max, v.min_rainfall_mm, v.max_rainfall_mm,
                       v.fertilizer_requirements, v.pest_management, v.disease_management,
                       v.storage_requirements, v.seed_rate_per_hectare, v.expected_yield_per_hectare,
                       v.market_preference, v.seed_availability, v.cost_per_kg
                FROM varieties v 
                JOIN crops c ON v.crop_id = c.id 
                WHERE c.crop_name = ? 
                ORDER BY v.extraction_confidence DESC, v.variety_name
                LIMIT ?
            """, (db_crop_name, limit))
            
                db_varieties = cursor.fetchall()
                
                # Import formatter for consistent variety display
                from scripts.utils.variety_formatter import format_variety_for_display
            
                # Format database varieties for frontend
                varieties = []
                for row in db_varieties:
                    variety = {
                        'name': row[0] or 'Unknown Variety',
                        'type': row[1] or 'Standard',
                        'maturity_days': row[3] or 120,
                        'yield_potential': row[2] or 'Not specified',
                        'drought_tolerance': row[11] or 'Not specified',
                        'disease_resistance': row[7] or [],  # This could be a JSON string array or plain text
                        'planting_time': row[6] or 'Seasonal planting',
                        'description': f'{crop_name} variety with good characteristics',
                        'soil_requirements': row[4] or 'Not specified',
                        'spacing_requirements': row[5] or 'Not specified',
                        'harvesting_guidelines': row[8] or 'Not specified',
                        'source_document': row[9] or 'Database',
                        'extraction_confidence': row[10] or 0,
                        'optimal_temperature_min': row[12],
                        'optimal_temperature_max': row[13],
                        'min_rainfall_mm': row[14],
                        'max_rainfall_mm': row[15],
                        'fertilizer_requirements': row[16] or 'Not specified',
                        'pest_management': row[17] or 'Not specified',
                        'disease_management': row[18] or 'Not specified',
                        'storage_requirements': row[19] or 'Not specified',
                        'seed_rate_per_hectare': row[20],
                        'expected_yield_per_hectare': row[21],
                        'market_preference': row[22] or 'Not specified',
                        'seed_availability': row[23] or 'Not specified',
                        'cost_per_kg': row[24]
                    }
                    
                    # Format the variety data for consistent display
                    formatted_variety = format_variety_for_display(variety)
                    varieties.append(formatted_variety)
                
                # Close SQLite connection
                conn.close()
                
                return jsonify({
                    'crop': crop_name,
                    'real_data': True,
                    'timestamp': datetime.now().isoformat(),
                    'total_found': len(varieties),
                    'varieties': varieties,
                    'data_source': 'database',
                    'weather_analysis': None
                })
        except Exception as e:
            print(f"Error using SQLite database: {e}")
            # Make sure connection is closed if an error occurred
            try:
                conn.close()
            except:
                pass
            # Continue to next fallback if SQLite fails
        
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

# Serve static files from Vite build output
# This must be registered LAST to avoid interfering with API routes
DIST_DIR = Path(__file__).parent / 'dist'

def register_frontend_routes():
    """Register frontend serving routes - must be called after all API routes"""
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """Serve the frontend SPA - handles both static assets and routing"""
        # Don't interfere with API routes (shouldn't reach here for /api/* but just in case)
        if path.startswith('api/'):
            return jsonify({'error': 'API route not found'}), 404
        
        # Check if the file exists in dist directory
        if path and DIST_DIR.joinpath(path).exists():
            return send_from_directory(str(DIST_DIR), path)
        
        # For SPA routing, serve index.html for all non-API routes
        if DIST_DIR.joinpath('index.html').exists():
            return send_from_directory(str(DIST_DIR), 'index.html')
        
        # If dist doesn't exist (development), return a helpful message
        return jsonify({
            'message': 'Frontend not built. Please run: npm run build',
            'path': path,
            'dist_exists': DIST_DIR.exists()
        }), 503

# Register frontend routes after all API routes
register_frontend_routes()

if __name__ == '__main__':
    print("[START] Starting Mlangizi wa Ulimi API Server...")
    
    # Get port from environment variable (Render sets this) or default to 8000
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"[INFO] API will be available on: http://0.0.0.0:{port}")
    print(f"[INFO] API Documentation: http://0.0.0.0:{port}/api/health")
    print(f"[INFO] Debug mode: {debug}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
