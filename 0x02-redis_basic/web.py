import requests
import time
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def get_page(url: str) -> str:
    count_key = f"count:{url}"
    content_key = f"content:{url}"

    # Check if the URL has been accessed before
    if r.exists(count_key):
        r.incr(count_key)
    else:
        r.set(count_key, 1)

    # Check if the HTML content is cached
    if r.exists(content_key):
        html = r.get(content_key)
    else:
        # Get HTML content from the URL
        response = requests.get(url)
        html = response.text
        r.set(content_key, html, ex=10)

    return html
