#!/usr/bin/env python3
"""
Implementing a web cache
"""

from time import sleep
from typing import Callable
import redis
from functools import wraps
import requests


def url_count(method: Callable) -> Callable:
    """Wrapper function to count frequency of url"""
    @wraps(method)
    def count_wrapper(*args):
        """Callback function to be returned"""
        cache = redis.Redis()
        key = "count:" + args[0]
        cache.incrby(key, 1)
        cache.expire(key, 10)
        return method
    return count_wrapper


@url_count
def get_page(url: str) -> str:
    """Web cache and tracker"""
    res = requests.get(url)
    return res
