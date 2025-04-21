"""
Caching utilities for the analysis app.
"""

import functools
import hashlib
import json
import os
import pickle
import time
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
import pandas as pd
from django.core.cache import cache
from django.conf import settings


def cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from the given arguments.
    
    Parameters
    ----------
    prefix : str
        Prefix for the cache key
    *args : tuple
        Positional arguments to include in the key
    **kwargs : dict
        Keyword arguments to include in the key
        
    Returns
    -------
    str
        Cache key
    """
    # Convert args and kwargs to a string representation
    key_parts = [prefix]
    
    # Add args
    for arg in args:
        if isinstance(arg, pd.DataFrame):
            # For DataFrames, use a hash of the content
            arg_hash = hashlib.md5(pd.util.hash_pandas_object(arg).values).hexdigest()
            key_parts.append(f"df:{arg_hash}")
        elif isinstance(arg, (list, tuple, dict, set)):
            # For collections, use a hash of the JSON representation
            arg_hash = hashlib.md5(json.dumps(arg, sort_keys=True).encode()).hexdigest()
            key_parts.append(f"json:{arg_hash}")
        else:
            # For other types, use string representation
            key_parts.append(str(arg))
    
    # Add kwargs
    for key, value in sorted(kwargs.items()):
        if isinstance(value, pd.DataFrame):
            # For DataFrames, use a hash of the content
            value_hash = hashlib.md5(pd.util.hash_pandas_object(value).values).hexdigest()
            key_parts.append(f"{key}:df:{value_hash}")
        elif isinstance(value, (list, tuple, dict, set)):
            # For collections, use a hash of the JSON representation
            value_hash = hashlib.md5(json.dumps(value, sort_keys=True).encode()).hexdigest()
            key_parts.append(f"{key}:json:{value_hash}")
        else:
            # For other types, use string representation
            key_parts.append(f"{key}:{value}")
    
    # Join parts and hash the result
    key_str = ":".join(key_parts)
    return hashlib.md5(key_str.encode()).hexdigest()


def memoize(timeout: int = 3600) -> Callable:
    """
    Decorator for memoizing function results in Django's cache.
    
    Parameters
    ----------
    timeout : int, optional
        Cache timeout in seconds, by default 3600 (1 hour)
        
    Returns
    -------
    Callable
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            key = cache_key(f"memoize:{func.__module__}.{func.__name__}", *args, **kwargs)
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, timeout)
            
            return result
        return wrapper
    return decorator


def disk_cache(directory: Optional[str] = None, timeout: int = 86400) -> Callable:
    """
    Decorator for caching function results on disk.
    
    Parameters
    ----------
    directory : str, optional
        Directory to store cache files, by default None (uses CACHE_DIR from settings)
    timeout : int, optional
        Cache timeout in seconds, by default 86400 (1 day)
        
    Returns
    -------
    Callable
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get cache directory
            cache_dir = directory or getattr(settings, 'CACHE_DIR', '/tmp/analysis_cache')
            
            # Create directory if it doesn't exist
            os.makedirs(cache_dir, exist_ok=True)
            
            # Generate cache key
            key = cache_key(f"disk_cache:{func.__module__}.{func.__name__}", *args, **kwargs)
            cache_file = os.path.join(cache_dir, f"{key}.pkl")
            
            # Check if cache file exists and is not expired
            if os.path.exists(cache_file):
                file_age = time.time() - os.path.getmtime(cache_file)
                if file_age < timeout:
                    # Load from cache
                    try:
                        with open(cache_file, 'rb') as f:
                            return pickle.load(f)
                    except:
                        # If loading fails, continue to function call
                        pass
            
            # Call function
            result = func(*args, **kwargs)
            
            # Save to cache
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(result, f)
            except:
                # If saving fails, just return the result
                pass
            
            return result
        return wrapper
    return decorator


class DataFrameCache:
    """
    Cache for pandas DataFrames.
    
    This class provides methods for caching DataFrames in memory or on disk.
    """
    
    def __init__(self, max_size: int = 10, directory: Optional[str] = None):
        """
        Initialize the DataFrame cache.
        
        Parameters
        ----------
        max_size : int, optional
            Maximum number of DataFrames to cache in memory, by default 10
        directory : str, optional
            Directory to store cache files, by default None (uses CACHE_DIR from settings)
        """
        self.max_size = max_size
        self.cache_dir = directory or getattr(settings, 'CACHE_DIR', '/tmp/analysis_cache')
        self.memory_cache = {}
        self.access_times = {}
        
        # Create directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get(self, key: str) -> Optional[pd.DataFrame]:
        """
        Get a DataFrame from the cache.
        
        Parameters
        ----------
        key : str
            Cache key
            
        Returns
        -------
        Optional[pd.DataFrame]
            The cached DataFrame, or None if not found
        """
        # Try memory cache first
        if key in self.memory_cache:
            # Update access time
            self.access_times[key] = time.time()
            return self.memory_cache[key]
        
        # Try disk cache
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    df = pickle.load(f)
                
                # Add to memory cache
                self._add_to_memory_cache(key, df)
                
                return df
            except:
                # If loading fails, return None
                return None
        
        return None
    
    def set(self, key: str, df: pd.DataFrame, disk: bool = True) -> None:
        """
        Set a DataFrame in the cache.
        
        Parameters
        ----------
        key : str
            Cache key
        df : pd.DataFrame
            DataFrame to cache
        disk : bool, optional
            Whether to also cache on disk, by default True
        """
        # Add to memory cache
        self._add_to_memory_cache(key, df)
        
        # Add to disk cache if requested
        if disk:
            cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(df, f)
            except:
                # If saving fails, just continue
                pass
    
    def _add_to_memory_cache(self, key: str, df: pd.DataFrame) -> None:
        """
        Add a DataFrame to the memory cache.
        
        Parameters
        ----------
        key : str
            Cache key
        df : pd.DataFrame
            DataFrame to cache
        """
        # Check if cache is full
        if len(self.memory_cache) >= self.max_size and key not in self.memory_cache:
            # Remove least recently used item
            lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
            del self.memory_cache[lru_key]
            del self.access_times[lru_key]
        
        # Add to cache
        self.memory_cache[key] = df
        self.access_times[key] = time.time()
    
    def clear(self) -> None:
        """
        Clear the cache.
        """
        # Clear memory cache
        self.memory_cache.clear()
        self.access_times.clear()
        
        # Clear disk cache
        for file in os.listdir(self.cache_dir):
            if file.endswith('.pkl'):
                try:
                    os.remove(os.path.join(self.cache_dir, file))
                except:
                    # If removal fails, just continue
                    pass
    
    def remove(self, key: str) -> None:
        """
        Remove an item from the cache.
        
        Parameters
        ----------
        key : str
            Cache key
        """
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
            del self.access_times[key]
        
        # Remove from disk cache
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except:
                # If removal fails, just continue
                pass
