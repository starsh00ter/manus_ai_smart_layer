#!/usr/bin/env python3

"""
Shared Cache Manager for Manus AI Projects

Provides unified caching logic for both projects with multiple storage backends
and intelligent cache invalidation.
"""

import os
import json
import hashlib
import pickle
import time
from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timedelta
from pathlib import Path

class CacheManager:
    """Unified cache manager for both projects"""
    
    def __init__(self, project_name: str = "smart_layer", cache_dir: str = None):
        self.project_name = project_name
        self.cache_dir = Path(cache_dir or f"cache/{project_name}")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache configuration
        self.default_ttl = 3600  # 1 hour
        self.max_cache_size = 100 * 1024 * 1024  # 100MB
        self.cleanup_interval = 3600  # 1 hour
        
        # Memory cache for frequently accessed items
        self.memory_cache = {}
        self.memory_cache_ttl = {}
        self.memory_cache_max_size = 1000
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "cleanups": 0
        }
        
        self.last_cleanup = time.time()
    
    def _get_cache_key(self, key: str, namespace: str = "default") -> str:
        """Generate a cache key with namespace"""
        return f"{self.project_name}:{namespace}:{key}"
    
    def _get_file_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        # Use hash to avoid filesystem issues with long keys
        key_hash = hashlib.md5(cache_key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        return pickle.dumps({
            "value": value,
            "timestamp": time.time(),
            "type": type(value).__name__
        })
    
    def _deserialize_value(self, data: bytes) -> tuple[Any, float]:
        """Deserialize value from storage"""
        try:
            obj = pickle.loads(data)
            return obj["value"], obj["timestamp"]
        except Exception:
            return None, 0
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Check if cache entry is expired"""
        return time.time() - timestamp > ttl
    
    def _cleanup_memory_cache(self):
        """Clean up expired entries from memory cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, ttl_time in self.memory_cache_ttl.items():
            if current_time > ttl_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.memory_cache.pop(key, None)
            self.memory_cache_ttl.pop(key, None)
        
        # Limit memory cache size
        if len(self.memory_cache) > self.memory_cache_max_size:
            # Remove oldest entries
            sorted_items = sorted(
                self.memory_cache_ttl.items(),
                key=lambda x: x[1]
            )
            
            to_remove = len(self.memory_cache) - self.memory_cache_max_size
            for key, _ in sorted_items[:to_remove]:
                self.memory_cache.pop(key, None)
                self.memory_cache_ttl.pop(key, None)
    
    def _cleanup_disk_cache(self):
        """Clean up expired entries from disk cache"""
        if time.time() - self.last_cleanup < self.cleanup_interval:
            return
        
        total_size = 0
        cache_files = []
        
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                stat = cache_file.stat()
                total_size += stat.st_size
                cache_files.append((cache_file, stat.st_mtime, stat.st_size))
            except OSError:
                continue
        
        # Remove expired files
        current_time = time.time()
        for cache_file, mtime, size in cache_files[:]:
            if current_time - mtime > self.default_ttl * 2:  # Double TTL for safety
                try:
                    cache_file.unlink()
                    cache_files.remove((cache_file, mtime, size))
                    total_size -= size
                except OSError:
                    continue
        
        # Remove oldest files if cache is too large
        if total_size > self.max_cache_size:
            cache_files.sort(key=lambda x: x[1])  # Sort by modification time
            
            for cache_file, mtime, size in cache_files:
                try:
                    cache_file.unlink()
                    total_size -= size
                    if total_size <= self.max_cache_size * 0.8:  # Leave some headroom
                        break
                except OSError:
                    continue
        
        self.last_cleanup = current_time
        self.stats["cleanups"] += 1
    
    def get(self, key: str, namespace: str = "default", default: Any = None) -> Any:
        """Get value from cache"""
        cache_key = self._get_cache_key(key, namespace)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            if cache_key in self.memory_cache_ttl:
                if time.time() <= self.memory_cache_ttl[cache_key]:
                    self.stats["hits"] += 1
                    return self.memory_cache[cache_key]
                else:
                    # Expired
                    self.memory_cache.pop(cache_key, None)
                    self.memory_cache_ttl.pop(cache_key, None)
        
        # Check disk cache
        file_path = self._get_file_path(cache_key)
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    value, timestamp = self._deserialize_value(f.read())
                
                if value is not None and not self._is_expired(timestamp, self.default_ttl):
                    # Add to memory cache for faster access
                    self.memory_cache[cache_key] = value
                    self.memory_cache_ttl[cache_key] = time.time() + 300  # 5 min in memory
                    
                    self.stats["hits"] += 1
                    return value
                else:
                    # Expired, remove file
                    file_path.unlink()
            except Exception:
                # Corrupted cache file, remove it
                try:
                    file_path.unlink()
                except OSError:
                    pass
        
        self.stats["misses"] += 1
        return default
    
    def set(self, key: str, value: Any, ttl: int = None, namespace: str = "default") -> bool:
        """Set value in cache"""
        cache_key = self._get_cache_key(key, namespace)
        ttl = ttl or self.default_ttl
        
        try:
            # Store in memory cache
            self.memory_cache[cache_key] = value
            self.memory_cache_ttl[cache_key] = time.time() + min(ttl, 300)  # Max 5 min in memory
            
            # Store in disk cache
            file_path = self._get_file_path(cache_key)
            with open(file_path, 'wb') as f:
                f.write(self._serialize_value(value))
            
            self.stats["sets"] += 1
            
            # Periodic cleanup
            self._cleanup_memory_cache()
            self._cleanup_disk_cache()
            
            return True
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache"""
        cache_key = self._get_cache_key(key, namespace)
        
        # Remove from memory cache
        self.memory_cache.pop(cache_key, None)
        self.memory_cache_ttl.pop(cache_key, None)
        
        # Remove from disk cache
        file_path = self._get_file_path(cache_key)
        try:
            if file_path.exists():
                file_path.unlink()
            self.stats["deletes"] += 1
            return True
        except OSError:
            return False
    
    def clear(self, namespace: str = None) -> bool:
        """Clear cache entries"""
        try:
            if namespace:
                # Clear specific namespace
                prefix = f"{self.project_name}:{namespace}:"
                
                # Clear memory cache
                keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(prefix)]
                for key in keys_to_remove:
                    self.memory_cache.pop(key, None)
                    self.memory_cache_ttl.pop(key, None)
                
                # Clear disk cache (this is approximate since we hash keys)
                for cache_file in self.cache_dir.glob("*.cache"):
                    try:
                        cache_file.unlink()
                    except OSError:
                        continue
            else:
                # Clear all cache
                self.memory_cache.clear()
                self.memory_cache_ttl.clear()
                
                for cache_file in self.cache_dir.glob("*.cache"):
                    try:
                        cache_file.unlink()
                    except OSError:
                        continue
            
            return True
            
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if key exists in cache"""
        return self.get(key, namespace) is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0
        total_requests = self.stats["hits"] + self.stats["misses"]
        if total_requests > 0:
            hit_rate = (self.stats["hits"] / total_requests) * 100
        
        # Calculate cache sizes
        memory_size = len(self.memory_cache)
        disk_size = 0
        disk_files = 0
        
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                disk_files += 1
                disk_size += cache_file.stat().st_size
        except OSError:
            pass
        
        return {
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests,
            "memory_entries": memory_size,
            "disk_entries": disk_files,
            "disk_size_mb": round(disk_size / (1024 * 1024), 2),
            "stats": self.stats.copy()
        }
    
    def cache_function(self, ttl: int = None, namespace: str = "functions"):
        """Decorator to cache function results"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                key_data = {
                    "func": func.__name__,
                    "args": args,
                    "kwargs": sorted(kwargs.items())
                }
                cache_key = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
                
                # Try to get from cache
                result = self.get(cache_key, namespace)
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl, namespace)
                return result
            
            return wrapper
        return decorator

# Singleton instance management
_cache_managers = {}

def get_cache_manager(project_name: str = "smart_layer") -> CacheManager:
    """Get a cache manager instance"""
    if project_name not in _cache_managers:
        _cache_managers[project_name] = CacheManager(project_name)
    
    return _cache_managers[project_name]

def reset_cache_managers():
    """Reset cache manager instances (useful for testing)"""
    global _cache_managers
    _cache_managers = {}

if __name__ == "__main__":
    # Test the cache manager
    cache = get_cache_manager("test_project")
    
    print("🔍 Testing Cache Manager...")
    
    # Test basic operations
    cache.set("test_key", "test_value", namespace="test")
    value = cache.get("test_key", namespace="test")
    print(f"Basic cache: {'✅' if value == 'test_value' else '❌'}")
    
    # Test function caching
    @cache.cache_function(ttl=60, namespace="functions")
    def expensive_function(x, y):
        time.sleep(0.1)  # Simulate expensive operation
        return x + y
    
    start_time = time.time()
    result1 = expensive_function(1, 2)
    first_call_time = time.time() - start_time
    
    start_time = time.time()
    result2 = expensive_function(1, 2)  # Should be cached
    second_call_time = time.time() - start_time
    
    print(f"Function cache: {'✅' if result1 == result2 and second_call_time < first_call_time else '❌'}")
    
    # Test statistics
    stats = cache.get_stats()
    print(f"Cache stats: {stats['hit_rate']}% hit rate, {stats['total_requests']} requests")
    
    print("✅ Cache manager test complete")

