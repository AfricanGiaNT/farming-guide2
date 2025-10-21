"""
Advanced Caching System for Crop Recommendations using REAL DATA ONLY.
Implements intelligent caching with TTL, invalidation, and performance optimization.
"""
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from scripts.utils.logger import logger


class AdvancedCachingSystem:
    """
    Advanced caching system for crop recommendations using ONLY real data sources.
    Implements intelligent caching with TTL, invalidation, and performance optimization.
    """
    
    def __init__(self, cache_duration: int = 3600):  # 1 hour default
        """
        Initialize the advanced caching system.
        
        Args:
            cache_duration: Cache duration in seconds
        """
        self.cache_duration = cache_duration
        self.cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }
        
        logger.info(f"Advanced Caching System initialized with {cache_duration}s TTL")
    
    def _generate_cache_key(self, 
                          lat: float, 
                          lon: float, 
                          season: str, 
                          rainfall_mm: float, 
                          temperature: float,
                          farmer_profile: Optional[Dict[str, Any]] = None) -> str:
        """Generate a unique cache key for the request."""
        # Create a hash of the request parameters
        key_data = {
            'lat': round(lat, 4),  # Round to 4 decimal places for cache efficiency
            'lon': round(lon, 4),
            'season': season,
            'rainfall_mm': round(rainfall_mm, 1),
            'temperature': round(temperature, 1),
            'farmer_profile': farmer_profile or {}
        }
        
        # Create hash with consistent ordering
        key_string = json.dumps(key_data, sort_keys=True, separators=(',', ':'))
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"crop_rec_{cache_key}"
    
    def get_cached_recommendations(self, 
                                 lat: float, 
                                 lon: float, 
                                 season: str, 
                                 rainfall_mm: float, 
                                 temperature: float,
                                 farmer_profile: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached crop recommendations if available and valid.
        
        Returns:
            Cached recommendations or None if not available/expired
        """
        cache_key = self._generate_cache_key(lat, lon, season, rainfall_mm, temperature, farmer_profile)
        
        self.cache_stats['total_requests'] += 1
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            
            # Check if cache is still valid
            if time.time() - cached_data['timestamp'] < self.cache_duration:
                self.cache_stats['hits'] += 1
                logger.info(f"Cache HIT for key: {cache_key[:16]}...")
                return cached_data['data']
            else:
                # Cache expired, remove it
                del self.cache[cache_key]
                self.cache_stats['evictions'] += 1
                logger.info(f"Cache EXPIRED for key: {cache_key[:16]}...")
        
        self.cache_stats['misses'] += 1
        logger.info(f"Cache MISS for key: {cache_key[:16]}...")
        return None
    
    def cache_recommendations(self, 
                            recommendations: Dict[str, Any],
                            lat: float, 
                            lon: float, 
                            season: str, 
                            rainfall_mm: float, 
                            temperature: float,
                            farmer_profile: Optional[Dict[str, Any]] = None) -> None:
        """
        Cache crop recommendations with metadata.
        
        Args:
            recommendations: The recommendations data to cache
            lat: Latitude
            lon: Longitude
            season: Planting season
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            farmer_profile: Farmer's profile
        """
        cache_key = self._generate_cache_key(lat, lon, season, rainfall_mm, temperature, farmer_profile)
        
        # Prepare cache data with metadata
        cache_data = {
            'data': recommendations,
            'timestamp': time.time(),
            'metadata': {
                'lat': lat,
                'lon': lon,
                'season': season,
                'rainfall_mm': rainfall_mm,
                'temperature': temperature,
                'farmer_profile': farmer_profile,
                'cache_key': cache_key,
                'algorithm_version': recommendations.get('algorithm_version', 'unknown')
            }
        }
        
        # Store in cache
        self.cache[cache_key] = cache_data
        
        # Clean up expired entries periodically
        self._cleanup_expired_entries()
        
        logger.info(f"Cached recommendations for key: {cache_key[:16]}...")
    
    def _cleanup_expired_entries(self) -> None:
        """Clean up expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.cache.items():
            if current_time - data['timestamp'] >= self.cache_duration:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            self.cache_stats['evictions'] += 1
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def invalidate_cache(self, pattern: Optional[str] = None) -> int:
        """
        Invalidate cache entries.
        
        Args:
            pattern: Optional pattern to match cache keys
            
        Returns:
            Number of entries invalidated
        """
        if pattern:
            # Invalidate entries matching pattern
            keys_to_remove = [key for key in self.cache.keys() if pattern in key]
        else:
            # Invalidate all entries
            keys_to_remove = list(self.cache.keys())
        
        for key in keys_to_remove:
            del self.cache[key]
            self.cache_stats['evictions'] += 1
        
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries")
        return len(keys_to_remove)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_stats['total_requests']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'hit_rate': round(hit_rate, 2),
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'evictions': self.cache_stats['evictions'],
            'total_requests': total_requests,
            'cache_duration': self.cache_duration
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information."""
        cache_info = {
            'total_entries': len(self.cache),
            'cache_duration': self.cache_duration,
            'stats': self.get_cache_stats(),
            'entries': []
        }
        
        current_time = time.time()
        for key, data in self.cache.items():
            age = current_time - data['timestamp']
            remaining_ttl = max(0, self.cache_duration - age)
            
            cache_info['entries'].append({
                'key': key[:16] + '...',
                'age_seconds': round(age, 1),
                'remaining_ttl': round(remaining_ttl, 1),
                'algorithm_version': data['metadata'].get('algorithm_version', 'unknown'),
                'location': f"{data['metadata']['lat']:.4f}, {data['metadata']['lon']:.4f}",
                'season': data['metadata']['season']
            })
        
        return cache_info


# Create global instance
advanced_caching_system = AdvancedCachingSystem()
