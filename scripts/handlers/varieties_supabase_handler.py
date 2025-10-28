#!/usr/bin/env python3
"""
Enhanced varieties handler using Supabase for real data
"""

import json
import os
from typing import Dict, List, Any, Optional

from supabase_api import SupabaseVarietiesAPI
from scripts.utils.variety_formatter import format_variety_for_display

class VarietiesSupabaseHandler:
    """Handler for varieties data using Supabase"""
    
    def __init__(self):
        """Initialize VarietiesSupabaseHandler"""
        self.supabase_api = SupabaseVarietiesAPI()
    
    def get_varieties_by_crop(self, crop_name: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get varieties for a specific crop from Supabase
        
        Args:
            crop_name: The name of the crop
            limit: Maximum number of varieties to return
            
        Returns:
            Dictionary containing varieties and metadata
        """
        try:
            # Normalize crop name
            normalized_crop_name = self._normalize_crop_name(crop_name)
            
            # Get varieties from Supabase - try normalized name first
            try:
                varieties_data = self.supabase_api.get_varieties_by_crop(normalized_crop_name)
            except Exception as e:
                print(f"Error fetching varieties with normalized name '{normalized_crop_name}': {e}")
                varieties_data = []
            
            # If no results with normalized name, try the original name
            if not varieties_data and normalized_crop_name != crop_name.lower():
                print(f"No varieties found with normalized name '{normalized_crop_name}', trying original '{crop_name}'")
                try:
                    varieties_data = self.supabase_api.get_varieties_by_crop(crop_name.lower())
                except Exception as e:
                    print(f"Error fetching varieties with original name '{crop_name}': {e}")
                    varieties_data = []
            
            if not varieties_data:
                return {
                    'crop': crop_name,
                    'total_found': 0,
                    'varieties': [],
                    'data_source': 'supabase',
                    'message': f'No varieties found for {crop_name}'
                }
            
            # Format varieties for frontend
            formatted_varieties = []
            print(f"🔄 Processing {len(varieties_data)} varieties from database...")
            
            for idx, variety in enumerate(varieties_data[:limit]):
                try:
                    # Debug: Log pest and disease management data
                    variety_name = variety.get('variety_name', f'Variety {idx+1}')
                    pest_mgmt = variety.get('pest_management')
                    disease_mgmt = variety.get('disease_management')
                    if pest_mgmt:
                        full_text = str(pest_mgmt)
                        if len(full_text) > 100:
                            print(f"🐛 Variety {variety_name} has pest_management ({len(full_text)} chars): {full_text[:100]}...")
                        else:
                            print(f"🐛 Variety {variety_name} has pest_management: {full_text}")
                    if disease_mgmt:
                        full_text = str(disease_mgmt)
                        if len(full_text) > 100:
                            print(f"🦠 Variety {variety_name} has disease_management ({len(full_text)} chars): {full_text[:100]}...")
                        else:
                            print(f"🦠 Variety {variety_name} has disease_management: {full_text}")
                    
                    # Convert to frontend format
                    frontend_variety = {
                        'name': variety.get('variety_name'),
                        'type': variety.get('type') or 'Standard',
                        'maturity_days': variety.get('maturity_days'),
                        'yield_potential': variety.get('yield_potential'),  # Get from Supabase
                        'drought_tolerance': variety.get('drought_tolerance'),
                        'disease_resistance': variety.get('disease_resistance'),
                        'planting_time': self._format_planting_months(variety.get('planting_months')),
                        'description': variety.get('description', f'{variety.get("variety_name")} {normalized_crop_name} variety'),
                        'soil_requirements': variety.get('soil_requirements'),
                        'spacing_requirements': variety.get('spacing_requirements'),
                        'harvesting_guidelines': variety.get('harvesting_guidelines'),
                        'source_document': variety.get('source_document'),
                        'extraction_confidence': variety.get('extraction_confidence', 80),
                        'optimal_temperature_min': variety.get('optimal_temperature_min'),
                        'optimal_temperature_max': variety.get('optimal_temperature_max'),
                        'min_rainfall_mm': variety.get('min_rainfall_mm'),
                        'max_rainfall_mm': variety.get('max_rainfall_mm'),
                        'fertilizer_requirements': variety.get('fertilizer_requirements'),
                        'pest_management': variety.get('pest_management'),
                        'disease_management': variety.get('disease_management'),
                        'storage_requirements': variety.get('storage_requirements'),
                        'seed_rate_per_hectare': variety.get('seed_rate_per_hectare'),
                        'expected_yield_per_hectare': variety.get('expected_yield_per_hectare'),
                        'market_preference': variety.get('market_preference'),
                        'seed_availability': variety.get('seed_availability'),
                        'cost_per_kg': variety.get('cost_per_kg')
                    }
                    
                    # Format the variety data for consistent display
                    try:
                        formatted_variety = format_variety_for_display(frontend_variety)
                        
                        # Debug: Check what was formatted
                        print(f"✅ Formatted variety {idx+1}/{len(varieties_data[:limit])}: {variety_name}")
                        pest_mgmt_formatted = formatted_variety.get('pest_management')
                        disease_mgmt_formatted = formatted_variety.get('disease_management')
                        if pest_mgmt_formatted:
                            if isinstance(pest_mgmt_formatted, dict):
                                items = pest_mgmt_formatted.get('items', [])
                                print(f"   - pest_management: {pest_mgmt_formatted.get('count', 0)} items, preview: '{pest_mgmt_formatted.get('preview', 'N/A')}'")
                                print(f"     items array: {items}, type: {type(items)}, length: {len(items) if isinstance(items, list) else 'N/A'}")
                            else:
                                print(f"   - pest_management: {type(pest_mgmt_formatted).__name__} = {str(pest_mgmt_formatted)[:50]}")
                        if disease_mgmt_formatted:
                            if isinstance(disease_mgmt_formatted, dict):
                                items = disease_mgmt_formatted.get('items', [])
                                print(f"   - disease_management: {disease_mgmt_formatted.get('count', 0)} items, preview: '{disease_mgmt_formatted.get('preview', 'N/A')}'")
                                print(f"     items array: {items}, type: {type(items)}, length: {len(items) if isinstance(items, list) else 'N/A'}")
                            else:
                                print(f"   - disease_management: {type(disease_mgmt_formatted).__name__} = {str(disease_mgmt_formatted)[:50]}")
                        
                        formatted_varieties.append(formatted_variety)
                    except Exception as format_error:
                        print(f"❌ Error formatting variety {idx+1} ({variety_name}): {format_error}")
                        import traceback
                        traceback.print_exc()
                        # Don't append this variety if formatting failed
                except Exception as e:
                    print(f"❌ Error processing variety {idx+1}: {e}")
                    import traceback
                    traceback.print_exc()
                    # Continue with next variety
                    continue
            
            print(f"✅ Handler returning {len(formatted_varieties)} formatted varieties for {crop_name}")
            if formatted_varieties:
                print(f"   First variety: {formatted_varieties[0].get('name', 'NO NAME')}")
                print(f"   First variety yield: {formatted_varieties[0].get('yield_potential', 'NO YIELD')}")
            
            return {
                'crop': crop_name,
                'total_found': len(formatted_varieties),
                'varieties': formatted_varieties,
                'data_source': 'supabase',
                'real_data': True
            }
            
        except Exception as e:
            print(f"Error fetching varieties from Supabase: {e}")
            return {
                'crop': crop_name,
                'error': f"Failed to fetch varieties: {str(e)}",
                'total_found': 0,
                'varieties': [],
                'data_source': 'error'
            }
    
    def _normalize_crop_name(self, crop_name: str) -> str:
        """
        Normalize crop name for database lookup
        
        Args:
            crop_name: The display name of the crop
            
        Returns:
            Normalized crop name for database
        """
        # Clean the crop name first (handle dashes, underscores, etc.)
        cleaned_name = crop_name.lower().replace('-', ' ').replace('_', ' ').strip()
        
        # Map common variants to standard names
        # Note: Frontend sends "beans" but DB has "phaseolus beans"
        # Frontend may also send "phaseolus-beans" or "phaseolus beans"
        crop_mapping = {
            # Beans variants - keep as is since API will try variants
            'beans': 'beans',  # Don't pre-normalize, let the API try both
            'phaseolus beans': 'phaseolus beans',
            'phaseolus-beans': 'phaseolus beans',
            # Groundnuts
            'groundnuts': 'groundnut',
            'soybean': 'soyabean',
            'soyabean': 'soyabean',
            'sweet_potato': 'sweet potato',
            'sweet potato': 'sweet potato',
            'pigeon_pea': 'pigeonpea',
            'pigeonpea': 'pigeonpea',
            'pearl_millet': 'pearl millet',
            'pearl millet': 'pearl millet',
            'finger_millet': 'finger millet',
            'finger millet': 'finger millet',
            'leafy_vegetables': 'leafy vegetables',
            'leafy vegetables': 'leafy vegetables',
            'chili': 'chillies',
            'chilies': 'chillies',
        }
        
        normalized = crop_name.lower().replace('-', ' ')
        return crop_mapping.get(normalized, normalized)
    
    def _format_planting_months(self, planting_months: Any) -> str:
        """
        Format planting months into a human-readable string
        
        Args:
            planting_months: List of planting months or month names
            
        Returns:
            Formatted planting months string
        """
        if not planting_months:
            return "Seasonal planting"
            
        # If already a string, return as is
        if isinstance(planting_months, str):
            return planting_months
            
        # If JSON string, try to parse
        if isinstance(planting_months, str) and (planting_months.startswith('[') or planting_months.startswith('{')):
            try:
                planting_months = json.loads(planting_months)
            except:
                return planting_months
                
        # If list of month numbers
        if isinstance(planting_months, list) and all(isinstance(m, int) for m in planting_months):
            month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            
            # Convert month numbers (1-12) to names
            month_names_list = [month_names[m-1] if 1 <= m <= 12 else str(m) for m in planting_months]
            
            # Format nicely
            if len(month_names_list) == 1:
                return month_names_list[0]
            elif len(month_names_list) == 2:
                return f"{month_names_list[0]} and {month_names_list[1]}"
            else:
                return ", ".join(month_names_list[:-1]) + f" and {month_names_list[-1]}"
        
        # Default fallback
        return str(planting_months)


# Test the handler
if __name__ == "__main__":
    handler = VarietiesSupabaseHandler()
    
    # Test with maize
    print("Testing with maize...")
    maize_result = handler.get_varieties_by_crop("maize")
    print(f"Found {maize_result['total_found']} maize varieties")
    for variety in maize_result['varieties'][:3]:  # Show first 3
        print(f"  - {variety['name']} ({variety['type']}): {variety['maturity_days']} days")
    
    # Test with beans
    print("\nTesting with beans...")
    beans_result = handler.get_varieties_by_crop("beans")
    print(f"Found {beans_result['total_found']} bean varieties")
    for variety in beans_result['varieties'][:3]:  # Show first 3
        print(f"  - {variety['name']}: {variety['maturity_days']} days")

