"""
Coordinate handler for the Agricultural Advisor Bot.
Parses and validates user input for geographical coordinates.
"""
import re
from typing import Optional, Tuple, Dict, List
from scripts.utils.logger import logger


class CoordinateHandler:
    """Handles parsing and validation of geographical coordinates."""
    
    def __init__(self):
        # Common coordinate patterns
        self.patterns = [
            # Decimal degrees: "lat, lon" or "lat,lon"
            r'^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$',
            # Decimal degrees with explicit labels: "lat: X, lon: Y"
            r'^\s*lat:\s*(-?\d+\.?\d*)\s*,\s*lon:\s*(-?\d+\.?\d*)\s*$',
            # Decimal degrees with N/S/E/W: "13.98S, 33.78E"
            r'^\s*(-?\d+\.?\d*)\s*([NS])\s*,\s*(-?\d+\.?\d*)\s*([EW])\s*$',
        ]
        
        # Predefined locations for Lilongwe area
        self.known_locations = {
            'lilongwe': (-13.9833, 33.7833),
            'lilongwe city': (-13.9833, 33.7833),
            'lilongwe center': (-13.9833, 33.7833),
            'lilongwe central': (-13.9833, 33.7833),
            'area 1': (-13.9700, 33.7700),
            'area 2': (-13.9800, 33.7800),
            'area 3': (-13.9900, 33.7900),
            'kawale': (-13.9300, 33.7300),
            'mgona': (-13.9500, 33.8000),
            'kanengo': (-13.9200, 33.7200),
        }
    
    def parse_coordinates(self, user_input: str, user_id: Optional[str] = None) -> Optional[Tuple[float, float]]:
        """
        Parse coordinates from user input.
        
        Args:
            user_input: String containing coordinates in various formats
            user_id: Optional user ID for logging
            
        Returns:
            Tuple of (latitude, longitude) or None if parsing fails
        """
        if not user_input:
            return None
        
        user_input = user_input.strip().lower()
        
        # Check for known locations first
        if user_input in self.known_locations:
            lat, lon = self.known_locations[user_input]
            logger.info(f"Matched known location '{user_input}' to coordinates: {lat}, {lon}", user_id)
            return lat, lon
        
        # Try to parse coordinate patterns
        for pattern in self.patterns:
            match = re.match(pattern, user_input, re.IGNORECASE)
            if match:
                try:
                    coords = self._extract_coordinates_from_match(match)
                    if coords and self.validate_coordinates(coords[0], coords[1]):
                        logger.info(f"Parsed coordinates from '{user_input}': {coords}", user_id)
                        return coords
                except Exception as e:
                    logger.error(f"Error parsing coordinates from '{user_input}': {e}", user_id)
                    continue
        
        logger.warning(f"Failed to parse coordinates from '{user_input}'", user_id)
        return None
    
    def _extract_coordinates_from_match(self, match) -> Optional[Tuple[float, float]]:
        """Extract coordinates from regex match object."""
        groups = match.groups()
        
        if len(groups) == 2:
            # Simple decimal format: lat, lon
            return float(groups[0]), float(groups[1])
        
        elif len(groups) == 4:
            # Format with N/S/E/W indicators
            lat = float(groups[0])
            lat_dir = groups[1].upper()
            lon = float(groups[2])
            lon_dir = groups[3].upper()
            
            # Apply direction indicators
            if lat_dir == 'S':
                lat = -lat
            if lon_dir == 'W':
                lon = -lon
            
            return lat, lon
        
        return None
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """
        Validate if coordinates are within valid range.
        
        Args:
            lat: Latitude value
            lon: Longitude value
            
        Returns:
            True if coordinates are valid, False otherwise
        """
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    def is_lilongwe_area(self, lat: float, lon: float) -> bool:
        """
        Check if coordinates are in the Lilongwe area.
        
        Args:
            lat: Latitude value
            lon: Longitude value
            
        Returns:
            True if coordinates are in Lilongwe area, False otherwise
        """
        # Lilongwe area bounds (approximate)
        lilongwe_bounds = {
            'lat_min': -14.2,
            'lat_max': -13.7,
            'lon_min': 33.5,
            'lon_max': 34.0
        }
        
        return (lilongwe_bounds['lat_min'] <= lat <= lilongwe_bounds['lat_max'] and
                lilongwe_bounds['lon_min'] <= lon <= lilongwe_bounds['lon_max'])
    
    def format_coordinates(self, lat: float, lon: float) -> str:
        """
        Format coordinates for display.
        
        Args:
            lat: Latitude value
            lon: Longitude value
            
        Returns:
            Formatted coordinate string
        """
        lat_dir = 'N' if lat >= 0 else 'S'
        lon_dir = 'E' if lon >= 0 else 'W'
        
        return f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}"
    
    def get_location_suggestions(self, partial_input: str) -> List[str]:
        """
        Get location suggestions based on partial input.
        
        Args:
            partial_input: Partial location name
            
        Returns:
            List of matching location names
        """
        partial_input = partial_input.lower().strip()
        suggestions = []
        
        for location in self.known_locations:
            if partial_input in location:
                suggestions.append(location.title())
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_help_text(self) -> str:
        """
        Get help text for coordinate input formats.
        
        Returns:
            Help text string
        """
        return """
🗺️ **Coordinate Input Formats:**

**Decimal Degrees:**
• `-13.9833, 33.7833`
• `lat: -13.9833, lon: 33.7833`

**With Direction:**
• `13.9833S, 33.7833E`

**Known Locations:**
• `Lilongwe` or `Lilongwe City`
• `Area 1`, `Area 2`, `Area 3`
• `Kawale`, `Mgona`, `Kanengo`

**Examples:**
• `/weather -13.9833, 33.7833`
• `/rain Lilongwe`
• `/crops Area 1`
"""
    
    def add_known_location(self, name: str, lat: float, lon: float) -> bool:
        """
        Add a new known location.
        
        Args:
            name: Location name
            lat: Latitude
            lon: Longitude
            
        Returns:
            True if added successfully, False otherwise
        """
        if self.validate_coordinates(lat, lon):
            self.known_locations[name.lower()] = (lat, lon)
            logger.info(f"Added known location: {name} ({lat}, {lon})")
            return True
        return False


# Global coordinate handler instance
coordinate_handler = CoordinateHandler() 