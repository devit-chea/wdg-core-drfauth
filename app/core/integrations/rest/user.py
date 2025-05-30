import httpx
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest
from typing import Optional, Dict, Any


class UserRest:
    AUTH_URL = settings.AUTH_SERVICE_URL

    def __init__(self, request: Optional[HttpRequest] = None):
        self.request = request
        self.session = httpx.Client(timeout=5)

    def _fetch_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Fetch data from API and cache it for 5 minutes."""
        cache_key = f"product_rest:{endpoint}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data  # Return cached response

        url = f"{self.AUTH_URL}/{endpoint}"

        headers = {
            "Authorization": self.request.headers.get("Authorization", ""),
            "Content-Type": "application/json",
        }

        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                cache.set(cache_key, data, timeout=300)  # Cache for 5 minutes
                return data
            return None
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"API error {e.response.status_code} from {url}: {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error while fetching data from {url}") from e

    def user_detail(self, id: int) -> Optional[Dict[str, Any]]:
        """Fetch current user with caching."""
        return self._fetch_data(f"user/{id}")

    def __del__(self):
        self.session.close()
