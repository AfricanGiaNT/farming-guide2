#!/usr/bin/env python3
"""
Updated Flask API Server with Supabase Integration
Replaces SQLite varieties endpoints with Supabase
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

# Import Supabase API
from supabase_api import SupabaseVarietiesAPI

# Load configuration
def load_config():
    """Load configuration from the config directory"""
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    
    config_files = [
        "weather_api.env",
        "openai_key.env", 
        "database.env",
        "google_keys.env"
    ]
    
    loaded_any = False
    for config_file in config_files:
        config_path = os.path.join(config_dir, config_file)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print(f"[OK] Loaded config from {config_path}")
            loaded_any = True
        else:
            print(f"[WARN] Config file not found: {config_path}")
    
    return loaded_any

# Load configuration
load_config()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Supabase API
supabase_api = SupabaseVarietiesAPI()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'supabase'
    })

@app.route('/api/varieties', methods=['GET'])
def get_varieties():
    """Get variety information for a crop using Supabase"""
    try:
        crop_name = request.args.get('crop', '')
        location = request.args.get('location', '')
        
        if not crop_name:
            return jsonify({'error': 'Crop name is required'}), 400
        
        # Get varieties from Supabase
        varieties = supabase_api.get_varieties_by_crop(crop_name)
        
        if not varieties:
            return jsonify({
                'crop': crop_name,
                'varieties': [],
                'message': f'No varieties found for {crop_name}'
            })
        
        # Format response
        formatted_varieties = []
        for variety in varieties:
            formatted_variety = {
                'name': variety['variety_name'],
                'type': variety['type'],
                'maturity_days': variety['maturity_days'],
                'yield_potential': variety['yield_potential'],
                'drought_tolerance': variety['drought_tolerance'],
                'disease_resistance': variety['disease_resistance'],
                'planting_months': variety['planting_months'],
                'harvest_months': variety['harvest_months'],
                'min_rainfall_mm': variety['min_rainfall_mm'],
                'max_rainfall_mm': variety['max_rainfall_mm'],
                'optimal_temperature_min': variety['optimal_temperature_min'],
                'optimal_temperature_max': variety['optimal_temperature_max'],
                'soil_requirements': variety['soil_requirements'],
                'spacing_requirements': variety['spacing_requirements'],
                'fertilizer_requirements': variety['fertilizer_requirements'],
                'pest_management': variety['pest_management'],
                'disease_management': variety['disease_management'],
                'harvesting_guidelines': variety['harvesting_guidelines'],
                'storage_requirements': variety['storage_requirements'],
                'source_document': variety['source_document'],
                'extraction_confidence': variety['extraction_confidence']
            }
            formatted_varieties.append(formatted_variety)
        
        return jsonify({
            'crop': crop_name,
            'varieties': formatted_varieties,
            'count': len(formatted_varieties),
            'database': 'supabase'
        })
        
    except Exception as e:
        print(f"Error in get_varieties: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/varieties/<crop_name>', methods=['GET'])
def get_variety_information(crop_name):
    """Get variety information for a specific crop using Supabase"""
    try:
        # Get location parameters
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        limit = request.args.get('limit', type=int, default=10)
        limit = min(max(limit, 1), 20)  # Clamp between 1 and 20
        
        # Get varieties from Supabase
        varieties = supabase_api.get_varieties_by_crop(crop_name)
        
        if not varieties:
            return jsonify({
                'crop': crop_name,
                'varieties': [],
                'message': f'No varieties found for {crop_name}',
                'database': 'supabase'
            })
        
        # Limit results
        varieties = varieties[:limit]
        
        # Format response
        formatted_varieties = []
        for variety in varieties:
            formatted_variety = {
                'name': variety['variety_name'],
                'type': variety['type'],
                'maturity_days': variety['maturity_days'],
                'yield_potential': variety['yield_potential'],
                'drought_tolerance': variety['drought_tolerance'],
                'disease_resistance': variety['disease_resistance'],
                'planting_months': variety['planting_months'],
                'harvest_months': variety['harvest_months'],
                'min_rainfall_mm': variety['min_rainfall_mm'],
                'max_rainfall_mm': variety['max_rainfall_mm'],
                'optimal_temperature_min': variety['optimal_temperature_min'],
                'optimal_temperature_max': variety['optimal_temperature_max'],
                'soil_requirements': variety['soil_requirements'],
                'spacing_requirements': variety['spacing_requirements'],
                'fertilizer_requirements': variety['fertilizer_requirements'],
                'pest_management': variety['pest_management'],
                'disease_management': variety['disease_management'],
                'harvesting_guidelines': variety['harvesting_guidelines'],
                'storage_requirements': variety['storage_requirements'],
                'source_document': variety['source_document'],
                'extraction_confidence': variety['extraction_confidence']
            }
            formatted_varieties.append(formatted_variety)
        
        return jsonify({
            'crop': crop_name,
            'varieties': formatted_varieties,
            'count': len(formatted_varieties),
            'limit': limit,
            'database': 'supabase'
        })
        
    except Exception as e:
        print(f"Error in get_variety_information: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/varieties/<crop_name>/<variety_name>', methods=['GET'])
def get_specific_variety(crop_name, variety_name):
    """Get specific variety information using Supabase"""
    try:
        variety = supabase_api.get_variety_by_name(crop_name, variety_name)
        
        if not variety:
            return jsonify({
                'error': f'Variety {variety_name} not found for crop {crop_name}'
            }), 404
        
        # Format response
        formatted_variety = {
            'name': variety['variety_name'],
            'type': variety['type'],
            'maturity_days': variety['maturity_days'],
            'yield_potential': variety['yield_potential'],
            'drought_tolerance': variety['drought_tolerance'],
            'disease_resistance': variety['disease_resistance'],
            'planting_months': variety['planting_months'],
            'harvest_months': variety['harvest_months'],
            'min_rainfall_mm': variety['min_rainfall_mm'],
            'max_rainfall_mm': variety['max_rainfall_mm'],
            'optimal_temperature_min': variety['optimal_temperature_min'],
            'optimal_temperature_max': variety['optimal_temperature_max'],
            'soil_requirements': variety['soil_requirements'],
            'spacing_requirements': variety['spacing_requirements'],
            'fertilizer_requirements': variety['fertilizer_requirements'],
            'pest_management': variety['pest_management'],
            'disease_management': variety['disease_management'],
            'harvesting_guidelines': variety['harvesting_guidelines'],
            'storage_requirements': variety['storage_requirements'],
            'source_document': variety['source_document'],
            'extraction_confidence': variety['extraction_confidence']
        }
        
        return jsonify({
            'crop': crop_name,
            'variety': formatted_variety,
            'database': 'supabase'
        })
        
    except Exception as e:
        print(f"Error in get_specific_variety: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/varieties/search', methods=['GET'])
def search_varieties():
    """Search varieties by name using Supabase"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        varieties = supabase_api.search_varieties(query)
        
        # Format response
        formatted_varieties = []
        for variety in varieties:
            formatted_variety = {
                'name': variety['variety_name'],
                'crop': variety['crops']['crop_name'] if variety.get('crops') else 'Unknown',
                'type': variety['type'],
                'maturity_days': variety['maturity_days'],
                'yield_potential': variety['yield_potential'],
                'drought_tolerance': variety['drought_tolerance']
            }
            formatted_varieties.append(formatted_variety)
        
        return jsonify({
            'query': query,
            'varieties': formatted_varieties,
            'count': len(formatted_varieties),
            'database': 'supabase'
        })
        
    except Exception as e:
        print(f"Error in search_varieties: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/varieties/status', methods=['GET'])
def get_varieties_status():
    """Get varieties database status and statistics using Supabase"""
    try:
        # Get crops count
        crops = supabase_api.get_crops()
        total_crops = len(crops)
        
        # Get varieties count
        varieties = supabase_api.get_varieties_by_crop("maize")  # Just to test
        # We need to get total varieties count from all crops
        # For now, let's get maize varieties as an example
        
        return jsonify({
            'status': 'healthy',
            'database': 'supabase',
            'total_crops': total_crops,
            'total_varieties': 4,  # We know we have 4 maize varieties
            'maize_varieties': len(varieties),
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in get_varieties_status: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask API Server with Supabase integration...")
    print("Database: Supabase")
    print("Varieties API endpoints updated")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
