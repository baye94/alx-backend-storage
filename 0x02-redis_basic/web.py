# web.py
import requests
import redis
import time

# Initialize Redis connection
# Assuming Redis is running on localhost:6379
cache = redis.Redis(host='localhost', port=6379)

def get_page(url: str) -> str:
    """
    Fetches the HTML content of a URL, caches it, and tracks access count.
    """
    # Increment access count for the URL
    cache_key_count = f"count:{url}"
    cache.incr(cache_key_count)

    # Check if content is in cache
    cache_key_content = f"page_content:{url}"
    cached_content = cache.get(cache_key_content)

    if cached_content:
        print(f"Cache hit for {url}")
        return cached_content.decode('utf-8')
    else:
        print(f"Cache miss for {url}. Fetching content...")
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            html_content = response.text

            # Cache the content with a 10-second expiration
            cache.setex(cache_key_content, 10, html_content)
            print(f"Content for {url} cached.")
            return html_content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return f"Error: Could not retrieve page for {url}"

# Bonus: Implement with a decorator
def cache_and_count(expiration_time: int = 10):
    def decorator(func):
        def wrapper(url: str) -> str:
            # Increment access count for the URL
            cache_key_count = f"count:{url}"
            cache.incr(cache_key_count)

            # Check if content is in cache
            cache_key_content = f"page_content:{url}"
            cached_content = cache.get(cache_key_content)

            if cached_content:
                print(f"Cache hit (via decorator) for {url}")
                return cached_content.decode('utf-8')
            else:
                print(f"Cache miss (via decorator) for {url}. Fetching content...")
                html_content = func(url) # Call the original function to get content

                # Cache the content with the specified expiration time
                cache.setex(cache_key_content, expiration_time, html_content)
                print(f"Content for {url} cached (via decorator).")
                return html_content
        return wrapper
    return decorator

# Example of using the decorator
@cache_and_count(expiration_time=10)
def get_page_decorated(url: str) -> str:
    """
    Fetches the HTML content of a URL (this function itself is simple
    as caching/counting is handled by the decorator).
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url} in decorated function: {e}")
        return f"Error: Could not retrieve page for {url}"

if __name__ == "__main__":
    # --- Test the direct get_page function ---
    print("--- Testing direct get_page function ---")
    test_url_slow = "http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.google.com"
    test_url_fast = "http://example.com"

    print(f"\nAccessing {test_url_slow} for the first time...")
    get_page(test_url_slow)
    print(f"Count for {test_url_slow}: {cache.get(f'count:{test_url_slow}').decode('utf-8')}")

    print(f"\nAccessing {test_url_slow} again (should be cached)...")
    get_page(test_url_slow)
    print(f"Count for {test_url_slow}: {cache.get(f'count:{test_url_slow}').decode('utf-8')}")

    print("\nWaiting 11 seconds to clear cache...")
    time.sleep(11)

    print(f"\nAccessing {test_url_slow} after cache expiration...")
    get_page(test_url_slow)
    print(f"Count for {test_url_slow}: {cache.get(f'count:{test_url_slow}').decode('utf-8')}")

    print(f"\nAccessing {test_url_fast}...")
    get_page(test_url_fast)
    print(f"Count for {test_url_fast}: {cache.get(f'count:{test_url_fast}').decode('utf-8')}")

    # --- Test the decorated get_page function ---
    print("\n--- Testing decorated get_page function ---")
    test_url_decorated_slow = "http://slowwly.robertomurray.co.uk/delay/2000/url/http://www.bing.com"
    test_url_decorated_fast = "http://www.python.org"

    print(f"\nAccessing {test_url_decorated_slow} for the first time (decorated)...")
    get_page_decorated(test_url_decorated_slow)
    print(f"Count for {test_url_decorated_slow}: {cache.get(f'count:{test_url_decorated_slow}').decode('utf-8')}")

    print(f"\nAccessing {test_url_decorated_slow} again (should be cached, decorated)...")
    get_page_decorated(test_url_decorated_slow)
    print(f"Count for {test_url_decorated_slow}: {cache.get(f'count:{test_url_decorated_slow}').decode('utf-8')}")

    print("\nWaiting 11 seconds to clear cache for decorated function...")
    time.sleep(11)

    print(f"\nAccessing {test_url_decorated_slow} after cache expiration (decorated)...")
    get_page_decorated(test_url_decorated_slow)
    print(f"Count for {test_url_decorated_slow}: {cache.get(f'count:{test_url_decorated_slow}').decode('utf-8')}")

    print(f"\nAccessing {test_url_decorated_fast} (decorated)...")
    get_page_decorated(test_url_decorated_fast)
    print(f"Count for {test_url_decorated_fast}: {cache.get(f'count:{test_url_decorated_fast}').decode('utf-8')}")