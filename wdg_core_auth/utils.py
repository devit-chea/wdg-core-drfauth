import json
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import redis
from django.conf import settings

# Parse host/port/db from CACHE_REDIS_LOCATION
parsed_url = urlparse(settings.CACHE_REDIS_LOCATION)


# Extract credentials and connection info
host = parsed_url.hostname
port = parsed_url.port or 6379
db = int(parsed_url.path.lstrip("/")) if parsed_url.path else 0
password = parsed_url.password

# Connect to Redis
redis_client = redis.Redis(
    host=host,
    port=port,
    db=db,
    password=password,
    ssl=False,  # Redis Cloud often requires SSL
)


# Parse to verify key
def parse_verify_key(key: str):
    if not key:
        return None
    return key.replace(r"\n", "\n")


def get_cached_json(key: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a JSON object from Redis.
    """
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except (json.JSONDecodeError, redis.RedisError):
        redis_client.delete(key)
    return None


def set_cached_json(key: str, value: Dict[str, Any], ttl: int = 300):
    """
    Set a JSON-serializable object into Redis with an optional TTL (in seconds).
    """
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except redis.RedisError:
        pass


def delete_cached_key(key: str):
    """
    Delete a cache key.
    """
    try:
        redis_client.delete(key)
    except redis.RedisError:
        pass
