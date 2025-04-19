import json
import httpx
import logging

from django.conf import settings
from typing import Optional, Dict, Any

from wdg_core_auth.utils import get_cached_json, set_cached_json


class FetchPermissionV1Selector:
    AUTH_URL = settings.AUTH_SERVICE_BASE_URL
    DEFAULT_ENDPOINT = "api/v1/user/permissions?paging=false"
    CACHE_TTL = 60 * 30  # 30 minutes

    def __init__(self, request=None):
        """
        Initializes the selector. Optionally accepts a request with an Authorization header.
        """
        self.request = request

    def _get_cache_key(self) -> Optional[str]:
        # Use Authorization token or user_id as cache key base
        auth_header = self.request.headers.get("Authorization")
        if auth_header:
            return f"permissions:{auth_header}"
        return None
    
    def _fetch_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        authorization = self.request.headers.get("Authorization") or ""
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }

        url = f"{self.AUTH_URL.rstrip('/')}/{endpoint.lstrip('/')}"
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
        cache_key = self._get_cache_key()

        # Try fetching from Redis cache
        if cache_key:
            permissions = get_cached_json(cache_key)
            if permissions:
                return permissions
                    
        # Fallback to HTTP call
        endpoint = getattr(settings, "AUTH_SERVICE_PERMISSION_ENDPOINT", self.DEFAULT_ENDPOINT)
        permissions = self._fetch_data(endpoint)

        # Store in cache
        if cache_key and permissions:
            set_cached_json(cache_key, permissions, ttl=self.CACHE_TTL)

        return permissions


class FetchPermissionSelector:
    AUTH_URL = settings.AUTH_SERVICE_BASE_URL
    DEFAULT_ENDPOINT = "api/v1/user/permissions?paging=false"
    CACHE_TTL = 60 * 30  # 30 minutes

    def __init__(self, request=None):
        self.request = request
        self.caching_enabled = getattr(settings, "AUTH_PERMISSION_CACHE_ENABLED", True)

    def _get_cache_key(self) -> Optional[str]:
        auth_header = self.request.headers.get("Authorization")
        if auth_header:
            return f"permissions:{auth_header}"
        return None

    def _fetch_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        authorization = self.request.headers.get("Authorization") or ""
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }

        url = f"{self.AUTH_URL.rstrip('/')}/{endpoint.lstrip('/')}"
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
        endpoint = getattr(settings, "AUTH_SERVICE_PERMISSION_ENDPOINT", self.DEFAULT_ENDPOINT)

        if self.caching_enabled:
            cache_key = self._get_cache_key()
            if cache_key:
                permissions = get_cached_json(cache_key)
                if permissions:
                    return permissions

        permissions = self._fetch_data(endpoint)

        if self.caching_enabled and permissions:
            cache_key = self._get_cache_key()
            if cache_key:
                set_cached_json(cache_key, permissions, ttl=self.CACHE_TTL)

        return permissions
