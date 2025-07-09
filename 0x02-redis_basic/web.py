#!/usr/bin/env python3
"""
Fetch and cache HTML content using Redis.
"""

import requests
import redis
from functools import wraps
from typing import Callable

# Connect to Redis
r = redis.Redis()

def count_access(func: Callable) -> Callable:
    """Decorator to count accesses per URL"""
    @wraps(func)
    def wrapper(url: str) -> str:
        r.incr(f"count:{url}")  # increment access count
        return func(url)
    return wrapper

def cache_page(expire: int = 10) -> Callable:
    """Decorator to cache HTML result for 10 seconds"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(url: str) -> str:
            key = f"cached:{url}"
            cached_html = r.get(key)
            if cached_html:
                return cached_html.decode('utf-8')  # return cached result
            result = func(url)
            r.setex(key, expire, result)  # cache with expiration
            return result
        return wrapper
    return decorator

@count_access
@cache_page(expire=10)
def get_page(url: str) -> str:
    """Get HTML content of a URL"""
    response = requests.get(url)
    return response.text
