#!/usr/bin/env python3
"""
Create a class to handle redis operations
"""

from functools import wraps
import uuid
import redis
from typing import Callable, Tuple, Union
import requests


def count_calls(method: Callable) -> Callable:
    """decorator function to count how many times a function is called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """"Callback function"""
        key = method.__qualname__
        cache = self._redis
        cache.incr(key)
        return method
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator function to record call hsitory of a function"""
    @wraps(method)
    def call_history(*args):
        """Callback for call history"""
        inputlist_key = method.__qualname__ + ":inputs"
        outputlist_key = method.__qualname__ + ":outputs"
        cache = (args[0])._redis
        cache.rpush(inputlist_key, args[1])
        output = method(*args)
        cache.rpush(outputlist_key, output)
        return output
    return call_history


def replay(method: Callable):
    """Show history of a function's call"""
    cache = redis.Redis()
    input_key = method.__qualname__ + ":inputs"
    output_key = method.__qualname__ + ":outputs"
    call_freq = cache.llen(input_key)
    in_list = cache.lrange(input_key, 0, -1)
    out_list = cache.lrange(output_key, 0, -1)
    print("Cache.store was called {} times".format(call_freq))
    for i in range(len(in_list)):
        print("{}(*({},)) -> {}".format(method.__qualname__,
                                        in_list[i].decode('utf-8'),
                                        out_list[i].decode('utf-8')))


class Cache():
    """Redis class to handle redis operations"""
    def __init__(self):
        """Constructor method for redis instance"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Method to store data"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key, fn=None):
        """Method to get a value using its key and a callback function"""
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key):
        """Get a string format of a value"""
        return self.get(key, str)

    def get_int(self, key):
        """Get an integer format of a value"""
        return self.get(key, int)
