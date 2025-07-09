#!/usr/bin/env python3
"""
Module to fetch and cache HTML pages using Redis.
"""

import redis
import requests
from functools import wraps
from typing import Callable

r = redis.Redis()


def count_access(method: Callable) -> Callable:
    """Decorator that counts how many times a URL is accessed."""
    @wraps(method)
    def wrapper(url: str) -> str:
        r.incr(f"count:{url}")
        return method(url)
    return wrapper


def cache_result(expiration: int = 10) -> Callable:
    """Decorator that caches the result of a URL fetch for a set time."""
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(url: str) -> str:
            key = f"cached:{url}"
            cached = r.get(key)
            if cached:
                return cached.decode("utf-8")
            result = method(url)
            r.setex(key, expiration, result)
            return result
        return wrapper
    return decorator


@count_access
@cache_result(expiration=10)
def get_page(url: str) -> str:
    """Fetch the HTML content of a URL and return it."""
    response = requests.get(url)
    return response.text
