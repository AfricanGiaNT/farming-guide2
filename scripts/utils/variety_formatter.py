"""
Utility functions for formatting variety data for display.
"""
import json
from typing import Dict, List, Union, Any

def format_disease_resistance(disease_resistance: Union[str, List[str]]) -> Dict[str, Any]:
    """
    Format disease resistance data for consistent display in UI.
    
    Args:
        disease_resistance: Either a string or list of disease resistances
        
    Returns:
        Dictionary with formatted disease resistance data ready for UI display
    """
    # Handle None or empty values
    if not disease_resistance:
        # Return None instead of empty object for better frontend handling
        return None
    
    # Handle empty strings
    if isinstance(disease_resistance, str) and disease_resistance.strip() == '':
        return None
    
    # Handle empty objects/dicts
    if isinstance(disease_resistance, dict) and len(disease_resistance) == 0:
        return None
    
    # Handle empty arrays - they should return formatted structure, not None
    if isinstance(disease_resistance, list) and len(disease_resistance) == 0:
        return {
            'text': 'Not specified',
            'items': [],
            'level': 'unknown'
        }
    
    # Convert string to array if needed
    resistance_items = []
    
    if isinstance(disease_resistance, str):
        if disease_resistance.startswith("[") and disease_resistance.endswith("]"):
            try:
                # Try to parse as JSON string
                import json
                resistance_items = json.loads(disease_resistance)
            except:
                # If parsing fails, use as plain text
                resistance_items = [disease_resistance]
        else:
            # Plain text - could be comma separated
            if "," in disease_resistance:
                resistance_items = [item.strip() for item in disease_resistance.split(",")]
            else:
                resistance_items = [disease_resistance]
    elif isinstance(disease_resistance, list):
        resistance_items = disease_resistance
    
    # Determine resistance level based on quantity
    level = "unknown"
    if resistance_items:
        count = len(resistance_items)
        if count >= 3:
            level = "high"
        elif count == 2:
            level = "moderate"
        elif count == 1:
            level = "low"
    
    # Format for display
    return {
        'text': ', '.join(resistance_items) if resistance_items else 'Not specified',
        'items': resistance_items,
        'level': level
    }

def ensure_renderable_value(value: Any) -> Any:
    """
    Ensure a value is safely renderable in React (not an object unless it has a text property)
    
    Args:
        value: Any value that might be rendered in the UI
        
    Returns:
        A safely renderable value (string, number, array of strings)
    """
    # Handle None case
    if value is None:
        return "Not specified"
    
    # Handle strings and numbers directly
    if isinstance(value, (str, int, float, bool)):
        return value
    
    # Handle arrays by converting all elements to strings
    if isinstance(value, list):
        return [str(item) if not isinstance(item, (str, int, float, bool)) else item for item in value]
    
    # Handle objects with a text property
    if isinstance(value, dict) and 'text' in value:
        return value['text']
    
    # Convert any other objects to a string
    try:
        import json
        return json.dumps(value)
    except:
        return str(value)

def format_variety_for_display(variety: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a variety object for consistent display in the UI.
    
    Args:
        variety: Raw variety data object from database or API
        
    Returns:
        Formatted variety data ready for UI display
    """
    formatted = {**variety}  # Copy original data
    
    # Format pest and disease management separately
    def parse_management_data(data):
        """Parse management data from various formats"""
        if not data:
            return []
        
        if isinstance(data, str):
            # Clean up the string
            data = data.strip()
            data_lower = data.lower()
            if not data or data_lower in ['none', 'null', 'not specified', 'na', 'n/a']:
                return []
            
            try:
                # Try to parse as JSON first
                if data.strip().startswith('['):
                    items = json.loads(data)
                    result = [item.strip() for item in items if item.strip() and str(item).strip().lower() not in ['none', 'null', 'not specified', 'na', 'n/a']]
                    if result:
                        return result
            except:
                pass
            
            # Try splitting by newlines (common in long text)
            if '\n' in data:
                items = [line.strip() for line in data.split('\n') if line.strip() 
                        and not line.strip().startswith('#')
                        and line.strip().lower() not in ['none', 'null', 'not specified', 'na', 'n/a']]
                if len(items) > 1:  # Only if we got multiple items
                    return items
            
            # Try splitting by numbered lists (1., 2., etc.)
            import re
            numbered_match = re.match(r'^(\d+[\.\)]\s+.+?)(?:\s+\d+[\.\)]|\s*$)', data, re.MULTILINE)
            if numbered_match or re.search(r'\d+[\.\)]\s+', data):
                items = re.split(r'\d+[\.\)]\s+', data)
                items = [item.strip() for item in items if item.strip() and item.strip().lower() not in ['none', 'null', 'not specified', 'na', 'n/a']]
                if len(items) > 1:
                    return items
            
            # Try splitting by bullet points or dashes
            for delimiter in ['•', '-', '*', '→']:
                if delimiter in data:
                    lines = [line.strip() for line in data.split(delimiter) 
                            if line.strip() and line.strip().lower() not in ['none', 'null', 'not specified', 'na', 'n/a']]
                    if len(lines) > 1:
                        return lines
                    break
            
            # Split by semicolons
            if ';' in data:
                items = [item.strip() for item in data.split(';') 
                        if item.strip() and item.strip().lower() not in ['none', 'null', 'not specified', 'na', 'n/a']]
                if len(items) > 1:
                    return items
            
            # Split by "For Fungus:" or similar patterns (common in disease management)
            if 'for fungus:' in data_lower or 'for disease:' in data_lower or 'for pest:' in data_lower:
                import re
                # Look for repeated patterns like "For Fungus: Disease:" appearing multiple times
                # This indicates multiple items that need to be split
                pattern_matches = re.findall(r'(?i)For\s+(?:Fungus|Disease|Pest):\s+[^:]+:', data)
                
                if len(pattern_matches) > 1:
                    # Split on the pattern, keeping the prefix with each item
                    parts = re.split(r'(?i)(For\s+(?:Fungus|Disease|Pest):\s+[^:]+:\s*)', data)
                    reconstructed = []
                    for i in range(len(parts)):
                        if parts[i].strip() and len(parts[i].strip()) > 5:
                            # Check if this part starts with "For"
                            if re.match(r'(?i)^For\s+(?:Fungus|Disease|Pest):', parts[i]):
                                # This is a header - combine with next if available
                                if i + 1 < len(parts):
                                    combined = (parts[i] + parts[i + 1]).strip()
                                    if combined:
                                        reconstructed.append(combined)
                                else:
                                    reconstructed.append(parts[i].strip())
                            elif not reconstructed or not re.match(r'(?i)^For\s+', reconstructed[-1] if reconstructed else ''):
                                # This is standalone content
                                reconstructed.append(parts[i].strip())
                    if len(reconstructed) > 1:
                        return reconstructed
                
                # Fallback: simpler split on "For [Type]:" pattern
                parts = re.split(r'(?i)(?=For\s+(?:Fungus|Disease|Pest):\s+[^:]+:)', data)
                parts = [p.strip() for p in parts if p.strip() and len(p.strip()) > 5]
                if len(parts) > 1:
                    # Clean up duplicates and merge related items
                    cleaned = []
                    for part in parts:
                        part = part.strip()
                        # Remove duplicate prefixes
                        if re.match(r'(?i)^For\s+(?:Fungus|Disease|Pest):', part):
                            # Check if this duplicates the previous item
                            if not cleaned or not part.startswith(cleaned[-1][:30]):
                                cleaned.append(part)
                        else:
                            cleaned.append(part)
                    if len(cleaned) > 1:
                        return cleaned[:6]
            
            # Split by periods that end sentences (for pest management with multiple actions)
            if '.' in data and ':' in data:
                import re
                # Split on periods followed by space and capital letter (new sentence)
                sentences = re.split(r'\.\s+(?=[A-Z])', data)
                sentences = [s.strip() + '.' if s.strip() and not s.strip().endswith('.') else s.strip() 
                            for s in sentences if s.strip() and len(s.strip()) > 10]
                # Only split if we get multiple reasonable sentences
                if len(sentences) > 1:
                    # Filter to reasonable length sentences
                    good_sentences = [s for s in sentences if 15 < len(s) < 300]
                    if len(good_sentences) >= 2:
                        return good_sentences[:6]  # Limit to 6 items
            
            # Split by commas (but be careful - only if items look like separate items)
            if ',' in data:
                items = [item.strip() for item in data.split(',') 
                        if item.strip() and item.strip().lower() not in ['none', 'null', 'not specified', 'na', 'n/a']]
                # Only split if items are reasonably short and look like separate items
                if len(items) > 1 and all(len(item) < 150 for item in items):
                    # Check if items don't form a sentence (capitalized first word suggests separate items)
                    if all(not item[0].isupper() or len(item.split()) <= 10 for item in items):
                        return items
                    # Or if they're very short (likely bullet-like)
                    if all(len(item) < 50 for item in items):
                        return items
            
            # If it's a very long single sentence, try to split by common patterns
            if len(data) > 200:
                # Try splitting by common separators in longer text
                for pattern in [' • ', ' - ', ': ', '. ']:
                    if pattern in data:
                        parts = [p.strip() for p in data.split(pattern) if p.strip() and len(p.strip()) > 10]
                        if len(parts) > 1:
                            return parts
            
            # If no delimiters found or single long sentence, return as single item
            return [data.strip()] if data.strip() else []
            
        elif isinstance(data, list):
            return [str(item).strip() for item in data 
                   if str(item).strip() and str(item).strip().lower() not in ['none', 'null', 'not specified', 'na', 'n/a']]
        elif isinstance(data, dict):
            # If it's already formatted, extract items
            if 'items' in data:
                return data['items']
            return []
        else:
            # Convert to string and return as single item
            result = str(data).strip()
            return [result] if result and result.lower() not in ['none', 'null', 'not specified', 'na', 'n/a'] else []

    # Extract pest management - USE ONLY DATA FROM DATABASE
    pest_items = []
    if 'pest_management' in variety and variety.get('pest_management'):
        pest_items = parse_management_data(variety['pest_management'])
        # Remove duplicates and limit to max 6 items (from actual database data)
        seen = set()
        unique_items = []
        for item in pest_items:
            item_lower = item.lower().strip()
            if item_lower not in seen and len(unique_items) < 6:
                seen.add(item_lower)
                unique_items.append(item)
        pest_items = unique_items

    # Extract disease management - USE ONLY DATA FROM DATABASE
    disease_items = []
    if 'disease_management' in variety and variety.get('disease_management'):
        disease_items = parse_management_data(variety['disease_management'])
        # Remove duplicates and limit to max 6 items (from actual database data)
        seen = set()
        unique_items = []
        for item in disease_items:
            item_lower = item.lower().strip()
            if item_lower not in seen and len(unique_items) < 6:
                seen.add(item_lower)
                unique_items.append(item)
        disease_items = unique_items

    # Format pest and disease management
    # For very short/generic items, try to enhance the preview
    pest_preview = pest_items[0] if pest_items else 'Not specified'
    if pest_items and len(pest_preview) < 30:
        # If it's very short, check if we have multiple items to combine
        if len(pest_items) > 1:
            pest_preview = f"{pest_preview} and {len(pest_items) - 1} more"
        # Or check if disease management can provide context
        elif disease_items:
            pest_preview = pest_preview  # Keep as is, will be shown separately
    
    disease_preview = disease_items[0] if disease_items else 'Not specified'
    if disease_items and len(disease_preview) < 30:
        if len(disease_items) > 1:
            disease_preview = f"{disease_preview} and {len(disease_items) - 1} more"
    
    formatted['pest_management'] = {
        'items': pest_items,
        'preview': pest_preview,
        'count': len(pest_items)
    }
    
    formatted['disease_management'] = {
        'items': disease_items,
        'preview': disease_preview, 
        'count': len(disease_items)
    }

    # Keep disease_resistance for backward compatibility but mark as deprecated
    combined_items = []
    if pest_items:
        combined_items.append(pest_items[0])
    if disease_items:
        combined_items.append(disease_items[0])
    
    if combined_items:
        formatted['disease_resistance'] = {
            'text': ', '.join(combined_items),
            'items': combined_items,
            'level': 'moderate'
        }
    else:
        # Fallback to original disease_resistance if no pest/disease management data
        if 'disease_resistance' in variety:
            disease_res = variety['disease_resistance']
            formatted_result = format_disease_resistance(disease_res)
            if formatted_result is None:
                formatted['disease_resistance'] = {
                    'text': 'Not specified',
                    'items': [],
                    'level': 'unknown'
                }
            else:
                formatted['disease_resistance'] = formatted_result
        else:
            formatted['disease_resistance'] = {
                'text': 'Not specified',
                'items': [],
                'level': 'unknown'
            }
    
    # Format yield potential as text + level
    if 'yield_potential' in variety and variety['yield_potential'] is not None:
        yield_value = variety['yield_potential']
        yield_level = "medium"
        
        # Convert to string if it's not already
        if not isinstance(yield_value, str):
            yield_value = str(yield_value)
        
        # Determine yield level based on value
        if isinstance(yield_value, str):
            lowercase_yield = yield_value.lower()
            
            # Check for text indicators first
            if 'high' in lowercase_yield or 'excellent' in lowercase_yield:
                yield_level = "high"
            elif 'low' in lowercase_yield or 'poor' in lowercase_yield:
                yield_level = "low"
            else:
                # Try to extract numeric values for yield level detection
                import re
                # Match patterns like "2500 kg/ha", "8-11t/ha", "11-13t/ha", "5t/ha"
                numbers = re.findall(r'(\d+(?:\.\d+)?)', lowercase_yield)
                
                if numbers:
                    # Convert to float and get max value (handle ranges like "8-11")
                    numeric_values = [float(n) for n in numbers]
                    max_value = max(numeric_values)
                    
                    # Detect unit and set thresholds
                    if 't/ha' in lowercase_yield or 'ton' in lowercase_yield:
                        # Tonnes per hectare thresholds
                        if max_value >= 10:
                            yield_level = "high"
                        elif max_value >= 6:
                            yield_level = "medium"
                        else:
                            yield_level = "low"
                    elif 'kg/ha' in lowercase_yield:
                        # Kg per hectare thresholds (for beans, groundnuts, etc.)
                        if max_value >= 2500:
                            yield_level = "high"
                        elif max_value >= 1500:
                            yield_level = "medium"
                        else:
                            yield_level = "low"
                    # Default to medium if we can't determine
        
        formatted['yield_potential'] = {
            'text': yield_value,
            'level': yield_level
        }
    elif 'yield_potential' not in formatted:
        # If yield_potential is missing or None, use expected_yield_per_hectare if available
        if 'expected_yield_per_hectare' in variety and variety.get('expected_yield_per_hectare'):
            formatted['yield_potential'] = {
                'text': f"{variety['expected_yield_per_hectare']} kg/ha",
                'level': "medium"
            }
        else:
            # Default fallback
            formatted['yield_potential'] = {
                'text': 'Not specified',
                'level': "medium"
            }
    
    # Format drought tolerance as text + level
    if 'drought_tolerance' in variety:
        drought_value = variety['drought_tolerance']
        drought_level = "medium"
        
        # Determine drought tolerance level
        if isinstance(drought_value, str):
            lowercase_drought = drought_value.lower()
            if 'high' in lowercase_drought or 'excellent' in lowercase_drought or 'good' in lowercase_drought:
                drought_level = "high"
            elif 'low' in lowercase_drought or 'poor' in lowercase_drought:
                drought_level = "low"
        
        formatted['drought_tolerance'] = {
            'text': drought_value,
            'level': drought_level
        }
    
    # Ensure all values are safely renderable in React
    # Exclude structured objects from ensure_renderable_value
    excluded_keys = ['disease_resistance', 'yield_potential', 'drought_tolerance', 'pest_management', 'disease_management']
    for key in formatted:
        if key not in excluded_keys:
            formatted[key] = ensure_renderable_value(formatted[key])
    
    return formatted
