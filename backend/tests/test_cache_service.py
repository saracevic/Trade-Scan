"""Unit tests for Cache service."""

import pytest
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.cache_service import CacheService


@pytest.fixture
def cache_service():
    """Create a cache service instance."""
    return CacheService(ttl=1, max_size=10)


class TestCacheService:
    """Test cases for CacheService."""
    
    def test_set_and_get(self, cache_service):
        """Test basic set and get operations."""
        cache_service.set("key1", "value1")
        
        result = cache_service.get("key1")
        assert result == "value1"
        
        stats = cache_service.get_stats()
        assert stats["hits"] == 1
        assert stats["sets"] == 1
    
    def test_cache_miss(self, cache_service):
        """Test cache miss."""
        result = cache_service.get("nonexistent")
        
        assert result is None
        
        stats = cache_service.get_stats()
        assert stats["misses"] == 1
    
    def test_ttl_expiration(self, cache_service):
        """Test TTL expiration."""
        cache_service.set("key1", "value1")
        
        # Should exist immediately
        assert cache_service.get("key1") == "value1"
        
        # Wait for TTL to expire
        time.sleep(1.5)
        
        # Should be expired
        assert cache_service.get("key1") is None
    
    def test_delete(self, cache_service):
        """Test delete operation."""
        cache_service.set("key1", "value1")
        assert cache_service.has_key("key1")
        
        result = cache_service.delete("key1")
        assert result is True
        assert not cache_service.has_key("key1")
        
        # Delete non-existent key
        result = cache_service.delete("nonexistent")
        assert result is False
    
    def test_clear(self, cache_service):
        """Test clear operation."""
        cache_service.set("key1", "value1")
        cache_service.set("key2", "value2")
        
        cache_service.clear()
        
        assert cache_service.get("key1") is None
        assert cache_service.get("key2") is None
        
        stats = cache_service.get_stats()
        assert stats["size"] == 0
    
    def test_max_size(self):
        """Test max size limit."""
        cache = CacheService(ttl=60, max_size=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        stats = cache.get_stats()
        assert stats["size"] == 3
    
    def test_hit_rate(self, cache_service):
        """Test hit rate calculation."""
        cache_service.set("key1", "value1")
        
        # 2 hits
        cache_service.get("key1")
        cache_service.get("key1")
        
        # 1 miss
        cache_service.get("nonexistent")
        
        stats = cache_service.get_stats()
        expected_hit_rate = (2 / 3) * 100
        assert abs(stats["hit_rate"] - expected_hit_rate) < 0.1
