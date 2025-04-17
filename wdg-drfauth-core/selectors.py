import httpx
import logging

from django.conf import settings
from typing import Optional, Dict, Any


class FetchPermissionSelector:
    AUTH_URL = settings.AUTH_SERVICE_BASE_URL

    def __init__(self, request=None):
        """
        Initializes the selector. Optionally accepts a request with an Authorization header.
        """
        self.request = request

    def _fetch_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        authorization = self.request.headers.get("Authorization") or ""
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }

        url = f"{self.AUTH_URL}/{endpoint}"
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=headers, timeout=5)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(
                f"HTTP error from {url}: {e.response.status_code} - {e.response.text}"
            )
        except httpx.RequestError as e:
            logging.error(f"Network error while fetching data from {url}: {e}")

        return None

    def fetch_permissions(self) -> Optional[Dict[str, Any]]:
        authorized = bool(self.request)
        return self._fetch_data("api/v1/user/permissions?paging=false")
