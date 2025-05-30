import httpx
import logging
from django.conf import settings
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from typing import Any, Dict, Optional
from django.core.cache import cache


class CompanySelector:
    BASE_URL = settings.COMPANY_SERVICE_URL

    def __init__(self, request):
        """Ensure request is provided upon instantiation."""
        if not request:
            raise ValueError(
                "Request object is required to initialize CompanySelector."
            )

        self.request = request
        self.session = httpx.Client(timeout=5)

    def _fetch_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Fetches data from the company service with the authenticated user's token and caches it for 5 minutes."""
        cache_key = f"company_selector:{endpoint}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data  # Return cached response

        url = f"{self.BASE_URL}/{endpoint}"

        # Extract the token from the request headers
        auth_header = self.request.headers.get("Authorization")
        if not auth_header:
            logging.error("Missing Authorization token in request")
            return {}

        headers = {
            "Authorization": auth_header,  # Pass the user's token
            "Content-Type": "application/json",
        }

        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                cache.set(cache_key, data, timeout=300)  # Cache for 5 minutes
                return data
            return {}
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"API error {e.response.status_code} from {url}: {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error while fetching data from {url}") from e

    def fetch_user_company_obj(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Fetch company details using the authenticated user's token."""
        return self._fetch_data(f"company/{company_id}")

    def fetch_branch_obj(self, branch_id: int) -> Optional[Dict[str, Any]]:
        """Fetch company details using the authenticated user's token."""
        return self._fetch_data(f"company-branch/{branch_id}")

    def branch_info(self, branch_id: int) -> Optional[Dict[str, Any]]:
        """Fetch company details using the authenticated user's token."""
        return self._fetch_data(f"company-branch/{branch_id}/info")

    def get_company_id(self, user) -> int:
        """Retrieve company_id via API call from Company Service."""
        if not user or not hasattr(user, "company_id"):
            raise PermissionDenied(
                "Access denied: User is either missing or not associated with any company. Please check authentication and user permissions."
            )

        company = self.fetch_user_company_obj(user.company_id)

        if not company:
            raise ObjectDoesNotExist(
                f"No associated company found for user with ID {user.id}. Please ensure the user is linked to a company."
            )

        return company.get("id")  # Ensure API returns `id`
