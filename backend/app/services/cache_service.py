"""
Cache service for Trade-Scan application.

This module provides in-memory caching with TTL (Time To Live) support
to reduce API calls and improve performance.
"""

import time
from typing import Optional, Any, Dict
from functools import wraps
from cachetools import TTLCache
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    In-memory cache service with TTL support.
    
    This service provides caching functionality to reduce redundant API calls
    and improve application performance. It uses TTLCache for automatic expiration.
    """
    
    def __init__(self, ttl: int = 300, max_size: int = 1000):
        """
        Initialize the cache service.
        
        Args:
            ttl: Time to live in seconds (default: 300 = 5 minutes)
            max_size: Maximum number of items in cache (default: 1000)
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache: TTLCache = TTLCache(maxsize=max_size, ttl=ttl)
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        logger.info(f"CacheService initialized with TTL={ttl}s, max_size={max_size}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        try:
            value = self._cache[key]
            self._stats["hits"] += 1
            logger.debug(f"Cache HIT: {key}")
            return value
        except KeyError:
            self._stats["misses"] += 1
            logger.debug(f"Cache MISS: {key}")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Store a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value
        self._stats["sets"] += 1
        logger.debug(f"Cache SET: {key}")
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key existed and was deleted, False otherwise
        """
        try:
            del self._cache[key]
            self._stats["deletes"] += 1
            logger.debug(f"Cache DELETE: {key}")
            return True
        except KeyError:
            return False
    
    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (
            (self._stats["hits"] / total_requests * 100) 
            if total_requests > 0 
            else 0
        )
        
        return {
            **self._stats,
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests
        }
    
    def has_key(self, key: str) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and is not expired, False otherwise
        """
        return key in self._cache


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds (uses cache default if None)
        key_prefix: Prefix for cache key
        
    Returns:
        Decorated function with caching
        
    Example:
        @cached(ttl=60, key_prefix="coin_data")
        def get_coin_data(symbol: str):
            return fetch_from_api(symbol)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Only cache if self has cache_service attribute
            if not hasattr(self, 'cache_service'):
                return func(self, *args, **kwargs)
            
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{args}:{sorted(kwargs.items())}"
            
            # Try to get from cache
            cached_result = self.cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = func(self, *args, **kwargs)
            self.cache_service.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service(ttl: int = 300, max_size: int = 1000) -> CacheService:
    """
    Get or create the global cache service instance.
    
    Args:
        ttl: Time to live in seconds (default: 300)
        max_size: Maximum cache size (default: 1000)
        
    Returns:
        CacheService instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService(ttl=ttl, max_size=max_size)
    return _cache_service
